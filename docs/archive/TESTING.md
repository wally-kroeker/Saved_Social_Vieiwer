# Testing the Notion Integration Module

This document provides instructions for testing the Notion integration module of the Process Saved Links application.

## Prerequisites

- A Notion account with API access
- A Notion database with the following properties:
  - `URL` (URL type): Contains the links to process
  - `Processed` (Checkbox type): Indicates whether the link has been processed
  - `Added` (Date type): When the link was added
  - `Platform` (Select type): The platform of the link (e.g., Instagram, YouTube)
  - `Processed At` (Date type): When the link was processed
  - `Processing Error` (Rich Text type): Any error that occurred during processing

## Setup

1. **Create a Notion Integration**:
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Name it "Process Saved Links" (or any name you prefer)
   - Select the workspace where your database is located
   - Click "Submit"
   - Copy the "Internal Integration Token"

2. **Share the Database with the Integration**:
   - Open your Notion database
   - Click the "..." menu in the top-right corner
   - Click "Add connections"
   - Search for and select your integration
   - Click "Confirm"

3. **Get the Database ID**:
   - Open your Notion database in the browser
   - The URL will look like: `https://www.notion.so/workspace/databaseID?v=...`
   - Copy the `databaseID` part (it's a 32-character string with hyphens)

4. **Configure the Environment**:
   - Edit the `.env` file in the project root
   - Replace the placeholder values with your actual Notion API token and database ID:
     ```
     NOTION_API_TOKEN=your_actual_token_here
     NOTION_DATABASE_ID=your_actual_database_id_here
     ```

## Running the Tests

1. **Install Dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Run the Test Script**:
   ```bash
   ./run_test.sh
   ```
   
   Or directly with uv:
   ```bash
   uv run test_notion.py
   ```

3. **Test Results**:
   - The script will test connecting to the Notion API
   - It will retrieve unprocessed links from your database
   - If there are unprocessed links, it will ask if you want to mark one as processed

## Troubleshooting

- **API Token Issues**: Make sure your token is correct and the integration has access to the database
- **Database ID Issues**: Verify the database ID is correct
- **Database Structure Issues**: Ensure your database has the required properties
- **Permission Issues**: Make sure the integration has been shared with the database

## Manual Testing

You can also test the module manually in a Python shell:

```python
from notion_integration import NotionIntegration

# Initialize the integration
notion = NotionIntegration()

# Get unprocessed links
links = notion.get_unprocessed_links(limit=5)
print(f"Found {len(links)} unprocessed links")

# Mark a link as processed (if there are any)
if links:
    link_id = links[0]['id']
    metadata = {"platform": "test", "content_id": "test123"}
    success = notion.mark_as_processed(link_id, metadata)
    print(f"Marked as processed: {success}")
``` 