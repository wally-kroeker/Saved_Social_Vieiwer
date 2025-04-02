document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const contentGrid = document.getElementById('content-grid');
    const contentCount = document.getElementById('content-count');
    const loadingElement = document.getElementById('loading');
    const noResultsElement = document.getElementById('no-results');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const platformFilter = document.getElementById('platform-filter');
    const contentModal = document.getElementById('content-modal');
    const modalContentContainer = document.getElementById('modal-content-container');
    const closeBtn = document.querySelector('.close-btn');
    
    // Templates
    const contentItemTemplate = document.getElementById('content-item-template');
    const videoViewTemplate = document.getElementById('video-view-template');
    
    // State
    let currentItems = [];
    let currentPlatform = '';
    let currentSearch = '';
    let resizeTimeout = null;
    
    // Helper functions for video cards
    function getThumbnailPath(thumbnailFile) {
        if (!thumbnailFile) return '';
        // Assuming the thumbnail is in the same folder as the video
        return `/media/${currentPlatform}/${thumbnailFile}`;
    }
    
    function getVideoPath(videoFile) {
        if (!videoFile) return '';
        return `/media/${currentPlatform}/${videoFile}`;
    }
    
    function extractCleanTitle(video) {
        if (!video.title) return '';
        // Remove leading numbers pattern like "02 24" or "03 07" at the beginning of the title
        return video.title.replace(/^\d{2}\s\d{2}\s+/, '');
    }
    
    function showVideoPlayer(item) {
        modalContentContainer.innerHTML = ''; // Clear previous content
        
        const playerContainer = document.createElement('div');
        playerContainer.className = 'modal-player-container';

        const videoEl = document.createElement('video');
        // Use item properties directly
        videoEl.src = `/media/${item.platform}/${item.filename}.mp4`;
        videoEl.controls = true;
        videoEl.autoplay = true;
        videoEl.className = 'content-video';
        
        const titleEl = document.createElement('h2');
        // Use extractCleanTitle with the item object
        titleEl.textContent = toTitleCase(extractCleanTitle(item));
        titleEl.className = 'content-title modal-title';
        
        // Container for buttons and transcript
        const controlsContainer = document.createElement('div');
        controlsContainer.style.textAlign = 'center'; // Center button
        controlsContainer.style.marginTop = '1rem';

        const transcriptContainer = document.createElement('div');
        transcriptContainer.className = 'modal-transcript-container';
        transcriptContainer.style.display = 'none'; // Hidden initially

        // Create View Transcript button
        const transcriptBtn = document.createElement('button');
        transcriptBtn.textContent = 'View Transcript';
        transcriptBtn.className = 'btn transcript-btn'; // Reuse existing styles
        
        if (item.has_transcript) {
            transcriptBtn.addEventListener('click', () => {
                if (transcriptContainer.style.display === 'none') {
                    loadTranscriptModal(item, transcriptContainer);
                    transcriptContainer.style.display = 'block';
                    transcriptBtn.textContent = 'Hide Transcript';
                } else {
                    transcriptContainer.style.display = 'none';
                    transcriptBtn.textContent = 'View Transcript';
                }
            });
        } else {
            transcriptBtn.disabled = true;
            transcriptBtn.style.opacity = 0.5;
            transcriptBtn.style.cursor = 'not-allowed';
            transcriptBtn.title = 'No transcript available';
        }
        
        // Append elements
        playerContainer.appendChild(videoEl);
        playerContainer.appendChild(titleEl);
        controlsContainer.appendChild(transcriptBtn); // Add button to controls container
        playerContainer.appendChild(controlsContainer); // Add controls below title
        playerContainer.appendChild(transcriptContainer); // Add transcript container (initially hidden)
        modalContentContainer.appendChild(playerContainer);
        
        contentModal.style.display = 'block';
    }
    
    // Initialize the page
    initializePage();
    
    // Initialize page with event listeners and initial content load
    function initializePage() {
        // Set up event listeners
        searchBtn.addEventListener('click', handleSearch);
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                handleSearch();
            }
        });
        platformFilter.addEventListener('change', handlePlatformChange);
        closeBtn.addEventListener('click', closeModal);
        window.addEventListener('click', function(event) {
            if (event.target === contentModal) {
                closeModal();
            }
        });
        
        // Add resize event listener for responsive grid
        window.addEventListener('resize', handleResize);
        
        // Load initial content
        loadContent();
        
        // Optimize grid layout for initial view
        optimizeGridLayout();
    }
    
    // Handle window resize with debounce for performance
    function handleResize() {
        if (resizeTimeout) {
            clearTimeout(resizeTimeout);
        }
        
        resizeTimeout = setTimeout(function() {
            optimizeGridLayout();
        }, 200); // 200ms debounce
    }
    
    // Optimize grid layout based on screen size
    function optimizeGridLayout() {
        const containerWidth = contentGrid.clientWidth;
        const idealCardWidth = getIdealCardWidth();
        const cardsPerRow = Math.floor(containerWidth / idealCardWidth);
        const actualCardWidth = Math.floor(containerWidth / cardsPerRow) - 24; // accounting for gap
        
        // Adjust the grid for optimal filling of screen
        document.documentElement.style.setProperty('--card-width', `${actualCardWidth}px`);
        
        // Calculate ideal card height based on 4:3 aspect ratio for image plus 25% text area
        // The total card height should maintain a ratio where the image is 75% and text is 25%
        const imageHeight = Math.floor(actualCardWidth * 0.75); // 3:4 aspect ratio for image
        const textHeight = Math.floor(imageHeight * 0.33); // Text area is 25% of total height (1/3 of image height)
        const totalCardHeight = imageHeight + textHeight;
        
        document.documentElement.style.setProperty('--card-height', `${totalCardHeight}px`);
        document.documentElement.style.setProperty('--image-height', `${imageHeight}px`);
        document.documentElement.style.setProperty('--text-height', `${textHeight}px`);
        
        // Adjust content grid height to fill available space
        const mainContent = document.querySelector('.main-content');
        const headerHeight = document.querySelector('.site-header').offsetHeight;
        const countHeight = contentCount.offsetHeight;
        const footerHeight = document.querySelector('.site-footer').offsetHeight;
        const availableHeight = window.innerHeight - headerHeight - footerHeight - 40; // 40px for padding
        
        mainContent.style.height = `${availableHeight}px`;
    }
    
    // Get ideal card width based on screen size
    function getIdealCardWidth() {
        const screenWidth = window.innerWidth;
        
        if (screenWidth >= 2000) {
            return 350;
        } else if (screenWidth >= 1600) {
            return 320;
        } else if (screenWidth >= 1200) {
            return 280;
        } else if (screenWidth >= 768) {
            return 250;
        } else {
            return 200;
        }
    }
    
    // Close modal
    function closeModal() {
        contentModal.style.display = 'none';
        
        // Pause video if playing
        const video = modalContentContainer.querySelector('video');
        if (video) {
            video.pause();
        }
    }
    
    // Handle search input
    function handleSearch() {
        currentSearch = searchInput.value.trim();
        loadContent();
    }
    
    // Handle platform filter change
    function handlePlatformChange() {
        currentPlatform = platformFilter.value;
        loadContent();
    }
    
    // Load content items
    function loadContent() {
        showLoading(true);
        
        let url = '/api/content';
        const params = new URLSearchParams();
        
        if (currentPlatform) {
            params.append('platform', currentPlatform);
        }
        
        if (currentSearch) {
            params.append('search', currentSearch);
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                currentItems = data.items || [];
                renderItems();
                showLoading(false);
            })
            .catch(error => {
                console.error('Error fetching content:', error);
                showLoading(false);
                showNoResults(true);
            });
    }
    
    // Render content items
    function renderItems() {
        contentGrid.innerHTML = '';
        
        if (currentItems.length === 0) {
            showNoResults(true);
            contentCount.textContent = 'No content found';
            return;
        }
        
        showNoResults(false);
        contentCount.textContent = `${currentItems.length} items found`;
        
        currentItems.forEach(item => {
            const card = createVideoCard(item);
            contentGrid.appendChild(card);
        });
    }
    
    // Create content card (OLD FUNCTION - no longer called directly by renderItems)
    function createContentCard(item) {
        const template = contentItemTemplate.content.cloneNode(true);
        const card = template.querySelector('.content-card');
        
        // Set card data attributes
        card.dataset.platform = item.platform;
        card.dataset.filename = item.filename;
        
        // Set title with proper capitalization and remove leading numbers
        const title = template.querySelector('.content-title');
        let cleanTitle = item.title;
        
        // Remove leading numbers pattern like "02 24" or "03 07" at the beginning of the title
        cleanTitle = cleanTitle.replace(/^\d{2}\s\d{2}\s+/, '');
        
        title.textContent = toTitleCase(cleanTitle);
        title.title = toTitleCase(cleanTitle); // tooltip
        
        // Set metadata
        const username = template.querySelector('.content-username');
        username.textContent = formatUsername(item.username);
        
        const date = template.querySelector('.content-date');
        date.textContent = formatDate(item.date);
        
        const platform = template.querySelector('.content-platform');
        platform.textContent = capitalizeFirstLetter(item.platform);
        
        // Set thumbnail
        const thumbnailImg = template.querySelector('.thumbnail-img');
        const thumbnailPath = `/media/${item.platform}/${item.filename}.jpg`;
        thumbnailImg.src = thumbnailPath;
        thumbnailImg.alt = cleanTitle;
        
        // Set type badge
        const typeBadge = template.querySelector('.content-type-badge');
        typeBadge.textContent = item.platform;
        
        // Add event listener to view button
        const viewBtn = template.querySelector('.view-btn');
        viewBtn.addEventListener('click', () => {
            viewContent(item);
        });
        
        return card;
    }
    
    // View content
    function viewContent(item) {
        modalContentContainer.innerHTML = '';
        
        const template = videoViewTemplate.content.cloneNode(true);
        
        // Set video source
        const video = template.querySelector('.content-video');
        video.src = `/media/${item.platform}/${item.filename}.mp4`;
        
        // Clean title for display
        let cleanTitle = item.title;
        cleanTitle = cleanTitle.replace(/^\d{2}\s\d{2}\s+/, '');
        
        // Set content details
        const title = template.querySelector('.content-title');
        title.textContent = toTitleCase(cleanTitle);
        
        const username = template.querySelector('.content-username');
        username.textContent = formatUsername(item.username);
        
        const date = template.querySelector('.content-date');
        date.textContent = formatDate(item.date);
        
        const platform = template.querySelector('.content-platform');
        platform.textContent = capitalizeFirstLetter(item.platform);
        
        // Set tab events
        const tabBtns = template.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                
                // Update active tab button
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Show selected tab content
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(content => {
                    content.style.display = 'none';
                });
                document.getElementById(`${tabName}-tab`).style.display = 'block';
                
                // Load tab content if needed
                if (tabName === 'transcript' && item.has_transcript) {
                    loadTranscript(item);
                } else if (tabName === 'metadata' && item.has_metadata) {
                    loadMetadata(item);
                }
            });
        });
        
        // Add content to modal
        modalContentContainer.appendChild(template);
        
        // Show modal
        contentModal.style.display = 'block';
        
        // Load initial metadata
        loadMetadata(item);
        
        // Check if transcript is available
        const transcriptTab = document.querySelector('[data-tab="transcript"]');
        if (!item.has_transcript) {
            transcriptTab.setAttribute('disabled', 'disabled');
            transcriptTab.classList.add('disabled');
            transcriptTab.title = 'No transcript available';
        } else {
            transcriptTab.removeAttribute('disabled');
            transcriptTab.classList.remove('disabled');
            transcriptTab.title = '';
        }
    }
    
    // Load transcript
    function loadTranscript(item) {
        const transcriptContent = document.querySelector('.transcript-content');
        transcriptContent.innerHTML = 'Loading transcript...';
        
        fetch(`/media/${item.platform}/${item.filename}.md`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Transcript not found');
                }
                return response.text();
            })
            .then(markdown => {
                transcriptContent.innerHTML = markdown;
            })
            .catch(error => {
                console.error('Error loading transcript:', error);
                transcriptContent.innerHTML = 'Error loading transcript';
            });
    }
    
    // Load metadata
    function loadMetadata(item) {
        const metadataContent = document.querySelector('.metadata-content');
        metadataContent.innerHTML = 'Loading metadata...';
        
        fetch(`/media/${item.platform}/${item.filename}.json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Metadata not found');
                }
                return response.json();
            })
            .then(metadata => {
                metadataContent.innerHTML = '';
                
                // Create a table for metadata
                const table = document.createElement('table');
                table.className = 'metadata-table';
                
                // Add rows for each metadata property
                for (const [key, value] of Object.entries(metadata)) {
                    if (typeof value === 'object') continue; // Skip nested objects
                    
                    const row = document.createElement('tr');
                    
                    const keyCell = document.createElement('td');
                    keyCell.className = 'metadata-key';
                    keyCell.textContent = formatKey(key);
                    
                    const valueCell = document.createElement('td');
                    valueCell.className = 'metadata-value';
                    valueCell.textContent = value;
                    
                    row.appendChild(keyCell);
                    row.appendChild(valueCell);
                    table.appendChild(row);
                }
                
                metadataContent.appendChild(table);
            })
            .catch(error => {
                console.error('Error loading metadata:', error);
                metadataContent.innerHTML = 'Error loading metadata';
            });
    }
    
    // Utility functions
    function showLoading(show) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
    
    function showNoResults(show) {
        noResultsElement.style.display = show ? 'block' : 'none';
    }
    
    function formatDate(dateStr) {
        if (!dateStr) return '';
        
        try {
            // Try to parse the date from the format in the filename
            if (dateStr.includes('-')) {
                // Already in YYYY-MM-DD format, possibly from our backend formatting
                const parts = dateStr.split('-');
                if (parts.length === 3) {
                    return `${parts[0]}-${parts[1]}-${parts[2]}`;
                }
            }
            
            // Try to parse as a date object
            const date = new Date(dateStr);
            
            // Check if the date is valid
            if (isNaN(date.getTime())) {
                // If standard parsing fails, try to parse numeric-only format like YYMMDD
                if (/^\d{6}$/.test(dateStr)) {
                    const year = 2000 + parseInt(dateStr.substring(0, 2));
                    const month = parseInt(dateStr.substring(2, 4));
                    const day = parseInt(dateStr.substring(4, 6));
                    
                    // Format as YYYY-MM-DD
                    return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
                }
                
                // If numeric parsing fails too, return the original
                return dateStr;
            }
            
            // Format as YYYY-MM-DD
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            return `${year}-${month}-${day}`;
        } catch (e) {
            // If all else fails, return original string
            return dateStr;
        }
    }
    
    function capitalizeFirstLetter(string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    function formatUsername(username) {
        if (!username) return '';
        // Remove any underscores and capitalize each word
        return username.replace(/_/g, ' ')
            .split(' ')
            .map(word => capitalizeFirstLetter(word))
            .join(' ');
    }
    
    function toTitleCase(str) {
        if (!str) return '';
        return str
            .split(' ')
            .map(word => {
                // Don't capitalize certain small words unless it's the first word
                const smallWords = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 'is', 'it', 'of', 'on', 'or', 'the', 'to', 'vs', 'via'];
                if (smallWords.includes(word.toLowerCase())) {
                    return word.toLowerCase();
                }
                return capitalizeFirstLetter(word);
            })
            .join(' ');
    }
    
    function formatKey(key) {
        // Convert camelCase to Title Case
        return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase());
    }
    
    // Video card creation function
    function createVideoCard(video) {
        const card = document.createElement('div');
        card.className = 'video-card content-card'; // Add content-card for base styles and hover effect
        card.dataset.videoId = video.basename; // Use filename or a unique ID if available
        card.dataset.platform = video.platform;
        card.dataset.filename = video.filename; // Store filename for player

        // Make the entire card clickable
        card.addEventListener('click', () => {
            // Pass the full video object to showVideoPlayer
            showVideoPlayer(video);
        });
        card.style.cursor = 'pointer'; // Indicate it's clickable

        const container = document.createElement('div');
        container.className = 'video-container content-thumbnail'; // Reuse thumbnail styles

        // Thumbnail handling
        if (video.has_thumbnail) { // Check if thumbnail exists
            const img = document.createElement('img');
            img.className = 'thumbnail-img'; // Reuse thumbnail image styles
            // Construct thumbnail path properly (assuming it's base filename + .jpg)
            img.src = `/media/${video.platform}/${video.filename}.jpg`;
            img.alt = video.title || 'Video thumbnail';
            img.style.objectFit = 'cover'; // Use full space
            img.onerror = () => { img.style.display = 'none'; }; // Hide if thumbnail fails to load
            container.appendChild(img);
        }

        // Type Badge (reusing from original card)
        const typeBadge = document.createElement('div');
        typeBadge.className = 'content-type-badge';
        typeBadge.textContent = video.platform;
        container.appendChild(typeBadge);

        // Add video player (hidden initially) - Optional, not needed for this card display
        /*
        const videoElement = document.createElement('video');
        videoElement.src = getVideoPath(video.filename);
        videoElement.controls = true;
        videoElement.style.display = 'none';
        container.appendChild(videoElement);
        */

        card.appendChild(container);

        // Video info section (reusing from original card)
        const info = document.createElement('div');
        info.className = 'video-info content-info'; // Reuse info styles

        const date = document.createElement('div');
        date.className = 'content-date';
        date.textContent = formatDate(video.date);
        info.appendChild(date);

        const title = document.createElement('div');
        title.className = 'content-title';
        title.textContent = toTitleCase(extractCleanTitle(video)); // Use toTitleCase for consistency
        info.appendChild(title);

        const metadata = document.createElement('div');
        metadata.className = 'content-metadata';

        const username = document.createElement('div');
        username.className = 'content-username';
        username.textContent = formatUsername(video.username || 'Unknown'); // Use formatUsername

        const platformSpan = document.createElement('span'); // Changed to span for inline display
        platformSpan.className = 'content-platform';
        platformSpan.textContent = capitalizeFirstLetter(video.platform);

        metadata.appendChild(username);
        metadata.appendChild(platformSpan);
        info.appendChild(metadata);

        // No explicit button needed as the whole card is clickable
        /*
        const viewBtn = document.createElement('button');
        viewBtn.className = 'transcript-btn';
        viewBtn.textContent = 'View Media';
        viewBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card click when button is clicked
            showVideoPlayer(video.filename, extractCleanTitle(video));
        });
        info.appendChild(viewBtn);
        */

        card.appendChild(info);

        return card;
    }
    
    // NEW Helper function to load transcript into the modal
    function loadTranscriptModal(item, container) {
        container.innerHTML = 'Loading transcript...'; // Indicate loading
        
        fetch(`/media/${item.platform}/${item.filename}.md`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Transcript not found or failed to load');
                }
                return response.text();
            })
            .then(markdown => {
                // Convert basic markdown links to HTML links if needed
                // Simple example: replace [text](url) with <a href="url" target="_blank">text</a>
                // let htmlContent = markdown.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
                
                // Use pre-wrap to preserve formatting
                container.innerHTML = ''; // Clear loading message
                const pre = document.createElement('pre');
                pre.textContent = markdown; // Display raw markdown text with preserved whitespace
                container.appendChild(pre);
                container.style.maxHeight = '40vh'; // Limit height
                container.style.overflowY = 'auto'; // Allow scrolling
                container.style.whiteSpace = 'pre-wrap'; // Ensure wrapping
                container.style.backgroundColor = '#2a2a2a'; // Darker background for readability
                container.style.padding = '1rem';
                container.style.borderRadius = '4px';
                container.style.marginTop = '1rem';
            })
            .catch(error => {
                console.error('Error loading transcript:', error);
                container.innerHTML = 'Error loading transcript.';
                container.style.color = '#ff6b6b'; // Indicate error
            });
    }
    
    // Initialize the layout on first load
    optimizeGridLayout();
}); 