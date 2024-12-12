import RPi.GPIO as GPIO
from datetime import datetime
import json
import logging
from threading import Thread
import time

class SensorSystem:
    def __init__(self):
        self.sensors = self.initialize_sensors()
        self.sensor_data = {}
        self.alert_thresholds = self.load_thresholds()
        self.start_monitoring()

    def initialize_sensors(self):
        GPIO.setmode(GPIO.BCM)
        sensors = {
            'motion': {'pin': 17, 'type': 'digital'},
            'door': {'pin': 18, 'type': 'digital'},
            'window': {'pin': 19, 'type': 'digital'},
            'temperature': {'pin': 20, 'type': 'analog'},
            'humidity': {'pin': 21, 'type': 'analog'},
            'smoke': {'pin': 22, 'type': 'digital'},
            'water': {'pin': 23, 'type': 'digital'}
        }
        
        for sensor in sensors.values():
            GPIO.setup(sensor['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return sensors

    def start_monitoring(self):
        Thread(target=self.continuous_monitoring, daemon=True).start()

    def continuous_monitoring(self):
        while True:
            for sensor_name, sensor in self.sensors.items():
                reading = self.read_sensor(sensor)
                self.sensor_data[sensor_name] = {
                    'value': reading,
                    'timestamp': datetime.now().isoformat(),
                    'status': self.check_threshold(sensor_name, reading)
                }
            time.sleep(1)

    def read_sensor(self, sensor):
        if sensor['type'] == 'digital':
            return GPIO.input(sensor['pin'])
        else:
            return self.read_analog_sensor(sensor['pin'])

    def check_threshold(self, sensor_name, value):
        threshold = self.alert_thresholds.get(sensor_name, {})
        if value > threshold.get('max', float('inf')) or \
           value < threshold.get('min', float('-inf')):
            self.trigger_alert(sensor_name, value)
            return 'ALERT'
        return 'NORMAL'

    def get_sensor_status(self):
        return {
            'sensor_data': self.sensor_data,
            'system_status': self.check_system_health(),
            'last_updated': datetime.now().isoformat()
        }
