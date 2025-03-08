#!/usr/bin/env python
"""
Offmute Transcription Script for the Process Saved Links application.

This script provides functionality to transcribe video/audio content using
the Offmute transcription service. It takes a video file as input and
returns a transcript in markdown format.
"""
import os
import sys
import json
import argparse
import tempfile
import requests
import logging
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("offmute")

# Try to import from the project's config, fall back to environment variables if needed
try:
    from config import OFFMUTE_API_KEY
except ImportError:
    OFFMUTE_API_KEY = os.environ.get("OFFMUTE_API_KEY", "")

# Base URL for the Offmute API
# Changed from api.offmute.com which seems to have DNS resolution issues
OFFMUTE_API_URL = "https://api.gemini-offmute.com/v1"

def transcribe_video(video_path, api_key=None, output_path=None, language="en"):
    """
    Transcribe a video using the Offmute API.
    
    Args:
        video_path (str): Path to the video file
        api_key (str, optional): Offmute API key, defaults to config or env var
        output_path (str, optional): Path to save the transcript, defaults to video_path.md
        language (str, optional): Language code, defaults to English
        
    Returns:
        str: Path to the transcript file or None if failed
    """
    # Check if video exists
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return None
    
    # Use provided API key or fall back to default
    api_key = api_key or OFFMUTE_API_KEY
    if not api_key:
        logger.error("No Offmute API key provided. Set OFFMUTE_API_KEY env var or pass as argument.")
        return None
    
    # Default output path
    if not output_path:
        output_path = os.path.splitext(video_path)[0] + ".md"
    
    try:
        logger.info(f"Uploading video for transcription: {video_path}")
        
        # Try the API method first
        result = _try_api_transcription(video_path, api_key, output_path, language)
        if result:
            return result
            
        # If API fails, immediately try the command-line method
        logger.info("API method failed, trying command-line fallback...")
        return _try_command_line_transcription(video_path, api_key, output_path)
            
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

def _try_api_transcription(video_path, api_key, output_path, language):
    """
    Try transcribing using the Offmute API.
    """
    try:
        # 1. Upload the video file
        with open(video_path, "rb") as video_file:
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            files = {
                "file": (os.path.basename(video_path), video_file)
            }
            
            data = {
                "language": language,
                "model": "general",  # Use general model
                "format": "markdown"  # Request markdown format
            }
            
            # Try API with a short timeout to fail faster if not available
            response = requests.post(
                f"{OFFMUTE_API_URL}/transcriptions", 
                headers=headers,
                files=files,
                data=data,
                timeout=5  # Short timeout to quickly fall back if API is down
            )
            
            if response.status_code != 202:
                logger.error(f"Error uploading video: {response.status_code} - {response.text}")
                return None
            
            # Extract job ID from response
            job_data = response.json()
            job_id = job_data.get("id")
            
            if not job_id:
                logger.error("No job ID received from Offmute API")
                return None
            
            logger.info(f"Transcription job started with ID: {job_id}")
        
        # 2. Poll for job completion
        max_attempts = 30  # Maximum number of attempts (30 * 10 seconds = 5 minutes)
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Check job status
            status_response = requests.get(
                f"{OFFMUTE_API_URL}/transcriptions/{job_id}",
                headers=headers,
                timeout=5  # Short timeout
            )
            
            if status_response.status_code != 200:
                logger.error(f"Error checking job status: {status_response.status_code} - {status_response.text}")
                return None
            
            status_data = status_response.json()
            status = status_data.get("status")
            
            if status == "completed":
                # Job completed successfully
                transcript_text = status_data.get("transcript", "")
                
                if not transcript_text:
                    logger.warning("Transcription completed but no text received")
                    transcript_text = "# Video Transcript\n\n*No transcript available*"
                
                # Save the transcript
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write("# Video Transcript\n\n")
                        f.write(transcript_text)
                    
                    logger.info(f"Transcript saved to: {output_path}")
                    return output_path
                    
                except Exception as e:
                    logger.error(f"Error saving transcript: {e}")
                    return None
                    
            elif status == "failed":
                # Job failed
                error = status_data.get("error", "Unknown error")
                logger.error(f"Transcription failed: {error}")
                return None
                
            elif status == "processing":
                # Job is still processing, wait and try again
                logger.info(f"Transcription in progress... (attempt {attempt}/{max_attempts})")
                time.sleep(10)  # Wait 10 seconds between checks
                
            else:
                # Unknown status
                logger.warning(f"Unknown job status: {status}")
                time.sleep(10)
        
        # Max attempts reached
        logger.error("Transcription timed out after maximum attempts")
        return None
    
    except Exception as e:
        logger.error(f"API transcription error: {e}")
        return None

