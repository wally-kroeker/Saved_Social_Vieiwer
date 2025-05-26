import React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bookmark, BookmarkCheck, FileText } from "lucide-react";

export type ContentStatus = "new" | "viewed" | "processing" | "completed";

export interface ContentItem {
  id: string;
  platform: string;
  filename: string;
  username: string;
  date: string;
  title: string;
  hasTranscript: boolean;
  hasThumbnail: boolean;
  hasMetadata: boolean;
  thumbnailUrl?: string | null;
  media_path?: string | null;
  transcript_path?: string | null;
  metadata?: { [key: string]: any } | null;
  status: ContentStatus;
  favorite: boolean;
  notes?: string;
  rating?: number;
}

interface ContentCardProps {
  item: ContentItem;
  onClick: (item: ContentItem) => void;
  onToggleFavorite: (itemId: string) => void;
}

const statusColors: Record<ContentStatus, string> = {
  new: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100",
  viewed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
  processing: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
  completed: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100",
};

const ContentCard: React.FC<ContentCardProps> = ({ item, onClick, onToggleFavorite }) => {
  const platformColors: Record<string, string> = {
    youtube: "bg-red-500",
    instagram: "bg-purple-500",
    tiktok: "bg-black",
    twitter: "bg-blue-400",
    default: "bg-gray-500",
  };

  const platformColor = platformColors[item.platform.toLowerCase()] || platformColors.default;
  
  const formattedDate = new Date(item.date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const defaultThumbnail = `/placeholder.svg`;
  
  const imageUrl = item.thumbnailUrl ? `/media/${item.thumbnailUrl}` : defaultThumbnail;

  return (
    <Card 
      className="h-full overflow-hidden hover:shadow-md transition-shadow duration-300 cursor-pointer border-border dark:border-gray-700"
      onClick={() => {
         console.log("Card Clicked in ContentCard:", item.id);
         onClick(item)
      }}
    >
      <div className="relative aspect-video overflow-hidden bg-muted">
        <img
          src={imageUrl}
          alt={item.title}
          className="object-cover w-full h-full transition-transform duration-300 hover:scale-105"
          loading="lazy"
          onError={(e) => {
            console.warn(`Failed to load image: ${imageUrl}`);
            (e.target as HTMLImageElement).src = defaultThumbnail;
          }}
        />
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-1 left-1 h-8 w-8 text-white hover:bg-black/30"
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(item.id);
          }}
        >
          {item.favorite ? (
            <BookmarkCheck className="h-5 w-5" fill="currentColor" />
          ) : (
            <Bookmark className="h-5 w-5" />
          )}
        </Button>
        <Badge className={`absolute top-2 right-2 ${platformColor}`}>
          {item.platform}
        </Badge>
      </div>
      <CardContent className="p-4">
        <h3 className="font-semibold text-sm line-clamp-2 mb-1" title={item.title}>
          {item.title || "Untitled Content"}
        </h3>
        <p className="text-xs text-muted-foreground">
          {item.username || "Unknown User"}
        </p>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center">
        <span className="text-xs text-muted-foreground">{formattedDate}</span>
        <div className="flex gap-1 flex-wrap justify-end">
          <Badge variant="outline" className={`text-xs ${statusColors[item.status]}`}>
            {item.status}
          </Badge>
          {!!item.notes && (
            <Badge variant="secondary" className="text-xs">
              <FileText className="h-3 w-3 mr-1" />
              Notes
            </Badge>
          )}
          {item.hasTranscript && (
            <Badge variant="outline" className="text-xs">
              Transcript
            </Badge>
          )}
          {item.hasMetadata && (
            <Badge variant="outline" className="text-xs">
              Metadata
            </Badge>
          )}
        </div>
      </CardFooter>
    </Card>
  );
};

export default ContentCard;
