from analyzer import Analyzer
import json


class PlantAnalyzer(Analyzer):

    __STATUS_THRESHOLDS_JSON_FILE_PATH = "sensors-config/plant-status-thresholds.json"
    __STATUS_THRESHOLDS_SOIL_MOISTURE_KEY = "soil_moisture"
    __STATUS_THRESHOLDS_NORMAL_KEY = "NORMAL"
    __STATUS_THRESHOLDS_THIRSTY_KEY = "THIRSTY"
    __STATUS_THRESHOLDS_DEHYDRATED_KEY = "DEHYDRATED"

    __PLANT_STATUS_TOPIC_STRUCTURE = "/greenhouse_{greenhouse_ID}/plant_{plant_ID}/status" # Plant status topic structure

    def __init__(self):
        super().__init__()
        self.__status_thresholds_data = self.__retrieve_status_thresholds_data()

    def __retrieve_status_thresholds_data(self):
        with open(self.__STATUS_THRESHOLDS_JSON_FILE_PATH, 'r') as file:
            return json.load(file)

    def __check_plant_status(self, soil_moisture_value):
        # NORMAL LEVEL
        if self.__status_thresholds_data[self.__STATUS_THRESHOLDS_NORMAL_KEY][self.__STATUS_THRESHOLDS_SOIL_MOISTURE_KEY][0] <= soil_moisture_value <= \
                self.__status_thresholds_data[self.__STATUS_THRESHOLDS_NORMAL_KEY][self.__STATUS_THRESHOLDS_SOIL_MOISTURE_KEY][1]:
            return self.__STATUS_THRESHOLDS_NORMAL_KEY

        # THIRSTY LEVEL
        if self.__status_thresholds_data[self.__STATUS_THRESHOLDS_THIRSTY_KEY][self.__STATUS_THRESHOLDS_SOIL_MOISTURE_KEY][0] <= soil_moisture_value <= \
                self.__status_thresholds_data[self.__STATUS_THRESHOLDS_THIRSTY_KEY][self.__STATUS_THRESHOLDS_SOIL_MOISTURE_KEY][1]:
            return self.__STATUS_THRESHOLDS_THIRSTY_KEY

        # DEHYDRATED LEVEL
        return self.__STATUS_THRESHOLDS_DEHYDRATED_KEY

    def __check_critical_status_and_send_alert(self, greenhouse_id, plant_id, soil_moisture_value):
        plant_status = self.__check_plant_status(soil_moisture_value)
        print(f"Greenhouse: {greenhouse_id}, Plant: {plant_id}, Status: {plant_status}", flush=True)

        if plant_status == self.__STATUS_THRESHOLDS_NORMAL_KEY:
            return False  # value is normal

        self.__publish_on_plant_status_topics(greenhouse_id=greenhouse_id, plant_id=plant_id, plant_status=plant_status)
        return True  # value is critical

    def __publish_on_plant_status_topics(self, greenhouse_id, plant_id, plant_status):
        plant_status_topic = self.__PLANT_STATUS_TOPIC_STRUCTURE.format(greenhouse_ID=greenhouse_id, plant_ID=plant_id)
        self._publish_value_on_topic(plant_status.lower(), plant_status_topic)


    def _check_status(self):
        results = self._database.databaseRead({"start_time": "-24h", "sensor_type": "soil_moisture"})
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

                # check if current value is already above threshold
                if len(readings) > 0 and self.__check_critical_status_and_send_alert(greenhouse_id=greenhouse_id, plant_id=plant_id, soil_moisture_value=readings[0]):
                    print("Current value is critical!", flush=True)
                    continue

                predictions = self._predictNextValues(readings, window_size=3, num_predictions=3)
                print(f"Greenhouse: {greenhouse_id}, Plant: {plant_id}, Predictions: {predictions}", flush=True)
                is_plant_critical = False
                index = 0
                while not is_plant_critical and index < len(predictions):
                    prediction = predictions[index]
                    # check if prediction is above threshold
                    is_plant_critical = self.__check_critical_status_and_send_alert(greenhouse_id=greenhouse_id, plant_id=plant_id, soil_moisture_value=prediction)
                    if is_plant_critical:
                        print("Predicted values show that plant will be critical!", flush=True)
                    index += 1

                if not is_plant_critical:
                    print("Predicted values show that plant will stay normal!", flush=True)
                    self.__publish_on_plant_status_topics(greenhouse_id=greenhouse_id, plant_id=plant_id, plant_status=self.__STATUS_THRESHOLDS_NORMAL_KEY)