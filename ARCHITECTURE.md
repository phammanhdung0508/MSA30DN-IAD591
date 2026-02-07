# Smart Home Voice Assistant Architecture

This document reflects the current structure and runtime flow of the project in `C:\fsb\IAD591\Final`.

## Overview
- **IoT (ESP32-S3)**: Wake word detection, sensor telemetry, and TCP audio streaming.
- **API (FastAPI)**: Receives TCP audio, transcribes with Whisper, generates replies via Gemini, stores data in SQLite, and ingests MQTT telemetry.
- **Web (Next.js)**: Mobile-first UI with Chat and Sensors tabs.
- **Database**: SQLite stored at `packages/db/smarthome.db` initialized from `packages/db/schema.sql`.

## Repository Structure
```
/
├── apps/
│   ├── api/           # FastAPI backend (Python)
│   ├── iot/           # ESP32-S3 firmware (ESP-IDF / PlatformIO)
│   └── web/           # Next.js 14 UI
├── packages/
│   ├── db/            # SQLite DB + schema.sql
│   ├── ui/            # Shared UI package
│   ├── api-client/    # (Reserved) API client package
│   ├── tsconfig/
│   └── eslint-config/
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## Runtime Architecture
### 1) Audio + Wake Word Flow
```
ESP32 WakeNet/VAD -> TCP audio stream -> FastAPI TCP recorder -> WAV file
-> Whisper transcription -> Gemini response -> SQLite chat_messages
```

### 2) MQTT Telemetry Flow
```
ESP32 publishes MQTT (sensor/temp_humid_msa_assign1)
-> FastAPI MQTT client subscribes
-> Device data stored in SQLite device_data
```

### 3) Web UI Flow
```
Next.js UI -> FastAPI REST
/chat/* for conversations
/sensor/* for telemetry summaries
```

## Key Components
### IoT Firmware (apps/iot)
- **Wake word**: ESP-SR (WakeNet + VAD) model loaded from `srmodels.bin`.
- **Audio stream**: TCP packets with headers `STRT`, `AUD0`, `STOP`.
- **Sensors**: DHT11 + MQ135; publishes JSON to MQTT topic.
- **Config**: `sdkconfig` / `sdkconfig.esp32-s3-devkitc-1-idf` for WiFi, MQTT, audio host/port.

### Backend API (apps/api)
- **TCP Audio**: `audio_tcp.py` accepts audio and saves WAV.
- **Whisper**: `whisper_worker.py` transcribes and triggers Gemini.
- **Gemini**: `gemini_client.py` uses REST API key from env.
- **MQTT**: `mqtt_client.py` ingests telemetry and stores into SQLite.
- **REST Endpoints**:
  - `POST /chat/session`
  - `POST /chat/message`
  - `GET /chat/session/{id}`
  - `GET /chat/last`
  - `GET /chat/status`
  - `GET /sensor/latest`
  - `GET /sensor/history`
  - `GET /sensor/summary`

### Database (packages/db)
- **device_data**: MQTT telemetry and device payloads.
- **chat_sessions / chat_messages**: Chat history (web + device).
- **schedules**: Reserved for automation schedules.

## Environment Configuration
Backend (`apps/api/.env`):
```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
WHISPER_ENABLED=1
WHISPER_MODEL=base
WHISPER_LANGUAGE=
WHISPER_TASK=transcribe
AUDIO_TCP_ENABLED=1
AUDIO_TCP_HOST=0.0.0.0
AUDIO_TCP_PORT=3334
CHAT_DEVICE_SESSION_ID=device
CHAT_DEFAULT_SESSION_ID=device
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_SUB_TOPICS=sensor/temp_humid_msa_assign1,smart-home/+/+/+/+
```

## Build & Run (Summary)
- **Root**: `pnpm dev` (turbo) runs web + api.
- **API only**: `uvicorn main:app --reload --port 8000`
- **Web only**: `pnpm dev` in `apps/web`
- **IoT**: Build/flash with PlatformIO in `apps/iot`

## Notes
- MQTT topic defaults align with Arduino-style payloads and are ingested as telemetry.
- Audio config keys on ESP32 still use `AUDIO_UDP_*` naming but the transport is TCP.
