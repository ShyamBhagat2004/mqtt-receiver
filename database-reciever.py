import json
import paho.mqtt.client as mqtt
import math

# MQTT settings
MQTT_BROKER = "broker.mqtt.cool"
MQTT_PORT = 1883
MQTT_TOPIC = "NMEA_Lightning"

# Define base coordinates and earth radius
base_lat = 38.002729
base_lon = 23.675644
earth_radius = 6371.0

# MQTT callback for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT callback for message reception
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received MQTT message: {message}")
    if message.startswith("$WIMLI,"):
        data = parse_lightning_message(message)
        if data:
            print(f"Formatted data: {data}")

def parse_lightning_message(message):
    try:
        parts = message.split(',')
        distance_miles = float(parts[1])
        bearing_degrees = float(parts[2].split('*')[0])
        return convert_to_coordinates(base_lat, base_lon, distance_miles, bearing_degrees)
    except Exception as e:
        print(f"Error parsing message: {e}")
        return None

def convert_to_coordinates(lat, lon, distance, bearing):
    distance_km = distance * 1.60934  # Convert miles to kilometers
    bearing_rad = math.radians(bearing)
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance_km / earth_radius) +
                            math.cos(lat_rad) * math.sin(distance_km / earth_radius) * math.cos(bearing_rad))
    new_lon_rad = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance_km / earth_radius) * math.cos(lat_rad),
                                       math.cos(distance_km / earth_radius) - math.sin(lat_rad) * math.sin(new_lat_rad))
    return math.degrees(new_lat_rad), math.degrees(new_lon_rad)

# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()