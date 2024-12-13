# Mock GPIO Setup for Development
import sys
import fake_rpi

sys.modules["RPi"] = fake_rpi.RPi
sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from utils.eas_utils import format_message
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from twilio.rest import Client
from cryptography.fernet import Fernet
from datetime import datetime
import RPi.GPIO as GPIO

# Core Setup
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Security Headers
Talisman(
    app,
    force_https_permanent=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    content_security_policy={
        "default-src": "'self'",
        "img-src": "'self' data:",
        "script-src": "'self'",
    },
)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["300 per hour"],
)

# Encryption Setup
encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(encryption_key)

# Logging Configuration
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/pisafe.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Validate Environment Variables
def validate_env_vars():
    required_vars = ["TWILIO_SID", "TWILIO_TOKEN", "TWILIO_NUMBER", "ALERT_RECIPIENTS"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")


validate_env_vars()

# Database Models
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


# Alert System
class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

    def process_eas_message(self, message):
        if not message or not isinstance(message, str):
            raise ValueError("Invalid EAS message provided.")
        decoded = format_message(message)
        self.distribute_alert(decoded)
        return decoded

    def distribute_alert(self, alert):
        try:
            # SMS Alert
            self.twilio_client.messages.create(
                body=alert,
                from_=os.getenv("TWILIO_NUMBER"),
                to=os.getenv("ALERT_RECIPIENTS"),
            )
            # Websocket Alert
            socketio.emit("alert", {"data": alert})
            # Log Alert
            logging.info(f"Alert Distributed: {alert}")
        except Exception as e:
            logging.error(f"Failed to distribute alert: {str(e)}")


# Security Monitor
class SecurityMonitor:
    def __init__(self):
        self.sensors = self.initialize_sensors()

    def initialize_sensors(self):
        try:
            GPIO.setmode(GPIO.BCM)
            return {"motion": 17, "door": 18, "window": 19}
        except Exception as e:
            logging.error(f"Failed to initialize sensors: {str(e)}")
            return {}

    def check_status(self):
        try:
            return {sensor: GPIO.input(pin) for sensor, pin in self.sensors.items()}
        except Exception as e:
            logging.error(f"Error checking sensor status: {str(e)}")
            return {}


# Routes
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/alert", methods=["POST"])
@login_required
def create_alert():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request data"}), 400
    try:
        alert_system.process_eas_message(data["message"])
        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f"Failed to create alert: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status")
@login_required
def system_status():
    try:
        return jsonify(security_monitor.check_status())
    except Exception as e:
        logging.error(f"Failed to fetch system status: {str(e)}")
        return jsonify({"error": str(e)}), 500


# WebSocket Events
@socketio.on("connect")
def handle_connect():
    try:
        emit("status", security_monitor.check_status())
    except Exception as e:
        logging.error(f"WebSocket connect error: {str(e)}")


@socketio.on("test_alert")
def handle_test_alert():
    try:
        alert_system.process_eas_message("TEST-EAS-ALERT")
    except Exception as e:
        logging.error(f"Failed to process test alert: {str(e)}")


# Error Handling
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Unhandled Exception: {str(error)}")
    return jsonify({"error": str(error)}), 500


# Initialize Systems
alert_system = AlertSystem()
security_monitor = SecurityMonitor()

if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=5000, ssl_context="adhoc")
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
