class GreenhouseWindow:

    def __init__(self, greenhouse_id, window_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__window_id = window_id

    def open(self):
        print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} opened!", flush=True)

    def close(self):
        print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} closed!", flush=True)

