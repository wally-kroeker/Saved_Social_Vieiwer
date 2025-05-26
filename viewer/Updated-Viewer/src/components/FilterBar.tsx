import React from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ContentStatus } from "./ContentCard";

export type SortOption = "date-desc" | "date-asc" | "title-asc" | "title-desc" | "username-asc" | "username-desc";
export type PlatformFilter = "all" | "youtube" | "instagram" | "tiktok" | "twitter";
export type StatusFilter = "all" | ContentStatus;

const statusFilterOptions: { value: StatusFilter; label: string }[] = [
  { value: "all", label: "All Statuses" },
  { value: "new", label: "New" },
  { value: "viewed", label: "Viewed" },
  { value: "processing", label: "Processing" },
  { value: "completed", label: "Completed" },
];

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  selectedPlatform: PlatformFilter;
  onPlatformChange: (value: PlatformFilter) => void;
  sortOption: SortOption;
  onSortChange: (value: SortOption) => void;
  statusFilter: StatusFilter;
  onStatusChange: (value: StatusFilter) => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  searchQuery,
  onSearchChange,
  selectedPlatform,
  onPlatformChange,
  sortOption,
  onSortChange,
  statusFilter,
  onStatusChange,
}) => {
  return (
    <div className="flex flex-col md:flex-row gap-3">
      <div className="relative flex-grow">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by title, username..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-8"
        />
      </div>
      
      <div className="flex gap-3">
        <Select
          value={selectedPlatform}
          onValueChange={(value) => onPlatformChange(value as PlatformFilter)}
        >
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Platform" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Platforms</SelectItem>
            <SelectItem value="youtube">YouTube</SelectItem>
            <SelectItem value="instagram">Instagram</SelectItem>
            <SelectItem value="tiktok">TikTok</SelectItem>
            <SelectItem value="twitter">Twitter</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={statusFilter}
          onValueChange={(value) => onStatusChange(value as StatusFilter)}
        >
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {statusFilterOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={sortOption}
          onValueChange={(value) => onSortChange(value as SortOption)}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="date-desc">Newest First</SelectItem>
            <SelectItem value="date-asc">Oldest First</SelectItem>
            <SelectItem value="title-asc">Title (A-Z)</SelectItem>
            <SelectItem value="title-desc">Title (Z-A)</SelectItem>
            <SelectItem value="username-asc">Username (A-Z)</SelectItem>
            <SelectItem value="username-desc">Username (Z-A)</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

export default FilterBar;
