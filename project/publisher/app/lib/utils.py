PLANT_CONFIG_JSON_FILE_PATH = "/app/sensors-config/plants-config.json"
GREENHOUSE_SENSORS_CONFIG_JSON_FILE_PATH = "/app/sensors-config/greenhouse-sensors-config.json"
PLANT_SENSORS_CONFIG_JSON_FILE_PATH = "/app/sensors-config/plant-sensors-config.json"
GREENHOUSES_KEY = "greenhouses"
GREENHOUSE_ID_KEY = "greenhouse_id"
PLANTS_KEY = "plants"
SENSORS_KEY = "sensors"
LIMIT_KEY = "limit"
LETHAL_LIMIT_KEY = "lethal_limit"
NAME_KEY = "name"
BOUNDARIES_KEY = "boundaries"
THRESHOLDS_KEY = "thresholds"
MIN_KEY = 'min'
MAX_KEY = 'max'
THRESHOLD_MIN_KEY = 'threshold_min'
THRESHOLD_MAX_KEY = 'threshold_max'
VALUE_KEY = 'value'

# MQTT broker configuration
BROKER = "mqtt_broker"  # docker-compose.yml service name
PORT = 1883
GREENHOUSE_TOPIC_STRUCTURE = "/greenhouse_{greenhouse_ID}/{sensor_type}" # Greenhouse topic structure
PLANT_TOPIC_STRUCTURE = "/greenhouse_{greenhouse_ID}/plant_{plant_ID}/{sensor_type}" # Plant topic structure