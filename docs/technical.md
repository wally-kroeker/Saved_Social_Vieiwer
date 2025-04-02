# Technical Documentation

## Development Environment

### Core Technologies
- **Python 3.10+**: Primary programming language
- **UV Package Manager**: For dependency management and virtual environments
- **FFmpeg**: Media conversion and thumbnail generation
- **Node.js & npm**: Required for Offmute transcription tool
- **Bash**: For operational scripts and command-line interface

### Platforms and APIs
- **Notion API**: For database integration and status tracking
- **YouTube**: Content source via yt-dlp
- **Instagram**: Content source via Instaloader
- **Gemini API**: For AI-assisted transcript generation

### Key Libraries
- **yt-dlp**: YouTube video downloading
- **Instaloader**: Instagram content downloading
- **Offmute**: AI-based video/audio transcription
- **FastAPI**: Backend for the content viewer
- **Jinja2**: HTML templating for the viewer interface
- **Uvicorn**: ASGI server for the content viewer

## System Architecture

The system follows a modular architecture with several key components:

### Core Components
1. **Processor Factory**: Creates platform-specific processors based on URL type
2. **Platform Processors**: Handle platform-specific processing logic
   - Base Processor: Abstract class defining common interface
   - YouTube Processor: YouTube-specific implementation
   - Instagram Processor: Instagram-specific implementation
3. **Notion Integration**: Manages interaction with Notion database
4. **Platform Config**: Configures platform-specific settings
5. **Process Links Manager**: Main orchestration script

### Supporting Components
1. **Output Manager**: Handles standardized file output
2. **Utility Modules**: Common functionality across the system
3. **Content Viewer**: FastAPI-based web interface for viewing processed content

## Development Setup

### Required System Dependencies

Before setting up the project, the following system dependencies must be installed:

1. **Python 3.10+**: Required for running the application
   ```bash
   # Check current version
   python3 --version
   
   # Install if needed (may require sudo)
   apt install python3 python3-pip python3-venv
   ```

2. **Node.js and npm**: Required for Offmute transcription tool
   ```bash
   # Check current versions
   node --version
   npm --version
   
   # Install if needed (may require sudo)
   apt install nodejs npm
   ```

3. **FFmpeg**: Required for media processing
   ```bash
   # Check if installed
   ffmpeg -version
   
   # Install if needed (may require sudo)
   apt install ffmpeg
   ```

### Installation

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd Process_Saved_Links

# Set up environment with UV
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Install Offmute globally
npm install -g offmute

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Verifying Installation

After installation, verify that all components are working correctly:

```bash
# Test Python environment
uv run python -c "import sys; print(sys.version)"

# Test Node.js and npm
node --version
npm --version

# Test FFmpeg
ffmpeg -version

# Test Offmute
offmute --version

# Test Notion connection
uv run python check_notion_connection.py
```

### Required External Tools

```bash
# Install FFmpeg
sudo apt update
sudo apt install ffmpeg

# Install Node.js and Offmute for transcription
sudo apt install nodejs npm
npm install -g offmute
```

### Configuration

The system uses multiple configuration mechanisms:

1. **Environment Variables** (.env file):
   - `NOTION_API_TOKEN`: Notion API token
   - `NOTION_DATABASE_ID`: ID of the Notion database
   - `GEMINI_API_KEY`: Google Gemini API key for transcription

2. **Platform Configuration** (platform_config.py):
   - Batch sizes for each platform
   - Rate limiting delays
   - Platform-specific processing options

3. **Global Configuration** (config.py):
   - Output directory paths
   - File format settings
   - General system settings

## Data Flow

1. **Input**: Links stored in Notion database with "Not started" status
2. **Processing**:
   - Notion Integration retrieves unprocessed links
   - Platform Processor filters links for the specific platform
   - Factory creates appropriate processor for each link
   - Processor downloads, processes, and saves content
3. **Output**:
   - Standardized files saved to output directory
   - Notion database updated with processing status
4. **Viewing**:
   - FastAPI server provides web interface
   - Processed content displayed in organized format

## File Structure

The system organizes content in a standardized format:

```
/Processed-ContentIdeas/
├── channel1-date-video_title.mp4       # Video file
├── channel1-date-video_title.jpg       # Thumbnail
├── channel1-date-video_title.md        # Transcript
├── channel1-date-video_title.json      # Metadata
└── ...
```

## Error Handling

The system implements several error handling strategies:

1. **Graceful Failure**: Individual processing failures don't affect the entire batch
2. **Status Tracking**: Failed items marked appropriately in Notion
3. **Logging**: Comprehensive logging system for debugging
4. **Rate Limiting**: Configurable delays between requests to avoid API rate limits
5. **Retry Logic**: For transient network issues

## Testing

The system includes several testing utilities:

1. **Connection Checkers**: Test connectivity to external services
   - check_notion_connection.py
   - check_instagram_connection.py
2. **Cleanup Utilities**: Manage test outputs
   - cleanup_files.py
   - cleanup_transcripts.py

## Performance Considerations

1. **Batch Processing**: Configurable batch sizes for each platform
2. **Parallel Processing**: Support for processing different platforms in parallel
3. **Rate Limiting**: Configurable delays to respect API limits
4. **Continuous Mode**: Option for ongoing processing until all items complete

## Security Considerations

1. **API Token Management**: Environment variables for sensitive tokens
2. **Secure Logging**: No sensitive information in logs
3. **Local Storage**: Content stored locally for privacy
