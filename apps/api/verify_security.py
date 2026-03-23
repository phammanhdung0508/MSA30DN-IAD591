import sys
from unittest.mock import MagicMock, patch
for m in ['mqtt_client', 'audio_tcp', 'whisper_worker', 'gemini_client']: sys.modules[m] = MagicMock()

def verify_sql():
    from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics
    with patch('sqlite3.connect') as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        for func, val, unit in [(get_sensor_summary, 48, 'hours'), (get_energy_analytics, 7, 'days'), (get_temp_analytics, 3, 'days')]:
            func("dev", val)
            query, params = mock_cursor.execute.call_args[0]
            assert f"timestamp >= datetime('now', '-' || ? || ' {unit}')" in query
            assert params == ("dev", val)
    print("✅ SQL verified.")

def verify_cors():
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware
    cors = next(m for m in app.user_middleware if m.cls == CORSMiddleware)
    assert cors.kwargs["allow_origins"] == ["*"] and cors.kwargs["allow_credentials"] is False
    print("✅ CORS verified.")

if __name__ == "__main__":
    try:
        verify_sql(); verify_cors()
        print("🚀 All passed!")
    except Exception as e:
        print(f"❌ Failed: {e}"); sys.exit(1)
