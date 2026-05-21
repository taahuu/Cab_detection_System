"""
Search Driver Node
==================
Simulates searching for the nearest available driver
around the pickup location.
"""

import uuid
import random
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Mock driver pool ─────────────────────────────────────────────
_MOCK_DRIVERS = [
    {"name": "Rajesh Kumar",   "phone": "+91-98765-43210", "rating": 4.8, "vehicle": "DL 01 AB 1234"},
    {"name": "Priya Sharma",   "phone": "+91-91234-56789", "rating": 4.9, "vehicle": "MH 12 CD 5678"},
    {"name": "Amit Patel",     "phone": "+91-99887-76655", "rating": 4.6, "vehicle": "KA 05 EF 9012"},
    {"name": "Sunita Reddy",   "phone": "+91-88776-65544", "rating": 4.7, "vehicle": "TN 09 GH 3456"},
]


def search_driver(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: find the nearest available driver from SQLite near the pickup point.

    Reads
    -----
    - ``state["pickup_lat"]``, ``state["pickup_lng"]``

    Writes
    ------
    - ``driver_found``       – whether a driver was matched.
    - ``driver_id``          – unique driver ID.
    - ``driver_name``        – driver's full name.
    - ``driver_phone``       – driver's phone number.
    - ``driver_rating``      – driver's rating (out of 5).
    - ``vehicle_number``     – vehicle registration number.
    - ``driver_eta_minutes`` – estimated time of arrival in minutes.
    """
    from app.database.repositories.driver_repository import get_active_drivers
    from app.graph.nodes.calculate_distance import _haversine

    pickup_lat = state.get("pickup_lat")
    pickup_lng = state.get("pickup_lng")

    if pickup_lat is None or pickup_lng is None:
        logger.warning("No pickup coordinates — cannot search for driver")
        return {
            "driver_found": False,
            "error": "Pickup coordinates are missing.",
        }

    logger.info("Searching for drivers near (%.4f, %.4f) from SQL database", pickup_lat, pickup_lng)

    # Retrieve all active drivers from the database
    active_drivers = get_active_drivers()
    
    if not active_drivers:
        logger.warning("No active drivers found in database")
        return {
            "driver_found": False,
            "driver_id": None,
            "driver_name": None,
            "driver_phone": None,
            "driver_rating": None,
            "vehicle_number": None,
            "driver_eta_minutes": None,
        }

    # Find the nearest driver
    nearest_driver = None
    min_distance = float("inf")

    for driver in active_drivers:
        driver_lat = driver.get("latitude")
        driver_lng = driver.get("longitude")
        
        # If driver has no coordinates, assign default ones (around Delhi) or skip
        if driver_lat is None or driver_lng is None:
            driver_lat, driver_lng = 28.6139, 77.2090

        dist = _haversine(pickup_lat, pickup_lng, driver_lat, driver_lng)
        if dist < min_distance:
            min_distance = dist
            nearest_driver = driver

    if nearest_driver:
        # Calculate a realistic ETA: 3 minutes base + 1.5 minutes per km of distance
        eta = round(3.0 + min_distance * 1.5, 1)
        # Cap ETA at reasonable limits
        eta = max(2.0, min(eta, 25.0))

        logger.info(
            "Nearest driver matched: %s (Dist: %.2f km, ETA: %.1f min)",
            nearest_driver["name"], min_distance, eta
        )
        return {
            "driver_found": True,
            "driver_id": nearest_driver["id"],
            "driver_name": nearest_driver["name"],
            "driver_phone": nearest_driver["phone"],
            "driver_rating": nearest_driver["rating"],
            "vehicle_number": nearest_driver["vehicle_number"],
            "driver_eta_minutes": eta,
        }

    logger.warning("No drivers available at this time")
    return {
        "driver_found": False,
        "driver_id": None,
        "driver_name": None,
        "driver_phone": None,
        "driver_rating": None,
        "vehicle_number": None,
        "driver_eta_minutes": None,
    }
