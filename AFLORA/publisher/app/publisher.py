import paho.mqtt.client as mqtt
import time
import json
import random
from lib.utils import *

def retrieve_greenhouse_sensor_data():
    with open(GREENHOUSE_SENSORS_CONFIG_JSON_FILE_PATH, 'r') as file:
        sensors_data = json.load(file)
        configured_sensors_data = []
        for sensor in sensors_data:
            current_sensor_data = build_base_sensor_data(sensor)
            if LIMIT_KEY in sensor:
                current_sensor_data[LIMIT_KEY] = sensor[LIMIT_KEY]
            if LETHAL_LIMIT_KEY in sensor:
                current_sensor_data[LETHAL_LIMIT_KEY] = sensor[LETHAL_LIMIT_KEY]
            configured_sensors_data.append(current_sensor_data)
        return configured_sensors_data


def retrieve_plant_sensor_data():
    with open(PLANT_SENSORS_CONFIG_JSON_FILE_PATH, 'r') as file:
        sensors_data = json.load(file)
        return [build_base_sensor_data(sensor) for sensor in sensors_data]


def build_base_sensor_data(sensor_data):
    return {
        NAME_KEY: sensor_data[NAME_KEY], 
        BOUNDARIES_KEY: (sensor_data[MIN_KEY], sensor_data[MAX_KEY]), 
        THRESHOLDS_KEY: (sensor_data[THRESHOLD_MIN_KEY], sensor_data[THRESHOLD_MAX_KEY])
        } 


def field_config():
    with open(PLANT_CONFIG_JSON_FILE_PATH, 'r') as file:
        greenhouses = json.load(file)
        return [
            {
                GREENHOUSE_ID_KEY: greenhouse[GREENHOUSE_ID_KEY],
                PLANTS_KEY: [plant for plant in greenhouse[PLANTS_KEY]]
            } for greenhouse in greenhouses]


# Publishs data on MQTT
def publish_data():
    configured_field = field_config()
    configured_greenhouse_sensors = retrieve_greenhouse_sensor_data()
    configured_plant_sensors = retrieve_plant_sensor_data()
    while True:
        for greenhouse in configured_field:
            for greenhouse_sensor in configured_greenhouse_sensors:
                greenhouse_topic = GREENHOUSE_TOPIC_STRUCTURE.format(greenhouse_ID=greenhouse[GREENHOUSE_ID_KEY], sensor_type=greenhouse_sensor[NAME_KEY])
                value = generate_sensor_data(greenhouse_sensor)
                publish_value_on_topic(value, greenhouse_topic)
            for plant_ID in greenhouse[PLANTS_KEY]:
                for plant_sensor in configured_plant_sensors:
                    plant_topic = PLANT_TOPIC_STRUCTURE.format(greenhouse_ID=greenhouse[GREENHOUSE_ID_KEY], plant_ID=plant_ID, sensor_type=plant_sensor[NAME_KEY])
                    value = generate_sensor_data(plant_sensor)
                    publish_value_on_topic(value, plant_topic)
        print(f"Published! {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", flush=True)
        time.sleep(15)  # Wait 15 seconds before sending new data


def publish_value_on_topic(value, topic):
    payload = json.dumps({VALUE_KEY: value}) # Serialize only the JSON value
    client.publish(topic, payload)
    # print(f"Published value '{value}' on topic '{topic}'! {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", flush=True)


def generate_sensor_data(sensor):
    boundaries = sensor[BOUNDARIES_KEY]
    thresholds = sensor[THRESHOLDS_KEY]
    if LIMIT_KEY in sensor and random.random() < 0.99: # put max threshold as limit with probability 0.9
            thresholds = (thresholds[0], sensor[LIMIT_KEY])
    elif LETHAL_LIMIT_KEY in sensor: # put max threshold as lethal_limit with probability 0.1
            thresholds = (thresholds[0], sensor[LETHAL_LIMIT_KEY])
    return generate_sensor_reading(boundaries, thresholds)


def generate_sensor_reading(boundaries, thresholds):
    min_value, max_value = boundaries
    min_threshold, max_threshold = thresholds
    if random.random() < 0.99: # generate random below threshold with probability 0.9
        return random.uniform(min_threshold+1, max_threshold-1)
    # generate random above threshold with probability 0.1
    if random.random() < 0.1:
        return random.uniform(min_value, min_threshold)
    return round(random.uniform(max_threshold, max_value), 2)


if __name__ == "__main__":
    # Broker connection
    client = mqtt.Client("Publisher")
    client.connect(BROKER, PORT)

    publish_data()