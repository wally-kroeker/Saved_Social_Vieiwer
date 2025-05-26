# V2 Content Viewer Architecture

## Overview

The V2 Content Viewer is a web application designed to provide an interactive interface for browsing, viewing, and managing social media content that has been previously downloaded and processed by an external system (like the link processing scripts in this project).

## Core Functionalities

- **Content Discovery:** Scans a designated `output` directory to find processed content items.
- **Browsing Interface:** Displays discovered content items in a filterable and sortable grid layout, typically showing thumbnails, titles, usernames, and platforms.
- **Filtering & Sorting:** Allows users to filter content by:
  - Platform (YouTube, Instagram, etc.)
  - Status
  - Search query (title, username)
  - Bookmarked status
  - Sorting is typically available by date or other relevant criteria
- **Detailed View (Modal):** Clicking on a content card opens a modal window providing a detailed view and interaction options for that specific item.
- **Media Playback:** Displays and allows playback of the primary media file (video or image) within the modal.
- **Metadata Viewing:** Optionally displays structured metadata associated with the content item (loaded from a JSON file).
- **Transcript Viewing:** Optionally displays a text transcript of the content (loaded from a Markdown file).
- **User Interaction:**
  - **Bookmarking:** Allows users to mark items as favorites
  - **Notes:** Provides a text area for users to add and save personal notes about the content item
  - **Rating:** Allows users to assign a rating (e.g., 0-5) to the content item
- **Data Persistence (User Data):** User-specific data like notes, ratings, bookmarks, and potentially viewing status are intended to be saved and loaded separately (currently handled by `user_data_manager.py` and likely a `user_data.json` file).

## Technical Stack

The frontend is built using:
- React with TypeScript
- Vite
- Tailwind CSS/shadcn UI components

It communicates with a backend API server (currently FastAPI in `viewer/main.py`) to fetch content listings and serve media files.

## Output Directory Structure

The Viewer relies heavily on a specific file organization within the main `output` directory. The backend API scans this directory to build the content list.

```
output/
├── <platform_name_1>/           # e.g., 'youtube', 'instagram'
│   ├── <base_filename_1>.<media_ext>    # Required: primary media file (.mp4, .mov, .avi, .mkv, .jpg, .jpeg, .png, .gif, .webp)
│   ├── <base_filename_1>.<thumb_ext>   # Optional: thumbnail image (.jpg, .png, .jpeg, .webp)
│   ├── <base_filename_1>.json          # Optional: metadata file (JSON)
│   └── <base_filename_1>.md            # Optional: transcript (Markdown; must share exact base filename)

├── <platform_name_2>/           # e.g., 'youtube'
│   ├── <base_filename_2>.<media_ext>    # Required: primary media file (.mp4, .mov, .avi, .mkv, .jpg, .jpeg, .png, .gif, .webp)
│   ├── <base_filename_2>.json          # Optional: metadata file (JSON)
│   └── <base_filename_2>.md            # Optional: transcript (Markdown; must share exact base filename)
```

### Key Points about the Structure

- **Platform Directories:** Content is organized into subdirectories named after the source platform (e.g., `youtube`, `instagram`). The viewer uses these directory names.
- **Base Filename Pattern:** All files related to a single piece of content *must* share the exact same base filename: `{platform}-{username}-{YYYY}-{MM}-{DD}-{title-slug}`, where:
  - `platform` is the directory name.
  - `username` is the content creator's handle (which may include underscores).
  - `YYYY-MM-DD` is the date of the content.
  - `title-slug` is a hyphen-separated, URL-friendly version of the content title.
- **Supported File Extensions:** The discovery logic recognizes:
  - Video: `.mp4`, `.mov`, `.avi`, `.mkv`
  - Image: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
  - Metadata: `.json`
  - Transcript/Description: `.md` (must match the base filename exactly)
- **Primary Media File:** Each content group must include at least one recognized media file. Videos are preferred over images for primary display. Images serve as thumbnails if no distinct thumbnail is found.
- **Thumbnail Selection:** Thumbnails are optional images that share the base filename. If no distinct thumbnail is provided for a video, the first available image is used. If the primary media is an image, it is used as its own thumbnail.
- **Exclusion of Non-matching Files:** Files that do not share the exact base filename (e.g., extra suffixes like `-0`) will be treated as separate items and may not be associated correctly.
- **Associated Files:** Metadata and transcript files must share the exact base filename to be associated with the primary media.

## Data Flow for Standalone Viewer

If rebuilding the viewer as a standalone project, the frontend would primarily need a backend that provides:

### 1. Content Listing API (`/api/content`)
An endpoint that scans the `output` directory according to the structure described above and returns a JSON array of content items. Each item object needs to conform to the structure expected by the frontend's `ContentItem` interface, including:
- `id` (unique identifier)
- `platform`, `filename`, `username`, `date` (ISO format), `title`
- `hasTranscript`, `hasThumbnail`, `hasMetadata` (booleans)
- `media_path` (relative URL path to the media, e.g., `youtube/file.mp4`)
- `transcript_path` (relative URL path to the transcript, e.g., `youtube/file.md`)
- `thumbnailUrl` (relative URL path to the thumbnail, e.g., `youtube/file.jpg`)
- `metadata` (the actual parsed JSON object from the metadata file)
- `status`, `favorite` (if user data is included)

### 2. Media Serving API (`/media/`)
An endpoint capable of serving static files (media, transcripts, thumbnails) from the `output` directory based on the relative paths provided in the content listing API response (e.g., a request to `/media/youtube/file.mp4` should serve `output/youtube/file.mp4`).

### 3. User Data API (Optional)
Endpoints for fetching and updating user-specific data like:
- Notes
- Ratings
- Favorites
- Status

This functionality would need to be retained if user interaction features are desired in the standalone version. 