#!/usr/bin/env python3
"""
Test downloading a specific Instagram post.
"""
import os
import tempfile
from scripts.instagram_downloader import download_instagram_post

# URL of a regular Instagram post from our list
# Using a regular post (reel) rather than a story which might have expired
instagram_url = "https://www.instagram.com/reel/DG0xVf3OI0y/?igsh=MW94Z3Z6OWgxdGoycA=="

print(f"Testing download of Instagram post: {instagram_url}")

# Create a temporary directory for output
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Saving output to: {temp_dir}")
    
    # Try to download the post without a session (anonymous)
    result = download_instagram_post(
        url=instagram_url,
        output_dir=temp_dir,
        session_path=None  # No session, try anonymous download
    )
    
    if result:
        print("Success! Post downloaded:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to download the post.") 