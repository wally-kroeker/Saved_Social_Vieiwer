# Process Saved Links

A tool for processing saved links from various platforms and saving them to a local directory for future reference. Currently supports YouTube and Instagram links.

## Features

- Process YouTube videos: Download videos, generate transcripts, and save metadata
- Process Instagram posts: Download images, save captions, and metadata
- Integration with Notion database for tracking processed links
- Platform-specific settings (batch sizes, rate limiting, etc.)
- Parallel processing of different platforms
- Continuous processing mode

## Prerequisites

- Python 3.10 or higher
- Node.js (for offmute transcript generation)
- Notion API token and database ID
- Gemini API key (for transcript generation)

## Installation

1. Clone the repository
2. Create a `.env` file with the required environment variables:
```
NOTION_API_TOKEN=your_notion_api_token
NOTION_DATABASE_ID=your_notion_database_id
GEMINI_API_KEY=your_gemini_api_key
```
3. Run the setup script:
```bash
./run_process_links_v2.sh
```

## Usage

### Basic Usage

```bash
# Process all platforms sequentially
./run_process_links_v2.sh

# Process only YouTube links
./run_process_links_v2.sh --platform youtube

# Process only Instagram links
./run_process_links_v2.sh --platform instagram
```

### Advanced Options

```bash
# Process platforms in parallel
./run_process_links_v2.sh --parallel

# Process continuously until stopped
./run_process_links_v2.sh --continuous

# Process a specific number of links per platform
./run_process_links_v2.sh --limit 5

# Combine options
./run_process_links_v2.sh --platform youtube --limit 5 --parallel --continuous
```

### Notion Database Structure

The Notion database must have the following properties:
- **URL**: URL of the link to process
- **Status**: Status of the processing (Not started, Processed, etc.)
- **Name**: Title of the content

## Architecture

### Key Components

- **platform_processor.py**: Handles platform-specific processing with appropriate settings
- **processor_factory.py**: Factory for creating processor instances
- **platform_config.py**: Configuration for platform-specific settings
- **process_links.py**: Main script for parallel processing
- **run_process_links_v2.sh**: Shell script for running the application

### Processing Flow

1. Fetch unprocessed links from Notion database
2. Filter links by platform type
3. Process each link using the appropriate processor
4. Update the Notion database with the processing status
5. Apply platform-specific delays between batches

## Troubleshooting

### Common Issues

- **Notion API errors**: Check that your Notion API token and database ID are correct
- **Transcript generation failures**: Ensure that Gemini API key is set correctly
- **Rate limiting**: If experiencing rate limiting, adjust the delay settings in platform_config.py

## Project Structure

The project follows a modular architecture:

- **Core Scheduler**: Manages scheduling and execution
- **Notion Integration**: Handles Notion database operations
- **Platform Processors**: Process content from specific platforms
- **Output Manager**: Standardizes output formatting

For detailed information, see the [Architecture Documentation](docs/overview/architecture.md).

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [Project Overview](docs/overview/project_overview.md) - High-level description and goals
- [Architecture](docs/overview/architecture.md) - System architecture and components
- [Requirements](docs/overview/requirements.md) - Detailed project requirements
- [Setup Guide](docs/development/setup_guide.md) - Setting up the development environment
- [Testing Guide](docs/development/testing_guide.md) - Testing procedures and guidelines

For a complete list of documentation, see the [Documentation Index](docs/overview/project_index.md).

## Development

### Testing

```bash
# Test the Notion integration
uv run python -m tests.test_notion_integration

# Test the Instagram processor
uv run python -m tests.test_instagram_processor

# Test the YouTube processor
uv run python -m tests.test_youtube_processor

# Run end-to-end tests
uv run python -m tests.test_production_flow --dry-run
```

For complete testing instructions, see the [Testing Guide](docs/development/testing_guide.md).

## License

[MIT License](LICENSE)

## Acknowledgments

- [Offmute](https://github.com/offmute/offmute) for transcription capabilities
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading
- [Notion API](https://developers.notion.com/) for database integration