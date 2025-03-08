#!/bin/bash
# Script to run the Process Saved Links application
# This script will be called by cron

# Navigate to the script directory
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Error: .env file not found at $SCRIPT_DIR/.env"
    exit 1
fi

# Load environment variables from .env file
echo "Loading environment variables from .env"
set -a
source "$SCRIPT_DIR/.env"
set +a

# Set up logging configuration
export LOG_LEVEL=DEBUG

# Ensure we're using the correct Python environment
VENV_PATH="$SCRIPT_DIR/.venv"

# Create virtual environment if it doesn't exist and install dependencies
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating new virtual environment..."
    uv venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
else
    source "$VENV_PATH/bin/activate"
fi

# Print information about the environment
echo "Running Process Saved Links at $(date)"
echo "Working directory: $(pwd)"
echo "Python executable: $(which python)"
echo "UV executable: $(which uv)"

# Check if required environment variables are set
if [ -z "$NOTION_API_TOKEN" ]; then
    echo "Error: NOTION_API_TOKEN not set in .env file"
    exit 1
fi

if [ -z "$NOTION_DATABASE_ID" ]; then
    echo "Error: NOTION_DATABASE_ID not set in .env file"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not set in .env file"
    exit 1
fi

# Check if offmute is installed
if ! command -v npx &> /dev/null; then
    echo "Error: npx command not found. Node.js may not be installed properly."
    exit 1
fi

# Check output directory
OUTPUT_DIR="/home/walub/Documents/Processed-ContentIdeas"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Function to process Instagram links
process_instagram_links() {
    echo "Processing Instagram links..."
    python run_instagram_post.py --limit 1
    
    # Wait for 15 minutes before processing the next link
    echo "Waiting 15 minutes before processing next link..."
    sleep 900  # 15 minutes = 900 seconds
}

# Main processing loop
while true; do
    echo "Starting new processing cycle at $(date)"
    process_instagram_links
done
