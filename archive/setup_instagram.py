#!/usr/bin/env python3
from instaloader import Instaloader
import os

def setup_instagram_session():
    # Create the session directory if it doesn't exist
    session_dir = os.path.expanduser("~/.config/instaloader")
    os.makedirs(session_dir, exist_ok=True)
    
    # Initialize Instaloader
    L = Instaloader(
        dirname_pattern=session_dir,
        filename_pattern="session-{username}",
        download_videos=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # Try to load existing session
    try:
        L.load_session_from_file("walub")
        print("Successfully loaded existing session")
    except FileNotFoundError:
        print("No existing session found. Please login:")
        L.interactive_login("walub")
        print("Session saved successfully")

if __name__ == "__main__":
    setup_instagram_session() 