import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define paths
OUTPUT_DIRECTORY = PROJECT_ROOT / 'output'
STATIC_DIRECTORY = Path(__file__).resolve().parent / 'static'
TEMPLATES_DIRECTORY = Path(__file__).resolve().parent / 'templates'

# Create FastAPI app
app = FastAPI(title="Content Viewer")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIRECTORY)), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIRECTORY))

# Define content item model
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
                 has_metadata: bool = False):
        self.platform = platform
        self.filename = filename
        self.file_path = file_path
        self.username = username
        self.date = date
        self.title = title
        self.has_transcript = has_transcript
        self.has_thumbnail = has_thumbnail
        self.has_metadata = has_metadata
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "filename": self.filename,
            "username": self.username,
            "date": self.date,
            "title": self.title,
            "has_transcript": self.has_transcript,
            "has_thumbnail": self.has_thumbnail,
            "has_metadata": self.has_metadata,
            "base_path": f"{self.platform}/{self.filename}"
        }

# Content discovery functions
def discover_content() -> List[ContentItem]:
    """Scan the output directory for content files"""
    content_items = []
    
    # Check if output directory exists
    if not OUTPUT_DIRECTORY.exists():
        print(f"Output directory does not exist: {OUTPUT_DIRECTORY}")
        return content_items
    
    # Scan platform directories
    for platform_dir in OUTPUT_DIRECTORY.iterdir():
        if not platform_dir.is_dir():
            continue
        
        platform = platform_dir.name
        print(f"Scanning platform directory: {platform}")
        
        # Scan content files
        file_extensions = {".mp4", ".jpg", ".jpeg", ".png", ".md", ".json"}
        found_files = {}
        
        for file_path in platform_dir.glob("**/*"):
            if not file_path.is_file():
                continue
                
            if file_path.suffix.lower() not in file_extensions:
                continue
            
            # Group files by base name (without extension)
            base_name = file_path.stem
            if base_name not in found_files:
                found_files[base_name] = []
            found_files[base_name].append(file_path)
        
        # Create content items
        for base_name, files in found_files.items():
            # Check for video file
            video_files = [f for f in files if f.suffix.lower() == ".mp4"]
            if not video_files:
                continue  # Skip if no video file
            
            video_path = video_files[0]
            filename = video_path.name
            
            # Check for transcript, thumbnail, and metadata
            has_transcript = any(f.suffix.lower() == ".md" for f in files)
            has_thumbnail = any(f.suffix.lower() in [".jpg", ".jpeg", ".png"] for f in files)
            has_metadata = any(f.suffix.lower() == ".json" for f in files)
            
            # Extract metadata from filename
            parts = base_name.split('-')
            
            # Standard format: platform-username-date-title
            username = parts[1] if len(parts) > 1 else ""
            date_str = parts[2] if len(parts) > 2 else ""
            
            # Format the title properly - join all remaining parts and replace hyphens with spaces
            if len(parts) > 3:
                # Create a better title by joining the remaining parts and properly formatting
                raw_title = ' '.join(parts[3:]).replace('-', ' ')
                # Clean up multiple spaces
                title = re.sub(r'\s+', ' ', raw_title).strip()
            else:
                title = base_name
            
            # Format date if it's in YYMMDD format
            if date_str and re.match(r'^[0-9]{6}$', date_str):
                try:
                    # Parse YYMMDD format
                    year = 2000 + int(date_str[0:2])
                    month = int(date_str[2:4])
                    day = int(date_str[4:6])
                    # Create a proper date string
                    date_obj = datetime(year, month, day)
                    # Store in ISO format for easy parsing in JavaScript
                    date_str = date_obj.strftime('%Y-%m-%d')
                except (ValueError, IndexError):
                    # Keep original if parsing fails
                    pass
            
            content_item = ContentItem(
                platform=platform,
                filename=base_name,
                file_path=video_path,
                username=username,
                date=date_str,
                title=title,
                has_transcript=has_transcript,
                has_thumbnail=has_thumbnail,
                has_metadata=has_metadata
            )
            
            content_items.append(content_item)
    
    # Sort by date (newest first)
    content_items.sort(key=lambda x: x.date if x.date else "", reverse=True)
    
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

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Content Viewer"}
    )

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 