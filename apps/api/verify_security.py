import sys
from unittest.mock import MagicMock, patch

# Mock unnecessary modules for database import
sys.modules['mqtt_client'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['gemini_client'] = MagicMock()

def test_parameterization():
    from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('apps.api.database.get_db_connection', return_value=mock_conn):
        # Test get_sensor_summary
        get_sensor_summary("test-device", hours=48)
        args, _ = mock_cursor.execute.call_args
        query, params = args
        assert "?" in query
        assert "48" not in query
        assert params == ("test-device", 48)
        print("✅ get_sensor_summary is parameterized")

        # Test get_energy_analytics
        get_energy_analytics("test-device", days=7)
        args, _ = mock_cursor.execute.call_args
        query, params = args
        assert "?" in query
        assert "7" not in query
        assert params == ("test-device", 7)
        print("✅ get_energy_analytics is parameterized")

        # Test get_temp_analytics
        get_temp_analytics("test-device", days=5)
        args, _ = mock_cursor.execute.call_args
        query, params = args
        assert "?" in query
        assert "5" not in query
        assert params == ("test-device", 5)
        print("✅ get_temp_analytics is parameterized")

if __name__ == "__main__":
    try:
        test_parameterization()
        print("\nAll SQL parameterization tests passed! 🛡️")
    except AssertionError as e:
        print(f"\n❌ Parameterization test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
