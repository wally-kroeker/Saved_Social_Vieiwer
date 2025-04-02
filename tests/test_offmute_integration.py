#!/usr/bin/env python3
"""
Test script to verify that the Instagram processor can correctly use offmute to generate transcripts.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from processors.instagram_processor import InstagramProcessor
from utils.logging_utils import get_logger

logger = get_logger("test_offmute_integration")

def test_offmute_integration():
    """Test that the Instagram processor can correctly use offmute to generate transcripts."""
    # Check if GEMINI_API_KEY is set
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set in environment or config")
        return False
    
    logger.info(f"GEMINI_API_KEY: {config.GEMINI_API_KEY[:4]}...{config.GEMINI_API_KEY[-4:]}")
    logger.info(f"OFFMUTE_ENABLED: {config.OFFMUTE_ENABLED}")
    
    # Create an Instagram processor
    processor = InstagramProcessor()
    
    # Check if offmute is enabled
    if not processor.offmute_enabled:
        logger.error("Offmute is not enabled in the Instagram processor")
        return False
    
    # Find a test video file
    test_dir = Path(os.path.dirname(__file__))
    test_videos = list(test_dir.glob("**/*.mp4"))
    
    if not test_videos:
        logger.error("No test video files found")
        return False
    
    test_video = test_videos[0]
    logger.info(f"Using test video: {test_video}")
    
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        output_path = Path(temp_file.name)
    
    # Generate a transcript
    logger.info(f"Generating transcript for {test_video} to {output_path}")
    result = processor._generate_transcript_with_offmute(test_video, output_path)
    
    if result:
        logger.info(f"Successfully generated transcript at {output_path}")
        logger.info(f"Transcript content (first 200 chars): {open(output_path, 'r').read()[:200]}")
        return True
    else:
        logger.error("Failed to generate transcript")
        return False

if __name__ == "__main__":
    success = test_offmute_integration()
    sys.exit(0 if success else 1) 