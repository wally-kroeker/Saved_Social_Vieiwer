# Social Media Content Viewer Architecture

## Overview
The Social Media Content Viewer is a web application built with FastAPI and modern web technologies that provides a unified interface for viewing saved social media content. It's designed to display content from various platforms (like YouTube and Instagram) in a consistent, user-friendly manner.

## System Architecture

### Backend (Python/FastAPI)
The backend is built using FastAPI and provides the following key components:

#### Core Components
- **FastAPI Application**: Main web server handling all HTTP requests
- **Content Management System**: Handles content discovery and caching
- **File System Integration**: Manages access to saved media files and metadata

#### Directory Structure
```
viewer/
├── main.py           # Main FastAPI application
├── user_data_manager.py # Handles loading/saving user-specific data (status, fav, notes)
├── static/          # Static assets (CSS, JavaScript) for original viewer
├── templates/       # HTML templates for original viewer
├── Updated-Viewer/  # Source code for the new React-based viewer (V2)
│   ├── src/
│   ├── public/
│   ├── dist/         # Build output for V2 viewer (served by FastAPI)
│   ├── package.json
│   └── ...
└── __pycache__/    # Python bytecode cache
# --- Outside viewer/ directory (example location) ---
# user_data.json      # Stores user status, favorites, notes
# user_data.json.bak  # Backup of user data
```

#### Key Classes

##### ContentItem
```python
class ContentItem:
    def __init__(self, 
                 platform: str,
                 filename: str, 
                 file_path: Path,
                 username: str = "", 
                 date: str = "", 
                 title: str = "",
                 has_transcript: bool = False,
                 has_thumbnail: bool = False,
                 has_metadata: bool = False)
```
Represents a single piece of content with its associated metadata and file information.

### Frontend (HTML/CSS/JavaScript)

#### Original Viewer (Jinja2 + Vanilla JS)

Components:
1. **Header**
   - Search functionality
   - Platform filtering
   
2. **Content Grid**
   - Responsive layout
   - Content cards with thumbnails
   
3. **Modal View**
   - Video player
   - Metadata display
   - Transcript viewer (when available)

Templates:
- `index.html`: Main application template
- Content item template (for grid items)
- Video view template (for modal view)

#### New Viewer (React/Vite - V2)
Located under the `/v2` path. This is a modern single-page application (SPA) built with React, Vite, TypeScript, and potentially other libraries (like Shadcn UI based on `package.json`). Features include:
- Content status tracking (new, viewed, processing, completed)
- Favorites/bookmarking
- User notes per item
- Filtering by status and favorites
- Interactive modal with media, metadata, transcript, and notes tabs

Components:
- (Details specific to the React application - needs further inspection of `Updated-Viewer/src` if required)

Build Output:
- Served statically from `viewer/Updated-Viewer/dist/`

### User Data Management (Backend)
- **Storage:** User-specific data (status, favorite, notes) is stored in a JSON file (`user_data.json`) managed by `user_data_manager.py`.
- **Backup:** A backup file (`user_data.json.bak`) is maintained for resilience against corruption.
- **API Endpoints:**
  - `GET /api/user_data`: Retrieves all user data.
  - `PUT /api/user_data/{platform}/{filename_base}`: Updates status, favorite, or notes for a specific item.

## API Endpoints

### Content Management
- `GET /`: Home page (Original Viewer)
- `GET /v2` & `/v2/*`: Root and sub-paths for the New Viewer (V2)
- `GET /api/content`: List all content with optional filtering
- `GET /api/content/{platform}`: List content for specific platform
- `GET /api/content/{platform}/{filename}`: Get specific content details
- `GET /media/{platform}/{path}`: Serve media files
- `GET /refresh`: Force content cache refresh

## Content Organization

### File Structure
Content is organized in the following structure:
```
output/
└── {platform}/
    └── {content_files}/
        ├── video.mp4
        ├── thumbnail.jpg (optional)
        ├── metadata.json (optional)
        └── transcript.md (optional)
```

### Content Discovery
The system automatically discovers content by:
1. Scanning the output directory
2. Grouping related files (video, thumbnail, metadata, transcript)
3. Parsing metadata from filenames and associated files
4. Caching content information for improved performance

### Caching
- Content information is cached for 5 minutes
- Cache can be manually refreshed via the `/refresh` endpoint
- Cache includes content metadata, file locations, and available assets

## Features

### Content Display (V2 Viewer)
- Responsive grid layout
- Thumbnail previews
- Basic content information display
- Platform-specific badges
- **Status Badges:** Color-coded indicators for new, viewed, processing, completed.
- **Feature Indicators:** Badges for transcript, metadata, and notes availability.

### Content Filtering (V2 Viewer)
- Full-text search across titles, usernames, and platforms
- Platform-specific filtering
- Real-time results updating
- **Filter by Favorites:** Toggle to show only bookmarked items.
- **Filter by Status:** Select specific content statuses to display.

### Content Interaction (V2 Viewer)
- **Bookmarking:** Toggle favorite status via card button or modal button.
- **Status Updates:** Change content status via modal dropdown/selector.
- **Notes:** View and edit user notes in the modal.

### Content Viewing
- Modal-based content viewer
- Video playback support
- Metadata display
- Transcript viewing (when available)

### User Interface (V2 Viewer)
- Modern, responsive design
- Intuitive navigation
- Search and filter capabilities
- **Enhanced Controls:** Bookmark toggles, status selectors.
- **Tabbed Modal:** Organizes detailed content view (Media, Metadata, Transcript, Notes).
- Loading states and error handling (including toast notifications).

## Technical Details

### Dependencies
- FastAPI: Web framework
- Jinja2: Template engine
- Static file serving
- HTML5 video playback

### Performance Considerations
- Content caching
- Lazy loading of media
- Responsive image loading
- Efficient DOM updates

### Security
- File access restrictions
- Path traversal prevention
- Content type validation

## Usage

### Content Requirements
- Supported video format: MP4
- Optional thumbnail formats: JPG, JPEG, PNG
- Optional metadata format: JSON
- Optional transcript format: MD

### File Naming Convention
Format: `platform-username-YYMMDD-title`
Example: `youtube-channelname-230401-video-title`

### Content Access
Content is served through the `/media/{platform}/{path}` endpoint with appropriate security checks and content type validation. 