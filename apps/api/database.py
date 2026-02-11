import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
DEFAULT_DB_DIR = os.path.join(PROJECT_ROOT, "packages", "db")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "smarthome.db")

DB_PATH = os.getenv("SQLITE_DB_PATH", DEFAULT_DB_PATH)
SCHEMA_PATH = os.path.join(DEFAULT_DB_DIR, "schema.sql")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    conn = get_db_connection()
    if conn:
        try:
            with open(SCHEMA_PATH, 'r') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        finally:
            conn.close()

def _empty_schedule():
    return [[False for _ in range(24)] for _ in range(7)]

def insert_device_data(zone, device_type, device_id, message_type, payload):
    conn = get_db_connection()
    if conn:
        try:
            if isinstance(payload, dict):
                payload_str = json.dumps(payload)
            else:
                payload_str = str(payload)
                
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO device_data (zone, device_type, device_id, message_type, payload)
                VALUES (?, ?, ?, ?, ?)
            ''', (zone, device_type, device_id, message_type, payload_str))
            conn.commit()
            logger.info(f"Data saved to DB: {zone}/{device_type}/{device_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert data: {e}")
        finally:
            conn.close()

def get_latest_device_data(device_id: str):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT payload, timestamp FROM device_data 
                WHERE device_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (device_id,))
            row = cursor.fetchone()
            if row:
                try:
                    return {
                        "timestamp": row['timestamp'],
                        "data": json.loads(row['payload'])
                    }
                except json.JSONDecodeError:
                    return {
                        "timestamp": row['timestamp'],
                        "data": row['payload']
                    }
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch data: {e}")
            return None
        finally:
            conn.close()
    return None

def get_latest_sensor_with_values(device_id: str):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT payload, timestamp FROM device_data
            WHERE device_id = ?
              AND json_extract(payload, '$.temperature') IS NOT NULL
              AND json_extract(payload, '$.humidity') IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (device_id,))
        row = cursor.fetchone()
        if row:
            try:
                return {
                    "timestamp": row['timestamp'],
                    "data": json.loads(row['payload'])
                }
            except json.JSONDecodeError:
                return {
                    "timestamp": row['timestamp'],
                    "data": row['payload']
                }
        return None
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch latest sensor values: {e}")
        return None
    finally:
        conn.close()

def get_device_data_history(device_id: str, limit: int = 100):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT payload, timestamp FROM device_data
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (device_id, limit))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            try:
                payload = json.loads(row['payload'])
            except json.JSONDecodeError:
                payload = row['payload']
            result.append({
                "timestamp": row['timestamp'],
                "data": payload
            })
        return result
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch history: {e}")
        return []
    finally:
        conn.close()

def get_sensor_summary(device_id: str, hours: int = 24):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT
                MIN(json_extract(payload, '$.temperature')) as temp_min,
                AVG(json_extract(payload, '$.temperature')) as temp_avg,
                MAX(json_extract(payload, '$.temperature')) as temp_max,
                MIN(json_extract(payload, '$.humidity')) as hum_min,
                AVG(json_extract(payload, '$.humidity')) as hum_avg,
                MAX(json_extract(payload, '$.humidity')) as hum_max,
                MIN(json_extract(payload, '$.co2')) as co2_min,
                AVG(json_extract(payload, '$.co2')) as co2_avg,
                MAX(json_extract(payload, '$.co2')) as co2_max
            FROM device_data
            WHERE device_id = ?
              AND timestamp >= datetime('now', '-{hours} hours')
        ''', (device_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "temperature": {
                "min": row["temp_min"],
                "avg": row["temp_avg"],
                "max": row["temp_max"],
            },
            "humidity": {
                "min": row["hum_min"],
                "avg": row["hum_avg"],
                "max": row["hum_max"],
            },
            "co2": {
                "min": row["co2_min"],
                "avg": row["co2_avg"],
                "max": row["co2_max"],
            },
        }
    except sqlite3.Error as e:
        logger.error(f"Summary query failed: {e}")
        return None
    finally:
        conn.close()

# --- Analytics Functions ---

