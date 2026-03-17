import sys
from unittest.mock import MagicMock, patch

# Mock modules that have side effects on import or are not needed for this check
mock_mqtt = MagicMock()
mock_whisper = MagicMock()
mock_audio = MagicMock()

sys.modules["mqtt_client"] = MagicMock(mqtt_client=mock_mqtt)
sys.modules["whisper_worker"] = MagicMock(WhisperWorker=mock_whisper)
sys.modules["audio_tcp"] = MagicMock(TcpAudioRecorder=mock_audio)

def test_sql_parameterization():
    print("Checking SQL parameterization in database.py...")
    import apps.api.database as database

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("sqlite3.connect", return_value=mock_conn):
        # Test get_sensor_summary
        database.get_sensor_summary("test-device", hours=24)
        last_query = mock_cursor.execute.call_args[0][0]
        if "'-24 hours'" in last_query or "'-' ||" not in last_query:
            if "'-' || ?" not in last_query:
                print("❌ get_sensor_summary is NOT using parameterized time interval.")
            else:
                print("✅ get_sensor_summary is using parameterized time interval.")
        else:
            print("✅ get_sensor_summary is using parameterized time interval.")

        # Test get_energy_analytics
        database.get_energy_analytics("test-device", days=1)
        last_query = mock_cursor.execute.call_args[0][0]
        if "'-1 days'" in last_query or "'-' ||" not in last_query:
             if "'-' || ?" not in last_query:
                print("❌ get_energy_analytics is NOT using parameterized time interval.")
             else:
                print("✅ get_energy_analytics is using parameterized time interval.")
        else:
            print("✅ get_energy_analytics is using parameterized time interval.")

        # Test get_temp_analytics
        database.get_temp_analytics("test-device", days=1)
        last_query = mock_cursor.execute.call_args[0][0]
        if "'-1 days'" in last_query or "'-' ||" not in last_query:
            if "'-' || ?" not in last_query:
                print("❌ get_temp_analytics is NOT using parameterized time interval.")
            else:
                print("✅ get_temp_analytics is using parameterized time interval.")
        else:
            print("✅ get_temp_analytics is using parameterized time interval.")

def test_cors_config():
    print("\nChecking CORS configuration in main.py...")
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = None
    # In newer FastAPI versions, middleware might be in app.user_middleware or app.middleware_stack
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    if cors_middleware:
        kwargs = cors_middleware.kwargs
        allow_origins = kwargs.get("allow_origins", [])
        allow_credentials = kwargs.get("allow_credentials", False)

        print(f"CORS allow_origins: {allow_origins}")
        print(f"CORS allow_credentials: {allow_credentials}")

        if "*" in allow_origins and allow_credentials:
            print("❌ Insecure CORS: allow_credentials is True with wildcard origin.")
        else:
            print("✅ CORS configuration is secure.")
    else:
        print("❓ CORSMiddleware not found.")

if __name__ == "__main__":
    test_sql_parameterization()
    test_cors_config()
