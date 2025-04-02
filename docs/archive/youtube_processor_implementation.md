# YouTube Processor Implementation Plan

This document outlines the detailed implementation plan for the YouTube processor component of the Process Saved Links project.

## Overview

The YouTube processor will be responsible for:
1. Validating YouTube URLs
2. Downloading YouTube videos
3. Processing the videos through offmute
4. Generating transcripts
5. Creating thumbnails
6. Producing standardized output files

## Implementation Steps

### 1. Create the Base Structure

```python
# processors/youtube_processor.py

from .base_processor import BaseProcessor
import os
import subprocess
import re
import logging

logger = logging.getLogger(__name__)

class YouTubeProcessor(BaseProcessor):
    """Processor for YouTube links"""
    
    def __init__(self, config):
        super().__init__(config)
        self.output_dir = config.get('output_dir')
        self.temp_dir = config.get('temp_dir')
        self.offmute_path = config.get('offmute_path')
        
    def validate_url(self, url):
        """Check if the URL is a valid YouTube URL"""
        youtube_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def process(self, url, metadata):
        """Process a YouTube URL and return the output paths"""
        # Implementation will go here
        pass
        
    def download_content(self, url):
        """Download a YouTube video using yt-dlp"""
        # Implementation will go here
        pass
        
    def generate_transcript(self, video_path):
        """Generate a transcript from the video"""
        # Implementation will go here
        pass
        
    def extract_thumbnail(self, video_path):
        """Extract a thumbnail from the video"""
        # Implementation will go here
        pass
        
    def process_audio(self, video_path):
        """Process the video through offmute"""
        # Implementation will go here
        pass
```

### 2. Implement URL Validation and Video Download

```python
def download_content(self, url):
    """Download a YouTube video using yt-dlp"""
    logger.info(f"Downloading YouTube video: {url}")
    
    # Create a temporary directory for the download
    os.makedirs(self.temp_dir, exist_ok=True)
    
    # Extract video ID from URL
    video_id = self._extract_video_id(url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    # Set output filename
    output_template = os.path.join(self.temp_dir, f"{video_id}.%(ext)s")
    
    # Prepare yt-dlp command
    command = [
        "yt-dlp",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--output", output_template,
        "--write-auto-sub",
        "--write-thumbnail",
        url
    ]
    
    try:
        # Run the command
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Find the downloaded video file
        for file in os.listdir(self.temp_dir):
            if file.startswith(video_id) and file.endswith(".mp4"):
                video_path = os.path.join(self.temp_dir, file)
                logger.info(f"Successfully downloaded video to: {video_path}")
                return video_path
        
        logger.error("Video download completed but could not find output file")
        return None
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading YouTube video: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return None
        
def _extract_video_id(self, url):
    """Extract the video ID from a YouTube URL"""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None
```

### 3. Implement Audio Processing with Offmute

```python
def process_audio(self, video_path):
    """Process the video through offmute"""
    logger.info(f"Processing audio with offmute: {video_path}")
    
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return None
    
    # Create output path
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(self.temp_dir, f"{base_name}_processed.mp4")
    
    # Prepare offmute command
    command = [
        self.offmute_path,
        "--input", video_path,
        "--output", output_path
    ]
    
    try:
        # Run the command
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        if os.path.exists(output_path):
            logger.info(f"Successfully processed audio: {output_path}")
            return output_path
        else:
            logger.error("Audio processing completed but could not find output file")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing audio: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return None
```

### 4. Implement Transcript Generation

