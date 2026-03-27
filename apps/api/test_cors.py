import os
import sys
from unittest.mock import MagicMock

# Mock dependencies before importing app
sys.modules["mqtt_client"] = MagicMock()
sys.modules["whisper_worker"] = MagicMock()
sys.modules["audio_tcp"] = MagicMock()
sys.modules["gemini_client"] = MagicMock()

def test_cors_config():
    # Set environment variable with whitespace
    os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:3000, https://example.com"

    # Import app here so it picks up the environment variable
    from apps.api.main import app

    # Find CORSMiddleware
    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls.__name__ == "CORSMiddleware":
            cors_middleware = middleware
            break

    if not cors_middleware:
        print("CORSMiddleware not found")
        sys.exit(1)

    allowed_origins = cors_middleware.kwargs.get("allow_origins")
    expected_origins = ["http://localhost:3000", "https://example.com"]

    print(f"Allowed origins: {allowed_origins}")

    if allowed_origins == expected_origins:
        print("CORS configuration test passed!")
    else:
        print(f"CORS configuration test failed. Expected {expected_origins}, got {allowed_origins}")
        sys.exit(1)

if __name__ == "__main__":
    test_cors_config()
