#created: 2025/10/05 21:37:44
#last-modified: 2025/10/05 23:25:16
#by kaldor31

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from dotenv import load_dotenv


load_dotenv()
CHANNEL_ID = os.getenv("CHANNEL_ID")

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "bot.log")
MAX_LOG_SIZE = 100 * 1024 * 1024  # 100 MB
BACKUP_COUNT = 5  # store 5 old logs


def setup_logger(name: str = "telegram_bot") -> logging.Logger:
    """
    reates and configures a logger with file rotation.
    Returns a pre-built logger object
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Log format: [YYYY-MM-DD hh:mm:ss] [INFO] message
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Also log to console (optional)
    """
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    """

    logger.info("Logger initialized successfully.")
    return logger


def log_request(logger: logging.Logger, user_id: int, raw_text: str, text: str):
    """Logs the user's incoming message"""
    logger.info(f"User {user_id}: {raw_text} -> {text}")


def log_response(logger: logging.Logger, user_id: int, response: str):
    """Logs the response sent to the user"""
    logger.info(f"Bot -> User {user_id}: {response}")

    # The length can be limited to avoid cluttering the file.
    """
    logger.info(f"Bot -> User {user_id}: {response[:200]}"
    """


def log_error(logger: logging.Logger, error: Exception):
    """Logs errors"""
    logger.error(f"Error occurred: {repr(error)}")


def get_latest_log_file() -> str:
    """Returns the path to the latest log file (for sending to the channel which is not realized yet)"""
    files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if not files:
        return ""
    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(LOG_DIR, f)), reverse=True)
    return os.path.join(LOG_DIR, files[0])