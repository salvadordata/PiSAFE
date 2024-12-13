import os
import sys
import json
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_required
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import fake_rpi

# Mock RPi GPIO for non-Raspberry Pi environments
sys.modules["RPi"] = fake_rpi.RPi
sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO
import RPi.GPIO as GPIO

# Flask App Initialization
app = Flask(__name__)
csrf = CSRFProtect(app)  # Enable CSRF protection
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Check for missing SECRET_KEY in production
if app.config["SECRET_KEY"] == "default_secret_key" and not app.debug:
    raise EnvironmentError("SECRET_KEY must be set in a production environment!")

socketio = SocketIO(app, cors_allowed_origins="*")

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)

# Security Headers using Flask-Talisman
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

# Logging Configuration
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/pisafe.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Encryption Key Setup
key = Fernet.generate_key()
cipher_suite = Fernet(key)


# Environment Variable Validation
def validate_env_vars():
    """Ensure required environment variables are set."""
    required_env_vars = [
        "TWILIO_SID",
        "TWILIO_TOKEN",
        "TWILIO_NUMBER",
        "ALERT_RECIPIENTS",
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


validate_env_vars()


# User Model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


# Alert System
class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN")
        )

    def process_eas_message(self, message):
        decoded = self.validate_message(message)
        self.distribute_alert(decoded)
        return decoded

    @staticmethod
    def validate_message(message):
        """Validate and sanitize the incoming message."""
        if not isinstance(message, str) or len(message) > 500:
            raise ValueError("Invalid message format or length.")
        return message.strip()

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


# Flask Routes
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/alert", methods=["POST"])
@csrf.exempt  # CSRF protection is not needed for API if handled via tokens
@login_required
@limiter.limit("10 per minute")  # Tighter rate limit for this endpoint
def create_alert():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400
    try:
        alert_system.process_eas_message(data["message"])
        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f"Failed to create alert: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status")
@login_required
@limiter.limit("5 per minute")
def system_status():
    return jsonify(security_monitor.check_status())


# WebSocket Events
@socketio.on("connect")
@login_required
def handle_connect():
    emit("status", security_monitor.check_status())


@socketio.on("test_alert")
@login_required
def handle_test_alert():
    alert_system.process_eas_message("TEST-EAS-ALERT")


# Error Handling
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Error: {str(error)}")
    return jsonify({"error": str(error)}), 500


# Initialize Core Systems
alert_system = AlertSystem()
security_monitor = SecurityMonitor()

# Enforce running only on Raspberry Pi
if not hasattr(GPIO, "BCM"):
    raise RuntimeError("This script must run on a Raspberry Pi.")

# Run Flask App
if __name__ == "__main__":
    app.debug = False  # Ensure debug mode is off in production
    socketio.run(app, host="0.0.0.0", port=5000, ssl_context="adhoc")
