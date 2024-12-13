import os
import logging
import json
from datetime import datetime
from twilio.rest import Client
from cryptography.fernet import Fernet
from OpenENDEC.decode import format_message


class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN")
        )
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise EnvironmentError("ENCRYPTION_KEY environment variable is missing.")
        self.cipher_suite = Fernet(encryption_key)
        self.alert_history = []
        self.initialize_logging()

    def initialize_logging(self):
        """
        Configures logging for alert processing.
        """
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename="logs/alerts.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def process_eas_message(self, message, geographic_area=None):
        """
        Processes an Emergency Alert System (EAS) message.

        Args:
            message (str): The raw EAS message.
            geographic_area (str, optional): The area to target the alert.

        Returns:
            str: The decoded and formatted alert message.
        """
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Invalid EAS message. Message must be a non-empty string.")

        decoded_message = format_message(message)
        encrypted_message = self.encrypt_message(decoded_message)
        self.validate_alert(decoded_message)
        self.distribute_alert(encrypted_message, geographic_area)
        self.log_alert(decoded_message)
        return decoded_message

    def distribute_alert(self, alert, area=None):
        """
        Distributes the alert via SMS, WebSocket, and sirens.

        Args:
            alert (str): The alert to distribute.
            area (str, optional): The geographic area for the alert.
        """
        recipients = self.get_recipients(area)
        for recipient in recipients:
            self.send_sms(recipient, alert)
            self.send_websocket(recipient, alert)
        self.trigger_sirens(area)

    def validate_alert(self, alert):
        """
        Validates the alert for format and duplication.

        Args:
            alert (str): The alert to validate.

        Returns:
            bool: True if the alert is valid.

        Raises:
            ValueError: If the alert format is invalid or if it's a duplicate.
        """
        if not self.is_valid_format(alert):
            raise ValueError("Invalid alert format.")
        if self.is_duplicate(alert):
            raise ValueError("Duplicate alert detected.")
        return True

    def encrypt_message(self, message):
        """
        Encrypts the alert message.

        Args:
            message (str): The message to encrypt.

        Returns:
            bytes: The encrypted message.
        """
        try:
            return self.cipher_suite.encrypt(json.dumps(message).encode())
        except Exception as e:
            logging.error(f"Failed to encrypt message: {e}")
            raise

    def decrypt_message(self, encrypted_message):
        """
        Decrypts the alert message.

        Args:
            encrypted_message (bytes): The encrypted message.

        Returns:
            dict: The decrypted message as a dictionary.
        """
        try:
            return json.loads(self.cipher_suite.decrypt(encrypted_message))
        except Exception as e:
            logging.error(f"Failed to decrypt message: {e}")
            raise

    def trigger_sirens(self, area):
        """
        Activates sirens in the specified area.

        Args:
            area (str): The geographic area to activate sirens.
        """
        siren_locations = self.get_siren_locations(area)
        for siren in siren_locations:
            self.activate_siren(siren)

    def get_recipients(self, area=None):
        """
        Fetches recipients for the alert based on the area.

        Args:
            area (str, optional): The area to filter recipients.

        Returns:
            list: A list of recipient contact details.
        """
        # Example placeholder logic
        all_recipients = os.getenv("ALERT_RECIPIENTS", "").split(",")
        if area:
            # Filter logic can be applied based on geographic area
            return [recipient for recipient in all_recipients if "@" in recipient]
        return all_recipients

    def send_sms(self, recipient, alert):
        """
        Sends an SMS alert to the specified recipient.

        Args:
            recipient (str): The recipient's phone number.
            alert (str): The alert message.
        """
        try:
            self.twilio_client.messages.create(
                body=alert, from_=os.getenv("TWILIO_PHONE_NUMBER"), to=recipient
            )
            logging.info(f"Alert sent to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send SMS to {recipient}: {e}")

    def send_websocket(self, recipient, alert):
        """
        Sends an alert via WebSocket.

        Args:
            recipient (str): The recipient's identifier.
            alert (str): The alert message.
        """
        # Placeholder for WebSocket integration
        logging.info(f"WebSocket alert sent to {recipient}: {alert}")

    def log_alert(self, alert):
        """
        Logs the alert into the system.

        Args:
            alert (str): The alert message.
        """
        logging.info(f"Alert logged: {alert}")
        self.alert_history.append(alert)

    def is_valid_format(self, alert):
        """
        Checks if the alert format is valid.

        Args:
            alert (str): The alert message.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(alert, str) and len(alert) > 0

    def is_duplicate(self, alert):
        """
        Checks if the alert is a duplicate.

        Args:
            alert (str): The alert message.

        Returns:
            bool: True if the alert is a duplicate, False otherwise.
        """
        return alert in self.alert_history

    def get_siren_locations(self, area):
        """
        Fetches siren locations for the specified area.

        Args:
            area (str): The area to fetch siren locations for.

        Returns:
            list: A list of siren locations.
        """
        # Placeholder for siren location data
        return ["Siren1", "Siren2", "Siren3"]

    def activate_siren(self, siren):
        """
        Activates a specific siren.

        Args:
            siren (str): The identifier of the siren to activate.
        """
        # Placeholder for siren activation logic
        logging.info(f"Siren activated: {siren}")
