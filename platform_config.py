"""
Platform-specific configuration for the Process Saved Links application.

This file contains settings specific to each platform, such as batch sizes,
rate limiting, and other platform-specific parameters.
"""

# YouTube settings
YOUTUBE_BATCH_SIZE = 5  # Process up to 5 YouTube links at once
YOUTUBE_DELAY_SECONDS = 0  # No delay needed between YouTube link processing

# Instagram settings
INSTAGRAM_BATCH_SIZE = 1  # Process only 1 Instagram link at a time
INSTAGRAM_DELAY_SECONDS = 900  # 15 minutes delay between Instagram link processing

# General settings
DEFAULT_BATCH_SIZE = 1
DEFAULT_DELAY_SECONDS = 0 