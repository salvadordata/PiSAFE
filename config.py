# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.urandom(24)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pisafe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Alert Settings
    ALERT_TIMEOUT = 300  # seconds
    MAX_ALERTS_PER_HOUR = 10
    
    # Sensor Settings
    SENSOR_CHECK_INTERVAL = 5  # seconds
    MOTION_SENSITIVITY = 0.8
