from time import sleep


class PlantSprinkler:

    def __init__(self, greenhouse_id, plant_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__plant_id = plant_id

    def turn_on(self):
        print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned on!", flush=True)

    def turn_off(self):
        print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler turned off!", flush=True)

    def operate_at_full_throttle(self):
        self.turn_on()
        sleep(1)
        print(f"Plant {self.__plant_id} in greenhouse {self.__greenhouse_id} sprinkler now operating at full throttle!", flush=True)
