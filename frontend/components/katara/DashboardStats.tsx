"use client";

import React from 'react';

interface SummaryStats {
  avg_temperature?: number;
  avg_humidity?: number;
  avg_ndvi?: number;
  total_devices: number;
  online_devices: number;
  offline_devices: number;
}

interface DashboardStatsProps {
  stats: SummaryStats;
  loading?: boolean;
}

export default function DashboardStats({ stats, loading = false }: DashboardStatsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  const formatValue = (value: number | undefined, decimals: number = 1) => {
    return value !== undefined ? value.toFixed(decimals) : '--';
  };

  const getDeviceStatusColor = (online: number, total: number) => {
    if (total === 0) return 'text-gray-600';
    const percentage = (online / total) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {/* Active Devices */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className={`text-3xl font-bold ${getDeviceStatusColor(stats.online_devices, stats.total_devices)}`}>
          {stats.online_devices}/{stats.total_devices}
        </div>
        <div className="text-gray-500 text-sm mt-1">Appareils Actifs</div>
        {stats.offline_devices > 0 && (
          <div className="text-xs text-red-500 mt-1">
            {stats.offline_devices} hors ligne
          </div>
        )}
      </div>

      {/* Average Temperature */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="text-3xl font-bold text-blue-600">
          {formatValue(stats.avg_temperature)}°C
        </div>
        <div className="text-gray-500 text-sm mt-1">Température Moyenne</div>
        {stats.avg_temperature !== undefined && (
          <div className="text-xs text-gray-400 mt-1">
            {stats.avg_temperature > 35 ? '⚠️ Élevée' : stats.avg_temperature < 15 ? '❄️ Basse' : '✅ Normale'}
          </div>
        )}
      </div>

      {/* Average Humidity */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="text-3xl font-bold text-cyan-600">
          {formatValue(stats.avg_humidity)}%
        </div>
        <div className="text-gray-500 text-sm mt-1">Humidité Moyenne</div>
        {stats.avg_humidity !== undefined && (
          <div className="text-xs text-gray-400 mt-1">
            {stats.avg_humidity < 30 ? '⚠️ Faible' : stats.avg_humidity > 80 ? '💧 Élevée' : '✅ Normale'}
          </div>
        )}
      </div>

      {/* Average NDVI */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="text-3xl font-bold text-green-600">
          {formatValue(stats.avg_ndvi)}
        </div>
        <div className="text-gray-500 text-sm mt-1">NDVI Moyen</div>
        {stats.avg_ndvi !== undefined && (
          <div className="text-xs text-gray-400 mt-1">
            {stats.avg_ndvi < 0.3 ? '⚠️ Stress' : stats.avg_ndvi > 0.6 ? '🌿 Sain' : '📊 Modéré'}
          </div>
        )}
      </div>
    </div>
  );
}
