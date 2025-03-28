"""
File utilities for the Process Saved Links application.

This module provides functions for common file operations used throughout
the application, such as creating directories, ensuring valid filenames,
and handling file paths.
"""
import os
import re
import shutil
import json
from pathlib import Path
from datetime import datetime

# Import our new standardized filename utilities
from utils.filename_utils import (
    sanitize_string,
    generate_base_filename,
    get_output_paths,
    ensure_output_dir
)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str or Path): Path to the directory
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(directory_path)
    os.makedirs(path, exist_ok=True)
    return path

def sanitize_filename(filename):
    """
    Sanitize a filename to make it safe for all operating systems.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Use our new sanitization function
    return sanitize_string(filename)

def generate_output_path(platform, link_id, output_type, extension, base_dir=None, username=None, date=None, title=None):
    """
    Generate a standardized output path for content files.
    
    Args:
        platform (str): Platform name (e.g., "instagram", "youtube")
        link_id (str): Unique identifier for the content
        output_type (str): Type of output (e.g., "video", "thumbnail", "transcript")
        extension (str): File extension without the dot
        base_dir (str or Path, optional): Base directory for outputs
        username (str, optional): Username of the content creator
        date (str, optional): Date of the content in YYYY-MM-DD format
        title (str, optional): Title of the content
        
    Returns:
        Path: Path object for the output file
    """
    from config import OUTPUT_DIR
    
    if base_dir is None:
        base_dir = OUTPUT_DIR
    
    # Use our new filename utilities to generate consistent filenames
    if username and date and title:
        # Use our standardized naming pattern
        base_filename = generate_base_filename(
            platform=platform,
            username=username,
            date=date,
            title=title
        )
        
        # Create the platform-specific subdirectory
        platform_dir = Path(base_dir) / sanitize_string(platform)
        ensure_directory_exists(platform_dir)
        
        # Add the extension
        filename = f"{base_filename}.{extension}"
        
        return platform_dir / filename
    else:
        # Fall back to the old pattern if metadata is missing
        # But still place it in the platform subdirectory
        safe_id = sanitize_string(link_id)
        filename = f"{platform}_{safe_id}_{output_type}.{extension}"
        
        # Create the platform-specific subdirectory
        platform_dir = Path(base_dir) / sanitize_string(platform)
        ensure_directory_exists(platform_dir)
        
        return platform_dir / filename

def save_metadata(metadata, filepath):
    """
    Save metadata to a JSON file.
    
    Args:
        metadata (dict): Metadata to save
        filepath (str or Path): Path to save the metadata
        
    Returns:
        Path: Path object for the saved metadata file
    """
    filepath = Path(filepath)
    
    # Add timestamp to metadata
    metadata["processed_at"] = datetime.now().isoformat()
    
    # Create the directory if it doesn't exist
    ensure_directory_exists(filepath.parent)
    
    # Write the metadata to the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_metadata(filepath):
    """
    Load metadata from a JSON file.
    
    Args:
        filepath (str or Path): Path to the metadata file
        
    Returns:
        dict: Loaded metadata or None if file does not exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def copy_file(source, destination, username=None, date=None, title=None):
    """
    Copy a file from source to destination.
    
    Args:
        source (str or Path): Source file path
        destination (str or Path): Destination file path
        username (str, optional): Username of the content creator
        date (str, optional): Date of the content in YYYY-MM-DD format
        title (str, optional): Title of the content
        
    Returns:
        Path: Path object for the destination file
    """
    source = Path(source)
    destination = Path(destination)
    
    # If username, date, and title are provided, use the new naming pattern
    if username and date and title:
        # Extract platform from the destination path (usually this is in a platform subdirectory)
        platform = destination.parent.name
        if platform not in ["instagram", "youtube"]:
            platform = "unknown"
            
        # Generate the new filename using our standardized function
        base_filename = generate_base_filename(
            platform=platform,
            username=username,
            date=date,
            title=title
        )
        
        # Get the extension from the destination path
        extension = destination.suffix
        
        # Update the destination path with the new filename and ensure it's in the platform subdirectory
        from config import OUTPUT_DIR
        platform_dir = Path(OUTPUT_DIR) / sanitize_string(platform)
        ensure_directory_exists(platform_dir)
        
        destination = platform_dir / f"{base_filename}{extension}"
    
    # Create the destination directory if it doesn't exist
    ensure_directory_exists(destination.parent)
    
    # Copy the file
    shutil.copy2(source, destination)
    
    return destination
