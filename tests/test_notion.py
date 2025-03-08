"""
Test script for the Notion integration module.

This script tests the basic functionality of the Notion integration module,
including connecting to the Notion API, retrieving unprocessed links, and
updating their status.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Make sure the required packages are installed
try:
    from notion_client import Client
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages are not installed.")
    print("Please install them using: uv pip install notion-client python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: .env file not found. Please create one based on .env.example")
    print("You can also set environment variables directly.")

# Import the Notion integration module
try:
    import notion_integration
except ImportError:
    print("Error: notion_integration.py not found or has errors.")
    sys.exit(1)

def test_notion_connection():
    """Test connection to the Notion API."""
    print("\n=== Testing Notion API Connection ===")
    
    # Check if token and database ID are set
    token = os.getenv("NOTION_API_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not token:
        print("Error: NOTION_API_TOKEN environment variable is not set.")
        print("Please set it in .env file or as an environment variable.")
        sys.exit(1)
    
    if not database_id:
        print("Error: NOTION_DATABASE_ID environment variable is not set.")
        print("Please set it in .env file or as an environment variable.")
        sys.exit(1)
    
    try:
        # Try to initialize the Notion integration
        notion_instance = notion_integration.NotionIntegration()
        print("✓ Successfully connected to Notion API")
        return notion_instance
    except Exception as e:
        print(f"✗ Failed to connect to Notion API: {e}")
        sys.exit(1)

def test_get_unprocessed_links(notion_instance):
    """Test retrieving unprocessed links from the Notion database."""
    print("\n=== Testing Retrieval of Unprocessed Links ===")
    
    try:
        # Try to get unprocessed links
        links = notion_instance.get_unprocessed_links(limit=5)
        print(f"✓ Successfully retrieved {len(links)} unprocessed links")
        
        # Print the first link for verification
        if links:
            first_link = links[0]
            print(f"\nFirst unprocessed link:")
            print(f"  ID: {first_link['id']}")
            print(f"  URL: {first_link['url']}")
            print(f"  Title: {first_link['title']}")
            return first_link
        else:
            print("Note: No unprocessed links found in the database.")
            return None
    except Exception as e:
        print(f"✗ Failed to retrieve unprocessed links: {e}")
        sys.exit(1)

def test_mark_as_processed(notion_instance, link):
    """Test marking a link as processed in the Notion database."""
    if not link:
        print("\n=== Skipping Test: Mark as Processed ===")
        print("No unprocessed link available for testing.")
        return
    
    print("\n=== Testing Mark as Processed ===")
    print(f"Note: This test will mark the link '{link['url']}' as processed.")
    
    # For automated testing, automatically proceed
    # Comment out the interactive prompt
    # response = input("Do you want to continue? (y/n): ")
    # if response.lower() != 'y':
    #     print("Test skipped.")
    #     return
    
    try:
        # Create test metadata
        metadata = {
            "platform": "test_platform",
            "content_id": "test_content_id",
            "processed_by": "test_script",
            "test_timestamp": datetime.now().isoformat(),
            "filename": "test_processed_file.mp4"  # Add filename for the Name property
        }
        
        # Try to mark as processed
        success = notion_instance.mark_as_processed(link['id'], metadata)
        
        if success:
            print(f"✓ Successfully marked link as processed")
        else:
            print(f"✗ Failed to mark link as processed")
    except Exception as e:
        print(f"✗ Error while marking link as processed: {e}")

def main():
    """Run all tests."""
    print("=== Notion Integration Tests ===")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test connection
    notion_instance = test_notion_connection()
    
    # Test getting unprocessed links
    link = test_get_unprocessed_links(notion_instance)
    
    # Test marking as processed
    test_mark_as_processed(notion_instance, link)
    
    print("\n=== Tests Completed ===")

if __name__ == "__main__":
    main() 