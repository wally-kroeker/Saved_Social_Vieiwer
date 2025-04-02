# Scheduling Implementation Plan

This document outlines the approach for implementing automated scheduling for the Process Saved Links project, ensuring the system runs three times daily.

## Requirements

- Run the system automatically at three specific times:
  - Morning (8:00 AM)
  - Noon (12:00 PM)
  - Night (11:00 PM)
- Ensure proper logging for unattended execution
- Handle errors gracefully
- Prevent overlapping runs

## Implementation Approach

We'll implement scheduling using two complementary methods:

1. **Cron Jobs**: For system-level scheduling
2. **Internal Scheduler**: For managing execution flow and preventing overlaps

### Cron Job Configuration

Cron jobs will be used to trigger the script at the specified times. Here's the crontab configuration:

```
# Process Saved Links - Run three times daily
0 8 * * * cd /home/walub/scripts/Process_Saved_Links && python main.py --scheduled morning >> /home/walub/scripts/Process_Saved_Links/logs/scheduled_$(date +\%Y\%m\%d).log 2>&1
0 12 * * * cd /home/walub/scripts/Process_Saved_Links && python main.py --scheduled noon >> /home/walub/scripts/Process_Saved_Links/logs/scheduled_$(date +\%Y\%m\%d).log 2>&1
0 23 * * * cd /home/walub/scripts/Process_Saved_Links && python main.py --scheduled night >> /home/walub/scripts/Process_Saved_Links/logs/scheduled_$(date +\%Y\%m\%d).log 2>&1
```

This configuration:
- Runs the script at 8:00 AM, 12:00 PM, and 11:00 PM
- Passes a `--scheduled` flag with the time of day
- Redirects output to a daily log file
- Changes to the project directory before execution

### Internal Scheduler Implementation

The internal scheduler will be implemented in Python to manage the execution flow:

```python
# scheduler.py

import os
import time
import logging
import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class Scheduler:
    """Manages scheduled execution of the link processing system"""
    
    def __init__(self, config):
        self.config = config
        self.lock_file = Path(config.get('lock_file', '/tmp/process_saved_links.lock'))
        self.status_file = Path(config.get('status_file', 'status.json'))
        self.pause_time = config.get('pause_between_items', 900)  # 15 minutes in seconds
    
    def acquire_lock(self):
        """Try to acquire the execution lock"""
        if self.lock_file.exists():
            # Check if the lock is stale (older than 6 hours)
            lock_time = datetime.datetime.fromtimestamp(self.lock_file.stat().st_mtime)
            current_time = datetime.datetime.now()
            if (current_time - lock_time).total_seconds() < 21600:  # 6 hours
                logger.warning(f"Another instance is already running (lock file: {self.lock_file})")
                return False
            else:
                logger.warning(f"Found stale lock file, removing: {self.lock_file}")
                self.lock_file.unlink()
        
        # Create the lock file
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        return True
    
    def release_lock(self):
        """Release the execution lock"""
        if self.lock_file.exists():
            self.lock_file.unlink()
    
    def update_status(self, run_type, status, items_processed=0):
        """Update the status file with the latest execution information"""
        status_data = {}
        
        # Read existing status if available
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status_data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error reading status file: {self.status_file}")
        
        # Update status
        current_time = datetime.datetime.now().isoformat()
        status_data[run_type] = {
            'last_run': current_time,
            'status': status,
            'items_processed': items_processed
        }
        
        # Write updated status
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def should_run(self, run_type):
        """Check if the system should run based on previous executions"""
        if not self.status_file.exists():
            return True
        
        try:
            with open(self.status_file, 'r') as f:
                status_data = json.load(f)
            
            if run_type not in status_data:
                return True
            
            last_run = datetime.datetime.fromisoformat(status_data[run_type]['last_run'])
            current_time = datetime.datetime.now()
            
            # If the last run was more than 4 hours ago, allow running again
            if (current_time - last_run).total_seconds() > 14400:  # 4 hours
                return True
            
            logger.info(f"Skipping {run_type} run, last run was at {last_run}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking run status: {e}")
            return True
    
    def run_scheduled(self, run_type, processor_func):
        """Run the system with scheduling logic"""
        logger.info(f"Starting scheduled run: {run_type}")
        
        # Check if we should run
        if not self.should_run(run_type):
            return
        
        # Try to acquire lock
        if not self.acquire_lock():
            return
        
        try:
            # Run the processor function
            items_processed = processor_func()
            
            # Update status
            self.update_status(run_type, "completed", items_processed)
            
            logger.info(f"Completed scheduled run: {run_type}, processed {items_processed} items")
            
        except Exception as e:
            logger.error(f"Error during scheduled run: {e}", exc_info=True)
            self.update_status(run_type, "failed")
        
        finally:
            # Always release the lock
            self.release_lock()
    
    def pause_between_items(self):
        """Pause between processing items"""
        logger.info(f"Pausing for {self.pause_time // 60} minutes before processing the next item...")
        time.sleep(self.pause_time)
```

