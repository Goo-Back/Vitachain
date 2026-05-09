"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "../../../../components/ui/badge";
import { 
  Loader2, 
  RefreshCw, 
  Filter, 
  Bell, 
  BellRing,
  AlertTriangle,
  CheckCircle
} from "lucide-react";
import AlertItem from "./AlertItem";
import StatusFilter from "./StatusFilter";
import BulkActions from "./BulkActions";

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

interface AlertFeedProps {
  className?: string;
  maxItems?: number;
  showFilters?: boolean;
}

export default function AlertFeed({ className = "", maxItems = 20, showFilters = true }: AlertFeedProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);

  // Filter states
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [readStatusFilter, setReadStatusFilter] = useState<string>("all");
  const [deviceFilter, setDeviceFilter] = useState<string>("all");

  const fetchAlerts = useCallback(async (reset = false) => {
    try {
      setLoading(true);
      setError(null);

      const currentOffset = reset ? 0 : offset;
      const params = new URLSearchParams({
        limit: maxItems.toString(),
        offset: currentOffset.toString(),
      });

      // Add filters
      if (severityFilter !== "all") {
        params.append('severity', severityFilter);
      }
      if (readStatusFilter !== "all") {
        params.append('read_status', readStatusFilter === "read" ? "true" : "false");
      }
      if (deviceFilter !== "all") {
        params.append('device_id', deviceFilter);
      }

      const response = await fetch(`/api/katara/alerts?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (reset) {
        setAlerts(data.alerts);
        setOffset(0);
      } else {
        setAlerts(prev => [...prev, ...data.alerts]);
      }
      
      setHasMore(data.pagination.has_more);
      setUnreadCount(data.unread_count);
      setTotalCount(data.total || data.alerts.length);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }, [maxItems, offset, severityFilter, readStatusFilter, deviceFilter]);

  useEffect(() => {
    fetchAlerts(true);
  }, [severityFilter, readStatusFilter, deviceFilter]);

  const handleMarkAsRead = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, read_status: true } : alert
    ));
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const handleLoadMore = () => {
    setOffset(prev => prev + maxItems);
    fetchAlerts(false);
  };

  const handleRefresh = () => {
    fetchAlerts(true);
  };

  const handleMarkAllAsRead = async () => {
    const unreadAlerts = alerts.filter(alert => !alert.read_status);
    
    for (const alert of unreadAlerts) {
      try {
        const response = await fetch(`/api/katara/alerts/${alert.id}/read`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          handleMarkAsRead(alert.id);
        }
      } catch (err) {
        console.error(`Failed to mark alert ${alert.id} as read:`, err);
      }
    }
  };

  const getSeverityStats = () => {
    const stats = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    };

    alerts.forEach(alert => {
      if (stats.hasOwnProperty(alert.severity)) {
        stats[alert.severity as keyof typeof stats]++;
      }
    });

    return stats;
  };

  const severityStats = getSeverityStats();

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {unreadCount > 0 ? (
              <BellRing className="h-5 w-5 text-orange-500" />
            ) : (
              <Bell className="h-5 w-5 text-muted-foreground" />
            )}
            Alerts
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount} unread
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
            
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllAsRead}
                className="text-xs"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Mark All Read
              </Button>
            )}
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="flex flex-wrap gap-2 pt-2">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="w-32 h-8 rounded border border-input bg-background px-2 py-1 text-sm"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <select
              value={readStatusFilter}
              onChange={(e) => setReadStatusFilter(e.target.value)}
              className="w-32 h-8 rounded border border-input bg-background px-2 py-1 text-sm"
            >
              <option value="all">All Status</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
            </select>

            {/* Device filter would be populated from actual devices */}
            <select
              value={deviceFilter}
              onChange={(e) => setDeviceFilter(e.target.value)}
              className="w-32 h-8 rounded border border-input bg-background px-2 py-1 text-sm"
            >
              <option value="all">All Devices</option>
              {/* Device options would be dynamically added */}
            </select>
          </div>
        )}

        {/* Severity Stats */}
        <div className="flex gap-2 pt-2">
          {Object.entries(severityStats).map(([severity, count]) => (
            count > 0 && (
              <Badge
                key={severity}
                variant="outline"
                className={`text-xs ${
                  severity === 'critical' ? 'border-red-500 text-red-500' :
                  severity === 'high' ? 'border-orange-500 text-orange-500' :
                  severity === 'medium' ? 'border-yellow-500 text-yellow-500' :
                  'border-blue-500 text-blue-500'
                }`}
              >
                {severity}: {count}
              </Badge>
            )
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        )}

        {loading && alerts.length === 0 && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {!loading && alerts.length === 0 && !error && (
          <div className="text-center py-8 text-muted-foreground">
            <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No alerts found</p>
            <p className="text-sm">Your farm is running smoothly!</p>
          </div>
        )}

        {alerts.map((alert) => (
          <AlertItem
            key={alert.id}
            alert={alert}
            onMarkAsRead={handleMarkAsRead}
          />
        ))}

        {hasMore && (
          <div className="text-center pt-4">
            <Button
              variant="outline"
              onClick={handleLoadMore}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : null}
              Load More Alerts
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
