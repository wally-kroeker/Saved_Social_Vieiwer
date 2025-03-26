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
                # Format selection - try progressively more flexible options
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4/best[ext=mp4]/best',
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
                    
                    # Create base filename following Instagram pattern:
                    # username-date-caption
                    base_filename = f"{uploader}-{formatted_date}-{title}"
                    self.logger.info(f"Generated base filename: {base_filename}")
                    
                    # Set up output paths using the same pattern as Instagram
                    if hasattr(config, "OUTPUT_DIR") and config.OUTPUT_DIR:
                        output_dir = config.OUTPUT_DIR
                    else:
                        output_dir = "/home/walub/Documents/Processed-ContentIdeas"
                        
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
                    
                    # Move files to final locations
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Convert video to mp4 if needed and move to final location
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
                    
                    self.logger.info(f"Moving video file from {video_file} to {output_paths['video']}")
                    os.rename(video_file, output_paths["video"])
                    
                    self.logger.info(f"Copying video file from {video_file} to {output_paths['video']}")
                    shutil.copy2(video_file, output_paths["video"])
                    
                    # Convert thumbnail to jpg if needed and move to final location
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
                        
                        self.logger.info(f"Moving thumbnail file from {thumbnail_file} to {output_paths['thumbnail']}")
                        os.rename(thumbnail_file, output_paths["thumbnail"])
                    
                    # Save metadata in the same format as Instagram
                    metadata = {
                        "title": info.get("title", ""),
                        "description": info.get("description", ""),
                        "uploader": info.get("uploader", ""),
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
                    
                    # Generate transcript using offmute
                    self.logger.info("Generating transcript")
                    self._generate_transcript(output_paths["video"], output_paths["transcript"])
                    
                    return {
                        "success": True,
                        "video_id": video_id,
                        "output_paths": output_paths,
                        "metadata": metadata
                    }
                    
            except Exception as e:
                import traceback
                self.logger.error(f"Error processing YouTube video: {e}")
                self.logger.error(traceback.format_exc())
                
                # Create a result with error information
                return {
                    "success": False,
                    "error": str(e),
                    "video_id": video_id,
                    "url": url
                }
    
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
            self.logger.warning("No GEMINI_API_KEY found - creating placeholder transcript")
            # Create a placeholder transcript
            with open(transcript_path, 'w') as f:
                f.write("# YouTube Transcript\n\n")
                f.write("Transcript generation requires GEMINI_API_KEY.\n")
                f.write(f"Video: {video_path}\n")
            return False
        
        try:
            # Ensure the video file exists
            if not os.path.exists(str(video_path)):
                self.logger.error(f"Video file does not exist: {video_path}")
                return False
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(str(transcript_path)), exist_ok=True)
            
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
                timeout=300   # Add a timeout of 5 minutes to prevent hanging
            )
            
            # Log the output regardless of success
            self.logger.info(f"Command exit code: {process.returncode}")
            self.logger.info(f"Command stdout: {process.stdout}")
            
            if process.returncode != 0:
                self.logger.error(f"Command stderr: {process.stderr}")
                # Create a fallback transcript with the error
                with open(transcript_path, 'w') as f:
                    f.write("# YouTube Transcript (Error)\n\n")
                    f.write(f"Error running offmute: {process.stderr}\n")
                    f.write(f"Video: {video_path}\n")
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
                # Create a fallback transcript
                with open(transcript_path, 'w') as f:
                    f.write("# YouTube Transcript (Not Generated)\n\n")
                    f.write("Offmute ran successfully but no transcript was created.\n")
                    f.write(f"Video: {video_path}\n")
                return False
                
        except Exception as e:
            import traceback
            self.logger.error(f"Error generating transcript: {e}")
            self.logger.error(traceback.format_exc())
            
            # Create a simple fallback transcript
            with open(transcript_path, 'w') as f:
                f.write("# YouTube Transcript (Error)\n\n")
                f.write(f"Error generating transcript: {str(e)}\n")
                f.write(f"Video: {video_path}\n")
            
            return False
