import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from twilio.rest import Client

load_dotenv()

# MQTT Configuration
BROKER = "192.168.1.50"  # Replace with your MQTT broker's IP
PORT = 1883
TOPIC = "eas/alert"

# Twilio Configuration (SMS, Voice Alerts)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
RECIPIENTS = os.getenv('ALERT_RECIPIENTS').split(',')

# Email Configuration
SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

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
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish(TOPIC, "EAS Alert Triggered!")
    client.disconnect()

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
