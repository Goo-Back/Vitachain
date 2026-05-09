"use client";

import { useState } from "react";
import { HistoryResponse } from "../hooks/useTelemetryHistory";

interface TrendChartsProps {
  data: HistoryResponse;
}

export default function TrendCharts({ data }: TrendChartsProps) {
  const [activeChart, setActiveChart] = useState<"temperature" | "humidity" | "ndvi">("temperature");

  const getChartData = (metric: "temperature" | "humidity" | "ndvi") => {
    return data.chart_data.flatMap(device =>
      device.hourly_data.map(hour => ({
        timestamp: hour.hour_bucket,
        value: hour[`avg_${metric}`],
        deviceName: device.device_name || device.device_id,
        deviceId: device.device_id,
      }))
    );
  };

  const getChartConfig = (metric: string, color: string, unit: string) => {
    return {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          time: {
            unit: data.period_info.devices_analyzed > 1 ? 'day' : 'hour',
            displayFormats: {
              day: 'MMM dd',
              hour: 'HH:mm'
            }
          },
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          title: {
            display: true,
            text: `${metric} (${unit})`
          },
          beginAtZero: false
        }
      },
      plugins: {
        legend: {
          display: data.period_info.devices_analyzed > 1
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    };
  };

  const renderChart = (metric: "temperature" | "humidity" | "ndvi") => {
    const chartData = getChartData(metric);
    
    if (chartData.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
          <p className="text-gray-500">No data available for {metric}</p>
        </div>
      );
    }

    // Simple SVG chart implementation (since we don't have Chart.js available)
    const values = chartData.map(d => d.value).filter(v => v !== null) as number[];
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const range = maxValue - minValue || 1;

    return (
      <div className="h-64 bg-gray-50 rounded-lg p-4">
        <div className="h-full flex items-end justify-between space-x-1">
          {chartData.slice(0, 50).map((point, index) => {
            if (point.value === null) return null;
            const height = ((point.value - minValue) / range) * 100;
            return (
              <div
                key={index}
                className="flex-1 bg-green-500 rounded-t"
                style={{ height: `${height}%` }}
                title={`${point.deviceName}: ${point.value?.toFixed(2)}`}
              />
            );
          })}
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          {chartData[0]?.timestamp ? new Date(chartData[0].timestamp).toLocaleDateString() : ''}
        </div>
      </div>
    );
  };

  const metricConfig = {
    temperature: { label: "Temperature", unit: "°C", color: "#ef4444" },
    humidity: { label: "Humidity", unit: "%", color: "#3b82f6" },
    ndvi: { label: "NDVI", unit: "", color: "#10b981" },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Trend Analysis</h2>
        
        {/* Chart Type Selector */}
        <div className="flex space-x-2">
          {Object.entries(metricConfig).map(([key, config]) => (
            <button
              key={key}
              onClick={() => setActiveChart(key as "temperature" | "humidity" | "ndvi")}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                activeChart === key
                  ? "bg-green-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {config.label}
            </button>
          ))}
        </div>
      </div>

      {/* Active Chart */}
      <div className="mb-4">
        <h3 className="text-md font-medium text-gray-800 mb-2">
          {metricConfig[activeChart].label} Trends
        </h3>
        {renderChart(activeChart)}
      </div>

      {/* Trend Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Temperature Trend</h4>
          <div className="flex items-center">
            <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
              data.trend_analysis.temperature_trend === 'increasing' ? 'bg-red-500' :
              data.trend_analysis.temperature_trend === 'decreasing' ? 'bg-blue-500' :
              'bg-gray-400'
            }`} />
            <span className="text-sm capitalize">{data.trend_analysis.temperature_trend}</span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Humidity Trend</h4>
          <div className="flex items-center">
            <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
              data.trend_analysis.humidity_trend === 'increasing' ? 'bg-blue-500' :
              data.trend_analysis.humidity_trend === 'decreasing' ? 'bg-red-500' :
              'bg-gray-400'
            }`} />
            <span className="text-sm capitalize">{data.trend_analysis.humidity_trend}</span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">NDVI Trend</h4>
          <div className="flex items-center">
            <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
              data.trend_analysis.ndvi_trend === 'increasing' ? 'bg-green-500' :
              data.trend_analysis.ndvi_trend === 'decreasing' ? 'bg-red-500' :
              'bg-gray-400'
            }`} />
            <span className="text-sm capitalize">{data.trend_analysis.ndvi_trend}</span>
          </div>
        </div>
      </div>

      {/* Correlations */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Metric Correlations</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex justify-between items-center bg-gray-50 rounded-lg p-3">
            <span className="text-sm text-gray-600">Temperature ↔ Humidity</span>
            <span className="text-sm font-medium">
              {data.trend_analysis.correlations.temp_humidity.toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between items-center bg-gray-50 rounded-lg p-3">
            <span className="text-sm text-gray-600">Temperature ↔ NDVI</span>
            <span className="text-sm font-medium">
              {data.trend_analysis.correlations.temp_ndvi.toFixed(3)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
