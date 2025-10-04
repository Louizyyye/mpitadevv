# app/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name="app_logger", log_file="app.log", level=logging.INFO):
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_file)

    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
