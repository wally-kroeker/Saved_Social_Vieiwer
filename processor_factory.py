"""
Processor factory module for the Process Saved Links application.

This module provides a factory class for creating processor instances
based on the specified platform type.
"""
from typing import Optional, Dict, Any, Type

from processors.base_processor import BaseProcessor
from processors.youtube_processor import YouTubeProcessor
from processors.instagram_processor import InstagramProcessor

class ProcessorFactory:
    """Factory class for creating processor instances."""
    
    _processors: Dict[str, Type[BaseProcessor]] = {
        "youtube": YouTubeProcessor,
        "instagram": InstagramProcessor,
    }
    
    @classmethod
    def create(cls, platform_type: str) -> Optional[BaseProcessor]:
        """
        Create a processor instance for the specified platform type.
        
        Args:
            platform_type: The type of processor to create (e.g., "youtube", "instagram")
            
        Returns:
            A processor instance, or None if the platform type is not supported
        """
        processor_class = cls._processors.get(platform_type.lower())
        if processor_class:
            return processor_class()
        return None
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        Get a list of supported platform types.
        
        Returns:
            A list of supported platform types
        """
        return list(cls._processors.keys()) 