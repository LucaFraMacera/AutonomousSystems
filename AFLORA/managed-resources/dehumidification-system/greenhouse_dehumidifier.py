from time import sleep
from managed_resource import publish_value_on_action_notification_topic

class GreenhouseDehumidifier:

    __STATE_OFF_KEY = "OFF"
    __STATE_ON_KEY = "ON"
    __STATE_FULL_THROTTLE_KEY = "FULL_THROTTLE"
    __NOTIFICATION_STRING_STRUCTURE = "Dehumidifier {dehumidifier_id} in greenhouse {greenhouse_id} {action}!"

    def __init__(self, greenhouse_id, dehumidifier_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__dehumidifier_id = dehumidifier_id
        self.__status = self.__STATE_OFF_KEY

    def turn_on(self, mqtt_client):
        if self.__status != self.__STATE_ON_KEY:
            self.__status = self.__STATE_ON_KEY
            self.__publish_notification(mqtt_client, "TURNED ON")
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned on!", flush=True)

    def turn_off(self, mqtt_client):
        if self.__status != self.__STATE_OFF_KEY:
            self.__status = self.__STATE_OFF_KEY
            self.__publish_notification(mqtt_client, "TURNED OFF")
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned off!", flush=True)

    def operate_at_full_throttle(self, mqtt_client):
        if self.__status != self.__STATE_FULL_THROTTLE_KEY:
            self.turn_on(mqtt_client)
            sleep(1)
            self.__status = self.__STATE_FULL_THROTTLE_KEY
            self.__publish_notification(mqtt_client, "OPERATING FULL THROTTLE")
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} now operating at full throttle!", flush=True)

    def __publish_notification(self, mqtt_client, action):
        value = self.__NOTIFICATION_STRING_STRUCTURE.format(greenhouse_id = self.__greenhouse_id, dehumidifier_id = self.__dehumidifier_id, action = action)
        publish_value_on_action_notification_topic(mqtt_client, value)

