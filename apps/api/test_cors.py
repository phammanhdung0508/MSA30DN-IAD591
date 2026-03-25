import os
import sys
from unittest.mock import MagicMock

# Mock dependencies to allow importing main.py
sys.modules['mqtt_client'] = MagicMock()
sys.modules['whisper_worker'] = MagicMock()
sys.modules['audio_tcp'] = MagicMock()
sys.modules['gemini_client'] = MagicMock()

# Set environment variable before import
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:3000,http://trusted.com"

from apps.api.main import app

def verify_cors():
    print("Verifying CORS configuration...")
    # Find CORSMiddleware in the app's middleware list
    cors_mw = None
    for mw in app.user_middleware:
        if "CORSMiddleware" in str(mw.cls):
            cors_mw = mw
            break

    if not cors_mw:
        print("[!] CORSMiddleware not found in app.")
        return

    allowed_origins = cors_mw.kwargs.get("allow_origins", [])
    expected_origins = ["http://localhost:3000", "http://trusted.com"]

    if allowed_origins == expected_origins:
        print(f"[✓] CORS allowed_origins correctly set to: {allowed_origins}")
    else:
        print(f"[!] CORS allowed_origins mismatch. Expected {expected_origins}, got {allowed_origins}")

if __name__ == "__main__":
    verify_cors()
