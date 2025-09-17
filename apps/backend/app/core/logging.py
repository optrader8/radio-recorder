import logging
import sys
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for development"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        if settings.ENVIRONMENT == "development":
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging():
    """Set up logging configuration"""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log"),
        ]
    )

    # Set colored formatter for console in development
    if settings.ENVIRONMENT == "development":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Replace the default console handler
        root_logger = logging.getLogger()
        root_logger.handlers = [
            handler for handler in root_logger.handlers
            if not isinstance(handler, logging.StreamHandler)
        ]
        root_logger.addHandler(console_handler)
        root_logger.addHandler(logging.FileHandler(log_dir / "app.log"))

    # Configure specific loggers
    configure_loggers()


def configure_loggers():
    """Configure specific loggers"""

    # SQLAlchemy logger
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )

    # Celery logger
    logging.getLogger("celery").setLevel(logging.INFO)

    # HTTP client logger
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # FFmpeg logger
    logging.getLogger("ffmpeg").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)