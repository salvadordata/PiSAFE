from datetime import datetime

def format_message(message):
    """
    Format EAS message for distribution.
    
    Args:
        message (str): Raw EAS message.
    
    Returns:
        str: Formatted alert message ready for distribution.
    """
    formatted = f"EMERGENCY ALERT SYSTEM\n{'-' * 30}\n"
    formatted += f"ALERT TYPE: {message.split('-')[0]}\n"
    formatted += f"MESSAGE: {message}\n"
    formatted += f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return formatted

# Remove or comment out test calls in the module itself
# print(format_message("FLOOD-Heavy rain expected in your area. Evacuate immediately."))

