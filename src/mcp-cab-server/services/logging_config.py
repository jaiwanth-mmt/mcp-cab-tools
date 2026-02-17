"""
Centralized logging configuration for MCP Cab Booking System.

This module provides a consistent logging setup across all services with:
- Structured log formatting
- Context-aware logging
- Performance tracking
- Easy debugging capabilities
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    # Emoji indicators for better visual scanning
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        """Format the log record with colors and structure."""
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.RESET)
        icon = self.ICONS.get(record.levelname, '  ')
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Module and function info
        module_info = f"{record.module}.{record.funcName}"
        
        # Build the formatted message
        formatted = (
            f"{color}{icon} {timestamp}{self.RESET} "
            f"{color}[{record.levelname:8}]{self.RESET} "
            f"[{module_info:30}] "
            f"{record.getMessage()}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class StructuredLogger(logging.LoggerAdapter):
    """
    Logger adapter that adds context to log messages.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": "123", "ip": "1.2.3.4"})
    """
    
    def process(self, msg, kwargs):
        """Add context information to the log message."""
        extra = kwargs.get('extra', {})
        if extra:
            # Format extra data in a readable way
            context_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            msg = f"{msg} [{context_str}]"
        return msg, kwargs


def setup_logging(level: str = "INFO", use_colors: bool = True, use_stderr: bool = True) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output (disable for file logging)
        use_stderr: Whether to log to stderr (True) or stdout (False).
                   When running as MCP server, must use stderr to avoid polluting JSON-RPC on stdout.
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create handler - use stderr for MCP servers to keep stdout clean for JSON-RPC
    stream = sys.stderr if use_stderr else sys.stdout
    handler = logging.StreamHandler(stream)
    handler.setLevel(numeric_level)
    
    # Set formatter
    if use_colors:
        formatter = ColoredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)-8s] [%(name)s.%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)


def get_logger(name: str, **context) -> StructuredLogger:
    """
    Get a logger instance with optional context.
    
    Args:
        name: Logger name (typically __name__)
        **context: Optional context to add to all log messages
        
    Returns:
        StructuredLogger instance
        
    Example:
        logger = get_logger(__name__, service="payment", version="1.0")
        logger.info("Processing payment")
    """
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger, context)


def log_function_call(func):
    """
    Decorator to automatically log function entry/exit with parameters and timing.
    
    Example:
        @log_function_call
        def process_payment(amount: float):
            ...
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log entry
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"→ Entering {func.__name__}({signature})")
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            logger.debug(f"← Exiting {func.__name__} (took {elapsed:.2f}ms)")
            return result
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(
                f"✗ Exception in {func.__name__} after {elapsed:.2f}ms: {type(e).__name__}: {e}"
            )
            raise
    
    return wrapper


def log_async_function_call(func):
    """
    Decorator for async functions to log entry/exit with timing.
    
    Example:
        @log_async_function_call
        async def fetch_data():
            ...
    """
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log entry
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"→ Entering {func.__name__}({signature})")
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"← Exiting {func.__name__} (took {elapsed:.2f}ms)")
            return result
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(
                f"✗ Exception in {func.__name__} after {elapsed:.2f}ms: {type(e).__name__}: {e}"
            )
            raise
    
    return wrapper


# Initialize logging on module import
# For MCP servers: logs go to stderr to keep stdout clean for JSON-RPC
# To disable logging entirely, set LOG_LEVEL=CRITICAL in environment
setup_logging(use_stderr=True)
