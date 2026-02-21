import sys
from unittest.mock import MagicMock, patch
import os

# Mock environment variables before importing anything
os.environ["WHISPER_ENABLED"] = "0"
os.environ["AUDIO_TCP_ENABLED"] = "0"
os.environ["GEMINI_API_KEY"] = "fake_key"

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sql_parameterization():
    print("Testing SQL parameterization...")
    import database

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('database.get_db_connection', return_value=mock_conn):
        # Test get_sensor_summary
        database.get_sensor_summary("test-device", hours=48)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        assert "?" in query, "Query should be parameterized with '?'"
        assert "|| ? ||" in query, "Query should use concatenation for interval"
        assert 48 in params, "Parameter 'hours' should be passed in execute arguments"
        print("✅ get_sensor_summary is parameterized")

        # Test get_energy_analytics
        database.get_energy_analytics("test-device", days=7)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "?" in query
        assert "|| ? ||" in query
        assert 7 in params
        print("✅ get_energy_analytics is parameterized")

        # Test get_temp_analytics
        database.get_temp_analytics("test-device", days=30)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "?" in query
        assert "|| ? ||" in query
        assert 30 in params
        print("✅ get_temp_analytics is parameterized")

def test_cors_config():
    print("\nTesting CORS configuration...")
    from main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None, "CORSMiddleware should be present"

    # In FastAPI/Starlette, middleware arguments are in .kwargs
    kwargs = cors_middleware.kwargs

    assert kwargs["allow_origins"] == ["*"], f"allow_origins should be ['*'], got {kwargs['allow_origins']}"
    assert kwargs["allow_credentials"] is False, f"allow_credentials should be False, got {kwargs['allow_credentials']}"
    print("✅ CORS configuration is secure (allow_origins=['*'], allow_credentials=False)")

if __name__ == "__main__":
    try:
        test_sql_parameterization()
        test_cors_config()
        print("\n✨ All security checks passed!")
    except AssertionError as e:
        print(f"\n❌ Security check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 An error occurred during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
