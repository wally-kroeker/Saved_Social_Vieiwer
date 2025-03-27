# Viewer Refactor Plan (FastAPI + JS)

## Objective
Replace the existing basic Python http.server and static HTML viewer with a more robust solution using a FastAPI backend and a dynamic JavaScript frontend.

## Assumptions
- FastAPI backend framework
- Local access (localhost)
- Current output directory structure remains
- Uses uv package manager and virtual environment

## Implementation Phases

### Phase 1: Backend (FastAPI)
1. Setup FastAPI Application
   - Create viewer/main.py
   - Install dependencies (fastapi, uvicorn)
   - Basic FastAPI app setup

2. Content Indexing
   - Scan OUTPUT_DIR for media files
   - Parse metadata from JSON files
   - Create content index in memory

3. API Endpoints
   - GET /api/content (paginated list)
   - GET /files/{filename:path} (media files)
   - GET /transcripts/{filename:path} (markdown)
   - POST /api/refresh_index (optional)

### Phase 2: Frontend
1. HTML Structure (viewer/index.html)
   - Search/filter controls
   - Content grid/list
   - Video player view
   - Transcript view

2. JavaScript (viewer/static/js/app.js)
   - API integration
   - State management
   - UI rendering
   - Event handling

### Phase 3: Integration
1. Update process_links_manager.sh
   - Use uvicorn for server
   - Implement PID management
   - Add restart functionality

2. Testing
   - API endpoints
   - UI functionality
   - Video playback
   - Security checks

### Phase 4: Documentation
1. Update README.md
2. Code cleanup
3. Bug fixes

## Key Features
- Efficient file serving
- Proper URL handling
- Security (prevent path traversal)
- Responsive UI
- Error handling


