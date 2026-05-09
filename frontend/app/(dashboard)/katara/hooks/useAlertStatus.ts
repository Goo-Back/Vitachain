"use client";

import { useState, useCallback } from "react";

interface AlertStatusUpdateResponse {
  id: string;
  read_status: boolean;
  read_at?: string;
  updated_at: string;
}

interface BulkStatusUpdateResponse {
  updated_count: number;
  failed_updates: number;
  updated_alerts: any[];
}

export function useAlertStatus() {
  const [isUpdating, setIsUpdating] = useState(false);

  const updateStatus = useCallback(async ({ alertId, readStatus }: { alertId: string; readStatus: boolean }) => {
    try {
      setIsUpdating(true);
      
      const response = await fetch(`/api/katara/alerts/${alertId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ read_status: readStatus }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update alert status: ${response.statusText}`);
      }

      return response.json() as Promise<AlertStatusUpdateResponse>;
    } catch (error) {
      console.error('Error updating alert status:', error);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const bulkUpdateStatus = useCallback(async ({ alertIds, readStatus }: { alertIds: string[]; readStatus: boolean }) => {
    try {
      setIsUpdating(true);
      
      const response = await fetch(`/api/katara/alerts/bulk-status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          alert_ids: alertIds,
          read_status: readStatus 
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update alerts: ${response.statusText}`);
      }

      return response.json() as Promise<BulkStatusUpdateResponse>;
    } catch (error) {
      console.error('Error bulk updating alert status:', error);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  }, []);

  return {
    updateStatus,
    bulkUpdateStatus,
    isUpdating
  };
}
