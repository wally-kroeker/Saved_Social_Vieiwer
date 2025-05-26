import React, { useState } from "react";
import { useContentData } from "@/hooks/useContentData";
import ContentGrid from "@/components/ContentGrid";
import FilterBar, { PlatformFilter, SortOption, StatusFilter } from "@/components/FilterBar";
import ContentModal from "@/components/ContentModal";
import Pagination from "@/components/Pagination";
import { ContentItem, ContentStatus } from "@/components/ContentCard";
import Header from "@/components/Header";
import { Button } from "@/components/ui/button";
import { RefreshCw, Bookmark } from "lucide-react";
import { toast } from "sonner";

// Define a type for the user data structure
type UserData = { [key: string]: { notes?: string; rating?: number } };

const Index = () => {
  // Filter and sort state
  const [searchQuery, setSearchQuery] = useState("");
  const [platform, setPlatform] = useState<PlatformFilter>("all");
  const [sortOption, setSortOption] = useState<SortOption>("date-desc");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  
  // Modal state
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  // No need for isModalOpen, modal controls its visibility based on selectedItem

  // Add state for user-specific data (notes, ratings)
  const [userData, setUserData] = useState<UserData>({});

  // Get content data with filtering, sorting, and pagination
  const { 
    items, 
    isLoading, 
    error, 
    totalItems, 
    totalPages,
    updateItem, // Keep using the existing updateItem from the hook for now
  } = useContentData({
    searchQuery,
    platform,
    sortOption,
    page: currentPage,
    itemsPerPage,
    favoritesOnly,
    statusFilter,
  });

  // Reset to page 1 when filters change
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setCurrentPage(1);
  };

  const handlePlatformChange = (value: PlatformFilter) => {
    setPlatform(value);
    setCurrentPage(1);
  };

  const handleSortChange = (value: SortOption) => {
    setSortOption(value);
    setCurrentPage(1);
  };

  const handleItemClick = (item: ContentItem) => {
    console.log("handleItemClick called in Index:", item.id);
    setSelectedItem(item);
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
  };

  const handleRefresh = async () => {
    // This would make an API call to refresh the content cache
    toast.promise(
      new Promise(resolve => setTimeout(resolve, 1000)), 
      {
        loading: "Refreshing content...",
        success: "Content refreshed successfully",
        error: "Failed to refresh content",
      }
    );
  };

  // Handle items per page change
  const handleItemsPerPageChange = (value: number) => {
    setItemsPerPage(value);
    setCurrentPage(1); // Reset to first page when changing items per page
  };

  const handleToggleFavoritesFilter = () => {
    setFavoritesOnly(!favoritesOnly);
    setCurrentPage(1);
  };

  const handleStatusFilterChange = (value: StatusFilter) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  // Update user data state (notes/ratings)
  const handleUpdateUserData = async (itemId: string, field: 'notes' | 'rating', value: string | number) => {
    // Update local state immediately for responsive UI
    setUserData(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));

    // Find the item to get platform and filename for API call
    const item = items.find(i => i.id === itemId) || selectedItem;
    if (!item) {
      console.error(`Item not found for ID: ${itemId}`);
      toast.error(`Failed to save ${field}: item not found`);
      return;
    }

    try {
      // Make API call to persist the data
      const response = await fetch(`/api/user_data/${item.platform}/${item.filename}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [field]: value }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      console.log(`Successfully saved ${field} for ${itemId} via API`);
      toast.success(`${field.charAt(0).toUpperCase() + field.slice(1)} saved successfully`);
    } catch (error) {
      console.error(`Failed to save ${field} for ${itemId}:`, error);
      toast.error(`Failed to save ${field}`);
      
      // Revert local state on API failure
      setUserData(prev => ({
        ...prev,
        [itemId]: {
          ...prev[itemId],
          [field]: prev[itemId]?.[field] // Revert to previous value
        }
      }));
    }
  };

  // Still use the hook's updateItem for backend changes (like favorite status)
  const handleUpdateItemBackend = (itemId: string, updates: Partial<ContentItem>) => {
    updateItem(itemId, updates);
    if (selectedItem?.id === itemId) {
      setSelectedItem(prev => prev ? { ...prev, ...updates } : null);
    }
  };

  const handleToggleFavorite = (itemId: string) => {
    const item = items.find(i => i.id === itemId) || selectedItem;
    if (item) {
      handleUpdateItemBackend(itemId, { favorite: !item.favorite });
    } else {
      console.error("Item not found for toggling favorite");
    }
  };

  // Log the state right before rendering
  console.log("Index Component - selectedItem state:", selectedItem);

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold">Social Media Content</h1>
            <p className="text-muted-foreground mt-1">
              Browse and view your saved social media content
            </p>
          </div>
          
          {/* Refresh and Favorite Buttons */}
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRefresh}
              className="flex items-center gap-1"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button
              variant={favoritesOnly ? "secondary" : "outline"}
              size="sm"
              onClick={handleToggleFavoritesFilter}
              className="flex items-center gap-1"
            >
              <Bookmark className="h-4 w-4" />
              {favoritesOnly ? "Bookmarks Only" : "Show All"}
            </Button>
          </div>
        </div>
        
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={handleSearchChange}
          selectedPlatform={platform}
          onPlatformChange={handlePlatformChange}
          sortOption={sortOption}
          onSortChange={handleSortChange}
          statusFilter={statusFilter}
          onStatusChange={handleStatusFilterChange}
        />
        
        <ContentGrid
          items={items}
          isLoading={isLoading}
          onItemClick={handleItemClick}
          onToggleFavorite={handleToggleFavorite}
        />
        
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          itemsPerPage={itemsPerPage}
          onItemsPerPageChange={handleItemsPerPageChange}
          totalItems={totalItems}
        />

        <ContentModal
          item={selectedItem}
          onClose={handleCloseModal}
          userData={userData}
          onUpdateUserData={handleUpdateUserData}
        />
      </main>
    </div>
  );
};

export default Index;
