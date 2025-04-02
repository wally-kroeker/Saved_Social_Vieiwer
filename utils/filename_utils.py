"""
Filename utilities for consistent naming across different platforms.
This module ensures all media files follow a consistent naming scheme
that works well with web applications and avoids problematic characters.
"""

import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Core output directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'output'

def sanitize_string(text: str) -> str:
    """
    Sanitize a string to be safe for filenames and URLs.
    
    Args:
        text: The string to sanitize
        
    Returns:
        A sanitized string with problematic characters replaced
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace hashtags with tag_ prefix
    text = re.sub(r'#(\w+)', r'tag_\1', text)
    
    # Replace remaining special chars and spaces with hyphens
    text = re.sub(r'[^\w\s-]', '-', text)
    
    # Replace all spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    
    # Trim to reasonable length to avoid filesystem limits
    return text[:100].strip('-')

def format_date(date_obj: Optional[datetime] = None, date_str: Optional[str] = None) -> str:
    """
    Format a date consistently as YYYY-MM-DD.
    
    Args:
        date_obj: A datetime object
        date_str: A date string (will attempt to parse if provided)
        
    Returns:
        A formatted date string or empty string if both inputs are None
    """
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    
    if date_str:
        # Try to parse common date formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        # If we couldn't parse it but it looks like a date, return as is
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
            
    # Default to today if we can't determine date
    return datetime.now().strftime('%Y-%m-%d')

def generate_base_filename(
    platform: str,
    username: str,
    date: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """
    Generate a consistent base filename across platforms.
    
    Args:
        platform: The platform name (e.g., 'youtube', 'instagram')
        username: The content creator's username
        date: The content date (YYYY-MM-DD)
        title: The content title or description
        
    Returns:
        A sanitized, consistent base filename without extension
    """
    # Sanitize each component
    platform = sanitize_string(platform)
    username = sanitize_string(username)
    
    # Format date if provided
    if date:
        formatted_date = format_date(date_str=date)
    else:
        formatted_date = format_date(date_obj=datetime.now())
    
    # Build the base components
    base = f"{platform}-{username}-{formatted_date}"
    
    # Add title if provided
    if title:
        sanitized_title = sanitize_string(title)
        if sanitized_title:
            base += f"-{sanitized_title}"
    
    return base

def get_file_paths(base_filename: str) -> Dict[str, str]:
    """
    Get the full file paths for all related files.
    
    Args:
        base_filename: The base filename without extension
        
    Returns:
        Dictionary containing paths for each file type
    """
    return {
        'video': f"{base_filename}.mp4",
        'thumbnail': f"{base_filename}.jpg",
        'transcript': f"{base_filename}.md",
        'metadata': f"{base_filename}.json",
    }

def ensure_output_dir(platform: Optional[str] = None) -> Path:
    """
    Ensure the output directory exists.
    
    Args:
        platform: Optional platform subdirectory
        
    Returns:
        Path object to the output directory
    """
    if platform:
        output_path = OUTPUT_DIR / sanitize_string(platform)
    else:
        output_path = OUTPUT_DIR
        
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def get_output_paths(
    platform: str,
    username: str,
    date: Optional[str] = None,
    title: Optional[str] = None,
    use_platform_subdir: bool = True
) -> Dict[str, Path]:
    """
    Get the full path objects for all output files.
    
    Args:
        platform: The platform name
        username: The content creator's username
        date: The content date
        title: The content title or description
        use_platform_subdir: Whether to use a platform subdirectory
        
    Returns:
        Dictionary containing Path objects for each file type
    """
    # Generate the base filename
    base_filename = generate_base_filename(platform, username, date, title)
    
    # Get the output directory
    if use_platform_subdir:
        output_dir = ensure_output_dir(platform)
    else:
        output_dir = ensure_output_dir()
    
    # Get relative paths
    file_paths = get_file_paths(base_filename)
    
    # Convert to full paths
    return {
        key: output_dir / path
        for key, path in file_paths.items()
    }

def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """
    Extract metadata from a filename that follows our naming convention.
    Useful for migration or identifying existing files.
    
    Args:
        filename: The filename to parse
        
    Returns:
        Dictionary with extracted metadata (platform, username, date, title)
    """
    # Remove extension
    base = os.path.splitext(os.path.basename(filename))[0]
    
    # Remove _transcription suffix if present
    if base.endswith('_transcription'):
        base = base[:-14]
    
    # Split by hyphens
    parts = base.split('-')
    
    result = {
        'platform': '',
        'username': '',
        'date': '',
        'title': ''
    }
    
    # Logic based on likely patterns
    
    # Pattern detection for 'platform-username-date-title'
    if len(parts) >= 3:
        # Common platforms
        if parts[0].lower() in ['youtube', 'instagram', 'tiktok', 'twitter']:
            result['platform'] = parts[0].lower()
            result['username'] = parts[1]
            
            # Look for date format in remaining parts
            for i, part in enumerate(parts[2:], 2):
                if re.match(r'\d{4}-\d{2}-\d{2}', part):
                    result['date'] = part
                    # Title is everything after the date
                    if i+1 < len(parts):
                        result['title'] = '-'.join(parts[i+1:])
                    break
        else:
            # Assume username-date-title pattern (common in current files)
            # First part is likely the username
            result['username'] = parts[0]
            
            # Look for date format
            for i, part in enumerate(parts[1:], 1):
                if re.match(r'\d{4}-\d{2}-\d{2}', part):
                    result['date'] = part
                    
                    # Try to determine platform from filename
                    if 'instagram' in filename.lower():
                        result['platform'] = 'instagram'
                    elif 'youtube' in filename.lower():
                        result['platform'] = 'youtube'
                    # Look for common Instagram usernames
                    elif result['username'].lower() in ['nononsensespirituality', 'edhonour']:
                        result['platform'] = 'instagram'
                    else:
                        result['platform'] = 'unknown'
                    
                    # Title is everything after the date
                    if i+1 < len(parts):
                        result['title'] = '-'.join(parts[i+1:])
                    break
    
    # If we still don't have a platform but have a username that looks familiar
    if not result['platform'] and result['username']:
        if result['username'].lower() in ['nononsensespirituality', 'edhonour']:
            result['platform'] = 'instagram'
    
    return result 