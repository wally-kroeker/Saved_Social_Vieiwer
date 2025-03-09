#!/usr/bin/env python3
"""
Main script for the Process Saved Links application.

This script processes links from various platforms in parallel,
respecting platform-specific settings such as batch sizes and rate limiting.
"""
import os
import sys
import time
import signal
import argparse
import threading
from typing import Dict, Any, List

from dotenv import load_dotenv
import platform_config
from processor_factory import ProcessorFactory
from platform_processor import PlatformProcessor
from utils.logging_utils import get_logger

logger = get_logger("process_links")

# Flag to indicate when the script should exit
should_exit = False

def signal_handler(sig, frame):
    """Handle signals to gracefully exit the script."""
    global should_exit
    logger.info("Received signal to exit, stopping processors...")
    should_exit = True

def process_platform(platform_type: str, args: argparse.Namespace):
    """
    Process links for a specific platform.
    
    Args:
        platform_type: Type of platform to process
        args: Command-line arguments
    """
    try:
        processor = PlatformProcessor(platform_type)
        
        if args.continuous:
            logger.info(f"Starting continuous processing for {platform_type}")
            while not should_exit:
                try:
                    processed = processor.process_batch(
                        limit=args.limit, 
                        continuous=False  # We handle continuity here
                    )
                    
                    if processed == 0 and not should_exit:
                        wait_time = processor.delay_seconds if processor.delay_seconds > 0 else 60
                        logger.info(f"No {platform_type} items processed, waiting {wait_time} seconds...")
                        
                        # Wait in small increments to check should_exit flag
                        for _ in range(wait_time):
                            if should_exit:
                                break
                            time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in {platform_type} processor: {e}")
                    # Wait before retrying
                    time.sleep(10)
        else:
            processor.process_batch(limit=args.limit, continuous=False)
            
    except Exception as e:
        logger.error(f"Fatal error in {platform_type} processor thread: {e}")

def main():
    """Main entry point."""
    global should_exit
    
    # Setup signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process links from various platforms")
    parser.add_argument("--platform", type=str, choices=ProcessorFactory.get_supported_platforms() + ["all"],
                        default="all", help="Platform to process (default: all)")
    parser.add_argument("--limit", type=int, help="Maximum number of links to process per platform")
    parser.add_argument("--continuous", action="store_true", help="Run continuously until stopped")
    parser.add_argument("--parallel", action="store_true", help="Process platforms in parallel")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["NOTION_API_TOKEN", "NOTION_DATABASE_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Determine which platforms to process
    platforms_to_process = ProcessorFactory.get_supported_platforms() if args.platform == "all" else [args.platform]
    
    if args.parallel:
        # Process platforms in parallel
        logger.info(f"Processing platforms in parallel: {', '.join(platforms_to_process)}")
        threads = []
        
        for platform in platforms_to_process:
            thread = threading.Thread(
                target=process_platform,
                args=(platform, args),
                name=f"{platform}_processor"
            )
            threads.append(thread)
            thread.start()
            logger.info(f"Started {platform} processor thread")
        
        # Wait for all threads to complete or for signal to exit
        try:
            while any(thread.is_alive() for thread in threads) and not should_exit:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping processors...")
            should_exit = True
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
            
    else:
        # Process platforms sequentially
        logger.info(f"Processing platforms sequentially: {', '.join(platforms_to_process)}")
        for platform in platforms_to_process:
            if should_exit:
                break
            logger.info(f"Processing {platform} platform")
            process_platform(platform, args)

if __name__ == "__main__":
    main() 