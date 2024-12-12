def format_message(message):
    """
    Format EAS message for distribution
    Args:
        message (str): Raw EAS message
    Returns:
        str: Formatted alert message ready for distribution
    """
    # Basic EAS message formatting
    formatted = f"EMERGENCY ALERT SYSTEM\n{'-'*30}\n"
    formatted += f"ALERT TYPE: {message.split('-')[0]}\n"
    formatted += f"MESSAGE: {message}\n"
    formatted += f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return formatted
