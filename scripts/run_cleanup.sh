#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/../.env" ]; then
    echo "Error: .env file not found at $SCRIPT_DIR/../.env"
    exit 1
fi

# Load environment variables from .env file
echo "Loading environment variables from .env"
set -a
source "$SCRIPT_DIR/../.env"
set +a

# Set up logging configuration
export LOG_LEVEL=DEBUG

# Print information about the environment
echo "Running cleanup script at $(date)"
echo "Working directory: $(pwd)"
echo "Python executable: $(which python)"
echo "UV executable: $(which uv)"

# Check if --dry-run flag is provided
if [ "$1" = "--dry-run" ]; then
    echo "Running in dry-run mode - no changes will be made"
    uv run python cleanup_output.py --dry-run
else
    echo "Running in normal mode - changes will be made"
    echo "To see what changes would be made without applying them, use: $0 --dry-run"
    uv run python cleanup_output.py
fi

echo "Cleanup completed at $(date)" 