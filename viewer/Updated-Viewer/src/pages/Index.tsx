import React, { useState } from "react";
import { useContentData } from "@/hooks/useContentData";
import ContentGrid from "@/components/ContentGrid";
import FilterBar, { PlatformFilter, SortOption } from "@/components/FilterBar";
import ContentModal from "@/components/ContentModal";
import Pagination from "@/components/Pagination";
import { ContentItem } from "@/components/ContentCard";
import Header from "@/components/Header";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

const Index = () => {
  // Filter and sort state
  const [searchQuery, setSearchQuery] = useState("");
  const [platform, setPlatform] = useState<PlatformFilter>("all");
  const [sortOption, setSortOption] = useState<SortOption>("date-desc");
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  
  // Modal state
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Get content data with filtering, sorting, and pagination
  const { 
    items, 
    isLoading, 
    error, 
    totalItems, 
    totalPages,
  } = useContentData({
    searchQuery,
    platform,
    sortOption,
    page: currentPage,
    itemsPerPage,
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
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
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
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh}
            className="flex items-center gap-1"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
        
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={handleSearchChange}
          selectedPlatform={platform}
          onPlatformChange={handlePlatformChange}
          sortOption={sortOption}
          onSortChange={handleSortChange}
        />
        
        <ContentGrid
          items={items}
          isLoading={isLoading}
          onItemClick={handleItemClick}
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
          isOpen={isModalOpen}
          onClose={handleCloseModal}
        />
      </main>
    </div>
  );
};

export default Index;
