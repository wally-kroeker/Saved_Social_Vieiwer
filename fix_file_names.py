#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import json
import argparse
from config import OUTPUT_DIR

def extract_metadata_from_filename(filename):
    """Extract username, date, and title from a filename."""
    # Remove extension
    base_name = os.path.splitext(filename)[0]
    
    # Try to match the standard pattern: username-YYYY-MM-DD-title
    standard_pattern = r'^([^-]+)-(\d{4}-\d{2}-\d{2})-(.+)$'
    match = re.match(standard_pattern, base_name)
    
    if match:
        username, date, title = match.groups()
        return username, date, title
    
    # Try to match Instagram pattern: instagram_ID_video
    instagram_pattern = r'^instagram_([A-Za-z0-9_-]+)_video$'
    match = re.match(instagram_pattern, base_name)
    
    if match:
        instagram_id = match.group(1)
        # Try to find metadata file
        metadata_file = os.path.join(os.path.dirname(filename), f"instagram_{instagram_id}_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Extract username
                username = metadata.get('node', {}).get('owner', {}).get('username', 'unknown')
                
                # Extract date
                timestamp = metadata.get('node', {}).get('taken_at_timestamp')
                if timestamp:
                    date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                else:
                    date = datetime.now().strftime("%Y-%m-%d")
                
                # Extract title from caption
                edges = metadata.get('node', {}).get('edge_media_to_caption', {}).get('edges', [])
                if edges:
                    title = edges[0].get('node', {}).get('text', '').split('\n')[0][:100]
                else:
                    title = f"Instagram Post {instagram_id}"
                
                return username, date, title
            except Exception as e:
                print(f"Error reading metadata file {metadata_file}: {e}")
    
    return None, None, None

def clean_filename(filename):
    """Clean filename by removing/replacing problematic characters."""
    # Remove quotes and hashtags
    cleaned = filename.replace('"', '').replace('#', '')
    # Replace multiple spaces with single space
    cleaned = ' '.join(cleaned.split())
    # Remove any dots, underscores, or question marks before the extension
    base, ext = os.path.splitext(cleaned)
    base = base.rstrip('._?')
    # Remove any trailing spaces
    base = base.rstrip()
    return f"{base}{ext}"

def find_matching_video(files, base_pattern):
    """Find a video file matching the base pattern, ignoring special endings."""
    base_pattern = base_pattern.rstrip('._?')
    for f in files:
        if f.endswith('.mp4'):
            f_base = os.path.splitext(f)[0].rstrip('._?')
            if f_base.lower() == base_pattern.lower():
                return f
    return None

def fix_file_names(directory, dry_run=True):
    """Fix file names in the Processed-ContentIdeas directory."""
    # Get all files
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Track processed files to avoid duplicates
    processed_files = set()
    renamed_files = {}  # Track old->new name mappings
    
    # First pass: process video files
    for filename in files:
        if filename.endswith('.mp4'):
            base_name = os.path.splitext(filename)[0]
            username, date, title = extract_metadata_from_filename(filename)
            
            if username and date and title:
                # Clean the filename
                new_filename = clean_filename(f"{username}-{date}-{title}.mp4")
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)
                
                if filename != new_filename:
                    if dry_run:
                        print(f"Would rename video: {filename} -> {new_filename}")
                        renamed_files[filename] = new_filename
                    else:
                        try:
                            shutil.move(old_path, new_path)
                            print(f"Renamed video: {filename} -> {new_filename}")
                            renamed_files[filename] = new_filename
                        except Exception as e:
                            print(f"Error renaming video {filename}: {e}")
                    processed_files.add(filename)
                
                # Process associated image files (thumbnails)
                base_without_ext = os.path.splitext(filename)[0]
                for img_file in files:
                    if any(img_file.startswith(f"{base_without_ext}") for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        if img_file not in processed_files:
                            img_ext = os.path.splitext(img_file)[1]
                            new_img_name = os.path.splitext(new_filename)[0] + img_ext
                            old_img_path = os.path.join(directory, img_file)
                            new_img_path = os.path.join(directory, new_img_name)
                            
                            if img_file != new_img_name:
                                if dry_run:
                                    print(f"Would rename image: {img_file} -> {new_img_name}")
                                else:
                                    try:
                                        shutil.move(old_img_path, new_img_path)
                                        print(f"Renamed image: {img_file} -> {new_img_name}")
                                    except Exception as e:
                                        print(f"Error renaming image {img_file}: {e}")
                                processed_files.add(img_file)
    
    # Second pass: process transcript files
    for filename in files:
        if filename.endswith('.md') or filename.endswith('._transcription.md'):
            base_name = os.path.splitext(filename)[0]
            base_name = base_name.replace('_transcription', '')  # Remove _transcription suffix
            
            # Skip if already processed
            if filename in processed_files:
                continue
            
            # Try to find associated video file
            video_pattern = None
            if base_name.startswith('instagram_'):
                # Handle Instagram-style transcripts
                instagram_id = base_name.split('_')[1]
                video_pattern = f"instagram_{instagram_id}_video"
            else:
                # Try to match standard pattern
                username, date, title = extract_metadata_from_filename(base_name)
                if username and date and title:
                    video_pattern = f"{username}-{date}-{title}"
            
            if video_pattern:
                # Find the matching video file
                matching_video = find_matching_video(files, video_pattern)
                if matching_video:
                    # Use the same base name as the video (without extension)
                    video_base = os.path.splitext(matching_video)[0]
                    if matching_video in renamed_files:
                        # If video was/will be renamed, use the new name
                        video_base = os.path.splitext(renamed_files[matching_video])[0]
                    new_filename = f"{video_base}.md"
                    old_path = os.path.join(directory, filename)
                    new_path = os.path.join(directory, new_filename)
                    
                    if filename != new_filename:
                        if dry_run:
                            print(f"Would rename transcript: {filename} -> {new_filename}")
                        else:
                            try:
                                shutil.move(old_path, new_path)
                                print(f"Renamed transcript: {filename} -> {new_filename}")
                            except Exception as e:
                                print(f"Error renaming transcript {filename}: {e}")
                        processed_files.add(filename)
                else:
                    print(f"No matching video file found for transcript: {filename}")
            else:
                print(f"Could not determine correct name for transcript: {filename}")

def main():
    """Main function to fix file names."""
    parser = argparse.ArgumentParser(description='Fix file names in output directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    directory = OUTPUT_DIR
    
    print("Starting file name cleanup...")
    if args.dry_run:
        print("DRY RUN: Showing proposed changes without making them")
    else:
        print("WARNING: This will actually rename files. Press Ctrl+C to cancel.")
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            exit(0)
    
    fix_file_names(directory, dry_run=args.dry_run)
    print("Cleanup complete!")

if __name__ == "__main__":
    main() 