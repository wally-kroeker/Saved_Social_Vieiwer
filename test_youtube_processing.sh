#!/bin/bash
# Test script to process a new YouTube video and verify the new naming/organization scheme

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}======= Testing YouTube Processing ============${NC}"
echo -e "${YELLOW}===============================================${NC}"

# Step 1: Debug the Notion database to find YouTube links
echo -e "${BLUE}Step 1: Checking for YouTube links in Notion...${NC}"
echo -e "${YELLOW}Query all links with 'Not Started' status:${NC}"
curl -s -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer $NOTION_API_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/databases/14d30fb596b98018bfeff81fa55eccb6/query \
     -d '{"filter": {"property": "Status", "status": {"equals": "Not Started"}}}' \
     | grep -o 'https://[^"]*youtube[^"]*' | head -n 10

echo -e "\n${YELLOW}Running a test to verify YouTube URL matching:${NC}"
python3 -c "from processors.youtube_processor import YouTubeProcessor; p = YouTubeProcessor(); print('Can process:', p.can_process('https://youtube.com/watch?v=PjuOsM3W3G8&si=iGJeIrdAF2rHCl2q'))"

# Step 2: Clean the current temporary and old-format files
echo -e "\n${BLUE}Step 2: Cleaning up temporary and old-format files...${NC}"
find output -type f -not -path "*/instagram/*" -not -path "*/youtube/*" -delete
rm -rf output/youtube/transcription output/youtube/config.json output/youtube/youtube_*.json 2>/dev/null
echo -e "${GREEN}Cleanup complete.${NC}"

# Step 3: Process a new YouTube video
echo -e "${BLUE}Step 3: Processing new YouTube video...${NC}"
./process_links_manager.sh youtube

# Step 4: List the output directory contents
echo -e "${BLUE}Step 4: Listing output directory contents...${NC}"
echo -e "${YELLOW}YouTube directory:${NC}"
ls -la output/youtube/

# Step 5: Clean up the extra files created by the processing
echo -e "${BLUE}Step 5: Cleaning up temporary files...${NC}"
rm -rf output/youtube/transcription output/youtube/config.json output/youtube/youtube_*.json 2>/dev/null
echo -e "${GREEN}Extra files cleaned up.${NC}"

echo -e "${BLUE}YouTube directory after cleanup:${NC}"
ls -la output/youtube/

echo -e "${GREEN}Test complete. Check the output above for any issues.${NC}" 