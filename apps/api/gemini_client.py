import json
import logging
import os
import urllib.error
import urllib.request

from database import get_latest_device_data

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_PROMPT = (
    "You are a smart home voice assistant.\n"
    "Rules:\n"
    "1. Always reply in English, regardless of the user's language.\n"
    "2. Keep responses short, clear, and direct.\n"
    "3. Do not return JSON or explain your process.\n"
    "4. If unsure, say you are not sure.\n"
)


SENSOR_KEYWORDS = ("temperature", "humidity", "air", "quantity")


def _needs_sensor_context(text: str) -> bool:
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in SENSOR_KEYWORDS)


def _build_sensor_context() -> str:
    device_id = os.getenv("SENSOR_DEVICE_ID", "esp32-main")
    latest = get_latest_device_data(device_id)
    if not latest:
        return "SENSOR_DATA: unavailable."
    data = latest.get("data") or {}
    timestamp = latest.get("timestamp") or "unknown"
    fields = []
    for key, label, unit in [
        ("temperature", "temperature", "C"),
        ("humidity", "humidity", "%"),
        ("co2", "co2", "ppm"),
        ("gas", "gas", "ppm"),
        ("nh3", "nh3", "ppm"),
        ("co", "co", "ppm"),
        ("rs", "rs", ""),
        ("ratio", "ratio", ""),
    ]:
        value = data.get(key)
        if value is None:
            continue
        if unit:
            fields.append(f"{label}={value}{unit}")
        else:
            fields.append(f"{label}={value}")
    details = "; ".join(fields) if fields else "no fields"
    return f"SENSOR_DATA (latest, {timestamp}): {details}."


def gemini_generate(transcript: str) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, skip Gemini")
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = os.getenv("GEMINI_PROMPT", DEFAULT_GEMINI_PROMPT)
    prompt = f"{prompt}\n\nAlways reply in English."

    context = None
    if _needs_sensor_context(transcript):
        context = _build_sensor_context()
    if context:
        text = (
            f"{prompt}\n\n{context}\n"
            "Use SENSOR_DATA to answer questions about temperature, humidity, or air quality.\n\n"
            f"TRANSCRIPT:\n{transcript}"
        )
    else:
        text = f"{prompt}\n\nTRANSCRIPT:\n{transcript}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": text}],
            }
        ]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        logger.warning("Gemini HTTP error: %s", e)
        return None
    except Exception:
        logger.exception("Gemini request failed")
        return None

    candidates = data.get("candidates") or []
    if not candidates:
        logger.warning("Gemini response empty")
        return None
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text_out = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    return text_out.strip() if text_out else None
