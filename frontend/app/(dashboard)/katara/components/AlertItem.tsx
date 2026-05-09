"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "../../../../components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  AlertTriangle, 
  Thermometer, 
  Droplets, 
  Leaf, 
  Check, 
  Clock,
  X
} from "lucide-react";

interface Alert {
  id: string;
  farmer_id: string;
  device_id?: string;
  type: string;
  severity: string;
  message: string;
  read_status: boolean;
  read_at?: string;
  created_at: string;
  metric?: string;
  value?: number;
  threshold?: number;
}

interface AlertItemProps {
  alert: Alert;
  onMarkAsRead?: (alertId: string) => void;
  className?: string;
}

export default function AlertItem({ alert, onMarkAsRead, className = "" }: AlertItemProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500 hover:bg-red-600";
      case "high":
        return "bg-orange-500 hover:bg-orange-600";
      case "medium":
        return "bg-yellow-500 hover:bg-yellow-600";
      case "low":
        return "bg-blue-500 hover:bg-blue-600";
      default:
        return "bg-gray-500 hover:bg-gray-600";
    }
  };

  const getMetricIcon = (metric?: string) => {
    switch (metric) {
      case "temperature":
        return <Thermometer className="h-4 w-4" />;
      case "humidity":
        return <Droplets className="h-4 w-4" />;
      case "ndvi":
        return <Leaf className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return "Just now";
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    } else if (diffInMinutes < 1440) { // 24 hours
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  };

  const handleMarkAsRead = async () => {
    if (alert.read_status || isUpdating) return;

    try {
      setIsUpdating(true);
      setError(null);

      const response = await fetch(`/api/katara/alerts/${alert.id}/read`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to mark alert as read: ${response.statusText}`);
      }

      if (onMarkAsRead) {
        onMarkAsRead(alert.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Card className={`${!alert.read_status ? 'border-l-4 border-l-orange-500' : ''} ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-2">
            {/* Alert Header */}
            <div className="flex items-center gap-2">
              {getMetricIcon(alert.metric)}
              <Badge className={`${getSeverityColor(alert.severity)} text-white`}>
                {alert.severity.toUpperCase()}
              </Badge>
              {alert.device_id && (
                <Badge variant="outline" className="text-xs">
                  {alert.device_id}
                </Badge>
              )}
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatTimestamp(alert.created_at)}
              </div>
            </div>

            {/* Alert Message */}
            <p className={`text-sm ${!alert.read_status ? 'font-medium' : 'text-muted-foreground'}`}>
              {alert.message}
            </p>

            {/* Alert Details */}
            {alert.metric && alert.value && alert.threshold && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>Value: {alert.value}</span>
                <span>•</span>
                <span>Threshold: {alert.threshold}</span>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="flex items-center gap-2 text-xs text-red-600">
                <X className="h-3 w-3" />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Action Button */}
          {!alert.read_status && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAsRead}
              disabled={isUpdating}
              className="ml-2"
            >
              {isUpdating ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : (
                <Check className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
