#!/usr/bin/env python3
from instaloader import Instaloader
import os

def create_instagram_session():
    # Create the session directory if it doesn't exist
    session_dir = os.path.expanduser("~/.config/instaloader")
    os.makedirs(session_dir, exist_ok=True)
    
    # Initialize Instaloader with specific options
    L = Instaloader(
        dirname_pattern=session_dir,
        filename_pattern="session-{username}",
        download_videos=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # Get username and password
    username = "walub"
    password = input(f"Enter Instagram password for {username}: ")
    
    try:
        # Login and save session
        L.login(username, password)
        print("Successfully logged in and saved session")
        
        # Verify the session file was created
        session_file = os.path.join(session_dir, f"session-{username}")
        if os.path.exists(session_file):
            print(f"Session file created at: {session_file}")
        else:
            print("Warning: Session file was not created")
            
    except Exception as e:
        print(f"Error creating session: {e}")

if __name__ == "__main__":
    create_instagram_session() 