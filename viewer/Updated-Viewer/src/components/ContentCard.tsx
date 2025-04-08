
import React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card";

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
  thumbnailUrl?: string;
}

interface ContentCardProps {
  item: ContentItem;
  onClick: (item: ContentItem) => void;
}

const ContentCard: React.FC<ContentCardProps> = ({ item, onClick }) => {
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
  
  return (
    <Card 
      className="h-full overflow-hidden hover:shadow-md transition-shadow duration-300 cursor-pointer border-border dark:border-gray-700"
      onClick={() => onClick(item)}
    >
      <div className="relative aspect-video overflow-hidden bg-muted">
        <img
          src={item.hasThumbnail ? item.thumbnailUrl : defaultThumbnail}
          alt={item.title}
          className="object-cover w-full h-full transition-transform duration-300 hover:scale-105"
          loading="lazy"
        />
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
        <div className="flex gap-1">
          {item.hasTranscript && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 rounded-full">
              Transcript
            </span>
          )}
          {item.hasMetadata && (
            <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded-full">
              Metadata
            </span>
          )}
        </div>
      </CardFooter>
    </Card>
  );
};

export default ContentCard;
