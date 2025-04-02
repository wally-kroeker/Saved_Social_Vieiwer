"""
Integration module for YouTube and Instagram processors to use the new filename utilities.
This provides adapter functions to bridge between the older processor code and
the new standardized filename utilities.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import os
import json
from datetime import datetime

from utils.filename_utils import (
    sanitize_string,
    generate_base_filename,
    get_file_paths,
    get_output_paths,
    ensure_output_dir
)

# Platform identifiers
PLATFORM_YOUTUBE = 'youtube'
PLATFORM_INSTAGRAM = 'instagram'

def get_youtube_output_paths(video_info: Dict[str, Any], use_platform_subdir: bool = True) -> Dict[str, Path]:
    """
    Generate standardized output paths for a YouTube video
    
    Args:
        video_info: YouTube video metadata dictionary
        use_platform_subdir: Whether to use platform subdirectory
        
    Returns:
        Dictionary with paths for video, thumbnail, transcript, and metadata files
    """
    # Extract relevant fields from YouTube metadata
    platform = PLATFORM_YOUTUBE
    
    # Extract username (channel name or uploader)
    username = video_info.get('channel', video_info.get('uploader', 'unknown'))
    
    # Extract date (upload_date or current date)
    date = video_info.get('upload_date')
    if date and len(date) == 8:  # YouTube format: YYYYMMDD
        date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    
    # Extract title
    title = video_info.get('title', '')
    
    # Generate standardized output paths
    return get_output_paths(
        platform=platform,
        username=username,
        date=date,
        title=title,
        use_platform_subdir=use_platform_subdir
    )

def get_instagram_output_paths(post_info: Dict[str, Any], use_platform_subdir: bool = True) -> Dict[str, Path]:
    """
    Generate standardized output paths for an Instagram post
    
    Args:
        post_info: Instagram post metadata dictionary
        use_platform_subdir: Whether to use platform subdirectory
        
    Returns:
        Dictionary with paths for video, thumbnail, transcript, and metadata files
    """
    platform = PLATFORM_INSTAGRAM
    
    # Extract username
    username = post_info.get('owner_username', post_info.get('owner', {}).get('username', 'unknown'))
    
    # Extract date
    date = None
    if 'taken_at_timestamp' in post_info:
        try:
            timestamp = int(post_info['taken_at_timestamp'])
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            date = None
    
    # Extract title/caption
    title = None
    if 'edge_media_to_caption' in post_info and 'edges' in post_info['edge_media_to_caption']:
        edges = post_info['edge_media_to_caption']['edges']
        if edges and 'node' in edges[0] and 'text' in edges[0]['node']:
            title = edges[0]['node']['text']
    
    # Generate standardized output paths
    return get_output_paths(
        platform=platform,
        username=username,
        date=date,
        title=title,
        use_platform_subdir=use_platform_subdir
    )

def save_metadata_file(metadata: Dict[str, Any], output_path: Path) -> None:
    """
    Save metadata to a JSON file with consistent formatting
    
    Args:
        metadata: Dictionary of metadata to save
        output_path: Path where the metadata file should be saved
    """
    # Ensure the target directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add platform field if not present
    if 'platform' not in metadata:
        if 'uploader' in metadata or 'channel' in metadata:
            metadata['platform'] = PLATFORM_YOUTUBE
        elif 'owner_username' in metadata or 'owner' in metadata:
            metadata['platform'] = PLATFORM_INSTAGRAM
        else:
            metadata['platform'] = 'unknown'
    
    # Write the metadata file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def save_transcript_file(transcript: str, output_path: Path) -> None:
    """
    Save transcript to a Markdown file
    
    Args:
        transcript: Transcript text
        output_path: Path where the transcript file should be saved
    """
    # Ensure the target directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the transcript file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(transcript) 