def _try_command_line_transcription(video_path, api_key, output_path):
    """
    Try transcribing using the npx offmute command line tool.
    """
    try:
        import subprocess
        
        # Prepare the command
        command = [
            "npx", 
            "offmute", 
            str(video_path)
        ]
        
        # Set the API key in the environment
        env = os.environ.copy()
        env["GEMINI_API_KEY"] = api_key
        
        # Run the command with a longer timeout
        logger.info(f"Running command: npx offmute {video_path}")
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        if process.returncode != 0:
            logger.error(f"Error running npx offmute: {process.stderr}")
            return None
        
        # Check if offmute generated a transcript file
        transcript_filename = os.path.splitext(os.path.basename(video_path))[0] + "_transcription.md"
        transcript_dir = os.path.dirname(video_path)
        generated_transcript = os.path.join(transcript_dir, transcript_filename)
        
        # Wait a bit to make sure file is fully written
        time.sleep(1)
        
        if os.path.exists(generated_transcript):
            # Copy the generated transcript to the output path
            with open(generated_transcript, "r", encoding="utf-8") as f:
                transcript_content = f.read()
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript_content)
            
            logger.info(f"Copied transcript from {generated_transcript} to {output_path}")
            return output_path
        else:
            logger.error(f"Transcript file not found at expected location: {generated_transcript}")
            
            # Fallback: check if it's in a 'transcription' subdirectory
            subdirectory_transcript = os.path.join(transcript_dir, "transcription", transcript_filename)
            if os.path.exists(subdirectory_transcript):
                # Copy the generated transcript to the output path
                with open(subdirectory_transcript, "r", encoding="utf-8") as f:
                    transcript_content = f.read()
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(transcript_content)
                
                logger.info(f"Copied transcript from {subdirectory_transcript} to {output_path}")
                return output_path
            
            return None
            
    except Exception as e:
        logger.error(f"Command line transcription error: {e}")
        return None

def format_transcript(transcript_json, output_path=None):
    """
    Format a transcript JSON into a readable markdown file.
    
    Args:
        transcript_json (dict): Transcript data from Offmute
        output_path (str, optional): Path to save the formatted transcript
        
    Returns:
        str: Path to the formatted transcript or None if failed
    """
    try:
        # Create markdown content
        markdown_content = "# Video Transcript\n\n"
        
        # Add speaker labels if available
        has_speakers = "speakers" in transcript_json
        
        if has_speakers:
            # Group by speaker
            current_speaker = None
            current_text = ""
            
            for segment in transcript_json.get("segments", []):
                speaker = segment.get("speaker", "Speaker")
                text = segment.get("text", "").strip()
                
                if not text:
                    continue
                
                if speaker != current_speaker:
                    # Add previous speaker's text
                    if current_speaker and current_text:
                        markdown_content += f"**{current_speaker}:** {current_text}\n\n"
                    
                    # Start new speaker
                    current_speaker = speaker
                    current_text = text
                else:
                    # Continue with same speaker
                    current_text += " " + text
            
            # Add the last speaker's text
            if current_speaker and current_text:
                markdown_content += f"**{current_speaker}:** {current_text}\n\n"
        else:
            # No speaker information, just add the text
            for segment in transcript_json.get("segments", []):
                text = segment.get("text", "").strip()
                if text:
                    markdown_content += f"{text}\n\n"
        
        # Save the formatted transcript
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            logger.info(f"Formatted transcript saved to: {output_path}")
            return output_path
        else:
            return markdown_content
            
    except Exception as e:
        logger.error(f"Error formatting transcript: {e}")
        return None

if __name__ == "__main__":
    # Script can be run directly with arguments
    parser = argparse.ArgumentParser(description="Transcribe videos using Offmute")
    parser.add_argument("input", help="Path to the video file")
    parser.add_argument("--output", help="Path to save the transcript")
    parser.add_argument("--api-key", help="Offmute API key")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    args = parser.parse_args()
    
    result = transcribe_video(
        args.input, 
        api_key=args.api_key, 
        output_path=args.output,
        language=args.language
    )
    
    if result:
        print(f"\nTranscription successful! Transcript saved to: {result}")
        sys.exit(0)
    else:
        print("\nTranscription failed!")
        sys.exit(1) 