from fastapi import FastAPI, Body
from pydantic import BaseModel
from mqtt_client import mqtt_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ACCommand(BaseModel):
    power: bool
    temperature: int
    mode: str

@app.on_event("startup")
async def startup_event():
    mqtt_client.start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.stop()

@app.get("/")
def read_root():
    return {"Hello": "World", "Status": "MQTT Service Running"}

@app.post("/ac/control")
def control_ac(command: ACCommand):
    """
    Publishes AC control commands to 'home/ac/control' topic.
    """
    topic = "home/ac/control"
    payload = command.dict()
    success = mqtt_client.publish(topic, payload)
    if success:
        return {"status": "success", "message": f"Sent command to {topic}", "data": payload}
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
