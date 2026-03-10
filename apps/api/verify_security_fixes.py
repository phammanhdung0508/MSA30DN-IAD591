import sys
import os
from unittest.mock import MagicMock, patch

# Mock modules to prevent side effects during import
sys.modules["mqtt_client"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()

import apps.api.database as database
from apps.api.main import app
from fastapi.middleware.cors import CORSMiddleware

def test_sql_injection():
    print("Checking for SQL injection vulnerabilities...")
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("apps.api.database.get_db_connection", return_value=mock_conn):
        # Test get_sensor_summary
        database.get_sensor_summary("test-device", hours=24)
        last_query = mock_cursor.execute.call_args[0][0]
        if "datetime('now', '-24 hours')" in last_query:
            print("❌ get_sensor_summary is VULNERABLE to SQL injection (hardcoded/interpolated value)")
        else:
            print("✅ get_sensor_summary seems secure")

        # Test get_energy_analytics
        database.get_energy_analytics("test-device", days=1)
        last_query = mock_cursor.execute.call_args[0][0]
        if "datetime('now', '-1 days')" in last_query:
            print("❌ get_energy_analytics is VULNERABLE to SQL injection (hardcoded/interpolated value)")
        else:
            print("✅ get_energy_analytics seems secure")

        # Test get_temp_analytics
        database.get_temp_analytics("test-device", days=1)
        last_query = mock_cursor.execute.call_args[0][0]
        if "datetime('now', '-1 days')" in last_query:
            print("❌ get_temp_analytics is VULNERABLE to SQL injection (hardcoded/interpolated value)")
        else:
            print("✅ get_temp_analytics seems secure")

def test_cors_security():
    print("\nChecking for insecure CORS configuration...")
    cors_middleware = None
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
            print("❌ Insecure CORS: allow_credentials=True with allow_origins=['*']")
        else:
            print("✅ CORS configuration seems secure")
    else:
        print("❓ CORSMiddleware not found")

if __name__ == "__main__":
    test_sql_injection()
    test_cors_security()
