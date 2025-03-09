# Project Context: Process Saved Links

## Product Overview
This project automates the process of downloading, processing, and organizing content from various social media platforms. It streamlines the workflow of saving interesting or useful content from platforms like Instagram and YouTube for later reference, analysis, or repurposing.

### Problems Solved
1. **Content Preservation**: Saves social media content that might otherwise be lost or difficult to find later
2. **Automated Processing**: Eliminates manual downloading and processing of content
3. **Organized Storage**: Creates a structured system for storing and accessing saved content
4. **Content Accessibility**: Makes content available offline and in standardized formats
5. **Searchable Archive**: Enables easy searching and browsing of saved content

## Technical Architecture

### Core Components
1. **Core Scheduler**: Manages scheduling and execution of the processing pipeline
2. **Notion Integration**: Handles communication with the Notion database
3. **Platform Processors**: Modular components for processing different social media platforms
4. **Output Manager**: Standardizes output formatting and storage

### System Flow
1. Core Scheduler initiates the process at scheduled times
2. Notion Integration retrieves unprocessed links
3. For each link:
   - Determine the appropriate Platform Processor
   - Process the content
   - Generate standardized outputs
   - Update the Notion database
   - Wait 15 minutes before processing the next link

### File Structure
```
Process_Saved_Links/
├── main.py                     # Entry point and scheduler
├── config.py                   # Configuration settings
├── notion_integration.py       # Notion database operations
├── output_manager.py           # Output standardization
├── processors/                 # Platform-specific processors
│   ├── base_processor.py       # Base class with common functionality
│   ├── instagram_processor.py  # Instagram-specific processing
│   ├── youtube_processor.py    # YouTube-specific processing
│   └── tiktok_processor.py     # Future platform (template)
├── utils/                      # Utility functions
│   ├── logging_utils.py        # Logging setup
│   └── file_utils.py           # File operations
└── scripts/                    # External scripts
    ├── download_post.sh        # Existing Instagram download script
    └── offmute.py              # Script for processing audio
```

## Technical Stack

### Core Technologies
- **Python 3.x**: Primary programming language
- **Notion API**: For database integration
- **Bash Scripts**: For some platform-specific operations
- **Cron**: For scheduling automated runs

### External Dependencies
- **notion-client**: Python client for Notion API
- **yt-dlp**: For downloading YouTube videos
- **offmute**: For processing video audio
- **ffmpeg**: For video and audio processing
- **markdown**: For generating transcript files

### Development Tools
- **Virtual Environment**: For dependency management
- **Logging**: For tracking execution and debugging

## Implementation Status

### Completed Features
- Existing Instagram link processing system
- Notion database integration for tracking links
- Output directory structure
- Viewer interface for processed content
- Notion integration module with testing framework
- Offmute integration for video transcription (using .env config)

### In Progress
- Modular architecture for the new system
- Refactored Instagram processor module
- YouTube processor module
- Core scheduler with 15-minute pauses
- Automated execution (3 times daily)
- Template for adding new platforms
- Comprehensive documentation

### Recent Fixes
1. **Offmute API Integration Fix**
   - Updated API URL to `https://api.gemini-offmute.com/v1`
   - Implemented robust fallback mechanism
   - Added better error handling and logging

2. **Notion Integration Fix**
   - Fixed method naming mismatch
   - Updated status update methods
   - Enhanced error handling

## Technical Requirements

### Platform-Specific Requirements
1. **Instagram Processing**
   - Download videos
   - Generate metadata
   - Create standardized outputs

2. **YouTube Processing**
   - Download videos using yt-dlp
   - Process audio using offmute
   - Generate MP4 video output
   - Create thumbnail JPG
   - Generate markdown transcript
   - Follow same naming convention as Instagram videos

### System Requirements
1. **Scheduling**
   - Run 3 times daily (morning, noon, 11:00 PM)
   - Ensure proper error handling for unattended execution
   - Log all activities for monitoring

2. **Performance**
   - Handle resource-intensive video processing
   - Maintain 15-minute pauses between items
   - Prevent scheduling overlaps

3. **Security**
   - Secure storage of API tokens
   - No exposure of sensitive information in logs

## Next Steps
1. Complete YouTube processor implementation
2. Test full end-to-end processing with actual Notion database
3. Create comprehensive documentation for system usage
4. Implement monitoring system for processing statistics
5. Prepare for future platform additions 