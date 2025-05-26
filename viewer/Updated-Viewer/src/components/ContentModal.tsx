import React, { useState, useEffect, useRef } from 'react';
import { XMarkIcon } from '@heroicons/react/24/solid';
import { ContentItem } from '@/components/ContentCard';

interface ContentModalProps {
  item: ContentItem | null;
  onClose: () => void;
  userData: { [key: string]: { notes?: string; rating?: number } };
  onUpdateUserData: (itemId: string, field: 'notes' | 'rating', value: string | number) => void;
}

type ViewMode = 'content' | 'transcript';

const ContentModal: React.FC<ContentModalProps> = ({ item, onClose, userData, onUpdateUserData }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('content');
  const [notes, setNotes] = useState('');
  const [rating, setRating] = useState(0);
  const [transcriptContent, setTranscriptContent] = useState<string | null>(null);
  const [isLoadingTranscript, setIsLoadingTranscript] = useState(false);
  const [transcriptError, setTranscriptError] = useState<string | null>(null);

  // Log the received item prop
  console.log("ContentModal - Received item prop:", item);

  const modalRef = useRef<HTMLDivElement>(null);

  // Reset view and load user data when item changes
  useEffect(() => {
    if (item) {
      // Use the correct key format: "platform/filename"
      const userDataKey = `${item.platform}/${item.filename}`;
      const currentData = userData[userDataKey] || {};
      console.log(`ContentModal - Loading user data for key: ${userDataKey}`, currentData);
      setNotes(currentData.notes || '');
      setRating(currentData.rating || 0);
      setViewMode('content'); // Start with content view
      setTranscriptContent(null); // Clear previous transcript
      setIsLoadingTranscript(false);
      setTranscriptError(null);
    } else {
      // Reset state when modal closes
      setNotes('');
      setRating(0);
      setViewMode('content');
      setTranscriptContent(null);
      setIsLoadingTranscript(false);
      setTranscriptError(null);
    }
  }, [item, userData]);

  // Fetch transcript when viewMode changes to 'transcript'
  useEffect(() => {
    if (viewMode === 'transcript' && item?.transcript_path && !transcriptContent && !isLoadingTranscript && !transcriptError) {
      setIsLoadingTranscript(true);
      fetch(`/media/${item.transcript_path}`)
        .then(async response => {
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to fetch transcript: ${response.status} ${errorText || response.statusText}`);
          }
          return response.text();
        })
        .then(data => {
          setTranscriptContent(data || "Transcript is empty.");
          setTranscriptError(null);
        })
        .catch(error => {
          console.error("Error fetching transcript:", error);
          setTranscriptError(error.message || "An unknown error occurred while loading the transcript.");
          setTranscriptContent(null);
        })
        .finally(() => {
          setIsLoadingTranscript(false);
        });
    }
  }, [viewMode, item, transcriptContent, isLoadingTranscript, transcriptError]);

  // Handle clicks outside the modal to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  const handleNotesChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotes(event.target.value);
  };

  const handleRatingChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRating(Number(event.target.value));
  };

  const handleSaveUserData = async () => {
    if (item) {
      // Save notes first
      await onUpdateUserData(item.id, 'notes', notes);
      // Small delay to avoid race condition
      await new Promise(resolve => setTimeout(resolve, 100));
      // Then save rating
      await onUpdateUserData(item.id, 'rating', rating);
    }
  };

  if (!item) {
    console.log("ContentModal - item is null, returning null");
    return null;
  }
  
  console.log("ContentModal - Rendering with item:", item);
  const isVideo = item.media_path && (item.media_path.endsWith('.mp4') || item.media_path.endsWith('.mov') || item.media_path.endsWith('.webm'));
  const isImage = item.media_path && (item.media_path.endsWith('.jpg') || item.media_path.endsWith('.jpeg') || item.media_path.endsWith('.png') || item.media_path.endsWith('.gif'));
  console.log(`ContentModal - isVideo: ${isVideo}, isImage: ${isImage}, media_path: ${item.media_path}`);

  const renderActiveButtonClass = (mode: ViewMode) => 
    viewMode === mode ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300 hover:bg-gray-500';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div 
        ref={modalRef}
        className="bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden"
      >
        {/* Modal Header */}
        <div className="flex justify-between items-center p-3 border-b border-gray-700 flex-shrink-0">
          <h2 className="text-lg font-semibold text-white truncate pr-4" title={item.title}>{item.title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Modal Body - Takes remaining space and scrolls */}
        <div className="flex-grow overflow-y-auto p-4">
          
          {/* Top Section: Media Player / User Data */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
            {/* Media Display */}
            <div className="bg-black rounded flex justify-center items-center min-h-[200px] max-h-[60vh]">
              {isVideo ? (
                <video controls src={`/media/${item.media_path}`} className="max-h-[60vh] max-w-full rounded">
                  Your browser does not support the video tag.
                </video>
              ) : isImage ? (
                <img src={`/media/${item.media_path}`} alt={item.title} className="max-h-[60vh] max-w-full object-contain rounded" />
              ) : (
                <div className="text-gray-500 h-40 flex items-center justify-center">No preview available</div>
              )}
            </div>

            {/* User Data Input Area */}
            <div className="flex flex-col space-y-3">
              <div>
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-300 mb-1">Notes</label>
                  <textarea
                      id="notes"
                      value={notes}
                      onChange={handleNotesChange}
                      placeholder="Add your notes..."
                      rows={4}
                      className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white focus:ring-blue-500 focus:border-blue-500"
                  />
              </div>
              <div>
                  <label htmlFor="rating" className="block text-sm font-medium text-gray-300 mb-1">Rating: <span className='font-bold'>{rating}</span> / 5</label>
                  <input
                      type="range"
                      id="rating"
                      min="0"
                      max="5"
                      step="1"
                      value={rating}
                      onChange={handleRatingChange}
                      className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
              </div>
              <button 
                onClick={handleSaveUserData}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm"
              >
                Save Notes & Rating
              </button>
            </div>
          </div>

          {/* Transcript Toggle Button - Only show if transcript is available */}
          {item.transcript_path && (
            <div className="flex justify-center mb-4 border-t border-gray-700 pt-4">
              <button
                onClick={() => setViewMode(viewMode === 'transcript' ? 'content' : 'transcript')}
                className={`px-4 py-2 text-sm rounded ${renderActiveButtonClass('transcript')}`}
              >
                {viewMode === 'transcript' ? 'Hide Transcript' : 'Show Transcript'}
              </button>
            </div>
          )}

          {/* Transcript Display Area */}
          {viewMode === 'transcript' && item.transcript_path && (
            <div className="bg-gray-900 p-3 rounded max-h-72 overflow-auto text-sm">
              {isLoadingTranscript ? (
                <p className="text-gray-400 animate-pulse">Loading transcript...</p>
              ) : transcriptError ? (
                <p className="text-red-400">Error: {transcriptError}</p>
              ) : transcriptContent ? (
                <pre className="whitespace-pre-wrap break-words text-gray-200 font-sans">{transcriptContent}</pre>
              ) : (
                <p className="text-gray-400">No transcript available.</p>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default ContentModal;
