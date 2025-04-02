#!/usr/bin/env python3
"""
Script to process YouTube links from the Notion database.

This script fetches unprocessed YouTube links from the Notion database,
downloads the videos, generates transcripts, and updates the database
with the processing status.
"""
import os
import sys
import argparse
import traceback
from typing import Optional, Dict, Any

from processors.youtube_processor import YouTubeProcessor
from notion_integration import get_unprocessed_links, mark_as_processed, mark_as_failed
from utils.logging_utils import get_logger

logger = get_logger("run_youtube")

def process_youtube_links(limit: Optional[int] = None) -> bool:
    """
    Process unprocessed YouTube links from the Notion database.
    
    Args:
        limit (int, optional): Maximum number of links to process
        
    Returns:
        bool: True if at least one link was processed, False otherwise
    """
    logger.info("Starting YouTube processor")
    
    # Initialize processor
    processor = YouTubeProcessor()
    
    # Get unprocessed links
    items = get_unprocessed_links(limit=limit or 1)
    logger.info(f"Found {len(items)} unprocessed links")
    
    if not items:
        logger.info("No unprocessed links found")
        return False
        
    processed_count = 0
    
    for item in items:
        logger.info(f"Processing item: {item}")
        
        url = item.get("url")
        if not url:
            logger.warning(f"Skipping item {item.get('id')} with no URL")
            continue
            
        logger.info(f"Checking URL: {url}")
        if not processor.can_process(url):
            logger.info(f"Skipping non-YouTube URL: {url}")
            continue
            
        logger.info(f"Processing YouTube URL: {url}")
        try:
            # Process the video
            result = processor.process(url, item)
            
            # Prepare metadata for Notion update
            notion_metadata = {
                "filename": result["metadata"]["title"],
                "video_id": result["video_id"],
                "output_paths": {
                    "video": result["output_paths"]["video"],
                    "thumbnail": result["output_paths"]["thumbnail"],
                    "transcript": result["output_paths"]["transcript"],
                    "metadata": result["output_paths"]["metadata"]
                },
                "uploader": result["metadata"]["uploader"],
                "processed_date": result["metadata"]["processed_date"]
            }
            
            # Mark as processed in Notion
            logger.info(f"Marking item {item['id']} as processed in Notion with metadata: {notion_metadata}")
            success = mark_as_processed(item["id"], notion_metadata)
            
            if success:
                logger.info(f"Successfully marked item {item['id']} as processed in Notion")
            else:
                logger.error(f"Failed to mark item {item['id']} as processed in Notion")
            
            processed_count += 1
            
        except Exception as e:
            error_msg = f"Error processing {url}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            mark_as_failed(item["id"], error_msg)
    
    return processed_count > 0

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Process YouTube links from Notion database")
    parser.add_argument("--limit", type=int, default=1,
                      help="Maximum number of links to process (default: 1)")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode with additional logging")
    args = parser.parse_args()
    
    if args.debug:
        # Set debug logging
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)
    
    try:
        success = process_youtube_links(args.limit)
        if success:
            logger.info("Successfully processed at least one YouTube link")
            sys.exit(0)
        else:
            logger.info("No YouTube links were processed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main() 