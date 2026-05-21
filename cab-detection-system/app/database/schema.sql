CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drivers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    vehicle_number TEXT NOT NULL,
    rating REAL DEFAULT 5.0,
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rides (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    driver_id TEXT,
    pickup_address TEXT NOT NULL,
    pickup_lat REAL,
    pickup_lng REAL,
    destination_address TEXT NOT NULL,
    destination_lat REAL,
    destination_lng REAL,
    distance_km REAL,
    duration_minutes REAL,
    cab_type TEXT,
    estimated_fare REAL,
    fare_currency TEXT DEFAULT 'INR',
    ride_status TEXT CHECK(ride_status IN ('waiting', 'in_progress', 'arrived', 'completed', 'cancelled', 'error')) DEFAULT 'waiting',
    payment_status TEXT CHECK(payment_status IN ('pending', 'success', 'failed')) DEFAULT 'pending',
    payment_method TEXT,
    transaction_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(driver_id) REFERENCES drivers(id)
);

CREATE TABLE IF NOT EXISTS geocode_cache (
    address TEXT PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    formatted_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
