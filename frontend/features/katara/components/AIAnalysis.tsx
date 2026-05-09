"use client";

import React, { useState } from 'react';
import { useKataraAI, AIAnalysisRequest, AIRecommendation } from '@/hooks/useKataraAI';

interface AIAnalysisProps {
  deviceId: string;
}

export default function AIAnalysis({ deviceId }: AIAnalysisProps) {
  const { 
    analysisJobs, 
    recommendations, 
    analysisResults, 
    loading, 
    error, 
    startAnalysis, 
    getRecommendations, 
    checkJobStatus, 
    cancelAnalysis 
  } = useKataraAI();

  const [showAnalysisForm, setShowAnalysisForm] = useState(false);
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<AIAnalysisRequest['analysis_type']>('crop_health');
  const [timeRange, setTimeRange] = useState(7);
  const [includeWeather, setIncludeWeather] = useState(true);
  const [includeNDVI, setIncludeNDVI] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);

  React.useEffect(() => {
    if (deviceId) {
      getRecommendations(deviceId);
    }
  }, [deviceId, getRecommendations]);

  React.useEffect(() => {
    // Poll for job status updates
    const interval = setInterval(() => {
      analysisJobs
        .filter(job => job.status === 'pending' || job.status === 'running')
        .forEach(job => {
          checkJobStatus(job.analysis_id);
        });
    }, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, [analysisJobs, checkJobStatus]);

  const handleStartAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    try {
      const request: AIAnalysisRequest = {
        analysis_type: selectedAnalysisType,
        time_range_days: timeRange,
        include_weather: includeWeather,
        include_ndvi: includeNDVI,
      };

      await startAnalysis(deviceId, request);
      setShowAnalysisForm(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Analysis failed');
    }
  };

  const getAnalysisTypeLabel = (type: AIAnalysisRequest['analysis_type']) => {
    switch (type) {
      case 'crop_health':
        return 'Santé des Cultures';
      case 'irrigation':
        return 'Analyse d\'Irrigation';
      case 'yield_prediction':
        return 'Prédiction de Rendement';
      case 'pest_risk':
        return 'Analyse de Risque Parasitaire';
      default:
        return type;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
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
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Analyse IA</h3>
        <button
          onClick={() => setShowAnalysisForm(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          + Nouvelle Analyse
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          Erreur: {error}
        </div>
      )}

      {formError && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {formError}
        </div>
      )}

      {/* Analysis Form */}
      {showAnalysisForm && (
        <div className="mb-6 p-4 border rounded-lg bg-gray-50">
          <h4 className="text-lg font-medium mb-4">Démarrer une Analyse IA</h4>
          <form onSubmit={handleStartAnalysis} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type d'Analyse
              </label>
              <select
                value={selectedAnalysisType}
                onChange={(e) => setSelectedAnalysisType(e.target.value as AIAnalysisRequest['analysis_type'])}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="crop_health">Santé des Cultures</option>
                <option value="irrigation">Analyse d'Irrigation</option>
                <option value="yield_prediction">Prédiction de Rendement</option>
                <option value="pest_risk">Analyse de Risque Parasitaire</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Période d'Analyse (jours)
              </label>
              <input
                type="number"
                min="1"
                max="30"
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={includeWeather}
                  onChange={(e) => setIncludeWeather(e.target.checked)}
                  className="rounded text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">Inclure les données météo</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={includeNDVI}
                  onChange={(e) => setIncludeNDVI(e.target.checked)}
                  className="rounded text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">Inclure les données NDVI</span>
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Analyse en cours...' : 'Démarrer l\'Analyse'}
              </button>
              <button
                type="button"
                onClick={() => setShowAnalysisForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Active Analysis Jobs */}
      {analysisJobs.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Analyses en Cours</h4>
          <div className="space-y-2">
            {analysisJobs.map((job) => (
              <div key={job.analysis_id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(job.status)}`}>
                    {job.status === 'pending' ? 'En attente' : 
                     job.status === 'running' ? 'En cours' :
                     job.status === 'completed' ? 'Terminée' : 'Échouée'}
                  </span>
                  <div>
                    <div className="font-medium">{getAnalysisTypeLabel(job.analysis_type as any)}</div>
                    <div className="text-sm text-gray-500">
                      ID: {job.analysis_id.slice(-8)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {job.status === 'pending' || job.status === 'running' ? (
                    <button
                      onClick={() => cancelAnalysis(job.analysis_id)}
                      className="text-sm text-red-600 hover:text-red-800 transition-colors"
                    >
                      Annuler
                    </button>
                  ) : null}
                  <button
                    onClick={() => checkJobStatus(job.analysis_id)}
                    className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    Actualiser
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Recommandations IA</h4>
          <div className="space-y-3">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className={`p-4 rounded-lg border ${getPriorityColor(rec.priority)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-semibold text-lg">{rec.title}</div>
                    <div className="text-sm opacity-75">
                      {getAnalysisTypeLabel(rec.analysis_type as any)} • 
                      Confiance: {(rec.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(rec.priority)}`}>
                    {rec.priority === 'critical' ? 'Critique' :
                     rec.priority === 'high' ? 'Haute' :
                     rec.priority === 'medium' ? 'Moyenne' : 'Faible'}
                  </span>
                </div>
                
                <div className="mb-3">
                  <p className="text-gray-700">{rec.description}</p>
                </div>

                {rec.action_items.length > 0 && (
                  <div>
                    <div className="font-medium text-sm mb-2">Actions recommandées:</div>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {rec.action_items.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-3 text-xs text-gray-500">
                  Créée: {new Date(rec.created_at).toLocaleDateString('fr-FR')}
                  {rec.expires_at && ` • Expire: ${new Date(rec.expires_at).toLocaleDateString('fr-FR')}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Résultats d'Analyse</h4>
          <div className="space-y-4">
            {analysisResults.map((result) => (
              <div key={result.analysis_id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-semibold">{getAnalysisTypeLabel(result.analysis_type as any)}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(result.completed_at || result.created_at).toLocaleDateString('fr-FR')}
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(result.status)}`}>
                    {result.status === 'completed' ? 'Terminée' : 'Échouée'}
                  </span>
                </div>

                {result.status === 'completed' && (
                  <div>
                    <div className="mb-3">
                      <h5 className="font-medium mb-1">Résumé</h5>
                      <p className="text-gray-700">{result.results.summary}</p>
                    </div>

                    {result.results.insights.length > 0 && (
                      <div className="mb-3">
                        <h5 className="font-medium mb-1">Informations Clés</h5>
                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                          {result.results.insights.map((insight, index) => (
                            <li key={index}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.results.risk_factors.length > 0 && (
                      <div className="mb-3">
                        <h5 className="font-medium mb-1">Facteurs de Risque</h5>
                        <div className="space-y-1">
                          {result.results.risk_factors.map((risk, index) => (
                            <div key={index} className={`p-2 rounded text-sm ${getPriorityColor(risk.severity)}`}>
                              <strong>{risk.factor}:</strong> {risk.description}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.results.performance_metrics && (
                      <div>
                        <h5 className="font-medium mb-1">Indicateurs de Performance</h5>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          {result.results.performance_metrics.crop_health_score !== undefined && (
                            <div className="bg-green-50 p-2 rounded">
                              <div className="font-medium text-green-800">Santé des Cultures</div>
                              <div className="text-green-600">{(result.results.performance_metrics.crop_health_score * 100).toFixed(0)}%</div>
                            </div>
                          )}
                          {result.results.performance_metrics.irrigation_efficiency !== undefined && (
                            <div className="bg-blue-50 p-2 rounded">
                              <div className="font-medium text-blue-800">Efficacité d'Irrigation</div>
                              <div className="text-blue-600">{(result.results.performance_metrics.irrigation_efficiency * 100).toFixed(0)}%</div>
                            </div>
                          )}
                          {result.results.performance_metrics.yield_potential !== undefined && (
                            <div className="bg-yellow-50 p-2 rounded">
                              <div className="font-medium text-yellow-800">Potentiel de Rendement</div>
                              <div className="text-yellow-600">{(result.results.performance_metrics.yield_potential * 100).toFixed(0)}%</div>
                            </div>
                          )}
                          {result.results.performance_metrics.pest_risk_level !== undefined && (
                            <div className="bg-red-50 p-2 rounded">
                              <div className="font-medium text-red-800">Niveau de Risque Parasitaire</div>
                              <div className="text-red-600">{(result.results.performance_metrics.pest_risk_level * 100).toFixed(0)}%</div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 && analysisResults.length === 0 && analysisJobs.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🤖</div>
          <p>Aucune analyse IA disponible</p>
          <p className="text-sm mt-2">Démarrez votre première analyse pour obtenir des recommandations intelligentes</p>
        </div>
      )}
    </div>
  );
}
