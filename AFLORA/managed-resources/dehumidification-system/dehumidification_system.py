from managed_resource import ManagedResource
import re
import json
from greenhouse_dehumidifier import GreenhouseDehumidifier
import random

MIN_NUMBER_OF_DEHUMIDIFIER_IN_GREENHOUSE = 3
MAX_NUMBER_OF_DEHUMIDIFIER_IN_GREENHOUSE = 8
PLANT_CONFIG_JSON_FILE_PATH = "/sensors-config/plants-config.json"
GREENHOUSE_ID_KEY = "greenhouse_id"


def greenhouses_config():
    with open(PLANT_CONFIG_JSON_FILE_PATH, 'r') as file:
        greenhouses = json.load(file)
        return [greenhouse[GREENHOUSE_ID_KEY] for greenhouse in greenhouses]


GREENHOUSES = greenhouses_config()


def set_up_dehumidifiers():
    dehumidifiers = {}
    for greenhouse_id in GREENHOUSES:
        greenhouse_key = f"greenhouse_{greenhouse_id}"

        dehumidifiers[greenhouse_key] = []
        for dehumidifier_id in range(random.randint(MIN_NUMBER_OF_DEHUMIDIFIER_IN_GREENHOUSE, MAX_NUMBER_OF_DEHUMIDIFIER_IN_GREENHOUSE)):
            dehumidifiers[greenhouse_key].append(GreenhouseDehumidifier(greenhouse_id, dehumidifier_id))

    return dehumidifiers


DEHUMIDIFIERS = set_up_dehumidifiers()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("/+/dehumidification_system")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)


def on_message(client, userdata, msg):
    print(f"Dehumidification system action updated {msg.topic}", flush=True)
    regex = r"^\/(.+)\/dehumidification_system"
    result = re.match(regex, msg.topic)
    if not result:
        return
    matched_groups = result.groups()
    published_mode = json.loads(msg.payload.decode('UTF-8'))["value"].upper()
    print(f"Mode: {published_mode}", flush=True)

    for dehumidifier in DEHUMIDIFIERS[matched_groups[0]]:

        if published_mode == "OFF":
            dehumidifier.turn_off()

        if published_mode == "ON":
            dehumidifier.turn_on()

        if published_mode == "FULL_THROTTLE":
            dehumidifier.operate_at_full_throttle()


class DehumidificationSystem(ManagedResource):

    def __init__(self) -> None:
        super().__init__(on_message=on_message, on_connect=on_connect, on_subscribe=on_subscribe)
        print("Starting dehumidifier system...", flush=True)
