"use client";

import { Badge } from "@/components/ui/badge";
import { Bell } from "lucide-react";

interface UnreadBadgeProps {
  unreadCount: number;
  className?: string;
  showIcon?: boolean;
  animate?: boolean;
}

export default function UnreadBadge({ 
  unreadCount, 
  className = "", 
  showIcon = true,
  animate = true 
}: UnreadBadgeProps) {
  if (unreadCount === 0) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      {showIcon && (
        <Bell className={`h-4 w-4 ${animate ? 'animate-pulse' : ''}`} />
      )}
      <Badge 
        variant="destructive" 
        className={`absolute -top-2 -right-2 h-5 px-1 text-xs font-bold flex items-center justify-center min-w-[20px] ${
          animate ? 'animate-bounce' : ''
        }`}
      >
        {unreadCount > 99 ? '99+' : unreadCount}
      </Badge>
    </div>
  );
}
