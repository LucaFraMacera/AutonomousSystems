import requests
import json
import time
import os
import utils

# Configurazioni
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
GRAFANA_URL = os.getenv('GRAFANA_URL')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')

PLANT_SENSORS_FILE = "/app/sensors-config/plant-sensors-config.json"
GREENHOUSE_SENSORS_FILE = "/app/sensors-config/greenhouse-sensors-config.json"

print(f"INFLUXDB_BUCKET: {INFLUXDB_BUCKET}", flush=True)
print(f"GRAFANA_URL: {GRAFANA_URL}", flush=True)
print(f"GRAFANA_API_KEY: {GRAFANA_API_KEY}", flush=True)

# Invio della dashboard a Grafana
def upload_dashboard(dashboard):
    headers = {"Authorization": f"Bearer {GRAFANA_API_KEY}"}
    for _ in range(10):
        try:
            response = requests.post(
                f"{GRAFANA_URL}/api/dashboards/db",
                headers=headers,
                json=dashboard,
            )
            
            if response.status_code == 200:
                print("Dashboard created successfully!", flush=True)
                break
            else:
                print(f"Error: {response.text}", flush=True)
            
        except requests.exceptions.ConnectionError:
            print("Error: Unable to connect to Grafana", flush=True)
            time.sleep(2)
            continue

def create_and_upload_dashboard(sensor_config_file, is_plant_related, dashboard_title):
    sensors = utils.get_sensors(sensor_config_file)
    sensor_types = [sensor['name'] for sensor in sensors]
    if sensors:
        print(f"Found sensor types: {sensor_types}", flush=True)
        dashboard = utils.create_dashboard(sensors, INFLUXDB_BUCKET, is_plant_related, dashboard_title)
        upload_dashboard(dashboard)
    else:
        print("No sensor types found.", flush=True) 
    

if __name__ == "__main__":
    create_and_upload_dashboard(PLANT_SENSORS_FILE, True, "Plants Sensor Dashboard")
    create_and_upload_dashboard(GREENHOUSE_SENSORS_FILE, False, "Greenhouses Sensor Dashboard")



