import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

def setup_logging():
    """
    Sets up logging configuration for the application.
    """
    # Configure logging
    log_filename = f"logs/historic_weather.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)  # Also log to console
        ]
    )

    # Create logger for this module to avoid duplicate logging
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully.")
    logger.info(f"Log file created at: {log_filename}")