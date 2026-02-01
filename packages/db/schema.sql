CREATE TABLE IF NOT EXISTS device_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    zone TEXT,
    device_type TEXT,
    device_id TEXT,
    message_type TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=Mon, 6=Sun
    hour INTEGER NOT NULL, -- 0-23
    is_active BOOLEAN DEFAULT 0,
    temp INTEGER DEFAULT 24,
    mode TEXT DEFAULT 'cool',
    UNIQUE(device_id, day_of_week, hour)
);
