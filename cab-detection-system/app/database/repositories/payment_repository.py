import logging
from app.database.repositories.ride_repository import update_ride_payment

logger = logging.getLogger(__name__)

def record_payment(ride_id: str, payment_method: str, transaction_id: str, amount: float, status: str = "success") -> bool:
    """Record a payment transaction for a ride by updating its payment fields in the database."""
    logger.info("Recording payment for ride %s: %.2f via %s (txn: %s)", ride_id, amount, payment_method, transaction_id)
    return update_ride_payment(
        ride_id=ride_id,
        payment_status=status,
        payment_method=payment_method,
        transaction_id=transaction_id
    )
