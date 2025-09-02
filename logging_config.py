"""
Logging configuration for the Deep Research Agent.

This module provides centralized logging configuration that can be imported
and used across the application for consistent logging setup.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_dir: Directory to store log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_dir}/deep_research_{timestamp}.log"
    
    # Configure logging
    handlers = []
    
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
    
    if log_to_file:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Set specific loggers
    main_logger = logging.getLogger("deep_research")
    main_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Reduce noise from external libraries
    logging.getLogger("ddgs").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    if log_to_file:
        main_logger.info(f"Logging initialized. Log file: {log_filename}")
    
    return main_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"deep_research.{name}")


# Example usage:
if __name__ == "__main__":
    # Set up logging
    logger = setup_logging(log_level="DEBUG")
    
    # Test logging
    logger.info("Logging system initialized successfully")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