def get_energy_analytics(device_id: str, days: int = 1):
    """
    Returns aggregated power usage per hour for the last N days.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        # SQLite json_extract might vary by version, but this is standard for recent ones.
        # We group by hour and take average of powerUsage.
        # timestamp format: YYYY-MM-DD HH:MM:SS
        cursor.execute(f'''
            SELECT 
                strftime('%H:00', timestamp) as time_bucket,
                AVG(json_extract(payload, '$.powerUsage')) as avg_usage,
                MAX(json_extract(payload, '$.power')) as was_active
            FROM device_data
            WHERE device_id = ? 
              AND timestamp >= datetime('now', '-{days} days')
            GROUP BY time_bucket
            ORDER BY time_bucket ASC
        ''', (device_id,))
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            # Format to match frontend: { time: "00:00", active: 0.2, idle: 0.1 }
            # usage = row['avg_usage'] or 0
            # We'll split usage into 'active' (if avg > 0) or just return usage
            usage = row['avg_usage'] if row['avg_usage'] is not None else 0
            result.append({
                "time": row['time_bucket'],
                "active": round(usage, 2),
                "idle": 0.1 # Placeholder or calculated base load
            })
            
        return result
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return []
    finally:
        conn.close()
        
def get_temp_analytics(device_id: str, days: int = 1):
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        # Group by Hour for proper time trend
        cursor.execute(f'''
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as time_bucket,
                AVG(json_extract(payload, '$.temperature')) as avg_indoor
            FROM device_data
            WHERE device_id = ?
              AND timestamp >= datetime('now', '-{days} days')
            GROUP BY time_bucket
            ORDER BY time_bucket ASC
        ''', (device_id,))
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            # Format time as HH:mm
            # time_bucket is "YYYY-MM-DD HH:00"
            time_str = row['time_bucket'][11:16] 
            
            result.append({
                "time": time_str,
                "indoor": round(row['avg_indoor'] or 0, 1),
            })
        return result
    except Exception as e:
        logger.error(f"Temp analytics error: {e}")
        return []
    finally:
        conn.close()

# --- Schedule Functions ---

def get_schedule(device_id: str):
    conn = get_db_connection()
    if not conn:
        return _empty_schedule()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT day_of_week, hour, is_active 
            FROM schedules 
            WHERE device_id = ?
        ''', (device_id,))
        rows = cursor.fetchall()
        
        # Transform to 7x24 grid
        grid = _empty_schedule()
        
        for row in rows:
            d = row['day_of_week']
            h = row['hour']
            if 0 <= d < 7 and 0 <= h < 24:
                grid[d][h] = bool(row['is_active'])
                
        return grid
    except Exception as e:
        logger.error(f"Get schedule error: {e}")
        return _empty_schedule()
    finally:
        conn.close()

def save_schedule(device_id: str, schedule_grid):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        # Transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Clear old schedule for this device (or upsert, but clear+insert is easier for full save)
        cursor.execute("DELETE FROM schedules WHERE device_id = ?", (device_id,))
        
        # Insert new
        params = []
        for d in range(7):
            for h in range(24):
                is_active = schedule_grid[d][h]
                if is_active: # Only store active slots to save space? Or store all. 
                    # Store only active for sparse, or all if we want explicit off.
                    # Let's store only active is cleaner, but make sure to delete first (DONE).
                    params.append((device_id, d, h, 1))
        
        if params:
            cursor.executemany('''
                INSERT INTO schedules (device_id, day_of_week, hour, is_active)
                VALUES (?, ?, ?, ?)
            ''', params)
            
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Save schedule error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# --- Chat Functions ---

def create_chat_session(session_id: str | None = None, source: str | None = None) -> str:
    sid = session_id or str(uuid4())
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO chat_sessions (id, source)
                VALUES (?, ?)
            ''', (sid, source))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create chat session: {e}")
        finally:
            conn.close()
    return sid

def add_chat_message(session_id: str, role: str, text: str, meta: dict | None = None):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        meta_str = json.dumps(meta) if meta else None
        cursor.execute('''
            INSERT INTO chat_messages (session_id, role, text, meta)
            VALUES (?, ?, ?, ?)
        ''', (session_id, role, text, meta_str))
        msg_id = cursor.lastrowid
        cursor.execute('''
            SELECT created_at FROM chat_messages WHERE id = ?
        ''', (msg_id,))
        row = cursor.fetchone()
        conn.commit()
        return {"id": msg_id, "created_at": row["created_at"] if row else None}
    except sqlite3.Error as e:
        logger.error(f"Failed to insert chat message: {e}")
        return None
    finally:
        conn.close()

def get_chat_history(session_id: str, limit: int = 200):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, role, text, meta, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
        ''', (session_id, limit))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            meta = None
            if row["meta"]:
                try:
                    meta = json.loads(row["meta"])
                except json.JSONDecodeError:
                    meta = row["meta"]
            result.append({
                "id": row["id"],
                "role": row["role"],
                "text": row["text"],
                "meta": meta,
                "ts": row["created_at"]
            })
        return result
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch chat history: {e}")
        return []
    finally:
        conn.close()

def get_last_messages(session_id: str, limit: int = 2):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, role, text, meta, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        ''', (session_id, limit))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            meta = None
            if row["meta"]:
                try:
                    meta = json.loads(row["meta"])
                except json.JSONDecodeError:
                    meta = row["meta"]
            result.append({
                "id": row["id"],
                "role": row["role"],
                "text": row["text"],
                "meta": meta,
                "ts": row["created_at"]
            })
        return result
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch last chat messages: {e}")
        return []
    finally:
        conn.close()
