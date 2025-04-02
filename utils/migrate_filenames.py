#!/usr/bin/env python3
"""
Migration script to update existing files to the new naming convention.
This script scans the output directory for media files and renames them
according to the new standardized naming scheme.
"""

import os
import json
import shutil
from pathlib import Path
import argparse
import re
import logging
from typing import Dict, List, Tuple, Optional

# Import our filename utilities
from utils.filename_utils import (
    sanitize_string, 
    generate_base_filename,
    get_file_paths,
    extract_metadata_from_filename,
    OUTPUT_DIR
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('filename_migration')

def identify_file_groups() -> Dict[str, List[Path]]:
    """
    Scan the output directory and group related files together
    (e.g., video, thumbnail, transcript, metadata for the same content)
    
    Returns:
        Dictionary mapping base names to lists of related files
    """
    file_groups = {}
    
    # Walk through the output directory
    for root, _, files in os.walk(OUTPUT_DIR):
        for filename in files:
            file_path = Path(root) / filename
            
            # Skip any non-media or metadata files
            if not any(filename.endswith(ext) for ext in ['.mp4', '.jpg', '.png', '.md', '.json']):
                continue
                
            # Get base name without extension
            base_name = os.path.splitext(filename)[0]
            
            # Handle special case where transcript might have _transcription suffix
            if base_name.endswith('_transcription'):
                base_name = base_name[:-14]  # Remove _transcription suffix
                
            # Store in our groups dictionary
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(file_path)
    
    return file_groups

def extract_metadata(file_paths: List[Path]) -> Dict[str, str]:
    """
    Extract metadata from the files, prioritizing JSON metadata files,
    then falling back to filename pattern matching
    
    Args:
        file_paths: List of paths to related files
        
    Returns:
        Dictionary with extracted metadata
    """
    # Default metadata
    metadata = {
        'platform': 'unknown',
        'username': 'unknown',
        'date': None,
        'title': None
    }
    
    # First try to find a JSON metadata file
    for path in file_paths:
        if path.suffix.lower() == '.json':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Extract platform-specific metadata
                if 'platform' in json_data:
                    metadata['platform'] = json_data['platform']
                
                # For YouTube
                if 'uploader' in json_data:
                    metadata['username'] = json_data['uploader']
                elif 'channel' in json_data:
                    metadata['username'] = json_data['channel']
                
                # For Instagram
                elif 'owner_username' in json_data:
                    metadata['username'] = json_data['owner_username']
                
                # Extract date
                if 'upload_date' in json_data:
                    metadata['date'] = json_data['upload_date']
                elif 'taken_at_timestamp' in json_data:
                    from datetime import datetime
                    timestamp = int(json_data['taken_at_timestamp'])
                    metadata['date'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                # Extract title
                if 'title' in json_data:
                    metadata['title'] = json_data['title']
                elif 'edge_media_to_caption' in json_data and 'edges' in json_data['edge_media_to_caption']:
                    edges = json_data['edge_media_to_caption']['edges']
                    if edges and 'node' in edges[0] and 'text' in edges[0]['node']:
                        metadata['title'] = edges[0]['node']['text']
                
                break
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error parsing JSON metadata file: {path}, {str(e)}")
    
    # If we don't have complete metadata, try to extract from filename
    if not all(metadata.values()):
        # Take the first file path to extract info from filename
        if file_paths:
            filename = file_paths[0].name
            filename_metadata = extract_metadata_from_filename(filename)
            
            # Update any missing fields
            for key, value in filename_metadata.items():
                if not metadata[key] and value:
                    metadata[key] = value
    
    # Ensure platform is set
    if not metadata['platform'] or metadata['platform'] == 'unknown':
        # Try to determine platform from filename or path
        for path in file_paths:
            path_str = str(path).lower()
            if 'instagram' in path_str:
                metadata['platform'] = 'instagram'
                break
            elif 'youtube' in path_str:
                metadata['platform'] = 'youtube'
                break
    
    # Last resort date extraction from filename
    if not metadata['date']:
        for path in file_paths:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
            if date_match:
                metadata['date'] = date_match.group(1)
                break
    
    return metadata

def rename_file_group(old_files: List[Path], metadata: Dict[str, str], dry_run: bool = False) -> List[Tuple[Path, Path]]:
    """
    Rename a group of related files according to the new naming convention
    
    Args:
        old_files: List of paths to files that should be renamed
        metadata: Dictionary with metadata for generating new names
        dry_run: If True, don't actually rename files
        
    Returns:
        List of tuples (old_path, new_path)
    """
    # Generate new base filename
    new_base = generate_base_filename(
        platform=metadata['platform'],
        username=metadata['username'],
        date=metadata['date'],
        title=metadata['title']
    )
    
    # Create output directory based on platform
    platform_dir = OUTPUT_DIR / sanitize_string(metadata['platform'])
    if not dry_run:
        platform_dir.mkdir(parents=True, exist_ok=True)
    
    # For each file, determine its type and new name
    renamed_files = []
    
    for old_path in old_files:
        # Determine file type based on extension
        ext = old_path.suffix.lower()
        
        if ext == '.mp4':
            file_type = 'video'
        elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
            file_type = 'thumbnail'
        elif ext == '.md':
            # Special case for transcripts with _transcription suffix
            if old_path.stem.endswith('_transcription'):
                file_type = 'transcript'
            else:
                file_type = 'transcript'
        elif ext == '.json':
            file_type = 'metadata'
        else:
            # Skip files we don't recognize
            logger.warning(f"Skipping unrecognized file type: {old_path}")
            continue
        
        # Get new standard filename for this file type
        new_filename = f"{new_base}{ext}"
        new_path = platform_dir / new_filename
        
        # Store the old->new mapping
        renamed_files.append((old_path, new_path))
        
        # Log the planned rename
        logger.info(f"{'Would rename' if dry_run else 'Renaming'}: {old_path} -> {new_path}")
        
        # Perform the rename if not dry run
        if not dry_run:
            if new_path.exists():
                logger.warning(f"Destination file already exists: {new_path}, skipping")
                continue
                
            try:
                # Ensure parent directory exists
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file to new location
                shutil.copy2(old_path, new_path)
                logger.info(f"Copied: {old_path} -> {new_path}")
                
                # Optionally delete the original if needed
                # os.remove(old_path)
                # logger.info(f"Deleted original: {old_path}")
            except (IOError, OSError) as e:
                logger.error(f"Error copying file {old_path} to {new_path}: {str(e)}")
    
    return renamed_files

def migrate_all_files(dry_run: bool = False, delete_originals: bool = False) -> int:
    """
    Migrate all files in the output directory to the new naming convention
    
    Args:
        dry_run: If True, don't actually rename files
        delete_originals: If True, delete original files after successful migration
        
    Returns:
        Count of successfully migrated file groups
    """
    # Find all file groups
    logger.info(f"Scanning output directory: {OUTPUT_DIR}")
    file_groups = identify_file_groups()
    
    logger.info(f"Found {len(file_groups)} file groups to process")
    
    # Process each group
    migrated_count = 0
    all_renamed_files = []
    
    for base_name, file_paths in file_groups.items():
        logger.info(f"Processing group: {base_name} ({len(file_paths)} files)")
        
        # Extract metadata from the files
        metadata = extract_metadata(file_paths)
        logger.info(f"Extracted metadata: {metadata}")
        
        # Rename the files
        renamed_files = rename_file_group(file_paths, metadata, dry_run)
        all_renamed_files.extend(renamed_files)
        
        if renamed_files:
            migrated_count += 1
    
    # If we need to delete originals and it's not a dry run
    if delete_originals and not dry_run:
        for old_path, _ in all_renamed_files:
            try:
                os.remove(old_path)
                logger.info(f"Deleted original file: {old_path}")
            except (IOError, OSError) as e:
                logger.error(f"Error deleting original file {old_path}: {str(e)}")
    
    return migrated_count

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Migrate existing files to the new naming convention"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Don't actually rename files, just show what would happen"
    )
    parser.add_argument(
        '--delete-originals',
        action='store_true',
        help="Delete original files after successful migration"
    )
    args = parser.parse_args()
    
    logger.info(f"Starting filename migration, dry run: {args.dry_run}")
    
    try:
        migrated_count = migrate_all_files(args.dry_run, args.delete_originals)
        logger.info(f"Migration complete. {migrated_count} file groups processed.")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 