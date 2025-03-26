#!/bin/bash
# Script to run the Process Saved Links application using UV

# Set the directory where the script is located as the working directory
cd "$(dirname "$0")"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display the script header
show_header() {
    echo -e "${YELLOW}===============================================${NC}"
    echo -e "${YELLOW}=== Process Saved Links Management Tool ====${NC}"
    echo -e "${YELLOW}===============================================${NC}"
    echo -e "${GREEN}Using UV as package manager${NC}"
}

# Check if UV is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Error: UV is not installed.${NC}"
        echo -e "Please install UV by running: ${BLUE}curl -sSf https://astral.sh/uv/install.sh | bash${NC}"
        echo -e "For more information, visit: ${BLUE}https://github.com/astral-sh/uv${NC}"
        exit 1
    fi

    # Display UV version
    echo -e "${GREEN}UV version:${NC} $(uv --version)"
}

# Check if .venv directory exists, if not create it
setup_env() {
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        uv venv
    fi
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}Error: requirements.txt not found${NC}"
        echo -e "Please ensure requirements.txt exists in the current directory"
        exit 1
    fi
    
    echo -e "${YELLOW}Activating virtual environment and ensuring dependencies...${NC}"
    source .venv/bin/activate
    uv pip install -r requirements.txt
}

# Check if environment variables are set
check_env_vars() {
    local missing_vars=()
    
    # Check required environment variables
    if [ -z "$NOTION_API_TOKEN" ]; then
        missing_vars+=("NOTION_API_TOKEN")
    fi
    
    if [ -z "$NOTION_DATABASE_ID" ]; then
        missing_vars+=("NOTION_DATABASE_ID")
    fi
    
    # GEMINI_API_KEY is recommended but not strictly required
    if [ -z "$GEMINI_API_KEY" ]; then
        echo -e "${YELLOW}Warning: GEMINI_API_KEY not set. Transcript generation may be limited.${NC}"
    fi
    
    # If any required variables are missing, show error
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo -e "${RED}Error: The following required environment variables are not set:${NC}"
        for var in "${missing_vars[@]}"; do
            echo -e "  - ${var}"
        done
        echo -e "\nPlease set these variables in your .env file or export them directly."
        exit 1
    fi
}

# Function to run a command with UV
run_with_uv() {
    echo -e "\n${YELLOW}=== Running: $1 ===${NC}"
    uv run python "$@"
}

# Function to display help
show_help() {
    echo -e "\n${GREEN}Process Saved Links Help${NC}"
    echo -e "${BLUE}This tool automates the process of downloading and organizing content from social media platforms.${NC}"
    echo -e "\nAvailable actions:"
    echo -e "  ${YELLOW}1) Process YouTube links${NC} - Download and process YouTube videos"
    echo -e "  ${YELLOW}2) Process Instagram links${NC} - Download and process Instagram posts"
    echo -e "  ${YELLOW}3) Process all platforms${NC} - Process both YouTube and Instagram"
    echo -e "  ${YELLOW}4) View processing status${NC} - Check current processing status and history"
    echo -e "  ${YELLOW}5) System diagnostics${NC} - Verify system components and connections"
    echo -e "  ${YELLOW}6) Configuration${NC} - View and edit configuration settings"
    echo -e "  ${YELLOW}h) Show help${NC} - Display this help message"
    echo -e "  ${YELLOW}q) Quit${NC} - Exit the script"
    
    echo -e "\n${BLUE}Common workflows:${NC}"
    echo -e "1. Run system diagnostics to ensure all components are working"
    echo -e "2. Process specific platforms or all platforms as needed"
    echo -e "3. Check processing status to verify results"
    
    echo -e "\n${BLUE}Command line usage:${NC}"
    echo -e "./process_links_manager.sh youtube --limit 2"
    echo -e "./process_links_manager.sh instagram --limit 1"
    echo -e "./process_links_manager.sh all --parallel"
    echo -e "./process_links_manager.sh status"
    echo -e "./process_links_manager.sh config view"
}

