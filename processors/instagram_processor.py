"""
Instagram processor module for the Process Saved Links application.

This module provides the InstagramProcessor class for processing Instagram links.
It uses our internal instagram_downloader.py script to download Instagram content.
"""
import os
import re
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import shutil

import config
from utils.logging_utils import get_logger
from processors.base_processor import BaseProcessor
from utils.file_utils import generate_output_path, copy_file
from scripts.instagram_downloader import download_instagram_post
from scripts.offmute import transcribe_video

logger = get_logger("instagram_processor")

class InstagramProcessor(BaseProcessor):
    """
    Processor for Instagram content.
    
    This class handles the downloading and processing of Instagram posts,
    reels, and stories using our instagram_downloader.py script.
    """
    
    def __init__(self):
        """
        Initialize the InstagramProcessor.
        """
        super().__init__("instagram")
        # Get the session path from config if available
        self.session_path = self.config.get("session_path", "")
        
        if not self.session_path:
            # Try to find a session file in the default location
            default_path = os.path.expanduser("~/.config/instaloader/session-walub")
            if os.path.exists(default_path):
                self.session_path = default_path
                logger.info(f"Using Instagram session from default location: {self.session_path}")
            else:
                logger.warning("No Instagram session file found")
        elif not os.path.exists(self.session_path):
            logger.warning(f"Instagram session file not found at: {self.session_path}")
        
        # Check if Offmute is enabled
        self.offmute_enabled = config.OFFMUTE_ENABLED
        if self.offmute_enabled:
            logger.info("Offmute transcription enabled")
        else:
            logger.warning("Offmute transcription disabled. Set OFFMUTE_API_KEY in config or .env")
    
    def can_process(self, url: str) -> bool:
        """
        Check if this processor can handle the given URL.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if this processor can handle the URL, False otherwise
        """
        # Check if the URL is an Instagram URL
        instagram_patterns = [
            r'https?://(?:www\.)?instagram\.com/p/[^/]+/?',
            r'https?://(?:www\.)?instagram\.com/reel/[^/]+/?',
            r'https?://(?:www\.)?instagram\.com/stories/[^/]+/[^/]+/?'
        ]
        
        for pattern in instagram_patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def extract_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract a unique identifier from the Instagram URL.
        
        Args:
            url (str): URL to extract ID from
            
        Returns:
            str: Extracted ID or None if extraction failed
        """
        # Extract the post/reel ID from the URL
        patterns = [
            r'instagram\.com/p/([^/]+)/?',
            r'instagram\.com/reel/([^/]+)/?',
            r'instagram\.com/stories/[^/]+/([^/]+)/?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                # Remove any query parameters
                shortcode = match.group(1).split('?')[0]
                return shortcode
        
        return None
    
    def process(self, url: str, notion_item: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process the Instagram content at the given URL.
        
        Args:
            url (str): URL to process
            notion_item (dict, optional): Notion database item related to this URL
            
        Returns:
            dict: Processing results including output file paths and metadata
        """
        logger.info(f"Processing Instagram URL: {url}")
        
        # Extract content ID from URL
        content_id = self.extract_id_from_url(url)
        if not content_id:
            logger.error(f"Could not extract content ID from URL: {url}")
            return None
        
        # Generate output paths
        output_paths = self.generate_output_paths(content_id)
        
        # Add output_dir to the paths dictionary
        output_paths["output_dir"] = generate_output_path(
            self.platform_name,
            content_id,
            "",
            ""
        ).parent
        
        # Create a temporary directory for downloading
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the content using our instagram_downloader.py script
            downloaded_files = download_instagram_post(url, temp_dir, self.session_path)
            
            if not downloaded_files:
                logger.error(f"Failed to download content from: {url}")
                return None
            
            # Process the downloaded files
            result = self._process_downloaded_files(downloaded_files, output_paths, content_id)
            
            if result:
                # Add metadata
                metadata = {
                    "url": url,
                    "content_id": content_id,
                    "platform": "instagram",
                    "title": notion_item.get("title", "") if notion_item else "",
                    "processed_files": result
                }
                
                # Save metadata
                self.save_metadata(content_id, metadata)
                
                return result
        
        return None
    
    def _process_downloaded_files(self, downloaded_files: Dict[str, Union[str, List[str]]], 
                                 output_paths: Dict[str, Path], 
                                 content_id: str) -> Optional[Dict[str, str]]:
        """
        Process the downloaded files and move them to the output directory.
        
        Args:
            downloaded_files (dict): Dictionary of downloaded file paths
            output_paths (dict): Dictionary of output file paths
            content_id (str): Content ID
            
        Returns:
            dict: Dictionary of processed file paths or None if processing failed
        """
        result = {"success": True}  # Add success flag
        
        try:
            # Extract metadata first to get username and date
            username = None
            date = None
            title = None
            caption = None
            
            if "metadata" in downloaded_files and os.path.exists(downloaded_files["metadata"]):
                try:
                    with open(downloaded_files["metadata"], "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    
                    # Extract username
                    if "node" in metadata and "owner" in metadata["node"]:
                        username = metadata["node"]["owner"]["username"]
                    elif "owner_username" in metadata:
                        username = metadata["owner_username"]
                    elif "owner" in metadata and "username" in metadata["owner"]:
                        username = metadata["owner"]["username"]
                    
                    # Extract date
                    if "node" in metadata and "taken_at_timestamp" in metadata["node"]:
                        timestamp = metadata["node"]["taken_at_timestamp"]
                        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    elif "taken_at_timestamp" in metadata:
                        timestamp = metadata["taken_at_timestamp"]
                        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    
                    # Extract title/caption
                    if "node" in metadata and "edge_media_to_caption" in metadata["node"]:
                        edges = metadata["node"]["edge_media_to_caption"]["edges"]
                        if edges:
                            caption = edges[0]["node"]["text"]
                            # Take first line or first 100 chars as title, whichever is shorter
                            title = caption.split("\n")[0][:100]
                    elif "edge_media_to_caption" in metadata and "edges" in metadata["edge_media_to_caption"]:
                        edges = metadata["edge_media_to_caption"]["edges"]
                        if edges and "node" in edges[0] and "text" in edges[0]["node"]:
                            caption = edges[0]["node"]["text"]
                            title = caption.split("\n")[0][:100]
                    
                    # If no title was found, use a generic title with the content ID
                    if not title or title.strip() == "":
                        title = f"Instagram Post {content_id}"
                except Exception as e:
                    logger.warning(f"Error extracting metadata: {e}")
            
            # If username isn't set, try to get it from the downloaded_files
            if not username and "username" in downloaded_files:
                username = downloaded_files["username"]
            
            # If date isn't set, use today's date
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Set platform explicitly for new file naming
            platform = "instagram"
            
            # Use our new filename utilities to generate consistent paths
            from utils.filename_utils import get_output_paths as get_standardized_paths
            standardized_paths = get_standardized_paths(
                platform=platform,
                username=username,
                date=date,
                title=title,
                use_platform_subdir=True
            )
            
            # Process video
            if "video" in downloaded_files and os.path.exists(downloaded_files["video"]):
                video_path = copy_file(
                    downloaded_files["video"],
                    standardized_paths["video"],
                    username=username,
                    date=date,
                    title=title
                )
                result["video"] = str(video_path)
                
                # Process video through offmute if enabled
                if self.offmute_enabled:
                    # Try to generate transcript, but continue even if it fails
                    try:
                        transcript_success = self._generate_transcript_with_offmute(video_path, standardized_paths["transcript"])
                        if transcript_success:
                            result["transcript"] = str(standardized_paths["transcript"])
                        else:
                            logger.warning("Transcript generation failed, but continuing with other processing")
                    except Exception as e:
                        logger.error(f"Error in transcript generation: {e}")
                        logger.warning("Continuing with other processing despite transcript error")
            
            # Process images (for carousel posts)
            if "images" in downloaded_files:
                image_paths = []
                for i, img_path in enumerate(downloaded_files["images"]):
                    if os.path.exists(img_path):
                        # Create a numbered version of the image path
                        from pathlib import Path
                        img_basename = Path(standardized_paths["thumbnail"]).stem
                        img_extension = Path(standardized_paths["thumbnail"]).suffix
                        img_output_path = Path(standardized_paths["thumbnail"]).parent / f"{img_basename}-{i}{img_extension}"
                        
                        img_path_copied = copy_file(
                            img_path, 
                            img_output_path,
                            username=username,
                            date=date,
                            title=title
                        )
                        image_paths.append(str(img_path_copied))
                
                if image_paths:
                    result["images"] = image_paths
                    
                    # Use the first image as the thumbnail if no specific thumbnail was set
                    if "thumbnail" not in result and image_paths:
                        thumbnail_path = copy_file(
                            downloaded_files["images"][0],
                            standardized_paths["thumbnail"],
                            username=username,
                            date=date,
                            title=title
                        )
                        result["thumbnail"] = str(thumbnail_path)
            
            # Process thumbnail
            if "thumbnail" in downloaded_files and os.path.exists(downloaded_files["thumbnail"]):
                thumbnail_path = copy_file(
                    downloaded_files["thumbnail"],
                    standardized_paths["thumbnail"],
                    username=username,
                    date=date,
                    title=title
                )
                result["thumbnail"] = str(thumbnail_path)
            
            # Process caption/transcript (only if offmute didn't create one)
            if caption and "transcript" not in result:
                # Create a simple markdown transcript
                transcript_text = f"# Instagram Post by {username}\n\n{caption}"
                
                # Save the transcript with consistent naming
                with open(standardized_paths["transcript"], "w", encoding="utf-8") as f:
                    f.write(transcript_text)
                
                result["transcript"] = str(standardized_paths["transcript"])
            
            # Process metadata
            if "metadata" in downloaded_files and os.path.exists(downloaded_files["metadata"]):
                # Read the metadata
                with open(downloaded_files["metadata"], "r", encoding="utf-8") as f:
                    raw_metadata = json.load(f)
                
                # Add platform information
                raw_metadata["platform"] = "instagram"
                if username:
                    raw_metadata["owner_username"] = username
                
                # Copy the metadata file
                metadata_file_copied = copy_file(
                    downloaded_files["metadata"],
                    standardized_paths["metadata"],
                    username=username,
                    date=date,
                    title=title
                )
                
                # Also update the metadata file with additional information
                with open(metadata_file_copied, "w", encoding="utf-8") as f:
                    json.dump(raw_metadata, f, indent=2, ensure_ascii=False)
                    
                result["metadata"] = str(metadata_file_copied)
            
            # Include username in the result
            if username:
                result["username"] = username
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing downloaded files: {e}")
            return None
    
    def _generate_transcript_with_offmute(self, video_path: Union[str, Path], output_path: Union[str, Path]) -> bool:
        """
        Generate a transcript for a video using offmute.
        
        Args:
            video_path (str or Path): Path to the video file
            output_path (str or Path): Path to save the transcript
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Generating transcript for video: {video_path}")
        
        # Get the API key from config (which gets it from environment)
        gemini_api_key = config.GEMINI_API_KEY
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables or config")
            return False
        
        try:
            # Ensure the video file exists
            if not os.path.exists(str(video_path)):
                logger.error(f"Video file does not exist: {video_path}")
                return False
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(str(output_path)), exist_ok=True)
            
            # Use only the direct npx offmute approach
            logger.info("Running npx offmute directly")
            
            # Prepare the command
            command = ["npx", "offmute", str(video_path)]
            
            # Set the environment with the API key
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = gemini_api_key
            
            # Log the command
            logger.info(f"Command: {' '.join(command)}")
            logger.info(f"Using GEMINI_API_KEY: {gemini_api_key[:4]}...{gemini_api_key[-4:]}")
            
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
            logger.info(f"Command exit code: {process.returncode}")
            logger.info(f"Command stdout: {process.stdout}")
            
            if process.returncode != 0:
                logger.error(f"Command stderr: {process.stderr}")
                return False
            
            # Check for the generated transcript file
            # The offmute tool adds "_transcription.md" to the original filename
            video_basename = os.path.basename(str(video_path))
            video_name_without_ext = os.path.splitext(video_basename)[0]
            transcript_filename = f"{video_name_without_ext}_transcription.md"
            video_dir = os.path.dirname(str(video_path))
            generated_transcript = os.path.join(video_dir, transcript_filename)
            
            logger.info(f"Looking for transcript at: {generated_transcript}")
            
            if os.path.exists(generated_transcript):
                # Instead of copying, read the content and write it to our standardized path
                with open(generated_transcript, 'r', encoding='utf-8') as src_file:
                    transcript_content = src_file.read()
                
                # Write to our standardized path
                with open(output_path, 'w', encoding='utf-8') as dest_file:
                    dest_file.write(transcript_content)
                    
                logger.info(f"Transcript moved from {generated_transcript} to {output_path}")
                
                # Remove the original transcript file
                try:
                    os.remove(generated_transcript)
                except:
                    logger.warning(f"Could not remove original transcript file: {generated_transcript}")
                    
                return True
            else:
                # Look for any transcription files in the directory
                import glob
                possible_transcripts = glob.glob(os.path.join(video_dir, "*_transcription.md"))
                
                if possible_transcripts:
                    # Use the most recent one
                    latest_transcript = max(possible_transcripts, key=os.path.getmtime)
                    logger.info(f"Found alternative transcript: {latest_transcript}")
                    
                    # Read content and write to our standardized path
                    with open(latest_transcript, 'r', encoding='utf-8') as src_file:
                        transcript_content = src_file.read()
                    
                    # Write to our standardized path
                    with open(output_path, 'w', encoding='utf-8') as dest_file:
                        dest_file.write(transcript_content)
                        
                    logger.info(f"Transcript moved from {latest_transcript} to {output_path}")
                    
                    # Remove the original transcript file
                    try:
                        os.remove(latest_transcript)
                    except:
                        logger.warning(f"Could not remove original transcript file: {latest_transcript}")
                        
                    return True
                
                logger.error(f"No transcript file found after offmute processing")
                logger.info(f"Files in directory: {os.listdir(video_dir)}")
                return False
                
        except Exception as e:
            import traceback
            logger.error(f"Error generating transcript with offmute: {e}")
            logger.error(traceback.format_exc())
            return False
