"use client";

import { DailyStats, TrendAnalysis } from "../hooks/useTelemetryHistory";

interface StatisticsPanelProps {
  dailyStats: DailyStats[];
  trendAnalysis: TrendAnalysis;
}

export default function StatisticsPanel({ dailyStats, trendAnalysis }: StatisticsPanelProps) {
  const calculateOverallStats = () => {
    if (dailyStats.length === 0) return null;

    const temps = dailyStats.map(d => d.avg_temp).filter(t => t !== null) as number[];
    const humidities = dailyStats.map(d => d.avg_humidity).filter(h => h !== null) as number[];
    const ndvis = dailyStats.map(d => d.avg_ndvi).filter(n => n !== null) as number[];

    return {
      temperature: {
        avg: temps.length > 0 ? temps.reduce((a, b) => a + b, 0) / temps.length : null,
        min: temps.length > 0 ? Math.min(...temps) : null,
        max: temps.length > 0 ? Math.max(...temps) : null,
      },
      humidity: {
        avg: humidities.length > 0 ? humidities.reduce((a, b) => a + b, 0) / humidities.length : null,
        min: humidities.length > 0 ? Math.min(...humidities) : null,
        max: humidities.length > 0 ? Math.max(...humidities) : null,
      },
      ndvi: {
        avg: ndvis.length > 0 ? ndvis.reduce((a, b) => a + b, 0) / ndvis.length : null,
        min: ndvis.length > 0 ? Math.min(...ndvis) : null,
        max: ndvis.length > 0 ? Math.max(...ndvis) : null,
      },
    };
  };

  const overallStats = calculateOverallStats();

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return '📈';
      case 'decreasing':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '❓';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'text-red-600';
      case 'decreasing':
        return 'text-blue-600';
      case 'stable':
        return 'text-gray-600';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Statistical Analysis</h2>

      {overallStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Temperature Statistics */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">Temperature</h3>
              <span className={getTrendColor(trendAnalysis.temperature_trend)}>
                {getTrendIcon(trendAnalysis.temperature_trend)}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Average:</span>
                <span className="font-medium">
                  {overallStats.temperature.avg ? `${overallStats.temperature.avg.toFixed(1)}°C` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Min:</span>
                <span className="font-medium">
                  {overallStats.temperature.min ? `${overallStats.temperature.min.toFixed(1)}°C` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Max:</span>
                <span className="font-medium">
                  {overallStats.temperature.max ? `${overallStats.temperature.max.toFixed(1)}°C` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Range:</span>
                <span className="font-medium">
                  {overallStats.temperature.min && overallStats.temperature.max ?
                    `${(overallStats.temperature.max - overallStats.temperature.min).toFixed(1)}°C` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Humidity Statistics */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">Humidity</h3>
              <span className={getTrendColor(trendAnalysis.humidity_trend)}>
                {getTrendIcon(trendAnalysis.humidity_trend)}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Average:</span>
                <span className="font-medium">
                  {overallStats.humidity.avg ? `${overallStats.humidity.avg.toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Min:</span>
                <span className="font-medium">
                  {overallStats.humidity.min ? `${overallStats.humidity.min.toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Max:</span>
                <span className="font-medium">
                  {overallStats.humidity.max ? `${overallStats.humidity.max.toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Range:</span>
                <span className="font-medium">
                  {overallStats.humidity.min && overallStats.humidity.max ?
                    `${(overallStats.humidity.max - overallStats.humidity.min).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* NDVI Statistics */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">NDVI</h3>
              <span className={getTrendColor(trendAnalysis.ndvi_trend)}>
                {getTrendIcon(trendAnalysis.ndvi_trend)}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Average:</span>
                <span className="font-medium">
                  {overallStats.ndvi.avg ? overallStats.ndvi.avg.toFixed(3) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Min:</span>
                <span className="font-medium">
                  {overallStats.ndvi.min ? overallStats.ndvi.min.toFixed(3) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Max:</span>
                <span className="font-medium">
                  {overallStats.ndvi.max ? overallStats.ndvi.max.toFixed(3) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Range:</span>
                <span className="font-medium">
                  {overallStats.ndvi.min && overallStats.ndvi.max ?
                    (overallStats.ndvi.max - overallStats.ndvi.min).toFixed(3) : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Daily Statistics Table */}
      {dailyStats.length > 0 && (
        <div>
          <h3 className="text-md font-medium text-gray-800 mb-4">Daily Breakdown</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Temp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Min/Max Temp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Humidity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg NDVI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Readings
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dailyStats.slice(0, 10).map((day, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(day.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {day.avg_temp ? `${day.avg_temp.toFixed(1)}°C` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {day.min_temp && day.max_temp ? 
                        `${day.min_temp.toFixed(1)}° - ${day.max_temp.toFixed(1)}°` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {day.avg_humidity ? `${day.avg_humidity.toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {day.avg_ndvi ? day.avg_ndvi.toFixed(3) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {day.total_readings.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {dailyStats.length > 10 && (
              <div className="px-6 py-3 bg-gray-50 text-center text-sm text-gray-500">
                Showing 10 of {dailyStats.length} days
              </div>
            )}
          </div>
        </div>
      )}

      {dailyStats.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-2">📊</div>
          <p className="text-gray-500">No daily statistics available</p>
        </div>
      )}
    </div>
  );
}
