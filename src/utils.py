import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def log_message(message, level="info"):
    """
    Log a message with the specified level.
    
    Args:
        message (str): The message to log.
        level (str): The logging level ('info', 'error', etc.).
    """
    if level == "error":
        logging.error(message)
    else:
        logging.info(message)