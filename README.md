# Process Saved Links

A system for automatically processing saved social media links from Instagram, YouTube, and other platforms.

## Overview

Process Saved Links automates the workflow of downloading, processing, and organizing content from various social media platforms. It helps users save and reference interesting or useful content for later analysis or repurposing.

### Key Features

- **Multi-Platform Support**: Process content from Instagram, YouTube, and potentially other platforms
- **Automated Processing**: Schedule automatic runs to process new content
- **Content Transcription**: Generate transcripts for video content using Offmute
- **Structured Organization**: Store processed content in a standardized directory structure
- **Notion Integration**: Use Notion as a database for tracking and managing links

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Offmute)
- ffmpeg (for video processing)
- Notion account with API access
- API keys for required services

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Process_Saved_Links.git
cd Process_Saved_Links

# Install uv
curl -sSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | bash

# Create a virtual environment
uv venv
source .venv/bin/activate  # On Linux/macOS

# Install dependencies
uv pip install -r requirements.txt

# Install Offmute
npm install -g offmute

# Set up environment variables (copy from template)
cp .env.example .env
# Edit .env with your API keys and configuration
```

For complete setup instructions, see the [Setup Guide](docs/development/setup_guide.md).

### Basic Usage

```bash
# Run with dry-run mode (no actual processing)
uv run python main.py --dry-run

# Run with a limited number of items
uv run python main.py --limit 1

# Run normally
uv run python main.py
```

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