"""
Output manager module for the Process Saved Links application.

This module provides the OutputManager class for standardizing output
formatting and storage across different platform processors.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import config
from utils.logging_utils import get_logger
from utils.file_utils import (
    ensure_directory_exists,
    sanitize_filename,
    generate_output_path,
    save_metadata,
    load_metadata,
    copy_file
)

logger = get_logger("output_manager")

class OutputManager:
    """
    Class for managing standardized output formatting and storage.
    
    This class provides methods for generating consistent output paths,
    saving content files, and managing metadata across different platform
    processors.
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the OutputManager.
        
        Args:
            output_dir (str or Path, optional): Base directory for outputs.
                If None, it will be fetched from config.
        """
        self.output_dir = Path(output_dir) if output_dir else config.OUTPUT_DIR
        ensure_directory_exists(self.output_dir)
        logger.info(f"Output manager initialized with directory: {self.output_dir}")
    
    def generate_output_paths(self, platform: str, content_id: str) -> Dict[str, Path]:
        """
        Generate standardized output file paths for the given content.
        
        Args:
            platform (str): Platform name (e.g., "instagram", "youtube")
            content_id (str): Unique identifier for the content
            
        Returns:
            Dict[str, Path]: Dictionary of output file paths
        """
        return {
            "video": generate_output_path(
                platform,
                content_id,
                "video",
                config.OUTPUT_FORMAT["video_extension"],
                self.output_dir
            ),
            "thumbnail": generate_output_path(
                platform,
                content_id,
                "thumbnail",
                config.OUTPUT_FORMAT["thumbnail_extension"],
                self.output_dir
            ),
            "transcript": generate_output_path(
                platform,
                content_id,
                "transcript",
                config.OUTPUT_FORMAT["transcript_extension"],
                self.output_dir
            ),
            "metadata": generate_output_path(
                platform,
                content_id,
                "metadata",
                config.OUTPUT_FORMAT["metadata_extension"],
                self.output_dir
            )
        }
    
    def save_content_file(self, source_path: Union[str, Path], 
                         destination_path: Union[str, Path]) -> Path:
        """
        Save a content file to the output directory.
        
        Args:
            source_path (str or Path): Source file path
            destination_path (str or Path): Destination file path
            
        Returns:
            Path: Path object for the saved file
        """
        source_path = Path(source_path)
        destination_path = Path(destination_path)
        
        if not source_path.exists():
            logger.error(f"Source file does not exist: {source_path}")
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
        
        # Create the destination directory if it doesn't exist
        ensure_directory_exists(destination_path.parent)
        
        # Copy the file
        try:
            copied_path = copy_file(source_path, destination_path)
            logger.info(f"Saved content file: {copied_path}")
            return copied_path
        except Exception as e:
            logger.error(f"Failed to save content file: {e}")
            raise
    
    def save_metadata(self, platform: str, content_id: str, 
                     metadata: Dict[str, Any]) -> Path:
        """
        Save metadata for the processed content.
        
        Args:
            platform (str): Platform name (e.g., "instagram", "youtube")
            content_id (str): Unique identifier for the content
            metadata (Dict[str, Any]): Metadata to save
            
        Returns:
            Path: Path to the saved metadata file
        """
        # Add platform and content ID to metadata
        metadata["platform"] = platform
        metadata["content_id"] = content_id
        
        # Generate the metadata file path
        metadata_path = self.generate_output_paths(platform, content_id)["metadata"]
        
        # Save the metadata
        try:
            saved_path = save_metadata(metadata, metadata_path)
            logger.info(f"Saved metadata: {saved_path}")
            return saved_path
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise
    
    def save_transcript(self, platform: str, content_id: str, 
                       transcript: str) -> Path:
        """
        Save a transcript for the processed content.
        
        Args:
            platform (str): Platform name (e.g., "instagram", "youtube")
            content_id (str): Unique identifier for the content
            transcript (str): Transcript content
            
        Returns:
            Path: Path to the saved transcript file
        """
        # Generate the transcript file path
        transcript_path = self.generate_output_paths(platform, content_id)["transcript"]
        
        # Create the directory if it doesn't exist
        ensure_directory_exists(transcript_path.parent)
        
        # Save the transcript
        try:
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            logger.info(f"Saved transcript: {transcript_path}")
            return transcript_path
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            raise
    
    def get_processed_content(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of all processed content.
        
        Args:
            platform (str, optional): Filter by platform
            
        Returns:
            List[Dict[str, Any]]: List of processed content metadata
        """
        results = []
        
        # Get all metadata files
        metadata_pattern = f"*_metadata.{config.OUTPUT_FORMAT['metadata_extension']}"
        if platform:
            metadata_pattern = f"{platform}*_metadata.{config.OUTPUT_FORMAT['metadata_extension']}"
        
        metadata_files = list(self.output_dir.glob(metadata_pattern))
        
        # Load metadata from each file
        for metadata_file in metadata_files:
            try:
                metadata = load_metadata(metadata_file)
                if metadata:
                    results.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
        
        return results
