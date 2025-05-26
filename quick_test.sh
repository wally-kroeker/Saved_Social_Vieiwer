#!/bin/bash
# Script to quickly build the V2 viewer, restart the server, and provide test link.

set -e # Exit immediately if a command exits with a non-zero status.

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the absolute path of the directory where the script resides
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

VIEWER_V2_DIR="${PROJECT_ROOT}/viewer/Updated-Viewer"
MANAGER_SCRIPT="${PROJECT_ROOT}/process_links_manager.sh"
TEST_URL="http://10.10.10.29:8080/v2"

echo -e "${YELLOW}--- Starting Quick Test Workflow ---${NC}"

# 1. Build V2 Viewer
echo -e "\n${YELLOW}[Step 1/3] Building V2 viewer...${NC}"
if [ -d "$VIEWER_V2_DIR" ]; then
  cd "$VIEWER_V2_DIR"
  echo "Running 'bun run build' in $(pwd)"
  bun run build
  echo -e "${GREEN}V2 viewer build complete.${NC}"
else
  echo -e "${RED}Error: V2 Viewer directory not found at ${VIEWER_V2_DIR}${NC}"
  exit 1
fi

# 2. Navigate back and Restart Server
echo -e "\n${YELLOW}[Step 2/3] Restarting FastAPI server...${NC}"
cd "$PROJECT_ROOT" # Ensure we are in the project root
if [ -f "$MANAGER_SCRIPT" ]; then
  echo "Running '$MANAGER_SCRIPT viewer restart'"
  "$MANAGER_SCRIPT" viewer restart
  # Note: Restart happens in the background, script continues immediately
  echo -e "${GREEN}Server restart command issued.${NC}"
else
  echo -e "${RED}Error: Manager script not found at ${MANAGER_SCRIPT}${NC}"
  exit 1
fi

# 3. Provide Test Link
echo -e "\n${YELLOW}[Step 3/3] Ready for Testing!${NC}"
echo -e "--------------------------------------------------"
echo -e "Click the link below to open the V2 Viewer:"
echo -e "${BLUE}${TEST_URL}${NC}"
echo -e "--------------------------------------------------"

echo -e "\n${GREEN}--- Quick Test Workflow Finished ---${NC}"

exit 0 