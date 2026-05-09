"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface HistoryParams {
  start_date: Date;
  end_date: Date;
  device_id?: string;
  aggregation: 'hour' | 'day';
}

export interface TelemetryPoint {
  device_id: string;
  temperature?: number;
  humidity?: number;
  ndvi?: number;
  battery_level?: number;
  timestamp: string;
}

export interface HistoryStats {
  avg_temperature?: number;
  min_temperature?: number;
  max_temperature?: number;
  avg_humidity?: number;
  min_humidity?: number;
  max_humidity?: number;
  avg_ndvi?: number;
  min_ndvi?: number;
  max_ndvi?: number;
  total_readings: number;
  data_points_per_day: number;
}

export interface HistoryTrend {
  parameter: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  change_rate: number;
  confidence: number;
}

export interface HistoryAlertPattern {
  alert_type: string;
  frequency: number;
  peak_hours: number[];
  correlation_with_weather?: string;
}

export interface HistoryResponse {
  chart_data: TelemetryPoint[];
  statistics: HistoryStats;
  trends: HistoryTrend[];
  alert_patterns: HistoryAlertPattern[];
  data_quality: {
    completeness: number;
    gaps: Array<{
      start: string;
      end: string;
      duration_hours: number;
    }>;
  };
  period_info: {
    start_date: string;
    end_date: string;
    total_days: number;
    aggregation_level: string;
  };
}

export function useKataraHistory() {
  const [historyData, setHistoryData] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Fetch historical data
  const fetchHistoryData = useCallback(async (params: HistoryParams) => {
    try {
      setError(null);
      setLoading(true);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const searchParams = new URLSearchParams({
        start_date: params.start_date.toISOString(),
        end_date: params.end_date.toISOString(),
        aggregation: params.aggregation,
      });

      if (params.device_id) {
        searchParams.append('device_id', params.device_id);
      }

      const response = await fetch(`/api/katara/history?${searchParams}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch historical data');
      }

      const data = await response.json();
      setHistoryData(data);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('History data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  // Clear history data
  const clearHistoryData = useCallback(() => {
    setHistoryData(null);
    setError(null);
  }, []);

  return {
    historyData,
    loading,
    error,
    fetchHistoryData,
    clearHistoryData,
  };
}
