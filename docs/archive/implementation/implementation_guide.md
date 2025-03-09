# Implementation Guide

This guide provides general information about implementing and extending the Process Saved Links system.

## Implementation Principles

The implementation follows these core principles:

1. **Modularity**: Each component has a clear, single responsibility
2. **Extensibility**: The system is designed to be extended with new platforms
3. **Error Resilience**: Failures in processing one item don't affect others
4. **Consistency**: All outputs follow standardized formats and naming conventions
5. **Configuration Over Code**: Customizable aspects are in configuration, not hardcoded

## Key Implementation Decisions

### 1. Python as Primary Language

Python was chosen as the primary language for:
- Excellent library support for API integrations
- Strong text and media processing capabilities
- Availability of libraries for all required functionalities
- Ease of maintenance and extension

### 2. Modular Processor Architecture

The processor architecture uses inheritance:
- `BaseProcessor` class defines the common interface
- Platform-specific processors inherit and implement platform-specific logic
- This allows consistent behavior while accommodating platform differences

### 3. Configuration Management

Configuration is centralized and loaded from:
- Environment variables (for sensitive information)
- Configuration files (for general settings)
- Command-line arguments (for runtime options)

### 4. Error Handling Strategy

Error handling follows these principles:
- Errors in one processor don't affect others
- Detailed error information is logged
- Failed items are marked as such in Notion
- The system can resume processing after failures

## Common Implementation Patterns

### Platform Processor Implementation

All platform processors follow this pattern:

```python
class PlatformProcessor(BaseProcessor):
    def __init__(self, config):
        super().__init__(config)
        # Platform-specific initialization
        
    def can_process(self, url):
        # Logic to determine if this processor can handle the URL
        return url_pattern_match
        
    def process(self, item):
        try:
            # 1. Download content
            self._download_content(item)
            
            # 2. Process content
            self._process_content(item)
            
            # 3. Generate outputs
            self._generate_outputs(item)
            
            # 4. Return success
            return True, {"metadata": metadata}
        except Exception as e:
            # Log and return error
            return False, {"error": str(e)}
```

### Configuration Loading

Configuration loading follows this pattern:

```python
def load_config():
    # Load from environment variables
    env_vars = load_environment_variables()
    
    # Load from config file
    file_config = load_config_file()
    
    # Merge configurations with environment variables taking precedence
    config = {**file_config, **env_vars}
    
    # Validate required configuration
    validate_config(config)
    
    return config
```

### Notion Integration

Notion integration follows this pattern:

```python
def get_unprocessed_items():
    # Query Notion database for unprocessed items
    
def mark_as_processed(item_id, metadata):
    # Update item in Notion as processed with metadata
    
def mark_as_failed(item_id, error):
    # Update item in Notion as failed with error message
```

## Adding a New Platform Processor

To add support for a new platform:

1. Create a new processor class that inherits from `BaseProcessor`
2. Implement the `can_process` method to identify URLs for this platform
3. Implement the `process` method with platform-specific logic
4. Add appropriate configuration for the new platform
5. Register the processor in the platform selector

Example:

```python
class TikTokProcessor(BaseProcessor):
    def __init__(self, config):
        super().__init__(config)
        self.tiktok_config = config.get("tiktok", {})
        
    def can_process(self, url):
        return "tiktok.com" in url
        
    def process(self, item):
        # TikTok-specific processing logic
        # ...
```

## Implementing Scheduling

The scheduling implementation uses:

1. A main scheduler that runs at specified times
2. A processing loop that handles items with pauses
3. Configuration for scheduling times and pause duration

## Testing Implementation

The testing strategy includes:

1. Unit tests for individual components
2. Integration tests for component interactions
3. End-to-end tests for the full processing pipeline
4. Dry-run mode for testing without affecting real data

## Related Documentation

- [Project Overview](../overview/project_overview.md) - High-level project description
- [Instagram Processor](./instagram_processor.md) - Instagram-specific implementation
- [YouTube Processor](./youtube_processor.md) - YouTube-specific implementation
- [Scheduling](./scheduling.md) - Scheduling implementation details 