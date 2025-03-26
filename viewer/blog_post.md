# Building a Personal Instagram Content Viewer: From Download to Display

In the world of digital content, Instagram hosts a wealth of valuable information and educational content. However, finding and reviewing this content later can be challenging. Today, I'd like to share a personal project I've been working on - an Instagram Videos Viewer that automatically organizes and displays saved Instagram content with transcripts.

## The Problem: Content Organization and Accessibility

Like many of you, I save interesting Instagram posts for later viewing. But Instagram's interface isn't optimized for revisiting content, especially when you want to:

- Search through saved videos by creator or topic
- Reference content without an internet connection
- Review written transcripts instead of watching videos again
- Organize content by date or other metadata

## The Solution: A Personal Content Viewer

I built a local web application that serves as a personal Instagram content library with these key features:

1. **Smart organization**: Videos are automatically categorized by creator and date
2. **Full-text search**: Find videos by searching descriptions and transcripts
3. **Transcript viewer**: Read instead of watch when preferred
4. **Offline access**: Everything runs locally, no internet required
5. **Clean, modern UI**: Dark mode interface for comfortable viewing

## Technical Implementation: The Transcript Viewer

One of the most interesting technical challenges was building a good transcript viewing experience. When displaying long-form text content in a modal dialog, several UX considerations came into play:

### Fixed Position Navigation

A common issue with modal scrolling is losing access to navigation controls. Our first implementation had the close button attached to the scrollable content, causing it to disappear when users scrolled down through long transcripts.

```javascript
// Original problematic implementation
modalContent.appendChild(closeBtn);
modalContent.appendChild(modalTitle);
modalContent.appendChild(modalBody);
```

The solution was to position the close button outside the scrollable container:

```javascript
// Fixed implementation
modal.appendChild(closeBtn); // Attached to the non-scrolling parent
modalContent.appendChild(modalTitle);
modalContent.appendChild(modalBody);
```

Combined with fixed CSS positioning:

```css
.close-btn {
    position: fixed;
    top: 15px;
    right: 15px;
    z-index: 1010;
}
```

This ensures the close button remains accessible regardless of how far the user scrolls.

### Improved Text Readability

For comfortable reading, we increased the font size and line spacing of transcript text:

```css
.markdown-content {
    line-height: 1.6;
    color: #e0e0e0;
    font-size: 1.2em; /* Increased from typical 1em */
}
```

### Enhanced Error Handling

We added robust error handling for transcript loading:

```javascript
fetch('./' + transcriptPath)
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to load transcript: ${response.status}`);
        }
        return response.text();
    })
    .then(text => {
        console.log("Transcript loaded successfully");
        showTranscriptModal(cleanTitle, text);
    })
    .catch(err => {
        console.error('Error loading transcript:', err);
        showTranscriptModal('Transcript Not Found', 
            'No transcript available for this video. Error: ' + err.message);
    });
```

This provides clear feedback when transcripts aren't available or can't be loaded.

## Server-Side Implementation

On the backend, we use Python's built-in HTTP server to serve both the video files and transcript files:

```python
# Special handling for transcript (.md) files
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
    except Exception as e:
        print(f"Error serving transcript {path}: {e}")
        self.send_error(500, f"Error serving transcript: {str(e)}")
```

## Future Improvements

Some potential next steps for this project include:

1. **Search inside transcripts**: Allow full-text search within the transcript content
2. **Timestamps in transcripts**: Link transcript sections back to specific video timestamps
3. **Tags and categories**: Add support for custom tagging and categorization
4. **Mobile app**: Develop a mobile version for on-the-go access
5. **AI summaries**: Generate automatic summaries of long transcripts

## Conclusion

Building this personal content viewer has significantly improved how I revisit and reference Instagram content. The ability to quickly search, view, and read content in a clean interface has saved me countless hours.

The project demonstrates how relatively simple technologies (Python's HTTP server and vanilla JavaScript) can be combined to create a powerful personal knowledge management tool.

If you're interested in setting up your own Instagram content viewer, the full source code is available on GitHub (link) with detailed installation instructions.

---

_What personal tools have you built to improve your content consumption? Let me know in the comments below!_ 