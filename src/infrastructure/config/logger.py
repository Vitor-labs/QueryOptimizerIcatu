"""Structured logging configuration for the application.

This module provides centralized logging configuration using structlog
for structured, contextual logging throughout the application.
"""

import logging
import sys
from typing import Any

import structlog


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "console",
    include_timestamp: bool = True,
) -> None:
    """Configure structured logging for the application.

    Sets up structlog with appropriate processors and formatters for
    development or production use.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ("console" or "json")
        include_timestamp: Whether to include timestamps in log output

    Examples:
        >>> configure_logging("DEBUG", "console")
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Build processor chain
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]

    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))

    # Add renderer based on format
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of calling module)

    Returns:
        Configured structlog logger instance

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing query", query_id="abc123", database="oracle")
        >>> logger.error("Optimization failed", error=str(e), query_hash="def456")
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: str | int | float | bool) -> None:
    """Bind context variables to all subsequent log messages.

    Context variables are included in all log messages until cleared.
    Useful for request IDs, user IDs, etc.

    Args:
        **kwargs: Key-value pairs to bind to logging context

    Examples:
        >>> bind_context(request_id="req-123", user_id="user-456")
        >>> logger = get_logger(__name__)
        >>> logger.info("Action performed")  # Will include request_id and user_id
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables.

    Examples:
        >>> clear_context()
    """
    structlog.contextvars.clear_contextvars()


# Configure logging on module import with sensible defaults
configure_logging()
