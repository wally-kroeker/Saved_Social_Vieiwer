#!/usr/bin/env python3
"""
Script to check Notion API connectivity.

This script tests the connection to the Notion API using the configured
credentials and ensures the database is accessible.
"""
import os
import sys
from typing import Dict, Any

# Check if notion-client is installed
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
except ImportError:
    print("Error: The notion-client package is required.")
    print("Please install it using: pip install notion-client")
    sys.exit(1)

# Import locally used modules
try:
    import config
    from utils.logging_utils import get_logger
except ImportError:
    print("Warning: Unable to import local modules.")
    print("Testing with environment variables only.")
    config = None

def check_notion_connection() -> Dict[str, Any]:
    """
    Test the connection to the Notion API.
    
    Returns:
        Dict with status information
    """
    results = {
        "success": False,
        "api_connection": False,
        "database_access": False,
        "errors": [],
        "db_info": None
    }
    
    # Get Notion API token and database ID
    notion_token = os.environ.get("NOTION_API_TOKEN")
    if not notion_token and hasattr(config, "NOTION_API_TOKEN"):
        notion_token = config.NOTION_API_TOKEN
    
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id and hasattr(config, "NOTION_DATABASE_ID"):
        database_id = config.NOTION_DATABASE_ID
    
    # Check if credentials are available
    if not notion_token:
        results["errors"].append("Notion API token not found")
        return results
    
    if not database_id:
        results["errors"].append("Notion database ID not found")
        return results
    
    # Initialize Notion client
    try:
        client = Client(auth=notion_token)
        print(f"✅ Successfully initialized Notion client")
        results["api_connection"] = True
    except Exception as e:
        error_msg = f"Failed to initialize Notion client: {str(e)}"
        print(f"❌ {error_msg}")
        results["errors"].append(error_msg)
        return results
    
    # Test database access
    try:
        # Try to query the database with minimal data (just 1 item)
        response = client.databases.query(
            database_id=database_id,
            page_size=1
        )
        
        # Check if we got a valid response
        if "results" in response:
            print(f"✅ Successfully connected to database: {database_id}")
            results["database_access"] = True
            
            # Get some information about the database
            db_info = client.databases.retrieve(database_id=database_id)
            results["db_info"] = {
                "title": db_info.get("title", [{}])[0].get("text", {}).get("content", "Unknown"),
                "properties": list(db_info.get("properties", {}).keys()),
                "item_count": len(response.get("results", []))
            }
            
            # Print database information
            if "title" in db_info:
                title = db_info.get("title", [{}])[0].get("text", {}).get("content", "Unknown")
                print(f"📊 Database title: {title}")
            
            print(f"📊 Database properties: {', '.join(results['db_info']['properties'])}")
            print(f"📊 Contains items: {response.get('has_more', False) or len(response.get('results', [])) > 0}")
            
            results["success"] = True
        else:
            error_msg = "Invalid response from Notion API"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
    except APIResponseError as e:
        error_msg = f"Notion API error: {str(e)}"
        print(f"❌ {error_msg}")
        results["errors"].append(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        results["errors"].append(error_msg)
    
    return results

if __name__ == "__main__":
    print("🔗 Testing Notion connectivity...")
    results = check_notion_connection()
    
    print("\n=== Summary ===")
    if results["success"]:
        print("✅ Notion connection successful")
    else:
        print("❌ Notion connection failed")
        print("Errors:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    sys.exit(0 if results["success"] else 1) 