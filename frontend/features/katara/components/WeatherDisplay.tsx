"use client";

import React from 'react';
import { useKataraWeather, WeatherData } from '@/hooks/useKataraWeather';

interface WeatherDisplayProps {
  deviceId: string;
  showHistory?: boolean;
}

export default function WeatherDisplay({ deviceId, showHistory = false }: WeatherDisplayProps) {
  const { weatherData, history, loading, error, fetchWeatherData, fetchWeatherHistory } = useKataraWeather();

  React.useEffect(() => {
    if (deviceId) {
      fetchWeatherData(deviceId);
      if (showHistory) {
        fetchWeatherHistory(deviceId);
      }
    }
  }, [deviceId, showHistory, fetchWeatherData, fetchWeatherHistory]);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Météo</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-6 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Météo</h3>
        <div className="text-red-600">
          Erreur: {error}
        </div>
      </div>
    );
  }

  if (!weatherData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Météo</h3>
        <div className="text-gray-500 text-center py-4">
          Aucune donnée météo disponible
        </div>
      </div>
    );
  }

  const getWeatherIcon = (main: string) => {
    switch (main.toLowerCase()) {
      case 'clear':
        return '☀️';
      case 'clouds':
        return '☁️';
      case 'rain':
        return '🌧️';
      case 'snow':
        return '❄️';
      case 'thunderstorm':
        return '⛈️';
      case 'drizzle':
        return '🌦️';
      case 'mist':
      case 'fog':
        return '🌫️';
      default:
        return '🌤️';
    }
  };

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Météo</h3>
        <button
          onClick={() => fetchWeatherData(deviceId)}
          className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Actualiser
        </button>
      </div>

      {/* Current Weather */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className="text-4xl">{getWeatherIcon(weatherData.current.weather_main)}</span>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {weatherData.current.temperature.toFixed(1)}°C
              </div>
              <div className="text-gray-600 capitalize">
                {weatherData.current.weather_description}
              </div>
            </div>
          </div>
          <div className="text-right text-sm text-gray-500">
            <div>📍 {weatherData.current.location.lat.toFixed(4)}, {weatherData.current.location.lng.toFixed(4)}</div>
            <div>Mis à jour: {new Date(weatherData.cached_at).toLocaleTimeString('fr-FR')}</div>
          </div>
        </div>

        {/* Weather Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="text-blue-600 text-sm">Humidité</div>
            <div className="text-lg font-semibold text-blue-800">
              {weatherData.current.humidity.toFixed(0)}%
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="text-green-600 text-sm">Pression</div>
            <div className="text-lg font-semibold text-green-800">
              {weatherData.current.pressure.toFixed(0)} hPa
            </div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg">
            <div className="text-purple-600 text-sm">Vent</div>
            <div className="text-lg font-semibold text-purple-800">
              {weatherData.current.wind_speed.toFixed(1)} m/s
            </div>
          </div>
          <div className="bg-yellow-50 p-3 rounded-lg">
            <div className="text-yellow-600 text-sm">UV Index</div>
            <div className="text-lg font-semibold text-yellow-800">
              {weatherData.current.uv_index.toFixed(1)}
            </div>
          </div>
        </div>

        {/* Additional Details */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 text-sm">
          <div className="flex items-center space-x-2">
            <span>🌧️</span>
            <span>Pluie (1h): {weatherData.current.rainfall_1h.toFixed(1)}mm</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>💧</span>
            <span>Pluie (24h): {weatherData.current.rainfall_24h.toFixed(1)}mm</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>👁️</span>
            <span>Visibilité: {weatherData.current.visibility.toFixed(0)}m</span>
          </div>
        </div>
      </div>

      {/* Weather Alerts */}
      {weatherData.alerts.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Alertes Météo</h4>
          <div className="space-y-2">
            {weatherData.alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${getAlertColor(alert.severity)}`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">⚠️</span>
                  <div>
                    <div className="font-medium">{alert.message}</div>
                    <div className="text-sm opacity-75">Type: {alert.type}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Forecast */}
      {weatherData.forecast.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Prévisions (24h)</h4>
          <div className="space-y-2">
            {weatherData.forecast.slice(0, 6).map((forecast, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{getWeatherIcon(forecast.weather_main)}</span>
                  <div>
                    <div className="text-sm font-medium capitalize">
                      {forecast.weather_description}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(forecast.timestamp).toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{forecast.temperature.toFixed(1)}°C</div>
                  <div className="text-xs text-gray-500">
                    💧 {forecast.humidity.toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History */}
      {showHistory && history.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Historique (7 jours)</h4>
          <div className="max-h-48 overflow-y-auto">
            <div className="space-y-1">
              {history.slice(0, 20).map((point, index) => (
                <div key={index} className="flex items-center justify-between text-sm p-2 hover:bg-gray-50 rounded">
                  <div className="flex items-center space-x-2">
                    <span>{getWeatherIcon(point.weather_main)}</span>
                    <span>{new Date(point.timestamp).toLocaleDateString('fr-FR')}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span>{point.temperature.toFixed(1)}°C</span>
                    <span>{point.humidity.toFixed(0)}%</span>
                    <span>{point.rainfall_1h.toFixed(1)}mm</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
