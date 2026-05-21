"""
Geocode Destination Node
========================
LangGraph node that converts a user-provided destination address
into geographic coordinates (latitude, longitude) using the
Google Maps Geocoding API (via the geocoding tool).

This node reads `destination_address` from the graph state,
geocodes it, and writes back `destination_lat`, `destination_lng`,
and `destination_formatted_address`.
"""

import os
import logging
from typing import Any

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Geocoding Tool – callable by the LLM agent
# ---------------------------------------------------------------------------

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


@tool
def geocode_address(address: str) -> dict:
    """Convert a human-readable address into latitude and longitude
    coordinates using the Google Maps Geocoding API or keyless fallbacks.

    Args:
        address: The destination address to geocode (e.g. "Times Square, New York").

    Returns:
        A dict with keys: latitude, longitude, formatted_address, and status.
    """
    from app.utils.helpers import geocode_location

    try:
        lat, lng, formatted = geocode_location(address)
        return {
            "status": "ok",
            "latitude": lat,
            "longitude": lng,
            "formatted_address": formatted,
        }
    except Exception as exc:
        logger.error("Error geocoding address '%s': %s", address, exc)
        return {
            "status": "error",
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# LangGraph Node
# ---------------------------------------------------------------------------

def geocode_destination(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: geocode the user's destination address.

    Reads
    -----
    - ``state["destination_address"]`` – the raw address string provided by the user.

    Writes
    ------
    - ``destination_lat``              – latitude of the destination.
    - ``destination_lng``              – longitude of the destination.
    - ``destination_formatted_address`` – cleaned/formatted address from the API.
    - ``geocode_status``               – "ok" | "geocoding_failed" | "error".
    - ``geocode_error``                – error message (if any).

    If `destination_address` is missing or empty the node short-circuits
    with a ``geocode_status`` of ``"error"``.
    """
    destination_address: str = state.get("destination_address", "").strip()

    if not destination_address:
        logger.warning("geocode_destination invoked with empty destination_address")
        return {
            "destination_lat": None,
            "destination_lng": None,
            "destination_formatted_address": None,
            "geocode_status": "error",
            "geocode_error": "Destination address is missing or empty.",
        }

    logger.info("Geocoding destination: %s", destination_address)
    result = geocode_address.invoke({"address": destination_address})

    return {
        "destination_lat": result.get("latitude"),
        "destination_lng": result.get("longitude"),
        "destination_formatted_address": result.get("formatted_address"),
        "geocode_status": result.get("status", "error"),
        "geocode_error": result.get("error"),
    }
