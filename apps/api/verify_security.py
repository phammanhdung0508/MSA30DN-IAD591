import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock modules that might have side effects on import
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()

import apps.api.database as database
import apps.api.main as main

class TestSecurity(unittest.TestCase):
    def test_sql_parameterization(self):
        """Verify that specific database functions use parameterized queries for intervals."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('apps.api.database.get_db_connection', return_value=mock_conn):
            # Test get_sensor_summary
            database.get_sensor_summary("test-device", hours=24)
            args, _ = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]
            self.assertIn("?", query)
            self.assertIn("datetime('now', '-' || ? || ' hours')", query)
            self.assertEqual(params, ("test-device", 24))

            # Test get_energy_analytics
            database.get_energy_analytics("test-device", days=7)
            args, _ = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]
            self.assertIn("?", query)
            self.assertIn("datetime('now', '-' || ? || ' days')", query)
            self.assertEqual(params, ("test-device", 7))

            # Test get_temp_analytics
            database.get_temp_analytics("test-device", days=7)
            args, _ = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]
            self.assertIn("?", query)
            self.assertIn("datetime('now', '-' || ? || ' days')", query)
            self.assertEqual(params, ("test-device", 7))

    def test_cors_configuration(self):
        """Verify CORS middleware configuration."""
        found_cors = False
        for middleware in main.app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                found_cors = True
                # Accessing kwargs from the middleware definition
                kwargs = middleware.kwargs
                self.assertEqual(kwargs.get("allow_origins"), ["*"])
                self.assertFalse(kwargs.get("allow_credentials"))
        self.assertTrue(found_cors, "CORSMiddleware not found in FastAPI app")

if __name__ == "__main__":
    unittest.main()
