# Project Memory

## Core Project Overview
The Saved Social Viewer project enables users to:
1. Download and archive content from social media platforms (YouTube, Instagram, etc.)
2. Store the content locally with metadata
3. Generate transcripts for video content
4. Browse and view the downloaded content through a web interface

## Current Architectural Components

### Backend Systems
- **Content Processors**: Platform-specific modules for downloading content from various sources
- **Notion Integration**: Tracks content to be processed and updates status
- **Transcript Generation**: Creates text transcripts from video content
- **File Management**: Standardized file naming and organization system

### Frontend Components
- **Content Viewer**: Web-based interface for browsing and viewing saved content
- **Management UI**: CLI-based interface for configuring and controlling the system

## Recent Architectural Decisions

### 2025-03-28: Filename Standardization
- **Problem**: Special characters in filenames (especially `#`) were causing issues with web serving
- **Solution**: 
  - Implemented consistent filename pattern: `{platform}-{username}-{date}-{sanitized_title}`
  - Created sanitization utilities that remove/replace problematic characters
  - Added migration tools to convert existing files
  - Organized content into platform-specific subdirectories
  
- **Key Components**:
  - `utils/filename_utils.py`: Core filename handling functions
  - `utils/migrate_filenames.py`: Migration tool for existing files  
  - `utils/processor_filename_integration.py`: Adapter layer for processors

### 2025-03-27: FastAPI Viewer Decision
- **Problem**: The basic Python `http.server` implementation had limitations with handling file paths, special characters, and search functionality
- **Solution**: Decided to rebuild the viewer using FastAPI for backend and modern JavaScript for frontend
- **Benefits**:
  - Improved URL path handling
  - Better security controls
  - Enhanced search and filtering
  - More robust error handling

## Implementation Status

### Completed
- ✅ YouTube content processor
- ✅ Instagram content processor
- ✅ Basic CLI interface
- ✅ Transcript generation
- ✅ Filename standardization system

### In Progress
- 🔄 File migration implementation
- 🔄 FastAPI viewer development
- 🔄 Improved content browsing interface

### Planned
- ⬜ Advanced search functionality
- ⬜ Content tagging system
- ⬜ Additional platform support (TikTok, Twitter/X)

## Technical Guidelines

### Filename Conventions
- Use the standardized pattern: `{platform}-{username}-{date}-{sanitized_title}`
- All content related to a single media item should share the same base filename
- Different file types are distinguished by extensions:
  - `.mp4`: Video content
  - `.jpg`: Thumbnail/preview image
  - `.md`: Transcript
  - `.json`: Metadata

### Directory Structure
- `/output/{platform}/`: Platform-specific content directories
- `/viewer/`: Viewer application code
- `/utils/`: Shared utility functions
- `/docs/`: Documentation

### Development Practices
- Use the UV package manager for Python dependencies
- Run unit tests before submitting changes
- Use type hints in Python code
- Document API endpoints and function parameters 