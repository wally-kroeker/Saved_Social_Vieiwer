# Process Saved Links: File Structure and Component Relationships

## Directory Structure

```
Process_Saved_Links/
│
├── cline_docs/                 # Memory Bank documentation
│   ├── activeContext.md        # Current focus and next steps
│   ├── productContext.md       # Project purpose and goals
│   ├── progress.md             # Project progress tracking
│   ├── systemPatterns.md       # Architecture and patterns
│   └── techContext.md          # Technical details and requirements
│
├── main.py                     # Entry point and scheduler
├── config.py                   # Configuration settings
├── notion_integration.py       # Notion database operations
├── output_manager.py           # Output standardization
│
├── processors/                 # Platform-specific processors
│   ├── __init__.py             # Package initialization
│   ├── base_processor.py       # Base class with common functionality
│   ├── instagram_processor.py  # Instagram-specific processing
│   ├── youtube_processor.py    # YouTube-specific processing
│   └── tiktok_processor.py     # Future platform (template)
│
├── utils/                      # Utility functions
│   ├── __init__.py             # Package initialization
│   ├── logging_utils.py        # Logging setup
│   └── file_utils.py           # File operations
│
├── scripts/                    # External scripts
│   ├── download_post.sh        # Existing Instagram download script
│   └── offmute.py              # Script for processing audio
│
├── tests/                      # Test suite
│   ├── __init__.py             # Package initialization
│   ├── test_instagram.py       # Tests for Instagram processor
│   ├── test_youtube.py         # Tests for YouTube processor
│   └── test_integration.py     # Integration tests
│
├── logs/                       # Log files
│   └── .gitkeep                # Placeholder to include directory in git
│
├── README.md                   # Project overview and quick start
├── requirements.txt            # Python dependencies
├── setup.py                    # Installation script
└── project_plan.md             # Detailed project plan
```

## Component Relationships

```
                                  ┌─────────────┐
                                  │    main.py  │
                                  └──────┬──────┘
                                         │
                 ┌────────────────┬──────┴───────┬────────────────┐
                 │                │              │                │
        ┌─────────────────┐ ┌───────────┐ ┌────────────┐ ┌────────────────┐
        │ config.py       │ │ scheduler │ │ notion_    │ │ output_        │
        └─────────────────┘ └─────┬─────┘ │ integration│ │ manager        │
                                  │       └──────┬─────┘ └────────┬───────┘
                                  │              │                │
                                  │       ┌──────┴─────┐          │
                                  │       │ Notion DB  │          │
                                  │       └────────────┘          │
                                  │                               │
                         ┌────────┴───────────┐                   │
                         │                    │                   │
                ┌────────┴─────────┐ ┌────────┴─────────┐         │
                │ Instagram        │ │ YouTube          │         │
                │ Processor        │ │ Processor        │         │
                └──────────────────┘ └──────────────────┘         │
                         │                    │                   │
                         │                    │                   │
                         └──────────┬─────────┘                   │
                                    │                             │
                                    │         ┌───────────────────┘
                                    │         │
                                    ▼         ▼
                              ┌─────────────────────┐
                              │ Processed Content   │
                              │ Directory           │
                              └─────────────────────┘
```

## Data Flow

1. **Configuration Loading**:
   - `main.py` loads settings from `config.py`
   - Configuration includes API tokens, paths, and scheduling parameters

2. **Link Retrieval**:
   - `notion_integration.py` queries the Notion database for unprocessed links
   - Returns a list of links with their metadata

3. **Processing Workflow**:
   - For each link:
     - Determine the appropriate processor (Instagram, YouTube, etc.)
     - Process the content using platform-specific logic
     - Generate standardized outputs

4. **Output Management**:
   - `output_manager.py` ensures consistent naming and organization
   - Stores processed files in the designated output directory

5. **Status Update**:
   - `notion_integration.py` updates the Notion database with processing results
   - Marks items as completed or failed

6. **Scheduling**:
   - System runs at scheduled times (morning, noon, 11:00 PM)
   - Manages pauses between processing items (15 minutes)

## Key Interfaces

### Processor Interface
All platform processors implement this common interface:

```python
class BaseProcessor:
    def validate_url(self, url):
        """Check if the URL belongs to this platform"""
        pass
        
    def process(self, url, metadata):
        """Process the content and return output paths"""
        pass
        
    def download_content(self, url):
        """Download content from the platform"""
        pass
        
    def generate_outputs(self, content_path):
        """Generate standardized outputs"""
        pass
```

### Notion Integration Interface

```python
class NotionIntegration:
    def get_unprocessed_links(self, limit=None):
        """Get links with 'Not started' status"""
        pass
        
    def update_status(self, page_id, filename, status="Done"):
        """Update the status of a processed link"""
        pass
```

### Output Manager Interface

```python
class OutputManager:
    def standardize_filename(self, url, platform, timestamp):
        """Generate a standardized filename"""
        pass
        
    def organize_files(self, video_path, thumbnail_path, transcript_path):
        """Organize files in the output directory"""
        pass