"use client";

import { useEffect, useRef, useCallback } from "react";
import { createClient } from "@supabase/supabase-js";

interface RealtimeAlertPayload {
  type: 'alert_status_change' | 'bulk_alert_status_change' | 'unread_count_change';
  alert_id?: string;
  farmer_id: string;
  read_status?: boolean;
  read_at?: string;
  timestamp: string;
  updated_count?: number;
  alerts?: Array<{
    id: string;
    read_status: boolean;
    read_at?: string;
  }>;
  unread_count?: number;
}

interface UseRealtimeAlertsProps {
  farmerId: string;
  onAlertStatusChange?: (alertId: string, readStatus: boolean, readAt?: string) => void;
  onBulkStatusChange?: (updatedAlerts: Array<{id: string; read_status: boolean; read_at?: string}>) => void;
  onUnreadCountChange?: (unreadCount: number) => void;
}

export function useRealtimeAlerts({
  farmerId,
  onAlertStatusChange,
  onBulkStatusChange,
  onUnreadCountChange
}: UseRealtimeAlertsProps) {
  const supabaseRef = useRef<any>(null);
  const subscriptionRef = useRef<any>(null);

  const initializeSupabase = useCallback(() => {
    if (!supabaseRef.current) {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
      const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      
      if (!supabaseUrl || !supabaseAnonKey) {
        console.warn('Supabase environment variables not found, real-time features disabled');
        return;
      }
      
      supabaseRef.current = createClient(supabaseUrl, supabaseAnonKey);
    }
    return supabaseRef.current;
  }, []);

  const handleRealtimeEvent = useCallback((payload: RealtimeAlertPayload) => {
    console.log('Realtime alert event received:', payload);

    switch (payload.type) {
      case 'alert_status_change':
        if (payload.alert_id && payload.read_status !== undefined && onAlertStatusChange) {
          onAlertStatusChange(payload.alert_id, payload.read_status, payload.read_at);
        }
        break;

      case 'bulk_alert_status_change':
        if (payload.alerts && onBulkStatusChange) {
          onBulkStatusChange(payload.alerts);
        }
        break;

      case 'unread_count_change':
        if (payload.unread_count !== undefined && onUnreadCountChange) {
          onUnreadCountChange(payload.unread_count);
        }
        break;

      default:
        console.warn('Unknown realtime event type:', payload.type);
    }
  }, [onAlertStatusChange, onBulkStatusChange, onUnreadCountChange]);

  const subscribeToAlertChanges = useCallback(() => {
    const supabase = initializeSupabase();
    if (!supabase) return;

    // Subscribe to alert status changes for this farmer
    const channel = supabase
      .channel(`alert-status-${farmerId}`)
      .on('postgres_changes', 
        { 
          event: 'UPDATE', 
          schema: 'public', 
          table: 'katara_alerts',
          filter: `farmer_id=eq.${farmerId}`
        },
        (payload: any) => {
          const newRecord = payload.new;
          const oldRecord = payload.old;
          
          // Only process if read_status actually changed
          if (newRecord.read_status !== oldRecord.read_status) {
            handleRealtimeEvent({
              type: 'alert_status_change',
              alert_id: newRecord.id,
              farmer_id: farmerId,
              read_status: newRecord.read_status,
              read_at: newRecord.read_at,
              timestamp: new Date().toISOString()
            });
          }
        }
      )
      .subscribe((status: string) => {
        console.log('Realtime subscription status:', status);
      });

    subscriptionRef.current = channel;

    return () => {
      if (subscriptionRef.current) {
        supabase.removeChannel(subscriptionRef.current);
        subscriptionRef.current = null;
      }
    };
  }, [farmerId, initializeSupabase, handleRealtimeEvent]);

  useEffect(() => {
    const cleanup = subscribeToAlertChanges();
    
    return cleanup;
  }, [subscribeToAlertChanges]);

  // Manual reconnect function
  const reconnect = useCallback(() => {
    if (subscriptionRef.current) {
      const supabase = initializeSupabase();
      if (supabase) {
        supabase.removeChannel(subscriptionRef.current);
      }
    }
    
    subscribeToAlertChanges();
  }, [initializeSupabase, subscribeToAlertChanges]);

  return {
    isConnected: !!subscriptionRef.current,
    reconnect
  };
}
