"""
Track Ride Node
===============
Simulates real-time ride tracking. In production this would
integrate with a WebSocket / polling service.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def track_ride(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: track the ride in progress.

    Reads
    -----
    - ``state["ride_id"]``
    - ``state["driver_id"]``
    - ``state["destination_lat"]``, ``state["destination_lng"]``

    Writes
    ------
    - ``ride_status``        – updated to ``"in_progress"`` then ``"arrived"``.
    - ``current_driver_lat`` – simulated driver position.
    - ``current_driver_lng`` – simulated driver position.
    """
    ride_id = state.get("ride_id")
    driver_id = state.get("driver_id")

    if not ride_id:
        logger.error("Cannot track ride: ride_id is missing")
        return {
            "ride_status": "error",
            "error": "Ride ID is missing.",
        }

    logger.info("Tracking ride %s", ride_id)

    from app.database.repositories.ride_repository import update_ride_status
    from app.database.repositories.driver_repository import update_driver_location

    # Transition status: first in progress, then arrived
    update_ride_status(ride_id, "in_progress")
    
    dest_lat = state.get("destination_lat")
    dest_lng = state.get("destination_lng")
    
    if driver_id and dest_lat is not None and dest_lng is not None:
        update_driver_location(driver_id, dest_lat, dest_lng)
        
    update_ride_status(ride_id, "arrived")

    return {
        "ride_status": "arrived",
        "current_driver_lat": dest_lat,
        "current_driver_lng": dest_lng,
    }
