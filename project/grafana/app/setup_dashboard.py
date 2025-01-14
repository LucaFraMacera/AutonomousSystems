import requests
import json
import time
import os

# Configurazioni
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
GRAFANA_URL = os.getenv('GRAFANA_URL')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')

print(f"INFLUXDB_BUCKET: {INFLUXDB_BUCKET}", flush=True)
print(f"GRAFANA_URL: {GRAFANA_URL}", flush=True)
print(f"GRAFANA_API_KEY: {GRAFANA_API_KEY}", flush=True)


# Query per ottenere i tipi di sensori
def get_sensors():
    with open('/app/sensors-config/sensors-config.json', 'r') as file:
        return json.load(file)["sensors"]
    
def create_threshold_steps(sensor_threshold_min, sensor_threshold_max):
    steps = []
    if sensor_threshold_min:
        # Aggiunge il limite inferiore
        steps.append({
            "color": "red",
            "value": None
        })
        steps.append({
            "color": "green",
            "value": sensor_threshold_min
        })
    else:
        # Valori inferiori al minimo
        steps.append({
            "color": "green",
            "value": None
        })
        
    if sensor_threshold_max:
        # Aggiunge il limite superiore
        steps.append({
            "color": "red",
            "value": sensor_threshold_max
        })
        
    return steps

def create_panel(sensor, i):
    print(sensor)
    is_thresholded = sensor["threshold_min"] or sensor["threshold_max"] 
    is_disc = sensor["chart_type"] == "disc"
    sensor_name = sensor["name"]
    sensor_name_as_title = sensor_name.replace('_', ' ').title()
    sensor_threshold_min = int(sensor["threshold_min"])
    sensor_threshold_max = int(sensor["threshold_max"])
    
    panel = {
            "title": f"{sensor_name_as_title}",
            "type": "timeseries" if not is_disc else "gauge",
            "gridPos": {"x": (i % 2) * 12, "y": (i // 2) * 9, "w": 12, "h": 9},
            "datasource": "influxdb",
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "fixedColor": "text" ,
                        "mode": "fixed"
                    } if not is_thresholded else {
                       "mode": "thresholds"
                        },
                    "custom": {
                        "axisBorderShow": False,
                        "axisCenteredZero": False,
                        "axisColorMode": "text",
                        "axisLabel": sensor_name_as_title,
                        "axisPlacement": "auto",
                        "barAlignment": 0 ,
                        "barWidthFactor": 0.6 ,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "viz": False
                        },
                        "insertNulls": False,
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {
                            "type": "linear"
                        },
                        "showPoints": "auto",
                        "spanNulls": False ,
                        "stacking": {
                            "group": "A" if not is_thresholded else "",
                            "mode": "none" if not is_thresholded else ""
                        },
                        "thresholdsStyle": {
                            "mode": "dashed"
                        }
                    } if not is_disc else {},
                    "displayName": f"{sensor_name_as_title} readings of plant #${{plant_id}} in farm #${{farm_id}}",
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": create_threshold_steps(sensor_threshold_min, sensor_threshold_max)
                    },
                    "unit": sensor["unit"],
                },
                "overrides": []
            },
            "targets": [
                {
                    "query": f"""
                            from(bucket: "{INFLUXDB_BUCKET}")
                            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                            |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
                            |> filter(fn: (r) => r["_field"] == "value")
                            |> filter(fn: (r) => r["farm_id"] == "${{farm_id}}")
                            |> filter(fn: (r) => r["plant_id"] == "${{plant_id}}")
                            |> filter(fn: (r) => r["sensor_type"] == "{sensor["name"]}")
                            |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
                            |> yield(name: "mean")
                    """,
                    "refId": "A",
                }
            ],
        }

    
    return panel
        
def create_dashboard(sensors):
    panels = []
    for i, sensor in enumerate(sensors):
        panels.append(
            create_panel(sensor, i)
        )
            
        

    dashboard = {
        "dashboard": {
            "title": "Dynamic Sensor Dashboard",
            "panels": panels,
            "templating": {
                "list": [
                    {
                        "name": "farm_id",
                        "label": "farm_id",
                        "description": "",
                        "type": "query",
                        "query": {
                            "query": """import "influxdata/influxdb/schema"
                                        schema.tagValues(
                                        bucket: "FLORA",
                                        tag: "farm_id"
                                        )
                                        """,
                            "datasource": "influxdb",
                            "sort": 0
                        },
                        "refresh": 2,  # Refresh on dashboard load
                        "hide": 0,
                        "multi": False,
                        "includeAll": False,
                        "current": {},
                        "options": []
                    },
                    {
                        "name": "plant_id",
                        "label": "plant_id",
                        "description": "",
                        "type": "query",
                        "query": {
                            "query": f"""import "influxdata/influxdb/schema"
                                        schema.tagValues(
                                        bucket: "FLORA",
                                        tag: "topic"
                                        ) |> filter(fn: (r) => r._value =~ /farm_${{farm_id}}/)
                                            """,
                            "datasource": "influxdb",
                            "sort": 0
                        },
                        "regex": f"/.*(\d{{3}})/",
                        "refresh": 2,  # Refresh on dashboard load
                        "hide": 0,
                        "multi": False,
                        "includeAll": False,
                        "current": {},
                        "options": []
                    }
                ]
            },
        },
        "overwrite": True,
    }
    return dashboard

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
        
    
    

if __name__ == "__main__":
    sensors = get_sensors()
    sensor_types = [sensor['name'] for sensor in sensors]
    if sensors:
        print(f"Found sensor types: {sensor_types}", flush=True)
        dashboard = create_dashboard(sensors)
        upload_dashboard(dashboard)
    else:
        print("No sensor types found.", flush=True)



