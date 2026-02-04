# Smart Home IoT System

A comprehensive Smart Home solution integrating a Next.js frontend, FastAPI backend, and Arduino-based IoT devices using MQTT communication.

## 🏗 Project Structure

This monorepo contains:

- **`apps/web`**: Next.js 14 application serving as the main control dashboard.
  - Features: Glassmorphism UI, Real-time status updates, Interactive controls, Analytics charts (Recharts).
- **`apps/api`**: FastAPI backend service.
  - Features: MQTT Client (Paho), SQLite Database integration, REST API endpoints.
- **`apps/iot`**: C++ code for ESP32/Arduino devices.
  - Features: MQTT connectivity, reading DHT sensors (Temp/Humidity), Actuator control (LED/Buzzer).
- **`packages/db`**: Shared SQLite database location.

## 🚀 Features

- **Real-time Monitoring**: Live display of Temperature and Humidity from IoT sensors.
- **Remote Control**: Toggle AC power, change modes (Cool/Heat/Dry/Fan), and adjust Fan Speed.
- **Analytics**: Visualization of temperature trends over the last 24 hours.
- **Automated Communication**: Seamless synchronization between Web Dashboard and Hardware via MQTT.

## 🛠 Tech Stack

- **Frontend**: React, Next.js, TailwindCSS, Lucide Icons, Recharts.
- **Backend**: Python, FastAPI, SQLite3, Paho-MQTT.
- **Communication Protocol**: MQTT (HiveMQ Public Broker).
- **Hardware/Simulation**: ESP32 (Wokwi Compatible), DHT22 Sensor.

## ⚙️ Setup & Installation

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
pip install fastapi uvicorn paho-mqtt
```

### 3. Database Setup
The SQLite database is automatically initialized at `packages/db/smarthome.db` when the API server starts.

## 🏃 Running the Application

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
- Open `apps/iot/main/smart_home_mqtt/smart_home_mqtt.ino` in Arduino IDE or Wokwi.
- Ensure the device is connected to WiFi and the configured MQTT Broker.

## 📡 MQTT Configuration

- **Broker**: `broker.hivemq.com`
- **Port**: `1883`
- **Topics**:
  - Telemetry (Sensor -> Cloud): `sensor/temp_humid_msa_assign1`
  - Control (Cloud -> Device): `sensor/control_msa_assign1`

## 📊 Database Schema

The system uses SQLite. Key tables:
- `device_data`: Stores telemetry logs (JSON payload) with timestamps.
- `schedules`: Stores device automation schedules.
