#!/bin/bash
# Script to run the Process Saved Links application
# This script uses the new architecture with platform-specific processing

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
export LOG_LEVEL=INFO

# Ensure we're using the correct Python environment
VENV_PATH="$SCRIPT_DIR/.venv"

# Function to check if virtual environment should be refreshed
should_refresh_venv() {
    # Check if venv doesn't exist or is older than a day
    if [ ! -d "$VENV_PATH" ] || [ -n "$(find "$VENV_PATH" -maxdepth 0 -mtime +1)" ]; then
        return 0  # True, should refresh
    else
        return 1  # False, no need to refresh
    fi
}

# Refresh virtual environment if needed
if should_refresh_venv; then
    echo "Creating/refreshing virtual environment..."
    rm -rf "$VENV_PATH"
    uv venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
else
    echo "Using existing virtual environment"
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
    echo "Warning: GEMINI_API_KEY not set in .env file. Transcript generation may fail."
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

# Parse command line arguments
PLATFORM="all"
LIMIT=""
PARALLEL=""
CONTINUOUS=""

print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --platform PLATFORM  Platform to process (youtube, instagram, or all)"
    echo "  --limit N            Maximum number of links to process per platform"
    echo "  --parallel           Process platforms in parallel"
    echo "  --continuous         Run continuously until stopped"
    echo "  --help               Show this help message"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --parallel)
            PARALLEL="--parallel"
            shift
            ;;
        --continuous)
            CONTINUOUS="--continuous"
            shift
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Run the processor with the specified options
echo "Starting link processor with platform=$PLATFORM $PARALLEL $CONTINUOUS $LIMIT"
python process_links.py --platform "$PLATFORM" $PARALLEL $CONTINUOUS $LIMIT

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "Processing completed successfully"
else
    echo "Processing failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE 