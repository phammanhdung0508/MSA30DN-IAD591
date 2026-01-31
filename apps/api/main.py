from fastapi import FastAPI, Body
from pydantic import BaseModel
from mqtt_client import mqtt_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ACControlParams(BaseModel):
    power: bool = True
    temperature: int = 24
    mode: str = "cool"

class DeviceCommand(BaseModel):
    zone: str = "living-room"
    device_type: str = "ac"
    device_id: str = "daikin-x"
    params: ACControlParams

@app.on_event("startup")
async def startup_event():
    mqtt_client.start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.stop()

@app.get("/")
def read_root():
    return {"Hello": "Smart Home API", "Status": "MQTT Service Running"}

@app.post("/ac/control")
def control_ac(cmd: DeviceCommand):
    """
    Sends a control command to a specific device via MQTT.
    Topic: smart-home/{zone}/{device_type}/{device_id}/command
    """
    payload = {
        "method": "set_state",
        "params": cmd.params.dict()
    }
    
    success = mqtt_client.send_command(cmd.zone, cmd.device_type, cmd.device_id, payload)
    
    if success:
        return {
            "status": "success", 
            "target": f"{cmd.zone}/{cmd.device_type}/{cmd.device_id}",
            "command": payload
        }
    return {"status": "error", "message": "Failed to publish message"}

@app.post("/test/publish")
def test_publish(topic: str, message: dict = Body(...)):
    """
    Test endpoint to publish arbitrary messages.
    """
    success = mqtt_client.publish(topic, message)
    if success:
        return {"status": "success", "topic": topic, "payload": message}
    return {"status": "error", "message": "Failed to publish"}
