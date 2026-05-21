import os
import hashlib
import logging
from typing import Optional, Tuple
import httpx
from app.database.db import get_db_connection

logger = logging.getLogger(__name__)

MOCK_COORDINATES = {
    # Famous Indore addresses
    "devi ahilyabai holkar airport": (22.7225, 75.8011, "Devi Ahilyabai Holkar International Airport, Indore, Madhya Pradesh, India"),
    "indore railway station": (22.7177, 75.8682, "Indore Junction Railway Station, Indore, Madhya Pradesh, India"),
    "sarwate bus stand": (22.7160, 75.8690, "Sarwate Bus Stand, Indore, Madhya Pradesh, India"),
    "rajendra nagar": (22.6756, 75.8306, "Rajendra Nagar, Indore, Madhya Pradesh, India"),
    "railway station": (22.7177, 75.8682, "Indore Junction Railway Station, Indore, Madhya Pradesh, India"),
    "vijay nagar": (22.7533, 75.8937, "Vijay Nagar, Indore, Madhya Pradesh, India"),
    "new delhi": (28.6139, 77.2090, "New Delhi, Delhi, India"),
    "navlakha": (22.7029, 75.8754, "Navlakha, Indore, Madhya Pradesh, India"),
    "airport": (22.7225, 75.8011, "Devi Ahilyabai Holkar International Airport, Indore, Madhya Pradesh, India"),
    "gurugram": (28.4595, 77.0266, "Gurugram, Haryana, India"),
    "gurgaon": (28.4595, 77.0266, "Gurgaon, Haryana, India"),
    "rajwada": (22.7185, 75.8538, "Rajwada, Indore, Madhya Pradesh, India"),
    "kolkata": (22.5726, 88.3639, "Kolkata, West Bengal, India"),
    "indore": (22.7196, 75.8577, "Indore, Madhya Pradesh, India"),
    "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra, India"),
    "bangalore": (12.9716, 77.5946, "Bangalore, Karnataka, India"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad, Telangana, India"),
    "chennai": (13.0827, 80.2707, "Chennai, Tamil Nadu, India"),
    "noida": (28.5355, 77.3910, "Noida, Uttar Pradesh, India"),
    "delhi": (28.6139, 77.2090, "Delhi, India"),
    "pune": (18.5204, 73.8567, "Pune, Maharashtra, India"),
}

INDORE_LANDMARKS = [
    "devi ahilyabai holkar airport",
    "indore railway station",
    "sarwate bus stand",
    "rajendra nagar",
    "railway station",
    "vijay nagar",
    "navlakha",
    "airport",
    "rajwada",
    "indore",
]

