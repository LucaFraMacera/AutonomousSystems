import json

def get_sensors(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
def create_threshold_steps(sensor_threshold_min, sensor_threshold_max, sensor_thresholds_letal=None):
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
            "color": "orange",
            "value": sensor_threshold_max
        })
    
    if sensor_thresholds_letal:
        steps.append({
            "color": "red",
            "value": sensor_thresholds_letal
        })
        
    return steps

def create_panel(sensor, i, influx_bucket, is_plant_related=False):
    print(sensor)
    has_lethal_limit = "lethal_limit" in sensor
    is_thresholded = sensor["threshold_min"] or sensor["threshold_max"]  or has_lethal_limit
    is_disc = sensor["chart_type"] == "disc"
    sensor_name = sensor["name"]
    sensor_name_as_title = sensor_name.replace('_', ' ').title()
    sensor_threshold_min = int(sensor["threshold_min"])
    sensor_threshold_max = int(sensor["threshold_max"])
    sensor_lethal_limit = int(sensor["lethal_limit"]) if has_lethal_limit else None
    
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
                    "displayName": f"{sensor_name_as_title} readings {"of plant #${plant_id}" if is_plant_related else ""} in greenhouse #${{greenhouse_id}}",
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": create_threshold_steps(sensor_threshold_min, sensor_threshold_max, sensor_lethal_limit)
                    },
                    "unit": sensor["unit"],
                },
                "overrides": []
            },
            "targets": [
                {
                    "query": f"""
                            from(bucket: "{influx_bucket}")
                            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                            |> filter(fn: (r) => r["_measurement"] == "sensor-values")
                            |> filter(fn: (r) => r["_field"] == "value")
                            |> filter(fn: (r) => r["greenhouse_id"] == "${{greenhouse_id}}")
                            {'|> filter(fn: (r)=>r["plant_id"] == "${plant_id}")' if is_plant_related else ""}
                            |> filter(fn: (r) => r["sensor_type"] == "{sensor["name"]}")
                            |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
                            |> yield(name: "mean")
                    """,
                    "refId": "A",
                }
            ],
        }

    
    return panel

        
def create_dashboard(sensors, influx_bucket, is_plant_related=False, dashboard_title="Dynamic Dashboard"):
    panels = []
    for i, sensor in enumerate(sensors):
        panels.append(
            create_panel(sensor, i, influx_bucket, is_plant_related)
        )
    
    templating_list = []
    templating_list.append({
                        "name": "greenhouse_id",
                        "label": "greenhouse_id",
                        "description": "",
                        "type": "query",
                        "query": {
                            "query": """import "influxdata/influxdb/schema"
                                        schema.tagValues(
                                        bucket: "AFLORA",
                                        tag: "greenhouse_id"
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
                    })
    
    if is_plant_related:
        templating_list.append({
                        "name": "plant_id",
                        "label": "plant_id",
                        "description": "",
                        "type": "query",
                        "query": {
                            "query": f"""import "influxdata/influxdb/schema"
                                        schema.tagValues(
                                        bucket: "AFLORA",
                                        tag: "plant_id"
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
                    })
        

    dashboard = {
        "dashboard": {
            "title": dashboard_title,
            "panels": panels,
            "templating": {
                "list": templating_list
            },
        },
        "overwrite": True,
    }
    return dashboard