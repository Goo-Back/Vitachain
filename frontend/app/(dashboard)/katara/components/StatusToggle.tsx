"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Check, 
  Eye, 
  EyeOff,
  Loader2
} from "lucide-react";

interface Alert {
  id: string;
  read_status: boolean;
  read_at?: string;
  created_at: string;
}

interface StatusToggleProps {
  alert: Alert;
  onStatusChange?: (alertId: string, readStatus: boolean) => void;
  optimisticUpdate?: boolean;
  className?: string;
}

export default function StatusToggle({ 
  alert, 
  onStatusChange, 
  optimisticUpdate = true,
  className = "" 
}: StatusToggleProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [optimisticStatus, setOptimisticStatus] = useState(alert.read_status);

  const handleStatusToggle = async (newStatus: boolean) => {
    if (isUpdating || optimisticStatus === newStatus) return;

    try {
      setIsUpdating(true);
      setError(null);

      // Optimistic update
      if (optimisticUpdate) {
        setOptimisticStatus(newStatus);
        if (onStatusChange) {
          onStatusChange(alert.id, newStatus);
        }
      }

      const response = await fetch(`/api/katara/alerts/${alert.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ read_status: newStatus }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update alert status: ${response.statusText}`);
      }

      // If not using optimistic updates, update after successful response
      if (!optimisticUpdate && onStatusChange) {
        onStatusChange(alert.id, newStatus);
      }

    } catch (err) {
      // Revert optimistic update on error
      if (optimisticUpdate) {
        setOptimisticStatus(alert.read_status);
        if (onStatusChange) {
          onStatusChange(alert.id, alert.read_status);
        }
      }
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setIsUpdating(false);
    }
  };

  const formatReadTime = (readAt?: string) => {
    if (!readAt) return null;
    
    const date = new Date(readAt);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return "Read just now";
    } else if (diffInMinutes < 60) {
      return `Read ${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    } else if (diffInMinutes < 1440) { // 24 hours
      const hours = Math.floor(diffInMinutes / 60);
      return `Read ${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      return `Read on ${date.toLocaleDateString()}`;
    }
  };

  const currentStatus = optimisticUpdate ? optimisticStatus : alert.read_status;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {currentStatus ? (
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            <Check className="h-3 w-3 mr-1" />
            Read
          </Badge>
          {alert.read_at && (
            <span className="text-xs text-muted-foreground">
              {formatReadTime(alert.read_at)}
            </span>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleStatusToggle(false)}
            disabled={isUpdating}
            className="h-6 px-2 text-xs"
          >
            {isUpdating ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <>
                <EyeOff className="h-3 w-3 mr-1" />
                Mark Unread
              </>
            )}
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs border-orange-500 text-orange-600">
            <Eye className="h-3 w-3 mr-1" />
            Unread
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleStatusToggle(true)}
            disabled={isUpdating}
            className="h-6 px-2 text-xs"
          >
            {isUpdating ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <>
                <Check className="h-3 w-3 mr-1" />
                Mark Read
              </>
            )}
          </Button>
        </div>
      )}
      
      {error && (
        <div className="text-xs text-red-600">
          Error: {error}
        </div>
      )}
    </div>
  );
}
