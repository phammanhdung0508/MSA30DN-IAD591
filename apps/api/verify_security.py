
import sys
from unittest.mock import MagicMock, patch

# Mock dependencies to prevent side effects during import
sys.modules['paho-mqtt'] = MagicMock()
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['gemini_client'] = MagicMock()

import sqlite3
import os

def check_sql_parameterization():
    print("Checking SQL parameterization in apps/api/database.py...")
    from apps.api.database import get_sensor_summary, get_energy_analytics, get_temp_analytics

    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Test get_sensor_summary
        get_sensor_summary("dev1", hours=24)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1] if len(args) > 1 else None

        if "'-24 hours'" in query:
             print("❌ get_sensor_summary: Parameter 'hours' is hardcoded or interpolated in the query string.")
        elif '?' in query and params and 24 in params:
             print("✅ get_sensor_summary: Parameter 'hours' is correctly parameterized.")
        else:
             print(f"❓ get_sensor_summary: Unexpected query format. Query: {query}")

        # Test get_energy_analytics
        get_energy_analytics("dev1", days=1)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1] if len(args) > 1 else None

        if "'-1 days'" in query:
             print("❌ get_energy_analytics: Parameter 'days' is hardcoded or interpolated in the query string.")
        elif '?' in query and params and 1 in params:
             print("✅ get_energy_analytics: Parameter 'days' is correctly parameterized.")
        else:
             print(f"❓ get_energy_analytics: Unexpected query format. Query: {query}")

        # Test get_temp_analytics
        get_temp_analytics("dev1", days=1)
        args, kwargs = mock_cursor.execute.call_args
        query = args[0]
        params = args[1] if len(args) > 1 else None

        if "'-1 days'" in query:
             print("❌ get_temp_analytics: Parameter 'days' is hardcoded or interpolated in the query string.")
        elif '?' in query and params and 1 in params:
             print("✅ get_temp_analytics: Parameter 'days' is correctly parameterized.")
        else:
             print(f"❓ get_temp_analytics: Unexpected query format. Query: {query}")

def check_cors_config():
    print("\nChecking CORS configuration in apps/api/main.py...")
    from apps.api.main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = next((m for m in app.user_middleware if m.cls == CORSMiddleware), None)

    if cors_middleware:
        # Access kwargs from the Middleware object
        options = cors_middleware.kwargs
        allow_origins = options.get("allow_origins", [])
        allow_credentials = options.get("allow_credentials", False)

        print(f"CORS allow_origins: {allow_origins}")
        print(f"CORS allow_credentials: {allow_credentials}")

        if "*" in allow_origins and allow_credentials:
            print("❌ Insecure CORS: allow_credentials is True while allow_origins contains '*'.")
        elif "*" in allow_origins and not allow_credentials:
            print("✅ Secure CORS: allow_credentials is False when allow_origins is '*'.")
        else:
            print("ℹ️ CORS configuration seems customized.")
    else:
        print("❓ CORSMiddleware not found in app.")

if __name__ == "__main__":
    check_sql_parameterization()
    check_cors_config()
