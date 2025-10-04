"""
Logger setup for Mpita Medical project
"""

import logging
import sys

def setup_logger(name="mpita_logger", level=logging.INFO):
    """
    Returns a configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(ch)

    return logger
