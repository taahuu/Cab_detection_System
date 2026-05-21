import os
import sqlite3
import logging
import uuid

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "taxi_system.db"
)

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "schema.sql"
)

def get_db_connection():
    """Return a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize tables using schema.sql and seed drivers if empty."""
    logger.info("Initializing database at %s", DB_PATH)
    
    if not os.path.exists(SCHEMA_PATH):
        logger.error("Schema file not found at %s", SCHEMA_PATH)
        return
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with get_db_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()
        
    seed_drivers_if_empty()

def seed_drivers_if_empty():
    """Seed default drivers if the drivers table is empty."""
    default_drivers = [
        {"name": "Rajesh Kumar", "phone": "+91-98765-43210", "rating": 4.8, "vehicle": "DL 01 AB 1234", "lat": 28.6200, "lng": 77.2100},
        {"name": "Priya Sharma", "phone": "+91-91234-56789", "rating": 4.9, "vehicle": "MH 12 CD 5678", "lat": 28.6100, "lng": 77.2200},
        {"name": "Amit Patel", "phone": "+91-99887-76655", "rating": 4.6, "vehicle": "KA 05 EF 9012", "lat": 28.6300, "lng": 77.1900},
        {"name": "Sunita Reddy", "phone": "+91-88776-65544", "rating": 4.7, "vehicle": "TN 09 GH 3456", "lat": 28.6000, "lng": 77.2000},
    ]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM drivers")
        count = cursor.fetchone()[0]
        if count == 0:
            logger.info("Seeding default drivers into database")
            for driver in default_drivers:
                driver_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO drivers (id, name, phone, vehicle_number, rating, status, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                    """,
                    (
                        driver_id,
                        driver["name"],
                        driver["phone"],
                        driver["vehicle"],
                        driver["rating"],
                        driver["lat"],
                        driver["lng"]
                    )
                )
            conn.commit()

# Run initialization
init_db()
