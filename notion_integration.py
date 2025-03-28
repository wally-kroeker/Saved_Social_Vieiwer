"""
Notion integration module for the Process Saved Links application.

This module provides functions for interacting with the Notion database,
including querying for unprocessed links and updating their status after
processing.
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Check if notion-client is installed, if not, provide instruction
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
except ImportError:
    raise ImportError(
        "The notion-client package is required. "
        "Please install it using: pip install notion-client"
    )

import config
from utils.logging_utils import get_logger

logger = get_logger("notion_integration")

class NotionIntegration:
    """
    Class for interacting with the Notion database.
    
    This class provides methods for querying the Notion database for unprocessed
    links and updating their status after processing.
    """
    
    def __init__(self, token: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize the NotionIntegration.
        
        Args:
            token (str, optional): Notion API token. If None, it will be fetched from config.
            database_id (str, optional): Notion database ID. If None, it will be fetched from config.
        """
        self.token = token or config.NOTION_API_TOKEN
        self.database_id = database_id or config.NOTION_DATABASE_ID
        
        if not self.token:
            logger.error("Notion API token is not set")
            raise ValueError("Notion API token is required. Set it in config.py or as an environment variable.")
        
        if not self.database_id:
            logger.error("Notion database ID is not set")
            raise ValueError("Notion database ID is required. Set it in config.py or as an environment variable.")
        
        try:
            self.client = Client(auth=self.token)
            logger.info("Notion client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            raise
    
    def get_unprocessed_links(self, limit: int = 10, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get unprocessed links from the Notion database.
        
        Args:
            limit (int, optional): Maximum number of links to retrieve. Defaults to 10.
            platform (str, optional): If specified, directly use URL filtering to find links for this platform.
            
        Returns:
            List[Dict[str, Any]]: List of unprocessed links with their metadata
        """
        logger.info(f"Querying Notion database for up to {limit} unprocessed links")
        
        try:
            # Filter for unprocessed links based on the existing script's property names
            filter_params = {
                "filter": {
                    "property": "Status",
                    "status": {
                        "equals": "Not started"
                    }
                },
                "page_size": limit
            }
            
            # If platform is specified, use additional filter for YouTube links
            if platform == "youtube":
                # Directly check Notion database for YouTube URLs
                filter_params = {
                    "filter": {
                        "and": [
                            {
                                "property": "Status",
                                "status": {
                                    "equals": "Not started"
                                }
                            },
                            {
                                "property": "URL",
                                "url": {
                                    "contains": "youtu"
                                }
                            }
                        ]
                    },
                    "page_size": limit
                }
                logger.info(f"Using YouTube-specific filtering for Notion query")
            
            # Query the database
            response = self.client.databases.query(
                database_id=self.database_id,
                **filter_params
            )
            
            results = []
            
            # Process the response
            for item in response.get("results", []):
                # Extract the URL
                url = item.get("properties", {}).get("URL", {}).get("url", "")
                
                if not url:
                    logger.warning(f"Skipping item {item.get('id')} with no URL")
                    continue
                
                # Extract any other properties we might need
                properties = item.get("properties", {})
                title = self._extract_title(properties)
                
                # Build the result item
                result_item = {
                    "id": item.get("id"),
                    "url": url,
                    "title": title,
                    "properties": properties
                }
                
                results.append(result_item)
            
            logger.info(f"Found {len(results)} unprocessed links")
            return results
        
        except APIResponseError as e:
            logger.error(f"Notion API error when querying for unprocessed links: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when querying for unprocessed links: {e}")
            raise
    
    def mark_as_processed(self, item_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark an item as processed in the Notion database.
        
        Args:
            item_id (str): ID of the item to mark as processed
            metadata (Dict[str, Any], optional): Additional metadata to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Marking item {item_id} as processed")
        
        # First attempt to update with 'Done' status
        properties = {
            "Status": {
                "status": {
                    "name": "Done"
                }
            }
        }
        
        try:
            self.client.pages.update(
                page_id=item_id,
                properties=properties
            )
            logger.info(f"Successfully marked item {item_id} as processed with status 'Done'")
            return True
            
        except Exception as e:
            # Check if the error indicates an invalid status option
            error_msg = str(e)
            if "Invalid" in error_msg or "expected" in error_msg:
                logger.error(f"Status option 'Done' appears invalid: {error_msg}. Falling back to 'Not started'.")
                fallback_properties = {
                    "Status": {
                        "status": {
                            "name": "Not started"
                        }
                    }
                }
                try:
                    self.client.pages.update(
                        page_id=item_id,
                        properties=fallback_properties
                    )
                    logger.info(f"Successfully marked item {item_id} as processed with fallback status 'Not started'")
                    return True
                except Exception as inner_e:
                    logger.error(f"Fallback update failed for item {item_id}: {inner_e}")
                    return False
            else:
                logger.error(f"Unexpected error when marking item {item_id} as processed: {e}")
                return False
    
    def mark_as_failed(self, item_id: str, error_message: str) -> bool:
        """
        Mark an item as failed in the Notion database.
        
        Args:
            item_id (str): ID of the item to mark as failed
            error_message (str): Error message to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Marking item {item_id} as failed")
        
        try:
            # Prepare the properties to update based on the existing script's property names
            properties = {
                "Status": {
                    "status": {
                        "name": "Not started"  # Using a valid status value
                    }
                }
            }
            
            # Update the page
            self.client.pages.update(
                page_id=item_id,
                properties=properties
            )
            
            logger.info(f"Successfully marked item {item_id} as failed (status set to Not started)")
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error when marking item as failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when marking item as failed: {e}")
            return False
    
    def _extract_title(self, properties: Dict[str, Any]) -> str:
        """
        Extract the title from the properties.
        
        Args:
            properties (Dict[str, Any]): Properties object from Notion
            
        Returns:
            str: Extracted title or empty string
        """
        # Try to find a title property
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title" and prop_value.get("title"):
                title_parts = []
                for title_item in prop_value.get("title", []):
                    title_parts.append(title_item.get("text", {}).get("content", ""))
                return "".join(title_parts)
        
        # If no title property found, return empty string
        return ""
    
    def _extract_date(self, properties: Dict[str, Any], property_name: str) -> Optional[str]:
        """
        Extract a date from the properties.
        
        Args:
            properties (Dict[str, Any]): Properties object from Notion
            property_name (str): Name of the date property
            
        Returns:
            Optional[str]: Extracted date as ISO string or None
        """
        date_prop = properties.get(property_name, {})
        if date_prop.get("type") == "date" and date_prop.get("date"):
            return date_prop.get("date", {}).get("start")
        return None

# Create a singleton instance
notion = NotionIntegration()

def get_unprocessed_links(limit: int = 10, platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get unprocessed links from the Notion database.
    
    This is a convenience function that uses the singleton instance.
    
    Args:
        limit (int, optional): Maximum number of links to retrieve. Defaults to 10.
        platform (str, optional): If specified, directly use URL filtering to find links for this platform.
        
    Returns:
        List[Dict[str, Any]]: List of unprocessed links with their metadata
    """
    return notion.get_unprocessed_links(limit, platform)

def mark_as_processed(item_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Mark an item as processed in the Notion database.
    
    This is a convenience function that uses the singleton instance.
    
    Args:
        item_id (str): ID of the item to mark as processed
        metadata (Dict[str, Any], optional): Additional metadata to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    return notion.mark_as_processed(item_id, metadata)

def mark_as_failed(item_id: str, error_message: str) -> bool:
    """
    Mark an item as failed in the Notion database.
    
    This is a convenience function that uses the singleton instance.
    
    Args:
        item_id (str): ID of the item to mark as failed
        error_message (str): Error message to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    return notion.mark_as_failed(item_id, error_message)