```python
def generate_transcript(self, video_path):
    """Generate a transcript from the video"""
    logger.info(f"Generating transcript for: {video_path}")
    
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return None
    
    # Create output path
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    
    # Check if subtitles were downloaded by yt-dlp
    subtitle_path = os.path.join(self.temp_dir, f"{base_name}.en.vtt")
    if not os.path.exists(subtitle_path):
        logger.warning(f"No subtitles found for: {video_path}")
        # Try to generate subtitles using speech recognition
        return self._generate_transcript_from_audio(video_path)
    
    # Convert VTT to markdown
    markdown_path = os.path.join(self.temp_dir, f"{base_name}.md")
    
    try:
        # Parse VTT and convert to markdown
        with open(subtitle_path, 'r', encoding='utf-8') as vtt_file:
            vtt_content = vtt_file.read()
        
        # Simple VTT to markdown conversion
        markdown_content = self._convert_vtt_to_markdown(vtt_content)
        
        # Write markdown file
        with open(markdown_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        
        logger.info(f"Successfully generated transcript: {markdown_path}")
        return markdown_path
        
    except Exception as e:
        logger.error(f"Error generating transcript: {e}")
        return None
        
def _convert_vtt_to_markdown(self, vtt_content):
    """Convert VTT content to markdown format"""
    lines = vtt_content.split('\n')
    markdown_lines = []
    current_text = ""
    
    # Skip header
    start_processing = False
    
    for line in lines:
        if not start_processing:
            if line.strip() == "":
                start_processing = True
            continue
        
        # Skip timing lines and cue identifiers
        if re.match(r'\d{2}:\d{2}:\d{2}', line) or line.strip().isdigit() or line.strip() == "":
            if current_text:
                markdown_lines.append(current_text)
                current_text = ""
            continue
        
        # Add text content
        if current_text:
            current_text += " " + line.strip()
        else:
            current_text = line.strip()
    
    # Add any remaining text
    if current_text:
        markdown_lines.append(current_text)
    
    # Format as markdown
    markdown_content = "# Video Transcript\n\n"
    for i, line in enumerate(markdown_lines):
        if line.strip():
            markdown_content += f"{line}\n\n"
    
    return markdown_content
    
def _generate_transcript_from_audio(self, video_path):
    """Generate transcript using speech recognition (fallback)"""
    # This would be implemented if needed, using a speech recognition library
    logger.warning("Speech recognition for transcript generation not implemented")
    
    # Create a placeholder transcript
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    markdown_path = os.path.join(self.temp_dir, f"{base_name}.md")
    
    with open(markdown_path, 'w', encoding='utf-8') as md_file:
        md_file.write("# Video Transcript\n\n")
        md_file.write("*Transcript not available for this video.*\n")
    
    return markdown_path
```

### 5. Implement Thumbnail Extraction

```python
def extract_thumbnail(self, video_path):
    """Extract a thumbnail from the video"""
    logger.info(f"Extracting thumbnail for: {video_path}")
    
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return None
    
    # Create output path
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    
    # Check if thumbnail was downloaded by yt-dlp
    for ext in ['.jpg', '.png', '.webp']:
        thumbnail_path = os.path.join(self.temp_dir, f"{base_name}{ext}")
        if os.path.exists(thumbnail_path):
            # Convert to jpg if needed
            if not thumbnail_path.endswith('.jpg'):
                jpg_path = os.path.join(self.temp_dir, f"{base_name}.jpg")
                self._convert_to_jpg(thumbnail_path, jpg_path)
                return jpg_path
            return thumbnail_path
    
    # If no thumbnail was downloaded, extract one from the video
    thumbnail_path = os.path.join(self.temp_dir, f"{base_name}.jpg")
    
    # Use ffmpeg to extract a frame from the middle of the video
    command = [
        "ffmpeg",
        "-i", video_path,
        "-ss", "00:00:05",  # 5 seconds in
        "-frames:v", "1",
        thumbnail_path
    ]
    
    try:
        # Run the command
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        if os.path.exists(thumbnail_path):
            logger.info(f"Successfully extracted thumbnail: {thumbnail_path}")
            return thumbnail_path
        else:
            logger.error("Thumbnail extraction completed but could not find output file")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting thumbnail: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return None
        
def _convert_to_jpg(self, input_path, output_path):
    """Convert an image to JPG format"""
    command = [
        "ffmpeg",
        "-i", input_path,
        output_path
    ]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting image to JPG: {e}")
        return False
```

### 6. Implement the Main Process Method

