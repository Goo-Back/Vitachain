"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface SummaryStats {
  avg_temperature?: number;
  avg_humidity?: number;
  avg_ndvi?: number;
  total_devices: number;
  online_devices: number;
  offline_devices: number;
}

export interface CurrentTelemetry {
  temperature?: number;
  humidity?: number;
  ndvi?: number;
  battery_level?: number;
  timestamp: string;
}

export interface DashboardDevice {
  id: string;
  device_id: string;
  name?: string;
  location_lat?: number;
  location_lng?: number;
  status: 'online' | 'offline' | 'unknown';
  last_seen: string;
  current_telemetry?: CurrentTelemetry;
}

export interface DashboardAlert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  created_at: string;
}

export interface AlertsInfo {
  unread_count: number;
  recent_alerts: DashboardAlert[];
}

export interface TelemetryPoint {
  device_id: string;
  temperature?: number;
  humidity?: number;
  ndvi?: number;
  timestamp: string;
}

export interface TrendData {
  last_24_hours: TelemetryPoint[];
}

export interface DashboardData {
  devices: DashboardDevice[];
  summary_stats: SummaryStats;
  alerts: AlertsInfo;
  trend_data: TrendData;
}

export interface UseKataraDashboardOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableRealtime?: boolean;
}

export function useKataraDashboard(options: UseKataraDashboardOptions = {}) {
  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
    enableRealtime = true
  } = options;

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected');
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      
      // Get current user session
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      // Fetch dashboard data from API
      const response = await fetch('/api/katara/dashboard', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch dashboard data');
      }

      const dashboardData: DashboardData = await response.json();
      setData(dashboardData);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  // Setup real-time subscriptions
  const setupRealtimeSubscriptions = useCallback(() => {
    if (!enableRealtime) return;

    // Get current user
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) return;

      const farmerId = user.id;

      // Subscribe to telemetry changes
      const telemetrySubscription = supabase
        .channel(`telemetry-${farmerId}`)
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'telemetry_readings',
            filter: `farmer_id=eq.${farmerId}`
          },
          (payload) => {
            console.log('New telemetry data:', payload);
            // Update device telemetry in state
            setData(prevData => {
              if (!prevData) return prevData;

              const newTelemetry = payload.new as any;
              const updatedDevices = prevData.devices.map(device => {
                if (device.device_id === newTelemetry.device_id) {
                  return {
                    ...device,
                    status: 'online' as const,
                    last_seen: newTelemetry.timestamp,
                    current_telemetry: {
                      temperature: newTelemetry.temperature,
                      humidity: newTelemetry.humidity,
                      ndvi: newTelemetry.ndvi,
                      battery_level: newTelemetry.battery_level,
                      timestamp: newTelemetry.timestamp
                    }
                  };
                }
                return device;
              });

              // Update summary stats
              const updatedStats = calculateSummaryStats(updatedDevices);

              // Add to trend data
              const updatedTrendData = {
                ...prevData.trend_data,
                last_24_hours: [
                  {
                    device_id: newTelemetry.device_id,
                    temperature: newTelemetry.temperature,
                    humidity: newTelemetry.humidity,
                    ndvi: newTelemetry.ndvi,
                    timestamp: newTelemetry.timestamp
                  },
                  ...prevData.trend_data.last_24_hours.slice(0, 99) // Keep last 100 points
                ]
              };

              return {
                ...prevData,
                devices: updatedDevices,
                summary_stats: updatedStats,
                trend_data: updatedTrendData
              };
            });
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            setConnectionStatus('connected');
          } else if (status === 'CHANNEL_ERROR') {
            setConnectionStatus('disconnected');
          }
        });

      // Subscribe to alert changes
      const alertsSubscription = supabase
        .channel(`alerts-${farmerId}`)
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'katara_alerts',
            filter: `farmer_id=eq.${farmerId}`
          },
          (payload) => {
            console.log('New alert:', payload);
            // Update alerts in state
            setData(prevData => {
              if (!prevData) return prevData;

              const newAlert = payload.new as any;
              const updatedAlerts = {
                unread_count: prevData.alerts.unread_count + 1,
                recent_alerts: [
                  {
                    id: newAlert.id,
                    type: newAlert.type,
                    severity: newAlert.severity,
                    message: newAlert.message,
                    created_at: newAlert.created_at
                  },
                  ...prevData.alerts.recent_alerts.slice(0, 9) // Keep last 10 alerts
                ]
              };

              return {
                ...prevData,
                alerts: updatedAlerts
              };
            });
          }
        )
        .subscribe();

      // Cleanup function
      return () => {
        telemetrySubscription.unsubscribe();
        alertsSubscription.unsubscribe();
      };
    });
  }, [supabase, enableRealtime]);

  // Calculate summary stats helper
  const calculateSummaryStats = (devices: DashboardDevice[]): SummaryStats => {
    const totalDevices = devices.length;
    const onlineDevices = devices.filter(d => d.status === 'online').length;
    const offlineDevices = totalDevices - onlineDevices;

    const temperatures = devices
      .map(d => d.current_telemetry?.temperature)
      .filter((t): t is number => t !== undefined);
    
    const humidities = devices
      .map(d => d.current_telemetry?.humidity)
      .filter((h): h is number => h !== undefined);
    
    const ndvis = devices
      .map(d => d.current_telemetry?.ndvi)
      .filter((n): n is number => n !== undefined);

    return {
      avg_temperature: temperatures.length > 0 
        ? temperatures.reduce((a, b) => a + b, 0) / temperatures.length 
        : undefined,
      avg_humidity: humidities.length > 0
        ? humidities.reduce((a, b) => a + b, 0) / humidities.length
        : undefined,
      avg_ndvi: ndvis.length > 0
        ? ndvis.reduce((a, b) => a + b, 0) / ndvis.length
        : undefined,
      total_devices: totalDevices,
      online_devices: onlineDevices,
      offline_devices: offlineDevices
    };
  };

  // Mark alert as read
  const markAlertAsRead = useCallback(async (alertId: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`/api/katara/alerts/${alertId}/read`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update local state
        setData(prevData => {
          if (!prevData) return prevData;
          
          const updatedAlerts = {
            ...prevData.alerts,
            unread_count: Math.max(0, prevData.alerts.unread_count - 1),
            recent_alerts: prevData.alerts.recent_alerts.map(alert =>
              alert.id === alertId ? { ...alert } : alert
            )
          };

          return {
            ...prevData,
            alerts: updatedAlerts
          };
        });
      }
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  }, [supabase]);

  // Mark all alerts as read
  const markAllAlertsAsRead = useCallback(async () => {
    // This would need a bulk update endpoint
    // For now, just update local state
    setData(prevData => {
      if (!prevData) return prevData;
      
      return {
        ...prevData,
        alerts: {
          ...prevData.alerts,
          unread_count: 0
        }
      };
    });
  }, []);

  // Refresh data
  const refresh = useCallback(() => {
    setLoading(true);
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Setup real-time subscriptions
  useEffect(() => {
    if (!enableRealtime) return;

    const cleanup = setupRealtimeSubscriptions();
    return cleanup;
  }, [setupRealtimeSubscriptions, enableRealtime]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refresh();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refresh]);

  return {
    data,
    loading,
    error,
    connectionStatus,
    selectedDeviceId,
    setSelectedDeviceId,
    refresh,
    markAlertAsRead,
    markAllAlertsAsRead,
  };
}
