#!/bin/bash

# Configuration
SOURCE_DIR="/home/docker/Saved_Social_Vieiwer/olddata/Processed-ContentIdeas"
OUTPUT_DIR="/home/docker/Saved_Social_Vieiwer/output/instagram"

# Default number of posts to migrate
MIGRATE_COUNT=10

# Parse command-line options
while getopts "n:" opt; do
  case $opt in
    n)
      MIGRATE_COUNT=${OPTARG}
      ;;
    \?)
      echo "Usage: $0 [-n number_of_posts_to_migrate]"
      exit 1
      ;;
  esac
done

# Validate MIGRATE_COUNT
if ! [[ "$MIGRATE_COUNT" =~ ^[0-9]+$ ]] || [ "$MIGRATE_COUNT" -lt 1 ]; then
    echo "Error: Invalid number specified with -n. Please provide a positive integer."
    exit 1
fi

echo "Migrating up to $MIGRATE_COUNT post(s)..."

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Associative array to group files by post base name (requires bash 4+)
declare -A posts

# --- Populate the posts array using a for loop --- 
shopt -s nullglob # Prevent errors if no files match
for file in "$SOURCE_DIR"/*; do
    if [ -f "$file" ]; then # Ensure it's a file
        filename=$(basename "$file")
        extension="${filename##*.}"
        stem="${filename%.*}"

        # Skip files with known problematic prefixes or formats we don't handle
        if [[ "$filename" == instagram_* || "$filename" == DG* || "$filename" == C* ]]; then
            # echo "Debug: Skipping known prefix: $filename"
            continue
        fi

        # Extract username, date, and title
        # Assumes format: username-YYYY-MM-DD-title.*
        if [[ "$stem" =~ ^([^-]+)-([0-9]{4}-[0-9]{2}-[0-9]{2})-(.*)$ ]]; then
            username="${BASH_REMATCH[1]}"
            date="${BASH_REMATCH[2]}"
            title="${BASH_REMATCH[3]}"
            post_key="${username}-${date}-${title}"
            
            # echo "Debug: Found match: Key=$post_key, File=$filename"
            
            # Store filename associated with its key
            posts["$post_key"]+="$filename " # Append filename with a space separator
        else
            echo "Skipping file with unexpected format: $filename"
        fi
    fi
done
shopt -u nullglob # Turn off nullglob
# --- End population ---

migrated_post_count=0

# Check if any posts were found
if [ ${#posts[@]} -eq 0 ]; then
    echo "No posts found matching the expected format in $SOURCE_DIR"
    exit 0
fi

echo "Found ${#posts[@]} potential posts to process."

# Process the grouped posts
for key in "${!posts[@]}"; do
    if [ $migrated_post_count -ge $MIGRATE_COUNT ]; then
        echo "Reached migration limit ($MIGRATE_COUNT)."
        break
    fi

    # Retrieve data from the key
    if [[ "$key" =~ ^([^-]+)-([0-9]{4}-[0-9]{2}-[0-9]{2})-(.*)$ ]]; then
        username="${BASH_REMATCH[1]}"
        date="${BASH_REMATCH[2]}"
        title="${BASH_REMATCH[3]}"
    else
        echo "Error parsing key: $key" # Should not happen
        continue
    fi

    echo "Processing post: $key"

    # Sanitize title: Replace non-alphanumeric (excluding -, .) with _
    safe_title=$(echo "$title" | sed 's/[^a-zA-Z0-9.-]/_/g')
    new_base="instagram-${username}-${date}-${safe_title}"

    files_to_process=(${posts[$key]}) # Split the space-separated string into an array
    required_types_found=("json" "jpg" "mp4" "md") # Track required types
    actual_types_found=()
    
    # --- Add logic to find existing .md and .txt files --- 
    found_md=""
    found_txt=""
    for temp_filename in "${files_to_process[@]}"; do
        temp_extension="${temp_filename##*.}"
        if [[ "$temp_extension" == "md" ]]; then
            found_md="$temp_filename"
        elif [[ "$temp_extension" == "txt" ]]; then
            found_txt="$temp_filename"
        fi
    done
    
    # Determine which file to skip if both .md and .txt exist
    file_to_skip=""
    if [[ -n "$found_md" && -n "$found_txt" ]]; then
        echo "  Found both .md and .txt, prioritizing .md: $found_md"
        file_to_skip="$found_txt" 
    fi
    # --- End added logic ---

    # Iterate over files for this post
    for filename in "${files_to_process[@]}"; do
        # --- Add skip logic --- 
        if [[ "$filename" == "$file_to_skip" ]]; then
            echo "  Skipping $filename (prioritizing .md)"
            continue
        fi
        # --- End skip logic ---
        
        extension="${filename##*.}"
        new_ext="$extension" # Default extension

        # Handle transcript files (only rename if not skipped)
        if [[ "$extension" == "txt" ]]; then 
            new_ext="md"
            echo "  Found transcript file (.txt): $filename, renaming to .md"
        elif [[ "$extension" == "md" ]]; then
             # Keep .md as .md, no message needed unless it's the one being prioritized
             new_ext="md" 
        fi

        new_filename="${new_base}.${new_ext}"
        source_path="$SOURCE_DIR/$filename"
        dest_path="$OUTPUT_DIR/$new_filename"

        if [ -f "$source_path" ]; then
            echo "  Copying: $filename -> $new_filename"
            cp "$source_path" "$dest_path"
            actual_types_found+=("$new_ext")
        else
            echo "  Warning: Source file not found: $source_path" # Should not happen if populated correctly
        fi
    done

    # Check if all required types were present (simple check)
    missing_types=()
    for req_type in "${required_types_found[@]}"; do
        found=0
        for act_type in "${actual_types_found[@]}"; do
            if [[ "$req_type" == "$act_type" ]]; then
                found=1
                break
            fi
        done
        if [ $found -eq 0 ]; then
            missing_types+=("$req_type")
        fi
    done

    if [ ${#missing_types[@]} -gt 0 ]; then
        echo "  Warning: Missing file types for post $key: ${missing_types[*]}"
    fi

    ((migrated_post_count++))
    echo "  Post migration complete."
    echo ""

done

echo "Migration script finished. Migrated $migrated_post_count post(s)."

exit 0 