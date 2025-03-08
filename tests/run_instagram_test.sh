#!/bin/bash

# Run Instagram processor test script
# This script runs the Instagram processor test with a test URL
# and uses a temporary directory for output to avoid affecting production data

# Set up environment
source ~/.bashrc
cd "$(dirname "$0")/.."

# Default test URL if none provided
DEFAULT_URL="https://www.instagram.com/p/CxKxKxKxKxK/"
TEST_URL="${1:-$DEFAULT_URL}"

# Check for direct-only flag
DIRECT_ONLY=""
if [ "$2" == "--direct-only" ]; then
    DIRECT_ONLY="--direct-only"
    echo "Testing direct download only with URL: $TEST_URL"
else
    echo "Testing Instagram processor with URL: $TEST_URL"
fi

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv environment..."
    uv run python tests/test_instagram_processor.py "$TEST_URL" $DIRECT_ONLY
else
    echo "uv not found, using regular python..."
    python tests/test_instagram_processor.py "$TEST_URL" $DIRECT_ONLY
fi

# Check exit status
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
else
    echo "Test failed!"
    exit 1
fi 