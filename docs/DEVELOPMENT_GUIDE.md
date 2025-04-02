# Development Guide

## Current Project Status

The Process Saved Links project is currently **operational** with both YouTube and Instagram processing working. The system can successfully:

- Process YouTube videos (download, generate transcripts, extract metadata)
- Process Instagram posts (images, videos, and stories)
- Integrate with Notion as a content database
- Output standardized content files
- View processed content through a FastAPI-based viewer

Recent architectural improvements include:
- Platform-specific processor configurations
- Factory pattern for processor instantiation
- Parallel processing capabilities
- Enhanced error handling

## Planned Improvements

The project is undergoing a significant restructuring to improve usability and maintainability:

### High Priority (Current Sprint)
- [x] Fix Notion status update issues
- [x] Implement improved file path handling for special characters
- [x] Create platform-specific configuration system
- [ ] Develop unified interactive CLI interface
- [ ] Implement parallel processing for different platforms

### Medium Priority
- [ ] Add command-line mode for automation/scripts
- [ ] Enhance error recovery mechanisms
- [ ] Improve transcript generation quality
- [ ] Add configuration management via CLI

### Future Enhancements
- [ ] Add support for additional platforms (Twitter, TikTok)
- [ ] Implement content tagging and categorization
- [ ] Create advanced search functionality in the viewer
- [ ] Develop mobile-friendly content access

## Project Structure

```
/Process_Saved_Links/
├── processors/                  # Platform-specific processors
│   ├── base_processor.py        # Base processor class
│   ├── youtube_processor.py     # YouTube-specific processing
│   └── instagram_processor.py   # Instagram-specific processing
├── notion_integration.py        # Notion API integration
├── platform_processor.py        # Platform processing orchestration
├── processor_factory.py         # Factory for creating processors
├── platform_config.py           # Platform-specific settings
├── process_links.py             # Main processing script
├── utils/                       # Utility functions
├── run_process_links_v2.sh      # Running script (current)
└── process_links_manager.sh     # New interactive CLI (planned)
```

## Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Process_Saved_Links
   ```

2. **Set up environment variables**:
   Create a `.env` file with:
   ```
   NOTION_API_TOKEN=your_notion_api_token
   NOTION_DATABASE_ID=your_notion_database_id
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Install dependencies with UV**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

4. **Ensure FFmpeg is installed**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

5. **Install Node.js for Offmute**:
   ```bash
   sudo apt install nodejs npm
   npm install -g offmute
   ```

## Running the Project

### Current Method

```bash
./run_process_links_v2.sh --platform youtube --limit 2
```

### Future Interactive CLI (Coming Soon)

```bash
./process_links_manager.sh
```

This will launch the interactive menu system with options for:
- Processing different platforms
- Viewing processing status
- Running diagnostics
- Managing configuration

## Development Workflow

1. **Check out a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow existing code style
   - Add appropriate logging
   - Implement error handling

3. **Test your changes**:
   - Test with real YouTube and Instagram links
   - Verify Notion integration
   - Ensure output files are correct

4. **Submit a pull request**:
   - Provide a clear description of changes
   - Link to any relevant issues

## Troubleshooting Common Issues

### Notion API Errors
- Check that your Notion API token and database ID are correct
- Verify the database has the required properties (URL, Status, Name)
- Ensure the Status property uses valid status options

### Transcript Generation Issues
- Verify the Gemini API key is valid
- Check that offmute is properly installed
- Ensure ffmpeg is installed and in the PATH

### File Path Problems
- Use the provided file path sanitization functions
- Avoid special characters in output directories
- Check file permissions on the output directory

## Getting Help

For questions or issues:
1. Check the existing documentation
2. Review the code comments
3. Contact the project maintainers 