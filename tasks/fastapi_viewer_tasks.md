# FastAPI Viewer Implementation Tasks - Simplified

## Backend Setup

### Initial Setup
- [x] Create basic FastAPI application structure
  - [x] Set up project directory structure
  - [x] Initialize FastAPI app with minimal configuration
  - [x] Configure to use UV for dependency management
  - [x] Configure environment variables
- [x] Set up essential dependencies
  - [x] Add FastAPI and Uvicorn
  - [x] Add Jinja2 for templating
  - [x] Add static file handling

### Core API Development
- [x] Implement content discovery system
  - [x] Create simple file system scanner for content
  - [x] Extract basic metadata from JSON files
  - [x] Implement caching for file system operations
- [x] Create core API endpoints
  - [x] GET /api/content - List all content
  - [x] GET /api/content/{platform} - List platform content
  - [x] GET /api/content/{id} - Get specific content item
- [x] Implement media handling
  - [x] Set up basic video streaming
  - [x] Set up static image serving
  - [x] Add transcript file handling
  - [x] Serve metadata JSON

## Frontend Development

### Base Structure
- [x] Create simple HTML/CSS/JS structure
  - [x] Basic responsive layout
  - [x] Simple navigation 
  - [x] Content listing page
- [x] Add minimal styling
  - [x] Clean, readable interface
  - [x] Mobile-friendly layout

### Content Views
- [x] Video Player
  - [x] Basic HTML5 video player
  - [x] Support for basic controls
- [x] Image Gallery
  - [x] Simple image display
  - [x] Basic navigation between images
- [x] Transcript Viewer
  - [x] Display formatted transcript
  - [x] Basic styling for readability
- [x] Metadata Display
  - [x] Show key metadata fields
  - [x] Format dates and titles properly

### Interactive Features
- [x] Simple Search
  - [x] Basic text search
  - [x] Filter by platform
- [x] Basic Navigation
  - [x] Pagination for content lists
  - [x] Back/forward navigation

## Testing

- [x] Basic Functionality Testing
  - [x] Verify API endpoints work
  - [x] Test content discovery
  - [x] Ensure media files load properly
- [x] Browser Testing
  - [x] Test in Chrome and Firefox
  - [x] Basic mobile testing

## Integration

- [x] Update process_links_manager.sh
  - [x] Add viewer start/stop commands
  - [x] Configure to use FastAPI server 