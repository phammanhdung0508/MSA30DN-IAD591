import sys
import os
from unittest.mock import MagicMock, patch

# Add apps/api to sys.path
sys.path.append(os.path.join(os.getcwd(), "apps/api"))

# Mock dependencies to avoid side effects during import
sys.modules["mqtt_client"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()
sys.modules["gemini_client"] = MagicMock()

def test_sql_parameterization():
    import database
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        # Test get_sensor_summary
        database.get_sensor_summary("test-device", hours=48)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "?" in query and "|| ? ||" in query, f"Query not parameterized correctly: {query}"
        assert params == ("test-device", 48)
        print("✅ get_sensor_summary is parameterized")

        # Test get_energy_analytics
        database.get_energy_analytics("test-device", days=7)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "?" in query and "|| ? ||" in query, f"Query not parameterized correctly: {query}"
        assert params == ("test-device", 7)
        print("✅ get_energy_analytics is parameterized")

        # Test get_temp_analytics
        database.get_temp_analytics("test-device", days=5)
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        assert "?" in query and "|| ? ||" in query, f"Query not parameterized correctly: {query}"
        assert params == ("test-device", 5)
        print("✅ get_temp_analytics is parameterized")

def test_cors_config():
    import main
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = None
    for middleware in main.app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None, "CORS middleware not found"

    # Check kwargs for CORSMiddleware
    kwargs = cors_middleware.kwargs
    assert kwargs["allow_origins"] == ["*"]
    assert kwargs["allow_credentials"] is False
    print("✅ CORS configuration is secure")

if __name__ == "__main__":
    try:
        test_sql_parameterization()
        test_cors_config()
        print("\n✨ All security checks passed!")
    except AssertionError as e:
        print(f"\n❌ Security check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
