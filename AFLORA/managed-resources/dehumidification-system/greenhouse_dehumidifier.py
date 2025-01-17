from time import sleep


class GreenhouseDehumidifier:

    def __init__(self, greenhouse_id, dehumidifier_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__dehumidifier_id = dehumidifier_id

    def turn_on(self):
        print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned on!", flush=True)

    def turn_off(self):
        print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} turned off!", flush=True)

    def operate_at_full_throttle(self):
        self.turn_on()
        sleep(1)
        print(f"Dehumidifier {self.__dehumidifier_id} in greenhouse {self.__greenhouse_id} now operating at full throttle!", flush=True)

