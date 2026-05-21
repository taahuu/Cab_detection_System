"""
Confirm Ride Node
=================
Presents the ride details to the user via the LLM and asks
for confirmation before dispatching the driver.
"""

import os
import logging
from typing import Any

from app.utils.llm_fallback import SafeChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
from app.utils.helpers import format_duration_hours

model = SafeChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def confirm_ride(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: confirm ride details with the user.

    Reads
    -----
    - Pickup and destination addresses, fare, driver info, ETA.

    Writes
    ------
    - ``ride_confirmed`` – ``True`` if user confirms, ``False`` otherwise.
    - ``ride_id``        – generated ride ID upon confirmation.
    - ``messages``       – appended summary message.
    """
    import uuid

    summary = (
        f"🚕 Ride Summary:\n"
        f"  📍 Pickup:      {state.get('pickup_formatted_address', 'N/A')}\n"
        f"  📍 Destination: {state.get('destination_formatted_address', 'N/A')}\n"
        f"  📏 Distance:    {state.get('distance_km', 'N/A')} km\n"
        f"  ⏱️  Duration:    {format_duration_hours(state.get('duration_minutes'))}\n"
        f"  💰 Fare:        {state.get('fare_currency', 'INR')} {state.get('estimated_fare', 'N/A')}\n"
        f"  🚗 Cab Type:    {state.get('cab_type', 'N/A')}\n"
        f"  👤 Driver:      {state.get('driver_name', 'N/A')} "
        f"(⭐ {state.get('driver_rating', 'N/A')})\n"
        f"  🚙 Vehicle:     {state.get('vehicle_number', 'N/A')}\n"
        f"  ⏳ Driver ETA:  {state.get('driver_eta_minutes', 'N/A')} min\n"
    )

    system_prompt = SystemMessage(
        content=(
            "You are a cab-booking assistant. Present the following ride summary "
            "to the user and ask them to confirm the ride. If the user's last "
            "message indicates confirmation (yes, ok, confirm, sure, etc.), "
            "respond with exactly 'CONFIRMED'. If they decline, respond with "
            "exactly 'CANCELLED'.\n\n" + summary
        )
    )

    messages = state.get("messages", [])
    response = model.invoke([system_prompt] + messages)
    reply = response.content.strip().upper()

    confirmed = "CONFIRMED" in reply
    ride_id = str(uuid.uuid4()) if confirmed else None

    logger.info("Ride confirmation: %s (ride_id=%s)", "YES" if confirmed else "NO", ride_id)

    if confirmed:
        from app.database.repositories.ride_repository import create_ride, update_ride_driver
        create_ride(
            ride_id=ride_id,
            user_id=state.get("user_id"),
            pickup_address=state.get("pickup_formatted_address") or state.get("pickup_address", ""),
            pickup_lat=state.get("pickup_lat"),
            pickup_lng=state.get("pickup_lng"),
            destination_address=state.get("destination_formatted_address") or state.get("destination_address", ""),
            destination_lat=state.get("destination_lat"),
            destination_lng=state.get("destination_lng"),
            distance_km=state.get("distance_km"),
            duration_minutes=state.get("duration_minutes"),
            cab_type=state.get("cab_type"),
            estimated_fare=state.get("estimated_fare"),
            fare_currency=state.get("fare_currency", "INR")
        )
        if state.get("driver_id"):
            update_ride_driver(ride_id, state.get("driver_id"))

    return {
        "ride_confirmed": confirmed,
        "ride_id": ride_id,
        "messages": [response],
    }
