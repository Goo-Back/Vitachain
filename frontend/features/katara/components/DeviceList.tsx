"use client";

import React from 'react';

export type DeviceStatus = 'online' | 'offline' | 'unknown';

interface CurrentTelemetry {
  temperature?: number;
  humidity?: number;
  ndvi?: number;
  battery_level?: number;
  timestamp: string;
}

interface DashboardDevice {
  id: string;
  device_id: string;
  name?: string;
  location_lat?: number;
  location_lng?: number;
  status: DeviceStatus;
  last_seen: string;
  current_telemetry?: CurrentTelemetry;
}

interface DeviceListProps {
  devices: DashboardDevice[];
  loading?: boolean;
  onDeviceSelect?: (device: DashboardDevice) => void;
}

export default function DeviceList({ devices, loading = false, onDeviceSelect }: DeviceListProps) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Appareils IoT</h2>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-3 border rounded animate-pulse">
              <div className="h-5 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getStatusColor = (status: DeviceStatus) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'offline':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: DeviceStatus) => {
    switch (status) {
      case 'online':
        return 'Actif';
      case 'offline':
        return 'Inactif';
      default:
        return 'Inconnu';
    }
  };

  const formatLastSeen = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffMins < 1440) return `Il y a ${Math.floor(diffMins / 60)}h`;
    return `Il y a ${Math.floor(diffMins / 1440)}j`;
  };

  const getBatteryColor = (level?: number) => {
    if (!level) return 'text-gray-400';
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBatteryIcon = (level?: number) => {
    if (!level) return '🔋';
    if (level > 80) return '🔋';
    if (level > 50) return '🔋';
    if (level > 20) return '🪫';
    return '🪫';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Appareils IoT</h2>
          <span className="text-sm text-gray-500">{devices.length} appareils</span>
        </div>
        
        {devices.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📡</div>
            <p>Aucun appareil enregistré</p>
            <p className="text-sm mt-2">Configurez vos appareils ESP32 pour commencer</p>
          </div>
        ) : (
          <div className="space-y-3">
            {devices.map((device) => (
              <div
                key={device.id}
                className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onDeviceSelect?.(device)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {device.name || `Appareil ${device.device_id.slice(-8)}`}
                    </div>
                    <div className="text-sm text-gray-500">
                      {device.device_id}
                    </div>
                    {device.location_lat && device.location_lng && (
                      <div className="text-xs text-gray-400 mt-1">
                        📍 {device.location_lat.toFixed(4)}, {device.location_lng.toFixed(4)}
                      </div>
                    )}
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(device.status)}`}>
                    {getStatusText(device.status)}
                  </span>
                </div>

                {device.current_telemetry ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div className="flex items-center space-x-1">
                      <span>🌡️</span>
                      <span>{device.current_telemetry.temperature?.toFixed(1)}°C</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span>💧</span>
                      <span>{device.current_telemetry.humidity?.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span>🌿</span>
                      <span>{device.current_telemetry.ndvi?.toFixed(2)}</span>
                    </div>
                    <div className={`flex items-center space-x-1 ${getBatteryColor(device.current_telemetry.battery_level)}`}>
                      <span>{getBatteryIcon(device.current_telemetry.battery_level)}</span>
                      <span>{device.current_telemetry.battery_level?.toFixed(0)}%</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-gray-400">
                    Aucune donnée télémétrique disponible
                  </div>
                )}

                <div className="text-xs text-gray-400 mt-2">
                  Dernière mise à jour: {formatLastSeen(device.last_seen)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
  );
}
