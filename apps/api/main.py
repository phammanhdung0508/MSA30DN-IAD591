from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from mqtt_client import mqtt_client
from database import (
    create_chat_session,
    add_chat_message,
    get_chat_history,
    get_last_messages,
)
import logging
import os
from dotenv import load_dotenv

from audio_tcp import TcpAudioRecorder
from whisper_worker import WhisperWorker
from gemini_client import gemini_generate

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper_worker = None
if os.getenv("WHISPER_ENABLED", "1") != "0":
    chat_device_session = os.getenv("CHAT_DEVICE_SESSION_ID", "device")

    def _store_device_chat(wav_path: str, transcript: str, gemini: str | None) -> None:
        session_id = create_chat_session(chat_device_session, source="device")
        add_chat_message(
            session_id,
            "user",
            transcript,
            meta={"source": "device", "wav": wav_path},
        )
        if gemini:
            add_chat_message(
                session_id,
                "assistant",
                gemini,
                meta={"source": "gemini", "wav": wav_path},
            )

    whisper_worker = WhisperWorker(
        model=os.getenv("WHISPER_MODEL", "base"),
        language=os.getenv("WHISPER_LANGUAGE", "") or None,
        task=os.getenv("WHISPER_TASK", "transcribe"),
        on_result=_store_device_chat,
    )

tcp_recorder = TcpAudioRecorder(
    host=os.getenv("AUDIO_TCP_HOST", "0.0.0.0"),
    port=int(os.getenv("AUDIO_TCP_PORT", os.getenv("AUDIO_UDP_PORT", "3334"))),
    save_dir=os.getenv("AUDIO_SAVE_DIR", "recordings"),
    sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
    silence_timeout_s=float(os.getenv("AUDIO_SILENCE_TIMEOUT_S", "6.0")),
    whisper_worker=whisper_worker,
)

# class ACControlParams(BaseModel):
#     power: bool = True
#     temperature: int = 24
#     mode: str = "cool"
#     fanSpeed: int = 2
#
# class DeviceCommand(BaseModel):
#     zone: str = "living-room"
#     device_type: str = "ac"
#     device_id: str = "daikin-x"
#     params: ACControlParams

class ScheduleData(BaseModel):
    schedule: List[List[bool]] # 7x24 grid

def _is_valid_schedule_grid(grid: List[List[bool]]) -> bool:
    if not isinstance(grid, list) or len(grid) != 7:
        return False
    for day in grid:
        if not isinstance(day, list) or len(day) != 24:
            return False
    return True

class ChatSessionCreate(BaseModel):
    session_id: str | None = None
    source: str | None = None

class ChatMessageRequest(BaseModel):
    session_id: str | None = None
    text: str
    source: str | None = None

@app.on_event("startup")
async def startup_event():
    from database import init_db
    init_db()
    mqtt_client.start()
    if os.getenv("AUDIO_TCP_ENABLED", "1") != "0":
        tcp_recorder.start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.stop()
    tcp_recorder.stop()

@app.post("/chat/session")
def create_chat_session_endpoint(data: ChatSessionCreate):
    session_id = create_chat_session(data.session_id, source=data.source or "web")
    return {"session_id": session_id}

@app.get("/chat/session/{session_id}")
def get_chat_session_history(session_id: str, limit: int = 200):
    messages = get_chat_history(session_id, limit=limit)
    return {"session_id": session_id, "messages": messages}

