# Smart Home Voice Assistant

Hệ thống Smart Home điều khiển bằng giọng nói, kết nối ESP32 (wake-word) với FastAPI (Whisper + Gemini) và UI web mobile-first để hiển thị hội thoại và dữ liệu cảm biến.

## Mục lục

- Tổng quan
- Tính năng
- Kiến trúc nhanh
- Sơ đồ hệ thống
- Tech stack
- Bắt đầu nhanh
- Cấu trúc repo
- Cấu hình môi trường
- Chạy hệ thống
- API chính
- MQTT (tùy chọn)
- Database
- Tài liệu liên quan
- Kiểm thử
- CI/CD
- Đóng góp
- License

## Tổng quan

Luồng chính:

1. ESP32 nhận wake word "Hi, Jason".
2. ESP32 stream audio TCP đến API.
3. API lưu WAV, transcribe bằng Whisper, gửi text sang Gemini.
4. Kết quả hội thoại lưu vào SQLite.
5. Web UI hiển thị chat và telemetry.

## Tính năng

- Wake-word trên ESP32 (ESP-SR).
- Streaming audio TCP từ thiết bị về API.
- Whisper chuyển giọng nói thành văn bản.
- Gemini tạo phản hồi hội thoại.
- Lưu chat và dữ liệu cảm biến vào SQLite.
- UI web mobile-first hiển thị chat và sensor.

## Kiến trúc nhanh

Audio/Wake-word:

```
ESP32 WakeNet/VAD -> TCP audio -> FastAPI recorder -> WAV
-> Whisper -> Gemini -> SQLite (chat_messages)
```

MQTT Telemetry:

```
ESP32 MQTT publish -> FastAPI MQTT subscribe -> SQLite (device_data)
```

Web UI:

```
Next.js UI -> FastAPI REST (/chat/*, /sensor/*)
```

## Sơ đồ hệ thống

Xem `DIAGRAMS.md` để xem toàn bộ sơ đồ Mermaid (tổng quan, luồng audio, MQTT, database, API, đối dây).

## Tech stack

- Frontend: Next.js 14, React, TailwindCSS
- Backend: FastAPI, Python, SQLite, Whisper, Gemini API
- IoT: ESP32-S3 (ESP-IDF / PlatformIO), INMP411 mic, LCD (optional)
- Giao tiếp: TCP (audio), MQTT (telemetry, optional)

## Bắt đầu nhanh

### Yêu cầu

- Node.js v18+
- Python 3.10+
- pnpm (`npm install -g pnpm`)

### Cài dependencies

```bash
pnpm install
```

### Backend (Python)

```bash
cd apps/api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Cài Whisper (tùy chọn)

```bash
pip install -U openai-whisper torch
```

## Cấu trúc repo

```
/
|-- apps/
|   |-- api/           # FastAPI backend
|   |-- iot/           # ESP32-S3 firmware
|   |-- web/           # Next.js UI
|-- packages/
|   |-- db/            # SQLite db + schema.sql
|   |-- ui/            # Shared UI
|   |-- api-client/    # Reserved
|   |-- tsconfig/
|   |-- eslint-config/
|-- turbo.json
|-- pnpm-workspace.yaml
|-- package.json
```

## Cấu hình môi trường

Tạo hoặc cập nhật file `apps/api/.env`:

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
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_SUB_TOPICS=sensor/temp_humid_msa_assign1,smart-home/+/+/+/+
```

## Chạy hệ thống

### Chạy tất cả (Turbo)

```bash
pnpm dev
```

### Chạy từng phần

Backend:

```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd apps/web
pnpm dev
```

IoT:
Build/flash trong `apps/iot` bằng PlatformIO. Cấu hình WiFi + audio host/port trong `sdkconfig` gồm `CONFIG_SMART_HOME_WIFI_SSID`, `CONFIG_SMART_HOME_WIFI_PASSWORD`, `CONFIG_SMART_HOME_AUDIO_UDP_HOST`, `CONFIG_SMART_HOME_AUDIO_UDP_PORT`.

## API chính

Chat:

- `POST /chat/session`
- `POST /chat/message`
- `GET /chat/session/{id}`
- `GET /chat/last`
- `GET /chat/status`

Sensors:

- `GET /sensor/latest`
- `GET /sensor/history`
- `GET /sensor/summary`

## MQTT (tùy chọn)

Broker: `MQTT_BROKER_URL` (API), `SMART_HOME_MQTT_BROKER_URI` (ESP32). Auth: `MQTT_USERNAME` / `MQTT_PASSWORD` và `SMART_HOME_MQTT_USERNAME` / `SMART_HOME_MQTT_PASSWORD` (nếu dùng). Topics mặc định: telemetry `sensor/temp_humid_msa_assign1` và wildcard `smart-home/+/+/+/+`.

Chi tiết schema MQTT: xem `MQTT_SCHEMA.md`.

## Database

SQLite nằm ở `packages/db/smarthome.db`, tự khởi tạo khi API chạy.

Bảng chính:

- `device_data`: telemetry (MQTT)
- `chat_sessions`, `chat_messages`: hội thoại
- `schedules`: lịch tự động hóa (dự phòng)

## Tài liệu liên quan

- `ARCHITECTURE.md`
- `DIAGRAMS.md`
- `WAKE_WORD.md`
- `MQTT_SCHEMA.md`

## Kiểm thử

Chưa có bộ test tự động được cấu hình. Nếu cần, có thể bổ sung test cho:

- API (FastAPI)
- UI (Next.js)
- Firmware (ESP32)

## CI/CD

Chưa cấu hình pipeline CI/CD.

## Đóng góp

1. Fork repo và tạo branch mới.
2. Ghi rõ mục tiêu thay đổi.
3. Tạo PR với mô tả ngắn gọn.

## License

Chưa xác định.
