import paho.mqtt.client as mqtt
from knowledge.database import Database
import json
import re

MANAGED_RESOURCES_JSON_FILE_PATH = "/app/sensors-config/managed-resources.json"


def get_managed_resources_list():
    with open(MANAGED_RESOURCES_JSON_FILE_PATH, 'r') as file:
        return json.load(file)


MANAGED_RESOURCES_LIST = get_managed_resources_list()


def check_if_is_managed_resource_topic(tags):
    for managed_resource in MANAGED_RESOURCES_LIST:
        if managed_resource in tags:
            return True
    return False


def getIdFromTopicTag(tag):
    # Matches only strings in the form of prefix_id
    regex = r"(.+)_([0-9]+$)"
    result = re.match(regex, tag)
    if (result):
        parts = result.groups()
        return parts[1]
    return None


def parseBrokerMessage(message):
    topic = message.topic
    payload = json.loads(message.payload.decode("utf-8"))
    tags = []
    for value in topic.split("/"):
        if (len(value) > 0):
            tags.append(value)
    if "status" in tags or "plan" in tags or check_if_is_managed_resource_topic(tags):
        return None
    point = {}
    if (len(tags) == 3):
        point["tags"] = {
            "greenhouse_id": getIdFromTopicTag(tags[0]),
            "plant_id": getIdFromTopicTag(tags[1]),
            "sensor_type": tags[2]
        }
    else:
        point["tags"] = {
            "greenhouse_id": getIdFromTopicTag(tags[0]),
            "sensor_type": tags[1]
        }
    point["fields"] = {
        "value": payload["value"]
    }
    return point


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("+/+/#")


def on_message(client, userdata, msg):
    print("Message arrived", flush=True)
    message = parseBrokerMessage(message=msg)
    if message is not None:
        database.databaseWrite(message)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)


if __name__ == '__main__':
    # Database connection
    database = Database()

    # Message broker connection
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mqtt_broker", 1883)
    client_mqtt.loop_forever()
