from abc import ABC, abstractmethod
import paho.mqtt.client as mqtt
import os
import json
from knowledge.database import Database
import re

MQTT_SERVICE_NAME = os.environ.get("MQTT_SERVICE_NAME", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
STATE_HISTORY_MEASUREMENT = "plan-history"
DATABASE = Database()


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
        
    def get_high_priority_plans(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    
    def writePlan(plan, tags):
        point={}
        point["measurement"] = STATE_HISTORY_MEASUREMENT
        point["tags"] = tags
        point["fields"]={
            "value":plan
        }
        DATABASE.databaseWrite(point=point)

    def readLastPlan(tags={}):
        tags["measurement"]=STATE_HISTORY_MEASUREMENT
        results = DATABASE.databaseRead(tags=tags)
        return results[0] if len(results) > 0 else None

    def getIdFromTopicTag(tag):
        # Matches only strings in the form of prefix_id
        regex = r"(.+)_([0-9]+$)"
        result = re.match(regex, tag)
        if (result):
            parts = result.groups()
            return parts[1]
        return None


