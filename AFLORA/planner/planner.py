from abc import ABC, abstractmethod
import paho.mqtt.client as mqtt
import os
import json

MQTT_SERVICE_NAME = os.environ.get("MQTT_SERVICE_NAME", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))

class Planner(ABC):

    def __init__(self, on_connect, on_subscribe, on_message) -> None:
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = on_connect
        self.client_mqtt.on_message = on_message
        self.client_mqtt.on_subscribe = on_subscribe
        self.connect()
        
    def connect(self):
        self.client_mqtt.connect(MQTT_SERVICE_NAME, MQTT_BROKER_PORT)
        self.client_mqtt.loop_forever()

    def publish(mqtt_client, topic, plan):
        print(f'Publish new plan {plan} on {topic}', flush=True)
        payload = json.dumps({"value":plan})
        mqtt_client.publish(topic, payload)

    def get_plans(filepath):
        with open(filepath, 'r') as file:
            return {status.upper():plan.upper() for status, plan in json.load(file).items()}
