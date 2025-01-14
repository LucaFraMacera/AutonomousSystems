import paho.mqtt.client as mqtt
import numpy as np
from sklearn.linear_model import LinearRegression
from abc import ABC, abstractmethod
import os

MQTT_SERVICE_NAME = os.environ.get('MQTT_SERVICE_NAME')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT'))


class Analyzer(ABC):

    def __init__(self):
        # Message Broker connection
        self.__client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.__client_mqtt.connect(MQTT_SERVICE_NAME, MQTT_BROKER_PORT)

    @abstractmethod
    def __check_status(self):
        pass

    def __predictNextValues(self, values, window_size, num_predictions):
        """
        Predicts multiple successive values in the sequence using linear regression with a moving window.
        """

        # Convert list of values to a NumPy array
        values_array = np.array(values)

        # Prepare the data for linear regression
        X = []
        y = []

        # Create the data windows and corresponding targets
        for i in range(len(values_array) - window_size - num_predictions + 1):
            X.append(values_array[i:i + window_size])  # Use the values passed as features
            y.append(values_array[
                     i + window_size:i + window_size + num_predictions])  # The values are the targets to be predicted

        X = np.array(X)
        y = np.array(y)

        # Transform X into a two-dimensional array
        X = X.reshape(-1, window_size)

        # Create a linear regression model
        model = LinearRegression()

        # Train the model on the prepared data
        model.fit(X, y)

        # Predict the next values in the sequence
        last_window = values_array[-window_size:]  # Take the last elements as a moving window
        next_values = model.predict(last_window.reshape(1, -1))

        return next_values.flatten()
