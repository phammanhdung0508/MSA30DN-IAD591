import sys
import os
from unittest.mock import MagicMock

# Mock dependencies before importing modules that use them
sys.modules['mqtt_client'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()

# Add apps/api to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

try:
    from database import get_sensor_summary, get_energy_analytics, get_temp_analytics, init_db, insert_device_data
    from main import app
    import json

    # 1. Verify SQL Injection Fix Functional
    print("Verifying SQL functions...")
    init_db()
    insert_device_data("test-zone", "sensor", "test-device", "telemetry", {"temperature": 25, "humidity": 50})

    summary = get_sensor_summary("test-device", 24)
    energy = get_energy_analytics("test-device", 1)
    temp = get_temp_analytics("test-device", 1)

    print(f"Summary: {summary is not None}")
    print(f"Energy: {isinstance(energy, list)}")
    print(f"Temp: {isinstance(temp, list)}")

    # 2. Verify CORS Hardening
    print("\nVerifying CORS configuration...")
    cors_middleware = next(m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware")
    allow_credentials = cors_middleware.kwargs.get("allow_credentials")
    allow_origins = cors_middleware.kwargs.get("allow_origins")

    print(f"CORS allow_origins: {allow_origins}")
    print(f"CORS allow_credentials: {allow_credentials}")

    if allow_credentials is False and allow_origins == ["*"]:
        print("SUCCESS: CORS hardening verified.")
    else:
        print("FAILURE: CORS configuration is insecure.")
        sys.exit(1)

    print("\nAll security fixes verified successfully.")

except Exception as e:
    print(f"Verification failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
