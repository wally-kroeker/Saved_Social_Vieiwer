# Process Saved Links

## Project Purpose

Process Saved Links automates the workflow of downloading, processing, and organizing content from social media platforms. It saves interesting content from Instagram and YouTube for later reference or research, eliminating manual downloading and organization.

## Key Features

- **Multi-Platform Support**: Process content from Instagram and YouTube
- **Notion Integration**: Track and manage links through a Notion database
- **Automated Content Processing**: Download videos, generate transcripts, and save metadata
- **Standardized Output**: Consistent file formats across different platforms
- **Content Viewer**: Browse and view processed content through a built-in web interface

## Technologies Used

### Backend Processing
- **Python 3.10+**: Core processing logic
- **UV Package Manager**: Dependency management
- **FFmpeg**: Media conversion and thumbnail generation
- **yt-dlp**: YouTube video downloading
- **Instaloader**: Instagram content downloading
- **Offmute**: AI-based video/audio transcription

### Storage and Database
- **Notion API**: Database for tracking links and processing status
- **Local File Storage**: Organized storage for downloaded content

### Content Viewing
- **FastAPI**: Backend for the content viewer
- **Jinja2**: HTML templating
- **Uvicorn**: ASGI server for the viewer

## System Architecture

The system follows a modular architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Process Runner │────▶│ Notion Integration │◀───▶│  Notion Database │
│                 │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Processor Factory │
│                 │
└──┬─────────┬────┘
   │         │
   ▼         ▼
┌─────────┐ ┌─────────┐
│ YouTube │ │Instagram│  ... (extensible to other platforms)
│Processor│ │Processor│
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│                     │
│    Output Files     │
│  (videos, images,   │
│transcripts, metadata)│
│                     │
└─────────────────────┘
```

## Workflow

1. The system periodically checks the Notion database for unprocessed links
2. Each link is processed by the appropriate platform processor:
   - YouTube links → YouTube Processor
   - Instagram links → Instagram Processor
3. Content is downloaded, processed, and saved in a standardized format
4. The Notion database is updated with processing status and metadata
5. The processed content can be viewed through the FastAPI-based content viewer

## Output Structure

```
/Processed-ContentIdeas/
├── channel1-date-video_title.mp4
├── channel1-date-video_title.jpg  (thumbnail)
├── channel1-date-video_title.md   (transcript)
├── channel1-date-video_title.json (metadata)
├── channel2-date-another_title.mp4
└── ...
```

## Project Status

The project is currently operational with both YouTube and Instagram processing implemented. The Notion integration, processing logic, and content viewer are all functional. Recent improvements include:
- Platform-specific processing configurations
- Enhanced transcript generation
- Parallel processing capabilities 