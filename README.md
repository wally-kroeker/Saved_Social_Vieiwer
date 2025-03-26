# Process Saved Links

A tool for processing saved links from various platforms and saving them to a local directory for future reference. Currently supports YouTube and Instagram links.

## Features

- Process YouTube videos: Download videos, generate transcripts, and save metadata
- Process Instagram posts: Download images, save captions, and metadata
- Integration with Notion database for tracking processed links
- Platform-specific settings (batch sizes, rate limiting, etc.)
- Parallel processing of different platforms
- Continuous processing mode
- Built-in content viewer for processed media

## Prerequisites

- Python 3.10 or higher
- Node.js (for offmute transcript generation)
- Notion API token and database ID
- Gemini API key (for transcript generation)

## Installation

1. Clone the repository
2. Install uv package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
4. Create a `.env` file with the required environment variables:
```
NOTION_API_TOKEN=your_notion_api_token
NOTION_DATABASE_ID=your_notion_database_id
GEMINI_API_KEY=your_gemini_api_key
```
5. Run the setup script:
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

# Interactive CLI (recommended)
./process_links_manager.sh
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

# Start the content viewer
./process_links_manager.sh viewer start

# Stop the content viewer
./process_links_manager.sh viewer stop
```

### Content Viewer

The project includes a built-in web-based viewer for processed content:

1. Start the viewer using one of these methods:
   - From the interactive CLI: Select option 7
   - From the command line: `./process_links_manager.sh viewer start`

2. Open your browser and navigate to: `http://localhost:8080`

3. Features of the viewer:
   - Browse all processed videos and content
   - Play videos directly in browser
   - View transcripts and metadata
   - Sort content by date or platform

4. Stop the viewer when done:
   - From the interactive CLI: Select option 8
   - From the command line: `./process_links_manager.sh viewer stop`

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
- **notion_integration.py**: Handles all Notion database operations
- **output_manager.py**: Manages output formatting and file organization

### Utility Scripts

- **fix_file_names.py**: Script for fixing file naming issues
- **cleanup_transcripts.py**: Cleanup script for transcript files
- **cleanup_files.py**: General file cleanup utility
- **check_notion_connection.py**: Test Notion API connectivity
- **check_instagram_connection.py**: Test Instagram API connectivity

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

```
.
├── run_process_links_v2.sh    # Main entry point script
├── process_links.py           # Core processing logic
├── process_links_manager.sh   # Interactive CLI interface
├── platform_processor.py      # Base platform processor
├── processor_factory.py       # Factory for creating processors
├── platform_config.py         # Platform-specific settings
├── notion_integration.py      # Notion API integration
├── output_manager.py          # Output formatting and management
├── config.py                  # Global configuration
├── processors/                # Platform-specific processors
├── utils/                     # Utility functions and helpers
├── docs/                      # Documentation
├── viewer/                    # Web-based content viewer
│   ├── server.py              # HTTP server for viewing content
│   └── videos.html            # Frontend for the viewer
├── output/                    # Processed content storage
├── tests/                     # Test suite
├── logs/                      # Log files
├── archive/                   # Archived/deprecated files
└── requirements.txt           # Python dependencies
```

### Key Components

- **platform_processor.py**: Handles platform-specific processing with appropriate settings
- **processor_factory.py**: Factory for creating processor instances
- **platform_config.py**: Configuration for platform-specific settings
- **process_links.py**: Main script for parallel processing
- **run_process_links_v2.sh**: Shell script for running the application
- **notion_integration.py**: Handles all Notion database operations
- **output_manager.py**: Manages output formatting and file organization

### Utility Scripts

- **fix_file_names.py**: Script for fixing file naming issues
- **cleanup_transcripts.py**: Cleanup script for transcript files
- **cleanup_files.py**: General file cleanup utility
- **check_notion_connection.py**: Test Notion API connectivity
- **check_instagram_connection.py**: Test Instagram API connectivity

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [Project Overview](docs/overview/project_overview.md) - High-level description and goals
- [Architecture](docs/overview/architecture.md) - System architecture and components
- [Requirements](docs/overview/requirements.md) - Detailed project requirements
- [Setup Guide](docs/development/setup_guide.md) - Setting up the development environment
- [Testing Guide](docs/development/testing_guide.md) - Testing procedures and guidelines

For a complete list of documentation, see the [Documentation Index](docs/overview/project_index.md).

## Development

### Environment Setup

The project uses `uv` as the package manager for better performance and dependency management. Make sure to always use `uv` when installing packages or running Python scripts:

```bash
# Install a new package
uv pip install package_name

# Run Python scripts
uv run python script.py

# Update dependencies
uv pip install -r requirements.txt
```

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