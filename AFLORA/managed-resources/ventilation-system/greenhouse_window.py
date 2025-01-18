from managed_resource import publish_value_on_action_notification_topic

class GreenhouseWindow:

    __CLOSE_KEY = "CLOSE"
    __OPEN_KEY = "OPEN"
    __NOTIFICATION_STRING_STRUCTURE = "Greenhouse {greenhouse_id} window {window_id} {action}!"

    def __init__(self, greenhouse_id, window_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__window_id = window_id
        self.__status = self.__CLOSE_KEY

    def open(self, mqtt_client):
        if self.__status != self.__OPEN_KEY:
            self.__status = self.__OPEN_KEY
            self.__publish_notification(mqtt_client, "OPENED")
            print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} opened!", flush=True)

    def close(self, mqtt_client):
        if self.__status != self.__CLOSE_KEY:
            self.__status = self.__CLOSE_KEY
            self.__publish_notification(mqtt_client, "CLOSED")
            print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} closed!", flush=True)

    def __publish_notification(self, mqtt_client, action):
        value = self.__NOTIFICATION_STRING_STRUCTURE.format(greenhouse_id = self.__greenhouse_id, window_id = self.__window_id, action = action)
        publish_value_on_action_notification_topic(mqtt_client, value)

