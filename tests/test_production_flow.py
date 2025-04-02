"""
Test script for the production flow with Instagram links from Notion.

This script tests the full production flow by:
1. Fetching unprocessed Instagram links from Notion
2. Processing them with the Instagram processor
3. Marking them as processed in Notion if successful
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the modules
import config
from notion_integration import NotionIntegration
from processors.instagram_processor import InstagramProcessor
from utils.logging_utils import get_logger

logger = get_logger("test_production_flow")

def test_instagram_production_flow(url=None, use_notion=True, dry_run=False):
    """
    Test the production flow for Instagram links.
    
    Args:
        url (str, optional): Specific Instagram URL to test. If None, one will be fetched from Notion.
        use_notion (bool): Whether to fetch URLs from Notion. Default is True.
        dry_run (bool): If True, don't mark as processed in Notion. Default is False.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        notion_items = []
        notion = None
        
        # Initialize Notion integration if needed
        if use_notion:
            logger.info("Initializing Notion integration")
            notion = NotionIntegration()
        
        # Fetch URL from Notion if not provided
        if url is None and use_notion:
            logger.info("Fetching unprocessed links from Notion")
            notion_items = notion.get_unprocessed_links(limit=1)
            
            if not notion_items:
                logger.info("No unprocessed Instagram links found in Notion")
                return True  # Not a failure, just nothing to process
            
            # Get the first Instagram link
            for item in notion_items:
                url = item.get("url", "")
                if url and "instagram.com" in url:
                    logger.info(f"Found Instagram link: {url}")
                    break
            else:
                logger.info("No Instagram links found in the unprocessed items")
                return True  # Not a failure, just no Instagram links
        
        if not url:
            logger.error("No URL provided and could not fetch one from Notion")
            return False
        
        # Initialize the Instagram processor
        logger.info("Initializing Instagram processor")
        processor = InstagramProcessor()
        
        # Check if the processor can handle the URL
        if not processor.can_process(url):
            logger.error(f"The URL is not recognized as an Instagram URL: {url}")
            return False
        
        # Process the URL
        logger.info(f"Processing URL: {url}")
        result = processor.process(url, notion_items[0] if notion_items else None)
        
        if not result:
            logger.error(f"Failed to process the URL: {url}")
            return False
        
        # Log the results
        logger.info(f"Successfully processed the URL: {url}")
        logger.info("Output files:")
        for key, path in result.items():
            if key in ["username", "title", "description"]:
                logger.info(f"  {key}: {path}")
                continue
                
            if isinstance(path, list):
                # Handle list of files (e.g., images)
                for file_path in path:
                    logger.info(f"  {key} (list item): {file_path}")
                    if not os.path.exists(file_path):
                        logger.warning(f"Output file does not exist: {file_path}")
            elif not os.path.exists(path):
                logger.warning(f"Output file does not exist: {path}")
            else:
                logger.info(f"  {key}: {path}")
        
        # Mark as processed in Notion if not a dry run
        if use_notion and notion_items and not dry_run:
            item_id = notion_items[0].get("id")
            if item_id:
                logger.info(f"Marking item {item_id} as processed in Notion")
                success = notion.mark_as_processed(item_id, metadata=result)
                if not success:
                    logger.error(f"Failed to mark item {item_id} as processed in Notion")
                    return False
            else:
                logger.warning("No item ID found, cannot mark as processed in Notion")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing production flow: {e}")
        return False

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the production flow for Instagram links")
    parser.add_argument("--url", help="Specific Instagram URL to test. If not provided, one will be fetched from Notion.")
    parser.add_argument("--no-notion", action="store_true", help="Don't use Notion integration")
    parser.add_argument("--dry-run", action="store_true", help="Don't mark as processed in Notion")
    args = parser.parse_args()
    
    use_notion = not args.no_notion
    success = test_instagram_production_flow(
        url=args.url,
        use_notion=use_notion,
        dry_run=args.dry_run
    )
    
    if success:
        logger.info("Test completed successfully")
        return 0
    else:
        logger.error("Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 