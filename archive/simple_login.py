#!/usr/bin/env python3
"""
Simple script to create an Instagram session file.
"""
from instaloader import Instaloader

# Create a new instance of Instaloader
loader = Instaloader()

# Login interactively
username = "walub"
loader.interactive_login(username)

# Save the session file to the current directory
print(f"Saving session file for {username}...")
loader.save_session_to_file(f"sessions/session-{username}")
print("Session saved successfully.") 