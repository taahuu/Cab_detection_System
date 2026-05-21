"""
Collect Location Node
=====================
Collects the user's current pickup location and geocodes it
into coordinates.
"""

import os
import logging
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


def collect_location(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: collect and geocode the user's pickup location.

    Reads
    -----
    - ``state["pickup_address"]`` - if already populated.
    - ``state["messages"]`` – looks for the latest user message containing
      a pickup address.

    Writes
    ------
    - ``pickup_address``           – raw address string.
    - ``pickup_lat``               – latitude of pickup point.
    - ``pickup_lng``               – longitude of pickup point.
    - ``pickup_formatted_address`` – formatted address from geocoder.
    """
    from app.utils.helpers import geocode_location
    from app.database.repositories.ride_repository import get_or_create_user

    user_name = state.get("user_name", "Guest User")
    user_phone = state.get("user_phone", "+91-99999-99999")
    user_id = get_or_create_user(user_name, user_phone)

    pickup_address = state.get("pickup_address")

    if not pickup_address:
        messages = state.get("messages", [])

        # Extract pickup address from the latest user message
        for msg in reversed(messages):
            content = msg.content if hasattr(msg, "content") else str(msg)
            if content.strip():
                pickup_address = content.strip()
                break

    if not pickup_address:
        logger.warning("No pickup address found in messages or state")
        return {
            "user_id": user_id,
            "pickup_address": None,
            "pickup_lat": None,
            "pickup_lng": None,
            "pickup_formatted_address": None,
            "error": "Pickup address is missing.",
        }

    # Clean prefix if any
    pickup_address_lower = pickup_address.lower()
    if pickup_address_lower.startswith("pickup:"):
        pickup_address = pickup_address[len("pickup:"):].strip()

    logger.info("Collecting pickup location: %s", pickup_address)

    # Perform geocoding (checks cache, Google Maps, Nominatim, mock)
    lat, lng, formatted = geocode_location(pickup_address)
    
    return {
        "user_id": user_id,
        "pickup_address": pickup_address,
        "pickup_lat": lat,
        "pickup_lng": lng,
        "pickup_formatted_address": formatted,
    }