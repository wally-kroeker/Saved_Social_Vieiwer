# Simplified Viewer Implementation Plan (FastAPI + Basic HTML)

## Objective
Replace the existing basic Python http.server and static HTML viewer with a streamlined FastAPI solution that prioritizes core functionality.

## Assumptions
- FastAPI backend framework
- Local access (localhost)
- Current output directory structure remains
- Uses uv package manager and virtual environment

## Implementation Phases

### Phase 1: Backend (FastAPI)
1. Setup FastAPI Application
   - Create viewer/main.py with minimal configuration
   - Install essential dependencies (fastapi, uvicorn, jinja2)
   - Configure static file serving

2. Content Discovery
   - Scan OUTPUT_DIR for content files by platform
   - Extract basic metadata from JSON files
   - Simple in-memory content index

3. Core API Endpoints
   - GET /api/content - List all content
   - GET /api/content/{platform} - List platform content
   - GET /api/content/{id} - Get specific content item
   - GET /static/{path} - Serve static assets

### Phase 2: Frontend
1. HTML Structure
   - Simple responsive layout
   - Basic navigation
   - Content listing page
   - Individual content views

2. Content Views
   - Basic HTML5 video player
   - Simple image display
   - Transcript viewer
   - Metadata display

3. Basic Interactivity
   - Simple text search
   - Platform filtering
   - Basic pagination

### Phase 3: Integration
1. Update process_links_manager.sh
   - Add viewer start/stop commands
   - Configure to use FastAPI server

## Key Features
- Straightforward file serving
- Proper handling of special characters in paths
- Mobile-friendly layout
- Basic search functionality

## Not Included (Future Enhancements)
- Advanced search capabilities
- User authentication
- Complex UI frameworks
- Analytics/statistics
- Content editing


