"use client";

import React, { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, Wind, Droplets, AlertTriangle, Thermometer, Eye } from 'lucide-react';

interface WeatherLocation {
  lat: number;
  lng: number;
}

interface CurrentWeather {
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
  uv_index?: number;
  location: WeatherLocation;
  timestamp: string;
}

interface WeatherForecastPoint {
  time: string;
  temperature: number;
  humidity: number;
  rain_probability: number;
  weather_main: string;
}

interface WeatherAlert {
  type: string;
  severity: string;
  message: string;
  valid_from: string;
  valid_until: string;
}

interface WeatherData {
  current: CurrentWeather;
  forecast: WeatherForecastPoint[];
  alerts: WeatherAlert[];
  cached_at: string;
  cache_expires: string;
}

interface WeatherWidgetProps {
  deviceId: string;
  className?: string;
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({ deviceId, className = "" }) => {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  useEffect(() => {
    fetchWeatherData();
  }, [deviceId]);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/katara/weather/${deviceId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          setError("Appareil non trouvé ou localisation non configurée");
        } else if (response.status === 422) {
          setError("Coordonnées de l'appareil invalides");
        } else if (response.status === 429) {
          setError("Limite de taux d'API météo dépassée");
        } else if (response.status === 502) {
          setError("Service météo indisponible");
        } else {
          setError("Erreur lors de la récupération des données météo");
        }
        return;
      }

      const data = await response.json();
      setWeatherData(data);
      setLastUpdated(new Date().toLocaleTimeString('fr-FR'));
      
    } catch (err) {
      console.error('Error fetching weather data:', err);
      setError("Erreur de connexion au service météo");
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (weatherMain: string, size: number = 24) => {
    switch (weatherMain.toLowerCase()) {
      case 'clear':
        return <Sun size={size} className="text-yellow-500" />;
      case 'clouds':
        return <Cloud size={size} className="text-gray-500" />;
      case 'rain':
      case 'drizzle':
        return <CloudRain size={size} className="text-blue-500" />;
      case 'thunderstorm':
        return <CloudRain size={size} className="text-purple-500" />;
      case 'snow':
        return <Cloud size={size} className="text-blue-300" />;
      default:
        return <Cloud size={size} className="text-gray-400" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (timeString: string) => {
    return new Date(timeString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getWindDirection = (degrees: number) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertTriangle size={20} />
          <span className="font-medium">Erreur météo</span>
        </div>
        <p className="text-sm text-gray-600 mt-2">{error}</p>
        <button
          onClick={fetchWeatherData}
          className="mt-3 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
        >
          Réessayer
        </button>
      </div>
    );
  }

  if (!weatherData) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <p className="text-gray-500">Aucune donnée météo disponible</p>
      </div>
    );
  }

  const { current, forecast, alerts } = weatherData;

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Météo</h3>
        <div className="flex items-center space-x-2">
          {getWeatherIcon(current.weather_main, 20)}
          <span className="text-sm text-gray-500">
            Mis à jour: {lastUpdated}
          </span>
        </div>
      </div>

      {/* Current Weather */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="flex items-center space-x-4">
          <div className="text-4xl font-bold text-gray-800">
            {Math.round(current.temperature)}°C
          </div>
          <div>
            <p className="text-gray-600 capitalize">{current.weather_description}</p>
            <p className="text-sm text-gray-500">
              Ressenti: {Math.round(current.temperature)}°C
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center space-x-1">
            <Droplets size={16} className="text-blue-500" />
            <span>{current.humidity}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <Wind size={16} className="text-gray-500" />
            <span>{current.wind_speed} m/s {getWindDirection(current.wind_direction)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Thermometer size={16} className="text-red-500" />
            <span>{current.pressure} hPa</span>
          </div>
          <div className="flex items-center space-x-1">
            <Eye size={16} className="text-gray-500" />
            <span>{current.visibility} km</span>
          </div>
        </div>
      </div>

      {/* Rainfall Information */}
      {(current.rainfall_1h > 0 || current.rainfall_24h > 0) && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
          <p className="text-sm font-medium text-blue-800">
            💧 Pluie: {current.rainfall_1h}mm (1h) / {current.rainfall_24h}mm (24h)
          </p>
        </div>
      )}

      {/* Weather Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2 mb-6">
          <h4 className="font-medium text-gray-700 flex items-center">
            <AlertTriangle size={16} className="text-orange-500 mr-1" />
            Alertes météo
          </h4>
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`p-3 rounded border text-sm ${getSeverityColor(alert.severity)}`}
            >
              <p className="font-medium">{alert.message}</p>
              <p className="text-xs mt-1 opacity-75">
                {formatDate(alert.valid_from)} - {formatDate(alert.valid_until)}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Forecast */}
      <div>
        <h4 className="font-medium text-gray-700 mb-3">Prévisions 24h</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {forecast.slice(0, 4).map((point, index) => (
            <div key={index} className="text-center p-3 bg-gray-50 rounded">
              <p className="text-xs text-gray-500 mb-1">
                {formatTime(point.time)}
              </p>
              <div className="flex justify-center mb-2">
                {getWeatherIcon(point.weather_main, 20)}
              </div>
              <p className="font-medium text-gray-800">
                {Math.round(point.temperature)}°C
              </p>
              {point.rain_probability > 0 && (
                <p className="text-xs text-blue-600">
                  💧 {point.rain_probability}%
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Cache Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Données météo cached: {new Date(weatherData.cached_at).toLocaleTimeString('fr-FR')} | 
          Expire: {new Date(weatherData.cache_expires).toLocaleTimeString('fr-FR')}
        </p>
      </div>
    </div>
  );
};

export default WeatherWidget;
