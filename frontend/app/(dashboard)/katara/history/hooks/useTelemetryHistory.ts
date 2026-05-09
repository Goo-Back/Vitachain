"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import { format, subDays, startOfDay, endOfDay } from "date-fns";

interface HistoryParams {
  start_date: string;
  end_date: string;
  device_id?: string;
  aggregation: "hour" | "day";
}

interface HourlyData {
  hour_bucket: string;
  avg_temp: number | null;
  min_temp: number | null;
  max_temp: number | null;
  avg_humidity: number | null;
  avg_ndvi: number | null;
  reading_count: number;
}

interface DeviceChartData {
  device_id: string;
  device_name: string | null;
  hourly_data: HourlyData[];
}

interface DailyStats {
  date: string;
  avg_temp: number | null;
  min_temp: number | null;
  max_temp: number | null;
  avg_humidity: number | null;
  avg_ndvi: number | null;
  total_readings: number;
}

interface TrendAnalysis {
  temperature_trend: string;
  humidity_trend: string;
  ndvi_trend: string;
  correlations: {
    temp_humidity: number;
    temp_ndvi: number;
  };
}

interface AlertPattern {
  date: string;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  main_causes: string[];
}

interface PeriodInfo {
  start_date: string;
  end_date: string;
  total_readings: number;
  devices_analyzed: number;
}

interface HistoryResponse {
  period_info: PeriodInfo;
  chart_data: DeviceChartData[];
  daily_stats: DailyStats[];
  trend_analysis: TrendAnalysis;
  alert_patterns: AlertPattern[];
}

interface UseTelemetryHistoryOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function useTelemetryHistory(options: UseTelemetryHistoryOptions = {}) {
  const { autoRefresh = false, refreshInterval = 300000 } = options; // 5 minutes default
  const [params, setParams] = useState<HistoryParams>({
    start_date: format(subDays(new Date(), 30), "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"),
    end_date: format(new Date(), "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"),
    aggregation: "hour",
  });
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);

  const supabase = createClientComponentClient();

  const fetchHistoryData = async (): Promise<HistoryResponse> => {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      throw new Error("Not authenticated");
    }

    const queryParams = new URLSearchParams({
      start_date: params.start_date,
      end_date: params.end_date,
      aggregation: params.aggregation,
    });

    if (selectedDeviceId) {
      queryParams.append("device_id", selectedDeviceId);
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/katara/history?${queryParams}`,
      {
        headers: {
          "Authorization": `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  };

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["telemetry-history", params, selectedDeviceId],
    queryFn: fetchHistoryData,
    enabled: !!(params.start_date && params.end_date),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Update params function
  const updateParams = (newParams: Partial<HistoryParams>) => {
    setParams(prev => ({ ...prev, ...newParams }));
  };

  // Quick date range presets
  const setDateRange = (days: number) => {
    const endDate = new Date();
    const startDate = subDays(endDate, days);
    
    updateParams({
      start_date: format(startOfDay(startDate), "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"),
      end_date: format(endOfDay(endDate), "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"),
    });
  };

  // Export data functions
  const exportToCSV = async () => {
    if (!data) return;

    const csvRows = [];
    
    // Header
    csvRows.push("Date,Device,Temperature,Humidity,NDVI,Reading Count");
    
    // Data rows
    data.chart_data.forEach(device => {
      device.hourly_data.forEach(hour => {
        csvRows.push(
          `${hour.hour_bucket},${device.device_name || device.device_id},${hour.avg_temp || ""},${hour.avg_humidity || ""},${hour.avg_ndvi || ""},${hour.reading_count}`
        );
      });
    });

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `telemetry-history-${format(new Date(), "yyyy-MM-dd")}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const exportToJSON = () => {
    if (!data) return;

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `telemetry-history-${format(new Date(), "yyyy-MM-dd")}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return {
    data,
    isLoading,
    error,
    params,
    selectedDeviceId,
    setSelectedDeviceId,
    updateParams,
    setDateRange,
    refetch,
    exportToCSV,
    exportToJSON,
  };
}

export type { HistoryResponse, DeviceChartData, HourlyData, DailyStats, TrendAnalysis, AlertPattern };
