"""
Platform processor module for the Process Saved Links application.

This module provides a class for processing content from specific platforms,
handling platform-specific settings such as batch sizes and rate limiting.
"""
import time
import logging
import threading
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Optional, Dict, Any, List

import platform_config
from processor_factory import ProcessorFactory
from notion_integration import get_unprocessed_links, mark_as_processed, mark_as_failed
from utils.logging_utils import get_logger

logger = get_logger("platform_processor")

class PlatformProcessor:
    """Class for processing content from specific platforms."""
    
    def __init__(self, platform_type: str):
        """
        Initialize the platform processor.
        
        Args:
            platform_type: The type of platform to process (e.g., "youtube", "instagram")
        """
        self.platform_type = platform_type.lower()
        self.processor = ProcessorFactory.create(self.platform_type)
        
        if not self.processor:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        # Get platform-specific settings
        if self.platform_type == "youtube":
            self.batch_size = platform_config.YOUTUBE_BATCH_SIZE
            self.delay_seconds = platform_config.YOUTUBE_DELAY_SECONDS
        elif self.platform_type == "instagram":
            self.batch_size = platform_config.INSTAGRAM_BATCH_SIZE
            self.delay_seconds = platform_config.INSTAGRAM_DELAY_SECONDS
        else:
            self.batch_size = platform_config.DEFAULT_BATCH_SIZE
            self.delay_seconds = platform_config.DEFAULT_DELAY_SECONDS
        
        logger.info(f"Initialized {self.platform_type} processor with batch_size={self.batch_size}, delay={self.delay_seconds}s")
    
    def process_batch(self, limit: Optional[int] = None, continuous: bool = False) -> int:
        """
        Process a batch of items from the platform.
        
        Args:
            limit: Maximum number of items to process (overrides batch_size if provided)
            continuous: Whether to process continuously until no more items are available
            
        Returns:
            Number of items processed
        """
        effective_batch_size = limit if limit is not None else self.batch_size
        processed_count = 0
        
        while True:
            logger.info(f"Processing {self.platform_type} batch with size {effective_batch_size}")
            
            # Get unprocessed links, using platform-specific filtering
            items = get_unprocessed_links(limit=effective_batch_size, platform=self.platform_type)
            logger.info(f"Found {len(items)} unprocessed links")
            
            if not items:
                logger.info(f"No more {self.platform_type} links to process")
                break
            
            # Filter items for the current platform
            platform_items = []
            for item in items:
                url = item.get("url", "")
                if self.processor.can_process(url):
                    platform_items.append(item)
            
            if not platform_items:
                logger.info(f"No {self.platform_type} links to process in this batch")
                if not continuous:
                    break
                time.sleep(self.delay_seconds)
                continue
            
            # Process each item
            for item in platform_items:
                url = item.get("url")
                if not url:
                    logger.warning(f"Skipping item {item.get('id')} with no URL")
                    continue
                
                if not self.processor.can_process(url):
                    logger.info(f"Skipping non-{self.platform_type} URL: {url}")
                    continue
                
                try:
                    logger.info(f"Processing {self.platform_type} URL: {url}")
                    result = self.processor.process(url, item)
                    
                    # Check if transcript generation was successful for video content
                    # Only mark as processed if either:
                    # 1. There's no video (so transcript not required)
                    # 2. There is a video AND we have a transcript
                    should_mark_processed = True
                    
                    if self.platform_type in ["youtube", "instagram"]:
                        if result and "video" in result:
                            # We have a video, so we should check for transcript
                            if "transcript" not in result:
                                logger.warning(f"Video processed but transcript generation failed for {url}")
                                should_mark_processed = False
                    
                    # Mark as processed in Notion only if we should
                    if result and should_mark_processed:
                        success = mark_as_processed(item.get("id"), result)
                        
                        if success:
                            processed_count += 1
                            logger.info(f"Successfully processed {self.platform_type} item: {item.get('id')}")
                        else:
                            logger.error(f"Failed to mark {self.platform_type} item as processed: {item.get('id')}")
                    elif result:
                        # We have a result but transcript failed
                        logger.warning(f"Item not marked as processed due to missing transcript: {item.get('id')}")
                    else:
                        # No result at all
                        logger.error(f"Processing failed for {self.platform_type} item: {item.get('id')}")
                        
                except Exception as e:
                    logger.error(f"Error processing {self.platform_type} URL {url}: {str(e)}")
                    mark_as_failed(item.get("id"), str(e))
            
            # Apply delay between batches if specified
            if self.delay_seconds > 0 and continuous:
                logger.info(f"Waiting {self.delay_seconds} seconds before processing next {self.platform_type} batch...")
                time.sleep(self.delay_seconds)
            
            # Exit loop if not in continuous mode
            if not continuous:
                break
        
        logger.info(f"Processed {processed_count} {self.platform_type} items")
        return processed_count 