"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { 
  CheckSquare, 
  Square, 
  Loader2,
  Check,
  EyeOff
} from "lucide-react";

interface Alert {
  id: string;
  read_status: boolean;
  created_at: string;
}

interface BulkActionsProps {
  alerts: Alert[];
  selectedAlerts: Set<string>;
  onSelectionChange: (selectedIds: Set<string>) => void;
  onBulkStatusChange?: (updatedCount: number) => void;
  className?: string;
}

export default function BulkActions({ 
  alerts, 
  selectedAlerts, 
  onSelectionChange,
  onBulkStatusChange,
  className = "" 
}: BulkActionsProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allIds = new Set(alerts.map(alert => alert.id));
      onSelectionChange(allIds);
    } else {
      onSelectionChange(new Set());
    }
  };

  const handleSelectAlert = (alertId: string, checked: boolean) => {
    const newSelection = new Set(selectedAlerts);
    if (checked) {
      newSelection.add(alertId);
    } else {
      newSelection.delete(alertId);
    }
    onSelectionChange(newSelection);
  };

  const handleBulkStatusUpdate = async (readStatus: boolean) => {
    if (selectedAlerts.size === 0 || isUpdating) return;

    try {
      setIsUpdating(true);
      setError(null);

      const response = await fetch(`/api/katara/alerts/bulk-status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          alert_ids: Array.from(selectedAlerts),
          read_status: readStatus 
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update alerts: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Clear selection after successful update
      onSelectionChange(new Set());
      
      if (onBulkStatusChange) {
        onBulkStatusChange(result.updated_count);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setIsUpdating(false);
    }
  };

  const isAllSelected = selectedAlerts.size === alerts.length && alerts.length > 0;
  const isPartiallySelected = selectedAlerts.size > 0 && selectedAlerts.size < alerts.length;
  const unreadSelected = Array.from(selectedAlerts).filter(id => {
    const alert = alerts.find(a => a.id === id);
    return alert && !alert.read_status;
  }).length;
  const readSelected = selectedAlerts.size - unreadSelected;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Selection Controls */}
      <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Checkbox
              checked={isAllSelected}
              ref={(ref) => {
                if (ref) {
                  ref.indeterminate = isPartiallySelected;
                }
              }}
              onCheckedChange={handleSelectAll}
            />
            <span className="text-sm font-medium">
              {isAllSelected ? 'Deselect All' : 'Select All'}
            </span>
          </div>
          
          <Badge variant="secondary" className="text-xs">
            {selectedAlerts.size} of {alerts.length} selected
          </Badge>
        </div>

        {/* Bulk Action Buttons */}
        {selectedAlerts.size > 0 && (
          <div className="flex items-center gap-2">
            {unreadSelected > 0 && (
              <Button
                variant="default"
                size="sm"
                onClick={() => handleBulkStatusUpdate(true)}
                disabled={isUpdating}
                className="text-xs"
              >
                {isUpdating ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <Check className="h-4 w-4 mr-1" />
                )}
                Mark {unreadSelected} Read
              </Button>
            )}
            
            {readSelected > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkStatusUpdate(false)}
                disabled={isUpdating}
                className="text-xs"
              >
                {isUpdating ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <EyeOff className="h-4 w-4 mr-1" />
                )}
                Mark {readSelected} Unread
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Individual Alert Checkboxes */}
      {selectedAlerts.size > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-muted-foreground font-medium">
            Selected Alerts:
          </div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {alerts
              .filter(alert => selectedAlerts.has(alert.id))
              .map(alert => (
                <div key={alert.id} className="flex items-center gap-2 p-2 bg-background rounded border">
                  <Checkbox
                    checked={selectedAlerts.has(alert.id)}
                    onCheckedChange={(checked) => handleSelectAlert(alert.id, checked as boolean)}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant={alert.read_status ? "secondary" : "outline"} 
                        className="text-xs"
                      >
                        {alert.read_status ? "Read" : "Unread"}
                      </Badge>
                      <span className="text-xs text-muted-foreground truncate">
                        {alert.id}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="text-xs text-red-600 p-2 bg-red-50 rounded">
          Error: {error}
        </div>
      )}

      {/* Status Summary */}
      {selectedAlerts.size === 0 && alerts.length > 0 && (
        <div className="text-xs text-muted-foreground text-center p-2">
          Select alerts to perform bulk actions
        </div>
      )}
    </div>
  );
}
