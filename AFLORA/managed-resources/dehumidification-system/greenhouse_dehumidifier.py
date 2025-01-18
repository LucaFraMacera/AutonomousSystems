from time import sleep


class GreenhouseDehumidifier:

    __STATE_OFF_KEY = "OFF"
    __STATE_ON_KEY = "ON"
    __STATE_FULL_THROTTLE_KEY = "FULL_THROTTLE"

    def __init__(self, greenhouse_id, dehumidifier_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__dehumidifier_id = dehumidifier_id
        self.__status = self.__STATE_OFF_KEY

    def turn_on(self):
        if self.__status != self.__STATE_ON_KEY:
            self.__status = self.__STATE_ON_KEY
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned on!", flush=True)

    def turn_off(self):
        if self.__status != self.__STATE_OFF_KEY:
            self.__status = self.__STATE_OFF_KEY
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned off!", flush=True)

    def operate_at_full_throttle(self):
        if self.__status != self.__STATE_FULL_THROTTLE_KEY:
            self.turn_on()
            sleep(1)
            self.__status = self.__STATE_FULL_THROTTLE_KEY
            print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} now operating at full throttle!", flush=True)

