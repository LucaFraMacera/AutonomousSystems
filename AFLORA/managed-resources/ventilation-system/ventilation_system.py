from managed_resource import ManagedResource
import re
import json
from greenhouse_window import GreenhouseWindow
import random

PLANT_CONFIG_JSON_FILE_PATH = "/sensors-config/plants-config.json"
GREENHOUSE_ID_KEY = "greenhouse_id"
NUMBER_OF_WINDOWS_KEY = "number_of_windows"

def greenhouses_config():
    with open(PLANT_CONFIG_JSON_FILE_PATH, 'r') as file:
        return json.load(file)


GREENHOUSES = greenhouses_config()


def set_up_windows():
    windows = {}
    for greenhouse in GREENHOUSES:
        greenhouse_key = f"greenhouse_{greenhouse[GREENHOUSE_ID_KEY]}"

        windows[greenhouse_key] = []
        for window_id in range(greenhouse[NUMBER_OF_WINDOWS_KEY]):
            windows[greenhouse_key].append(GreenhouseWindow(greenhouse[GREENHOUSE_ID_KEY], window_id))

    return windows


WINDOWS = set_up_windows()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("/+/ventilation_system")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)


def on_message(client, userdata, msg):
    print(f"Ventilation system action updated {msg.topic}", flush=True)
    regex = r"^\/(.+)\/ventilation_system"
    result = re.match(regex, msg.topic)
    if not result:
        return
    matched_groups = result.groups()
    published_mode = json.loads(msg.payload.decode('UTF-8'))["value"].upper()
    print(f"Mode: {published_mode}", flush=True)

    open_windows = 0
    for window in WINDOWS[matched_groups[0]]:

        if published_mode == "CLOSE_WINDOWS":
            window.close(client)

        if published_mode == "OPEN_HALF_OF_THE_WINDOWS":
            if open_windows >= len(WINDOWS[matched_groups[0]]) // 2:
                break
            window.open(client)
            open_windows += 1

        if published_mode == "OPEN_ALL_THE_WINDOWS":
            window.open(client)


class VentilationSystem(ManagedResource):

    def __init__(self) -> None:
        super().__init__(on_message=on_message, on_connect=on_connect, on_subscribe=on_subscribe)
        print("Starting ventilation system...", flush=True)
