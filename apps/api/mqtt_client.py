import paho.mqtt.client as mqtt
import json
import logging
import asyncio
from database import insert_device_data

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker: str = "broker.hivemq.com", port: int = 1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topics = [
            "sensor/temp_humid_msa_assign1"
        ]

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            for topic in self.topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            logger.info(f"[{msg.topic}] {payload}")
            
            # Specific handling for MSA Assign 1 topic
            if msg.topic == "sensor/temp_humid_msa_assign1":
                try:
                    data = json.loads(payload)
                    # Map flat JSON to our DB structure
                    # Arduino sends: {"temperature": X, "humidity": Y, "gas": Z}
                    # We treat this as telemetry for a specific device
                    insert_device_data("living-room", "sensor", "esp32-main", "telemetry", data)
                    logger.info(f"Saved sensor data: {data}")
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON from sensor")
                return

            # Basic parsing of topic structure for other devices
            # Topic: smart-home/{zone}/{device_type}/{device_id}/{msg_type}
            parts = msg.topic.split("/")
            if len(parts) == 5:
                zone, dev_type, dev_id, msg_type = parts[1], parts[2], parts[3], parts[4]
                # Save to DB
                insert_device_data(zone, dev_type, dev_id, msg_type, payload)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def start(self):
        logger.info(f"Connecting to broker {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic: str, message: dict):
        payload = json.dumps(message)
        result = self.client.publish(topic, payload)
        status = result[0]
        if status == 0:
            logger.info(f"Send `{payload}` to topic `{topic}`")
            return True
        else:
            logger.error(f"Failed to send message to topic {topic}")
            return False

    def send_command(self, zone: str, device_type: str, device_id: str, command: dict):
        # Special handling for ESP32 Main (Arduino Sketch)
        if device_id == "esp32-main":
            topic = "sensor/control_msa_assign1"
            # Extract power state to map to ALARM_ON/OFF
            # command structure: {"method": "set_state", "params": {"power": true, ...}}
            params = command.get("params", {})
            power = params.get("power", False)
            payload = "ALARM_ON" if power else "ALARM_OFF"
            
            logger.info(f"Sending raw command `{payload}` to `{topic}`")
            result = self.client.publish(topic, payload)
            return result[0] == 0

        # Standard handling
        topic = f"smart-home/{zone}/{device_type}/{device_id}/command"
        return self.publish(topic, command)

mqtt_client = MQTTClient()
