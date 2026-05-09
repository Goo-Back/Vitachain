"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Filter,
  Eye,
  Check,
  X
} from "lucide-react";

interface StatusFilterProps {
  currentFilter: 'all' | 'read' | 'unread';
  onFilterChange: (filter: 'all' | 'read' | 'unread') => void;
  unreadCount?: number;
  readCount?: number;
  totalCount?: number;
  className?: string;
}

export default function StatusFilter({ 
  currentFilter, 
  onFilterChange, 
  unreadCount = 0,
  readCount = 0,
  totalCount = 0,
  className = "" 
}: StatusFilterProps) {
  const filters = [
    {
      key: 'all' as const,
      label: 'All Alerts',
      icon: Filter,
      count: totalCount,
      variant: (currentFilter === 'all' ? 'default' : 'outline') as 'default' | 'outline'
    },
    {
      key: 'unread' as const,
      label: 'Unread',
      icon: Eye,
      count: unreadCount,
      variant: (currentFilter === 'unread' ? 'default' : 'outline') as 'default' | 'outline',
      highlight: unreadCount > 0
    },
    {
      key: 'read' as const,
      label: 'Read',
      icon: Check,
      count: readCount,
      variant: (currentFilter === 'read' ? 'default' : 'outline') as 'default' | 'outline'
    }
  ];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
        {filters.map((filter) => {
          const Icon = filter.icon;
          return (
            <Button
              key={filter.key}
              variant={filter.variant}
              size="sm"
              onClick={() => onFilterChange(filter.key)}
              className={`relative h-8 px-3 text-xs font-medium transition-all ${
                filter.highlight && filter.key === 'unread' 
                  ? 'bg-orange-500 hover:bg-orange-600 text-white border-orange-500' 
                  : ''
              }`}
            >
              <Icon className="h-3 w-3 mr-1" />
              {filter.label}
              {filter.count > 0 && (
                <Badge 
                  variant="secondary" 
                  className={`ml-1 h-4 px-1 text-xs ${
                    filter.highlight && filter.key === 'unread'
                      ? 'bg-white text-orange-500'
                      : ''
                  }`}
                >
                  {filter.count}
                </Badge>
              )}
              {filter.highlight && filter.key === 'unread' && (
                <div className="absolute -top-1 -right-1 h-2 w-2 bg-orange-500 rounded-full animate-pulse" />
              )}
            </Button>
          );
        })}
      </div>
      
      {/* Clear filter indicator */}
      {currentFilter !== 'all' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onFilterChange('all')}
          className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
        >
          <X className="h-3 w-3 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
