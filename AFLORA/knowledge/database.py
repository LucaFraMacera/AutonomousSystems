import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os


class Database:
    MEASUREMENT = "sensor-values"

    def __init__(self):
        self._bucket = os.environ.get("INFLUX_BUCKET", "")
        self._token = os.environ.get("INFLUX_TOKEN", "")
        self._url = os.environ.get("INFLUX_LINK", "http://localhost:8086")
        self._org = os.environ.get("INFLUX_ORG", "")
        self._client = influxdb_client.InfluxDBClient(url=self._url, token=self._token)

    def databaseWrite(self, point):
        point["measurement"] = self.MEASUREMENT
        write_api = self._client.write_api(write_options=SYNCHRONOUS)
        try:
            write_api.write(bucket=self._bucket, org=self._org, record=[point])
            print("Writing in InfluxDB successfully completed!", flush=True)
        except Exception as e:
            print(f"Error when writing to InfluxDB: {e}", flush=True)

    def databaseRead(self, tags):
        query_api = self._client.query_api()
        # Building query
        query = f'from(bucket:"{self._bucket}")'
        start_time = "start:" + (tags["start_time"] if "start_time" in tags.keys() else "-2m")
        end_time = ', stop:' + tags["end_time"] if "end_time" in tags.keys() else ""
        query += f'|>range({start_time}{end_time})'
        query += f'|>filter(fn:(r)=>r["_measurement"]=="{self.MEASUREMENT}")'
        for tag, value in tags.items():
            if tag != "start_time" and tag != "end_time":
                query += f'|>filter(fn:(r)=>r["{tag}"]=="{value}")'
        
        result = query_api.query(query=query, org=self._org)
        # Getting values from the returning records
        sensorReadings = []
        for table in result:
            for record in table.records:
                sensorReadings.append(self.createSensorData(record))
        return sensorReadings
    
    def createSensorData(self, record):
        current_sensor_reading = {
            "greenhouse_id": record["greenhouse_id"],
            "sensor_type": record["sensor_type"],
            "value": record.get_value()
        }
        if "plant_id" in record.values:
            current_sensor_reading["plant_id"] = record["plant_id"]
        return current_sensor_reading
