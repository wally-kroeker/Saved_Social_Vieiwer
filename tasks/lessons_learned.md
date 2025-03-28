# Lessons Learned

## Filename Handling & Storage

### Special Characters in Filenames
- **Problem**: Characters like `#` in filenames caused issues in web contexts because:
  - `#` is treated as a fragment identifier in URLs
  - Web servers often strip everything after `#` in URL paths
  - URL-encoding special characters can be handled inconsistently across systems
  
- **Solution**: 
  - Implemented comprehensive sanitization that replaces problematic characters
  - Converted hashtags (`#tag`) to a prefix format (`tag_tag`)
  - Standardized on hyphen-separated components

### Consistent Naming Convention
- **Pattern**: `{platform}-{username}-{date}-{sanitized_title}`
- **Benefits**:
  - Source platform is immediately identifiable
  - Content creator attribution is preserved
  - Chronological sorting works naturally
  - Descriptive titles improve searchability
  - Consistent extensions make file type identification reliable

### Migration vs. Clean Break
- **Approach**: Created tools to migrate existing files rather than requiring a clean break
- **Benefits**:
  - Preserves existing content
  - Allows gradual adoption of new standards
  - Enables thorough validation before committing to changes

## System Design Insights

### Abstraction Layers
- Created `filename_utils.py` as a core module with pure functions
- Added `processor_filename_integration.py` as an adapter layer between existing code and new utilities
- This separation allows:
  - Clean interfaces for new code
  - Backward compatibility with existing systems
  - Easier testing of core functions

### Data Organization
- **Platform-Based Directory Structure**: Organizing content by platform improves:
  - Navigation and browsing
  - Backup strategies
  - Application of platform-specific processing
  - Isolation of platform-specific issues

### Metadata Management
- **Approach**: Store standardized metadata in JSON files alongside media
- **Benefits**:
  - Content is self-describing
  - Media can be processed without external database
  - Preservation of original metadata
  - Enables offline/local-first processing

## Web Infrastructure Lessons

### URL Path Handling
- URLs with special characters require careful handling on both client and server
- Different segments of the URL are processed differently
- Fragment identifiers (`#`) are never sent to the server in HTTP requests

### Server Framework Considerations
- Simple `http.server` implementations have limitations with:
  - URL parsing
  - Path handling
  - Error recovery
  - Special character handling
  
- Modern frameworks like FastAPI provide:
  - Robust parameter parsing
  - Path validation
  - Explicit typing
  - Better security controls

## Integration Patterns

### Bridging Old and New Systems
- Created adapter functions that:
  - Extract relevant metadata from platform-specific formats
  - Generate consistent output paths
  - Apply new naming standards without changing existing processing logic
  
- This approach allows incremental improvement without requiring full rewrites 