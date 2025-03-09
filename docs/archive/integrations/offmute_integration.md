# Offmute Integration

This document describes the integration of Offmute with the Process Saved Links system for transcription and audio processing.

## Overview

Offmute is a tool for intelligent meeting transcription and analysis using Google's Gemini models. In our system, it's used to generate transcripts from video content downloaded from social media platforms.

## Key Features

- **Transcription & Diarization**: Converts audio/video content to text while identifying different speakers
- **Smart Speaker Identification**: Attempts to identify speakers by name and role when possible
- **Meeting Reports**: Generates structured reports with key points and action items
- **Video Analysis**: Extracts and analyzes visual information from videos
- **Markdown-Formatted Output**: Provides well-structured transcripts in Markdown format

## Integration Methods

The system integrates with Offmute in two ways:

1. **API Integration**: Direct calls to the Offmute API
2. **CLI Fallback**: Command-line execution as a fallback if the API fails

### API Integration

The API integration uses the Gemini-Offmute API endpoint:

```python
def generate_transcript_with_api(video_path, api_key):
    """Generate transcript using the Offmute API."""
    api_url = "https://api.gemini-offmute.com/v1"
    # API call implementation
    # ...
```

### CLI Fallback

The CLI fallback uses the `npx offmute` command:

```python
def generate_transcript_with_cli(video_path, api_key):
    """Generate transcript using the Offmute CLI."""
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key
    
    command = ["npx", "offmute", video_path]
    # CLI execution implementation
    # ...
```

## Configuration

The Offmute integration requires:

1. **API Key**: Gemini API key stored in the `.env` file as `GEMINI_API_KEY`
2. **Timeout Settings**: Configurable timeouts for API calls
3. **Output Path**: Path for transcript output

Example configuration:

```python
offmute_config = {
    "api_key": os.environ.get("GEMINI_API_KEY"),
    "api_timeout": 300,  # 5 minutes
    "cli_timeout": 1800,  # 30 minutes
    "output_dir": os.path.join(base_output_dir, "transcripts")
}
```

## Usage in Processors

Both Instagram and YouTube processors use Offmute for transcript generation:

```python
def _generate_transcript(self, video_path, output_path):
    """Generate transcript for the given video."""
    try:
        # Try API first
        success, transcript = self._generate_transcript_with_offmute(video_path, output_path)
        if success:
            return True, transcript
            
        # Fall back to CLI if API fails
        return self._generate_transcript_with_offmute_cli(video_path, output_path)
    except Exception as e:
        self.logger.error(f"Transcript generation failed: {str(e)}")
        return False, None
```

## Error Handling

The integration includes robust error handling:

1. **API Timeout**: If the API call times out, fall back to CLI
2. **CLI Failure**: If CLI fails, log the error and continue processing without transcript
3. **Permission Issues**: Check for appropriate permissions before API/CLI calls
4. **File Validation**: Verify video file exists and is accessible

## Output Format

The transcript output is a Markdown file with:

1. **Header**: Title, date, and participants
2. **Transcript Body**: Time-stamped text with speaker identification
3. **Summary**: Key points extracted from the content

## Recent Fixes

The Offmute integration was recently updated to fix DNS resolution issues:

1. Updated the API URL to `https://api.gemini-offmute.com/v1`
2. Implemented a more robust fallback mechanism
3. Added better error handling and logging throughout the process
4. Added timeout configuration to prevent long waits if the API is down

## Related Documentation

- [Implementation Guide](../implementation/implementation_guide.md) - General implementation information
- [Instagram Processor](../implementation/instagram_processor.md) - Instagram-specific implementation
- [YouTube Processor](../implementation/youtube_processor.md) - YouTube-specific implementation 