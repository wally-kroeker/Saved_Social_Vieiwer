"""
Test configuration for the Process Saved Links application.

This module contains test-specific configuration settings that override
the main configuration for testing purposes.
"""
import os
import tempfile
from pathlib import Path

# Import the main configuration
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# Create a temporary output directory for testing
TEMP_OUTPUT_DIR = Path(tempfile.mkdtemp())

# Override the output directory
config.OUTPUT_DIR = TEMP_OUTPUT_DIR

# Find the Instagram download script
INSTA_SCRIPT_PATH = Path(__file__).resolve().parent.parent.parent / "instadownload_script" / "download_post.sh"
if INSTA_SCRIPT_PATH.exists():
    config.PLATFORMS["instagram"]["download_script"] = str(INSTA_SCRIPT_PATH)
    print(f"Using Instagram download script at: {INSTA_SCRIPT_PATH}")
else:
    print(f"Warning: Instagram download script not found at: {INSTA_SCRIPT_PATH}")
    # Try to find it in other locations
    possible_locations = [
        Path(__file__).resolve().parent.parent / "scripts" / "download_post.sh",
        Path("/home/walub/scripts/instadownload_script/download_post.sh")
    ]
    
    for location in possible_locations:
        if location.exists():
            config.PLATFORMS["instagram"]["download_script"] = str(location)
            print(f"Using Instagram download script at: {location}")
            break
    else:
        print("Error: Could not find Instagram download script")

# Print the test configuration
print(f"Test output directory: {config.OUTPUT_DIR}")
print(f"Instagram download script: {config.PLATFORMS['instagram']['download_script']}")

# Set log level to DEBUG for testing
import logging
logging.getLogger("test_instagram_processor").setLevel(logging.DEBUG)
logging.getLogger("instagram_processor").setLevel(logging.DEBUG) 