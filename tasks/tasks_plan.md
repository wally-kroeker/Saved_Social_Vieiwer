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

### Phase 4: Code Restructuring
1. ✅ Move all Python scripts to src directory
   - Processor scripts (run_youtube_post.py, run_instagram_post.py)
   - Core modules (platform_processor.py, processor_factory.py)
   - Utility modules and config files
   
2. ✅ Update import paths for compatibility
   - Fix relative imports in moved modules
   - Ensure backward compatibility with existing scripts

3. ✅ Organize processors as a proper package
   - Separate processor implementations by platform
   - Maintain factory pattern for extensibility

4. ✅ Document new project structure in active_context.md

## Key Features
- Straightforward file serving
- Proper handling of special characters in paths
- Mobile-friendly layout
- Basic search functionality
- ✅ Dark mode UI theme

## Not Included (Future Enhancements)
- Advanced search capabilities
- User authentication
- Complex UI frameworks
- Analytics/statistics
- Content editing

## Completed Tasks
1. ✅ Enhanced video player functionality
   - Made video cards fully clickable
   - Improved modal layout and controls
   - Added transcript viewing support
   - Enhanced user experience
2. ✅ Cleaned up viewer directory structure
   - Removed unnecessary files
   - Improved code organization
3. ✅ Implemented basic FastAPI viewer with core functionality
4. ✅ Created responsive frontend with content cards and video player
5. ✅ Added search and filtering capabilities
6. ✅ Integrated with process_links_manager.sh
7. ✅ Implemented dark mode UI theme
8. ✅ Completed code restructuring to improve project organization

## Next Steps
1. Gather user feedback on video player enhancements
2. Monitor performance with large video libraries
3. Consider implementing video quality selection
4. Add support for video playback position memory
5. Explore adding video thumbnails for better preview
6. Consider implementing video playlists
7. Further testing of the restructured codebase
8. Consider adding more platforms in the processor factory
9. Explore advanced content tagging and categorization
10. Implement additional search capabilities in the viewer


