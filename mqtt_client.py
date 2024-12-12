import sys
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
import RPi.GPIO as GPIO
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
from twilio.rest import Client


# MQTT Configuration
BROKER = "localhost"  # For development testing
PORT = 1883
TOPIC = "eas/alert"


# Twilio Configuration (SMS, Voice Alerts)
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"  # Twilio phone number
RECIPIENTS = ["+19876543210", "+12345678901"]  # Add recipient numbers


# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"


# Send SMS Alert
def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for number in RECIPIENTS:
        client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=number)


# Send Email Alert
def send_email(subject, message):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(RECIPIENTS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())


# Forward Alerts via MQTT
def forward_alert():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Use latest API version
        client.connect(BROKER, PORT, keepalive=5)  # Shorter timeout
        client.publish(TOPIC, "EAS Alert Triggered!")
        client.disconnect()
    except Exception as e:
        print(f"MQTT Connection Status: {str(e)}")


# Send Notifications
def send_notifications(message):
    print("Sending SMS alerts...")
    send_sms(message)
    print("Sending email notifications...")
    send_email("Emergency Alert", message)
    print("Alert notifications sent.")


# Main function
if __name__ == "__main__":
    print("Forwarding alert via MQTT...")
    forward_alert()
    print("Sending notifications...")
    send_notifications("An emergency alert has been triggered.")
    print("All notifications sent.")
