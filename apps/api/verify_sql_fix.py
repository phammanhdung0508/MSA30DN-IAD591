import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the current directory to sys.path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSQLInjectionFix(unittest.TestCase):
    @patch('sqlite3.connect')
    def test_get_sensor_summary_is_parameterized(self, mock_connect):
        from database import get_sensor_summary

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        get_sensor_summary("test-device", hours=48)

        # Check that execute was called
        self.assertTrue(mock_cursor.execute.called)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        # Verify query uses ? instead of f-string
        self.assertIn("timestamp >= datetime('now', '-' || ? || ' hours')", query)
        self.assertNotIn("-48 hours", query)

        # Verify params contains hours
        self.assertEqual(params, ("test-device", 48))

    @patch('sqlite3.connect')
    def test_get_energy_analytics_is_parameterized(self, mock_connect):
        from database import get_energy_analytics

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        get_energy_analytics("test-device", days=7)

        self.assertTrue(mock_cursor.execute.called)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        self.assertIn("timestamp >= datetime('now', '-' || ? || ' days')", query)
        self.assertNotIn("-7 days", query)
        self.assertEqual(params, ("test-device", 7))

    @patch('sqlite3.connect')
    def test_get_temp_analytics_is_parameterized(self, mock_connect):
        from database import get_temp_analytics

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        get_temp_analytics("test-device", days=3)

        self.assertTrue(mock_cursor.execute.called)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        self.assertIn("timestamp >= datetime('now', '-' || ? || ' days')", query)
        self.assertNotIn("-3 days", query)
        self.assertEqual(params, ("test-device", 3))

    def test_source_code_no_f_strings_in_queries(self):
        db_path = os.path.join(os.path.dirname(__file__), "database.py")
        with open(db_path, "r") as f:
            content = f.read()

        # Check that f-strings are not used with execute in the problematic functions
        # We look for 'execute(f'
        self.assertNotIn("cursor.execute(f'''", content)
        self.assertNotIn("cursor.execute(f\"", content)
        self.assertNotIn("cursor.execute(f'", content)

if __name__ == "__main__":
    unittest.main()
