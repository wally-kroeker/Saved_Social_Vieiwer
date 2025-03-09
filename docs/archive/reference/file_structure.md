# File Structure Reference

This document provides a detailed overview of the project's file organization.

## Directory Structure

```
Process_Saved_Links/
├── main.py                     # Main entry point and scheduler
├── config.py                   # Configuration loading and management
├── notion_integration.py       # Notion API integration
├── output_manager.py           # Output file management
├── processors/                 # Platform-specific processors
│   ├── __init__.py             # Processor initialization
│   ├── base_processor.py       # Base class for all processors
│   ├── instagram_processor.py  # Instagram-specific processing
│   ├── youtube_processor.py    # YouTube-specific processing
│   └── platform_selector.py    # Logic to select appropriate processor
├── utils/                      # Utility functions and helpers
│   ├── __init__.py             # Utilities initialization
│   ├── logging_utils.py        # Logging configuration
│   ├── file_utils.py           # File operations helpers
│   └── url_utils.py            # URL parsing and validation
├── scripts/                    # External scripts and tools
│   ├── download_post.sh        # Instagram download script
│   ├── offmute.py              # Offmute integration script
│   └── setup_env.sh            # Environment setup script
├── tests/                      # Test scripts and test data
│   ├── __init__.py             # Tests initialization
│   ├── test_notion_integration.py  # Notion integration tests
│   ├── test_instagram_processor.py # Instagram processor tests
│   ├── test_youtube_processor.py   # YouTube processor tests
│   ├── test_offmute.py         # Offmute integration tests
│   └── test_production_flow.py # End-to-end testing
├── docs/                       # Project documentation
│   ├── overview/               # Project overview documentation
│   ├── implementation/         # Implementation details
│   ├── integrations/           # Integration documentation
│   ├── development/            # Development guides
│   ├── reference/              # Reference documentation
│   └── README.md               # Documentation index
├── .env                        # Environment variables (not in version control)
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Project README
```

## Key Files Explained

### Core Files

- **main.py**: The main entry point for the application. Contains the scheduler and orchestrates the processing pipeline.
- **config.py**: Handles loading and validating configuration from environment variables and config files.
- **notion_integration.py**: Manages all interactions with the Notion API, including retrieving links and updating their status.
- **output_manager.py**: Handles file operations for the standardized output format, ensuring consistent naming and organization.

### Processor Files

- **processors/base_processor.py**: Abstract base class defining the interface all platform processors must implement.
- **processors/instagram_processor.py**: Handles Instagram-specific content processing.
- **processors/youtube_processor.py**: Handles YouTube-specific content processing.
- **processors/platform_selector.py**: Determines which processor should handle a given URL.

### Utility Files

- **utils/logging_utils.py**: Configures logging for the application, including log rotation and formatting.
- **utils/file_utils.py**: Provides helper functions for file operations, such as creating directories and checking file existence.
- **utils/url_utils.py**: Contains functions for URL validation, parsing, and normalization.

### Script Files

- **scripts/download_post.sh**: Bash script for downloading Instagram posts (used by the Instagram processor).
- **scripts/offmute.py**: Python script for interacting with the Offmute API and CLI.
- **scripts/setup_env.sh**: Helper script for setting up the environment for development or production.

### Test Files

- **tests/test_notion_integration.py**: Tests for the Notion integration.
- **tests/test_instagram_processor.py**: Tests for the Instagram processor.
- **tests/test_youtube_processor.py**: Tests for the YouTube processor.
- **tests/test_offmute.py**: Tests for the Offmute integration.
- **tests/test_production_flow.py**: End-to-end tests for the production flow.

### Configuration Files

- **.env**: Contains environment variables for configuration (not committed to version control).
- **.env.example**: Example environment variables with placeholder values.
- **requirements.txt**: Lists all Python dependencies.

## Output Directory Structure

The processed content is organized in the following structure:

```
/home/walub/Documents/Processed-ContentIdeas/
├── instagram/                  # Instagram content
│   ├── post_id_1/              # Directory for a specific post
│   │   ├── video.mp4           # Processed video
│   │   ├── thumbnail.jpg       # Video thumbnail
│   │   ├── transcript.md       # Markdown transcript
│   │   └── metadata.json       # Metadata about the post
│   └── ...
├── youtube/                    # YouTube content
│   ├── video_id_1/             # Directory for a specific video
│   │   ├── video.mp4           # Processed video
│   │   ├── thumbnail.jpg       # Video thumbnail
│   │   ├── transcript.md       # Markdown transcript
│   │   └── metadata.json       # Metadata about the video
│   └── ...
└── logs/                       # Processing logs
    ├── instagram_processor_YYYYMMDD_HHMMSS.log  # Instagram processor logs
    ├── youtube_processor_YYYYMMDD_HHMMSS.log    # YouTube processor logs
    └── notion_integration_YYYYMMDD_HHMMSS.log   # Notion integration logs
```

## Related Documentation

- [Project Overview](../overview/project_overview.md) - High-level project description
- [Architecture](../overview/architecture.md) - System architecture and components
- [Implementation Guide](../implementation/implementation_guide.md) - Implementation details 