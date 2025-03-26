#!/usr/bin/env python3
"""
Run the main script focused on Instagram posts.
This script runs the main processor with a specific focus on Instagram posts.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

import config
from utils.logging_utils import get_logger
from notion_integration import NotionIntegration
from processors.instagram_processor import InstagramProcessor
from output_manager import OutputManager

# Set up logging
logger = get_logger("run_instagram")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process Instagram links from Notion")
    parser.add_argument("--dry-run", action="store_true", help="Run without updating Notion")
    parser.add_argument("--limit", type=int, default=1, help="Maximum number of links to process")
    parser.add_argument("--url", type=str, help="Process a specific URL instead of fetching from Notion")
    return parser.parse_args()

def process_instagram_links():
    """Process Instagram links from Notion database"""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    logger.info("Starting Instagram processor")
    
    if args.url:
        # Process a specific URL
        url = args.url
        logger.info(f"Processing specific URL: {url}")
        
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
    else:
        # Process from Notion
        
        # Get credentials from environment
        notion_token = os.environ.get('NOTION_API_TOKEN')
        notion_database_id = os.environ.get('NOTION_DATABASE_ID')
        
        if not notion_token or not notion_database_id:
            logger.error("Missing Notion credentials in environment variables")
            raise ValueError("NOTION_API_TOKEN and NOTION_DATABASE_ID must be set")
        
        notion = NotionIntegration(notion_token, notion_database_id)
        
        # Get unprocessed links from Notion
        links = notion.get_unprocessed_links(limit=args.limit)
        logger.info(f"Found {len(links)} unprocessed links")
        
        if not links:
            logger.info("No links to process")
            return
        
        # Process each link
        for link in links:
            url = link.get("url")
            notion_item = link
            
            if not url:
                logger.warning("Link has no URL, skipping")
                continue
            
            logger.info(f"Processing URL: {url}")
            
            # Create processor
            processor = InstagramProcessor()
            
            # Process the link if it's an Instagram link
            if processor.can_process(url):
                logger.info("Using InstagramProcessor")
                try:
                    result = processor.process(url, notion_item)
                    
                    if result:
                        # If not a dry run, update Notion
                        if not args.dry_run:
                            notion.mark_as_processed(
                                notion_item.get("id"),
                                result
                            )
                    else:
                        logger.error(f"Failed to process URL: {url}")
                except Exception as e:
                    logger.error(f"Error processing URL: {url} - {e}")
                    if not args.dry_run:
                        notion.mark_as_failed(notion_item.get("id"), str(e))
            else:
                logger.info(f"Skipping non-Instagram URL: {url}")

if __name__ == "__main__":
    process_instagram_links() 