import sys
from unittest.mock import MagicMock

# Mock dependencies that might have side effects on import
mock_mqtt = MagicMock()
mock_audio = MagicMock()
mock_whisper = MagicMock()
sys.modules['mqtt_client'] = MagicMock(mqtt_client=mock_mqtt)
sys.modules['audio_tcp'] = MagicMock(TcpAudioRecorder=MagicMock(return_value=mock_audio))
sys.modules['whisper_worker'] = MagicMock(WhisperWorker=MagicMock(return_value=mock_whisper))

import sqlite3
import os
from apps.api.main import app
from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics

def test_sql_parameterization():
    print("Verifying SQL parameterization...")
    # We will use a mock cursor to capture the SQL and parameters
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock get_db_connection
    import apps.api.database as db
    original_get_db = db.get_db_connection
    db.get_db_connection = MagicMock(return_value=mock_conn)

    try:
        # Test get_sensor_summary
        get_sensor_summary("test-device", 12)
        sql, params = mock_cursor.execute.call_args[0]
        assert "datetime('now', '-' || ? || ' hours')" in sql
        assert params == ("test-device", 12)
        print("✅ get_sensor_summary is parameterized")

        # Test get_energy_analytics
        get_energy_analytics("test-device", 7)
        sql, params = mock_cursor.execute.call_args[0]
        assert "datetime('now', '-' || ? || ' days')" in sql
        assert params == ("test-device", 7)
        print("✅ get_energy_analytics is parameterized")

        # Test get_temp_analytics
        get_temp_analytics("test-device", 3)
        sql, params = mock_cursor.execute.call_args[0]
        assert "datetime('now', '-' || ? || ' days')" in sql
        assert params == ("test-device", 3)
        print("✅ get_temp_analytics is parameterized")

    finally:
        db.get_db_connection = original_get_db

def test_cors_config():
    print("Verifying CORS configuration...")
    cors_middleware = next(m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware")
    assert cors_middleware.kwargs["allow_origins"] == ["*"]
    assert cors_middleware.kwargs["allow_credentials"] is False
    print("✅ CORS configuration is secure (allow_credentials=False with allow_origins=['*'])")

if __name__ == "__main__":
    try:
        test_sql_parameterization()
        test_cors_config()
        print("\nAll security verifications passed!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
