import sys
import os
import sqlite3
import json
from unittest.mock import MagicMock

# Mock dependencies that might be imported or needed
sys.modules['mqtt_client'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['gemini_client'] = MagicMock()

# Import the functions to test
from database import (
    init_db,
    get_db_connection,
    insert_device_data,
    get_sensor_summary,
    get_energy_analytics,
    get_temp_analytics,
    DB_PATH
)

def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    # Insert some test data
    payload = {
        "temperature": 25.5,
        "humidity": 60.0,
        "co2": 400,
        "powerUsage": 1.2,
        "power": True
    }
    insert_device_data("living-room", "sensor", "esp32-test", "telemetry", payload)

def test_sensor_summary():
    print("Testing get_sensor_summary...")
    summary = get_sensor_summary("esp32-test", hours=24)
    assert summary is not None
    assert summary["temperature"]["avg"] == 25.5
    print("✅ get_sensor_summary passed")

def test_energy_analytics():
    print("Testing get_energy_analytics...")
    analytics = get_energy_analytics("esp32-test", days=1)
    assert len(analytics) > 0
    assert analytics[0]["active"] == 1.2
    print("✅ get_energy_analytics passed")

def test_temp_analytics():
    print("Testing get_temp_analytics...")
    analytics = get_temp_analytics("esp32-test", days=1)
    assert len(analytics) > 0
    assert analytics[0]["indoor"] == 25.5
    print("✅ get_temp_analytics passed")

def test_sql_injection_attempt():
    print("Testing SQL injection prevention...")
    # This should not crash and should return None or empty results if the parameterization works correctly
    # If it was string interpolation, this might cause a syntax error or return unexpected data
    try:
        # Attempting a classic injection: "1) OR 1=1 --"
        # In our case it is datetime('now', '-' || ? || ' hours')
        # So it becomes datetime('now', '-' || '1) OR 1=1 --' || ' hours') which is invalid for SQLite but safe from injection
        summary = get_sensor_summary("esp32-test", hours="1) OR 1=1 --")
        print("✅ SQL injection attempt handled safely (no crash)")
    except Exception as e:
        print(f"❌ SQL injection attempt caused an error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_test_db()
    test_sensor_summary()
    test_energy_analytics()
    test_temp_analytics()
    test_sql_injection_attempt()
    print("\nAll database security tests passed! 🛡️")
