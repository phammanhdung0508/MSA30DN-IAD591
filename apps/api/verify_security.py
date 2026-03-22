import sys
from unittest.mock import MagicMock, patch

# Mock modules to avoid side effects during import
sys.modules["mqtt_client"] = sys.modules["whisper_worker"] = sys.modules["audio_tcp"] = MagicMock()

from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics
from apps.api.main import app

def check_sql():
    with patch("sqlite3.connect") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        tests = [(get_sensor_summary, "hours", 24), (get_energy_analytics, "days", 7), (get_temp_analytics, "days", 3)]
        for func, arg, val in tests:
            func("dev", **{arg: val})
            q, p = mock_cursor.execute.call_args[0]
            assert "?" in q and str(val) not in q and p == ("dev", val), f"{func.__name__} failed"
    print("✅ SQL Parameterization Verified")

def check_cors():
    mw = next(m for m in app.user_middleware if "CORSMiddleware" in str(m.cls))
    if "*" in mw.kwargs.get("allow_origins", []):
        assert not mw.kwargs.get("allow_credentials"), "Insecure CORS: credentials allowed with wildcard origin"
    print("✅ CORS Security Verified")

if __name__ == "__main__":
    try:
        check_sql()
        check_cors()
        print("\nAll security checks passed!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
