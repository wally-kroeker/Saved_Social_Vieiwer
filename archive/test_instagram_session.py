#!/usr/bin/env python3
from instaloader import Instaloader
import os

def test_instagram_session():
    # Initialize Instaloader
    L = Instaloader()
    
    # Try to load the session
    session_path = os.path.expanduser("~/.config/instaloader/session-walub")
    print(f"Testing session file: {session_path}")
    
    try:
        # Load the session
        L.load_session_from_file("walub", os.path.dirname(session_path))
        print("Successfully loaded session")
        
        # Test the session by getting the current user's profile
        profile = L.context.get_current_user()
        print(f"Logged in as: {profile.username}")
        
    except Exception as e:
        print(f"Error loading session: {e}")

if __name__ == "__main__":
    test_instagram_session() 