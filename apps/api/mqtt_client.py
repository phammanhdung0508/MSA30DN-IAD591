import paho.mqtt.client as mqtt
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker: str = "test.mosquitto.org", port: int = 1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topics = ["home/sensors/#"]

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
            logger.info(f"Received `{payload}` from `{msg.topic}`")
            # Here you would typically process the data
            # e.g., save to DB, push to websocket, etc.
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

mqtt_client = MQTTClient()
