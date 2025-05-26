import React from "react";
import ContentCard, { ContentItem } from "./ContentCard";
import { Skeleton } from "@/components/ui/skeleton";

interface ContentGridProps {
  items: ContentItem[];
  isLoading: boolean;
  onItemClick: (item: ContentItem) => void;
  onToggleFavorite: (itemId: string) => void;
}

const ContentGrid: React.FC<ContentGridProps> = ({ 
  items, 
  isLoading, 
  onItemClick, 
  onToggleFavorite 
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-6">
      {isLoading
        ? Array.from({ length: 20 }).map((_, i) => (
            <div key={`skeleton-${i}`} className="h-full">
              <div className="h-full rounded-md overflow-hidden border border-border dark:border-gray-800">
                <Skeleton className="h-40 w-full" />
                <div className="p-4">
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-3 w-2/3" />
                </div>
                <div className="px-4 pb-4">
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            </div>
          ))
        : items.map((item) => (
            <ContentCard
              key={item.id}
              item={item}
              onClick={onItemClick}
              onToggleFavorite={onToggleFavorite}
            />
          ))}
      {!isLoading && items.length === 0 && (
        <div className="col-span-full flex justify-center items-center py-20">
          <p className="text-muted-foreground text-center">
            No content found matching your filters.
          </p>
        </div>
      )}
    </div>
  );
};

export default ContentGrid;
