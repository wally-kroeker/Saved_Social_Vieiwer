#!/usr/bin/env python3
"""
Script to clean up and standardize file names in the output directory.
Files that don't match the pattern [username]-[date]-[title].[extension] will be moved to an archive folder.
"""
import os
import re
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import config
from utils.logging_utils import get_logger

logger = get_logger("cleanup_output")

def get_file_metadata(filepath: Path) -> Optional[Dict[str, str]]:
    """
    Extract metadata from a file's name or its associated JSON file.
    
    Args:
        filepath (Path): Path to the file
        
    Returns:
        Dict[str, str]: Dictionary containing username, date, and title if found
    """
    # Try to get metadata from the filename first
    filename = filepath.name
    pattern = r"^([^-]+)-(\d{4}-\d{2}-\d{2})-(.+?)\.[^.]+$"
    match = re.match(pattern, filename)
    
    if match:
        return {
            "username": match.group(1),
            "date": match.group(2),
            "title": match.group(3)
        }
    
    # If filename doesn't match, try to find associated JSON file
    json_pattern = filepath.with_suffix(".json")
    if json_pattern.exists():
        try:
            with open(json_pattern, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                if "node" in metadata:
                    node = metadata["node"]
                    username = node.get("owner", {}).get("username")
                    timestamp = node.get("taken_at_timestamp")
                    date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else None
                    title = None
                    if "edge_media_to_caption" in node:
                        edges = node["edge_media_to_caption"]["edges"]
                        if edges:
                            title = edges[0]["node"]["text"].split("\n")[0][:100]
                    
                    if username and date and title:
                        return {
                            "username": username,
                            "date": date,
                            "title": title
                        }
        except Exception as e:
            logger.warning(f"Error reading metadata from {json_pattern}: {e}")
    
    return None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for all operating systems.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Limit length to avoid issues with max path length
    if len(sanitized) > 200:
        sanitized = sanitized[:197] + "..."
    return sanitized

def get_new_filename(filepath: Path, metadata: Dict[str, str]) -> Tuple[Path, bool]:
    """
    Generate the new filename for a file based on metadata.
    
    Args:
        filepath (Path): Path to the file
        metadata (Dict[str, str]): Dictionary containing username, date, and title
        
    Returns:
        Tuple[Path, bool]: New path and whether it would conflict with existing files
    """
    extension = filepath.suffix
    new_filename = f"{metadata['username']}-{metadata['date']}-{sanitize_filename(metadata['title'])}{extension}"
    new_path = filepath.parent / new_filename
    
    # Check if the new filename would conflict with existing files
    counter = 1
    while new_path.exists():
        base, ext = os.path.splitext(new_filename)
        new_filename = f"{base}-{counter}{ext}"
        new_path = filepath.parent / new_filename
        counter += 1
    
    return new_path, counter > 1

def rename_file(filepath: Path, metadata: Dict[str, str], dry_run: bool = True) -> Path:
    """
    Rename a file to match the standard pattern.
    
    Args:
        filepath (Path): Path to the file
        metadata (Dict[str, str]): Dictionary containing username, date, and title
        dry_run (bool): If True, only show what would be done without making changes
        
    Returns:
        Path: New path of the renamed file
    """
    new_path, has_conflict = get_new_filename(filepath, metadata)
    
    if dry_run:
        logger.info(f"Would rename: {filepath.name} -> {new_path.name}")
        if has_conflict:
            logger.warning(f"  Note: This would conflict with existing files, using counter suffix")
    else:
        filepath.rename(new_path)
    
    return new_path

def cleanup_output_directory(dry_run: bool = True):
    """
    Clean up the output directory by standardizing file names and moving non-conforming files to an archive.
    
    Args:
        dry_run (bool): If True, only show what would be done without making changes
    """
    output_dir = Path(config.OUTPUT_DIR)
    archive_dir = output_dir / "archive"
    
    if dry_run:
        logger.info("DRY RUN - No changes will be made")
        logger.info("The following changes would be made:")
        logger.info("-" * 50)
    
    # Create archive directory if it doesn't exist
    if not dry_run:
        archive_dir.mkdir(exist_ok=True)
    
    # Get all files in the output directory
    files = list(output_dir.glob("*"))
    
    # Group files by their base name (without extension)
    file_groups: Dict[str, List[Path]] = {}
    for filepath in files:
        if filepath.is_file() and filepath.name != "archive":
            base_name = filepath.stem
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(filepath)
    
    # Process each group of files
    for base_name, files in file_groups.items():
        # Try to get metadata from the first file
        metadata = get_file_metadata(files[0])
        
        if metadata:
            # Rename all files in the group to match the standard pattern
            for filepath in files:
                try:
                    new_path = rename_file(filepath, metadata, dry_run)
                    if not dry_run:
                        logger.info(f"Renamed {filepath} to {new_path}")
                except Exception as e:
                    logger.error(f"Error renaming {filepath}: {e}")
                    if not dry_run:
                        # Move to archive if rename fails
                        shutil.move(str(filepath), str(archive_dir / filepath.name))
        else:
            # Move all files in the group to archive
            for filepath in files:
                if dry_run:
                    logger.info(f"Would move to archive: {filepath.name}")
                else:
                    try:
                        shutil.move(str(filepath), str(archive_dir / filepath.name))
                        logger.info(f"Moved {filepath} to archive")
                    except Exception as e:
                        logger.error(f"Error moving {filepath} to archive: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up and standardize file names in the output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what changes would be made without making them")
    args = parser.parse_args()
    
    cleanup_output_directory(dry_run=args.dry_run) 