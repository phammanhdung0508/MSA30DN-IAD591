import paho.mqtt.client as mqtt
import json
import logging
import os
import ssl
from urllib.parse import urlparse
from database import insert_device_data

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()

        broker_url = os.getenv("MQTT_BROKER_URL", "mqtt://localhost:1883")
        parsed = urlparse(broker_url)
        self.broker = parsed.hostname or "localhost"
        self.port = parsed.port or (8883 if parsed.scheme in {"mqtts", "ssl", "tls"} else 1883)
        self.use_tls = parsed.scheme in {"mqtts", "ssl", "tls"}
        self.username = os.getenv("MQTT_USERNAME", "")
        self.password = os.getenv("MQTT_PASSWORD", "")
        self.tls_ca = os.getenv("MQTT_TLS_CA", "")
        self.tls_insecure = os.getenv("MQTT_TLS_INSECURE", "false").lower() in {"1", "true", "yes"}
        self.sensor_topic = os.getenv("MQTT_SENSOR_TOPIC", "sensor/temp_humid_msa_assign1")
        self.control_topic = os.getenv("MQTT_CONTROL_TOPIC", "sensor/control_msa_assign1")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        topics_env = os.getenv(
            "MQTT_SUB_TOPICS",
            f"{self.sensor_topic},smart-home/+/+/+/+"
        )
        self.topics = [t.strip() for t in topics_env.split(",") if t.strip()]

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
            if msg.topic == self.sensor_topic:
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
                # Save to DB (try JSON first, fall back to raw)
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    data = payload
                insert_device_data(zone, dev_type, dev_id, msg_type, data)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def start(self):
        logger.info(f"Connecting to broker {self.broker}:{self.port}")
        if self.username:
            self.client.username_pw_set(self.username, self.password or None)
        if self.use_tls:
            if self.tls_ca:
                self.client.tls_set(ca_certs=self.tls_ca, tls_version=ssl.PROTOCOL_TLS_CLIENT)
            else:
                self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
            if self.tls_insecure:
                self.client.tls_insecure_set(True)
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
            topic = self.control_topic
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
