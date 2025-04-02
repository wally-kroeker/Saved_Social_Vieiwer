#!/usr/bin/env python3
import os
import re
import shutil
import argparse
from pathlib import Path

def is_valid_filename(filename):
    # Check for Instagram pattern
    instagram_pattern = r'^instagram_[A-Za-z0-9_-]+_(metadata|thumbnail|transcript|video|video_transcription)\.(json|jpg|md|mp4)$'
    if re.match(instagram_pattern, filename):
        return True
    
    # Check for content creator pattern
    creator_pattern = r'^[a-zA-Z0-9_-]+-\d{4}-\d{2}-\d{2}-[a-zA-Z0-9_-]+\.(jpg|json|md|mp4|txt)$'
    if re.match(creator_pattern, filename):
        return True
    
    return False

def cleanup_files(directory, dry_run=True):
    # Create archive directory if it doesn't exist
    archive_dir = os.path.join(directory, 'archive')
    if not dry_run:
        os.makedirs(archive_dir, exist_ok=True)
    
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Track files to move
    files_to_move = []
    
    # Check each file
    for filename in files:
        if not is_valid_filename(filename):
            files_to_move.append(filename)
    
    # Print summary
    print(f"\nFound {len(files_to_move)} files that don't match the naming patterns:")
    for filename in files_to_move:
        print(f"  - {filename}")
    
    if dry_run:
        print("\nThis was a dry run. No files were moved.")
        return
    
    # Move files
    for filename in files_to_move:
        src = os.path.join(directory, filename)
        dst = os.path.join(archive_dir, filename)
        try:
            shutil.move(src, dst)
            print(f"Moved: {filename} -> archive/")
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    
    print(f"\nMoved {len(files_to_move)} files to archive directory")

def main():
    parser = argparse.ArgumentParser(description='Clean up files by moving non-conforming files to archive')
    parser.add_argument('directory', help='Directory to clean up')
    parser.add_argument('--no-dry-run', action='store_true', help='Actually move files instead of just showing what would be moved')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a directory")
        return
    
    cleanup_files(args.directory, dry_run=not args.no_dry_run)

if __name__ == '__main__':
    main() 