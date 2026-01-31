#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"
#include <WiFi.h>
#include <PubSubClient.h>

// --- Hardware Config ---
// Pin definition based on diagram.json
// ESP32-S2 Board in diagram
#define DHTPIN 4
#define DHTTYPE DHT22

// I2C for LCD
#define SDA_PIN 8
#define SCL_PIN 9

// Actuators & Inputs
#define LED_PIN 2       // Diagram: esp:2 -> r1 -> led1
#define BUZZER_PIN 18   // Diagram: esp:18 -> r2 -> bz1
#define BUTTON_PIN 15   // Diagram: esp:15 -> btn1

// Simulation adjustments
#define TEMP_THRESHOLD 30.0

// --- Objects ---
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE);

// --- Network Config ---
// Wokwi simulation wifi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT Broker
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

// Topic Structure: smart-home/{zone}/{device_type}/{device_id}/{msg_type}
// We choose: zone="living-room", type="sensor", id="dht22-1"
const char* CLIENT_ID = "wokwi-esp32-s2-01";
const char* TOPIC_TELEMETRY = "smart-home/living-room/sensor/dht22-1/telemetry";
const char* TOPIC_STATUS    = "smart-home/living-room/sensor/dht22-1/status";

WiFiClient espClient;
PubSubClient client(espClient);

// --- State Variables ---
bool alarmEnabled = true;
bool lastButtonState = HIGH;
bool tempHighSent = false;
unsigned long lastNotifyMs = 0;
const unsigned long NOTIFY_COOLDOWN_MS = 60000;

bool manualControl = false; // Manual override status
static unsigned long lastDhtErrorMs = 0;

// Rate limiting
static unsigned long lastTelemetryMs = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 2000;

static unsigned long lastStatusMs = 0;
const unsigned long STATUS_INTERVAL_MS = 5000;

void setAlarm(bool state) {
  digitalWrite(LED_PIN, state ? HIGH : LOW);
  digitalWrite(BUZZER_PIN, state ? HIGH : LOW);
}

void lcdPrint(float humidity, float temperature) {
  lcd.setCursor(0, 1);
  lcd.printf("H:%.1f T:%.1fC   ", humidity, temperature);
}

void connectWifi() {
  delay(10);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnectMqtt() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect with unique Client ID
    if (client.connect(CLIENT_ID)) {
      Serial.println("connected");
      // Publish "online" status immediately
      client.publish(TOPIC_STATUS, "{\"status\":\"online\"}");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void publishTelemetry(float humidity, float temperature) {
  // Construct JSON payload
  // Format: {"temp": 25.0, "hum": 60.0, ...}
  char msg[128];
  snprintf(msg, sizeof(msg), 
    "{\"temperature\":%.2f, \"humidity\":%.2f, \"device_id\":\"%s\"}", 
    temperature, humidity, CLIENT_ID
  );
  
  if (client.publish(TOPIC_TELEMETRY, msg)) {
    Serial.printf("Published to %s: %s\n", TOPIC_TELEMETRY, msg);
  } else {
    Serial.println("Publish failed");
  }
}

void setup() {
  Serial.begin(115200);

  // Init Pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Init I2C and LCD
  Wire.begin(SDA_PIN, SCL_PIN); 
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Init System...");

  // Init Sensors
  dht.begin();

  // Init Network
  connectWifi();
  client.setServer(mqtt_server, mqtt_port);
  
  lcd.setCursor(0, 0);
  lcd.print("System Ready    ");
}

void loop() {
  // OTA / Network maintain
  if (!client.connected()) {
    reconnectMqtt();
  }
  client.loop();

  // 1. Read Inputs
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  bool btnState = digitalRead(BUTTON_PIN);

  // 2. Button Logic (Toggle Manual Control or Alarm)
  if (btnState == LOW && lastButtonState == HIGH) {
    manualControl = !manualControl;
    Serial.printf("Manual Control: %s\n", manualControl ? "ON" : "OFF");
    // Toggle alarm for feedback
    setAlarm(manualControl);
    delay(200); // Debounce simple
  }
  lastButtonState = btnState;

  // 3. Logic: High Temp Alarm (if not manual override)
  if (!manualControl) {
    if (!isnan(t) && t > TEMP_THRESHOLD) {
      setAlarm(true);
    } else {
      setAlarm(false);
    }
  }

  // 4. Update UI
  if (!isnan(h) && !isnan(t)) {
    lcdPrint(h, t);
  } else {
    lcd.setCursor(0, 1);
    lcd.print("Sensor Error    ");
  }

  // 5. IoT Publish (Telemetry)
  unsigned long now = millis();
  if (now - lastTelemetryMs > TELEMETRY_INTERVAL_MS) {
    if (!isnan(h) && !isnan(t)) {
      publishTelemetry(h, t);
      lastTelemetryMs = now;
    }
  }

  // 6. IoT Publish (Heartbeat/Status)
  if (now - lastStatusMs > STATUS_INTERVAL_MS) {
    // Should match mqtt_client expected topics?
    // Client listens to smart-home/+/+/+/status
    char statusMsg[128];
    snprintf(statusMsg, sizeof(statusMsg), 
      "{\"alive\":true, \"wifi\":%d, \"alarm\":%d}", 
      WiFi.status() == WL_CONNECTED, digitalRead(LED_PIN)
    );
    client.publish(TOPIC_STATUS, statusMsg);
    lastStatusMs = now;
  }
}
