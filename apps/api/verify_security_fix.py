import sys
import os
from unittest.mock import MagicMock, patch

# Add the current directory to sys.path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_parameterization():
    print("Testing database parameterization...")
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Import database after patching
        import database

        # Test get_sensor_summary
        database.get_sensor_summary("test-device", hours=48)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        # print(f"Query: {query.strip()}")
        # print(f"Params: {params}")

        assert "datetime('now', '-' || ? || ' hours')" in query
        assert params == ("test-device", 48)
        print("get_sensor_summary: PASSED")

        # Test get_energy_analytics
        database.get_energy_analytics("test-device", days=7)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "datetime('now', '-' || ? || ' days')" in query
        assert params == ("test-device", 7)
        print("get_energy_analytics: PASSED")

        # Test get_temp_analytics
        database.get_temp_analytics("test-device", days=3)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "datetime('now', '-' || ? || ' days')" in query
        assert params == ("test-device", 3)
        print("get_temp_analytics: PASSED")

def test_cors_config():
    print("Testing CORS configuration...")
    # Mocking components that start threads or need env vars
    with patch('mqtt_client.mqtt_client'), \
         patch('audio_tcp.TcpAudioRecorder'), \
         patch('whisper_worker.WhisperWorker'), \
         patch('dotenv.load_dotenv'):

        import main
        from fastapi.middleware.cors import CORSMiddleware

        found = False
        for middleware in main.app.user_middleware:
            if middleware.cls == CORSMiddleware:
                found = True
                # Starlette Middleware stores options in .kwargs
                kwargs = getattr(middleware, "kwargs", {})
                print(f"Middleware kwargs: {kwargs}")
                assert kwargs.get("allow_credentials") is False
                print("CORS allow_credentials: False (PASSED)")
                break
        assert found, "CORSMiddleware not found"

if __name__ == "__main__":
    try:
        test_database_parameterization()
        test_cors_config()
        print("\nAll security fixes verified successfully!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
