# Mock GPIO Setup for Development
import sys
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO

<<<<<<< HEAD

=======
>>>>>>> e310ef17bee2e7b01f1b226a71a3b4ef7582c4cb
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from utils.eas_utils import format_message
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
import logging
from twilio.rest import Client
from cryptography.fernet import Fernet
from datetime import datetime
import RPi.GPIO as GPIO

# Core Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Security Headers
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    content_security_policy={
        'default-src': "'self'",
        'img-src': "'self' data:",
        'script-src': "'self'"
    }
)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["300 per hour"]
)

# Encryption Setup
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Logging Configuration
logging.basicConfig(
    filename='logs/pisafe.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database Models
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Alert System
class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
        
    def process_eas_message(self, message):
        decoded = format_message(message)
        self.distribute_alert(decoded)
        return decoded

    def distribute_alert(self, alert):
        # SMS Alert
        self.twilio_client.messages.create(
            body=alert,
            from_=os.getenv('TWILIO_NUMBER'),
            to=os.getenv('ALERT_RECIPIENTS')
        )
        # Websocket Alert
        socketio.emit('alert', {'data': alert})
        # Log Alert
        logging.info(f"Alert Distributed: {alert}")

# Security Monitor
class SecurityMonitor:
    def __init__(self):
        self.sensors = self.initialize_sensors()
        
    def initialize_sensors(self):
        GPIO.setmode(GPIO.BCM)
        # Setup various sensors
        return {'motion': 17, 'door': 18, 'window': 19}

    def check_status(self):
        return {sensor: GPIO.input(pin) for sensor, pin in self.sensors.items()}

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/alert', methods=['POST'])
@login_required
def create_alert():
    data = request.json
    alert_system.process_eas_message(data['message'])
    return jsonify({'status': 'success'})

@app.route('/api/status')
@login_required
def system_status():
    return jsonify(security_monitor.check_status())

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    emit('status', security_monitor.check_status())

@socketio.on('test_alert')
def handle_test_alert():
    alert_system.process_eas_message("TEST-EAS-ALERT")

# Error Handling
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Error: {str(error)}")
    return jsonify({'error': str(error)}), 500

# Initialize Systems
alert_system = AlertSystem()
security_monitor = SecurityMonitor()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context='adhoc')
