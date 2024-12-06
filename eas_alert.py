from OpenENDEC.eas_encoder import EASEncoder
from gpiozero import LED
import os
import time

# GPIO Configuration
relay = LED(17)  # GPIO pin for relay


# Generate EAS Alert
def create_eas_alert(output_file="eas_alert.wav"):
    """
    Generates an EAS-compliant alert using OpenENDEC.
    Saves the generated alert to the specified output file.
    """
    print("[INFO] Generating EAS Alert...")
    try:
        # Use OpenENDEC to generate the alert
        EASEncoder.generate_alert(output_file)
        print(f"[SUCCESS] EAS Alert saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to generate EAS alert: {e}")


# Trigger GPIO Relay
def trigger_relay():
    """
    Activates the GPIO relay to trigger external alarms.
    The relay stays active for 5 seconds.
    """
    print("[INFO] Activating relay for external alarm...")
    try:
        relay.on()
        time.sleep(5)
        relay.off()
        print("[SUCCESS] Relay deactivated.")
    except Exception as e:
        print(f"[ERROR] Failed to activate relay: {e}")


# Play Alert Audio
def play_alert(audio_file="eas_alert.wav"):
    """
    Plays the generated alert audio file.
    """
    print(f"[INFO] Playing alert audio: {audio_file}")
    if not os.path.exists(audio_file):
        print(f"[ERROR] Audio file {audio_file} not found.")
        return
    try:
        os.system(f"ffplay -nodisp -autoexit {audio_file}")
        print("[SUCCESS] Audio playback complete.")
    except Exception as e:
        print(f"[ERROR] Failed to play alert audio: {e}")


# Main Execution
if __name__ == "__main__":
    print("[START] Starting EAS Alert Process...")
    create_eas_alert()
    trigger_relay()
    play_alert()
    print("[COMPLETE] EAS Alert Process Finished.")
