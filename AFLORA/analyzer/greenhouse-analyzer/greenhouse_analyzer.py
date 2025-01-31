from analyzer import Analyzer
import json


class GreenhouseAnalyzer(Analyzer):

    __STATUS_THRESHOLDS_JSON_FILE_PATH = "sensors-config/greenhouse-status-thresholds.json"

    __STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY = "temperature"
    __STATUS_THRESHOLDS_HUMIDITY_SENSOR_KEY = "humidity"
    __STATUS_THRESHOLDS_CO2_SENSOR_KEY = "co2"
    __STATUS_THRESHOLDS_SMOKE_SENSOR_KEY = "smoke"
    __STATUS_THRESHOLDS_FINE_DUST_SENSOR_KEY = "fine_dust"

    __STATUS_THRESHOLDS_NORMAL_KEY = "NORMAL"
    __STATUS_THRESHOLDS_HIGH_CO2_KEY = "HIGH_CO2"
    __STATUS_THRESHOLDS_EXTREME_CO2_KEY = "EXTREME_CO2"
    __STATUS_THRESHOLDS_SMOKE_KEY = "SMOKE"
    __STATUS_THRESHOLDS_FIRE_KEY = "FIRE"
    __STATUS_THRESHOLDS_HIGH_DUST_KEY = "HIGH_DUST"
    __STATUS_THRESHOLDS_EXTREME_DUST_KEY = "EXTREME_DUST"
    __STATUS_THRESHOLDS_HIGH_TEMPERATURE_KEY = "HIGH_TEMPERATURE"
    __STATUS_THRESHOLDS_EXTREME_TEMPERATURE_KEY = "EXTREME_TEMPERATURE"
    __STATUS_THRESHOLDS_HIGH_HUMIDITY_KEY = "HIGH_HUMIDITY"
    __STATUS_THRESHOLDS_EXTREME_HUMIDITY_KEY = "EXTREME_HUMIDITY"

    __GREENHOUSE_STATUS_TOPIC_STRUCTURE = "/greenhouse_{greenhouse_ID}/status"  # Greenhouse status topic structure

    def __init__(self):
        super().__init__()
        self.__status_thresholds_data = self._retrieve_status_thresholds_data(self.__STATUS_THRESHOLDS_JSON_FILE_PATH)

    def __publish_on_plant_status_topics(self, greenhouse_id, greenhouse_id_status):
        plant_status_topic = self.__GREENHOUSE_STATUS_TOPIC_STRUCTURE.format(greenhouse_ID=greenhouse_id)
        self._publish_value_on_topic(greenhouse_id_status.lower(), plant_status_topic)

    def __assess_status(self, sensor_readings):
        # Order matters!
        co2_sensor_reading = sensor_readings[self.__STATUS_THRESHOLDS_CO2_SENSOR_KEY]
        dust_sensor_reading = sensor_readings[self.__STATUS_THRESHOLDS_FINE_DUST_SENSOR_KEY]
        temperature_sensor_reading = sensor_readings[self.__STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY]
        humidity_sensor_reading = sensor_readings[self.__STATUS_THRESHOLDS_HUMIDITY_SENSOR_KEY]
        smoke_sensor_reading = sensor_readings[self.__STATUS_THRESHOLDS_SMOKE_SENSOR_KEY]

        # FIRE
        fire_sensors_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_FIRE_KEY]
        if (smoke_sensor_reading is not None and
                fire_sensors_thresholds[self.__STATUS_THRESHOLDS_SMOKE_SENSOR_KEY] == smoke_sensor_reading and
                temperature_sensor_reading is not None and
                fire_sensors_thresholds[self.__STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY][0] <= temperature_sensor_reading <= fire_sensors_thresholds[self.__STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY][1] and
                co2_sensor_reading is not None and
                fire_sensors_thresholds[self.__STATUS_THRESHOLDS_CO2_SENSOR_KEY][0] <= co2_sensor_reading <= fire_sensors_thresholds[self.__STATUS_THRESHOLDS_CO2_SENSOR_KEY][1]):
            return self.__STATUS_THRESHOLDS_FIRE_KEY

        # SMOKE
        if smoke_sensor_reading is not None and self.__status_thresholds_data[self.__STATUS_THRESHOLDS_SMOKE_KEY][self.__STATUS_THRESHOLDS_SMOKE_SENSOR_KEY] == smoke_sensor_reading:
            return self.__STATUS_THRESHOLDS_SMOKE_KEY

        # EXTREME_CO2
        extreme_co2_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_EXTREME_CO2_KEY][self.__STATUS_THRESHOLDS_CO2_SENSOR_KEY]
        if co2_sensor_reading is not None and extreme_co2_thresholds[0] <= co2_sensor_reading <= extreme_co2_thresholds[1]:
            return self.__STATUS_THRESHOLDS_EXTREME_CO2_KEY

        # EXTREME_DUST
        extreme_dust_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_EXTREME_DUST_KEY][self.__STATUS_THRESHOLDS_FINE_DUST_SENSOR_KEY]
        if dust_sensor_reading is not None and extreme_dust_thresholds[0] <= dust_sensor_reading <= extreme_dust_thresholds[1]:
            return self.__STATUS_THRESHOLDS_EXTREME_DUST_KEY

        # EXTREME_TEMPERATURE
        extreme_temperature_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_EXTREME_TEMPERATURE_KEY][self.__STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY]
        if temperature_sensor_reading is not None and extreme_temperature_thresholds[0] <= temperature_sensor_reading <= extreme_temperature_thresholds[1]:
            return self.__STATUS_THRESHOLDS_EXTREME_TEMPERATURE_KEY

        # EXTREME_HUMIDITY
        extreme_humidity_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_EXTREME_HUMIDITY_KEY][self.__STATUS_THRESHOLDS_HUMIDITY_SENSOR_KEY]
        if humidity_sensor_reading is not None and extreme_humidity_thresholds[0] <= humidity_sensor_reading <= extreme_humidity_thresholds[1]:
            return self.__STATUS_THRESHOLDS_EXTREME_HUMIDITY_KEY

        # HIGH_CO2
        high_co2_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_HIGH_CO2_KEY][self.__STATUS_THRESHOLDS_CO2_SENSOR_KEY]
        if co2_sensor_reading is not None and high_co2_thresholds[0] <= co2_sensor_reading <= high_co2_thresholds[1]:
            return self.__STATUS_THRESHOLDS_HIGH_CO2_KEY

        # HIGH_DUST
        high_dust_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_HIGH_DUST_KEY][self.__STATUS_THRESHOLDS_FINE_DUST_SENSOR_KEY]
        if dust_sensor_reading is not None and high_dust_thresholds[0] <= dust_sensor_reading <= high_dust_thresholds[1]:
            return self.__STATUS_THRESHOLDS_HIGH_DUST_KEY

        # EXTREME_TEMPERATURE
        high_temperature_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_HIGH_TEMPERATURE_KEY][self.__STATUS_THRESHOLDS_TEMPERATURE_SENSOR_KEY]
        if temperature_sensor_reading is not None and high_temperature_thresholds[0] <= temperature_sensor_reading <= high_temperature_thresholds[1]:
            return self.__STATUS_THRESHOLDS_HIGH_TEMPERATURE_KEY

        # EXTREME_HUMIDITY
        high_humidity_thresholds = self.__status_thresholds_data[self.__STATUS_THRESHOLDS_HIGH_HUMIDITY_KEY][self.__STATUS_THRESHOLDS_HUMIDITY_SENSOR_KEY]
        if humidity_sensor_reading is not None and high_humidity_thresholds[0] <= humidity_sensor_reading <= high_humidity_thresholds[1]:
            return self.__STATUS_THRESHOLDS_HIGH_HUMIDITY_KEY

        # NORMAL
        return self.__STATUS_THRESHOLDS_NORMAL_KEY

    def __check_critical_status_and_send_alert(self, greenhouse_id, sensor_readings):
        greenhouse_status = self.__assess_status(sensor_readings)
        print(f"Greenhouse: {greenhouse_id}, Status: {greenhouse_status}", flush=True)

        if greenhouse_status == self.__STATUS_THRESHOLDS_NORMAL_KEY:
            return False

        self.__publish_on_plant_status_topics(greenhouse_id=greenhouse_id, greenhouse_id_status=greenhouse_status)
        return True

    def build_greenhouse_sensors_single_readings(self, sensor_types):
        sensors_single_readings = {}
        for sensor, readings in sensor_types.items():
            sensors_single_readings[sensor] = None
            if len(readings) > 0:
                sensors_single_readings[sensor] = readings[0]
        return sensors_single_readings
    def _check_status(self):
        results = self._database.databaseRead({"measurement":"sensor-values", "start_time": "-24h", "sensor_type": ["co2", "fine_dust", "humidity", "smoke", "temperature"]})

        greenhouse_readings = {}
        for result in results:
            greenhouse_id = result["greenhouse_id"]
            sensor_type = result["sensor_type"]
            value = result["value"]
            if greenhouse_id not in greenhouse_readings:
                greenhouse_readings[greenhouse_id] = {}

            if sensor_type not in greenhouse_readings[greenhouse_id]:
                greenhouse_readings[greenhouse_id][sensor_type] = [value]
            else:
                greenhouse_readings[greenhouse_id][sensor_type].append(value)

        for greenhouse_id, sensor_types in greenhouse_readings.items():
            # check if current value is already above threshold
            current_sensors_single_readings = self.build_greenhouse_sensors_single_readings(sensor_types)
            if self.__check_critical_status_and_send_alert(greenhouse_id=greenhouse_id, sensor_readings=current_sensors_single_readings):
                print(f"Current value {current_sensors_single_readings} is critical!", flush=True)
                continue

            predictions = {}
            number_of_predicted_values = 3
            for sensor, readings in sensor_types.items():
                predictions[sensor] = self._predictNextValues(readings, window_size=3, num_predictions=number_of_predicted_values)
            print(f"Greenhouse: {greenhouse_id}, Predictions: {predictions}", flush=True)
            is_greenhouse_critical = False
            index = 0
            while not is_greenhouse_critical and index < number_of_predicted_values:
                prediction_single_readings = self.build_greenhouse_sensors_single_readings(predictions)
                # remove readings from predictions
                for sensor in sensor_types:
                    predictions[sensor] = predictions[sensor][1:]  # remove the first element
                # check if prediction is above threshold
                is_greenhouse_critical = self.__check_critical_status_and_send_alert(greenhouse_id=greenhouse_id, sensor_readings=prediction_single_readings)
                if is_greenhouse_critical:
                    print("Predicted values show that greenhouse will be critical!", flush=True)
                index += 1

            if not is_greenhouse_critical:
                print("Predicted values show that greenhouse will stay normal!", flush=True)
                self.__publish_on_plant_status_topics(greenhouse_id=greenhouse_id, greenhouse_id_status=self.__STATUS_THRESHOLDS_NORMAL_KEY)
