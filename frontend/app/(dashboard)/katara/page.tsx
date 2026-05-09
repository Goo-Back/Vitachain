"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import DashboardStats from "@/components/katara/DashboardStats";
import DeviceList from "@/components/katara/DeviceList";
import AlertPanel from "@/components/katara/AlertPanel";
import TelemetryCharts from "@/components/katara/TelemetryCharts";
import { useKataraDashboard, DashboardDevice } from "@/hooks/useKataraDashboard";

export default function KataraDashboard() {
  const {
    data,
    loading,
    error,
    connectionStatus,
    selectedDeviceId,
    setSelectedDeviceId,
    refresh,
    markAlertAsRead,
    markAllAlertsAsRead,
  } = useKataraDashboard({
    autoRefresh: true,
    refreshInterval: 30000, // 30 seconds
    enableRealtime: true,
  });

  const handleDeviceSelect = (device: DashboardDevice) => {
    setSelectedDeviceId(device.device_id);
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'bg-green-500';
      case 'reconnecting':
        return 'bg-yellow-500';
      case 'disconnected':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'En ligne';
      case 'reconnecting':
        return 'Reconnexion...';
      case 'disconnected':
        return 'Hors ligne';
      default:
        return 'Inconnu';
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Link href="/" className="text-2xl font-bold text-green-600">🌱 VitaChain</Link>
                <span className="ml-4 text-gray-500">KATARA Dashboard</span>
              </div>
              <nav className="flex space-x-4">
                <Link href="/dashboard/katara" className="text-green-600 font-medium">
                  IoT
                </Link>
                <Link href="/profile" className="text-gray-700 hover:text-green-600">
                  Profil
                </Link>
                <Link href="/auth/logout" className="text-gray-700 hover:text-green-600">
                  Déconnexion
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Error Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <div className="text-red-400 text-2xl">⚠️</div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-red-800">Erreur de chargement</h3>
                <p className="mt-2 text-red-700">{error}</p>
                <button
                  onClick={refresh}
                  className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
                >
                  Réessayer
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-green-600">🌱 VitaChain</Link>
              <span className="ml-4 text-gray-500">KATARA Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${getConnectionStatusColor()}`}></div>
                <span className="text-sm text-gray-600">{getConnectionStatusText()}</span>
              </div>
              
              {/* Refresh Button */}
              <button
                onClick={refresh}
                disabled={loading}
                className="p-2 text-gray-600 hover:text-green-600 transition-colors disabled:opacity-50"
                title="Actualiser"
              >
                🔄
              </button>
              
              <nav className="flex space-x-4">
                <Link href="/dashboard/katara" className="text-green-600 font-medium">
                  IoT
                </Link>
                <Link href="/profile" className="text-gray-700 hover:text-green-600">
                  Profil
                </Link>
                <Link href="/auth/logout" className="text-gray-700 hover:text-green-600">
                  Déconnexion
                </Link>
              </nav>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord KATARA</h1>
          <p className="mt-2 text-gray-600">Agriculture intelligente avec IoT</p>
        </div>

        {loading && !data ? (
          // Loading skeleton
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
                  <div className="h-8 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-lg shadow animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-12 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : data ? (
          // Dashboard Content
          <div className="space-y-8">
            {/* Stats Cards */}
            <DashboardStats stats={data.summary_stats} loading={loading} />

            {/* Device and Alerts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Device List */}
              <DeviceList
                devices={data.devices}
                loading={loading}
                onDeviceSelect={handleDeviceSelect}
              />

              {/* Alert Panel */}
              <AlertPanel
                alerts={data.alerts}
                loading={loading}
                onAlertRead={markAlertAsRead}
                onMarkAllRead={markAllAlertsAsRead}
              />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 xl:grid-cols-1 gap-8">
              <TelemetryCharts
                trendData={data.trend_data}
                loading={loading}
                selectedDeviceId={selectedDeviceId || undefined}
              />
            </div>

            {/* Selected Device Info */}
            {selectedDeviceId && (
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Détails de l'appareil sélectionné</h2>
                  <button
                    onClick={() => setSelectedDeviceId(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>
                <div className="text-sm text-gray-600">
                  Affichage des données pour: <code className="bg-gray-100 px-2 py-1 rounded">{selectedDeviceId}</code>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Last Updated */}
        {data && (
          <div className="mt-8 text-center text-sm text-gray-500">
            Dernière mise à jour: {new Date().toLocaleString('fr-FR')}
          </div>
        )}
      </main>
    </div>
  );
}