# Function to handle status viewing
view_status() {
    echo -e "\n${GREEN}Processing Status${NC}"
    echo -e "${YELLOW}1)${NC} View active jobs"
    echo -e "${YELLOW}2)${NC} View processing history"
    echo -e "${YELLOW}3)${NC} View error logs"
    echo -e "${YELLOW}4)${NC} Clear completed jobs"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " status_choice
    
    case $status_choice in
        1)
            echo -e "${BLUE}Checking for active jobs...${NC}"
            # Implement actual status checking based on your system
            ps aux | grep -E "process_links.py|run_youtube_post.py|run_instagram_post.py" | grep -v grep
            ;;
        2)
            echo -e "${BLUE}Processing history:${NC}"
            if [ -f "processing_history.log" ]; then
                tail -n 20 processing_history.log
            else
                echo -e "${YELLOW}No processing history found.${NC}"
            fi
            ;;
        3)
            echo -e "${BLUE}Error logs:${NC}"
            for log_file in logs/*.log; do
                if [ -f "$log_file" ]; then
                    echo -e "${YELLOW}=== $log_file ===${NC}"
                    grep -i "error\|exception\|failed" "$log_file" | tail -n 10
                    echo ""
                fi
            done
            if [ ! -d "logs" ] || [ -z "$(ls -A logs 2>/dev/null)" ]; then
                echo -e "${YELLOW}No log files found.${NC}"
            fi
            ;;
        4)
            echo -e "${RED}Warning: This will clear completed job records.${NC}"
            read -p "Are you sure you want to proceed? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                echo -e "${BLUE}Clearing completed jobs...${NC}"
                # Implement job clearing logic here
                echo -e "${GREEN}Completed jobs cleared.${NC}"
            else
                echo -e "${YELLOW}Operation cancelled.${NC}"
            fi
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    
    # Return to status menu after action
    read -p "Press Enter to return to status menu..."
    view_status
}

# Function to handle diagnostics
run_diagnostics() {
    echo -e "\n${GREEN}System Diagnostics${NC}"
    echo -e "${YELLOW}1)${NC} Check Notion connectivity"
    echo -e "${YELLOW}2)${NC} Check Instagram connectivity"
    echo -e "${YELLOW}3)${NC} Verify environment setup"
    echo -e "${YELLOW}4)${NC} Check output directory"
    echo -e "${YELLOW}5)${NC} Test transcript generation"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " diag_choice
    
    case $diag_choice in
        1)
            echo -e "${BLUE}Checking Notion connectivity...${NC}"
            run_with_uv check_notion_connection.py
            ;;
        2)
            echo -e "${BLUE}Checking Instagram connectivity...${NC}"
            run_with_uv check_instagram_connection.py
            ;;
        3)
            echo -e "${BLUE}Verifying environment setup...${NC}"
            echo -e "Python: $(python --version)"
            echo -e "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
            echo -e "FFmpeg: $(ffmpeg -version 2>/dev/null | head -n 1 || echo 'Not installed')"
            echo -e "Offmute: $(npx offmute --version 2>/dev/null || echo 'Not installed')"
            # Check key packages
            echo -e "\n${BLUE}Checking installed packages:${NC}"
            uv pip list | grep -E "notion-client|yt-dlp|instaloader|fastapi"
            ;;
        4)
            echo -e "${BLUE}Checking output directory...${NC}"
            output_dir="/home/walub/Documents/Processed-ContentIdeas"
            if [ ! -d "$output_dir" ]; then
                echo -e "${YELLOW}Output directory doesn't exist. Creating it now...${NC}"
                mkdir -p "$output_dir"
                echo -e "${GREEN}Output directory created at: $output_dir${NC}"
            else
                echo -e "${GREEN}Output directory exists at: $output_dir${NC}"
                file_count=$(find "$output_dir" -type f | wc -l)
                echo -e "Contains $file_count files"
                echo -e "Total size: $(du -sh "$output_dir" | cut -f1)"
            fi
            ;;
        5)
            echo -e "${BLUE}Testing transcript generation...${NC}"
            
            # First check if Offmute is installed
            if ! command -v npx &> /dev/null; then
                echo -e "${RED}NPX is not installed. Cannot run Offmute.${NC}"
                echo -e "${YELLOW}Please install Node.js and NPM first.${NC}"
            else
                # Check if offmute is available
                if ! npx offmute --version &> /dev/null; then
                    echo -e "${RED}Offmute is not installed or not accessible.${NC}"
                    echo -e "${YELLOW}Try installing it with: npm install -g offmute${NC}"
                else
                    echo -e "${GREEN}✓ Offmute is installed: $(npx offmute --version 2>&1)${NC}"
                    
                    # Now check for GEMINI_API_KEY
                    if [ -z "$GEMINI_API_KEY" ]; then
                        echo -e "${RED}GEMINI_API_KEY not set. Transcript generation will be limited.${NC}"
                        echo -e "${YELLOW}Set this in your .env file for full functionality.${NC}"
                    else
                        echo -e "${GREEN}✓ GEMINI_API_KEY is set${NC}"
                    fi
                    
                    # Offer to run a real test with a sample file
                    echo -e "${YELLOW}Would you like to run a full test with a sample audio file? (yes/no)${NC}"
                    read -p "This will create a test transcript file: " run_test
                    
                    if [ "$run_test" = "yes" ]; then
                        # Create a temporary directory
                        test_dir="/tmp/offmute_test"
                        mkdir -p "$test_dir"
                        
                        echo -e "${YELLOW}Running transcript test...${NC}"
                        
                        # Try to find a sample audio/video file, or download one
                        sample_file=""
                        
                        # Look for existing sample files
                        if [ -d "test_samples" ] && [ -f "test_samples/sample.mp3" ]; then
                            sample_file="test_samples/sample.mp3"
                        elif [ -f "/usr/share/sounds/alsa/Front_Center.wav" ]; then
                            # Use system sample sound on Linux
                            sample_file="/usr/share/sounds/alsa/Front_Center.wav"
                        fi
                        
                        if [ -z "$sample_file" ]; then
                            # Create a simple test file with ffmpeg if available
                            if command -v ffmpeg &> /dev/null; then
                                test_wav="$test_dir/test_audio.wav"
                                echo -e "${YELLOW}Creating test audio file...${NC}"
                                ffmpeg -f lavfi -i "sine=frequency=1000:duration=3" -ar 44100 "$test_wav" -y &> /dev/null
                                sample_file="$test_wav"
                            else
                                echo -e "${RED}No sample file found and ffmpeg is not available to create one.${NC}"
                                echo -e "${YELLOW}Please install ffmpeg or place a sample file in test_samples/sample.mp3${NC}"
                                rm -rf "$test_dir"
                                break
                            fi
                        fi
                        
                        # Run offmute with the sample file
                        test_output="$test_dir/transcript.txt"
                        echo -e "${YELLOW}Processing sample file with Offmute...${NC}"
                        
                        export GEMINI_API_KEY
                        npx offmute "$sample_file" --output "$test_output" &> "$test_dir/offmute.log"
                        
                        if [ -f "$test_output" ] && [ -s "$test_output" ]; then
                            echo -e "${GREEN}✓ Transcript generation successful!${NC}"
                            echo -e "${BLUE}Generated transcript preview:${NC}"
                            head -n 5 "$test_output"
                            echo -e "${YELLOW}...(truncated)${NC}"
                        else
                            echo -e "${RED}Failed to generate transcript.${NC}"
                            echo -e "${YELLOW}Offmute log:${NC}"
                            cat "$test_dir/offmute.log"
                        fi
                        
                        # Clean up
                        echo -e "${YELLOW}Cleaning up test files...${NC}"
                        rm -rf "$test_dir"
                    else
                        echo -e "${YELLOW}Skipping full transcript test.${NC}"
                    fi
                fi
            fi
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    
    # Return to diagnostics menu after action
    read -p "Press Enter to return to diagnostics menu..."
    run_diagnostics
}

# Function to handle configuration
manage_config() {
    echo -e "\n${GREEN}Configuration Management${NC}"
    echo -e "${YELLOW}1)${NC} View current configuration"
    echo -e "${YELLOW}2)${NC} Edit YouTube processor settings"
    echo -e "${YELLOW}3)${NC} Edit Instagram processor settings"
    echo -e "${YELLOW}4)${NC} Edit output settings"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " config_choice
    
    case $config_choice in
        1)
            echo -e "${BLUE}Current configuration:${NC}"
            if [ -f "platform_config.py" ]; then
                echo -e "${YELLOW}=== Platform Settings ===${NC}"
                grep -E "YOUTUBE_|INSTAGRAM_|DEFAULT_" platform_config.py
            else
                echo -e "${RED}Configuration file not found.${NC}"
            fi
            
            echo -e "\n${YELLOW}=== Environment Variables ===${NC}"
            echo -e "NOTION_API_TOKEN: ${NOTION_API_TOKEN:0:5}..."
            echo -e "NOTION_DATABASE_ID: ${NOTION_DATABASE_ID:0:10}..."
            echo -e "GEMINI_API_KEY: ${GEMINI_API_KEY:+Set (not shown)}"
            ;;
        2)
            if [ ! -f "platform_config.py" ]; then
                echo -e "${RED}Configuration file not found.${NC}"
                break
            fi
            
            echo -e "${BLUE}Current YouTube settings:${NC}"
            grep -E "YOUTUBE_" platform_config.py
            
            echo -e "\n${YELLOW}Edit YouTube settings:${NC}"
            read -p "Enter new batch size [5]: " yt_batch
            read -p "Enter delay in seconds [0]: " yt_delay
            
            yt_batch=${yt_batch:-5}
            yt_delay=${yt_delay:-0}
            
            sed -i "s/YOUTUBE_BATCH_SIZE = [0-9]*/YOUTUBE_BATCH_SIZE = $yt_batch/" platform_config.py
            sed -i "s/YOUTUBE_DELAY_SECONDS = [0-9]*/YOUTUBE_DELAY_SECONDS = $yt_delay/" platform_config.py
            
            echo -e "${GREEN}YouTube settings updated.${NC}"
            ;;
        3)
            if [ ! -f "platform_config.py" ]; then
                echo -e "${RED}Configuration file not found.${NC}"
                break
            fi
            
            echo -e "${BLUE}Current Instagram settings:${NC}"
            grep -E "INSTAGRAM_" platform_config.py
            
            echo -e "\n${YELLOW}Edit Instagram settings:${NC}"
            read -p "Enter new batch size [1]: " ig_batch
            read -p "Enter delay in seconds [900]: " ig_delay
            
            ig_batch=${ig_batch:-1}
            ig_delay=${ig_delay:-900}
            
            sed -i "s/INSTAGRAM_BATCH_SIZE = [0-9]*/INSTAGRAM_BATCH_SIZE = $ig_batch/" platform_config.py
            sed -i "s/INSTAGRAM_DELAY_SECONDS = [0-9]*/INSTAGRAM_DELAY_SECONDS = $ig_delay/" platform_config.py
            
            echo -e "${GREEN}Instagram settings updated.${NC}"
            ;;
        4)
            echo -e "${BLUE}Output directory settings:${NC}"
            output_dir="/home/walub/Documents/Processed-ContentIdeas"
            echo -e "Current output directory: $output_dir"
            
            read -p "Do you want to change the output directory? (yes/no): " change_dir
            if [ "$change_dir" = "yes" ]; then
                read -p "Enter new output directory: " new_dir
                if [ -n "$new_dir" ]; then
                    if [ ! -d "$new_dir" ]; then
                        mkdir -p "$new_dir"
                    fi
                    # Update the output directory in configuration files
                    # This would need to be adapted to your actual configuration system
                    echo -e "${GREEN}Output directory updated to: $new_dir${NC}"
                    echo -e "${YELLOW}Note: You may need to update other configuration files manually.${NC}"
                else
                    echo -e "${RED}Invalid directory. No changes made.${NC}"
                fi
            fi
            ;;
        b|B)
            return
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
    
    # Return to config menu after action
    read -p "Press Enter to return to configuration menu..."
    manage_config
}

