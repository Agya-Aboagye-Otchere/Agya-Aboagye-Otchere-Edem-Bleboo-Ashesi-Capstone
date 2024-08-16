#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <PZEM004Tv30.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <esp_sleep.h>
#include <Adafruit_MLX90614.h>

Adafruit_MPU6050 mpu;
PZEM004Tv30 pzem(Serial2, 16, 17); // Serial2, RX pin 16, and TX pin 17
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

const int esp_ID = 1;  // Device ID 

const char* ssid = "";
const char* password = "";
const char* mqtt_server = "192.168.162.231"; // broker URL
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
unsigned long lastVibrationMsg = 0;
unsigned long lastSpeedMsg = 0;
unsigned long lastVoltageCurrentMsg = 0;
unsigned long lastTemperatureMsg = 0;

#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
const char* vibration_topic = "motor_data/vibration_data";
const char* speed_topic = "motor_data/speed_data";
const char* voltage_topic = "motor_data/voltage";
const char* current_topic = "motor_data/current";
const char* temperature_topic = "motor_data/temperature";
const char* command2_topic = "Capstone_Topic/#";
const char* command1_topic = "command1";

// Hall effect sensor pin
const int hallSensorPin = 35;

// Variables to store the count and the last state of the sensor
volatile int rpmCount = 0;
unsigned long lastRpmTime = 0;

// Duration in milliseconds to calculate RPM
const unsigned long rpmDuration = 1000; // 1 second

// Sampling intervals in milliseconds
const int vibrationSamplingInterval = 1; // 1 kHz for vibration
const int speedSamplingInterval = 2000;     // 2 seconds for speed
const int voltageCurrentSamplingInterval = 1000; // 1 second for voltage and current
const int temperatureSamplingInterval = 1000;    // 1 second for temperature

// Time to stay awake in milliseconds (20 minutes)
const unsigned long awakeTime = 20 * 60 * 1000;

// Deep sleep duration in microseconds (1 hour)
const unsigned long sleepDuration = 60 * 60 * 1000000;

// Interrupt Service Routine for Hall sensor
void IRAM_ATTR countPulse() {
  rpmCount++;
}

void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("Connection Failed. Rebooting...");
    delay(5000);
    ESP.restart();
  }

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  randomSeed(micros());
}

void setup_ota() {
  // No custom hostname or password set for OTA
  ArduinoOTA
    .onStart([]() {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
        type = "sketch";
      else // U_SPIFFS
        type = "filesystem";

      Serial.println("Start updating " + type);
    })
    .onEnd([]() {
      Serial.println("\nEnd");
    })
    .onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    })
    .onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

  ArduinoOTA.begin();
  Serial.println("OTA Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";   
    clientId += String(random(0xffff), HEX); 
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(command2_topic); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Setting up");
  setup_wifi();
  setup_ota();  // Setup OTA

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  Serial.println("MPU6050 Found!");
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  pinMode(hallSensorPin, INPUT_PULLUP); // Set hall sensor pin as input with internal pullup
  attachInterrupt(digitalPinToInterrupt(hallSensorPin), countPulse, RISING); // Attach interrupt to the hall sensor pin

  Wire.begin(4, 5); // Initialize I2C with pins 4 and 5 for GY-906
  mlx.begin();
}

void loop() {
  static unsigned long startTime = millis();

  if (!client.connected()) reconnect();
  client.loop();
  ArduinoOTA.handle();  // Handle OTA updates

  unsigned long now = millis();

  // Check if the device should go to deep sleep
  if (now - startTime >= awakeTime) {
    Serial.println("Entering deep sleep for 1 hour...");
    esp_deep_sleep(sleepDuration);
  }

  // Sample speed data at specified interval (2 seconds)
  if (now - lastSpeedMsg >= speedSamplingInterval) {
    lastSpeedMsg = now;

    // Calculate RPM from pulse count
    float rpm = (rpmCount * 60.0) / (speedSamplingInterval / 1000.0); // Convert pulses to RPM

    // Create a JSON document for speed data
    StaticJsonDocument<100> speedDoc;
    speedDoc["esp_ID"] = esp_ID;
    speedDoc["RPM"] = rpm;

    // Serialize JSON document to string
    char speedBuffer[100];
    serializeJson(speedDoc, speedBuffer);

    // Publish speed data
    publishMessage(speed_topic, String(speedBuffer), true);

    // Print RPM to Serial for debugging
    Serial.print("RPM: ");
    Serial.println(rpm);

    // Reset count for next interval
    rpmCount = 0;
  }

  // Sample vibration data at 1 kHz
  if (now - lastVibrationMsg >= vibrationSamplingInterval) {
    lastVibrationMsg = now;

    // Get new sensor events with the readings
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Create a JSON document for vibration data
    StaticJsonDocument<200> vibrationDoc;
    vibrationDoc["esp_ID"] = esp_ID;
    vibrationDoc["AccelX"] = a.acceleration.x;
    vibrationDoc["AccelY"] = a.acceleration.y;
    vibrationDoc["AccelZ"] = a.acceleration.z;

    // Serialize JSON document to string
    char vibrationBuffer[200];
    serializeJson(vibrationDoc, vibrationBuffer);

    // Publish vibration data
    publishMessage(vibration_topic, String(vibrationBuffer), true);

    // Print JSON string to Serial for debugging
    Serial.println(vibrationBuffer);
  }

  // Sample voltage and current data at 1 Hz
  if (now - lastVoltageCurrentMsg >= voltageCurrentSamplingInterval) {
    lastVoltageCurrentMsg = now;

    // Read voltage and current from PZEM-004T
    float voltage = pzem.voltage();
    float current = pzem.current();

    // Create JSON documents for voltage and current data
    StaticJsonDocument<100> voltageDoc;
    voltageDoc["esp_ID"] = esp_ID;
    voltageDoc["Voltage"] = voltage;
    char voltageBuffer[100];
    serializeJson(voltageDoc, voltageBuffer);
    publishMessage(voltage_topic, String(voltageBuffer), true);
    Serial.print("Voltage: ");
    Serial.println(voltage);

    StaticJsonDocument<100> currentDoc;
    currentDoc["esp_ID"] = esp_ID;
    currentDoc["Current"] = current;
    char currentBuffer[100];
    serializeJson(currentDoc, currentBuffer);
    publishMessage(current_topic, String(currentBuffer), true);
    Serial.print("Current: ");
    Serial.println(current);
  }

   // Sample temperature data at 1 Hz
  if (now - lastTemperatureMsg >= temperatureSamplingInterval) {
    lastTemperatureMsg = now;

    float temperature = mlx.readObjectTempC();

    // Create a JSON document for temperature data
    StaticJsonDocument<100> temperatureDoc;
    temperatureDoc["esp_ID"] = esp_ID;
    temperatureDoc["Temperature_C"] = temperature;

    // Serialize JSON document to string
    char temperatureBuffer[100];
    serializeJson(temperatureDoc, temperatureBuffer);

    // Publish temperature data
    publishMessage(temperature_topic, String(temperatureBuffer), true);

    // Print temperature to Serial for debugging
    Serial.print("Temperature (C): ");
    Serial.println(temperature);
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage += (char)payload[i];

  Serial.println("Message arrived [" + String(topic) + "]" + incommingMessage);

  if (strcmp(topic, command1_topic) == 0) {
    if (incommingMessage.equals("1")) digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on 
    else digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off 
  }
}

void publishMessage(const char* topic, String payload, boolean retained) {
  if (client.publish(topic, payload.c_str(), retained))
    Serial.println("Message published [" + String(topic) + "]: " + payload);
}
