import sys
from unittest.mock import MagicMock

# Mock dependencies that might be imported or initialized on main.py import
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()

import sqlite3
import apps.api.database as database
from apps.api.main import app
from fastapi.middleware.cors import CORSMiddleware

def test_security():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    orig = database.get_db_connection
    database.get_db_connection = lambda: mock_conn
    try:
        for fn, arg, unit in [(database.get_sensor_summary, 24, "hours"),
                             (database.get_energy_analytics, 7, "days"),
                             (database.get_temp_analytics, 1, "days")]:
            fn("dev", arg)
            q, p = mock_cursor.execute.call_args[0]
            assert f"datetime('now', '-' || ? || ' {unit}')" in q and p == ("dev", arg)
        mw = next(m for m in app.user_middleware if m.cls == CORSMiddleware)
        assert "*" in mw.kwargs["allow_origins"] and mw.kwargs["allow_credentials"] is False
        print("✅ Security checks passed")
    finally: database.get_db_connection = orig

if __name__ == "__main__":
    try:
        test_security()
    except AssertionError as e:
        print(f"\n❌ Security check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 An error occurred during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
