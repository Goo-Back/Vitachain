"use client";

import { useState, useEffect } from "react";
import { Badge } from "../../../../components/ui/badge";
import { Bell, BellRing } from "lucide-react";

interface AlertBadgeProps {
  className?: string;
  showCount?: boolean;
}

export default function AlertBadge({ className = "", showCount = true }: AlertBadgeProps) {
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUnreadCount();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchUnreadCount, 30000); // Poll every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      setError(null);
      
      const response = await fetch('/api/katara/alerts?limit=1&is_read=false');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch alert count: ${response.statusText}`);
      }

      const data = await response.json();
      setUnreadCount(data.unread_count || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
      // Don't show error to user for badge, just log it
      console.error("AlertBadge error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`relative ${className}`}>
        <Bell className="h-5 w-5 text-muted-foreground animate-pulse" />
      </div>
    );
  }

  if (error || unreadCount === 0) {
    return (
      <div className={`relative ${className}`}>
        <Bell className="h-5 w-5 text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <BellRing className="h-5 w-5 text-orange-500" />
      {showCount && unreadCount > 0 && (
        <Badge 
          variant="destructive" 
          className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
        >
          {unreadCount > 99 ? "99+" : unreadCount}
        </Badge>
      )}
    </div>
  );
}
