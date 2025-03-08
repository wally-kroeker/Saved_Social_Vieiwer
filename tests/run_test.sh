#!/bin/bash

# Run the Notion integration test using uv
echo "Running Notion integration test using uv..."

# Change to the project root directory if script is run from another location
cd "$(dirname "$0")/.." || exit 1

# Run the test script
uv run tests/test_notion.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
else
    echo "Test failed. Please check the error messages above."
fi 