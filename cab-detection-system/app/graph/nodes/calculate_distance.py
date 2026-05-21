"""
Calculate Distance Node
=======================
Calculates the driving distance and estimated travel time between
the pickup and destination coordinates using the Google Maps
Distance Matrix API.
"""

import os
import logging
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


def calculate_distance(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: compute distance & duration between pickup and destination.

    Reads
    -----
    - ``state["pickup_lat"]``, ``state["pickup_lng"]``
    - ``state["destination_lat"]``, ``state["destination_lng"]``

    Writes
    ------
    - ``distance_km``       – driving distance in kilometres.
    - ``duration_minutes``  – estimated travel time in minutes.
    """
    pickup_lat = state.get("pickup_lat")
    pickup_lng = state.get("pickup_lng")
    dest_lat = state.get("destination_lat")
    dest_lng = state.get("destination_lng")

    if None in (pickup_lat, pickup_lng, dest_lat, dest_lng):
        logger.error("Missing coordinates for distance calculation")
        return {
            "distance_km": None,
            "duration_minutes": None,
            "error": "Coordinates are incomplete — cannot calculate distance.",
        }

    origins = f"{pickup_lat},{pickup_lng}"
    destinations = f"{dest_lat},{dest_lng}"

    if not GOOGLE_MAPS_API_KEY:
        logger.warning("GOOGLE_MAPS_API_KEY not set; using Haversine fallback")
        return _haversine_fallback(pickup_lat, pickup_lng, dest_lat, dest_lng)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origins,
        "destinations": destinations,
        "key": GOOGLE_MAPS_API_KEY,
        "units": "metric",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        # Check if the response contains valid rows and elements
        if data.get("status") == "REQUEST_DENIED":
            logger.warning("Google Distance Matrix API request denied: %s. Falling back to Haversine.", data.get("error_message"))
            return _haversine_fallback(pickup_lat, pickup_lng, dest_lat, dest_lng)

        if not data.get("rows") or not data["rows"][0].get("elements"):
            logger.warning("Google Distance Matrix API returned empty rows. Status: %s. Falling back to Haversine.", data.get("status"))
            return _haversine_fallback(pickup_lat, pickup_lng, dest_lat, dest_lng)

        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            logger.warning("Distance Matrix returned element status: %s. Falling back to Haversine.", element["status"])
            return _haversine_fallback(pickup_lat, pickup_lng, dest_lat, dest_lng)

        distance_km = round(element["distance"]["value"] / 1000, 2)
        duration_min = round(element["duration"]["value"] / 60, 1)

        logger.info("Distance: %.2f km, Duration: %.1f min", distance_km, duration_min)
        return {
            "distance_km": distance_km,
            "duration_minutes": duration_min,
        }

    except Exception as exc:
        logger.warning("Error calling Distance Matrix API: %s. Falling back to Haversine.", exc)
        return _haversine_fallback(pickup_lat, pickup_lng, dest_lat, dest_lng)


def _haversine_fallback(lat1: float, lon1: float, lat2: float, lon2: float) -> dict[str, Any]:
    """Calculate driving distance/duration estimate using straight-line distance with a 1.2x routing factor."""
    distance = _haversine(lat1, lon1, lat2, lon2)
    driving_distance = distance * 1.2
    # Assume 40 km/h average speed: duration = distance / 40 * 60 = distance / 0.67
    duration_min = driving_distance / 0.667
    return {
        "distance_km": round(driving_distance, 2),
        "duration_minutes": round(duration_min, 1),
    }


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two points."""
    import math

    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
