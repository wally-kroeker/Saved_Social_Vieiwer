"""
Base processor module for the Process Saved Links application.

This module defines the BaseProcessor class, which provides the common
interface and functionality for all platform-specific processors.
"""
import re
from abc import ABC, abstractmethod
from pathlib import Path

import config
from utils.logging_utils import get_logger

class BaseProcessor(ABC):
    """
    Base class for all platform-specific content processors.
    
    This abstract class defines the common interface that all platform
    processors must implement, as well as providing common utility
    methods.
    """
    
    def __init__(self, platform_name):
        """
        Initialize the BaseProcessor.
        
        Args:
            platform_name (str): Name of the platform this processor handles
        """
        self.platform_name = platform_name
        self.logger = get_logger(f"{platform_name}_processor")
        self.config = config.PLATFORMS.get(platform_name, {})
        
    @abstractmethod
    def can_process(self, url):
        """
        Check if this processor can handle the given URL.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if this processor can handle the URL, False otherwise
        """
        pass
    
    @abstractmethod
    def process(self, url, notion_item=None):
        """
        Process the content at the given URL.
        
        Args:
            url (str): URL to process
            notion_item (dict, optional): Notion database item related to this URL
            
        Returns:
            dict: Processing results including output file paths and metadata
        """
        pass
    
    def extract_id_from_url(self, url):
        """
        Extract a unique identifier from the URL.
        
        This method should be overridden by platform-specific subclasses
        to extract an appropriate ID.
        
        Args:
            url (str): URL to extract ID from
            
        Returns:
            str: Extracted ID or None if extraction failed
        """
        return None
    
    def generate_output_paths(self, content_id):
        """
        Generate standardized output file paths for the given content ID.
        
        Args:
            content_id (str): Unique identifier for the content
            
        Returns:
            dict: Dictionary of output file paths
        """
        from utils.file_utils import generate_output_path
        
        return {
            "video": generate_output_path(
                self.platform_name,
                content_id,
                "video",
                config.OUTPUT_FORMAT["video_extension"]
            ),
            "thumbnail": generate_output_path(
                self.platform_name,
                content_id,
                "thumbnail",
                config.OUTPUT_FORMAT["thumbnail_extension"]
            ),
            "transcript": generate_output_path(
                self.platform_name,
                content_id,
                "transcript",
                config.OUTPUT_FORMAT["transcript_extension"]
            ),
            "metadata": generate_output_path(
                self.platform_name,
                content_id,
                "metadata",
                config.OUTPUT_FORMAT["metadata_extension"]
            )
        }
    
    def save_metadata(self, content_id, metadata):
        """
        Save metadata for the processed content.
        
        Args:
            content_id (str): Unique identifier for the content
            metadata (dict): Metadata to save
            
        Returns:
            Path: Path to the saved metadata file
        """
        from utils.file_utils import save_metadata
        
        # Add platform and content ID to metadata
        metadata["platform"] = self.platform_name
        metadata["content_id"] = content_id
        
        # Generate the metadata file path
        metadata_path = self.generate_output_paths(content_id)["metadata"]
        
        # Save the metadata
        return save_metadata(metadata, metadata_path)
