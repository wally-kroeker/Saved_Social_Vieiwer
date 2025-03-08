#!/bin/bash
# Run the production flow test with proper environment setup

# Ensure we're in the right directory
cd "$(dirname "$0")/.." || exit 1

# Set up colored output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing production flow with Instagram links from Notion${NC}"

# Check for URL argument
URL_ARG=""
DRY_RUN=""
NO_NOTION=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url=*)
      URL_ARG="--url=${1#*=}"
      shift
      ;;
    --url)
      URL_ARG="--url=$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="--dry-run"
      shift
      ;;
    --no-notion)
      NO_NOTION="--no-notion"
      shift
      ;;
    *)
      # If it's not a recognized option, assume it's a URL
      if [[ $1 == http* ]]; then
        URL_ARG="--url=$1"
      fi
      shift
      ;;
  esac
done

echo "Using uv environment..."
if command -v uv &> /dev/null; then
    uv run python -m tests.test_production_flow $URL_ARG $DRY_RUN $NO_NOTION
    EXIT_CODE=$?
else
    echo -e "${RED}uv not found, falling back to regular Python${NC}"
    python -m tests.test_production_flow $URL_ARG $DRY_RUN $NO_NOTION
    EXIT_CODE=$?
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Production test completed successfully!${NC}"
else
    echo -e "${RED}Production test failed with exit code $EXIT_CODE${NC}"
fi

exit $EXIT_CODE 