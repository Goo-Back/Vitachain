"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface NDVIAlert {
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  type: string;
}

export interface NDVICurrent {
  ndvi_value: number;
  timestamp: string;
  location: {
    lat: number;
    lng: number;
  };
  image_url?: string;
}

export interface NDVIHistoryPoint {
  timestamp: string;
  ndvi_value: number;
  image_url?: string;
}

export interface NDVIData {
  current: NDVICurrent;
  trend: {
    direction: 'increasing' | 'decreasing' | 'stable';
    change_rate: number;
    period_days: number;
  };
  historical: NDVIHistoryPoint[];
  alerts: NDVIAlert[];
  cached_at: string;
  cache_expires: string;
}

export function useKataraNDVI() {
  const [ndviData, setNdvData] = useState<NDVIData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Fetch NDVI data for device
  const fetchNDVIData = useCallback(async (deviceId: string) => {
    try {
      setError(null);
      setLoading(true);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/ndvi/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch NDVI data');
      }

      const data = await response.json();
      setNdvData(data);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('NDVI data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  // Fetch NDVI history for device
  const fetchNDVIHistory = useCallback(async (deviceId: string, days: number = 30) => {
    try {
      setError(null);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/ndvi/${deviceId}/history?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch NDVI history');
      }

      const data = await response.json();
      return data.history || [];
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('NDVI history fetch error:', err);
      return [];
    }
  }, [supabase]);

  // Clear NDVI data
  const clearNDVIData = useCallback(() => {
    setNdvData(null);
    setError(null);
  }, []);

  return {
    ndviData,
    loading,
    error,
    fetchNDVIData,
    fetchNDVIHistory,
    clearNDVIData,
  };
}
