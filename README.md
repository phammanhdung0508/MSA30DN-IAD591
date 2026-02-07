# Smart Home Voice Assistant

A voice-first Smart Home system that connects ESP32 wake-word detection with a FastAPI backend (Whisper + Gemini) and a mobile-first web UI.

## System Overview

1. ESP32 detects wake word (“Hi, Jason”).
2. ESP32 streams audio via TCP to the API server.
3. API saves WAV, transcribes with Whisper, sends text to Gemini.
4. User text + Gemini response are stored in SQLite.
5. Web UI displays the conversation as a mobile-first chat screen.

## Project Structure

This monorepo contains:

- **`apps/web`**: Next.js 14 mobile-first web UI for chat.
  - Features: Minimal chat display UI.
- **`apps/api`**: FastAPI backend service.
  - Features: TCP audio receiver, Whisper transcription, Gemini response, SQLite storage, MQTT ingest.
- **`apps/iot`**: ESP32-S3 firmware.
  - Features: Wake word detection (ESP-SR), TCP audio streaming, LCD status.
- **`packages/db`**: Shared SQLite database location.

## Features

- **Wake Word**: ESP32 detects “Hi, Jason”.
- **Audio Streaming**: TCP audio stream from ESP32 to API.
- **Speech → Text**: Whisper transcription.
- **Text → Response**: Gemini generates assistant replies.
- **Chat Log**: Conversation saved to SQLite and displayed in UI.

## Tech Stack

- **Frontend**: React, Next.js, TailwindCSS.
- **Backend**: Python, FastAPI, SQLite3, Whisper, Gemini API.
- **Communication Protocol**: TCP (audio stream), MQTT (optional telemetry).
- **Hardware**: ESP32-S3 + INMP411 mic + (optional) I2C LCD.

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- pnpm (`npm install -g pnpm`)

### 1. Install Dependencies (Frontend & Monorepo)
```bash
pnpm install
```

### 2. Setup Python Environment (Backend)
Navigate to `apps/api` and install dependencies:
```bash
cd apps/api
# Create venv (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
```

### 3. Optional Whisper Install
Whisper is not installed by default. If you want local transcription:
```bash
pip install -U openai-whisper torch
```

### 4. Environment Variables
Create/edit `apps/api/.env`:
```
GEMINI_API_KEY=your_key
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
```

### 5. Database Setup
The SQLite database is automatically initialized at `packages/db/smarthome.db` when the API server starts.

## Running the Application

### Option 1: Run All (Turbo Mode)
From the root directory:
```bash
pnpm dev
```
This starts both the Web Frontend (localhost:3000) and API Server (localhost:8000).

### Option 2: Run Individually

**Backend (API):**
```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

**Frontend (Web):**
```bash
cd apps/web
pnpm dev
```

**IoT Device:**
- Build/flash `apps/iot` using PlatformIO.
- Set WiFi + audio host/port in `sdkconfig`:
  - `CONFIG_SMART_HOME_WIFI_SSID`
  - `CONFIG_SMART_HOME_WIFI_PASSWORD`
  - `CONFIG_SMART_HOME_AUDIO_UDP_HOST` (API server IP)
  - `CONFIG_SMART_HOME_AUDIO_UDP_PORT` (API TCP port, default 3334)

## Chat API (Backend)

- `POST /chat/session`
- `GET /chat/session/{id}`
- `POST /chat/message`
- `GET /chat/last`
- `GET /chat/status`

## MQTT Configuration (Optional)

- **Broker**: Configure via `MQTT_BROKER_URL` (API) and `SMART_HOME_MQTT_BROKER_URI` (ESP32).
- **Auth**: Optional via `MQTT_USERNAME` / `MQTT_PASSWORD` and `SMART_HOME_MQTT_USERNAME` / `SMART_HOME_MQTT_PASSWORD`.
**Topics**:
- Telemetry (Sensor -> Cloud): `sensor/temp_humid_msa_assign1`
- Smart Home wildcard: `smart-home/+/+/+/+`

## Database Schema

The system uses SQLite. Key tables:
- `device_data`: Stores telemetry logs (JSON payload) with timestamps.
- `schedules`: Stores device automation schedules.
- `chat_sessions`: Chat session metadata.
- `chat_messages`: Stored conversation messages (user/assistant).
