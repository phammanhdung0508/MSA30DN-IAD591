import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the apps/api directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "apps/api"))

# Mock dependencies that might have side effects on import
sys.modules["mqtt_client"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()

import database

class TestSecurityFixes(unittest.TestCase):
    @patch("database.get_db_connection")
    def test_get_sensor_summary(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Mocking row factory behavior
        mock_cursor.fetchone.return_value = {
            "temp_min": 20, "temp_avg": 22, "temp_max": 24,
            "hum_min": 40, "hum_avg": 45, "hum_max": 50,
            "co2_min": 400, "co2_avg": 450, "co2_max": 500
        }

        result = database.get_sensor_summary("test-device", hours=24)

        self.assertIsNotNone(result)
        self.assertEqual(result["temperature"]["min"], 20)

        # Check if execute was called with parameters
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        self.assertIn("?", query, "Query should be parameterized")
        self.assertEqual(params, ("test-device", 24))

    @patch("database.get_db_connection")
    def test_get_energy_analytics(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"time_bucket": "12:00", "avg_usage": 0.5, "was_active": 1}
        ]

        result = database.get_energy_analytics("test-device", days=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["time"], "12:00")

        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        self.assertIn("?", query, "Query should be parameterized")
        self.assertEqual(params, ("test-device", 1))

    @patch("database.get_db_connection")
    def test_get_temp_analytics(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"time_bucket": "2023-01-01 12:00", "avg_indoor": 22.5}
        ]

        result = database.get_temp_analytics("test-device", days=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["time"], "12:00")

        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        self.assertIn("?", query, "Query should be parameterized")
        self.assertEqual(params, ("test-device", 1))

    def test_cors_config(self):
        with open("apps/api/main.py", "r") as f:
            content = f.read()

        self.assertIn("allow_credentials=False", content, "CORS allow_credentials should be False when allow_origins is '*'")

if __name__ == "__main__":
    unittest.main()
