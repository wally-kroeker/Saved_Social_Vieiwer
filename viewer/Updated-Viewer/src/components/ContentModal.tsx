import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ContentItem } from "./ContentCard";

interface ContentModalProps {
  item: ContentItem | null;
  isOpen: boolean;
  onClose: () => void;
}

const ContentModal: React.FC<ContentModalProps> = ({ item, isOpen, onClose }) => {
  const [metadataContent, setMetadataContent] = useState<string | null>(null);
  const [transcriptContent, setTranscriptContent] = useState<string | null>(null);
  const [isLoadingMetadata, setIsLoadingMetadata] = useState(false);
  const [isLoadingTranscript, setIsLoadingTranscript] = useState(false);
  const [metadataError, setMetadataError] = useState<string | null>(null);
  const [transcriptError, setTranscriptError] = useState<string | null>(null);
  
  useEffect(() => {
    // Reset state when item changes or modal closes
    setMetadataContent(null);
    setTranscriptContent(null);
    setIsLoadingMetadata(false);
    setIsLoadingTranscript(false);
    setMetadataError(null);
    setTranscriptError(null);

    if (item && isOpen) {
      // Fetch metadata if available
      if (item.hasMetadata) {
        setIsLoadingMetadata(true);
        setMetadataError(null);
        fetch(`/media/${item.platform}/${item.filename}.json`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json(); // Assuming metadata is JSON
          })
          .then(data => {
            setMetadataContent(JSON.stringify(data, null, 2)); // Pretty print JSON
          })
          .catch(error => {
            console.error("Error fetching metadata:", error);
            setMetadataError("Failed to load metadata.");
          })
          .finally(() => setIsLoadingMetadata(false));
      }

      // Fetch transcript if available
      if (item.hasTranscript) {
        setIsLoadingTranscript(true);
        setTranscriptError(null);
        fetch(`/media/${item.platform}/${item.filename}.md`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.text(); // Transcript is likely plain text or markdown
          })
          .then(data => {
            setTranscriptContent(data);
          })
          .catch(error => {
            console.error("Error fetching transcript:", error);
            setTranscriptError("Failed to load transcript.");
          })
          .finally(() => setIsLoadingTranscript(false));
      }
    }
  }, [item, isOpen]); // Rerun effect when item or isOpen changes

  if (!item) return null;

  const formattedDate = new Date(item.date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {item.title || "Untitled Content"}
            <Badge className="ml-2">{item.platform}</Badge>
          </DialogTitle>
          <DialogDescription>
            {item.username} • {formattedDate}
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4">
          <Tabs defaultValue="media">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="media">Media</TabsTrigger>
              {item.hasMetadata && (
                <TabsTrigger value="metadata">Metadata</TabsTrigger>
              )}
              {item.hasTranscript && (
                <TabsTrigger value="transcript">Transcript</TabsTrigger>
              )}
            </TabsList>
            <TabsContent value="media" className="mt-4">
              <div className="aspect-video overflow-hidden bg-black rounded-md">
                <video
                  controls
                  className="w-full h-full"
                  poster={item.hasThumbnail ? item.thumbnailUrl : undefined}
                >
                  <source
                    src={`/media/${item.platform}/${item.filename}.mp4`}
                    type="video/mp4"
                  />
                  Your browser does not support the video tag.
                </video>
              </div>
            </TabsContent>
            {item.hasMetadata && (
              <TabsContent value="metadata" className="mt-4">
                <div className="bg-muted p-4 rounded-md overflow-auto max-h-96">
                  <pre className="text-sm">
                    {isLoadingMetadata && <code>Loading metadata...</code>}
                    {metadataError && <code className="text-destructive">{metadataError}</code>}
                    {metadataContent && <code>{metadataContent}</code>}
                    {!isLoadingMetadata && !metadataError && !metadataContent && <code>Metadata not available or empty.</code>}
                  </pre>
                </div>
              </TabsContent>
            )}
            {item.hasTranscript && (
              <TabsContent value="transcript" className="mt-4">
                <div className="bg-muted p-4 rounded-md overflow-auto max-h-96">
                  <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {isLoadingTranscript && <p>Loading transcript...</p>}
                    {transcriptError && <p className="text-destructive">{transcriptError}</p>}
                    {transcriptContent && <p>{transcriptContent}</p>}
                    {!isLoadingTranscript && !transcriptError && !transcriptContent && <p>Transcript not available or empty.</p>}
                  </div>
                </div>
              </TabsContent>
            )}
          </Tabs>
        </div>

        <DialogFooter className="flex justify-between items-center gap-2">
          <div className="text-xs text-muted-foreground">
            File: {item.filename}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ContentModal;
