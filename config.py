import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pisafe.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    REMEMBER_COOKIE_SAMESITE = "Strict"

    # Alert Settings
    ALERT_TIMEOUT = int(os.getenv("ALERT_TIMEOUT", 300))  # seconds
    MAX_ALERTS_PER_HOUR = int(os.getenv("MAX_ALERTS_PER_HOUR", 10))

    # Sensor Settings
    SENSOR_CHECK_INTERVAL = int(os.getenv("SENSOR_CHECK_INTERVAL", 5))  # seconds
    MOTION_SENSITIVITY = float(os.getenv("MOTION_SENSITIVITY", 0.8))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

