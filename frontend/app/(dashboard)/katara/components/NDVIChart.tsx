"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from "recharts";
import { Calendar, Download, TrendingUp, TrendingDown } from "lucide-react";

interface NDVIHistoryPoint {
  id: string;
  date: string;
  ndvi_value: number;
  ndvi_trend: string;
  data_quality: string;
  cloud_cover: number;
  acquisition_date: string;
  imagery_url: string;
}

interface NDVIChartProps {
  deviceId: string;
  className?: string;
}

interface ChartDataPoint {
  date: string;
  ndvi_value: number;
  trend: string;
  quality: string;
}

export default function NDVIChart({ deviceId, className }: NDVIChartProps) {
  const [historyData, setHistoryData] = useState<NDVIHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [daysRange, setDaysRange] = useState("30");
  const [chartType, setChartType] = useState<"line" | "area">("line");

  useEffect(() => {
    fetchHistoryData();
  }, [deviceId, daysRange]);

  const fetchHistoryData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/katara/ndvi/${deviceId}/history?days=${daysRange}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch NDVI history: ${response.statusText}`);
      }

      const data = await response.json();
      setHistoryData(data.history || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getChartData = (): ChartDataPoint[] => {
    return historyData.map(point => ({
      date: new Date(point.date).toLocaleDateString("fr-MA", { month: "short", day: "numeric" }),
      ndvi_value: point.ndvi_value,
      trend: point.ndvi_trend,
      quality: point.data_quality
    })).reverse(); // Reverse to show chronological order
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "improving":
        return "#10b981"; // green
      case "declining":
        return "#ef4444"; // red
      case "stable":
        return "#3b82f6"; // blue
      default:
        return "#6b7280"; // gray
    }
  };

  const getQualityOpacity = (quality: string) => {
    switch (quality) {
      case "excellent":
        return 1.0;
      case "good":
        return 0.8;
      case "fair":
        return 0.6;
      case "poor":
        return 0.4;
      default:
        return 0.5;
    }
  };

  const calculateStatistics = () => {
    if (historyData.length === 0) return null;

    const values = historyData.map(d => d.ndvi_value);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Calculate trend
    if (values.length >= 2) {
      const recent = values.slice(-7); // Last 7 days
      const earlier = values.slice(-14, -7); // Previous 7 days
      if (recent.length >= 3 && earlier.length >= 3) {
        const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
        const earlierAvg = earlier.reduce((a, b) => a + b, 0) / earlier.length;
        const trend = recentAvg - earlierAvg;
        
        return {
          avg,
          min,
          max,
          trend,
          trendDirection: trend > 0.01 ? "improving" : trend < -0.01 ? "declining" : "stable"
        };
      }
    }

    return { avg, min, max, trend: 0, trendDirection: "stable" };
  };

  const exportData = () => {
    const csvContent = [
      ["Date", "NDVI Value", "Trend", "Data Quality", "Cloud Cover", "Acquisition Date"],
      ...historyData.map(point => [
        point.date,
        point.ndvi_value.toFixed(3),
        point.ndvi_trend,
        point.data_quality,
        point.cloud_cover.toFixed(1),
        point.acquisition_date
      ])
    ].map(row => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ndvi-history-${deviceId}-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("fr-MA", {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          <p className="text-sm">
            <span className="font-medium">NDVI:</span> {data.ndvi_value.toFixed(3)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Trend:</span> {data.trend}
          </p>
          <p className="text-sm">
            <span className="font-medium">Quality:</span> {data.quality}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            NDVI Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            NDVI Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-600 mb-4">Error: {error}</div>
            <Button onClick={fetchHistoryData} variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = getChartData();
  const stats = calculateStatistics();

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            NDVI Trend Analysis
          </span>
          <div className="flex items-center gap-2">
            <Select value={daysRange} onValueChange={setDaysRange}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">7 days</SelectItem>
                <SelectItem value="30">30 days</SelectItem>
                <SelectItem value="60">60 days</SelectItem>
                <SelectItem value="90">90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={() => setChartType(chartType === "line" ? "area" : "line")}
              variant="outline"
              size="sm"
            >
              {chartType === "line" ? "Area" : "Line"}
            </Button>
            <Button onClick={exportData} variant="outline" size="sm">
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Statistics Summary */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.avg.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Average NDVI</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.max.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Maximum NDVI</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {stats.min.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Minimum NDVI</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1">
                {stats.trendDirection === "improving" ? (
                  <TrendingUp className="h-5 w-5 text-green-600" />
                ) : stats.trendDirection === "declining" ? (
                  <TrendingDown className="h-5 w-5 text-red-600" />
                ) : (
                  <div className="h-5 w-5 bg-blue-600 rounded-full" />
                )}
                <span className="text-lg font-bold capitalize">{stats.trendDirection}</span>
              </div>
              <div className="text-sm text-gray-600">Overall Trend</div>
            </div>
          </div>
        )}

        {/* Chart */}
        {chartData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === "line" ? (
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    domain={[-0.1, 0.9]}
                    tick={{ fontSize: 12 }}
                    label={{ value: "NDVI Value", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="ndvi_value"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ fill: "#10b981", r: 4 }}
                    activeDot={{ r: 6 }}
                    name="NDVI Value"
                  />
                </LineChart>
              ) : (
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    domain={[-0.1, 0.9]}
                    tick={{ fontSize: 12 }}
                    label={{ value: "NDVI Value", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="ndvi_value"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.3}
                    strokeWidth={2}
                    name="NDVI Value"
                  />
                </AreaChart>
              )}
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            No historical NDVI data available for the selected period
          </div>
        )}

        {/* NDVI Health Zones */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-600 mb-2">NDVI Health Zones</h4>
          <div className="grid grid-cols-4 gap-2 text-xs">
            <div className="bg-green-100 p-2 rounded text-center">
              <div className="font-medium text-green-800">Healthy</div>
              <div className="text-green-600">NDVI ≥ 0.4</div>
            </div>
            <div className="bg-yellow-100 p-2 rounded text-center">
              <div className="font-medium text-yellow-800">Moderate</div>
              <div className="text-yellow-600">0.3 ≤ NDVI &lt; 0.4</div>
            </div>
            <div className="bg-orange-100 p-2 rounded text-center">
              <div className="font-medium text-orange-800">Poor</div>
              <div className="text-orange-600">0.2 ≤ NDVI &lt; 0.3</div>
            </div>
            <div className="bg-red-100 p-2 rounded text-center">
              <div className="font-medium text-red-800">Critical</div>
              <div className="text-red-600">NDVI &lt; 0.2</div>
            </div>
          </div>
        </div>

        {/* Data Quality Legend */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-600 mb-2">Data Quality</h4>
          <div className="grid grid-cols-4 gap-2 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded-full opacity-100"></div>
              <span>Excellent</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-blue-500 rounded-full opacity-80"></div>
              <span>Good</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-yellow-500 rounded-full opacity-60"></div>
              <span>Fair</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-500 rounded-full opacity-40"></div>
              <span>Poor</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
