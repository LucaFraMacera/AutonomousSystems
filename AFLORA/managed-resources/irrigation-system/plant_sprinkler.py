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
        self.__status = self.__STATE_OFF_KEY

    def turn_on(self, mqtt_client):
        if self.__status != self.__STATE_ON_KEY:
            self.__status = self.__STATE_ON_KEY
            self.__publish_notification(mqtt_client, "OPENED")
            print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned on!", flush=True)

    def turn_off(self, mqtt_client):
        if self.__status != self.__STATE_OFF_KEY:
            self.__status = self.__STATE_OFF_KEY
            self.__publish_notification(mqtt_client, "CLOSED")
            print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned off!", flush=True)

    def operate_at_full_throttle(self, mqtt_client):
        if self.__status != self.__STATE_FULL_THROTTLE_KEY:
            self.turn_on()
            sleep(1)
            self.__status = self.__STATE_FULL_THROTTLE_KEY
            self.__publish_notification(mqtt_client, "OPERATING AT FULL THROTTLE")
            print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler now operating at full throttle!", flush=True)

    def __publish_notification(self, mqtt_client, action):
        value = self.__NOTIFICATION_STRING_STRUCTURE.format(greenhouse_id = self.__greenhouse_id, plant_id = self.__plant_id, action = action)
        publish_value_on_action_notification_topic(mqtt_client, value)