```python
def process(self, url, metadata):
    """Process a YouTube URL and return the output paths"""
    logger.info(f"Processing YouTube URL: {url}")
    
    # Validate URL
    if not self.validate_url(url):
        logger.error(f"Invalid YouTube URL: {url}")
        return None
    
    # Download the video
    video_path = self.download_content(url)
    if not video_path:
        logger.error(f"Failed to download video from: {url}")
        return None
    
    # Process the audio
    processed_video = self.process_audio(video_path)
    if not processed_video:
        logger.warning(f"Audio processing failed, using original video: {video_path}")
        processed_video = video_path
    
    # Generate transcript
    transcript_path = self.generate_transcript(video_path)
    
    # Extract thumbnail
    thumbnail_path = self.extract_thumbnail(video_path)
    
    # Generate standardized output paths
    timestamp = metadata.get('timestamp', datetime.datetime.now().strftime('%Y-%m-%d'))
    title = metadata.get('title', 'YouTube Video')
    
    # Create standardized filename base
    filename_base = f"youtube-{timestamp}-{self._sanitize_filename(title)}"
    
    # Create final output paths
    final_video_path = os.path.join(self.output_dir, f"{filename_base}.mp4")
    final_thumbnail_path = os.path.join(self.output_dir, f"{filename_base}.jpg")
    final_transcript_path = os.path.join(self.output_dir, f"{filename_base}.md")
    
    # Copy files to final location
    shutil.copy2(processed_video, final_video_path)
    
    if thumbnail_path:
        shutil.copy2(thumbnail_path, final_thumbnail_path)
    
    if transcript_path:
        shutil.copy2(transcript_path, final_transcript_path)
    
    # Clean up temporary files
    self._cleanup_temp_files(video_path)
    
    # Return the paths to the processed files
    return {
        'video': final_video_path,
        'thumbnail': final_thumbnail_path if thumbnail_path else None,
        'transcript': final_transcript_path if transcript_path else None
    }
    
def _sanitize_filename(self, filename):
    """Sanitize a string to be used as a filename"""
    # Replace spaces with hyphens
    filename = filename.replace(' ', '-')
    # Remove any non-alphanumeric characters except hyphens
    filename = re.sub(r'[^a-zA-Z0-9-]', '', filename)
    # Limit length
    if len(filename) > 50:
        filename = filename[:50]
    return filename
    
def _cleanup_temp_files(self, video_path):
    """Clean up temporary files"""
    try:
        # Get the base name without extension
        base_path = os.path.splitext(video_path)[0]
        
        # Remove all files with this base name
        for file in os.listdir(self.temp_dir):
            if file.startswith(os.path.basename(base_path)):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")
```

## Integration with the Main System

The YouTube processor will be integrated into the main system through the processor factory pattern:

```python
# processors/__init__.py

from .instagram_processor import InstagramProcessor
from .youtube_processor import YouTubeProcessor

def get_processor(url, config):
    """Factory function to get the appropriate processor for a URL"""
    
    # Initialize processors
    instagram_processor = InstagramProcessor(config)
    youtube_processor = YouTubeProcessor(config)
    
    # Check which processor can handle the URL
    if instagram_processor.validate_url(url):
        return instagram_processor
    elif youtube_processor.validate_url(url):
        return youtube_processor
    
    # No suitable processor found
    return None
```

## Testing Plan

1. **Unit Tests**:
   - Test URL validation with various YouTube URL formats
   - Test video ID extraction
   - Test thumbnail extraction
   - Test transcript generation

2. **Integration Tests**:
   - Test the complete processing of a YouTube video
   - Verify output file formats and naming
   - Test handling of various video types (short, long, with/without captions)

3. **Error Handling Tests**:
   - Test behavior with invalid URLs
   - Test behavior when download fails
   - Test behavior when processing fails

## Dependencies

- yt-dlp: For downloading YouTube videos
- ffmpeg: For video processing and thumbnail extraction
- offmute: For audio processing
- Python libraries: os, subprocess, re, shutil, datetime

## Conclusion

This implementation plan provides a detailed guide for developing the YouTube processor component. By following this plan, the developer can create a robust module that integrates seamlessly with the rest of the system and handles YouTube content processing effectively.