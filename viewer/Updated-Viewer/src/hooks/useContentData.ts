import { useState, useEffect, useMemo, useCallback } from "react";
import { ContentItem } from "@/components/ContentCard";
import { PlatformFilter, SortOption, StatusFilter } from "@/components/FilterBar";
import { toast } from "sonner";

// Define type for user data associated with an item
interface UserItemData {
  status: "new" | "viewed" | "processing" | "completed";
  favorite: boolean;
  notes?: string;
  rating?: number;
}

// Define type for the whole user data blob from the API
type UserDataBlob = Record<string, UserItemData>;

// This function fetches content from the API
const fetchContent = async (): Promise<Omit<ContentItem, keyof UserItemData>[]> => {
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
      media_path: item.media_path,
      transcript_path: item.transcript_path,
      thumbnailUrl: item.thumbnailUrl || (item.has_thumbnail 
        ? `/media/${item.platform}/${item.filename}.jpg`
        : undefined),
    }));
  } catch (error) {
    console.error("Failed to fetch content:", error);
    toast.error("Failed to load content");
    return [];
  }
};

const fetchUserData = async (): Promise<UserDataBlob> => {
  try {
    const response = await fetch("/api/user_data");
    if (!response.ok) throw new Error(`Error fetching user data: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch user data:", error);
    toast.error("Failed to load user data (status, favorites, notes)");
    return {};
  }
};

// Mock data for development
const generateMockData = (): ContentItem[] => {
  const platforms = ["youtube", "instagram", "tiktok", "twitter"];
  const usernames = ["user1", "creator2", "channel3", "social4"];
  const statuses = ["new", "viewed", "processing", "completed"] as const;
  
  return Array.from({ length: 100 }).map((_, i) => {
    const platform = platforms[Math.floor(Math.random() * platforms.length)];
    const username = usernames[Math.floor(Math.random() * usernames.length)];
    const date = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString();
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const favorite = Math.random() > 0.8;
    const notes = favorite ? `This is a note for mock item ${i + 1}` : undefined;

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
      status,
      favorite,
      notes,
    };
  });
};

export interface ContentDataOptions {
  searchQuery: string;
  platform: PlatformFilter;
  sortOption: SortOption;
  page: number;
  itemsPerPage: number;
  favoritesOnly: boolean;
  statusFilter: StatusFilter;
}

const DEFAULT_USER_ITEM_DATA: UserItemData = {
  status: "new",
  favorite: false,
  notes: "",
  rating: 0,
};

export const useContentData = (options: ContentDataOptions) => {
  const [baseContentItems, setBaseContentItems] = useState<Omit<ContentItem, keyof UserItemData>[]>([]);
  const [userData, setUserData] = useState<UserDataBlob>({});
  const [allItems, setAllItems] = useState<ContentItem[]>([]);
  const [isLoadingContent, setIsLoadingContent] = useState(true);
  const [isLoadingUserData, setIsLoadingUserData] = useState(true);
  const [contentError, setContentError] = useState<string | null>(null);
  const [userDataError, setUserDataError] = useState<string | null>(null);

  const isLoading = isLoadingContent || isLoadingUserData;
  const error = contentError || userDataError;

  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoadingContent(true);
      setIsLoadingUserData(true);
      setContentError(null);
      setUserDataError(null);

      try {
        const [contentResult, userDataResult] = await Promise.all([
          fetchContent(),
          fetchUserData(),
        ]);
        setBaseContentItems(contentResult);
        setUserData(userDataResult);
      } catch (err) {
        console.error("Error during initial data load:", err);
      } finally {
        setIsLoadingContent(false);
        setIsLoadingUserData(false);
      }
    };
    loadInitialData();
  }, []);

  useEffect(() => {
    if (baseContentItems.length > 0) {
      const mergedItems = baseContentItems.map(baseItem => {
        const itemKey = `${baseItem.platform}/${baseItem.filename}`;
        const userItemData = userData[itemKey] || DEFAULT_USER_ITEM_DATA;
        return { ...baseItem, ...userItemData };
      });
      setAllItems(mergedItems);
    }
  }, [baseContentItems, userData]);

  const updateItem = useCallback(async (itemId: string, updates: Partial<UserItemData>) => {
    const itemIndex = allItems.findIndex(item => item.id === itemId);
    if (itemIndex === -1) return;

    const originalItem = allItems[itemIndex];
    const updatedItem = { ...originalItem, ...updates };

    setAllItems(prevItems => [
      ...prevItems.slice(0, itemIndex),
      updatedItem,
      ...prevItems.slice(itemIndex + 1),
    ]);

    const itemKey = `${originalItem.platform}/${originalItem.filename}`;
    setUserData(prevData => ({
      ...prevData,
      [itemKey]: { ...(prevData[itemKey] || DEFAULT_USER_ITEM_DATA), ...updates },
    }));

    const apiUpdates: Record<string, any> = {};
    if ('status' in updates) apiUpdates.status = updates.status;
    if ('favorite' in updates) apiUpdates.favorite = updates.favorite;
    if ('notes' in updates) apiUpdates.notes = updates.notes;
    if ('rating' in updates) apiUpdates.rating = updates.rating;

    if (Object.keys(apiUpdates).length === 0) return;

    try {
      const response = await fetch(`/api/user_data/${originalItem.platform}/${originalItem.filename}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiUpdates),
      });
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      console.log(`Successfully updated item ${itemId} via API`);
      if ('notes' in apiUpdates) toast.success("Notes saved");

    } catch (error) {
      console.error(`Failed to update item ${itemId} via API:`, error);
      toast.error(`Failed to save changes for ${originalItem.title}`);
      setAllItems(prevItems => [
        ...prevItems.slice(0, itemIndex),
        originalItem,
        ...prevItems.slice(itemIndex + 1),
      ]);
      setUserData(prevData => ({
        ...prevData,
        [itemKey]: prevData[itemKey] || DEFAULT_USER_ITEM_DATA,
      }));
    }
  }, [allItems]);

  const filteredAndSortedItems = useMemo(() => {
    if (!allItems.length) return [];
    
    let filtered = allItems;
    
    if (options.searchQuery) {
      const query = options.searchQuery.toLowerCase();
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(query) || 
        item.username.toLowerCase().includes(query)
      );
    }
    
    if (options.platform !== "all") {
      filtered = filtered.filter(item => 
        item.platform.toLowerCase() === options.platform
      );
    }
    
    if (options.favoritesOnly) {
      filtered = filtered.filter(item => item.favorite);
    }
    
    if (options.statusFilter !== "all") {
      filtered = filtered.filter(item => item.status === options.statusFilter);
    }
    
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
  }, [allItems, options.searchQuery, options.platform, options.sortOption, options.favoritesOnly, options.statusFilter]);

  const totalFilteredItems = filteredAndSortedItems.length;
  const totalPages = Math.max(1, Math.ceil(totalFilteredItems / options.itemsPerPage));
  const validPage = Math.min(Math.max(1, options.page), totalPages);
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
    updateItem,
  };
};
