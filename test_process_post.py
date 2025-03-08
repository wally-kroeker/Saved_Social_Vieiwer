#!/usr/bin/env python3
"""
Test processing a specific Instagram post through the main processing flow.
"""
import os
import sys
from dotenv import load_dotenv

import config
from utils.logging_utils import get_logger
from notion_integration import NotionIntegration
from processors.instagram_processor import InstagramProcessor
from output_manager import OutputManager

# Set up logging
logger = get_logger("test_process")

def test_process_post():
    """Test process for a specific Instagram post"""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting test process")
    
    # URL of a regular Instagram post from our list
    url = "https://www.instagram.com/reel/DG0xVf3OI0y/?igsh=MW94Z3Z6OWgxdGoycA=="
    
    # Create an Instagram processor
    processor = InstagramProcessor()
    
    # Check if the processor can handle this URL
    if processor.can_process(url):
        logger.info(f"Processing Instagram URL: {url}")
        
        # Process the URL with dry run mode
        result = processor.process(url, None)
        
        if result:
            logger.info("Processing successful!")
            for key, value in result.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.error("Processing failed")
    else:
        logger.error(f"Cannot process URL: {url}")

if __name__ == "__main__":
    test_process_post() 