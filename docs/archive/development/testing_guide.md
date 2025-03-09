# Testing Guide

This guide provides instructions for testing the various components of the Process Saved Links system.

## Testing Philosophy

The testing approach for this project follows these principles:

1. **Component-Level Testing**: Test individual components in isolation
2. **Integration Testing**: Test interactions between components
3. **End-to-End Testing**: Test the complete processing pipeline
4. **Dry-Run Mode**: Test without affecting production data

## Testing Requirements

- Python 3.x with uv package manager
- Notion account with API access
- API keys for required services
- Test media files for content processing

## Testing the Notion Integration

### Prerequisites

- A Notion account with API access
- A Notion database with the following properties:
  - `URL` (URL type): Contains the links to process
  - `Processed` (Checkbox type): Indicates whether the link has been processed
  - `Added` (Date type): When the link was added
  - `Platform` (Select type): The platform of the link (e.g., Instagram, YouTube)
  - `Processed At` (Date type): When the link was processed
  - `Processing Error` (Rich Text type): Any error that occurred during processing

### Setup

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

### Running the Tests

```bash
# Using the test script
./run_test.sh

# Or directly with uv
uv run python -m tests.test_notion_integration
```

## Testing the Instagram Processor

### Prerequisites

- Instagram processor configured
- Test Instagram posts (public posts recommended for testing)
- Offmute configured with API key

### Running the Tests

```bash
# Run the Instagram processor test
uv run python -m tests.test_instagram_processor

# Test with a specific Instagram URL
uv run python -m tests.test_instagram_processor --url https://www.instagram.com/p/EXAMPLE/

# Test with a dry run (no actual processing)
uv run python -m tests.test_instagram_processor --dry-run
```

## Testing the YouTube Processor

### Prerequisites

- YouTube processor configured
- Test YouTube videos (public videos recommended for testing)
- yt-dlp installed and configured
- Offmute configured with API key

### Running the Tests

```bash
# Run the YouTube processor test
uv run python -m tests.test_youtube_processor

# Test with a specific YouTube URL
uv run python -m tests.test_youtube_processor --url https://www.youtube.com/watch?v=EXAMPLE

# Test with a dry run (no actual processing)
uv run python -m tests.test_youtube_processor --dry-run
```

## Testing the Offmute Integration

### Prerequisites

- Offmute installed (via npm)
- Gemini API key configured in the `.env` file
- Test video file

### Running the Tests

```bash
# Test the Offmute API integration
uv run python -m tests.test_offmute --api

# Test the Offmute CLI fallback
uv run python -m tests.test_offmute --cli

# Test with a specific video file
uv run python -m tests.test_offmute --file path/to/test/video.mp4
```

## End-to-End Testing

### Prerequisites

- All components configured
- Test links in the Notion database
- All required API keys configured

### Running the Tests

```bash
# Run the full end-to-end test with dry run mode
uv run python -m tests.test_production_flow --dry-run

# Run the full end-to-end test with a single item
uv run python -m tests.test_production_flow --limit 1

# Run the full end-to-end test with real processing
uv run python -m tests.test_production_flow
```

## Troubleshooting Common Issues

### Notion Integration Issues

- **API Token Issues**: Make sure your token is correct and the integration has access to the database
- **Database ID Issues**: Verify the database ID is correct
- **Database Structure Issues**: Ensure your database has the required properties
- **Permission Issues**: Make sure the integration has been shared with the database

### Instagram Processor Issues

- **Download Failures**: Verify the URL is valid and the content is public or accessible
- **Processing Errors**: Check that ffmpeg is installed and accessible
- **Transcription Errors**: Verify the Offmute API key and connection

### YouTube Processor Issues

- **Download Failures**: Verify that yt-dlp is installed and configured correctly
- **Processing Errors**: Check that ffmpeg is installed and accessible
- **Transcription Errors**: Verify the Offmute API key and connection

### Offmute Issues

- **API Connection Errors**: Verify the API key and network connection
- **CLI Execution Errors**: Ensure Offmute is installed via npm
- **Timeout Errors**: Consider increasing timeout values for larger files

## Manual Testing

You can also test components manually in a Python shell:

### Testing Notion Integration

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

### Testing Platform Processors

```python
from processors.instagram_processor import InstagramProcessor
from config import load_config

# Load configuration
config = load_config()

# Initialize processor
processor = InstagramProcessor(config)

# Process a link
url = "https://www.instagram.com/p/EXAMPLE/"
success, result = processor.process({"url": url, "id": "test123"})
print(f"Processing result: {success}")
```

## Related Documentation

- [Setup Guide](./setup_guide.md) - Setting up the development environment
- [Implementation Guide](../implementation/implementation_guide.md) - Implementation details 