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
- Node.js 14+ and npm (for Offmute transcript generation)
- FFmpeg (for media processing and thumbnail generation)
- Notion API token and database ID
- Gemini API key (for transcript generation)

## Installation

### 1. Install System Dependencies

First, ensure you have the required system dependencies installed:

```bash
# Check Python version (should be 3.10+)
python3 --version

# Install Node.js 14+ using NVM (recommended method)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc  # or restart terminal
nvm install stable
nvm use stable
node --version  # Should be 14+

# Install FFmpeg
# On Ubuntu/Debian:
apt update
apt install ffmpeg
# On MacOS:
brew install ffmpeg
```

### 2. Install UV Package Manager

UV is a fast, reliable package manager for Python:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to your PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Install Offmute for Transcription

```bash
# Method 1: Install globally (may require permission fixes)
npm install -g offmute

# Method 2: Fix permission issues (if method 1 fails)
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
npm install -g offmute

# Verify installation
offmute --help
```

### 4. Set Up the Project

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Process_Saved_Links

# Create and activate virtual environment with UV
uv venv
source .venv/bin/activate

# Install Python dependencies
uv pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file with your API keys:

```bash
# Create .env file
cat > .env << EOF
# Notion API Configuration
NOTION_API_TOKEN=your_notion_api_token
NOTION_DATABASE_ID=your_notion_database_id

# API key used for offmute transcription
GEMINI_API_KEY=your_gemini_api_key
EOF

# Edit the file if needed
nano .env
```

### 6. Verify Installation

```bash
# Test Notion connection
uv run python check_notion_connection.py
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
   - Search and filter functionality

4. Stop or restart the viewer:
   - From the interactive CLI: Select option 8
   - From the command line: `./process_links_manager.sh viewer restart`

> **Note:** The viewer is being upgraded to use FastAPI for improved reliability and performance, especially when handling special characters in filenames. This change requires the standardized filename conventions described in the [Filename Conventions](#filename-conventions) section.

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

## Filename Conventions

The project follows a standardized naming convention for all output files, to ensure consistency and proper file handling:

### Standard Naming Pattern
```
{platform}-{username}-{date}-{sanitized_title}.{extension}
```

For example:
- `instagram-username-2025-03-26-post-title.mp4`
- `youtube-channelname-2025-03-25-video-title.jpg`

### Directory Structure
All content is organized into platform-specific subdirectories:
```
output/
├── instagram/  # Instagram content
└── youtube/    # YouTube content
```

### Important Notes for Developers
- **Special Characters:** Hashtags (`#`), spaces, and other special characters in titles are replaced with hyphens or underscores. This is crucial for proper URL handling in the viewer.
- **Consistent Extensions:** Each content item will have multiple associated files with the same base name but different extensions:
  - `.mp4` - Video content
  - `.jpg` - Thumbnail image
  - `.md` - Transcript
  - `.json` - Metadata
- **Breaking Changes:** Code that assumes the old naming format (`platform_id_filetype.ext`) will break with the new naming system.

### Migration
A migration utility is available in `utils/migrate_filenames.py` to convert existing files to the new naming convention:
```bash
# Show what would be migrated (dry run)
python -m utils.migrate_filenames --dry-run

# Migrate files for real
python -m utils.migrate_filenames
```

### Key Components

- **platform_processor.py**: Handles platform-specific processing with appropriate settings
- **processor_factory.py**: Factory for creating processor instances
- **platform_config.py**: Configuration for platform-specific settings
- **process_links.py**: Main script for parallel processing
- **run_process_links_v2.sh**: Shell script for running the application
- **notion_integration.py**: Handles all Notion database operations
- **output_manager.py**: Manages output formatting and file organization

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

## Troubleshooting Installation

### UV Installation Issues

If UV is installed but not found in your PATH:

```bash
# Add UV to your PATH
export PATH="$HOME/.local/bin:$PATH"

# Make it permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Node.js Version Issues

If Offmute fails with syntax errors, your Node.js version is likely too old:

```bash
# Check current version
node --version

# Install NVM (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc

# Install and use latest stable Node.js
nvm install stable
nvm use stable
```

### NPM Permission Issues

If you encounter permission errors with npm:

```bash
# Set up a user-local npm prefix
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Now install packages globally without sudo
npm install -g offmute
```

### Python Virtual Environment Issues

If you have issues with the virtual environment:

```bash
# Alternative way to create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies with pip if UV isn't working
pip install -r requirements.txt
```