### File Management
- Sanitize file names to remove problematic characters
- Create standardized file structures for all platforms
- Use consistent naming conventions
- Implement robust path handling for different operating systems
- Ensure centralized path generation logic (e.g., using `get_output_paths`) is the single source of truth. Avoid recalculating paths in helper functions like `copy_file`; instead, trust the path provided by the central utility to prevent inconsistencies arising from different interpretations of base directories (e.g., `src` vs. project root).

## Process Optimization 