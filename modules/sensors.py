import RPi.GPIO as GPIO
from datetime import datetime
import json
import logging
from threading import Thread
import time
import random  # Simulated analog data for ADC


class SensorSystem:
    def __init__(self):
        self.sensors = self.initialize_sensors()
        self.sensor_data = {}
        self.alert_thresholds = self.load_thresholds()
        self.start_monitoring()
        self.setup_logging()

    def setup_logging(self):
        """
        Sets up logging for the SensorSystem.
        """
        logging.basicConfig(
            filename="logs/sensors.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logging.info("SensorSystem initialized successfully.")

    def initialize_sensors(self):
        """
        Initializes sensors and sets up GPIO pins.

        Returns:
            dict: Dictionary containing sensor configurations.
        """
        try:
            GPIO.setmode(GPIO.BCM)
            sensors = {
                "motion": {"pin": 17, "type": "digital"},
                "door": {"pin": 18, "type": "digital"},
                "window": {"pin": 19, "type": "digital"},
                "temperature": {"pin": 20, "type": "analog"},
                "humidity": {"pin": 21, "type": "analog"},
                "smoke": {"pin": 22, "type": "digital"},
                "water": {"pin": 23, "type": "digital"},
            }

            for sensor in sensors.values():
                GPIO.setup(sensor["pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logging.info("Sensors initialized successfully.")
            return sensors
        except Exception as e:
            logging.error(f"Failed to initialize sensors: {e}")
            return {}

    def start_monitoring(self):
        """
        Starts the background thread for continuous sensor monitoring.
        """
        Thread(target=self.continuous_monitoring, daemon=True).start()
        logging.info("Continuous monitoring started.")

    def continuous_monitoring(self):
        """
        Continuously monitors sensors and updates their data.
        """
        while True:
            try:
                for sensor_name, sensor in self.sensors.items():
                    reading = self.read_sensor(sensor)
                    self.sensor_data[sensor_name] = {
                        "value": reading,
                        "timestamp": datetime.now().isoformat(),
                        "status": self.check_threshold(sensor_name, reading),
                    }
                logging.debug(f"Updated sensor data: {self.sensor_data}")
            except Exception as e:
                logging.error(f"Error during monitoring: {e}")
            time.sleep(1)

    def read_sensor(self, sensor):
        """
        Reads the value from a sensor.

        Args:
            sensor (dict): Sensor configuration.

        Returns:
            int/float: The sensor reading.
        """
        try:
            if sensor["type"] == "digital":
                return GPIO.input(sensor["pin"])
            else:
                return self.read_analog_sensor(sensor["pin"])
        except Exception as e:
            logging.error(f"Failed to read sensor {sensor}: {e}")
            return None

    def read_analog_sensor(self, pin):
        """
        Simulates reading analog sensor data using a random value.

        Args:
            pin (int): GPIO pin of the analog sensor.

        Returns:
            float: Simulated analog sensor reading.
        """
        try:
            # Simulating an analog sensor read
            simulated_value = random.uniform(0, 100)
            logging.debug(f"Analog sensor on pin {pin} read value: {simulated_value}")
            return simulated_value
        except Exception as e:
            logging.error(f"Failed to read analog sensor on pin {pin}: {e}")
            return None

    def check_threshold(self, sensor_name, value):
        """
        Checks if a sensor reading exceeds alert thresholds.

        Args:
            sensor_name (str): Name of the sensor.
            value (int/float): Sensor reading value.

        Returns:
            str: 'ALERT' if thresholds are exceeded, 'NORMAL' otherwise.
        """
        try:
            threshold = self.alert_thresholds.get(sensor_name, {})
            if (
                value > threshold.get("max", float("inf"))
                or value < threshold.get("min", float("-inf"))
            ):
                self.trigger_alert(sensor_name, value)
                return "ALERT"
            return "NORMAL"
        except Exception as e:
            logging.error(f"Failed to check threshold for {sensor_name}: {e}")
            return "ERROR"

    def load_thresholds(self):
        """
        Loads alert thresholds for sensors.

        Returns:
            dict: Dictionary containing thresholds for each sensor.
        """
        # Example thresholds; replace with a real data source if necessary
        return {
            "motion": {"max": 1, "min": 0},
            "door": {"max": 1, "min": 0},
            "window": {"max": 1, "min": 0},
            "temperature": {"max": 50, "min": -10},
            "humidity": {"max": 100, "min": 20},
            "smoke": {"max": 1, "min": 0},
            "water": {"max": 1, "min": 0},
        }

    def trigger_alert(self, sensor_name, value):
        """
        Triggers an alert for a specific sensor.

        Args:
            sensor_name (str): Name of the sensor.
            value (int/float): Sensor reading value.
        """
        alert_message = (
            f"ALERT: {sensor_name.capitalize()} sensor detected an issue! Value: {value}"
        )
        logging.warning(alert_message)

    def get_sensor_status(self):
        """
        Retrieves the current status of all sensors.

        Returns:
            dict: Dictionary containing sensor data, system health, and last update timestamp.
        """
        return {
            "sensor_data": self.sensor_data,
            "system_status": self.check_system_health(),
            "last_updated": datetime.now().isoformat(),
        }

    def check_system_health(self):
        """
        Checks the overall system health based on sensor statuses.

        Returns:
            str: 'HEALTHY' if all sensors are functioning normally, 'UNHEALTHY' otherwise.
        """
        try:
            all_sensors_ok = all(
                data["status"] == "NORMAL" for data in self.sensor_data.values()
            )
            system_status = "HEALTHY" if all_sensors_ok else "UNHEALTHY"
            logging.info(f"System health check: {system_status}")
            return system_status
        except Exception as e:
            logging.error(f"Failed to check system health: {e}")
            return "ERROR"
