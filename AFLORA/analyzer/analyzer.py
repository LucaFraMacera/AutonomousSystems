import paho.mqtt.client as mqtt
import numpy as np
from sklearn.linear_model import LinearRegression
from abc import ABC, abstractmethod
import os
import json
from knowledge.database import Database
from time import sleep

MQTT_SERVICE_NAME = os.environ.get('MQTT_SERVICE_NAME')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT'))
VALUE_KEY = 'value'


class Analyzer(ABC):

    def __init__(self):
        # Message Broker connection
        self._client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self._client_mqtt.connect(MQTT_SERVICE_NAME, MQTT_BROKER_PORT)
        # No loop forever here
        # Database
        self._database = Database()

    @abstractmethod
    def _check_status(self):
        pass

    def _retrieve_status_thresholds_data(self, path):
        with open(path, 'r') as file:
            return json.load(file)

    def start(self):
        print("Analyzer is starting...", flush=True)
        while True:
            self._check_status()
            print("Sleeping", flush=True)
            sleep(2)

    def _publish_value_on_topic(self, value, topic):
        payload = json.dumps({VALUE_KEY: value})  # Serialize only the JSON value
        self._client_mqtt.publish(topic, payload)

    def _predictNextValues(self, values, window_size, num_predictions):
        """
        Predicts multiple successive values in the sequence using linear regression with a moving window.
        """

        # Convert list of values to a NumPy array
        values_array = np.array(values)

        # Ensure there is enough data
        if len(values_array) <= window_size:
            print(f"Not enough data to generate windows. Dataset size: {len(values_array)}, window_size: {window_size}", flush=True)
            return []

        # Prepare the data for linear regression
        X = []
        y = []

        # Create the data windows and corresponding targets
        for i in range(len(values_array) - window_size):
            X.append(values_array[i:i + window_size])  # Use the values in the window as features
            y.append(values_array[i + window_size])  # Predict the next value

        X = np.array(X)
        y = np.array(y)

        # Debugging: Print shapes and contents of X and y
        # print(f"X shape: {X.shape}, y shape: {y.shape}", flush=True)
        # print(f"X: {X}", flush=True)
        # print(f"y: {y}", flush=True)

        # Ensure X is 2D and y is 1D
        X = X.reshape(-1, window_size)
        y = y.ravel()

        # Create a linear regression model
        model = LinearRegression()

        # Train the model on the prepared data
        model.fit(X, y)

        # Predict the next values in the sequence
        last_window = values_array[-window_size:]  # Take the last elements as a moving window
        predictions = []

        for _ in range(num_predictions):
            # Predict the next value
            next_value = model.predict(last_window.reshape(1, -1))[0]
            predictions.append(next_value)

            # Update the window by appending the predicted value and removing the oldest one
            last_window = np.roll(last_window, -1)  # Shift left
            last_window[-1] = next_value  # Add the new prediction

        return predictions
