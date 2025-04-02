#!/usr/bin/env python3
"""Script to clean up transcript files."""
import os
import re
import shutil
import json
import argparse
from pathlib import Path
from config import OUTPUT_DIR

def cleanup_transcripts(directory):
    """Rename Instagram-style transcript files to match the server's expected pattern."""
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Find Instagram-style transcript files
    instagram_pattern = r'^instagram_([A-Za-z0-9_-]+)_transcript\.md$'
    for filename in files:
        match = re.match(instagram_pattern, filename)
        if match:
            # Extract the ID from the filename
            instagram_id = match.group(1)
            
            # Find the corresponding video file
            video_pattern = f"instagram_{instagram_id}_video.mp4"
            video_files = [f for f in files if f.startswith(video_pattern)]
            
            if video_files:
                video_file = video_files[0]
                # Extract username, date, and title from video filename
                # Format: username-YYYY-MM-DD-title.mp4
                base_name = os.path.splitext(video_file)[0]
                parts = base_name.split('-')
                
                if len(parts) >= 4:
                    username = parts[0]
                    date = parts[1]
                    title = '-'.join(parts[2:])
                    
                    # Create new transcript filename
                    new_filename = f"{username}-{date}-{title}.md"
                    old_path = os.path.join(directory, filename)
                    new_path = os.path.join(directory, new_filename)
                    
                    # Rename the file
                    try:
                        shutil.move(old_path, new_path)
                        print(f"Renamed: {filename} -> {new_filename}")
                    except Exception as e:
                        print(f"Error renaming {filename}: {e}")
            else:
                print(f"No matching video file found for transcript: {filename}")

def main():
    """Main function to clean up transcripts."""
    parser = argparse.ArgumentParser(description='Clean up transcript files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    directory = OUTPUT_DIR
    
    print("Starting transcript cleanup...")
    cleanup_transcripts(directory)
    print("Cleanup complete!")

if __name__ == "__main__":
    main() 