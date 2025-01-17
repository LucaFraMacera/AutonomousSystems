from managed_resource import ManagedResource
import re
import json
from plant_sprinkler import PlantSprinkler

PLANT_CONFIG_JSON_FILE_PATH = "/sensors-config/plants-config.json"
GREENHOUSE_ID_KEY = "greenhouse_id"
PLANTS_KEY = "plants"


def greenhouses_config():
    with open(PLANT_CONFIG_JSON_FILE_PATH, 'r') as file:
        greenhouses = json.load(file)
        return [
            {
                GREENHOUSE_ID_KEY: greenhouse[GREENHOUSE_ID_KEY],
                PLANTS_KEY: [plant for plant in greenhouse[PLANTS_KEY]]
            } for greenhouse in greenhouses]


GREENHOUSES = greenhouses_config()


def set_up_sprinklers():
    sprinklers = {}
    for greenhouse in GREENHOUSES:
        greenhouse_id = greenhouse[GREENHOUSE_ID_KEY]
        plants = greenhouse[PLANTS_KEY]

        greenhouse_key = f"greenhouse_{greenhouse_id}"

        sprinklers[greenhouse_key] = {}
        for plant_id in plants:
            sprinklers[greenhouse_key][f"plant_{plant_id}"] = PlantSprinkler(greenhouse_id, plant_id)

    return sprinklers


SPRINKLERS = set_up_sprinklers()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("/+/+/irrigation_system")
        client.subscribe("/+/irrigation_system")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)


def on_message(client, userdata, msg):
    print(f"Irrigation system action updated {msg.topic}", flush=True)
    regex = r"^\/([^\/]+)(?:\/([^\/]+))?\/irrigation_system"
    result = re.match(regex, msg.topic)
    if not result:
        return
    matched_groups = result.groups()
    published_mode = json.loads(msg.payload.decode('UTF-8'))["value"].upper()
    print(f"Mode: {published_mode}", flush=True)

    if matched_groups[1] is not None:
        plant_sprinkler = SPRINKLERS[matched_groups[0]][matched_groups[1]]
        if published_mode == "OFF":
            plant_sprinkler.turn_off()

        if published_mode == "ON":
            plant_sprinkler.turn_on()

        if published_mode == "FULL_THROTTLE":
            plant_sprinkler.operate_at_full_throttle()
    else:
        greenhouse_plants = SPRINKLERS[matched_groups[0]]
        for plant_id in greenhouse_plants:
            plant_sprinkler = greenhouse_plants[plant_id]
            if published_mode == "OFF":
                plant_sprinkler.turn_off()

            if published_mode == "ON":
                plant_sprinkler.turn_on()

            if published_mode == "FULL_THROTTLE":
                plant_sprinkler.operate_at_full_throttle()


class IrrigationSystem(ManagedResource):

    def __init__(self) -> None:
        super().__init__(on_message=on_message, on_connect=on_connect, on_subscribe=on_subscribe)
        print("Starting irrigation system...", flush=True)
