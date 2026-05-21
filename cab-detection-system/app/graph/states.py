"""
Ride Graph State
================
Defines the shared state schema used by all nodes and edges
in the cab-detection-system LangGraph ride workflow.
"""

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class RideState(TypedDict, total=False):
    """Shared state flowing through every node of the ride graph.

    Fields are grouped by the node that typically writes them.
    ``messages`` uses LangGraph's built-in message reducer so that
    each node can *append* messages rather than overwrite.
    """

    # ── Chat history (LLM conversation) ──────────────────────────
    messages: Annotated[list, add_messages]

    # ── User Details ─────────────────────────────────────────────
    user_id: Optional[str]
    user_name: Optional[str]
    user_phone: Optional[str]

    # ── Collect Location ─────────────────────────────────────────
    pickup_address: Optional[str]
    pickup_lat: Optional[float]
    pickup_lng: Optional[float]
    pickup_formatted_address: Optional[str]

    # ── Collect Destination ──────────────────────────────────────
    destination_address: Optional[str]

    # ── Geocode Destination ──────────────────────────────────────
    destination_lat: Optional[float]
    destination_lng: Optional[float]
    destination_formatted_address: Optional[str]
    geocode_status: Optional[str]       # "ok" | "geocoding_failed" | "error"
    geocode_error: Optional[str]

    # ── Calculate Distance ───────────────────────────────────────
    distance_km: Optional[float]
    duration_minutes: Optional[float]

    # ── Calculate Fare ───────────────────────────────────────────
    estimated_fare: Optional[float]
    fare_currency: Optional[str]
    cab_type: Optional[str]             # "mini" | "sedan" | "suv" | "premium"

    # ── Search Driver ────────────────────────────────────────────
    driver_found: Optional[bool]
    driver_id: Optional[str]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    driver_rating: Optional[float]
    vehicle_number: Optional[str]
    driver_eta_minutes: Optional[float]

    # ── Confirm Ride ─────────────────────────────────────────────
    ride_confirmed: Optional[bool]
    ride_id: Optional[str]

    # ── Track Ride ───────────────────────────────────────────────
    ride_status: Optional[str]          # "waiting" | "in_progress" | "arrived" | "completed" | "cancelled"
    current_driver_lat: Optional[float]
    current_driver_lng: Optional[float]

    # ── Process Payment ──────────────────────────────────────────
    payment_method: Optional[str]       # "cash" | "card" | "upi" | "wallet"
    payment_status: Optional[str]       # "pending" | "success" | "failed"
    payment_amount: Optional[float]
    transaction_id: Optional[str]

    # ── Complete Ride ────────────────────────────────────────────
    ride_completed: Optional[bool]
    ride_summary: Optional[str]

    # ── Error handling ───────────────────────────────────────────
    error: Optional[str]
