# System Architecture

## Architecture Overview

The Process Saved Links system follows a modular architecture designed for extensibility and maintainability. This document outlines the key components and their interactions.

## Core Components

### 1. Core Scheduler

The Core Scheduler manages the overall execution of the processing pipeline:

- Initiates the processing pipeline at scheduled times (morning, noon, 11:00 PM)
- Orchestrates the processing flow for links retrieved from Notion
- Enforces the 15-minute pause between processing items
- Manages error handling and recovery mechanisms
- Provides logging for system monitoring

### 2. Notion Integration

The Notion Integration component acts as the bridge between the system and the Notion database:

- Retrieves unprocessed links from the configured Notion database
- Updates the status of links after processing (success or failure)
- Stores metadata about processed content in the Notion database
- Handles authentication and API communication with Notion

### 3. Platform Processors

Each Platform Processor handles the specifics of content processing for a particular platform:

- **Base Processor**: Provides common functionality for all platform processors
- **Instagram Processor**: Handles Instagram-specific content processing
- **YouTube Processor**: Handles YouTube-specific content processing
- **Future Platform Processors**: Template for adding new platforms

Each processor implements the following functionality:
- URL validation and metadata extraction
- Content downloading
- Media processing (video, audio, images)
- Transcript generation (using Offmute)
- Output formatting according to standardized conventions

### 4. Output Manager

The Output Manager ensures consistent output formatting and organization:

- Manages file naming conventions
- Organizes output in the standard directory structure
- Handles file operations and permission management
- Ensures consistency across different platform outputs

## System Interactions

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Core Scheduler │────▶│ Notion Integration ◀───▶│  Notion Database │
│                 │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│                 │
│ Platform Selector │
│                 │
└────────┬────────┘
         │
         ├─────────────┬─────────────┐
         │             │             │
         ▼             ▼             ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
│                 │ │             │ │             │
│ Instagram      │ │ YouTube    │ │ Future      │
│ Processor      │ │ Processor  │ │ Processors  │
│                 │ │             │ │             │
└────────┬────────┘ └──────┬──────┘ └──────┬──────┘
         │                 │               │
         └────────┬────────┘               │
                  │                        │
                  └────────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │                 │
                     │ Output Manager  │
                     │                 │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │                 │
                     │ Output Directory │
                     │                 │
                     └─────────────────┘
```

## File Structure

The project's file structure reflects this architecture:

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

## Data Flow

1. **Initialization**: The Core Scheduler starts and loads configuration
2. **Link Retrieval**: Notion Integration queries the database for unprocessed links
3. **Platform Selection**: The system identifies the appropriate processor for each link
4. **Content Processing**: The Platform Processor handles the content-specific operations
5. **Output Generation**: Standardized outputs are created following naming conventions
6. **Status Update**: Notion database is updated with processing results
7. **Pause**: The system waits 15 minutes before processing the next item

## Key Design Decisions

1. **Modular Architecture**: Each platform is handled by a separate processor module that implements a common interface, making it easy to add new platforms.

2. **Centralized Configuration**: All configurable parameters are managed in a central configuration module.

3. **Standardized Output**: All platform processors produce output in a consistent format and directory structure.

4. **Error Isolation**: Errors in processing one link don't affect the processing of other links.

5. **Logging and Monitoring**: Comprehensive logging enables effective monitoring and troubleshooting.

## Related Documentation

- [Project Overview](./project_overview.md) - High-level project description
- [Requirements](./requirements.md) - Detailed project requirements
- [Implementation Guide](../implementation/implementation_guide.md) - Implementation details 