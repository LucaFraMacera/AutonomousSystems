from planner import Planner
import re
import json

class GreenhousePlanner(Planner):

    TOPIC = "/{greenhouse}/plan"
    PLANS_FILE_PATH = "/sensors-config/greenhouses-plans.json"

    def __init__(self) -> None:
        super().__init__(on_connect=on_connect, on_message=on_message, on_subscribe=on_subscribe)
    
    def get_greenhouses_plans():
        return Planner.get_plant_plans(GreenhousePlanner.PLANS_FILE_PATH)
    

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected", flush=True)
        client.subscribe("/+/status")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}", flush=True)
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}", flush=True)

def on_message(client, userdata, msg):
    print("Greenhouse status updated", flush=True)
    regex = r"^\/(.+)\/status"
    result = re.match(regex, msg.topic)
    if not result:
        return
    matched_groups = result.groups()
    plans = GreenhousePlanner.get_plant_plans()
    published_status = json.loads(msg.payload.decode('UTF-8'))["value"].upper()
    if published_status in plans.keys():
        topic = GreenhousePlanner.TOPIC.format(greenhouse=matched_groups[0])
        GreenhousePlanner.publish(client, topic, plans[published_status])