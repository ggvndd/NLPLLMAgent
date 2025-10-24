"""
Logging utilities for the Career Coach Agent.

Provides centralized logging configuration and utilities for different components.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str, 
    log_level: str = "INFO", 
    log_dir: str = "logs", 
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler with rotation
    log_file = os.path.join(log_dir, f"{name.split('.')[-1]}.log")
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def setup_error_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Set up a dedicated error logger for critical issues.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Error logger instance
    """
    error_logger = logging.getLogger("errors")
    
    # Clear existing handlers
    error_logger.handlers.clear()
    
    # Set to ERROR level only
    error_logger.setLevel(logging.ERROR)
    
    # Create error formatter with more detail
    error_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create error file handler
    error_file = os.path.join(log_dir, "errors.log")
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(error_formatter)
    
    # Add handler to logger
    error_logger.addHandler(error_handler)
    
    # Don't propagate to avoid duplicate logs
    error_logger.propagate = False
    
    return error_logger


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            # Log function entry
            logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log successful completion
                logger.debug(f"{func.__name__} completed in {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                # Log error
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_async_function_call(logger: logging.Logger):
    """
    Decorator to log async function calls with parameters and execution time.
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function for async functions
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            # Log function entry
            logger.debug(f"Calling async {func.__name__} with args: {args}, kwargs: {kwargs}")
            
            try:
                # Execute async function
                result = await func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log successful completion
                logger.debug(f"Async {func.__name__} completed in {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                # Log error
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"Async {func.__name__} failed after {execution_time:.3f}s: {str(e)}")
                raise
                
        return wrapper
    return decorator


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.
    
    Usage:
        class MyClass(LoggerMixin):
            def __init__(self):
                self.setup_logging()
    """
    
    def setup_logging(self, log_level: str = "INFO", log_dir: str = "logs"):
        """
        Set up logging for the class.
        
        Args:
            log_level: Logging level
            log_dir: Directory for log files
        """
        class_name = self.__class__.__name__.lower()
        self.logger = setup_logger(class_name, log_level, log_dir)
    
    def log_info(self, message: str):
        """Log info message."""
        if hasattr(self, 'logger'):
            self.logger.info(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error message."""
        if hasattr(self, 'logger'):
            self.logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message: str):
        """Log warning message."""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
    
    def log_debug(self, message: str):
        """Log debug message."""
        if hasattr(self, 'logger'):
            self.logger.debug(message)


# Create a global error logger for critical system errors
error_logger = setup_error_logger()


def log_critical_error(message: str, exception: Optional[Exception] = None):
    """
    Log critical errors that should always be recorded.
    
    Args:
        message: Error message
        exception: Optional exception instance
    """
    if exception:
        error_logger.critical(f"{message}: {str(exception)}", exc_info=True)
    else:
        error_logger.critical(message)