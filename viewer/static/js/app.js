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
            const card = createContentCard(item);
            contentGrid.appendChild(card);
        });
    }
    
    // Create content card
    function createContentCard(item) {
        const template = contentItemTemplate.content.cloneNode(true);
        const card = template.querySelector('.content-card');
        
        // Set card data attributes
        card.dataset.platform = item.platform;
        card.dataset.filename = item.filename;
        
        // Set title with proper capitalization
        const title = template.querySelector('.content-title');
        title.textContent = toTitleCase(item.title);
        title.title = toTitleCase(item.title); // tooltip
        
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
        thumbnailImg.alt = item.title;
        
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
        
        // Set content details
        const title = template.querySelector('.content-title');
        title.textContent = toTitleCase(item.title);
        
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
    
    // Event listeners
    searchBtn.addEventListener('click', () => {
        currentSearch = searchInput.value.trim();
        loadContent();
    });
    
    searchInput.addEventListener('keyup', event => {
        if (event.key === 'Enter') {
            currentSearch = searchInput.value.trim();
            loadContent();
        }
    });
    
    platformFilter.addEventListener('change', () => {
        currentPlatform = platformFilter.value;
        loadContent();
    });
    
    closeBtn.addEventListener('click', () => {
        contentModal.style.display = 'none';
        const video = document.querySelector('.content-video');
        if (video) {
            video.pause();
        }
    });
    
    // Close modal when clicking outside content
    contentModal.addEventListener('click', event => {
        if (event.target === contentModal) {
            contentModal.style.display = 'none';
            const video = document.querySelector('.content-video');
            if (video) {
                video.pause();
            }
        }
    });
    
    // Initialize
    loadContent();
}); 