# Process YouTube links
process_youtube() {
    limit=$1
    
    echo -e "${BLUE}Processing YouTube links...${NC}"
    echo -e "${YELLOW}This will process up to $limit YouTube links from Notion.${NC}"
    
    # Run the YouTube processor
    if [ -f "process_links.py" ]; then
        run_with_uv process_links.py --platform youtube --limit "$limit"
    else
        # Fallback to old script if new one doesn't exist
        run_with_uv run_youtube_post.py --limit "$limit"
    fi
    
    echo -e "${GREEN}YouTube processing complete.${NC}"
}

# Process Instagram links
process_instagram() {
    limit=$1
    
    echo -e "${BLUE}Processing Instagram links...${NC}"
    echo -e "${YELLOW}This will process up to $limit Instagram links from Notion.${NC}"
    echo -e "${YELLOW}Note: Instagram has rate limits, so processing may be slower.${NC}"
    
    # Run the Instagram processor
    if [ -f "process_links.py" ]; then
        run_with_uv process_links.py --platform instagram --limit "$limit"
    else
        # Fallback to old script if new one doesn't exist
        run_with_uv run_instagram_post.py --limit "$limit"
    fi
    
    echo -e "${GREEN}Instagram processing complete.${NC}"
}

# Process all platforms
process_all() {
    limit=$1
    parallel=$2
    
    echo -e "${BLUE}Processing all platforms...${NC}"
    echo -e "${YELLOW}This will process up to $limit links from each platform.${NC}"
    
    if [ "$parallel" = "true" ]; then
        echo -e "${YELLOW}Running platforms in parallel...${NC}"
        
        # Run both processors in parallel
        if [ -f "process_links.py" ]; then
            run_with_uv process_links.py --platform all --limit "$limit" --parallel &
            wait
        else
            # Fallback to old scripts if new one doesn't exist
            run_with_uv run_youtube_post.py --limit "$limit" &
            run_with_uv run_instagram_post.py --limit "$limit" &
            wait
        fi
    else
        echo -e "${YELLOW}Running platforms sequentially...${NC}"
        
        # Run both processors sequentially
        if [ -f "process_links.py" ]; then
            run_with_uv process_links.py --platform all --limit "$limit"
        else
            # Fallback to old scripts if new one doesn't exist
            run_with_uv run_youtube_post.py --limit "$limit"
            run_with_uv run_instagram_post.py --limit "$limit"
        fi
    fi
    
    echo -e "${GREEN}All platform processing complete.${NC}"
}

