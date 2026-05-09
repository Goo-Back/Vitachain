"use client";

import React from 'react';

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

interface DashboardAlert {
  id: string;
  type: string;
  severity: AlertSeverity;
  message: string;
  created_at: string;
}

interface AlertsInfo {
  unread_count: number;
  recent_alerts: DashboardAlert[];
}

interface AlertPanelProps {
  alerts: AlertsInfo;
  loading?: boolean;
  onAlertRead?: (alertId: string) => void;
  onMarkAllRead?: () => void;
}

export default function AlertPanel({ alerts, loading = false, onAlertRead, onMarkAllRead }: AlertPanelProps) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Alertes</h2>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-3 border rounded animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: AlertSeverity) => {
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

  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case 'low':
        return 'ℹ️';
      case 'medium':
        return '⚠️';
      case 'high':
        return '🚨';
      case 'critical':
        return '🔥';
      default:
        return '📢';
    }
  };

  const getSeverityText = (severity: AlertSeverity) => {
    switch (severity) {
      case 'low':
        return 'Faible';
      case 'medium':
        return 'Moyenne';
      case 'high':
        return 'Élevée';
      case 'critical':
        return 'Critique';
      default:
        return 'Inconnue';
    }
  };

  const formatAlertTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffMins < 1440) return `Il y a ${Math.floor(diffMins / 60)}h`;
    return `Il y a ${Math.floor(diffMins / 1440)}j`;
  };

  const handleAlertClick = (alert: DashboardAlert) => {
    onAlertRead?.(alert.id);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Alertes</h2>
        <div className="flex items-center space-x-2">
          {alerts.unread_count > 0 && (
            <>
              <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                {alerts.unread_count} non lue{alerts.unread_count > 1 ? 's' : ''}
              </span>
              {onMarkAllRead && (
                <button
                  onClick={onMarkAllRead}
                  className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Tout marquer comme lu
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {alerts.recent_alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">✅</div>
          <p>Aucune alerte</p>
          <p className="text-sm mt-2">Tous les systèmes fonctionnent normalement</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.recent_alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md ${getSeverityColor(alert.severity)}`}
              onClick={() => handleAlertClick(alert)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
                  <span className="font-medium">{alert.message}</span>
                </div>
                <span className="text-xs px-2 py-1 bg-white bg-opacity-60 rounded">
                  {getSeverityText(alert.severity)}
                </span>
              </div>
              
              <div className="flex justify-between items-center text-xs opacity-75">
                <span>Type: {alert.type}</span>
                <span>{formatAlertTime(alert.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {alerts.recent_alerts.length > 0 && alerts.unread_count === 0 && (
        <div className="mt-4 pt-4 border-t text-center text-sm text-gray-500">
          Toutes les alertes ont été lues
        </div>
      )}
    </div>
  );
}
