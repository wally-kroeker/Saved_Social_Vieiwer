#!/bin/bash
# Test script to process a new Instagram post and verify the new naming/organization scheme

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}=== Testing New Processing with FastAPI ====${NC}"
echo -e "${YELLOW}===============================================${NC}"

# Step 1: Clean the current temporary and old-format files
echo -e "${BLUE}Step 1: Cleaning up temporary and old-format files...${NC}"
find output -type f -not -path "*/instagram/*" -not -path "*/youtube/*" -delete
rm -rf output/instagram/transcription output/instagram/config.json output/instagram/instagram_*.json 2>/dev/null
rm -rf output/youtube/transcription output/youtube/config.json output/youtube/youtube_*.json 2>/dev/null
echo -e "${GREEN}Cleanup complete.${NC}"

# Step 2: Process a new Instagram post
echo -e "${BLUE}Step 2: Processing new Instagram post...${NC}"
./process_links_manager.sh instagram

# Step 3: List the output directory contents
echo -e "${BLUE}Step 3: Listing output directory contents...${NC}"
echo -e "${YELLOW}Instagram directory:${NC}"
ls -la output/instagram/
echo -e "${YELLOW}YouTube directory:${NC}"
ls -la output/youtube/

# Step 4: Clean up the extra files created by the processing
echo -e "${BLUE}Step 4: Cleaning up temporary files...${NC}"
rm -rf output/instagram/transcription output/instagram/config.json output/instagram/instagram_*.json 2>/dev/null
rm -rf output/youtube/transcription output/youtube/config.json output/youtube/youtube_*.json 2>/dev/null
echo -e "${GREEN}Extra files cleaned up.${NC}"

echo -e "${BLUE}Instagram directory after cleanup:${NC}"
ls -la output/instagram/

# Step 5: Restart the viewer with the FastAPI server
echo -e "${BLUE}Step 5: Restarting the viewer...${NC}"
./process_links_manager.sh viewer restart

echo -e "${GREEN}Test complete. Check the output above for any issues.${NC}"
echo -e "${BLUE}You can now access the viewer at http://localhost:8080${NC}" 