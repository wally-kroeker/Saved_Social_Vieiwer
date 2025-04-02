"""
Test script for the Instagram processor.

This script tests the Instagram processor with a temporary output directory
to avoid affecting the production environment.
"""
import os
import sys
import tempfile
import argparse
import subprocess
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the test configuration first to override settings
from tests import test_config

import config
from processors.instagram_processor import InstagramProcessor
from utils.logging_utils import get_logger

logger = get_logger("test_instagram_processor")

def test_direct_download(url):
    """
    Test the download script directly to see if it works.
    
    Args:
        url (str): Instagram URL to test
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Find the download script
    download_script = config.PLATFORMS["instagram"]["download_script"]
    if not os.path.exists(download_script):
        logger.error(f"Download script not found at: {download_script}")
        return False
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Run the download script directly
            logger.info(f"Running download script directly: {download_script} {url}")
            process = subprocess.run(
                [download_script, url],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Log the output
            logger.info(f"Download script stdout: {process.stdout}")
            logger.info(f"Download script stderr: {process.stderr}")
            
            # Check if the download was successful
            if process.returncode != 0:
                logger.error(f"Download script failed with return code: {process.returncode}")
                return False
            
            # Check if any files were downloaded
            script_dir = os.path.dirname(os.path.abspath(download_script))
            temp_download_dir = os.path.join(script_dir, "temp_downloads")
            
            if not os.path.exists(temp_download_dir):
                logger.error(f"Temp download directory not found: {temp_download_dir}")
                return False
            
            files = os.listdir(temp_download_dir)
            logger.info(f"Files in temp download directory: {files}")
            
            if not files:
                logger.error("No files were downloaded")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing direct download: {e}")
            return False

def test_instagram_processor(url, use_temp_dir=True):
    """
    Test the Instagram processor with a given URL.
    
    Args:
        url (str): Instagram URL to test
        use_temp_dir (bool): Whether to use a temporary directory for output
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create a temporary directory for output if requested
    original_output_dir = config.OUTPUT_DIR
    temp_dir = None
    
    try:
        if use_temp_dir:
            temp_dir = tempfile.TemporaryDirectory()
            config.OUTPUT_DIR = Path(temp_dir.name)
            logger.info(f"Using temporary output directory: {config.OUTPUT_DIR}")
        
        # First test direct download to see if it works
        if not test_direct_download(url):
            logger.error("Direct download test failed, skipping processor test")
            return False
        
        # Initialize the Instagram processor
        processor = InstagramProcessor()
        
        # Check if the processor can handle the URL
        if not processor.can_process(url):
            logger.error(f"The URL is not recognized as an Instagram URL: {url}")
            return False
        
        # Process the URL
        result = processor.process(url)
        
        if not result:
            logger.error(f"Failed to process the URL: {url}")
            return False
        
        # Log the results
        logger.info(f"Successfully processed the URL: {url}")
        logger.info(f"Output files:")
        for key, path in result.items():
            logger.info(f"  {key}: {path}")
            
            # Add more debugging information
            logger.debug(f"Processing result item - Key: {key}, Type: {type(path)}")
            
            # Skip verification for non-file values
            if key in ["username", "title", "description"]:
                logger.debug(f"Skipping verification for non-file value: {key}")
                continue
            
            # Verify that the file exists
            if isinstance(path, list):
                # Handle list of files (e.g., images)
                logger.debug(f"Verifying list of files for key: {key}")
                for file_path in path:
                    if not os.path.exists(file_path):
                        logger.error(f"Output file does not exist: {file_path}")
                        return False
            elif not os.path.exists(path):
                logger.error(f"Output file does not exist: {path}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Instagram processor: {e}")
        return False
    
    finally:
        # Restore the original output directory
        config.OUTPUT_DIR = original_output_dir
        
        # Clean up the temporary directory
        if temp_dir:
            temp_dir.cleanup()

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the Instagram processor")
    parser.add_argument("url", help="Instagram URL to test")
    parser.add_argument("--output-dir", help="Output directory (uses temp dir if not specified)")
    parser.add_argument("--direct-only", action="store_true", help="Only test direct download, not the processor")
    args = parser.parse_args()
    
    use_temp_dir = True
    if args.output_dir:
        config.OUTPUT_DIR = Path(args.output_dir)
        use_temp_dir = False
    
    if args.direct_only:
        success = test_direct_download(args.url)
    else:
        success = test_instagram_processor(args.url, use_temp_dir)
    
    if success:
        logger.info("Test completed successfully")
        return 0
    else:
        logger.error("Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 