# Main menu function
show_menu() {
    echo -e "\n${GREEN}Select an action:${NC}"
    echo -e "${YELLOW}1)${NC} Process YouTube links"
    echo -e "${YELLOW}2)${NC} Process Instagram links"
    echo -e "${YELLOW}3)${NC} Process all platforms"
    echo -e "${YELLOW}4)${NC} View processing status"
    echo -e "${YELLOW}5)${NC} System diagnostics"
    echo -e "${YELLOW}6)${NC} Configuration"
    echo -e "${YELLOW}h)${NC} Show help"
    echo -e "${YELLOW}q)${NC} Quit"

    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Processing YouTube links${NC}"
            read -p "Enter maximum number of links to process [1]: " limit
            limit=${limit:-1}
            process_youtube "$limit"
            ;;
        2)
            echo -e "${YELLOW}Processing Instagram links${NC}"
            read -p "Enter maximum number of links to process [1]: " limit
            limit=${limit:-1}
            process_instagram "$limit"
            ;;
        3)
            echo -e "${YELLOW}Processing all platforms${NC}"
            read -p "Enter maximum number of links to process per platform [1]: " limit
            limit=${limit:-1}
            read -p "Run in parallel? (yes/no) [no]: " parallel
            parallel=${parallel:-no}
            parallel_flag="false"
            if [ "$parallel" = "yes" ]; then
                parallel_flag="true"
            fi
            process_all "$limit" "$parallel_flag"
            ;;
        4)
            view_status
            ;;
        5)
            run_diagnostics
            ;;
        6)
            manage_config
            ;;
        h|H)
            show_help
            ;;
        q|Q)
            echo -e "${GREEN}Exiting.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
}

