"use client";

import { useState } from "react";
import Link from "next/link";
import { useTelemetryHistory } from "./hooks/useTelemetryHistory";
import DateRangeSelector from "./components/DateRangeSelector";
import DeviceSelector from "./components/DeviceSelector";
import TrendCharts from "./components/TrendCharts";
import StatisticsPanel from "./components/StatisticsPanel";
import AlertPatterns from "./components/AlertPatterns";
import ExportControls from "./components/ExportControls";

export default function KataraHistory() {
  const {
    data,
    isLoading,
    error,
    params,
    selectedDeviceId,
    setSelectedDeviceId,
    updateParams,
    setDateRange,
    refetch,
    exportToCSV,
    exportToJSON,
  } = useTelemetryHistory({
    autoRefresh: false, // History data doesn't need auto-refresh
  });

  const handleDateRangeChange = (startDate: string, endDate: string) => {
    updateParams({
      start_date: startDate,
      end_date: endDate,
    });
  };

  const handleAggregationChange = (aggregation: "hour" | "day") => {
    updateParams({ aggregation });
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
                <span className="ml-4 text-gray-500">KATARA History</span>
              </div>
              <nav className="flex space-x-4">
                <Link href="/dashboard/katara" className="text-green-600 font-medium">
                  Dashboard
                </Link>
                <Link href="/dashboard/katara/history" className="text-green-600 font-medium">
                  History
                </Link>
                <Link href="/profile" className="text-gray-700 hover:text-green-600">
                  Profile
                </Link>
                <Link href="/auth/logout" className="text-gray-700 hover:text-green-600">
                  Logout
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
                <h3 className="text-lg font-medium text-red-800">Error loading history data</h3>
                <p className="mt-2 text-red-700">{error.message}</p>
                <button
                  onClick={() => refetch()}
                  className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
                >
                  Retry
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
              <span className="ml-4 text-gray-500">KATARA History</span>
            </div>
            <nav className="flex space-x-4">
              <Link href="/dashboard/katara" className="text-green-600 font-medium">
                Dashboard
              </Link>
              <Link href="/dashboard/katara/history" className="text-green-600 font-medium">
                History
              </Link>
              <Link href="/profile" className="text-gray-700 hover:text-green-600">
                Profile
              </Link>
              <Link href="/auth/logout" className="text-gray-700 hover:text-green-600">
                Logout
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Telemetry History</h1>
          <p className="mt-2 text-gray-600">
            Analyze historical sensor data, trends, and patterns for your agricultural devices.
          </p>
        </div>

        {/* Controls Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Date Range Selector */}
            <div className="lg:col-span-2">
              <DateRangeSelector
                startDate={params.start_date}
                endDate={params.end_date}
                onDateRangeChange={handleDateRangeChange}
                onQuickSelect={setDateRange}
                isLoading={isLoading}
              />
            </div>

            {/* Device Selector */}
            <div>
              <DeviceSelector
                selectedDeviceId={selectedDeviceId}
                onDeviceSelect={setSelectedDeviceId}
                devices={data?.chart_data || []}
                isLoading={isLoading}
              />
            </div>

            {/* Aggregation & Export */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Aggregation Level
                </label>
                <select
                  value={params.aggregation}
                  onChange={(e) => handleAggregationChange(e.target.value as "hour" | "day")}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                  disabled={isLoading}
                >
                  <option value="hour">Hourly</option>
                  <option value="day">Daily</option>
                </select>
              </div>

              <ExportControls
                onExportCSV={exportToCSV}
                onExportJSON={exportToJSON}
                isLoading={isLoading || !data}
              />
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            <span className="ml-4 text-gray-600">Loading history data...</span>
          </div>
        )}

        {/* Data Display */}
        {!isLoading && data && (
          <div className="space-y-8">
            {/* Period Info */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Period</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Start Date:</span>
                  <p className="font-medium">{new Date(data.period_info.start_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-gray-500">End Date:</span>
                  <p className="font-medium">{new Date(data.period_info.end_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-gray-500">Total Readings:</span>
                  <p className="font-medium">{data.period_info.total_readings.toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-gray-500">Devices:</span>
                  <p className="font-medium">{data.period_info.devices_analyzed}</p>
                </div>
              </div>
            </div>

            {/* Trend Charts */}
            <TrendCharts data={data} />

            {/* Statistics Panel */}
            <StatisticsPanel 
              dailyStats={data.daily_stats} 
              trendAnalysis={data.trend_analysis}
            />

            {/* Alert Patterns */}
            <AlertPatterns alertPatterns={data.alert_patterns} />
          </div>
        )}

        {/* No Data State */}
        {!isLoading && (!data || data.chart_data.length === 0) && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
            <p className="text-gray-600">
              No telemetry data found for the selected period and filters.
              Try adjusting the date range or check your device connectivity.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
