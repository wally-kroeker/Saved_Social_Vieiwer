# Process Saved Links: Project Summary

## Project Overview

The Process Saved Links project aims to create a unified solution for processing saved social media links from various platforms. It builds upon an existing Instagram link processing system, adding support for YouTube videos and creating a modular, extensible architecture that can be easily expanded to support additional platforms in the future.

## Key Requirements

1. **Refactor Existing Functionality**:
   - Update the existing process_notion_links.py script
   - Increase pause time between downloads to 15 minutes (from 5 minutes)

2. **Add YouTube Processing**:
   - Download YouTube videos
   - Process videos through offmute for audio enhancement
   - Generate MP4 video output
   - Create thumbnail JPG
   - Generate markdown transcript

3. **Standardize Output**:
   - Ensure YouTube output follows the same naming format as Instagram videos
   - Place processed content in the same output folder

4. **Automate Execution**:
   - Run the system 3 times daily (morning, noon, and 11:00 PM)
   - Implement proper scheduling and error handling

5. **Create Extensible Architecture**:
   - Design a modular system that can be extended to other platforms
   - Make the solution templateable for platforms like TikTok

## Architecture Overview

The system follows a modular architecture with these key components:

1. **Core Scheduler**: Manages execution timing and flow
2. **Notion Integration**: Handles database operations
3. **Platform Processors**: Modular components for different platforms
4. **Output Manager**: Standardizes output formatting

### Component Relationships

```
                                  ┌─────────────┐
                                  │    main.py  │
                                  └──────┬──────┘
                                         │
                 ┌────────────────┬──────┴───────┬────────────────┐
                 │                │              │                │
        ┌─────────────────┐ ┌───────────┐ ┌────────────┐ ┌────────────────┐
        │ config.py       │ │ scheduler │ │ notion_    │ │ output_        │
        └─────────────────┘ └─────┬─────┘ │ integration│ │ manager        │
                                  │       └──────┬─────┘ └────────┬───────┘
                                  │              │                │
                                  │       ┌──────┴─────┐          │
                                  │       │ Notion DB  │          │
                                  │       └────────────┘          │
                                  │                               │
                         ┌────────┴───────────┐                   │
                         │                    │                   │
                ┌────────┴─────────┐ ┌────────┴─────────┐         │
                │ Instagram        │ │ YouTube          │         │
                │ Processor        │ │ Processor        │         │
                └──────────────────┘ └──────────────────┘         │
                         │                    │                   │
                         │                    │                   │
                         └──────────┬─────────┘                   │
                                    │                             │
                                    │         ┌───────────────────┘
                                    │         │
                                    ▼         ▼
                              ┌─────────────────────┐
                              │ Processed Content   │
                              │ Directory           │
                              └─────────────────────┘
```

## Implementation Plan

The implementation is divided into four phases:

### Phase 1: Project Setup and Refactoring (1-2 days)
- Create project structure
- Implement core components
- Refactor Instagram processing
- Test compatibility with existing output

### Phase 2: YouTube Processing (2-3 days)
- Implement YouTube download functionality
- Integrate with offmute
- Implement transcript generation
- Create thumbnail extraction
- Test output format

### Phase 3: Scheduling and Automation (1 day)
- Implement scheduling system
- Set up automated execution
- Add comprehensive logging and error handling

### Phase 4: Testing and Documentation (1-2 days)
- Test with various links
- Document system architecture
- Create usage instructions
- Prepare for future platform additions

## Key Technical Solutions

### YouTube Processing

The YouTube processor will:
1. Validate YouTube URLs using regex patterns
2. Download videos using yt-dlp
3. Process audio using offmute
4. Generate transcripts from subtitles or speech recognition
5. Extract thumbnails from the video
6. Standardize output naming and format

Detailed implementation is provided in [youtube_processor_implementation.md](youtube_processor_implementation.md).

### Scheduling System