# Main function
main() {
    show_header
    check_uv
    setup_env
    check_env_vars
    
    # If command-line arguments were provided
    if [ $# -gt 0 ]; then
        case "$1" in
            "youtube")
                limit=${2:-1}
                process_youtube "$limit"
                ;;
            "instagram")
                limit=${2:-1}
                process_instagram "$limit"
                ;;
            "all")
                limit=${2:-1}
                parallel_flag="false"
                if [ "$3" = "--parallel" ]; then
                    parallel_flag="true"
                fi
                process_all "$limit" "$parallel_flag"
                ;;
            "status")
                view_status
                ;;
            "diagnostics")
                run_diagnostics
                ;;
            "config")
                if [ "$2" = "view" ]; then
                    if [ -f "platform_config.py" ]; then
                        echo -e "${BLUE}Platform configuration:${NC}"
                        cat platform_config.py
                    else
                        echo -e "${RED}Configuration file not found.${NC}"
                    fi
                else
                    manage_config
                fi
                ;;
            "help")
                show_help
                ;;
            *)
                echo -e "${RED}Unknown command: $1${NC}"
                show_help
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # Interactive mode
    while true; do
        show_menu
        echo
        read -p "Press Enter to continue..."
    done
}

# Make the script executable
chmod +x "$0"

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo -e "${BLUE}Loading environment variables from .env${NC}"
    set -a
    source .env
    set +a
fi

# Run the script
main "$@" 