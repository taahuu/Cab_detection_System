"""
Complete Ride Node
==================
Final node in the ride workflow. Marks the ride as completed
and generates a summary for the user.
"""

import logging
from typing import Any

from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)
from app.utils.helpers import format_duration_hours


def complete_ride(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: finalise the ride and produce a summary.

    Reads
    -----
    - Most state fields to compile a final summary.

    Writes
    ------
    - ``ride_completed`` – ``True``.
    - ``ride_status``    – ``"completed"``.
    - ``ride_summary``   – human-readable summary string.
    - ``messages``       – appended final summary message.
    """
    summary = (
        "✅ Ride Completed!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  🆔 Ride ID:      {state.get('ride_id', 'N/A')}\n"
        f"  📍 From:         {state.get('pickup_formatted_address', 'N/A')}\n"
        f"  📍 To:           {state.get('destination_formatted_address', 'N/A')}\n"
        f"  📏 Distance:     {state.get('distance_km', 'N/A')} km\n"
        f"  ⏱️  Duration:     {format_duration_hours(state.get('duration_minutes'))}\n"
        f"  👤 Driver:       {state.get('driver_name', 'N/A')}\n"
        f"  🚙 Vehicle:      {state.get('vehicle_number', 'N/A')}\n"
        f"  💰 Amount Paid:  {state.get('fare_currency', 'INR')} "
        f"{state.get('payment_amount', 'N/A')}\n"
        f"  💳 Payment:      {state.get('payment_method', 'N/A')} "
        f"({state.get('payment_status', 'N/A')})\n"
        f"  🧾 Transaction:  {state.get('transaction_id', 'N/A')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Thank you for riding with us! 🙏"
    )

    logger.info("Ride %s completed successfully", state.get("ride_id"))

    ride_id = state.get("ride_id")
    if ride_id:
        from app.database.repositories.ride_repository import update_ride_status
        update_ride_status(ride_id, "completed")

    return {
        "ride_completed": True,
        "ride_status": "completed",
        "ride_summary": summary,
        "messages": [AIMessage(content=summary)],
    }
