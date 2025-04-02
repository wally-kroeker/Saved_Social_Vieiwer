"""
Configuration settings for the Process Saved Links application.

This module contains all configurable parameters including API keys,
file paths, scheduling settings, and platform-specific configurations.
"""
import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv is not required, but recommended

# Base directories
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", BASE_DIR / "output"))

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Notion API settings
NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")

# Platform processor settings
PLATFORMS = {
    "instagram": {
        "enabled": True,
        "session_path": os.path.join(BASE_DIR, "sessions", "session-walub"),
        "output_subdir": "instagram"
    },
    "youtube": {
        "enabled": True,
        "output_subdir": "youtube"
    },
    "twitter": {
        "enabled": False,
        "output_subdir": "twitter"
    }
}

# Offmute settings for transcription (if used)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OFFMUTE_API_KEY = GEMINI_API_KEY  # For backward compatibility
OFFMUTE_ENABLED = GEMINI_API_KEY != ""

# Scheduling settings
SCHEDULER_INTERVAL_MINUTES = 15
SCHEDULER_MAX_ITEMS_PER_RUN = 5

# Logging settings
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# File Paths
SCRIPTS_DIR = BASE_DIR / "scripts"

# Scheduling Configuration
RUN_TIMES = {
    "morning": "08:00",
    "noon": "12:00",
    "evening": "23:00"  # 11:00 PM
}
PAUSE_BETWEEN_ITEMS = 15 * 60  # 15 minutes in seconds

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Output Format Configuration
OUTPUT_FORMAT = {
    "video_extension": "mp4",
    "thumbnail_extension": "jpg",
    "transcript_extension": "md",
    "metadata_extension": "json",
}

# Create necessary directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