def get_cached_coordinates(address: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """Retrieve coordinates and formatted address from database geocode cache."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT latitude, longitude, formatted_address FROM geocode_cache WHERE address = ?",
                (address.strip().lower(),)
            )
            row = cursor.fetchone()
            if row:
                return row["latitude"], row["longitude"], row["formatted_address"]
    except Exception as e:
        logger.error("Error reading from geocode cache: %s", e)
    return None, None, None

def save_to_geocode_cache(address: str, lat: float, lng: float, formatted_address: str):
    """Save geocoded address to database cache."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO geocode_cache (address, latitude, longitude, formatted_address)
                VALUES (?, ?, ?, ?)
                """,
                (address.strip().lower(), lat, lng, formatted_address)
            )
            conn.commit()
    except Exception as e:
        logger.error("Error writing to geocode cache: %s", e)

def geocode_location(address: str) -> tuple[float, float, str]:
    """Resolve an address to coordinates using Cache, Google Maps, Nominatim, or Mock Fallback."""
    if not address:
        return 28.6139, 77.2090, "Delhi, India"

    address_clean = address.strip()
    
    # 1. Try Indore mock database first to ensure Indore-specific landmarks resolve locally
    addr_lower = address_clean.lower()
    other_cities = ["delhi", "new delhi", "noida", "gurgaon", "gurugram", "mumbai", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata", "pune"]
    
    is_indore_target = False
    matched_landmark = None
    for landmark in sorted(INDORE_LANDMARKS, key=len, reverse=True):
        if landmark in addr_lower:
            # If it's a generic landmark ("railway station", "airport"), check if another city is mentioned in the query
            if landmark in ["railway station", "airport"]:
                if any(city in addr_lower for city in other_cities):
                    continue
            matched_landmark = landmark
            is_indore_target = True
            break
            
    if is_indore_target and matched_landmark:
        coords = MOCK_COORDINATES[matched_landmark]
        lat, lng, formatted = coords
        save_to_geocode_cache(address_clean, lat, lng, formatted)
        logger.info("Geocoded via Indore mock database: '%s' -> (%.4f, %.4f)", address_clean, lat, lng)
        return lat, lng, formatted

    # 2. Check SQLite geocoding cache
    cached_lat, cached_lng, cached_formatted = get_cached_coordinates(address_clean)
    if cached_lat is not None and cached_lng is not None:
        logger.info("Geocoding cache hit for '%s' -> (%.4f, %.4f)", address_clean, cached_lat, cached_lng)
        return cached_lat, cached_lng, cached_formatted

    # 2. Try Google Maps Geocoding API if key is set
    google_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if google_key and "your_google_maps" not in google_key:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {"address": address_clean, "key": google_key}
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                location = result["geometry"]["location"]
                lat = location["lat"]
                lng = location["lng"]
                formatted = result.get("formatted_address", address_clean)
                
                # Cache and return
                save_to_geocode_cache(address_clean, lat, lng, formatted)
                logger.info("Geocoded via Google Maps: '%s' -> (%.4f, %.4f)", address_clean, lat, lng)
                return lat, lng, formatted
            else:
                logger.warning("Google Geocoding non-OK status: %s for '%s'", data.get("status"), address_clean)
        except Exception as e:
            logger.warning("Google Geocoding failed for '%s': %s", address_clean, e)

    # 3. Try Nominatim (OpenStreetMap) Geocoding API as fallback
    try:
        url_nom = "https://nominatim.openstreetmap.org/search"
        params_nom = {"q": address_clean, "format": "json", "limit": 1}
        headers = {"User-Agent": "cab-detection-system/1.0"}
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url_nom, params=params_nom, headers=headers)
            response.raise_for_status()
            data = response.json()
        if data:
            result = data[0]
            lat = float(result["lat"])
            lng = float(result["lon"])
            formatted = result.get("display_name", address_clean)
            
            # Cache and return
            save_to_geocode_cache(address_clean, lat, lng, formatted)
            logger.info("Geocoded via Nominatim: '%s' -> (%.4f, %.4f)", address_clean, lat, lng)
            return lat, lng, formatted
        else:
            logger.warning("Nominatim returned no results for '%s'", address_clean)
    except Exception as e:
        logger.warning("Nominatim Geocoding failed for '%s': %s", address_clean, e)

    # 4. Try local mock cities list
    addr_lower = address_clean.lower()
    for city, coords in sorted(MOCK_COORDINATES.items(), key=lambda x: len(x[0]), reverse=True):
        if city in addr_lower:
            if len(coords) == 3:
                lat, lng, formatted = coords
            else:
                lat, lng = coords
                formatted = f"{city.title()}, India"
            save_to_geocode_cache(address_clean, lat, lng, formatted)
            logger.info("Geocoded via local mock database: '%s' -> (%.4f, %.4f)", address_clean, lat, lng)
            return lat, lng, formatted

    # 5. Ultimate hash-based simulated location fallback
    h = int(hashlib.md5(addr_lower.encode("utf-8")).hexdigest(), 16)
    lat = 28.5 + (h % 100) / 500.0  # 28.5 to 28.7
    lng = 77.1 + ((h >> 8) % 100) / 500.0  # 77.1 to 77.3
    formatted = f"{address_clean} (Simulated Location)"
    
    # Save cache
    save_to_geocode_cache(address_clean, lat, lng, formatted)
    logger.info("Geocoded via hash-based fallback: '%s' -> (%.4f, %.4f)", address_clean, lat, lng)
    return lat, lng, formatted

def format_duration_hours(minutes) -> str:
    """Format duration minutes to a readable string with hours."""
    if minutes is None:
        return "N/A"
    try:
        minutes_val = float(minutes)
    except (ValueError, TypeError):
        return str(minutes)
    
    hours = int(minutes_val // 60)
    mins = int(round(minutes_val % 60))
    if mins == 60:
        hours += 1
        mins = 0
        
    dec_hours = minutes_val / 60.0
    if hours > 0:
        if mins > 0:
            return f"{hours} hr {mins} min ({dec_hours:.2f} hours)"
        else:
            return f"{hours} hr ({dec_hours:.2f} hours)"
    else:
        return f"{mins} min ({dec_hours:.2f} hours)"

