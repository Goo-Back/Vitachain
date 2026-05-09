"use client";

import React from 'react';
import { useKataraNDVI, NDVIData } from '@/hooks/useKataraNDVI';

interface NDVIDisplayProps {
  deviceId: string;
  showHistory?: boolean;
}

export default function NDVIDisplay({ deviceId, showHistory = false }: NDVIDisplayProps) {
  const { ndviData, loading, error, fetchNDVIData } = useKataraNDVI();

  React.useEffect(() => {
    if (deviceId) {
      fetchNDVIData(deviceId);
    }
  }, [deviceId, fetchNDVIData]);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">NDVI - Végétation</h3>
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
        <h3 className="text-lg font-semibold mb-4">NDVI - Végétation</h3>
        <div className="text-red-600">
          Erreur: {error}
        </div>
      </div>
    );
  }

  if (!ndviData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">NDVI - Végétation</h3>
        <div className="text-gray-500 text-center py-4">
          Aucune donnée NDVI disponible
        </div>
      </div>
    );
  }

  const getNDVIStatus = (value: number) => {
    if (value < 0.2) return { status: 'Sol nu ou végétation morte', color: 'text-red-600', bgColor: 'bg-red-100' };
    if (value < 0.4) return { status: 'Végétation clairsemée', color: 'text-orange-600', bgColor: 'bg-orange-100' };
    if (value < 0.6) return { status: 'Végétation modérée', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    if (value < 0.8) return { status: 'Végétation saine', color: 'text-green-600', bgColor: 'bg-green-100' };
    return { status: 'Végétation très dense', color: 'text-emerald-600', bgColor: 'bg-emerald-100' };
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return '📈';
      case 'decreasing':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendText = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return 'Amélioration';
      case 'decreasing':
        return 'Dégradation';
      default:
        return 'Stable';
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

  const currentNDVI = ndviData.current.ndvi_value;
  const ndviStatus = getNDVIStatus(currentNDVI);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">NDVI - Végétation</h3>
        <button
          onClick={() => fetchNDVIData(deviceId)}
          className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Actualiser
        </button>
      </div>

      {/* Current NDVI Value */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {currentNDVI.toFixed(3)}
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${ndviStatus.bgColor} ${ndviStatus.color}`}>
                {ndviStatus.status}
              </div>
            </div>
            <div className="text-left">
              <div className="text-sm text-gray-600">
                📍 {ndviData.current.location.lat.toFixed(4)}, {ndviData.current.location.lng.toFixed(4)}
              </div>
              <div className="text-xs text-gray-500">
                Mis à jour: {new Date(ndviData.cached_at).toLocaleDateString('fr-FR')}
              </div>
            </div>
          </div>
        </div>

        {/* NDVI Scale */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>0.0</span>
            <span>Échelle NDVI</span>
            <span>1.0</span>
          </div>
          <div className="w-full h-6 bg-gradient-to-r from-red-500 via-yellow-500 via-green-500 to-emerald-500 rounded-full relative">
            <div 
              className="absolute top-1/2 transform -translate-y-1/2 w-4 h-4 bg-white border-2 border-gray-800 rounded-full shadow-md"
              style={{ left: `${currentNDVI * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Sol nu</span>
            <span>Stress</span>
            <span>Sain</span>
            <span>Très sain</span>
          </div>
        </div>

        {/* Trend Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Tendance</h4>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{getTrendIcon(ndviData.trend.direction)}</span>
              <div>
                <div className="font-medium">{getTrendText(ndviData.trend.direction)}</div>
                <div className="text-sm text-gray-600">
                  {ndviData.trend.change_rate > 0 ? '+' : ''}{ndviData.trend.change_rate.toFixed(3)} sur {ndviData.trend.period_days} jours
                </div>
              </div>
            </div>
            <div className="text-right text-sm text-gray-500">
              <div>Période: {ndviData.trend.period_days} jours</div>
              <div>Taux: {Math.abs(ndviData.trend.change_rate * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* NDVI Alerts */}
      {ndviData.alerts.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Alertes NDVI</h4>
          <div className="space-y-2">
            {ndviData.alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${getAlertColor(alert.severity)}`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">🌿</span>
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

      {/* Historical Data */}
      {showHistory && ndviData.historical.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Historique NDVI</h4>
          <div className="max-h-48 overflow-y-auto">
            <div className="space-y-1">
              {ndviData.historical.slice(0, 20).map((point, index) => {
                const status = getNDVIStatus(point.ndvi_value);
                return (
                  <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${status.bgColor}`}></div>
                      <span className="text-sm">
                        {new Date(point.timestamp).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className={`font-medium ${status.color}`}>
                        {point.ndvi_value.toFixed(3)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {status.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* NDVI Image (if available) */}
      {ndviData.current.image_url && (
        <div className="mt-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Image Satellite</h4>
          <div className="relative">
            <img 
              src={ndviData.current.image_url} 
              alt="NDVI Satellite Image"
              className="w-full h-48 object-cover rounded-lg"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
            <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded text-xs font-medium">
              NDVI: {currentNDVI.toFixed(3)}
            </div>
          </div>
        </div>
      )}

      {/* NDVI Information */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">Qu'est-ce que le NDVI?</h4>
        <div className="text-xs text-blue-800 space-y-1">
          <p>Le NDVI (Normalized Difference Vegetation Index) mesure la santé de la végétation.</p>
          <p>• Valeurs proches de 1: Végétation très saine et dense</p>
          <p>• Valeurs autour de 0.5: Végétation modérément saine</p>
          <p>• Valeurs proches de 0: Sol nu ou végétation morte</p>
          <p>• Valeurs négatives: Eau, neige ou surfaces artificielles</p>
        </div>
      </div>
    </div>
  );
}
