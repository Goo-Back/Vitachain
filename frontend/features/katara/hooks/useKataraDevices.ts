"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface KataraDevice {
  id: string;
  device_id: string;
  name?: string;
  location_lat?: number;
  location_lng?: number;
  status: 'online' | 'offline' | 'unknown';
  last_seen: string;
  created_at: string;
  updated_at: string;
  farmer_id: string;
}

export interface DeviceCreateRequest {
  name: string;
  location_lat: number;
  location_lng: number;
}

export interface DeviceUpdateRequest {
  name?: string;
  location_lat?: number;
  location_lng?: number;
}

export function useKataraDevices() {
  const [devices, setDevices] = useState<KataraDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Fetch devices
  const fetchDevices = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch('/api/katara/devices', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch devices');
      }

      const data = await response.json();
      setDevices(data.devices || []);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Devices fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  // Create device
  const createDevice = useCallback(async (deviceData: DeviceCreateRequest): Promise<KataraDevice> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch('/api/katara/devices', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to create device');
      }

      const newDevice = await response.json();
      setDevices(prev => [...prev, newDevice]);
      return newDevice;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Device creation error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Update device
  const updateDevice = useCallback(async (deviceId: string, updateData: DeviceUpdateRequest): Promise<KataraDevice> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/devices/${deviceId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to update device');
      }

      const updatedDevice = await response.json();
      setDevices(prev => prev.map(device => 
        device.id === deviceId ? updatedDevice : device
      ));
      return updatedDevice;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Device update error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Delete device
  const deleteDevice = useCallback(async (deviceId: string): Promise<void> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/devices/${deviceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to delete device');
      }

      setDevices(prev => prev.filter(device => device.id !== deviceId));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Device deletion error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Get device by ID
  const getDevice = useCallback(async (deviceId: string): Promise<KataraDevice | null> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/devices/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch device');
      }

      return await response.json();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Device fetch error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Initial fetch
  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  return {
    devices,
    loading,
    error,
    fetchDevices,
    createDevice,
    updateDevice,
    deleteDevice,
    getDevice,
  };
}
