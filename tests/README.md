# Tests for Process Saved Links

This directory contains test scripts for the Process Saved Links project.

## Available Tests

- `test_notion.py`: Tests the Notion integration module
- `import_test.py`: Simple test to verify that modules can be imported correctly

## Running Tests

### Using the run_test.sh Script

The easiest way to run the Notion integration test is to use the provided shell script:

```bash
# From the project root directory
./tests/run_test.sh

# Or from the tests directory
./run_test.sh
```

### Running Tests Manually

You can also run the tests manually using the `uv` package manager:

```bash
# From the project root directory
uv run tests/test_notion.py
uv run tests/import_test.py
```

## Test Requirements

The tests require the following:

1. A `.env` file in the project root with the following variables:
   ```
   NOTION_API_TOKEN=your_notion_api_token
   NOTION_DATABASE_ID=your_notion_database_id
   ```

2. The required packages installed:
   ```bash
   uv pip install notion-client python-dotenv
   ```

## Adding New Tests

When adding new tests, follow these guidelines:

1. Place test files in this directory with a `test_` prefix
2. Add the project root to the Python path in each test file:
   ```python
   import sys
   from pathlib import Path
   
   # Add the project root directory to the Python path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

3. Update this README.md file with information about the new test 