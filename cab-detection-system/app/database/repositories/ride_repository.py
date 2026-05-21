import logging
import uuid
from typing import Optional, Any
from app.database.db import get_db_connection

logger = logging.getLogger(__name__)

def get_or_create_user(name: str, phone: str, email: Optional[str] = None) -> str:
    """Retrieve an existing user's ID by name and phone, or create a new user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE name = ? AND phone = ?",
            (name, phone)
        )
        row = cursor.fetchone()
        if row:
            return row["id"]
        
        # Create new user
        user_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, name, phone, email) VALUES (?, ?, ?, ?)",
            (user_id, name, phone, email)
        )
        conn.commit()
        logger.info("Created new user in database: %s (id=%s)", name, user_id)
        return user_id

def create_ride(
    ride_id: str,
    user_id: Optional[str],
    pickup_address: str,
    pickup_lat: float,
    pickup_lng: float,
    destination_address: str,
    destination_lat: float,
    destination_lng: float,
    distance_km: float,
    duration_minutes: float,
    cab_type: str,
    estimated_fare: float,
    fare_currency: str = "INR"
) -> bool:
    """Insert a new ride record with status 'waiting'."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rides (
                    id, user_id, pickup_address, pickup_lat, pickup_lng,
                    destination_address, destination_lat, destination_lng,
                    distance_km, duration_minutes, cab_type, estimated_fare,
                    fare_currency, ride_status, payment_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'waiting', 'pending')
                """,
                (
                    ride_id, user_id, pickup_address, pickup_lat, pickup_lng,
                    destination_address, destination_lat, destination_lng,
                    distance_km, duration_minutes, cab_type, estimated_fare,
                    fare_currency
                )
            )
            conn.commit()
            logger.info("Saved new ride in database: %s", ride_id)
            return True
    except Exception as e:
        logger.error("Error creating ride: %s", e)
        return False

def update_ride_driver(ride_id: str, driver_id: str) -> bool:
    """Assign a driver to a ride."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rides SET driver_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (driver_id, ride_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error updating ride driver: %s", e)
        return False

def update_ride_status(ride_id: str, status: str) -> bool:
    """Update the status of a ride."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rides SET ride_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, ride_id)
            )
            conn.commit()
            logger.info("Updated ride %s status to %s", ride_id, status)
            return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error updating ride status: %s", e)
        return False

def update_ride_payment(
    ride_id: str,
    payment_status: str,
    payment_method: str,
    transaction_id: str
) -> bool:
    """Update payment details for a ride."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE rides
                SET payment_status = ?, payment_method = ?, transaction_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (payment_status, payment_method, transaction_id, ride_id)
            )
            conn.commit()
            logger.info("Updated ride %s payment status to %s", ride_id, payment_status)
            return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error updating ride payment: %s", e)
        return False

def get_ride(ride_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a ride by its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rides WHERE id = ?", (ride_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
