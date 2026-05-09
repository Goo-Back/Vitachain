"use client";

import React, { useState } from 'react';
import { useKataraHistory, HistoryParams } from '@/hooks/useKataraHistory';

interface HistoryAnalysisProps {
  deviceId?: string;
}

export default function HistoryAnalysis({ deviceId }: HistoryAnalysisProps) {
  const { historyData, loading, error, fetchHistoryData } = useKataraHistory();
  const [showFilters, setShowFilters] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedDevice, setSelectedDevice] = useState(deviceId || '');
  const [aggregation, setAggregation] = useState<'hour' | 'day'>('day');

  const handleFetchHistory = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!startDate || !endDate) {
      return;
    }

    const params: HistoryParams = {
      start_date: new Date(startDate),
      end_date: new Date(endDate),
      aggregation,
      device_id: selectedDevice || undefined,
    };

    fetchHistoryData(params);
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return '📈';
      case 'decreasing':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendText = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'En augmentation';
      case 'decreasing':
        return 'En diminution';
      default:
        return 'Stable';
    }
  };

  const getQualityColor = (completeness: number) => {
    if (completeness >= 90) return 'text-green-600';
    if (completeness >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Analyse Historique</h3>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          {showFilters ? 'Masquer les Filtres' : 'Afficher les Filtres'}
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-6 p-4 border rounded-lg bg-gray-50">
          <h4 className="text-lg font-medium mb-4">Filtres d'Analyse</h4>
          <form onSubmit={handleFetchHistory} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date de Début
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date de Fin
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Appareil (optionnel)
                </label>
                <input
                  type="text"
                  value={selectedDevice}
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  placeholder="ID de l'appareil"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Niveau d'Agrégation
                </label>
                <select
                  value={aggregation}
                  onChange={(e) => setAggregation(e.target.value as 'hour' | 'day')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="hour">Heure</option>
                  <option value="day">Jour</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Analyse en cours...' : 'Lancer l\'Analyse'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowFilters(false);
                  setStartDate('');
                  setEndDate('');
                  setSelectedDevice('');
                  setAggregation('day');
                }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Réinitialiser
              </button>
            </div>
          </form>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          Erreur: {error}
        </div>
      )}

      {loading && (
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-6 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      )}

      {historyData && (
        <div className="space-y-6">
          {/* Period Information */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="text-md font-medium text-blue-900 mb-2">Période d'Analyse</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-blue-600">Début</div>
                <div className="font-medium">{new Date(historyData.period_info.start_date).toLocaleDateString('fr-FR')}</div>
              </div>
              <div>
                <div className="text-blue-600">Fin</div>
                <div className="font-medium">{new Date(historyData.period_info.end_date).toLocaleDateString('fr-FR')}</div>
              </div>
              <div>
                <div className="text-blue-600">Durée</div>
                <div className="font-medium">{historyData.period_info.total_days} jours</div>
              </div>
              <div>
                <div className="text-blue-600">Agrégation</div>
                <div className="font-medium">{historyData.period_info.aggregation_level === 'hour' ? 'Horaire' : 'Quotidienne'}</div>
              </div>
            </div>
          </div>

          {/* Statistics */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Statistiques</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-900 mb-2">Température</h5>
                <div className="space-y-1 text-sm">
                  <div>Moyenne: {historyData.statistics.avg_temperature?.toFixed(1)}°C</div>
                  <div>Min: {historyData.statistics.min_temperature?.toFixed(1)}°C</div>
                  <div>Max: {historyData.statistics.max_temperature?.toFixed(1)}°C</div>
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-900 mb-2">Humidité</h5>
                <div className="space-y-1 text-sm">
                  <div>Moyenne: {historyData.statistics.avg_humidity?.toFixed(1)}%</div>
                  <div>Min: {historyData.statistics.min_humidity?.toFixed(1)}%</div>
                  <div>Max: {historyData.statistics.max_humidity?.toFixed(1)}%</div>
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-900 mb-2">NDVI</h5>
                <div className="space-y-1 text-sm">
                  <div>Moyenne: {historyData.statistics.avg_ndvi?.toFixed(3)}</div>
                  <div>Min: {historyData.statistics.min_ndvi?.toFixed(3)}</div>
                  <div>Max: {historyData.statistics.max_ndvi?.toFixed(3)}</div>
                </div>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-sm">
                <div>Total des lectures: {historyData.statistics.total_readings}</div>
                <div>Points de données par jour: {historyData.statistics.data_points_per_day}</div>
              </div>
            </div>
          </div>

          {/* Trends */}
          {historyData.trends.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-3">Tendances</h4>
              <div className="space-y-2">
                {historyData.trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getTrendIcon(trend.trend)}</span>
                      <div>
                        <div className="font-medium capitalize">{trend.parameter}</div>
                        <div className="text-sm text-gray-600">{getTrendText(trend.trend)}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">
                        {trend.change_rate > 0 ? '+' : ''}{trend.change_rate.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-500">
                        Confiance: {(trend.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alert Patterns */}
          {historyData.alert_patterns.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-3">Schémas d'Alertes</h4>
              <div className="space-y-3">
                {historyData.alert_patterns.map((pattern, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{pattern.alert_type}</div>
                      <div className="text-sm text-gray-600">
                        Fréquence: {pattern.frequency} fois
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">
                      Pics d'activité: {pattern.peak_hours.join(', ')}h
                    </div>
                    {pattern.correlation_with_weather && (
                      <div className="text-sm text-blue-600 mt-1">
                        Corrélation météo: {pattern.correlation_with_weather}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Quality */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Qualité des Données</h4>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="font-medium">Complétude</div>
                <div className={`font-bold ${getQualityColor(historyData.data_quality.completeness)}`}>
                  {historyData.data_quality.completeness.toFixed(1)}%
                </div>
              </div>
              
              {historyData.data_quality.gaps.length > 0 && (
                <div>
                  <div className="font-medium text-sm mb-2">Périodes Manquantes:</div>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {historyData.data_quality.gaps.map((gap, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        {new Date(gap.start).toLocaleDateString('fr-FR')} - {new Date(gap.end).toLocaleDateString('fr-FR')} 
                        ({gap.duration_hours}h)
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chart Data Summary */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Résumé des Données</h4>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">
                <div>Points de données: {historyData.chart_data.length}</div>
                <div>Période: {new Date(historyData.period_info.start_date).toLocaleDateString('fr-FR')} - {new Date(historyData.period_info.end_date).toLocaleDateString('fr-FR')}</div>
              </div>
              {historyData.chart_data.length > 0 && (
                <div className="mt-3 text-sm">
                  <div className="font-medium mb-1">Premier et dernier points:</div>
                  <div>Début: {new Date(historyData.chart_data[0].timestamp).toLocaleString('fr-FR')}</div>
                  <div>Fin: {new Date(historyData.chart_data[historyData.chart_data.length - 1].timestamp).toLocaleString('fr-FR')}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {!historyData && !loading && !error && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📊</div>
          <p>Aucune donnée historique disponible</p>
          <p className="text-sm mt-2">Sélectionnez une période et lancez l'analyse pour voir les tendances</p>
        </div>
      )}
    </div>
  );
}
