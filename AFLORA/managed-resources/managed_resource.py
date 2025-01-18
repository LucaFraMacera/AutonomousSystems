from abc import ABC
import paho.mqtt.client as mqtt
import os
import json

MQTT_SERVICE_NAME = os.environ.get('MQTT_SERVICE_NAME')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT'))
VALUE_KEY = 'value'
ACTION_NOTIFICATION_TOPIC = '/action_notification'

def publish_value_on_action_notification_topic(client, value):
    payload = json.dumps({VALUE_KEY:value})
    client.publish(ACTION_NOTIFICATION_TOPIC, payload)

class ManagedResource(ABC):

    def __init__(self, on_connect, on_subscribe, on_message):
        # Message Broker connection
        self._client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self._client_mqtt.on_connect = on_connect
        self._client_mqtt.on_message = on_message
        self._client_mqtt.on_subscribe = on_subscribe
        self._client_mqtt.connect(MQTT_SERVICE_NAME, MQTT_BROKER_PORT)
        self._client_mqtt.loop_forever()


    