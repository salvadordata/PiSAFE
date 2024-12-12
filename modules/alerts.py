from twilio.rest import Client
from datetime import datetime
import logging
import json
from OpenENDEC.decode import format_message
from cryptography.fernet import Fernet

class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
        self.cipher_suite = Fernet(os.getenv('ENCRYPTION_KEY'))
        self.alert_history = []
        self.initialize_logging()

    def initialize_logging(self):
        logging.basicConfig(
            filename='logs/alerts.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def process_eas_message(self, message, geographic_area=None):
        decoded_message = format_message(message)
        encrypted_message = self.encrypt_message(decoded_message)
        self.validate_alert(decoded_message)
        self.distribute_alert(encrypted_message, geographic_area)
        self.log_alert(decoded_message)
        return decoded_message

    def distribute_alert(self, alert, area=None):
        recipients = self.get_recipients(area)
        for recipient in recipients:
            self.send_sms(recipient, alert)
            self.send_websocket(recipient, alert)
            self.trigger_sirens(area)

    def validate_alert(self, alert):
        if not self.is_valid_format(alert):
            raise ValueError("Invalid alert format")
        if self.is_duplicate(alert):
            raise ValueError("Duplicate alert detected")
        return True

    def encrypt_message(self, message):
        return self.cipher_suite.encrypt(json.dumps(message).encode())

    def decrypt_message(self, encrypted_message):
        return json.loads(self.cipher_suite.decrypt(encrypted_message))

    def trigger_sirens(self, area):
        siren_locations = self.get_siren_locations(area)
        for siren in siren_locations:
            self.activate_siren(siren)
