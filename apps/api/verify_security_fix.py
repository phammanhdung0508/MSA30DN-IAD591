import sys
from unittest.mock import MagicMock

# Mock dependencies that might be imported and cause side effects
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()

def verify_sql_parameterization():
    print("Verifying SQL parameterization in apps/api/database.py...")
    import apps.api.database as db

    # Mocking sqlite3 connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Patch get_db_connection to return our mock connection
    db.get_db_connection = lambda: mock_conn

    # Test get_sensor_summary
    db.get_sensor_summary("test-device", hours=24)
    query = mock_cursor.execute.call_args[0][0]
    params = mock_cursor.execute.call_args[0][1]

    assert "datetime('now', '-' || ? || ' hours')" in query, "get_sensor_summary query is not parameterized correctly"
    assert params == ("test-device", 24), f"get_sensor_summary parameters are incorrect: {params}"
    print("✅ get_sensor_summary is parameterized.")

    # Test get_energy_analytics
    db.get_energy_analytics("test-device", days=7)
    query = mock_cursor.execute.call_args[0][0]
    params = mock_cursor.execute.call_args[0][1]

    assert "datetime('now', '-' || ? || ' days')" in query, "get_energy_analytics query is not parameterized correctly"
    assert params == ("test-device", 7), f"get_energy_analytics parameters are incorrect: {params}"
    print("✅ get_energy_analytics is parameterized.")

    # Test get_temp_analytics
    db.get_temp_analytics("test-device", days=30)
    query = mock_cursor.execute.call_args[0][0]
    params = mock_cursor.execute.call_args[0][1]

    assert "datetime('now', '-' || ? || ' days')" in query, "get_temp_analytics query is not parameterized correctly"
    assert params == ("test-device", 30), f"get_temp_analytics parameters are incorrect: {params}"
    print("✅ get_temp_analytics is parameterized.")

def verify_cors_config():
    print("\nVerifying CORS configuration in apps/api/main.py...")
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None, "CORSMiddleware not found"

    kwargs = cors_middleware.kwargs
    assert kwargs.get("allow_origins") == ["*"], f"CORS allow_origins should be ['*'], got {kwargs.get('allow_origins')}"
    assert kwargs.get("allow_credentials") is False, f"CORS allow_credentials must be False when allow_origins is ['*'], got {kwargs.get('allow_credentials')}"
    print("✅ CORS configuration is secure.")

if __name__ == "__main__":
    try:
        verify_sql_parameterization()
        verify_cors_config()
        print("\n✨ All security checks passed!")
    except AssertionError as e:
        print(f"\n❌ Security check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
