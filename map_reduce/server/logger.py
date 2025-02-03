"""
Structured logging configuration for all server components.
Provides both console and file logging with rotation.
"""
import logging
import logging.handlers
import os
import sys
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

from map_reduce.server.configs import LOGGING, ConfigError

# Default log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

def setup_logging(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False,
) -> structlog.BoundLogger:
    """
    Setup structured logging with both console and file handlers.
    
    Args:
        name: Logger name
        log_level: Minimum log level
        log_file: Optional log file path
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        json_format: Whether to use JSON formatting
    
    Returns:
        A configured structured logger
    """
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    else:
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"{name}.log")

    # Setup standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure processors
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.exception_formatter,
            )
        )

    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if json_format:
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        if json_format:
            file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Get logger
    logger = structlog.get_logger(name)

    # Add handlers to root logger
    root_logger = logging.getLogger()
    for handler in handlers:
        root_logger.addHandler(handler)

    return logger

def get_logger(
    name: str,
    adapter: Dict[str, Any] = None,
    extras: bool = False,
    **kwargs
) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        adapter: Optional dict of context variables
        extras: Whether to include extra fields in log messages
        **kwargs: Additional configuration options
    
    Returns:
        A configured structured logger
    
    Raises:
        ConfigError: If logger configuration is invalid
    """
    try:
        configs = LOGGING.get(name, {})
        log_level = configs.get("level", "INFO")
        log_file = configs.get("log_file")
        json_format = configs.get("json_format", False)
        
        logger = setup_logging(
            name=name,
            log_level=log_level,
            log_file=log_file,
            json_format=json_format,
            **kwargs
        )
        
        # Bind context variables
        if adapter:
            logger = logger.bind(**adapter)
            
        return logger
    except Exception as e:
        raise ConfigError(f"Failed to configure logger: {str(e)}")
