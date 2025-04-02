# Project Overview

## Introduction

The Process Saved Links project automates the workflow of downloading, processing, and organizing content from various social media platforms. It helps users save and reference interesting or useful content from platforms like Instagram and YouTube for later analysis or repurposing.

## Purpose and Goals

The primary goals of this project are to:

1. **Automate Content Collection**: Eliminate manual downloading and processing of social media content
2. **Standardize Output Format**: Create consistent file formats and organization across platforms
3. **Centralize Content Management**: Manage all saved content through a single Notion database
4. **Provide Accessibility**: Make content available offline and in searchable formats
5. **Enable Expansion**: Create a flexible architecture that can accommodate new platforms

## Key Features

- **Multi-Platform Support**: Process content from Instagram, YouTube, and potentially other platforms
- **Automated Processing**: Schedule automatic runs to process new content
- **Content Transcription**: Generate transcripts for video content using Offmute
- **Structured Organization**: Store processed content in a standardized directory structure
- **Notion Integration**: Use Notion as a database for tracking and managing links
- **Configurable Processing**: Customize processing options for different content types

## System Overview

The system works as follows:

1. The system checks a Notion database for unprocessed links at scheduled intervals
2. For each unprocessed link:
   - The system identifies the appropriate processor based on the link type
   - The processor downloads and processes the content according to platform-specific rules
   - The system generates standardized outputs (video, thumbnail, transcript)
   - The Notion database is updated to mark the link as processed
3. A 15-minute pause is observed between processing items
4. This process repeats at scheduled times throughout the day

## Project Timeline

The project is structured into four phases:

### Phase 1: Project Setup and Refactoring (Completed)
- Create project structure
- Implement core components
- Refactor existing Instagram processing
- Ensure compatibility with existing output

### Phase 2: YouTube Processing (In Progress)
- Implement YouTube download functionality
- Integrate with offmute for audio processing
- Implement transcript generation
- Create thumbnail extraction

### Phase 3: Scheduling and Automation (In Progress)
- Implement scheduling system
- Set up automated execution
- Add comprehensive logging and error handling

### Phase 4: Testing and Documentation (Upcoming)
- Test with various links
- Document system architecture
- Create usage instructions
- Prepare for future platform additions

## Related Documentation

- [Architecture](./architecture.md) - Detailed system architecture
- [Requirements](./requirements.md) - Specific project requirements
- [Implementation Guide](../implementation/implementation_guide.md) - Implementation details 