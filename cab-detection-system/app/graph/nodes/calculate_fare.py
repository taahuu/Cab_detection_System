"""
Calculate Fare Node
===================
Estimates the ride fare based on distance, duration, and cab type.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Pricing tiers (per km / per minute / base fare) ──────────────
PRICING = {
    "mini":    {"base": 30.0,  "per_km": 8.0,   "per_min": 1.5},
    "sedan":   {"base": 50.0,  "per_km": 12.0,  "per_min": 2.0},
    "suv":     {"base": 80.0,  "per_km": 16.0,  "per_min": 2.5},
    "premium": {"base": 120.0, "per_km": 22.0,  "per_min": 3.5},
}

DEFAULT_CAB_TYPE = "sedan"
DEFAULT_CURRENCY = "INR"


def calculate_fare(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: estimate the ride fare.

    Reads
    -----
    - ``state["distance_km"]``
    - ``state["duration_minutes"]``
    - ``state["cab_type"]`` (optional, defaults to ``"sedan"``)

    Writes
    ------
    - ``estimated_fare`` – total estimated fare.
    - ``fare_currency``  – currency code (e.g. ``"INR"``).
    - ``cab_type``       – confirmed cab type used for pricing.
    """
    distance = state.get("distance_km")
    duration = state.get("duration_minutes")
    cab_type = state.get("cab_type", DEFAULT_CAB_TYPE).lower()

    if distance is None or duration is None:
        logger.error("Cannot calculate fare: missing distance or duration")
        return {
            "estimated_fare": None,
            "fare_currency": DEFAULT_CURRENCY,
            "cab_type": cab_type,
            "error": "Distance or duration is missing.",
        }

    tier = PRICING.get(cab_type, PRICING[DEFAULT_CAB_TYPE])

    fare = tier["base"] + (tier["per_km"] * distance) + (tier["per_min"] * duration)
    fare = round(fare, 2)

    logger.info(
        "Fare calculated: %s %.2f (%s, %.2f km, %.1f min)",
        DEFAULT_CURRENCY, fare, cab_type, distance, duration,
    )

    return {
        "estimated_fare": fare,
        "fare_currency": DEFAULT_CURRENCY,
        "cab_type": cab_type,
    }
