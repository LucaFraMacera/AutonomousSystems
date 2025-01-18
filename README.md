# AFLORA: Autonomous Farming Life-cycle Observation with Real-time Analytics

## Introduction
Our project monitors data related to the greenhouse environment and plant health, including parameters such as temperature, humidity, and CO2 levels, as well as plant-specific metrics like soil moisture.

The primary goal of the system is to automate crop management, optimizing resources such as water and energy consumption while improving crop quality and yield.

The system is based on a MAPE-K LOOP architecture. It uses data gathered by sensors to store and analyze the current state of the crops, enabling it to decide which actuators to activate when detected levels exceed or fall below predefined thresholds.


## Project build and deploy steps
After cloning the repository write in the terminal: 

    cd ./AFLORA

###### To build and run the project execute:

    docker-compose build --no-cache

followed by

    docker-compose up

###### To delete all the containers execute:

    docker-compose down -v