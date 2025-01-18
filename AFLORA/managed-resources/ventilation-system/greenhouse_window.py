class GreenhouseWindow:

    __CLOSE_KEY = "CLOSE"
    __OPEN_KEY = "OPEN"

    def __init__(self, greenhouse_id, window_id) -> None:
        self.__greenhouse_id = greenhouse_id
        self.__window_id = window_id
        self.__status = self.__CLOSE_KEY

    def open(self):
        if self.__status != self.__OPEN_KEY:
            self.__status = self.__OPEN_KEY
            print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} opened!", flush=True)

    def close(self):
        if self.__status != self.__CLOSE_KEY:
            self.__status = self.__CLOSE_KEY
            print(f"Window {self.__window_id} in greenhouse {self.__greenhouse_id} closed!", flush=True)

