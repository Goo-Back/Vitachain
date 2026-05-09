"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface WeatherAlert {
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  type: string;
}

export interface WeatherCurrent {
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  rainfall_1h: number;
  rainfall_24h: number;
  weather_main: string;
  weather_description: string;
  visibility: number;
  uv_index: number;
  location: {
    lat: number;
    lng: number;
  };
}

export interface WeatherForecast {
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  rainfall: number;
  weather_main: string;
  weather_description: string;
}

export interface WeatherData {
  current: WeatherCurrent;
  forecast: WeatherForecast[];
  alerts: WeatherAlert[];
  cached_at: string;
  cache_expires: string;
}

export interface WeatherHistoryPoint {
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  rainfall_1h: number;
  weather_main: string;
  weather_description: string;
}

export function useKataraWeather() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [history, setHistory] = useState<WeatherHistoryPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Fetch weather data for device
  const fetchWeatherData = useCallback(async (deviceId: string) => {
    try {
      setError(null);
      setLoading(true);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/weather/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch weather data');
      }

      const data = await response.json();
      setWeatherData(data);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Weather data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  // Fetch weather history for device
  const fetchWeatherHistory = useCallback(async (deviceId: string, days: number = 7) => {
    try {
      setError(null);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/weather/${deviceId}/history?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch weather history');
      }

      const data = await response.json();
      setHistory(data.history || []);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Weather history fetch error:', err);
    }
  }, [supabase]);

  // Clear weather data
  const clearWeatherData = useCallback(() => {
    setWeatherData(null);
    setHistory([]);
    setError(null);
  }, []);

  return {
    weatherData,
    history,
    loading,
    error,
    fetchWeatherData,
    fetchWeatherHistory,
    clearWeatherData,
  };
}
