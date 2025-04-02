#!/usr/bin/env python
"""
Instagram downloader script for the Process Saved Links application.

This script provides a standalone function to download Instagram posts, reels,
and stories using the instaloader library.
"""
import os
import sys
import json
import tempfile
import shutil
import logging
from pathlib import Path

# Try importing instaloader, provide installation instructions if not found
try:
    import instaloader
    from instaloader.exceptions import InstaloaderException
except ImportError:
    print("Error: instaloader package is required.")
    print("Please install it using: pip install instaloader")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("instagram_downloader")

def get_shortcode_from_url(url):
    """
    Extract the shortcode from an Instagram URL.
    
    Args:
        url (str): Instagram URL
        
    Returns:
        str: Shortcode or None if not found
    """
    import re
    
    # Patterns for different types of Instagram URLs
    patterns = [
        r'instagram\.com/p/([^/]+)/?',
        r'instagram\.com/reel/([^/]+)/?',
        r'instagram\.com/stories/[^/]+/([^/]+)/?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # Remove any query parameters
            shortcode = match.group(1).split('?')[0]
            return shortcode
            
    logger.error(f"Could not extract shortcode from URL: {url}")
    return None

def download_instagram_post(url, output_dir=None, session_path=None):
    """
    Download an Instagram post, reel, or story.
    
    Args:
        url (str): Instagram URL to download
        output_dir (str, optional): Directory to save the downloaded files
        session_path (str, optional): Path to an existing session file
        
    Returns:
        dict: Dictionary containing paths to downloaded files
    """
    # Extract the shortcode from the URL
    shortcode = get_shortcode_from_url(url)
    if not shortcode:
        logger.error(f"Invalid Instagram URL: {url}")
        return None
    
    # Create a temporary directory if no output directory is provided
    with tempfile.TemporaryDirectory() as temp_dir:
        download_dir = output_dir or temp_dir
        logger.info(f"Downloading to: {download_dir}")
        
        try:
            # Initialize Instaloader with specific options
            L = instaloader.Instaloader(
                dirname_pattern=download_dir,
                download_videos=True,
                download_video_thumbnails=True,
                save_metadata=True,
                compress_json=False
            )
            
            # Attempt to log in anonymously if no session path is provided
            logged_in = False
            
            # Try to log in using session file
            if session_path:
                try:
                    logger.info(f"Attempting to use session: {session_path}")
                    # Direct login without session file (anonymous)
                    # This is more likely to work for most public posts
                    logged_in = True
                except Exception as e:
                    logger.warning(f"Could not use session: {e}")
            
            # Download the post by shortcode
            try:
                logger.info(f"Downloading post with shortcode: {shortcode}")
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                L.download_post(post, target=shortcode)
                logger.info("Download completed successfully")
            except Exception as e:
                logger.error(f"Error downloading post: {e}")
                return None
            
            # Collect the downloaded files
            result = {}
            downloaded_files = os.listdir(download_dir)
            logger.info(f"Downloaded files: {downloaded_files}")
            
            # Find different types of files
            video_files = [f for f in downloaded_files if f.endswith(".mp4")]
            image_files = [f for f in downloaded_files if f.endswith((".jpg", ".jpeg", ".png")) and not f.endswith("_thumbnail.jpg")]
            json_files = [f for f in downloaded_files if f.endswith(".json")]
            caption_files = [f for f in downloaded_files if f.endswith(".txt")]
            
            # Organize the results
            if video_files:
                result["video"] = os.path.join(download_dir, video_files[0])
                logger.info(f"Found video: {video_files[0]}")
            
            if image_files:
                result["images"] = [os.path.join(download_dir, f) for f in image_files]
                result["thumbnail"] = os.path.join(download_dir, image_files[0])
                logger.info(f"Found {len(image_files)} images")
            
            if json_files:
                result["metadata"] = os.path.join(download_dir, json_files[0])
                logger.info(f"Found metadata: {json_files[0]}")
                
                # Extract username from metadata
                try:
                    with open(result["metadata"], "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    if "node" in metadata and "owner" in metadata["node"]:
                        result["username"] = metadata["node"]["owner"]["username"]
                        logger.info(f"Username: {result['username']}")
                except Exception as e:
                    logger.warning(f"Error extracting username from metadata: {e}")
            
            if caption_files:
                result["caption"] = os.path.join(download_dir, caption_files[0])
                logger.info(f"Found caption: {caption_files[0]}")
            
            if not result:
                logger.error("No files were downloaded")
                return None
                
            # If we're using a temporary directory, copy the files to the output directory
            if output_dir is None and result:
                output_dir = tempfile.mkdtemp()
                for key, value in result.items():
                    if key == "images":
                        # Handle list of images
                        new_paths = []
                        for i, img_path in enumerate(value):
                            dest_path = os.path.join(output_dir, f"image_{i}{os.path.splitext(img_path)[1]}")
                            shutil.copy2(img_path, dest_path)
                            new_paths.append(dest_path)
                        result[key] = new_paths
                    elif key not in ["username"]:
                        # Handle single file
                        dest_path = os.path.join(output_dir, os.path.basename(value))
                        shutil.copy2(value, dest_path)
                        result[key] = dest_path
                
                result["output_dir"] = output_dir
                logger.info(f"Copied files to output directory: {output_dir}")
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return None

if __name__ == "__main__":
    # Script can be run directly with arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Instagram posts, reels, and stories")
    parser.add_argument("url", help="Instagram URL to download")
    parser.add_argument("--output-dir", help="Directory to save the downloaded files")
    parser.add_argument("--session", help="Path to an existing session file")
    args = parser.parse_args()
    
    result = download_instagram_post(args.url, args.output_dir, args.session)
    
    if result:
        print("\nDownload successful!")
        print("Files:")
        for key, value in result.items():
            if key == "images":
                print(f"  Images:")
                for img in value:
                    print(f"    - {img}")
            elif key not in ["output_dir", "username"]:
                print(f"  {key}: {value}")
        
        if "username" in result:
            print(f"\nUsername: {result['username']}")
            
        sys.exit(0)
    else:
        print("\nDownload failed!")
        sys.exit(1) 