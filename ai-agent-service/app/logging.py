import logging
import sys
from typing import Any

import structlog
from app.config import get_settings


def configure_logging() -> None:
    """
    Configures structlog to output structured JSON in production and
    colorful console logs in development. Replaces the default Python log handlers.
    """
    settings = get_settings()

    # Set the root logger level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)

    # Common processors for both dev and prod
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    is_development = settings.environment.lower() == "development"

    if is_development:
        # Development: Human-readable colorful logs
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=True)]
    else:
        # Production: JSON structured logging
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    """
    Returns a structlog logger instance.
    """
    return structlog.get_logger(name)
