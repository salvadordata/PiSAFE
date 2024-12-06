import os
from gpiozero import LED
import time
from OpenENDEC import eas_encoder  # Integration with OpenENDEC

# Configure GPIO
relay = LED(17)

# Generate the EAS Alert using OpenENDEC
def create_eas_alert(output_file="eas_alert.wav"):
    eas_encoder.generate_alert(output_file)

# Trigger GPIO relay for external alarms
def trigger_relay():
    relay.on()
    time.sleep(5)  # Relay active for 5 seconds
    relay.off()

# Play the generated alert audio
def play_alert(audio_file="eas_alert.wav"):
    os.system(f"ffplay -nodisp -autoexit {audio_file}")

# Main function
if __name__ == "__main__":
    print("Generating EAS Alert...")
    create_eas_alert()
    print("Triggering external alarm...")
    trigger_relay()
    print("Playing alert audio...")
    play_alert()
    print("Alert process complete.")
