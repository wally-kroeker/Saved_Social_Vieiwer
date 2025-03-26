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

# Remove existing environment if it exists
if [ -d "$VENV_PATH" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_PATH"
fi

# Create fresh virtual environment and install dependencies
echo "Creating new virtual environment..."
uv venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
echo "Installing dependencies..."
uv pip install -r requirements.txt

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
    
    # Wait for 15 minutes before next Instagram processing to avoid rate limiting
    echo "Waiting 15 minutes before processing next Instagram link..."
    sleep 900  # 15 minutes = 900 seconds
}

# Function to process YouTube links
process_youtube_links() {
    echo "========== Processing YouTube links ==========="
    # Process all available YouTube links
    local processed_count=0
    local max_attempts=10  # Prevent infinite loops if something goes wrong
    
    for ((i=1; i<=max_attempts; i++)); do
        echo "YouTube processing attempt $i of $max_attempts"
        python run_youtube_post.py --limit 1
        exit_code=$?
        
        echo "YouTube processor exit code: $exit_code"
        
        if [ $exit_code -eq 0 ]; then
            echo "Successfully processed a YouTube link"
            processed_count=$((processed_count + 1))
        elif [ $exit_code -eq 1 ]; then
            echo "No more YouTube links to process"
            break
        else
            echo "Error occurred while processing YouTube links (exit code: $exit_code)"
            break
        fi
    done
    
    echo "Processed $processed_count YouTube links"
    echo "========== YouTube processing complete ==========="
}

# Main processing loop
while true; do
    echo "==============================================="
    echo "Starting new processing cycle at $(date)"
    echo "==============================================="
    
    # First, process all YouTube links
    process_youtube_links
    
    # Then process Instagram links (with rate limit)
    process_instagram_links
done
