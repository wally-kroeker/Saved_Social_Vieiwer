"""
Logging utilities for the Process Saved Links application.

This module provides functions for setting up and configuring logging
throughout the application.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

import config

def setup_logger(name, log_file=None, level=None):
    """
    Set up a logger with the specified name and configuration.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to the log file. If None, a default path will be used.
        level (str, optional): Logging level. If None, the default from config will be used.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if level is None:
        level = config.LOG_LEVEL
    
    if log_file is None:
        # Create a log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(config.LOG_DIR, f"{name}_{timestamp}.log")
    
    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """
    Get or create a logger with the specified name.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Otherwise, set up the logger
    return setup_logger(name)
