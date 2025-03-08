"""
Simple test to verify that the Notion integration module can be imported.
"""
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import notion_integration
    print("✓ Notion integration module imported successfully")
    
    # Check if the singleton instance was created
    if hasattr(notion_integration, 'notion'):
        print("✓ Notion integration singleton instance exists")
    else:
        print("✗ Notion integration singleton instance not found")
    
except ImportError as e:
    print(f"✗ Failed to import notion_integration: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}") 