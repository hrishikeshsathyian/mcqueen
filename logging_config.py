import logging
import logging.config
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        },
        "filehandler": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": str(LOG_FILE),
        },
    },
    "root": {
        "handlers": ["console", "filehandler"],
        "level": "INFO",
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger("httpx").disabled = True
    logging.getLogger("httpcore").disabled = True
