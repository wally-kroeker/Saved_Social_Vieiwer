#!/usr/bin/env python3
"""
Process Saved Links - Main Production Script

This script is the main entry point for the production system.
It processes new links from Notion, handles downloads and processing,
and updates the Notion database with the results.
"""
import os
import sys
import argparse
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

import config
from utils.logging_utils import get_logger
from notion_integration import NotionIntegration
from processors.instagram_processor import InstagramProcessor
from output_manager import OutputManager

# Set up logging
logger = get_logger("main")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process saved links from Notion")
    parser.add_argument("--dry-run", action="store_true", help="Run without updating Notion")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of links to process")
    parser.add_argument("--platform", type=str, help="Process only links from specific platform")
    return parser.parse_args()

def process_links():
    """Process links from Notion database"""
    # Load environment variables
    load_dotenv()
    
    logger.info("Processing links")
    
    # Get credentials from environment
    notion_token = os.environ.get('NOTION_API_TOKEN')
    notion_database_id = os.environ.get('NOTION_DATABASE_ID')
    
    if not notion_token or not notion_database_id:
        logger.error("Missing Notion credentials in environment variables")
        raise ValueError("NOTION_API_TOKEN and NOTION_DATABASE_ID must be set")
    
    notion = NotionIntegration(notion_token, notion_database_id)
    
    # Set batch size (can also come from env if needed)
    batch_size = 5  # Process 5 links at a time
    
    # Fetch unprocessed links
    links = notion.get_unprocessed_links(limit=batch_size)
    logger.info(f"Processing {len(links)} links")
    
    # Check what format the links are in
    if links and len(links) > 0:
        sample_item = links[0]
        logger.debug(f"Sample link item format: {type(sample_item)}, content: {sample_item}")
    
    for i, link_item in enumerate(links):
        try:
            # Handle different possible formats from the API
            if isinstance(link_item, tuple) and len(link_item) >= 2:
                item = link_item[0]
                url = link_item[1]
            elif isinstance(link_item, dict) and 'properties' in link_item:
                # Direct Notion API item format
                item = link_item
                # Extract URL from properties - adjust this based on your actual structure
                url = extract_url_from_notion_item(item)
            else:
                logger.error(f"Unrecognized link format: {link_item}")
                continue
            
            if not url:
                logger.error(f"Could not extract URL from item: {item}")
                continue
                
            logger.info(f"Processing URL: {url}")
            
            # Determine processor - fix for potentially missing function
            processor = get_processor_for_url(url)
            if processor:
                logger.info(f"Using {processor.__class__.__name__}")
                
                # Process the link
                result = processor.process(url, item)
                
                if result and result.get('success'):
                    logger.info(f"Successfully processed URL: {url}")
                    logger.info("Output files:")
                    for key, value in result.items():
                        if key != 'success':
                            if isinstance(value, list):
                                for j, item_value in enumerate(value):
                                    logger.info(f"  {key} (list item {j}): {item_value}")
                            else:
                                logger.info(f"  {key}: {value}")
                    
                    # Update Notion
                    item_id = item.get('id')
                    logger.info(f"Updating Notion item status to 'Done': {item_id}")
                    notion.mark_as_processed(item_id)
                    logger.info("Notion item updated successfully")
                else:
                    logger.error(f"Failed to process URL: {url}")
                    if result and result.get('error'):
                        logger.error(f"Error: {result.get('error')}")
            else:
                logger.error(f"No processor found for URL: {url}")
            
            # Only add the 15-minute pause if there are more items to process
            if i < len(links) - 1:  # If this is not the last item
                logger.info("Pausing for 15 minutes before processing next item to avoid rate limiting")
                time.sleep(900)  # 15 minutes = 900 seconds
            
        except Exception as e:
            logger.exception(f"Error processing URL {url if 'url' in locals() else 'unknown'}: {e}")

# Add this helper function to extract URLs from Notion items
def extract_url_from_notion_item(item):
    """Extract URL from a Notion item based on its properties"""
    try:
        # Check different possible property names for the URL
        for prop_name in ['URL', 'url', 'Link', 'link']:
            if prop_name in item.get('properties', {}):
                prop = item['properties'][prop_name]
                
                # Handle different property types
                if prop['type'] == 'url':
                    return prop['url']
                elif prop['type'] == 'rich_text':
                    for text in prop.get('rich_text', []):
                        if text.get('type') == 'text':
                            return text['text']['content']
                        
        logger.warning(f"Could not find URL property in item: {item}")
        return None
    except Exception as e:
        logger.error(f"Error extracting URL from item: {e}")
        return None

# Add this if it's missing
def get_processor_for_url(url):
    """Return the appropriate processor for a given URL"""
    if not url:
        return None
        
    # Check for Instagram URLs
    if 'instagram.com' in url.lower():
        return InstagramProcessor()
    
    # Add other processors for different types of URLs
    # Example:
    # if 'twitter.com' in url.lower() or 'x.com' in url.lower():
    #     return TwitterProcessor()
        
    # No matching processor found
    logger.warning(f"No processor found for URL: {url}")
    return None

def main():
    """Main entry point."""
    try:
        logger.info("Starting Process Saved Links")
        process_links()
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
