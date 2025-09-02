import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configures the root logger for the application.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"historic_weather_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also log to console for immediate feedback
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully.")
    logger.info(f"Log file created at: {log_filename}")
