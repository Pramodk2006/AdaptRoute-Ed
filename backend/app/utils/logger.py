"""
Structured logging configuration using loguru.
Provides both human-readable (dev) and JSON (production) output.
"""
import sys
from app.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure loguru logger based on environment settings."""
    from loguru import logger

    logger.remove()  # Remove default handler

    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{name}:{function}:{line} — {message}"
    )

    if settings.LOG_FORMAT == "json":
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            serialize=True,       # JSON output
            backtrace=False,
            diagnose=False,
        )
    else:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format=log_format,
            colorize=True,
            backtrace=True,
            diagnose=settings.DEBUG,
        )

    logger.info(
        f"Logging configured | level={settings.LOG_LEVEL} "
        f"format={settings.LOG_FORMAT} env={settings.ENVIRONMENT}"
    )


# Convenience re-export so consumers can: from app.utils.logger import logger
from loguru import logger  # noqa: E402

__all__ = ["logger", "setup_logging"]
