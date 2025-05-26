import os
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import user data manager functions correctly
from user_data_manager import load_user_data, update_user_data_for_item

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define paths
OUTPUT_DIRECTORY = PROJECT_ROOT / 'output'
NEW_VIEWER_DIRECTORY = Path(__file__).resolve().parent / 'Updated-Viewer' / 'dist'

# Create FastAPI app
app = FastAPI(title="Content Viewer V2")

# Mount static files for the viewer
# Serve assets (CSS, JS, images) from the build directory
app.mount("/assets", StaticFiles(directory=str(NEW_VIEWER_DIRECTORY / 'assets')), name="viewer-assets")
# Serve other potential static files from the root of the build directory
app.mount("/static", StaticFiles(directory=str(NEW_VIEWER_DIRECTORY)), name="viewer-static-root")

# Define content item model
class ContentItem:
    def __init__(self, 
                 platform: str,
                 filename: str, 
                 file_path: Path, # The actual path to the main media file (e.g., mp4)
                 username: str = "", 
                 date: str = "", 
                 title: str = "",
                 has_transcript: bool = False,
                 transcript_file_path: Optional[Path] = None, # Add path to transcript file
                 has_thumbnail: bool = False,
                 thumbnail_file_path: Optional[Path] = None, # Add path to thumbnail file
                 has_metadata: bool = False,
                 metadata_file_path: Optional[Path] = None, # Add path to metadata file
                 metadata: Optional[Dict[str, Any]] = None): # Add field for loaded metadata
        self.platform = platform
        self.filename = filename # Base filename without extension
        self.file_path = file_path # Path to the main media file
        self.username = username
        self.date = date
        self.title = title
        self.has_transcript = has_transcript
        self.transcript_file_path = transcript_file_path # Store transcript path
        self.has_thumbnail = has_thumbnail
        self.thumbnail_file_path = thumbnail_file_path # Store thumbnail path
        self.has_metadata = has_metadata
        self.metadata_file_path = metadata_file_path # Store metadata path
        self.metadata = metadata # Store loaded metadata
        
    def to_dict(self) -> Dict[str, Any]:
        # Helper to get relative path for serving via API
        def get_relative_serve_path(full_path: Optional[Path]) -> Optional[str]:
            if full_path and full_path.is_file():
                try:
                    relative_path = full_path.relative_to(OUTPUT_DIRECTORY)
                    return str(relative_path).replace('\\', '/')
                except ValueError:
                    print(f"Warning: Could not make path relative to OUTPUT_DIRECTORY: {full_path}")
                    return None
            return None

        # Calculate paths ONLY when converting to dict
        media_serve_path = get_relative_serve_path(self.file_path)
        transcript_serve_path = get_relative_serve_path(self.transcript_file_path)
        thumbnail_serve_path = get_relative_serve_path(self.thumbnail_file_path)

        data = {
            "id": f"{self.platform}-{self.filename}",
            "platform": self.platform,
            "filename": self.filename,
            "username": self.username,
            "date": self.date,
            "title": self.title,
            # Booleans based on whether the *original* file exists
            "has_transcript": self.transcript_file_path is not None and self.transcript_file_path.is_file(),
            "has_thumbnail": self.thumbnail_file_path is not None and self.thumbnail_file_path.is_file(),
            "has_metadata": self.metadata is not None, # Based on loaded metadata
            
            # Actual paths for frontend use (will be null if file doesn't exist or path fails)
            "media_path": media_serve_path,
            "transcript_path": transcript_serve_path,
            "thumbnailUrl": thumbnail_serve_path,
            
            "metadata": self.metadata, # The actual metadata object
        }
        # Add status and favorite if they exist (e.g., loaded from user_data)
        # Example: if hasattr(self, 'status'): data['status'] = self.status
        # Example: if hasattr(self, 'favorite'): data['favorite'] = self.favorite
        
        # Clean up null values before returning if desired, but often better for frontend to handle
        # return {k: v for k, v in data.items() if v is not None}
        return data

