from time import sleep
from managed_resource import publish_value_on_action_notification_topic

class PlantSprinkler:

    __STATE_OFF_KEY = "OFF"
    __STATE_ON_KEY = "ON"
    __STATE_FULL_THROTTLE_KEY = "FULL_THROTTLE"
    __NOTIFICATION_STRING_STRUCTURE = "Plant {plant_id} in greenhouse {greenhouse_id} sprinkler {action}!"

    def __init__(self, greenhouse_id, plant_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__plant_id = plant_id
        self.__status = (self.__STATE_OFF_KEY, False)

    def turn_on(self, is_greenhouse_action, mqtt_client):
        status, current_priority = self.__status

        if ((status != self.__STATE_OFF_KEY and current_priority == is_greenhouse_action) and
                (status != self.__STATE_OFF_KEY and current_priority is True and is_greenhouse_action is False)):
            return

        if status != self.__STATE_OFF_KEY and current_priority is False and is_greenhouse_action is True:
            self.__status = (status, True)
            return

        self.__status = (self.__STATE_ON_KEY, is_greenhouse_action)
        self.__publish_notification(mqtt_client, "OPENED")
        print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned on!", flush=True)


    def turn_off(self, is_greenhouse_action, mqtt_client):
        status, current_priority = self.__status

        if ((status != self.__STATE_OFF_KEY and current_priority != is_greenhouse_action) or
                (status == self.__STATE_OFF_KEY and current_priority == is_greenhouse_action)):
            return

        if status == self.__STATE_OFF_KEY:
            self.__status = (self.__STATE_OFF_KEY, is_greenhouse_action)
            return

        # status != self.__STATE_OFF_KEY and current_priority == is_greenhouse_action
        self.__status = (self.__STATE_OFF_KEY, is_greenhouse_action)
        self.__publish_notification(mqtt_client, "CLOSED")
        print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned off!", flush=True)

    def operate_at_full_throttle(self, is_greenhouse_action, mqtt_client):
        status, current_priority = self.__status

        if status != self.__STATE_FULL_THROTTLE_KEY:
            self.__status = (self.__STATE_FULL_THROTTLE_KEY, is_greenhouse_action)
            self.__publish_notification(mqtt_client, "OPERATING AT FULL THROTTLE")
            print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler now operating at full throttle!", flush=True)
            return

        if is_greenhouse_action:
            self.__status = (self.__STATE_FULL_THROTTLE_KEY, True)

    def __publish_notification(self, mqtt_client, action):
        value = self.__NOTIFICATION_STRING_STRUCTURE.format(greenhouse_id = self.__greenhouse_id, plant_id = self.__plant_id, action = action)
        publish_value_on_action_notification_topic(mqtt_client, value)
