import os
import jwt
import json
import hashlib
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import RPi.GPIO as GPIO
import psutil  # For CPU temperature


class SecuritySystem:
    def __init__(self):
        encryption_key = os.getenv("ENCRYPTION_KEY")
        jwt_secret = os.getenv("JWT_SECRET")

        if not encryption_key or not jwt_secret:
            raise EnvironmentError(
                "Required environment variables (ENCRYPTION_KEY, JWT_SECRET) are missing."
            )

        self.session_tokens = {}
        self.cipher_suite = Fernet(encryption_key)
        self.jwt_secret = jwt_secret
        self.initialize_security_hardware()
        self.setup_logging()

    def initialize_security_hardware(self):
        """
        Initializes GPIO pins for the security system.
        """
        try:
            GPIO.setmode(GPIO.BCM)
            self.secure_pins = {
                "motion": 17,
                "door": 18,
                "window": 19,
                "siren": 20,
                "backup_power": 21,
            }
            for pin in self.secure_pins.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logging.info("Security hardware initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize security hardware: {e}")

    def authenticate_user(self, username, password):
        """
        Authenticates a user and generates a JWT token if credentials are valid.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.

        Returns:
            str: JWT token if authentication is successful, None otherwise.
        """
        hashed_password = self.hash_password(password)
        user = self.verify_credentials(username, hashed_password)
        if user:
            token = self.generate_token(user)
            self.session_tokens[user["user_id"]] = token
            return token
        logging.warning(f"Authentication failed for username: {username}")
        return None

    def verify_token(self, token):
        """
        Verifies the validity of a JWT token.

        Args:
            token (str): The JWT token to verify.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            decoded = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return self.session_tokens.get(decoded["user_id"]) == token
        except jwt.ExpiredSignatureError:
            logging.warning("Token verification failed: Token has expired.")
        except jwt.InvalidTokenError:
            logging.warning("Token verification failed: Invalid token.")
        return False

    def encrypt_data(self, data):
        """
        Encrypts sensitive data.

        Args:
            data (dict): Data to encrypt.

        Returns:
            bytes: Encrypted data.
        """
        try:
            return self.cipher_suite.encrypt(json.dumps(data).encode())
        except Exception as e:
            logging.error(f"Failed to encrypt data: {e}")
            raise

    def decrypt_data(self, encrypted_data):
        """
        Decrypts encrypted data.

        Args:
            encrypted_data (bytes): The encrypted data to decrypt.

        Returns:
            dict: Decrypted data.
        """
        try:
            return json.loads(self.cipher_suite.decrypt(encrypted_data))
        except Exception as e:
            logging.error(f"Failed to decrypt data: {e}")
            raise

    def monitor_system_health(self):
        """
        Monitors the system's health by checking various components.

        Returns:
            dict: System health status including CPU temperature, voltage, backup power, and sensor statuses.
        """
        try:
            return {
                "cpu_temp": self.get_cpu_temperature(),
                "voltage": self.check_power_supply(),
                "backup_power": self.check_backup_power(),
                "sensor_status": self.check_all_sensors(),
            }
        except Exception as e:
            logging.error(f"Failed to monitor system health: {e}")
            return {}

    def intrusion_detection(self):
        """
        Detects intrusions based on sensor states and triggers an alarm if necessary.
        """
        try:
            sensor_states = self.check_all_sensors()
            if any(sensor_states.values()):
                self.trigger_alarm()
                self.notify_authorities()
                logging.warning("Intrusion detected!")
        except Exception as e:
            logging.error(f"Failed to perform intrusion detection: {e}")

    def hash_password(self, password):
        """
        Hashes a password using SHA-256.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        if not isinstance(password, str):
            raise ValueError("Password must be a string.")
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_credentials(self, username, hashed_password):
        """
        Verifies user credentials against a simple in-memory data store.

        Args:
            username (str): Username of the user.
            hashed_password (str): Hashed password.

        Returns:
            dict: User information if credentials are valid, None otherwise.
        """
        # Simulated user database
        user_database = {
            "admin": hashlib.sha256("admin123".encode()).hexdigest(),
            "user": hashlib.sha256("user123".encode()).hexdigest(),
        }

        if username in user_database and user_database[username] == hashed_password:
            logging.info(f"User {username} authenticated successfully.")
            return {"user_id": username, "username": username}
        logging.warning(f"Authentication failed for user {username}.")
        return None

    def generate_token(self, user):
        """
        Generates a JWT token for an authenticated user.

        Args:
            user (dict): User information.

        Returns:
            str: Generated JWT token.
        """
        try:
            return jwt.encode(
                {
                    "user_id": user["user_id"],
                    "exp": datetime.utcnow() + timedelta(hours=1),
                },
                self.jwt_secret,
                algorithm="HS256",
            )
        except Exception as e:
            logging.error(f"Failed to generate token: {e}")
            raise

    def get_cpu_temperature(self):
        """
        Retrieves the current CPU temperature.

        Returns:
            float: CPU temperature in degrees Celsius.
        """
        try:
            # Use psutil or read from system sensors
            temp = psutil.sensors_temperatures().get("cpu_thermal", [{}])[0].get(
                "current", 0.0
            )
            logging.info(f"CPU temperature: {temp}°C")
            return temp
        except Exception as e:
            logging.error(f"Failed to retrieve CPU temperature: {e}")
            return 0.0

    def check_power_supply(self):
        """
        Placeholder to check power supply status.

        Returns:
            float: Voltage of the power supply.
        """
        # Replace with actual logic
        return 12.0

    def check_backup_power(self):
        """
        Checks the status of the backup power.

        Returns:
            bool: True if backup power is operational, False otherwise.
        """
        try:
            backup_power_status = GPIO.input(self.secure_pins["backup_power"])
            if backup_power_status == GPIO.HIGH:
                logging.info("Backup power is operational.")
                return True
            else:
                logging.warning("Backup power is not operational.")
                return False
        except Exception as e:
            logging.error(f"Failed to check backup power: {e}")
            return False

    def check_all_sensors(self):
        """
        Checks the status of all connected sensors.

        Returns:
            dict: Dictionary containing sensor statuses.
        """
        try:
            return {name: GPIO.input(pin) for name, pin in self.secure_pins.items()}
        except Exception as e:
            logging.error(f"Failed to check sensors: {e}")
            return {}

    def trigger_alarm(self):
        """
        Triggers the security alarm.
        """
        logging.info("Alarm triggered!")

    def notify_authorities(self):
        """
        Sends a notification to authorities about an intrusion.
        """
        logging.info("Authorities notified.")
