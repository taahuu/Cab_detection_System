import logging
from typing import Optional, Any
from app.database.db import get_db_connection

logger = logging.getLogger(__name__)

def get_active_drivers() -> list[dict[str, Any]]:
    """Retrieve all active drivers from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, phone, vehicle_number, rating, status, latitude, longitude FROM drivers WHERE status = 'active'"
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_driver_location(driver_id: str, lat: float, lng: float) -> bool:
    """Update a driver's current coordinates."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE drivers SET latitude = ?, longitude = ? WHERE id = ?",
                (lat, lng, driver_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error updating driver location: %s", e)
        return False

def update_driver_status(driver_id: str, status: str) -> bool:
    """Update driver status (e.g. 'active', 'inactive')."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE drivers SET status = ? WHERE id = ?",
                (status, driver_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error updating driver status: %s", e)
        return False