# Content discovery functions
def discover_content() -> List[ContentItem]:
    """Scan the output directory for content files, grouping by base name first."""
    content_items = []
    
    if not OUTPUT_DIRECTORY.exists():
        print(f"Output directory does not exist: {OUTPUT_DIRECTORY}")
        return content_items
    
    media_extensions = { ".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png", ".gif", ".webp" }
    video_extensions = { ".mp4", ".mov", ".avi", ".mkv" }
    image_extensions = { ".jpg", ".jpeg", ".png", ".gif", ".webp" }
    transcript_extension = ".md"
    metadata_extension = ".json"

    for platform_dir in OUTPUT_DIRECTORY.iterdir():
        if not platform_dir.is_dir() or platform_dir.name.startswith('.'): # Skip non-dirs and hidden dirs
            continue
        
        platform = platform_dir.name
        print(f"--- Scanning platform directory: {platform} ---")
        
        # Group files by base name first
        found_files_by_base: Dict[str, Dict[str, Path]] = {}
        for file_path in platform_dir.iterdir():
            if file_path.is_file():
                base_name = file_path.stem
                ext = file_path.suffix.lower()
                if base_name not in found_files_by_base:
                    found_files_by_base[base_name] = {}
                found_files_by_base[base_name][ext] = file_path

        print(f"Found {len(found_files_by_base)} potential items based on unique filenames.")

        # Process each group of files sharing a base name
        for base_name, files_dict in found_files_by_base.items():
            main_media_path: Optional[Path] = None
            main_media_ext: Optional[str] = None
            is_video = False

            # 1. Find primary media file (video > image)
            for ext in video_extensions:
                if ext in files_dict:
                    main_media_path = files_dict[ext]
                    main_media_ext = ext
                    is_video = True
                    break
            if not main_media_path:
                 for ext in image_extensions:
                     if ext in files_dict:
                         main_media_path = files_dict[ext]
                         main_media_ext = ext
                         is_video = False # It's an image
                         break
            
            # Skip if no recognizable media file found for this base_name
            if not main_media_path or not main_media_ext:
                # print(f"Skipping base '{base_name}': No primary media file found.")
                continue

            # 2. Find associated files
            metadata_path = files_dict.get(metadata_extension)
            transcript_path = files_dict.get(transcript_extension)
            
            # 3. Find thumbnail (prefer jpg/png, different from main media if main is image)
            thumbnail_path: Optional[Path] = None
            preferred_thumb_exts = [".jpg", ".png", ".jpeg", ".webp"]
            for ext in preferred_thumb_exts:
                if ext in files_dict and files_dict[ext] != main_media_path: 
                    thumbnail_path = files_dict[ext]
                    break
            # If no distinct thumbnail found and it's a video, use any available image
            if is_video and not thumbnail_path:
                 for ext in image_extensions:
                     if ext in files_dict:
                         thumbnail_path = files_dict[ext]
                         break
            # If the main media is an image, use itself as the thumbnail
            elif not is_video:
                 thumbnail_path = main_media_path

            # 4. Load metadata content
            loaded_metadata: Optional[Dict[str, Any]] = None
            if metadata_path:
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f: # Specify encoding
                        loaded_metadata = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to read/parse metadata {metadata_path}: {e}")

            # 5. Extract info from filename pattern: platform-username-YYYY-MM-DD-title
            parts = base_name.split('-')
            username = "Unknown"
            date_str = ""
            title = base_name # Default title
            iso_date_str = ""
            
            # Parsing logic (same as before, seems reasonable for observed names)
            if len(parts) >= 5 and parts[0] == platform:
                username = parts[1]
                if re.match(r'^\d{4}$', parts[2]) and re.match(r'^\d{2}$', parts[3]) and re.match(r'^\d{2}$', parts[4]):
                    date_str = f"{parts[2]}-{parts[3]}-{parts[4]}"
                    title = ' '.join(parts[5:]).replace('-', ' ')
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        iso_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        iso_date_str = ""
                else:
                     username = parts[1]
                     title = ' '.join(parts[2:]).replace('-', ' ')
            elif len(parts) > 1 and parts[0] == platform:
                 username = parts[1]
                 title = ' '.join(parts[2:]).replace('-', ' ')
            
            title = re.sub(r'\s+', ' ', title).strip() # Clean title
            if not title: title = base_name # Fallback title
            
            # 6. Create ContentItem instance
            content_item = ContentItem(
                platform=platform,
                filename=base_name,
                file_path=main_media_path,
                username=username,
                date=iso_date_str,
                title=title,
                has_transcript=transcript_path is not None,
                transcript_file_path=transcript_path,
                has_thumbnail=thumbnail_path is not None,
                thumbnail_file_path=thumbnail_path,
                has_metadata=loaded_metadata is not None,
                metadata_file_path=metadata_path,
                metadata=loaded_metadata
            )
            content_items.append(content_item)

    print(f"--- Finished discovery: {len(content_items)} items found ---")
    # Sort by date (newest first)
    content_items.sort(key=lambda x: x.date if x.date else "0000-00-00T00:00:00Z", reverse=True)
    
    return content_items

