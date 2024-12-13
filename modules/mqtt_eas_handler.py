import logging
from dsame3 import DSAMEDecoder
import json
import os

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/mqtt_handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MQTTHandler")

# Function to save decoded messages securely
def save_decoded_message(decoded_message):
    try:
        if not os.path.exists("decoded_messages"):
            os.makedirs("decoded_messages")
        
        file_path = os.path.join("decoded_messages", "decoded_message.json")
        with open(file_path, "w") as file:
            json.dump(decoded_message, file, indent=4)

        logger.info(f"Decoded message saved successfully to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save decoded message: {str(e)}")
        raise RuntimeError("Could not save decoded message")

# Extended MQTT message handler
def handle_mqtt_message(payload):
    """
    Handles incoming MQTT messages, decodes EAS alerts, and logs results.
    Ensures secure processing and saves decoded data to a file.
    """
    logger.info("Received MQTT message. Processing payload...")
    
    # Ensure payload is not empty
    if not payload:
        logger.warning("Empty MQTT payload received. Ignoring message.")
        return {"error": "Empty payload received"}, 400

    try:
        # Initialize EAS decoder
        decoder = DSAMEDecoder()
        logger.info("Initialized DSAME decoder.")

        # Decode the payload
        decoded_message = decoder.decode(payload)
        logger.info(f"Decoded EAS Message: {decoded_message}")

        # Save the decoded message securely
        save_path = save_decoded_message(decoded_message)

        return {
            "status": "success",
            "decoded_message": decoded_message,
            "file_path": save_path
        }
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decoding error: {str(json_err)}")
        return {"error": "Invalid JSON in payload"}, 400
    except FileNotFoundError as fnf_err:
        logger.error(f"File handling error: {str(fnf_err)}")
        return {"error": "File handling issue occurred"}, 500
    except Exception as e:
        logger.error(f"Failed to decode MQTT message: {str(e)}")
        return {"error": "An error occurred while processing the message"}, 500

# Example usage (assuming this is part of a larger MQTT handler system)
if __name__ == "__main__":
    # Simulating an incoming MQTT payload
    sample_payload = b"Example raw EAS data"
    
    result = handle_mqtt_message(sample_payload)
    print("Handler Result:", result)
