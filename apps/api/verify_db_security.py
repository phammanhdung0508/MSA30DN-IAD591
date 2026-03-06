import sys
import unittest
from unittest.mock import MagicMock, patch

# Mocking modules that might have side effects on import
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()

import database

class TestDatabaseSecurity(unittest.TestCase):
    @patch('database.get_db_connection')
    def test_get_sensor_summary_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        database.get_sensor_summary("test-device", hours=48)

        # Check if execute was called with parameters
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        self.assertIn('?', query)
        self.assertIn('48', str(params))
        self.assertNotIn('-48 hours', query)

    @patch('database.get_db_connection')
    def test_get_energy_analytics_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        database.get_energy_analytics("test-device", days=7)

        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        self.assertIn('?', query)
        self.assertIn('7', str(params))
        self.assertNotIn('-7 days', query)

    @patch('database.get_db_connection')
    def test_get_temp_analytics_parameterized(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        database.get_temp_analytics("test-device", days=3)

        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        self.assertIn('?', query)
        self.assertIn('3', str(params))
        self.assertNotIn('-3 days', query)

if __name__ == '__main__':
    unittest.main()