### Main Script Integration

The main script will integrate with the scheduler:

```python
# main.py

import argparse
import logging
import sys
from scheduler import Scheduler
from notion_integration import NotionIntegration
from processors import get_processor
from config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/process_links.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process saved social media links.')
    parser.add_argument('--scheduled', choices=['morning', 'noon', 'night'],
                        help='Run as a scheduled job (morning, noon, or night)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Maximum number of links to process')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    return parser.parse_args()

def process_links(config, limit=None):
    """Process links from the Notion database"""
    notion = NotionIntegration(config)
    scheduler = Scheduler(config)
    
    # Get unprocessed links
    links = notion.get_unprocessed_links(limit)
    
    if not links:
        logger.info("No new links to process.")
        return 0
    
    logger.info(f"Processing {len(links)} links...")
    
    items_processed = 0
    
    for i, link_data in enumerate(links):
        link = link_data['url']
        page_id = link_data['page_id']
        metadata = link_data['metadata']
        
        logger.info(f"Processing link {i+1}/{len(links)}: {link}")
        
        # Get the appropriate processor for this link
        processor = get_processor(link, config)
        
        if not processor:
            logger.warning(f"No processor available for link: {link}")
            continue
        
        # Process the link
        try:
            result = processor.process(link, metadata)
            
            if result:
                # Update Notion database
                notion.update_status(page_id, result.get('video', ''), status="Done")
                items_processed += 1
                logger.info(f"Successfully processed: {link}")
            else:
                notion.update_status(page_id, "", status="Failed")
                logger.error(f"Failed to process: {link}")
        
        except Exception as e:
            logger.error(f"Error processing link: {e}", exc_info=True)
            notion.update_status(page_id, "", status="Failed")
        
        # Pause between items, but not after the last one
        if i < len(links) - 1:
            scheduler.pause_between_items()
    
    logger.info(f"Completed processing {items_processed} out of {len(links)} links")
    return items_processed

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config()
    
    # If running as a scheduled job
    if args.scheduled:
        scheduler = Scheduler(config)
        scheduler.run_scheduled(args.scheduled, lambda: process_links(config, args.limit))
    else:
        # Run directly
        process_links(config, args.limit)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
```

## Setting Up Cron Jobs

To set up the cron jobs, follow these steps:

1. Open the crontab editor:
   ```
   crontab -e
   ```

2. Add the cron job entries as specified above

3. Save and exit the editor

## Monitoring and Maintenance

### Log Rotation

To prevent logs from growing too large, we'll implement log rotation:

```
# /etc/logrotate.d/process_saved_links
/home/walub/scripts/Process_Saved_Links/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 walub walub
}
```

### Status Monitoring

The status file (`status.json`) will contain information about the last run:

```json
{
  "morning": {
    "last_run": "2025-02-26T08:00:12.345678",
    "status": "completed",
    "items_processed": 5
  },
  "noon": {
    "last_run": "2025-02-26T12:00:09.123456",
    "status": "completed",
    "items_processed": 3
  },
  "night": {
    "last_run": "2025-02-25T23:00:15.678901",
    "status": "completed",
    "items_processed": 7
  }
}
```

This file can be used to:
- Track when the system last ran
- Monitor success/failure status
- Count processed items

## Error Handling and Recovery

The scheduling system includes several error handling mechanisms:

1. **Lock File**: Prevents multiple instances from running simultaneously
2. **Stale Lock Detection**: Automatically cleans up stale locks (older than 6 hours)
3. **Status Tracking**: Records the outcome of each run
4. **Exception Handling**: Catches and logs all exceptions
5. **Logging**: Comprehensive logging for debugging

## Testing the Scheduler

To test the scheduler:

1. **Manual Testing**:
   ```
   python main.py --scheduled morning
   python main.py --scheduled noon
   python main.py --scheduled night
   ```

2. **Simulated Cron Execution**:
   ```
   cd /home/walub/scripts/Process_Saved_Links && python main.py --scheduled morning
   ```

3. **Lock File Testing**:
   - Run two instances simultaneously to verify lock file works
   - Create a stale lock file to verify cleanup works

## Conclusion

This scheduling implementation provides a robust solution for running the Process Saved Links system three times daily. It includes mechanisms for preventing overlaps, handling errors, and tracking execution status, ensuring reliable automated operation.