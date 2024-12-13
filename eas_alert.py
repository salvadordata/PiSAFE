import os
import time
import logging
import subprocess
import platform
import re
from easencode.easencode import EASEncoder

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Fake GPIO setup for non-Raspberry Pi environments
if platform.system() != "Linux":
    import fake_rpi
    import sys

    sys.modules["RPi"] = fake_rpi.RPi
    sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO

from gpiozero import LED

# GPIO Configuration
relay = LED(17)  # GPIO pin for relay


# Generate EAS Alert
def create_eas_alert(output_file="eas_alert.wav"):
    """
    Generates an EAS-compliant alert using OpenENDEC.
    Saves the generated alert to the specified output file.
    """
    logging.info("Generating EAS Alert...")
    try:
        EASEncoder.generate_alert(output_file)
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Generated file {output_file} does not exist.")
        logging.info(f"EAS Alert saved to {output_file}")
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Failed to generate EAS alert: {e}")


# Trigger GPIO Relay
def trigger_relay(duration=5):
    """
    Activates the GPIO relay to trigger external alarms.
    The relay stays active for the specified duration.
    """
    logging.info("Activating relay for external alarm...")
    try:
        relay.on()
        time.sleep(duration)
        relay.off()
        logging.info("Relay deactivated.")
    except Exception as e:
        logging.error(f"Failed to activate relay: {e}")


# Validate Safe File Paths
def is_safe_path(file_path):
    """
    Validates the provided file path to prevent directory traversal attacks.
    """
    return bool(re.match(r"^[\w,\s-]+\.[A-Za-z]{3}$", os.path.basename(file_path)))


# Play Alert Audio
def play_alert(audio_file="eas_alert.wav"):
    """
    Plays the generated alert audio file.
    """
    if not is_safe_path(audio_file):
        logging.error(f"Unsafe file path: {audio_file}")
        return
    logging.info(f"Playing alert audio: {audio_file}")
    if not os.path.exists(audio_file):
        logging.error(f"Audio file {audio_file} not found.")
        return
    try:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", audio_file], check=True)
        logging.info("Audio playback complete.")
    except FileNotFoundError:
        logging.error("FFmpeg is not installed. Install it to enable audio playback.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Audio playback failed: {e}")
    except Exception as e:
        logging.error(f"Failed to play alert audio: {e}")


# Main Execution
if __name__ == "__main__":
    logging.info("Starting EAS Alert Process...")
    try:
        create_eas_alert()
        trigger_relay()
        play_alert()
        logging.info("EAS Alert Process Finished.")
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
