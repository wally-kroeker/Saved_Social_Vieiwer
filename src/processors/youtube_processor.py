"""
YouTube processor module for the Process Saved Links application.

This module provides functionality for downloading and processing YouTube videos,
including video download, thumbnail extraction, and transcript generation using
yt-dlp and offmute.
"""
import os
import re
import json
import tempfile
import subprocess
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import yt_dlp

from processors.base_processor import BaseProcessor
from utils.logging_utils import get_logger
import config
from config import OUTPUT_DIR

class YouTubeProcessor(BaseProcessor):
    """
    Processor for handling YouTube videos.
    
    This class implements the BaseProcessor interface for YouTube content,
    providing functionality to download videos and generate transcripts.
    """
    
    def __init__(self):
        """Initialize the YouTube processor."""
        super().__init__("youtube")
        self.logger = get_logger("youtube_processor")
        
        # YouTube URL patterns - using looser patterns to match more URLs
        self.url_patterns = [
            r'(?:https?://)?(?:www\.)?youtu(?:be\.com|\.be).*',
            r'(?:https?://)?(?:www\.)?youtube\.com/.*',
        ]
    
    def can_process(self, url: str) -> bool:
        """
        Check if this processor can handle the given URL.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if this processor can handle the URL, False otherwise
        """
        self.logger.info(f"Checking if processor can handle URL: {url}")
        
        # More specific YouTube URL patterns
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',   # Standard YouTube
            r'https?://(?:www\.)?youtu\.be/[\w-]+',               # Short YouTube 
            r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',     # YouTube shorts
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+'       # Embedded YouTube
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                self.logger.info(f"URL {url} matches YouTube pattern: {pattern}")
                return True
                
        # Check if URL contains youtube.com or youtu.be using a more general pattern
        if re.search(r'youtu(?:\.be|be\.com)', url):
            self.logger.info(f"URL {url} contains YouTube domain")
            return True
            
        self.logger.info(f"URL {url} does not match any YouTube pattern")
        return False
    
    def extract_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: YouTube video ID or None if extraction failed
        """
        # Try different URL patterns
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11})(?:&|/|$)',  # Standard and mobile URLs
            r'youtu\.be/([0-9A-Za-z_-]{11})',         # Short URLs
            r'shorts/([0-9A-Za-z_-]{11})'             # Shorts URLs
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                self.logger.info(f"Extracted video ID {video_id} from URL {url}")
                return video_id
                
        self.logger.warning(f"Could not extract video ID from URL: {url}")
        return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to be safe for all operating systems.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        # Replace spaces with underscores for offmute compatibility
        sanitized = sanitized.replace(' ', '_')
        # Limit length and remove trailing spaces/dots
        sanitized = sanitized.strip('. ')[:100]
        return sanitized
    
    def process(self, url: str, notion_item: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a YouTube video URL.
        
        Args:
            url (str): YouTube URL to process
            notion_item (dict, optional): Notion database item related to this URL
            
        Returns:
            dict: Processing results including output file paths and metadata
        """
        self.logger.info(f"Processing YouTube URL: {url}")
        
        # Extract video ID
        video_id = self.extract_id_from_url(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure yt-dlp options
            ydl_opts = {
                # Format selection - smaller file size (360p MP4)
                'format': '18',  # 360p MP4 (video+audio, much smaller size)
                'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
                'writethumbnail': True,  # Enable thumbnail download
                'writeinfojson': True,   # Enable metadata download
                'verbose': True,         # More verbose output
                # Add merge options to ensure output is in mp4 format
                'merge_output_format': 'mp4',
                # Add fallbacks
                'ignoreerrors': False,  # Don't ignore errors
                'quiet': False,         # Show output
                'no_warnings': False    # Show warnings
            }
            
            try:
                # Download video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.logger.info(f"Downloading video {video_id}")
                    info = ydl.extract_info(url, download=True)
                    
                    # Get downloaded files
                    video_file = None
                    thumbnail_file = None
                    metadata_file = os.path.join(temp_dir, f"{video_id}.info.json")
                    
                    # List all files in temp directory for debugging
                    self.logger.info(f"Files in temp directory: {os.listdir(temp_dir)}")
                    
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if file.endswith(('.mp4', '.webm', '.mkv')):
                            video_file = file_path
                            self.logger.info(f"Found video file: {file_path}")
                        elif file.endswith(('.jpg', '.png', '.webp')):
                            thumbnail_file = file_path
                            self.logger.info(f"Found thumbnail file: {file_path}")
                        elif file.endswith('.json'):
                            metadata_file = file_path
                            self.logger.info(f"Found metadata file: {file_path}")
                    
                    if not video_file:
                        raise FileNotFoundError("Video file not found after download")
                    
                    # Get metadata for filename
                    title = self._sanitize_filename(info.get("title", "Untitled"))
                    uploader = self._sanitize_filename(info.get("uploader", "unknown"))
                    upload_date = info.get("upload_date", datetime.now().strftime("%Y-%m-%d"))
                    
                    # Format date as YYYY-MM-DD
                    formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                    
                    # Create base filename following platform-username-date-title pattern
                    base_filename = f"{uploader}-{formatted_date}-{title}"
                    self.logger.info(f"Generated base filename: {base_filename}")
                    
                    # Set up output directory
                    output_dir = OUTPUT_DIR / "youtube"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    self.logger.info(f"Using output directory: {output_dir}")
                    
                    output_paths = {
                        "video": os.path.join(output_dir, f"{base_filename}.mp4"),
                        "thumbnail": os.path.join(output_dir, f"{base_filename}.jpg"),
                        "transcript": os.path.join(output_dir, f"{base_filename}.md"),
                        "metadata": os.path.join(output_dir, f"{base_filename}.json")
                    }
                    
                    # Log output paths
                    for key, path in output_paths.items():
                        self.logger.info(f"Output path for {key}: {path}")
                    
                    # Process video file - Convert to mp4 if needed
                    if not video_file.endswith('.mp4'):
                        self.logger.info("Converting video to MP4 format")
                        mp4_file = os.path.join(temp_dir, f"{video_id}.mp4")
                        ffmpeg_cmd = [
                            'ffmpeg', '-i', video_file,
                            '-c:v', 'copy', '-c:a', 'copy',
                            mp4_file
                        ]
                        self.logger.info(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
                        result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
                        self.logger.info(f"ffmpeg output: {result.stdout}")
                        video_file = mp4_file
                    
                    # Copy video to final location (don't use rename which fails after the file is gone)
                    self.logger.info(f"Preparing to copy video. Source path variable: {video_file}")
                    if os.path.exists(video_file):
                        self.logger.info(f"Source file {video_file} exists before copy.")
                    else:
                        self.logger.error(f"Source file {video_file} DOES NOT exist before copy attempt!")
                    self.logger.info(f"Target path: {output_paths['video']}")
                    self.logger.info(f"Copying video file from {video_file} to {output_paths['video']}")
                    shutil.copy2(video_file, output_paths["video"])
                    
                    # Process thumbnail - convert to jpg if needed and copy to final location
                    if thumbnail_file:
                        if not thumbnail_file.endswith('.jpg'):
                            self.logger.info("Converting thumbnail to JPG format")
                            jpg_file = os.path.join(temp_dir, f"{video_id}.jpg")
                            ffmpeg_cmd = [
                                'ffmpeg', '-i', thumbnail_file, jpg_file
                            ]
                            self.logger.info(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
                            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
                            self.logger.info(f"ffmpeg output: {result.stdout}")
                            thumbnail_file = jpg_file
                        
                        self.logger.info(f"Copying thumbnail file to {output_paths['thumbnail']}")
                        shutil.copy2(thumbnail_file, output_paths["thumbnail"])
                    else:
                        # If no thumbnail, create a placeholder file
                        self.logger.warning("No thumbnail file found, creating a placeholder")
                        with open(output_paths["thumbnail"], 'w') as f:
                            f.write("No thumbnail available")
                    
                    # Create metadata in the same format as Instagram
                    metadata = {
                        "title": info.get("title", ""),
                        "description": info.get("description", ""),
                        "uploader": info.get("uploader", ""),
                        "platform": "youtube",  # explicitly mark platform
                        "duration": info.get("duration", 0),
                        "view_count": info.get("view_count", 0),
                        "like_count": info.get("like_count", 0),
                        "upload_date": formatted_date,
                        "processed_date": datetime.now().isoformat(),
                        "video_id": video_id,
                        "original_url": url,
                        "output_filename": base_filename
                    }
                    
                    # Write metadata to JSON file
                    self.logger.info(f"Writing metadata to {output_paths['metadata']}")
                    with open(output_paths["metadata"], 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    # Generate transcript using offmute - no fallback if it fails
                    self.logger.info("Generating transcript using offmute")
                    success = self._generate_transcript(output_paths["video"], output_paths["transcript"])
                    if not success:
                        self.logger.error("Transcript generation failed - no fallback will be created")
                    
                    # Clean up temporary files created by offmute
                    self._cleanup_offmute_files(output_dir)
                    
                    return {
                        "success": True,
                        "video_id": video_id,
                        "output_paths": output_paths,
                        "metadata": metadata,
                        "platform": "youtube",
                        "username": uploader,
                        "title": title
                    }
                    
            except Exception as e:
                import traceback
                self.logger.error(f"Error processing YouTube video: {e}")
                self.logger.error(traceback.format_exc())
                
                # Clean up any temporary files in case of error
                try:
                    self._cleanup_offmute_files(OUTPUT_DIR / "youtube")
                except Exception as cleanup_error:
                    self.logger.error(f"Error during cleanup: {cleanup_error}")
                
                # Create a result with error information
                return {
                    "success": False,
                    "error": str(e),
                    "video_id": video_id,
                    "url": url,
                    "platform": "youtube"
                }
    
    def _cleanup_offmute_files(self, output_dir: Path) -> None:
        """
        Clean up temporary files created by offmute.
        
        Args:
            output_dir (Path): Directory containing files to clean up
        """
        self.logger.info(f"Cleaning up temporary offmute files in {output_dir}")
        
        try:
            # Remove config.json file
            config_json = os.path.join(output_dir, "config.json")
            if os.path.exists(config_json):
                self.logger.info(f"Removing config.json file: {config_json}")
                os.remove(config_json)
            
            # Remove transcription directory
            transcription_dir = os.path.join(output_dir, "transcription")
            if os.path.exists(transcription_dir) and os.path.isdir(transcription_dir):
                self.logger.info(f"Removing transcription directory: {transcription_dir}")
                shutil.rmtree(transcription_dir)
                
            self.logger.info("Temporary offmute files cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up offmute files: {e}")
            # Don't re-raise the exception - we want the processing to continue
            
    def _generate_transcript(self, video_path: str, transcript_path: str) -> bool:
        """
        Generate transcript for a video using offmute.
        
        Args:
            video_path (str): Path to the video file
            transcript_path (str): Path where transcript should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Generating transcript for {video_path} using offmute")
        
        # Get the API key from config (which gets it from environment)
        gemini_api_key = None
        if "GEMINI_API_KEY" in os.environ:
            gemini_api_key = os.environ["GEMINI_API_KEY"]
            self.logger.info("Using GEMINI_API_KEY from environment")
        elif hasattr(config, "GEMINI_API_KEY") and config.GEMINI_API_KEY:
            gemini_api_key = config.GEMINI_API_KEY
            self.logger.info("Using GEMINI_API_KEY from config")
            
        if not gemini_api_key:
            self.logger.error("No GEMINI_API_KEY found - transcript generation will fail")
            return False
        
        try:
            # Ensure the video file exists
            if not os.path.exists(str(video_path)):
                self.logger.error(f"Video file does not exist: {video_path}")
                return False
            
            # Get video duration to determine timeout
            try:
                # Use ffprobe to get video duration
                ffprobe_cmd = [
                    'ffprobe', 
                    '-v', 'error', 
                    '-show_entries', 'format=duration', 
                    '-of', 'default=noprint_wrappers=1:nokey=1', 
                    str(video_path)
                ]
                duration_output = subprocess.check_output(ffprobe_cmd, text=True).strip()
                video_duration = float(duration_output)
                
                # Calculate timeout - 5 minutes base + 1 minute per 10 minutes of video, capped at 30 minutes
                # This is a reasonable balance for most videos
                base_timeout = 300  # 5 minutes
                duration_factor = min(video_duration / 600, 25 * 60)  # 1 minute per 10 minutes, max 25 minutes
                timeout = base_timeout + duration_factor
                
                timeout = min(timeout, 1800)  # Cap at 30 minutes max (1800 seconds)
                
                self.logger.info(f"Video duration: {video_duration:.2f} seconds, setting timeout to {timeout:.2f} seconds")
            except Exception as e:
                self.logger.warning(f"Could not determine video duration, using default timeout: {e}")
                timeout = 600  # 10 minutes default timeout
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(str(transcript_path)), exist_ok=True)
            
            # Check file size to warn about potentially long processing times
            file_size_mb = os.path.getsize(str(video_path)) / (1024 * 1024)
            if file_size_mb > 100:  # If file is larger than 100MB
                self.logger.warning(f"Large video file: {file_size_mb:.2f}MB. Transcription may take a long time.")
            
            # Use direct npx offmute approach
            self.logger.info("Running npx offmute directly")
            
            # Prepare the command
            command = ["npx", "offmute", str(video_path)]
            
            # Set the environment with the API key
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = gemini_api_key
            
            # Log the command
            self.logger.info(f"Command: {' '.join(command)}")
            self.logger.info(f"Using GEMINI_API_KEY: {gemini_api_key[:4]}...{gemini_api_key[-4:]}")
            
            # Run the command
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=env,
                check=False,  # Don't raise an exception on non-zero exit
                timeout=timeout   # Use calculated timeout
            )
            
            # Log the output regardless of success
            self.logger.info(f"Command exit code: {process.returncode}")
            self.logger.info(f"Command stdout: {process.stdout}")
            
            if process.returncode != 0:
                self.logger.error(f"Command stderr: {process.stderr}")
                return False
            
            # Check for the generated transcript file
            # The offmute tool adds "_transcription.md" to the original filename
            video_basename = os.path.basename(str(video_path))
            video_name_without_ext = os.path.splitext(video_basename)[0]
            transcript_filename = f"{video_name_without_ext}_transcription.md"
            video_dir = os.path.dirname(str(video_path))
            generated_transcript = os.path.join(video_dir, transcript_filename)
            
            self.logger.info(f"Looking for transcript at: {generated_transcript}")
            
            if os.path.exists(generated_transcript):
                # Copy the transcript to the output path
                shutil.copy2(generated_transcript, transcript_path)
                self.logger.info(f"Transcript copied from {generated_transcript} to {transcript_path}")
                
                # Remove the original transcript file
                try:
                    os.remove(generated_transcript)
                    self.logger.info(f"Removed original transcript file: {generated_transcript}")
                except Exception as e:
                    self.logger.warning(f"Could not remove original transcript file: {e}")
                
                return True
            else:
                # Look for any transcription files in the directory
                import glob
                possible_transcripts = glob.glob(os.path.join(video_dir, "*_transcription.md"))
                
                if possible_transcripts:
                    # Use the most recent one
                    latest_transcript = max(possible_transcripts, key=os.path.getmtime)
                    self.logger.info(f"Found alternative transcript: {latest_transcript}")
                    # Copy to the output path
                    shutil.copy2(latest_transcript, transcript_path)
                    self.logger.info(f"Transcript copied from {latest_transcript} to {transcript_path}")
                    return True
                
                self.logger.error(f"No transcript file found after offmute processing")
                return False
                
        except subprocess.TimeoutExpired as e:
            import traceback
            self.logger.error(f"Transcription timed out after {e.timeout} seconds. Video may be too long for transcription.")
            self.logger.error(f"Consider using a shorter video or increasing the timeout. Original error: {e}")
            self.logger.error(traceback.format_exc())
            return False
        except Exception as e:
            import traceback
            self.logger.error(f"Error generating transcript: {e}")
            self.logger.error(traceback.format_exc())
            return False
