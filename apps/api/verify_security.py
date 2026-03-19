import sys
from unittest.mock import MagicMock

# Mock dependencies to prevent side effects
sys.modules["mqtt_client"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()
sys.modules["sqlite3"] = MagicMock()

def test_sql_parameterization():
    from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics
    import sqlite3

    mock_conn = sqlite3.connect(":memory:")
    mock_cursor = mock_conn.cursor()

    # Check get_sensor_summary
    get_sensor_summary("test", hours=10)
    last_query = mock_cursor.execute.call_args[0][0]
    assert "datetime('now', '-' || ? || ' hours')" in last_query, "get_sensor_summary not parameterized"

    # Check get_energy_analytics
    get_energy_analytics("test", days=5)
    last_query = mock_cursor.execute.call_args[0][0]
    assert "datetime('now', '-' || ? || ' days')" in last_query, "get_energy_analytics not parameterized"

    # Check get_temp_analytics
    get_temp_analytics("test", days=3)
    last_query = mock_cursor.execute.call_args[0][0]
    assert "datetime('now', '-' || ? || ' days')" in last_query, "get_temp_analytics not parameterized"
    print("✅ SQL parameterization verified")

def test_cors_config():
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = next(m for m in app.user_middleware if m.cls == CORSMiddleware)
    assert cors_middleware.kwargs["allow_origins"] == ["*"]
    assert cors_middleware.kwargs["allow_credentials"] is False, "CORS allow_credentials must be False when allow_origins is ['*']"
    print("✅ CORS configuration verified")

if __name__ == "__main__":
    try:
        test_sql_parameterization()
        test_cors_config()
        print("🛡️ All security checks passed!")
    except AssertionError as e:
        print(f"❌ Security check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)
