import paho.mqtt.client as mqtt
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker: str = "broker.emqx.io", port: int = 1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topics = [
            "smart-home/+/+/+/telemetry",
            "smart-home/+/+/+/status",
            "smart-home/+/+/+/response"
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
            
            # Basic parsing of topic structure
            # Topic: smart-home/{zone}/{device_type}/{device_id}/{msg_type}
            parts = msg.topic.split("/")
            if len(parts) == 5:
                zone, dev_type, dev_id, msg_type = parts[1], parts[2], parts[3], parts[4]
                # Here you can dispatch to different handlers based on msg_type
                if msg_type == "telemetry":
                    pass # Handle telemetry
                elif msg_type == "status":
                    pass # Handle status
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
        topic = f"smart-home/{zone}/{device_type}/{device_id}/command"
        return self.publish(topic, command)

mqtt_client = MQTTClient()
