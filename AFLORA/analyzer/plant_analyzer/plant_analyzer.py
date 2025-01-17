from time import sleep
from analyzer import Analyzer
from knowledge.database import Database

class PlantAnalyzer(Analyzer):

    def __init__(self):
        super().__init__()
        self.__database = Database()
        self._check_status()

    def _check_status(self):
        while True:
            results = self.__database.databaseRead({"start_time": "-24h", "sensor_type": "soil_moisture"})
            plants_readings = {}
            for result in results:
                greenhouse_id = result["greenhouse_id"]
                plant_id = result["plant_id"]
                value = result["value"]
                if greenhouse_id not in plants_readings:
                    plants_readings[greenhouse_id] = {}

                if plant_id not in plants_readings[greenhouse_id]:
                    plants_readings[greenhouse_id][plant_id] = [value]
                else:
                    plants_readings[greenhouse_id][plant_id].append(value)

            for greenhouse_id, plants in plants_readings.items():
                for plant_id, readings in plants.items():
                    predictions = self._predictNextValues(readings, window_size=3, num_predictions=1)
                    print(f"{greenhouse_id}, {plant_id}, {float(predictions[0]) if len(predictions) > 0 else predictions}", flush=True)
            print("Sleeping", flush=True)
            sleep(2)
