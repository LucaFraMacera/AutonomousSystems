FROM nodered/node-red:4.0
USER root
RUN npm install node-red-dashboard
RUN npm install node-red-contrib-influxdb
RUN npm install node-red-contrib-telegrambot

# Installa il parser json
RUN apk add --no-cache jq

USER node-red

# Load environment variable containing sensors configuration
ENTRYPOINT ["/bin/sh", "-c", "export PLANT_SENSORS=$(cat /config/plant-sensors-config.json | jq -c .)&& export GREENHOUSE_SENSORS=$(cat /config/greenhouse-sensors-config.json | jq -c .) && exec npm start --cache /data/.npm -- --userDir /data"]
