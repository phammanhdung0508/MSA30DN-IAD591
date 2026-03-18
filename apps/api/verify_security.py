import sys
from unittest.mock import MagicMock

# Mock dependencies to avoid side effects
sys.modules["mqtt_client"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()
sys.modules["sqlite3"] = MagicMock()

def verify_sql_parameterization():
    import apps.api.database as database
    import sqlite3

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    database.get_db_connection = MagicMock(return_value=mock_conn)

    # Check get_sensor_summary
    database.get_sensor_summary("test-device", hours=24)
    # The last call to execute should have ? and NOT the value 24 in the query string
    args, _ = mock_cursor.execute.call_args
    query = args[0]
    params = args[1]
    assert "?" in query, "SQL query should be parameterized"
    assert "24" not in query, "SQL query should not contain interpolated values"
    assert 24 in params, "SQL parameters should contain the 'hours' value"
    print("✅ get_sensor_summary SQL parameterization verified")

    # Check get_energy_analytics
    database.get_energy_analytics("test-device", days=7)
    args, _ = mock_cursor.execute.call_args
    query = args[0]
    params = args[1]
    assert "?" in query, "SQL query should be parameterized"
    assert "7" not in query, "SQL query should not contain interpolated values"
    assert 7 in params, "SQL parameters should contain the 'days' value"
    print("✅ get_energy_analytics SQL parameterization verified")

    # Check get_temp_analytics
    database.get_temp_analytics("test-device", days=3)
    args, _ = mock_cursor.execute.call_args
    query = args[0]
    params = args[1]
    assert "?" in query, "SQL query should be parameterized"
    assert "3" not in query, "SQL query should not contain interpolated values"
    assert 3 in params, "SQL parameters should contain the 'days' value"
    print("✅ get_temp_analytics SQL parameterization verified")

def verify_cors_config():
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = next(m for m in app.user_middleware if m.cls == CORSMiddleware)
    assert cors_middleware.kwargs["allow_credentials"] is False, "CORS allow_credentials must be False when allow_origins is '*'"
    print("✅ CORS configuration verified")

if __name__ == "__main__":
    try:
        verify_sql_parameterization()
        verify_cors_config()
        print("\n🚀 All security verifications passed!")
    except AssertionError as e:
        print(f"\n❌ Security verification failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
