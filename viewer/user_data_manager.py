import json
import shutil
from pathlib import Path
from typing import Dict, Any

# Define file paths (relative to this script's location, adjust if needed)
# Consider placing outside 'viewer' if packaging is a concern
_SCRIPT_DIR = Path(__file__).resolve().parent
USER_DATA_FILE = _SCRIPT_DIR / "user_data.json"
USER_DATA_BACKUP_FILE = _SCRIPT_DIR / "user_data.json.bak"

def load_user_data() -> Dict[str, Any]:
    """Loads user data, attempting backup file if primary fails."""
    data = {}
    file_to_try = USER_DATA_FILE
    
    for attempt in range(2): # Try primary, then backup
        if file_to_try.exists():
            try:
                with open(file_to_try, 'r') as f:
                    data = json.load(f)
                print(f"Successfully loaded user data from {file_to_try}")
                # If loaded from backup, restore it to primary
                if file_to_try == USER_DATA_BACKUP_FILE:
                    save_user_data(data)
                    print(f"Restored user data from backup to {USER_DATA_FILE}")
                return data
            except json.JSONDecodeError:
                print(f"Warning: Failed to decode JSON from {file_to_try}. Corrupted?")
            except Exception as e:
                print(f"Error reading {file_to_try}: {e}")
        
        # Prepare for next attempt (try backup)
        file_to_try = USER_DATA_BACKUP_FILE

    print("No valid user data file found (primary or backup). Starting fresh.")
    return data # Return empty dict if both fail

def save_user_data(data: Dict[str, Any]) -> None:
    """Saves user data, backing up the existing file first."""
    # 1. Backup existing file
    if USER_DATA_FILE.exists():
        try:
            shutil.copy2(USER_DATA_FILE, USER_DATA_BACKUP_FILE)
            print(f"Backed up user data to {USER_DATA_BACKUP_FILE}")
        except Exception as e:
            print(f"Error creating backup file {USER_DATA_BACKUP_FILE}: {e}")
            # Decide if you want to proceed without backup? Maybe raise error?
            # For now, we proceed cautiously

    # 2. Write new data
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2) # Pretty print for readability
        print(f"Saved user data to {USER_DATA_FILE}")
    except Exception as e:
        print(f"Error writing user data to {USER_DATA_FILE}: {e}")
        # Consider attempting to restore from backup if write fails?

def get_user_data_for_item(platform: str, filename_base: str) -> Dict[str, Any]:
    """Gets user data for a specific item, providing defaults."""
    all_data = load_user_data()
    item_key = f"{platform}/{filename_base}"
    # Defaults align with expected frontend structure
    default_item_data = {"status": "new", "favorite": False, "notes": ""}
    return all_data.get(item_key, default_item_data)

def update_user_data_for_item(platform: str, filename_base: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Updates and saves user data for a specific item."""
    all_data = load_user_data()
    item_key = f"{platform}/{filename_base}"
    
    # Get current data or defaults
    current_item_data = all_data.get(item_key, {"status": "new", "favorite": False, "notes": ""})
    
    # Apply valid updates
    allowed_keys = {"status", "favorite", "notes"}
    valid_updates = {k: v for k, v in updates.items() if k in allowed_keys}
    current_item_data.update(valid_updates)
    
    # Update the main dictionary
    all_data[item_key] = current_item_data
    
    # Save the entire dataset
    save_user_data(all_data)
    
    # Return the updated data for the specific item
    return current_item_data

# Example usage (optional - can be run directly for testing)
if __name__ == "__main__":
    print("Testing user_data_manager...")
    # Ensure files are created if they don't exist for testing
    if not USER_DATA_FILE.exists():
        save_user_data({})
        
    test_platform = "youtube"
    test_filename = "test-video-123"
    
    # Get initial data (should be defaults)
    initial_data = get_user_data_for_item(test_platform, test_filename)
    print(f"Initial data for {test_platform}/{test_filename}: {initial_data}")
    
    # Update data
    updates = {"favorite": True, "status": "viewed", "notes": "This is a test note."}
    updated_data = update_user_data_for_item(test_platform, test_filename, updates)
    print(f"Updated data: {updated_data}")
    
    # Verify retrieval
    retrieved_data = get_user_data_for_item(test_platform, test_filename)
    print(f"Retrieved data: {retrieved_data}")
    assert retrieved_data == updated_data
    
    # Test another item
    updates_2 = {"status": "processing"}
    updated_data_2 = update_user_data_for_item("instagram", "insta-pic-456", updates_2)
    print(f"Updated data 2: {updated_data_2}")
    
    # Load all data
    all_user_data = load_user_data()
    print(f"All user data:\n{json.dumps(all_user_data, indent=2)}")
    print("Test complete.") 