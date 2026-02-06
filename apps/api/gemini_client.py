import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_PROMPT = (
    "Bạn là trợ lý giọng nói kiểu Alexa. Nhiệm vụ: trả lời trực tiếp câu hỏi của người dùng.\n"
    "Yêu cầu:\n"
    "1. Trả lời ngắn gọn, rõ ràng, đúng trọng tâm.\n"
    "2. Giữ đúng ngôn ngữ của người hỏi (Việt/Anh).\n"
    "3. Không trả về JSON, không giải thích quy trình.\n"
    "4. Nếu không chắc, hãy nói bạn không chắc.\n"
)


def gemini_generate(transcript: str) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, skip Gemini")
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = os.getenv("GEMINI_PROMPT", DEFAULT_GEMINI_PROMPT)

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
