import { useState, useEffect, useMemo } from "react";
import { ContentItem } from "@/components/ContentCard";
import { PlatformFilter, SortOption } from "@/components/FilterBar";
import { toast } from "sonner";

// This function fetches content from the API
const fetchContent = async (): Promise<ContentItem[]> => {
  try {
    const response = await fetch("/api/content");
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.items.map((item: any) => ({
      id: `${item.platform}-${item.filename}`,
      platform: item.platform,
      filename: item.filename,
      username: item.username || "",
      date: item.date || new Date().toISOString(),
      title: item.title || "",
      hasTranscript: item.has_transcript || false,
      hasThumbnail: item.has_thumbnail || false,
      hasMetadata: item.has_metadata || false,
      thumbnailUrl: item.has_thumbnail 
        ? `/media/${item.platform}/${item.filename}.jpg`
        : undefined,
    }));
  } catch (error) {
    console.error("Failed to fetch content:", error);
    toast.error("Failed to load content");
    return [];
  }
};

// Mock data for development
const generateMockData = (): ContentItem[] => {
  const platforms = ["youtube", "instagram", "tiktok", "twitter"];
  const usernames = ["user1", "creator2", "channel3", "social4"];
  
  return Array.from({ length: 100 }).map((_, i) => {
    const platform = platforms[Math.floor(Math.random() * platforms.length)];
    const username = usernames[Math.floor(Math.random() * usernames.length)];
    const date = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString();
    
    return {
      id: `content-${i}`,
      platform,
      filename: `${platform}-${username}-${date.substring(0, 10)}-item-${i}`,
      username,
      date,
      title: `Sample Content Item ${i + 1}`,
      hasTranscript: Math.random() > 0.5,
      hasThumbnail: Math.random() > 0.3,
      hasMetadata: Math.random() > 0.4,
      thumbnailUrl: `/placeholder.svg`,
    };
  });
};

export interface ContentDataOptions {
  searchQuery: string;
  platform: PlatformFilter;
  sortOption: SortOption;
  page: number;
  itemsPerPage: number;
}

export const useContentData = (options: ContentDataOptions) => {
  const [allItems, setAllItems] = useState<ContentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadContent = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Switch to using the fetchContent function
        const items = await fetchContent();
        // const items = generateMockData(); // Comment out mock data
        setAllItems(items);
      } catch (err) {
        setError("Failed to load content");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadContent();
  }, []);

  const filteredAndSortedItems = useMemo(() => {
    if (!allItems.length) return [];
    
    // Filter by search query
    let filtered = allItems.filter(item => {
      if (options.searchQuery) {
        const query = options.searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(query);
        const matchesUsername = item.username.toLowerCase().includes(query);
        return matchesTitle || matchesUsername;
      }
      return true;
    });
    
    // Filter by platform
    if (options.platform !== "all") {
      filtered = filtered.filter(item => 
        item.platform.toLowerCase() === options.platform
      );
    }
    
    // Sort items
    return filtered.sort((a, b) => {
      switch (options.sortOption) {
        case "date-desc":
          return new Date(b.date).getTime() - new Date(a.date).getTime();
        case "date-asc":
          return new Date(a.date).getTime() - new Date(b.date).getTime();
        case "title-asc":
          return a.title.localeCompare(b.title);
        case "title-desc":
          return b.title.localeCompare(a.title);
        case "username-asc":
          return a.username.localeCompare(b.username);
        case "username-desc":
          return b.username.localeCompare(a.username);
        default:
          return 0;
      }
    });
  }, [allItems, options.searchQuery, options.platform, options.sortOption]);

  // Calculate pagination
  const totalFilteredItems = filteredAndSortedItems.length;
  const totalPages = Math.max(1, Math.ceil(totalFilteredItems / options.itemsPerPage));
  
  // Ensure current page is valid
  const validPage = Math.min(Math.max(1, options.page), totalPages);
  
  // Get current page of items
  const paginatedItems = useMemo(() => {
    const startIndex = (validPage - 1) * options.itemsPerPage;
    const endIndex = startIndex + options.itemsPerPage;
    return filteredAndSortedItems.slice(startIndex, endIndex);
  }, [filteredAndSortedItems, validPage, options.itemsPerPage]);

  return {
    items: paginatedItems,
    isLoading,
    error,
    totalItems: totalFilteredItems,
    totalPages,
    currentPage: validPage,
  };
};
