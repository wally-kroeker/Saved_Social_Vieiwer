# Content Viewer

A simple web-based viewer for the processed content from the Process Saved Links project.

## Features

- Browse all processed videos and content
- Play videos directly in browser
- View transcripts and metadata
- Sort content by date or platform

## Usage

1. Start the viewer using one of these methods:
   - From the interactive CLI: `./process_links_manager.sh` and select option 7
   - From the command line: `./process_links_manager.sh viewer start`

2. Open your browser and navigate to: `http://localhost:8080`

3. Stop the viewer when done:
   - From the interactive CLI: Select option 8
   - From the command line: `./process_links_manager.sh viewer stop`

## Technical Details

The viewer consists of:
- `server.py`: A Python HTTP server that serves content from the output directory
- `videos.html`: Frontend interface for browsing and viewing content

The server automatically detects videos, transcripts, and thumbnails from the output directory. 