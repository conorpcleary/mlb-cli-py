"""
Logging configuration for the MLB CLI application.
Provides a standard logger that writes to a local log file.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# Ensure log directory exists
LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(LOG_DIR, "mlb_cli.log")

def get_logger(name):
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Rotating file handler (5MB per file, keeps 2 backups)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
