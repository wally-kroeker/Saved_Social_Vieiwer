#!/usr/bin/env python3
"""
Create a local Instagram session file in the project directory.
"""
from instaloader import Instaloader
import os

# Define the local session path
SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
USERNAME = "walub"
SESSION_FILE = os.path.join(SESSION_DIR, f"session-{USERNAME}")

# Create the directory if it doesn't exist
os.makedirs(SESSION_DIR, exist_ok=True)

# Create an instance of Instaloader
L = Instaloader()

try:
    # Login using interactive login
    print(f"Logging in as {USERNAME}...")
    L.interactive_login(USERNAME)
    
    # Explicitly save the session file to our project directory
    L.save_session_to_file(SESSION_FILE)
    
    print(f"Session saved successfully to {SESSION_FILE}")
    print(f"To use this session, update your config.py to point to this file.")
    
except Exception as e:
    print(f"Error logging in: {e}") 