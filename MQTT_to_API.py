import paho.mqtt.client as mqtt
import requests
import json

# MQTT Broker
mqtt_broker = "192.168.162.231"
mqtt_port = 1883
mqtt_main_topic = "motor_data"

# Define the IP address of the API server
api_ip = "192.168.162.231"  # Replace this with the IP address of your API server

# Corrected API Endpoints (ensure these URLs point to your actual web server)
api_url_current = f"http://{api_ip}/Capstone/3wObjectsRest/current_read.php"
api_url_voltage = f"http://{api_ip}/Capstone/3wObjectsRest/voltage.php"
api_url_speed = f"http://{api_ip}/Capstone/3wObjectsRest/speed.php"
api_url_vibration = f"http://{api_ip}/Capstone/3wObjectsRest/vibration_api.php"
api_url_temperature = f"http://{api_ip}/Capstone/3wObjectsRest/temperature.php"

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_main_topic + "/#")  # Subscribe to all subtopics of the main topic

# Function to send data to the appropriate API
def send_data(api_url, data):
    try:
        print(f"Sending data to URL: {api_url} with payload: {data}")  # Debug information
        response = requests.post(api_url, json=data)
        print(f"API Response: {response.status_code}, Response Text: {response.text}")
    except Exception as e:
        print(f"Error sending data to API: {str(e)}")

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message: {payload} on topic {msg.topic}")

    # Extract subtopics
    subtopics = msg.topic.split("/")
    
    if len(subtopics) == 2:  # Ensure the topic has the expected number of subtopics
        _, parameter_name = subtopics

        # Parse the payload as JSON
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return

        # Extract esp_ID from the data
        esp_ID = data.get("esp_ID")
        if esp_ID is None:
            print("Missing esp_ID in payload")
            return

        # Determine the API endpoint and data structure
        if parameter_name == "current":
            api_url = api_url_current
            data_payload = {
                "esp_ID": esp_ID,
                "C": data["Current"]
            }
        elif parameter_name == "voltage":
            api_url = api_url_voltage
            data_payload = {
                "esp_ID": esp_ID,
                "V": data["Voltage"]
            }
        elif parameter_name == "speed_data":
            api_url = api_url_speed
            data_payload = {
                "esp_ID": esp_ID,
                "S": data["RPM"]
            }
        elif parameter_name == "vibration_data":
            api_url = api_url_vibration
            data_payload = {
                "esp_ID": esp_ID,
                "ax": data["AccelX"],
                "ay": data["AccelY"],
                "az": data["AccelZ"]
            }
        elif parameter_name == "temperature":
            api_url = api_url_temperature
            data_payload = {
                "esp_ID": esp_ID,
                "temp": data["Temperature_C"]
            }
        else:
            print("Unknown parameter name")
            return

        # Send data to the appropriate API
        send_data(api_url, data_payload)
    else:
        print("Unexpected topic structure")

# Create MQTT client instance
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Loop to maintain connection
client.loop_forever()
