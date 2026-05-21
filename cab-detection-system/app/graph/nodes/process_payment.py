"""
Process Payment Node
====================
Processes the ride payment. Currently simulates a successful
transaction — in production, integrate with a payment gateway
(Razorpay, Stripe, etc.).
"""

import uuid
import logging
from typing import Any

logger = logging.getLogger(__name__)


def process_payment(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: process payment for the completed ride.

    Reads
    -----
    - ``state["estimated_fare"]``
    - ``state["fare_currency"]``
    - ``state["payment_method"]`` (optional, defaults to ``"cash"``)

    Writes
    ------
    - ``payment_method``  – confirmed method.
    - ``payment_status``  – ``"success"`` or ``"failed"``.
    - ``payment_amount``  – the amount charged.
    - ``transaction_id``  – unique transaction identifier.
    """
    fare = state.get("estimated_fare")
    currency = state.get("fare_currency", "INR")
    method = state.get("payment_method", "cash")
    ride_id = state.get("ride_id")

    if fare is None:
        logger.error("Cannot process payment: fare is missing")
        return {
            "payment_status": "failed",
            "error": "Fare amount is missing.",
        }

    # Simulate payment processing
    transaction_id = str(uuid.uuid4())

    logger.info(
        "Payment processed: %s %.2f via %s (txn: %s)",
        currency, fare, method, transaction_id,
    )

    if ride_id:
        from app.database.repositories.payment_repository import record_payment
        record_payment(
            ride_id=ride_id,
            payment_method=method,
            transaction_id=transaction_id,
            amount=fare,
            status="success"
        )

    return {
        "payment_method": method,
        "payment_status": "success",
        "payment_amount": fare,
        "transaction_id": transaction_id,
    }
