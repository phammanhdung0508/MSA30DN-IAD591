import sqlite3
import os
import sys
from unittest.mock import MagicMock, patch

# Mocking parts of the app to test database.py in isolation
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['gemini_client'] = MagicMock()

import apps.api.database as database

def test_sql_injection_pattern():
    print("Checking for SQL injection patterns in database.py...")

    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Test get_sensor_summary
        database.get_sensor_summary("test_device", hours=24)
        call_args = mock_cursor.execute.call_args[0]
        query = call_args[0]
        if "'-24 hours'" in query:
            print("[!] Vulnerable pattern found in get_sensor_summary: value interpolated in query string")
        else:
            print("[✓] get_sensor_summary seems to use parameterization for hours")

        # Test get_energy_analytics
        database.get_energy_analytics("test_device", days=1)
        call_args = mock_cursor.execute.call_args[0]
        query = call_args[0]
        if "'-1 days'" in query:
            print("[!] Vulnerable pattern found in get_energy_analytics: value interpolated in query string")
        else:
            print("[✓] get_energy_analytics seems to use parameterization for days")

        # Test get_temp_analytics
        database.get_temp_analytics("test_device", days=1)
        call_args = mock_cursor.execute.call_args[0]
        query = call_args[0]
        if "'-1 days'" in query:
            print("[!] Vulnerable pattern found in get_temp_analytics: value interpolated in query string")
        else:
            print("[✓] get_temp_analytics seems to use parameterization for days")

if __name__ == "__main__":
    test_sql_injection_pattern()