The scheduling system will:
1. Use cron jobs to trigger execution at specified times
2. Implement an internal scheduler to manage execution flow
3. Use lock files to prevent overlapping runs
4. Track execution status and results
5. Implement comprehensive error handling and logging

Detailed implementation is provided in [scheduling_implementation.md](scheduling_implementation.md).

### Modular Architecture

The system uses:
1. A processor factory pattern to select the appropriate processor for each link
2. A common interface for all platform processors
3. Standardized output management
4. Centralized configuration

Detailed architecture is provided in [file_structure.md](file_structure.md) and [systemPatterns.md](cline_docs/systemPatterns.md).

## File Structure

```
Process_Saved_Links/
│
├── cline_docs/                 # Memory Bank documentation
│   ├── activeContext.md        # Current focus and next steps
│   ├── productContext.md       # Project purpose and goals
│   ├── progress.md             # Project progress tracking
│   ├── systemPatterns.md       # Architecture and patterns
│   └── techContext.md          # Technical details and requirements
│
├── main.py                     # Entry point and scheduler
├── config.py                   # Configuration settings
├── notion_integration.py       # Notion database operations
├── output_manager.py           # Output standardization
│
├── processors/                 # Platform-specific processors
│   ├── __init__.py             # Package initialization
│   ├── base_processor.py       # Base class with common functionality
│   ├── instagram_processor.py  # Instagram-specific processing
│   ├── youtube_processor.py    # YouTube-specific processing
│   └── tiktok_processor.py     # Future platform (template)
│
├── utils/                      # Utility functions
│   ├── __init__.py             # Package initialization
│   ├── logging_utils.py        # Logging setup
│   └── file_utils.py           # File operations
│
├── scripts/                    # External scripts
│   ├── download_post.sh        # Existing Instagram download script
│   └── offmute.py              # Script for processing audio
│
├── tests/                      # Test suite
│   ├── __init__.py             # Package initialization
│   ├── test_instagram.py       # Tests for Instagram processor
│   ├── test_youtube.py         # Tests for YouTube processor
│   └── test_integration.py     # Integration tests
│
├── logs/                       # Log files
│   └── .gitkeep                # Placeholder to include directory in git
│
├── README.md                   # Project overview and quick start
├── requirements.txt            # Python dependencies
├── setup.py                    # Installation script
└── project_plan.md             # Detailed project plan
```

## Technical Requirements

### Dependencies
- Python 3.x
- notion-client
- yt-dlp
- ffmpeg
- offmute

### Configuration
- Notion API token and database ID
- Output directory paths
- Scheduling configuration
- Platform-specific settings

## Next Steps

1. **Review and Approve Plan**:
   - Review the project plan and architecture
   - Approve the implementation approach
   - Identify any missing requirements or considerations

2. **Begin Implementation**:
   - Set up the project structure
   - Implement the core components
   - Refactor the Instagram processor
   - Develop the YouTube processor
   - Implement the scheduling system

3. **Testing and Deployment**:
   - Test with various links from different platforms
   - Verify output compatibility with the existing viewer
   - Set up automated scheduling
   - Deploy the system

## Documentation

The following documentation has been prepared for this project:

- [README.md](README.md): Project overview and quick start guide
- [project_plan.md](project_plan.md): Detailed implementation plan
- [file_structure.md](file_structure.md): File structure and component relationships
- [youtube_processor_implementation.md](youtube_processor_implementation.md): YouTube processor implementation details
- [scheduling_implementation.md](scheduling_implementation.md): Scheduling system implementation details
- [cline_docs/](cline_docs/): Memory Bank documentation

## Conclusion

The Process Saved Links project provides a robust, modular solution for processing social media content from various platforms. By refactoring the existing Instagram processing functionality and adding support for YouTube videos, the system will offer a comprehensive solution for saving and organizing social media content. The modular architecture ensures that the system can be easily extended to support additional platforms in the future.