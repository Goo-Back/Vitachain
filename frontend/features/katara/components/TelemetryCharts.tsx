"use client";

import React from 'react';

interface TelemetryPoint {
  device_id: string;
  temperature?: number;
  humidity?: number;
  ndvi?: number;
  timestamp: string;
}

interface TrendData {
  last_24_hours: TelemetryPoint[];
}

interface TelemetryChartsProps {
  trendData: TrendData;
  loading?: boolean;
  selectedDeviceId?: string;
}

export default function TelemetryCharts({ trendData, loading = false, selectedDeviceId }: TelemetryChartsProps) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Tendances (24h)</h2>
        <div className="space-y-6">
          {['Température', 'Humidité', 'NDVI'].map((title, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2 w-32"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Filter data by selected device if provided
  const filteredData = selectedDeviceId
    ? trendData.last_24_hours.filter(point => point.device_id === selectedDeviceId)
    : trendData.last_24_hours;

  // Sort by timestamp
  const sortedData = [...filteredData].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  // Group data by hour for cleaner visualization
  const hourlyData = sortedData.reduce((acc, point) => {
    const hour = new Date(point.timestamp).getHours();
    if (!acc[hour]) {
      acc[hour] = {
        hour,
        temperatures: [],
        humidities: [],
        ndvis: [],
        timestamps: []
      };
    }
    
    if (point.temperature !== undefined) acc[hour].temperatures.push(point.temperature);
    if (point.humidity !== undefined) acc[hour].humidities.push(point.humidity);
    if (point.ndvi !== undefined) acc[hour].ndvis.push(point.ndvi);
    acc[hour].timestamps.push(point.timestamp);
    
    return acc;
  }, {} as Record<number, { hour: number; temperatures: number[]; humidities: number[]; ndvis: number[]; timestamps: string[] }>);

  // Calculate hourly averages
  const chartData = Object.values(hourlyData).map(hourData => ({
    hour: hourData.hour,
    temperature: hourData.temperatures.length > 0 
      ? hourData.temperatures.reduce((a, b) => a + b, 0) / hourData.temperatures.length 
      : null,
    humidity: hourData.humidities.length > 0
      ? hourData.humidities.reduce((a, b) => a + b, 0) / hourData.humidities.length
      : null,
    ndvi: hourData.ndvis.length > 0
      ? hourData.ndvis.reduce((a, b) => a + b, 0) / hourData.ndvis.length
      : null,
    dataPoints: hourData.timestamps.length
  })).sort((a, b) => a.hour - b.hour);

  const formatHour = (hour: number) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  const renderMiniChart = (title: string, data: number[], color: string, unit: string) => {
    if (data.length === 0) return null;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    return (
      <div>
        <h3 className="text-lg font-medium mb-2">{title}</h3>
        <div className="h-32 relative bg-gray-50 rounded p-2">
          <svg className="w-full h-full" viewBox="0 0 200 100">
            {data.map((value, index) => {
              const x = (index / (data.length - 1 || 1)) * 180 + 10;
              const y = 90 - ((value - min) / range) * 70;
              
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="2"
                  fill={color}
                />
              );
            })}
            
            {/* Draw connecting lines */}
            {data.map((value, index) => {
              if (index === 0) return null;
              const x = (index / (data.length - 1 || 1)) * 180 + 10;
              const y = 90 - ((value - min) / range) * 70;
              const prevX = ((index - 1) / (data.length - 1 || 1)) * 180 + 10;
              const prevY = 90 - ((data[index - 1] - min) / range) * 70;
              
              return (
                <line
                  key={`line-${index}`}
                  x1={prevX}
                  y1={prevY}
                  x2={x}
                  y2={y}
                  stroke={color}
                  strokeWidth="1"
                />
              );
            })}
          </svg>
          
          <div className="absolute bottom-1 left-2 text-xs text-gray-500">
            {min.toFixed(1)}{unit}
          </div>
          <div className="absolute bottom-1 right-2 text-xs text-gray-500">
            {max.toFixed(1)}{unit}
          </div>
        </div>
      </div>
    );
  };

  if (chartData.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Tendances (24h)</h2>
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📊</div>
          <p>Aucune donnée de tendance disponible</p>
          <p className="text-sm mt-2">Les données apparaîtront ici après 24h de collecte</p>
        </div>
      </div>
    );
  }

  const temperatureData = chartData.map(d => d.temperature).filter((t): t is number => t !== null);
  const humidityData = chartData.map(d => d.humidity).filter((h): h is number => h !== null);
  const ndviData = chartData.map(d => d.ndvi).filter((n): n is number => n !== null);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Tendances (24h)</h2>
        <div className="text-sm text-gray-500">
          {selectedDeviceId ? `Appareil: ${selectedDeviceId.slice(-8)}` : 'Tous les appareils'}
        </div>
      </div>

      <div className="space-y-6">
        {/* Temperature Chart */}
        {temperatureData.length > 0 && renderMiniChart('Température', temperatureData, '#ef4444', '°C')}
        
        {/* Humidity Chart */}
        {humidityData.length > 0 && renderMiniChart('Humidité', humidityData, '#3b82f6', '%')}
        
        {/* NDVI Chart */}
        {ndviData.length > 0 && renderMiniChart('NDVI', ndviData, '#10b981', '')}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {temperatureData.length > 0 ? (Math.max(...temperatureData)).toFixed(1) : '--'}°C
            </div>
            <div className="text-sm text-gray-500">Temp. Max</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {humidityData.length > 0 ? (Math.min(...humidityData)).toFixed(1) : '--'}%
            </div>
            <div className="text-sm text-gray-500">Humidité Min</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {ndviData.length > 0 ? (ndviData[ndviData.length - 1]).toFixed(2) : '--'}
            </div>
            <div className="text-sm text-gray-500">NDVI Actuel</div>
          </div>
        </div>
      </div>
    </div>
  );
}