# Cache for content items
content_cache = None
last_cache_update = None

def get_content(force_refresh=False) -> List[ContentItem]:
    """Get content items with caching"""
    global content_cache, last_cache_update
    
    # Check if cache needs to be refreshed
    if content_cache is None or force_refresh or (
        last_cache_update is not None and 
        (datetime.now() - last_cache_update).seconds > 300  # Refresh every 5 minutes
    ):
        content_cache = discover_content()
        last_cache_update = datetime.now()
        print(f"Content cache refreshed: {len(content_cache)} items found")
    
    return content_cache

# Routes for Viewer (formerly V2)
@app.get("/", response_class=FileResponse)
async def serve_viewer_root():
    """Serve the root index.html for the viewer."""
    index_path = NEW_VIEWER_DIRECTORY / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Viewer index.html not found. Did you build it?")
    return FileResponse(index_path)

@app.get("/api/content")
async def list_content(platform: Optional[str] = None, search: Optional[str] = None):
    """List all content or filter by platform"""
    content_items = get_content()
    
    # Filter by platform
    if platform:
        content_items = [item for item in content_items if item.platform.lower() == platform.lower()]
    
    # Filter by search query
    if search:
        search = search.lower()
        content_items = [
            item for item in content_items 
            if search in item.title.lower() or 
               search in item.username.lower() or 
               search in item.platform.lower()
        ]
    
    return {"items": [item.to_dict() for item in content_items]}

@app.get("/api/content/{platform}")
async def list_platform_content(platform: str, search: Optional[str] = None):
    """List content for a specific platform"""
    content_items = get_content()
    
    # Filter by platform
    content_items = [item for item in content_items if item.platform.lower() == platform.lower()]
    
    # Filter by search query
    if search:
        search = search.lower()
        content_items = [
            item for item in content_items 
            if search in item.title.lower() or 
               search in item.username.lower()
        ]
    
    return {"items": [item.to_dict() for item in content_items]}

@app.get("/api/content/{platform}/{filename}")
async def get_content_item(platform: str, filename: str):
    """Get details for a specific content item"""
    content_items = get_content()
    
    # Find the specific item
    for item in content_items:
        if item.platform.lower() == platform.lower() and item.filename == filename:
            return item.to_dict()
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.get("/media/{platform}/{path:path}")
async def get_media(platform: str, path: str):
    """Serve media files"""
    file_path = OUTPUT_DIRECTORY / platform / path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

@app.get("/refresh")
async def refresh_content():
    """Force refresh of content cache"""
    items = get_content(force_refresh=True)
    return {"status": "success", "item_count": len(items)}

# --- Pydantic Models for User Data ---
class UserDataItemUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Item status (e.g., new, viewed, processing, completed)")
    favorite: Optional[bool] = Field(None, description="Favorite status")
    notes: Optional[str] = Field(None, description="User notes")
    rating: Optional[int] = Field(None, description="User rating (0-5)")

# --- API Endpoints for User Data ---
@app.get("/api/user_data")
async def get_all_user_data():
    """Retrieve all stored user data (status, favorites, notes)."""
    try:
        data = load_user_data()
        return data
    except Exception as e:
        print(f"Error loading user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load user data")

@app.put("/api/user_data/{platform}/{filename_base}")
async def update_single_item_user_data(platform: str, filename_base: str, updates: UserDataItemUpdate):
    """Update the status, favorite, or notes for a specific item."""
    try:
        # Convert Pydantic model to dict, excluding unset values
        update_dict = updates.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No update data provided")
            
        updated_item_data = update_user_data_for_item(
            platform,
            filename_base,
            update_dict
        )
        return updated_item_data # Return the updated data for the specific item
    except Exception as e:
        print(f"Error updating user data for {platform}/{filename_base}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user data")

# Catch-all route for client-side routing (must be last)
@app.get("/{rest_of_path:path}")
async def serve_viewer_spa(rest_of_path: str):
    """Serve the main index.html for any path to support client-side routing."""
    index_path = NEW_VIEWER_DIRECTORY / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Viewer index.html not found. Did you build it?")
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 