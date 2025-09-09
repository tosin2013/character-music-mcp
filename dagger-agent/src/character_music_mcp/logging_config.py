"""Logging configuration for the Dagger Test Repair Agent"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging for the application"""

    # Set the logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Configure processors based on format
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes"""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get a logger instance for this class"""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> dict[str, Any]:
    """Create a log context for function calls"""
    return {
        "function": func_name,
        "parameters": {k: v for k, v in kwargs.items() if not k.startswith("_")}
    }


def log_dagger_operation(operation: str, container_image: str, **kwargs: Any) -> dict[str, Any]:
    """Create a log context for Dagger operations"""
    return {
        "dagger_operation": operation,
        "container_image": container_image,
        **kwargs
    }


def log_github_event(event_type: str, repository: str, **kwargs: Any) -> dict[str, Any]:
    """Create a log context for GitHub events"""
    return {
        "github_event": event_type,
        "repository": repository,
        **kwargs
    }


def log_api_call(service: str, endpoint: str, status_code: int = None, **kwargs: Any) -> dict[str, Any]:
    """Create a log context for API calls"""
    context = {
        "api_service": service,
        "endpoint": endpoint,
        **kwargs
    }
    if status_code is not None:
        context["status_code"] = status_code
    return context