@app.post("/chat/message")
def post_chat_message(req: ChatMessageRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    session_id = create_chat_session(req.session_id, source=req.source or "web")
    user_meta = {"source": req.source or "web"}
    user_row = add_chat_message(session_id, "user", text, meta=user_meta)

    assistant_text = gemini_generate(text)
    if assistant_text:
        assistant_meta = {"source": "gemini"}
        assistant_row = add_chat_message(session_id, "assistant", assistant_text, meta=assistant_meta)
        return {
            "session_id": session_id,
            "user_text": text,
            "assistant_text": assistant_text,
            "user_ts": user_row["created_at"] if user_row else None,
            "assistant_ts": assistant_row["created_at"] if assistant_row else None,
        }

    return {
        "session_id": session_id,
        "user_text": text,
        "assistant_text": "",
        "user_ts": user_row["created_at"] if user_row else None,
        "assistant_ts": None,
        "error": "Gemini unavailable",
    }

@app.get("/chat/last")
def get_chat_last(session_id: str | None = None):
    sid = session_id or os.getenv("CHAT_DEFAULT_SESSION_ID", "device")
    messages = list(reversed(get_last_messages(sid, limit=4)))
    last_user = next((m for m in reversed(messages) if m["role"] == "user"), None)
    last_assistant = next((m for m in reversed(messages) if m["role"] == "assistant"), None)
    return {
        "session_id": sid,
        "user_text": last_user["text"] if last_user else None,
        "assistant_text": last_assistant["text"] if last_assistant else None,
        "messages": messages,
    }

@app.get("/chat/status")
def get_chat_status():
    return {
        "whisper_enabled": whisper_worker is not None,
        "recorder_running": tcp_recorder.is_running(),
        "recording": tcp_recorder.is_recording(),
        "whisper_queue": whisper_worker.queue_size() if whisper_worker else 0,
    }

# @app.get("/")
# def read_root():
#     return {"Hello": "Smart Home API", "Status": "MQTT Service Running"}

# In-memory state store to persist command state (Power, Mode, etc.) since sensor only sends Telemetry
# DEVICE_STATES = {}

# @app.get("/ac/{device_id}/status")
# def get_ac_status(device_id: str):
#     """
#     Retrieve the latest status of an AC unit from the database.
#     """
#     db_result = get_latest_device_data(device_id)
#
#     # Base state from memory (or default)
#     base_state = DEVICE_STATES.get(device_id, {
#         "power": False,
#         "temperature": 24, # Target temp
#         "currentTemperature": 24, # Sensor temp
#         "outdoorTemperature": 32.0,
#         "mode": "cool",
#         "fanSpeed": 2,
#         "humidity": 50,
#         "powerUsage": 0
#     })
#
#     # Create a copy to return
#     img_state = base_state.copy()
#
#     if db_result:
#         # payload from DB
#         payload = db_result.get("data", {})
#
#         # Merge payload into default state
#         # Map specific sensor fields if needed
#         if "temperature" in payload:
#             img_state["currentTemperature"] = payload["temperature"]
#         if "humidity" in payload:
#             img_state["humidity"] = payload["humidity"]
#
#         # If payload contains state (from other sources)
#         if "power" in payload: img_state["power"] = payload["power"]
#         if "mode" in payload: img_state["mode"] = payload["mode"]
#         if "fanSpeed" in payload: img_state["fanSpeed"] = payload["fanSpeed"]
#
#         return {
#             "timestamp": db_result.get("timestamp"),
#             "data": img_state
#         }
#
#     # Return default/mock if no data found yet
#     return {
#         "timestamp": None,
#         "data": img_state
#     }

# @app.post("/ac/control")
# def control_ac(cmd: DeviceCommand):
#     """
#     Sends a control command to a specific device via MQTT.
#     Topic: smart-home/{zone}/{device_type}/{device_id}/command
#     """
#     payload = {
#         "method": "set_state",
#         "params": cmd.params.dict()
#     }
#
#     # Update memory state to persist command
#     current = DEVICE_STATES.get(cmd.device_id, {
#         "power": False,
#         "temperature": 24,
#         "mode": "cool",
#         "fanSpeed": 2,
#         "currentTemperature": 24, # Sensor temp
#         "outdoorTemperature": 32.0,
#         "humidity": 50,
#         "powerUsage": 0
#     })
#     current.update(cmd.params.dict())
#     DEVICE_STATES[cmd.device_id] = current
#
#     success = mqtt_client.send_command(cmd.zone, cmd.device_type, cmd.device_id, payload)
#
#     if success:
#         return {
#             "status": "success",
#             "target": f"{cmd.zone}/{cmd.device_type}/{cmd.device_id}",
#             "command": payload
#         }
#     raise HTTPException(status_code=500, detail="Failed to publish message to MQTT broker")

# @app.post("/test/publish")
# def test_publish(topic: str, message: dict = Body(...)):
#     """
#     Test endpoint to publish arbitrary messages.
#     """
#     success = mqtt_client.publish(topic, message)
#     if success:
#         return {"status": "success", "topic": topic, "payload": message}
#     return {"status": "error", "message": "Failed to publish"}

# --- New Endpoints ---

# @app.get("/analytics/energy/{device_id}")
# def get_energy(device_id: str):
#     return {"data": get_energy_analytics(device_id)}

# @app.get("/analytics/temperature/{device_id}")
# def get_temperature(device_id: str):
#     return {"data": get_temp_analytics(device_id)}

# @app.get("/schedule/{device_id}")
# def get_device_schedule(device_id: str):
#     schedule = get_schedule(device_id)
#     return {"schedule": schedule}

# @app.post("/schedule/{device_id}")
# def save_device_schedule(device_id: str, data: ScheduleData):
#     if not _is_valid_schedule_grid(data.schedule):
#         raise HTTPException(status_code=400, detail="Schedule must be a 7x24 boolean grid")
#     success = save_schedule(device_id, data.schedule)
#     if success:
#         return {"status": "success"}
#     raise HTTPException(status_code=500, detail="Failed to save schedule")
