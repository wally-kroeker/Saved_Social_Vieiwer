#!/usr/bin/env python3
"""
Check available links in the Notion database.
"""
from notion_integration import NotionIntegration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
notion_token = os.environ.get('NOTION_API_TOKEN')
notion_database_id = os.environ.get('NOTION_DATABASE_ID')

if not notion_token or not notion_database_id:
    print("Missing Notion credentials in environment variables")
    exit(1)

notion = NotionIntegration(notion_token, notion_database_id)

# Get unprocessed links
links = notion.get_unprocessed_links(limit=10)

print(f"Found {len(links)} unprocessed links:")
for i, link in enumerate(links):
    url = link.get("url", "No URL")
    title = link.get("title", "No Title")
    platform = link.get("platform", "Unknown Platform")
    
    print(f"{i+1}. {platform}: {title}")
    print(f"   URL: {url}")
    print("") 