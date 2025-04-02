#!/usr/bin/env python3
"""
Instagram Connectivity Test Script
---------------------------------
Tests connectivity to the Instagram API using the configured credentials.
This script is part of the diagnostics menu for the Process Saved Links project.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional

try:
    import instaloader
except ImportError:
    print("Error: instaloader package not found. Installing...")
    os.system("pip install instaloader")
    try:
        import instaloader
    except ImportError:
        print("Failed to install instaloader. Please install it manually with: pip install instaloader")
        sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('instagram_connection_test')

def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """Load configuration from the config file."""
    if not os.path.exists(config_file):
        logger.error(f"Config file '{config_file}' not found")
        return {}
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return {}

def check_instagram_connection() -> Dict[str, Any]:
    """
    Test connection to Instagram API using configured credentials.
    
    Returns:
        dict: Results of the connection test including status and any error messages
    """
    results = {
        "success": False,
        "authenticated": False,
        "error": None,
        "username": None,
        "details": {}
    }
    
    # Try to load credentials from config or environment variables
    config = load_config()
    username = os.environ.get('INSTAGRAM_USERNAME') or config.get('instagram', {}).get('username')
    password = os.environ.get('INSTAGRAM_PASSWORD') or config.get('instagram', {}).get('password')
    
    if not username or not password:
        results["error"] = "Instagram credentials not found in environment variables or config.json"
        logger.error(results["error"])
        return results
    
    results["username"] = username
    
    # Create Instagram loader instance
    instance = instaloader.Instaloader()
    
    try:
        # Test basic connectivity by attempting to login
        logger.info(f"Attempting to log in to Instagram as {username}")
        instance.login(username, password)
        results["authenticated"] = True
        
        # Get profile information as a basic test
        profile = instaloader.Profile.from_username(instance.context, username)
        results["details"] = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography[:50] + "..." if len(profile.biography) > 50 else profile.biography,
            "followers": profile.followers,
            "followees": profile.followees,
            "posts": profile.mediacount
        }
        
        # Successfully connected and retrieved data
        results["success"] = True
        logger.info("Successfully connected to Instagram and retrieved profile data")
    
    except instaloader.exceptions.ConnectionException as e:
        results["error"] = f"Connection error: {str(e)}"
        logger.error(results["error"])
    except instaloader.exceptions.BadCredentialsException:
        results["error"] = "Invalid Instagram credentials"
        logger.error(results["error"])
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        results["error"] = "Two-factor authentication is required"
        logger.error(results["error"])
    except instaloader.exceptions.InstaloaderException as e:
        results["error"] = f"Instaloader error: {str(e)}"
        logger.error(results["error"])
    except Exception as e:
        results["error"] = f"Unexpected error: {str(e)}"
        logger.error(results["error"])
    
    return results

if __name__ == "__main__":
    print("\n===== Instagram Connection Test =====\n")
    
    results = check_instagram_connection()
    
    if results["success"]:
        print("✅ Successfully connected to Instagram!")
        print(f"  - Logged in as: {results['username']}")
        print(f"  - Full name: {results['details']['full_name']}")
        print(f"  - Followers: {results['details']['followers']}")
        print(f"  - Following: {results['details']['followees']}")
        print(f"  - Posts: {results['details']['posts']}")
    else:
        print("❌ Failed to connect to Instagram.")
        print(f"  - Error: {results['error']}")
        
        if not results.get("username"):
            print("\nSuggestion: Add Instagram credentials to your config.json file or set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables.")
        elif not results.get("authenticated"):
            print("\nSuggestion: Check your Instagram credentials. They may be incorrect or your account might have additional security requirements.")
    
    print("\nTest completed.") 