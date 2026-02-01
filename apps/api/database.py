import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
DB_DIR = os.path.join(PROJECT_ROOT, "packages", "db")
DB_PATH = os.path.join(DB_DIR, "smarthome.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
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
        
def get_temp_analytics(device_id: str, days: int = 7):
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        # Group by Day
        cursor.execute(f'''
            SELECT 
                strftime('%w', timestamp) as day_num,
                strftime('%Y-%m-%d', timestamp) as date_str,
                AVG(json_extract(payload, '$.temperature')) as avg_indoor
            FROM device_data
            WHERE device_id = ?
              AND timestamp >= datetime('now', '-{days} days')
            GROUP BY date_str, day_num
            ORDER BY date_str ASC
        ''', (device_id,))
        
        rows = cursor.fetchall()
        week_map = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        result = []
        for row in rows:
            day_str = week_map[int(row['day_num'])]
            result.append({
                "time": day_str,
                "indoor": round(row['avg_indoor'] or 0, 1),
                "outdoor": 32 # Hardcode or fetch if available
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
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT day_of_week, hour, is_active 
            FROM schedules 
            WHERE device_id = ?
        ''', (device_id,))
        rows = cursor.fetchall()
        
        # Transform to 7x24 grid
        # Initialize empty grid
        grid = [[False for _ in range(24)] for _ in range(7)]
        
        for row in rows:
            d = row['day_of_week']
            h = row['hour']
            if 0 <= d < 7 and 0 <= h < 24:
                grid[d][h] = bool(row['is_active'])
                
        return grid
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
