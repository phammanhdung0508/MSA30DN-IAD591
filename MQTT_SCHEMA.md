# MQTT Topic Schema Design

This document outlines the standard MQTT topic structure for the **IoT Smart AC System**.

**Root Topic**: `smart-home`

## 1. Telemetry (Sensors -> Cloud)
Data sent periodically by devices (e.g., every 5 seconds).

**Topic**: `smart-home/{zone}/{device_type}/{device_id}/telemetry`

**Example**: `smart-home/living-room/sensor/env-01/telemetry`

**Payload (JSON)**:
```json
{
  "timestamp": 1706428000,
  "temperature": 24.5,
  "humidity": 60.2,
  "power_consumption": 1.2
}
```

## 2. Status / Heartbeat (Device <-> Cloud)
Used to track device connectivity (LWT - Last Will and Testament) and health.

**Topic**: `smart-home/{zone}/{device_type}/{device_id}/status`

**Example**: `smart-home/living-room/ac/daikin-x/status`

**Payload**:
- **Online**: `{"state": "online", "ip": "192.168.1.105", "uptime": 1200}`
- **Offline**: `{"state": "offline"}` (Sent via LWT)

## 3. Command (Cloud -> Device)
Instructions sent to the device to change its state.

**Topic**: `smart-home/{zone}/{device_type}/{device_id}/command`

**Example**: `smart-home/living-room/ac/daikin-x/command`

**Payload (JSON)**:
```json
{
  "request_id": "req-001",
  "method": "set_state",
  "params": {
    "power": "ON",
    "mode": "cool",
    "target_temp": 22,
    "fan_speed": 2
  }
}
```

## 4. Command Response (Device -> Cloud)
Confirmation that a command was received and executed.

**Topic**: `smart-home/{zone}/{device_type}/{device_id}/response`

**Example**: `smart-home/living-room/ac/daikin-x/response`

**Payload (JSON)**:
```json
{
  "request_id": "req-001",
  "success": true,
  "current_state": {
    "power": "ON",
    "target_temp": 22
  }
}
```
