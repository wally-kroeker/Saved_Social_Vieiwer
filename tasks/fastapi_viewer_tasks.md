# FastAPI Viewer Implementation Tasks - Simplified

## Backend Setup

### Initial Setup
- [ ] Create basic FastAPI application structure
  - [ ] Set up project directory in `viewer/`
  - [ ] Initialize FastAPI app with minimal configuration
  - [ ] Configure to use UV for dependency management
- [ ] Set up essential dependencies
  - [ ] Add FastAPI and Uvicorn 
  - [ ] Add Jinja2 for templating
  - [ ] Add static file handling

### Core API Development
- [ ] Implement content discovery system
  - [ ] Create simple file system scanner for content
  - [ ] Extract basic metadata from JSON files
- [ ] Create core API endpoints
  - [ ] GET /api/content - List all content
  - [ ] GET /api/content/{platform} - List platform content
  - [ ] GET /api/content/{id} - Get specific content
- [ ] Implement media handling
  - [ ] Set up basic video streaming
  - [ ] Set up static image serving
  - [ ] Add transcript file serving
  - [ ] Serve metadata JSON

## Frontend Development

### Base Structure
- [ ] Create simple HTML/CSS/JS structure
  - [ ] Basic responsive layout
  - [ ] Simple navigation 
  - [ ] Content listing page
- [ ] Add minimal styling
  - [ ] Clean, readable interface
  - [ ] Mobile-friendly layout

### Content Views
- [ ] Video Player
  - [ ] Basic HTML5 video player
  - [ ] Support for basic controls
- [ ] Image Gallery
  - [ ] Simple image display
  - [ ] Basic navigation between images
- [ ] Transcript Viewer
  - [ ] Display formatted transcript
  - [ ] Basic styling for readability
- [ ] Metadata Display
  - [ ] Show key metadata fields
  - [ ] Format dates and titles properly

### Interactive Features
- [ ] Simple Search
  - [ ] Basic text search
  - [ ] Filter by platform
- [ ] Basic Navigation
  - [ ] Pagination for content lists
  - [ ] Back/forward navigation

## Testing

- [ ] Basic Functionality Testing
  - [ ] Verify API endpoints work
  - [ ] Test content discovery
  - [ ] Ensure media files load properly
- [ ] Browser Testing
  - [ ] Test in Chrome and Firefox
  - [ ] Basic mobile testing

## Integration

- [ ] Update process_links_manager.sh
  - [ ] Add viewer start/stop commands
  - [ ] Configure to use FastAPI server 