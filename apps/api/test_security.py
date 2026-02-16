import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add current directory to path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database

class TestSecurity(unittest.TestCase):

    @patch('database.get_db_connection')
    def test_get_sensor_summary_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        database.get_sensor_summary("test-device", hours=48)

        # Check if execute was called
        self.assertTrue(mock_cursor.execute.called)
        args, kwargs = mock_cursor.execute.call_args
        sql = args[0]
        params = args[1]

        # Verify SQL doesn't contain the literal '48' but has '?'
        self.assertNotIn("'48 hours'", sql)
        self.assertIn("'-' || ? || ' hours'", sql)
        self.assertEqual(params, ("test-device", 48))

    @patch('database.get_db_connection')
    def test_get_energy_analytics_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        database.get_energy_analytics("test-device", days=7)

        # Check if execute was called
        self.assertTrue(mock_cursor.execute.called)
        args, kwargs = mock_cursor.execute.call_args
        sql = args[0]
        params = args[1]

        # Verify SQL doesn't contain the literal '7' but has '?'
        self.assertNotIn("'7 days'", sql)
        self.assertIn("'-' || ? || ' days'", sql)
        self.assertEqual(params, ("test-device", 7))

    @patch('database.get_db_connection')
    def test_get_temp_analytics_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        database.get_temp_analytics("test-device", days=30)

        # Check if execute was called
        self.assertTrue(mock_cursor.execute.called)
        args, kwargs = mock_cursor.execute.call_args
        sql = args[0]
        params = args[1]

        # Verify SQL doesn't contain the literal '30' but has '?'
        self.assertNotIn("'30 days'", sql)
        self.assertIn("'-' || ? || ' days'", sql)
        self.assertEqual(params, ("test-device", 30))

if __name__ == '__main__':
    unittest.main()
