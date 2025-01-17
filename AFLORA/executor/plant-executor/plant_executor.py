from executor import Executor, retrieve_actions_data, publish_value_on_topic
import re
import json

PLANT_ACTIONS_JSON_FILE_PATH = "sensors-config/plant-actions.json"
PLANT_ACTION_TOPIC_STRUCTURE = "/{greenhouse}/{plant}/{managed_resource}"  # Plant status topic structure

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("/+/+/plan")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)


def on_message(client, userdata, msg):
    print(f"Plant plan updated {msg.topic}", flush=True)
    regex = r"^\/(.+)\/(.+)\/plan"
    result = re.match(regex, msg.topic)
    if not result:
        return
    matched_groups = result.groups()
    published_plan = json.loads(msg.payload.decode('UTF-8'))["value"].upper()
    plant_actions_data = retrieve_actions_data(PLANT_ACTIONS_JSON_FILE_PATH)
    for managed_resource, action in plant_actions_data[published_plan].items():
        topic = PLANT_ACTION_TOPIC_STRUCTURE.format(greenhouse=matched_groups[0], plant=matched_groups[1], managed_resource=managed_resource)
        print(f"Plan: {published_plan}, Topic: {topic}, Action: {action}")
        publish_value_on_topic(client, action, topic)


class PlantExecutor(Executor):

    def __init__(self) -> None:
        super().__init__(on_message=on_message, on_connect=on_connect, on_subscribe=on_subscribe)
