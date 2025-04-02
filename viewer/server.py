import http.server
import socketserver
import os
import json
import re
import urllib.parse
import posixpath
from datetime import datetime
from pathlib import Path

# Get the project root directory (parent of viewer directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define paths relative to project root
OUTPUT_DIRECTORY = PROJECT_ROOT / 'output'
VIEWER_DIRECTORY = PROJECT_ROOT / 'viewer'

# Server configuration
PORT = 8081

# Function to get metadata for all videos
def get_video_metadata():
    videos = []
    
    try:
        print(f"Scanning for videos in: {OUTPUT_DIRECTORY}")
        # Look in both output directory and its subdirectories
        for root, dirs, files in os.walk(OUTPUT_DIRECTORY):
            print(f"Scanning directory: {root}")
            # Filter for MP4 files
            mp4_files = [f for f in files if f.endswith('.mp4')]
            
            print(f"Found {len(mp4_files)} MP4 files in {root}")
            
            for filename in mp4_files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, OUTPUT_DIRECTORY)
                
                print(f"Processing file: {relative_path}")
                
                # Parse the filename to extract metadata
                base_name = os.path.splitext(filename)[0]
                
                # Check if transcript exists
                transcript_path = os.path.join(root, base_name + '.md')
                has_transcript = os.path.exists(transcript_path)
                
                # Check for thumbnail
                thumbnail_path = None
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    possible_thumb = os.path.join(root, base_name + ext)
                    if os.path.exists(possible_thumb):
                        thumbnail_path = os.path.relpath(possible_thumb, OUTPUT_DIRECTORY)
                        break
                
                # Extract date using regex
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', base_name)
                date_str = date_match.group(1) if date_match else ""
                
                # Extract username and description
                parts = base_name.split('-')
                if len(parts) >= 1:  # Changed from >= 4 to >= 1 to be more permissive
                    username = parts[0] if parts else "Unknown"
                    
                    # Get parts after the date for the description
                    date_index = -1
                    for i, part in enumerate(parts):
                        if date_match and date_match.group(1) in part:
                            date_index = i
                            break
                    
                    if date_index >= 0 and date_index + 1 < len(parts):
                        description = ' '.join(parts[date_index+1:]).replace('-', ' ')
                    else:
                        description = base_name
                    
                    # URL encode the filename for safe handling in URLs (especially # characters)
                    safe_filename = urllib.parse.quote(relative_path, safe='')
                    
                    videos.append({
                        'filename': relative_path,
                        'safe_filename': safe_filename,
                        'basename': base_name,
                        'username': username,
                        'date': date_str,
                        'description': description,
                        'hasTranscript': has_transcript,
                        'thumbnail': thumbnail_path,
                        'size': os.path.getsize(file_path)
                    })
        
        # Sort videos by date (newest first)
        videos.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
        
        print(f"Found {len(videos)} video files in {OUTPUT_DIRECTORY}")
        
        # Debug print the first video data for inspection
        if videos:
            print(f"First video metadata: {videos[0]}")
    except Exception as e:
        print(f"Error scanning videos directory: {e}")
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
    
    return videos

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local testing
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax."""
        # Special case for the video list API
        if path == '/api/videos':
            return None
            
        # Print path for debugging
        print(f"Requested path: {path}")
        
        # URL decode the path to handle URL-encoded characters
        try:
            decoded_path = urllib.parse.unquote(path, errors='surrogatepass')
            print(f"URL-decoded path: {decoded_path}")
        except UnicodeDecodeError:
            decoded_path = path
        
        # Check if this is requesting a transcript file
        is_transcript = decoded_path.endswith('.md')
        if is_transcript:
            print(f"Transcript file requested: {decoded_path}")
            
        # abandon query parameters
        decoded_path = decoded_path.split('?',1)[0]
        
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = decoded_path.rstrip().endswith('/')
        try:
            decoded_path = urllib.parse.unquote(decoded_path, errors='surrogatepass')
        except UnicodeDecodeError:
            decoded_path = urllib.parse.unquote_to_bytes(decoded_path)
            decoded_path = decoded_path.decode('utf-8', 'replace')
        decoded_path = posixpath.normpath(decoded_path)
        
        print(f"Normalized path: {decoded_path}")
        
        # Determine which directory to use based on the path
        if decoded_path == '/' or decoded_path == '/videos.html':
            # Serve viewer files from the viewer directory
            result = os.path.join(VIEWER_DIRECTORY, decoded_path.lstrip('/') or 'videos.html')
            print(f"Serving viewer file: {result}")
            return result
        else:
            # For all media content, serve from the output directory
            words = decoded_path.split('/')
            words = filter(None, words)
            path = OUTPUT_DIRECTORY
            
            for word in words:
                if os.path.dirname(word) or word in (os.curdir, os.pardir):
                    # Ignore components that are not a simple filename
                    continue
                path = os.path.join(path, word)
            if trailing_slash:
                path += '/'
            
            # Check if the file exists
            if os.path.exists(path):
                print(f"Serving content file (exists): {path}")
                # For transcript files, set the content type to text/markdown
                if path.endswith('.md'):
                    self.content_type = 'text/markdown'
            else:
                print(f"File not found: {path}")
                # Try to find a matching file regardless of case or URL encoding
                try:
                    parent_dir = os.path.dirname(path)
                    basename = os.path.basename(path)
                    if os.path.exists(parent_dir):
                        for file in os.listdir(parent_dir):
                            if os.path.basename(file).lower() == basename.lower():
                                corrected_path = os.path.join(parent_dir, file)
                                print(f"Found close match: {corrected_path}")
                                return corrected_path
                except Exception as e:
                    print(f"Error trying to find matching file: {e}")
                
            return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects."""
        try:
            import shutil
            shutil.copyfileobj(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            print(f"Client disconnected while receiving file: {self.path}")
        except Exception as e:
            print(f"Error copying file {self.path}: {e}")

    def do_GET(self):
        try:
            if self.path == '/api/videos':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Get video metadata
                video_data = get_video_metadata()
                self.wfile.write(json.dumps(video_data).encode())
            elif self.path == '/':
                # Redirect to videos.html
                self.send_response(302)
                self.send_header('Location', '/videos.html')
                self.end_headers()
            else:
                # Check if it's a request for a transcript file
                if self.path.endswith('.md'):
                    path = self.translate_path(self.path)
                    try:
                        # Check if file exists
                        if not os.path.isfile(path):
                            self.send_error(404, "Transcript not found")
                            return
                            
                        # Send response headers
                        self.send_response(200)
                        self.send_header('Content-type', 'text/markdown')
                        fs = os.fstat(os.open(path, os.O_RDONLY))
                        self.send_header('Content-Length', str(fs[6]))
                        self.end_headers()
                        
                        # Send file content
                        with open(path, 'rb') as f:
                            self.copyfile(f, self.wfile)
                            
                        print(f"Successfully served transcript: {path}")
                        return
                    except Exception as e:
                        print(f"Error serving transcript {path}: {e}")
                        self.send_error(500, f"Error serving transcript: {str(e)}")
                        return
                        
                # For all other files, use the default handler
                return super().do_GET()
        except BrokenPipeError:
            print("Client disconnected while receiving data (broken pipe).")
            return
        except ConnectionResetError:
            print("Connection reset by client.")
            return
        except Exception as e:
            print(f"Error handling request: {e}")
            return

def main():
    """Start the server."""
    # Ensure output directory exists
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create the server with a custom socket handling
        # Use "0.0.0.0" instead of "" to explicitly bind to all interfaces
        server = socketserver.TCPServer(("0.0.0.0", PORT), MyHandler)
        server.allow_reuse_address = True
        
        print(f"Starting viewer server at http://0.0.0.0:{PORT}")
        print(f"Serving content from: {OUTPUT_DIRECTORY}")
        print(f"Serving viewer files from: {VIEWER_DIRECTORY}")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'server' in locals():
            server.server_close()
            print("Server closed.")

if __name__ == "__main__":
    main()