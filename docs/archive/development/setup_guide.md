# Setup Guide

This guide provides instructions for setting up the development environment for the Process Saved Links project.

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Offmute)
- ffmpeg (for video processing)
- git
- A Notion account with API access
- API keys for required services

## Clone the Repository

```bash
git clone https://github.com/yourusername/Process_Saved_Links.git
cd Process_Saved_Links
```

## Environment Setup

### 1. Install uv

We use uv as our package manager:

```bash
# Install uv
curl -sSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | bash
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On Linux/macOS
source .venv/bin/activate
# On Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
uv pip install -r requirements.txt
```

### 4. Install Offmute

```bash
# Install Offmute globally
npm install -g offmute
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Notion API Configuration
NOTION_API_TOKEN=your_notion_api_token
NOTION_DATABASE_ID=your_notion_database_id

# Output Paths
OUTPUT_BASE_DIR=/home/walub/Documents/Processed-ContentIdeas
LOG_DIR=/home/walub/Documents/Processed-ContentIdeas/logs

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Scheduling
MORNING_RUN_TIME=08:00
NOON_RUN_TIME=12:00
EVENING_RUN_TIME=23:00
PROCESSING_PAUSE_MINUTES=15

# Processing Options
MAX_ITEMS_PER_RUN=10
```

## Notion Setup

### 1. Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "Process Saved Links" (or any name you prefer)
4. Select the workspace where your database is located
5. Click "Submit"
6. Copy the "Internal Integration Token" to the `.env` file

### 2. Set Up the Notion Database

1. Create a new database in Notion with the following properties:
   - `URL` (URL type): Contains the links to process
   - `Processed` (Checkbox type): Indicates whether the link has been processed
   - `Added` (Date type): When the link was added
   - `Platform` (Select type): The platform of the link (e.g., Instagram, YouTube)
   - `Processed At` (Date type): When the link was processed
   - `Processing Error` (Rich Text type): Any error that occurred during processing

2. Share the database with your integration:
   - Open your Notion database
   - Click the "..." menu in the top-right corner
   - Click "Add connections"
   - Search for and select your integration
   - Click "Confirm"

3. Get the Database ID:
   - Open your Notion database in the browser
   - The URL will look like: `https://www.notion.so/workspace/databaseID?v=...`
   - Copy the `databaseID` part to the `.env` file

## Output Directory Setup

Create the necessary output directories:

```bash
mkdir -p /home/walub/Documents/Processed-ContentIdeas/instagram
mkdir -p /home/walub/Documents/Processed-ContentIdeas/youtube
mkdir -p /home/walub/Documents/Processed-ContentIdeas/logs
```

## Install External Dependencies

### 1. FFmpeg

FFmpeg is required for video processing:

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# On macOS with Homebrew
brew install ffmpeg

# On Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

### 2. yt-dlp

yt-dlp is required for YouTube video downloading:

```bash
# Install using pip
uv pip install yt-dlp
```

## Verify Installation

Run the following tests to verify your setup:

```bash
# Test the configuration loading
uv run python -c "from config import load_config; print(load_config())"

# Test the Notion integration
uv run python -m tests.test_notion_integration

# Test Offmute installation
npx offmute --help
```

## Development Workflow

1. **Activate the Virtual Environment**:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

2. **Run Tests**:
   ```bash
   uv run python -m tests.test_notion_integration
   ```

3. **Run the Application in Development Mode**:
   ```bash
   # Run with dry-run mode (no actual processing)
   uv run python main.py --dry-run
   
   # Run with a limited number of items
   uv run python main.py --limit 1
   
   # Run normally
   uv run python main.py
   ```

## Troubleshooting

### Common Issues and Solutions

1. **Notion API Connection Issues**:
   - Verify your API token is correct
   - Ensure the integration has access to the database
   - Check your network connection

2. **Offmute Installation Problems**:
   - Make sure Node.js and npm are up to date
   - Try reinstalling: `npm uninstall -g offmute && npm install -g offmute`
   - Check for error messages in the npm log

3. **Permission Issues**:
   - Ensure you have write permissions to the output directories
   - Check file ownership and permissions

4. **Import Errors**:
   - Make sure you're running from the project root
   - Verify that the virtual environment is activated
   - Check that all dependencies are installed

## Related Documentation

- [Testing Guide](./testing_guide.md) - Testing procedures and guidelines
- [Implementation Guide](../implementation/implementation_guide.md) - Implementation details 