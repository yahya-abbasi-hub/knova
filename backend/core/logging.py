import logging
import sys

from backend.core.config import settings


def setup_logging() -> None:
    """
    Configure logging for the entire application.
    Call this once, when the app starts up.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Quiet down noisy third-party libraries so our own logs aren't drowned out
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific file/module.
    Usage: logger = get_logger(__name__)
    """
    return logging.getLogger(name)