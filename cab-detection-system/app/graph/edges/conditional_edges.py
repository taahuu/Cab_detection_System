"""
Conditional Edges
=================
Router functions used by LangGraph to decide which node
to transition to based on the current state.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def route_after_geocode(state: dict[str, Any]) -> str:
    """After geocoding, check if it succeeded.

    Returns
    -------
    - ``"calculate_distance"`` – geocoding was successful.
    - ``"collect_destination"`` – geocoding failed; re-ask the user.
    """
    if state.get("geocode_status") == "ok":
        logger.info("Geocoding succeeded – proceeding to calculate_distance")
        return "calculate_distance"

    logger.warning("Geocoding failed – routing back to collect_destination")
    return "collect_destination"


def route_after_driver_search(state: dict[str, Any]) -> str:
    """After searching for a driver, check if one was found.

    Returns
    -------
    - ``"confirm_ride"`` – a driver was matched.
    - ``"search_driver"`` – no driver found; retry search.
    """
    if state.get("driver_found"):
        logger.info("Driver found – proceeding to confirm_ride")
        return "confirm_ride"

    logger.warning("No driver found – retrying search_driver")
    return "search_driver"


def route_after_confirm(state: dict[str, Any]) -> str:
    """After the user confirms or cancels the ride.

    Returns
    -------
    - ``"track_ride"`` – ride confirmed by user.
    - ``"__end__"``    – user cancelled the ride.
    """
    if state.get("ride_confirmed"):
        logger.info("Ride confirmed – proceeding to track_ride")
        return "track_ride"

    logger.info("Ride cancelled by user – ending graph")
    return "__end__"


def route_after_payment(state: dict[str, Any]) -> str:
    """After processing payment, check if it succeeded.

    Returns
    -------
    - ``"complete_ride"`` – payment successful.
    - ``"process_payment"`` – payment failed; retry.
    """
    if state.get("payment_status") == "success":
        logger.info("Payment successful – proceeding to complete_ride")
        return "complete_ride"

    logger.warning("Payment failed – retrying process_payment")
    return "process_payment"
