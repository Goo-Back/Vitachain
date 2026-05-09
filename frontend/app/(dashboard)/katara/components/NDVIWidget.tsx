"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Eye, TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";

interface NDVIData {
  current: {
    ndvi_value: number;
    ndvi_trend: string;
    vegetation_health: string;
    imagery_url: string;
    cloud_cover: number;
    data_quality: string;
    location: {
      lat: number;
      lng: number;
    };
    acquisition_date: string;
    timestamp: string;
  };
  trend: {
    ndvi_30d_avg: number;
    ndvi_7d_avg: number;
    ndvi_change_7d: number;
    trend_direction: string;
    stress_detected: boolean;
  };
  historical: Array<{
    date: string;
    ndvi_value: number;
    data_quality: string;
  }>;
  alerts: Array<{
    type: string;
    severity: string;
    message: string;
  }>;
  cached_at: string;
  cache_expires: string;
}

interface NDVIWidgetProps {
  deviceId: string;
  className?: string;
}

export default function NDVIWidget({ deviceId, className }: NDVIWidgetProps) {
  const [ndviData, setNdviData] = useState<NDVIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showImagery, setShowImagery] = useState(false);

  useEffect(() => {
    fetchNDVIData();
  }, [deviceId]);

  const fetchNDVIData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/katara/ndvi/${deviceId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch NDVI data: ${response.statusText}`);
      }

      const data = await response.json();
      setNdviData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case "good":
        return "bg-green-500";
      case "moderate":
        return "bg-yellow-500";
      case "poor":
        return "bg-orange-500";
      case "critical":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case "good":
        return "✅";
      case "moderate":
        return "⚠️";
      case "poor":
        return "🟡";
      case "critical":
        return "🚨";
      default:
        return "❓";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving":
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case "declining":
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      case "stable":
        return <Minus className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getDataQualityColor = (quality: string) => {
    switch (quality) {
      case "excellent":
        return "bg-green-100 text-green-800";
      case "good":
        return "bg-blue-100 text-blue-800";
      case "fair":
        return "bg-yellow-100 text-yellow-800";
      case "poor":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("fr-MA", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            Satellite NDVI Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Satellite NDVI Data</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
          <Button onClick={fetchNDVIData} className="mt-4" variant="outline">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!ndviData) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Satellite NDVI Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            No NDVI data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            🛰️ Satellite NDVI Data
          </span>
          <div className="flex items-center gap-2">
            <Badge className={getDataQualityColor(ndviData.current.data_quality)}>
              {ndviData.current.data_quality}
            </Badge>
            {getTrendIcon(ndviData.current.ndvi_trend)}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current NDVI Value */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-600">Current NDVI Value</h4>
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${getHealthColor(ndviData.current.vegetation_health)}`} />
              <span className="text-2xl font-bold">
                {ndviData.current.ndvi_value.toFixed(3)}
              </span>
              <Badge variant="outline">
                {getHealthIcon(ndviData.current.vegetation_health)} {ndviData.current.vegetation_health}
              </Badge>
            </div>
            <p className="text-xs text-gray-500">
              Range: -1 to 1 (vegetation typically 0.2-0.8)
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-600">Trend Analysis</h4>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-sm">7-day avg:</span>
                <span className="font-medium">{ndviData.trend.ndvi_7d_avg.toFixed(3)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">30-day avg:</span>
                <span className="font-medium">{ndviData.trend.ndvi_30d_avg.toFixed(3)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">7-day change:</span>
                <span className={`font-medium ${ndviData.trend.ndvi_change_7d < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {ndviData.trend.ndvi_change_7d > 0 ? '+' : ''}{ndviData.trend.ndvi_change_7d.toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Satellite Imagery */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-600">Satellite Imagery</h4>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm">
                <strong>Cloud Cover:</strong> {ndviData.current.cloud_cover.toFixed(1)}%
              </p>
              <p className="text-sm">
                <strong>Acquisition:</strong> {formatDate(ndviData.current.acquisition_date)}
              </p>
            </div>
            <Button
              onClick={() => setShowImagery(!showImagery)}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              {showImagery ? 'Hide' : 'Show'} Imagery
            </Button>
          </div>
          
          {showImagery && (
            <div className="mt-4 border rounded-lg overflow-hidden">
              <img
                src={ndviData.current.imagery_url}
                alt="NDVI Satellite Imagery"
                className="w-full h-64 object-cover"
                onError={(e) => {
                  e.currentTarget.src = "/api/placeholder/400/256";
                  e.currentTarget.alt = "Imagery not available";
                }}
              />
              <div className="p-2 bg-gray-100 text-xs text-center">
                NDVI Vegetation Health Map
              </div>
            </div>
          )}
        </div>

        {/* Alerts */}
        {ndviData.alerts.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-600">Vegetation Health Alerts</h4>
            <div className="space-y-2">
              {ndviData.alerts.map((alert, index) => (
                <Alert key={index} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {alert.message}
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </div>
        )}

        {/* Historical Data Preview */}
        {ndviData.historical.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-600">Recent History (7 days)</h4>
            <div className="grid grid-cols-7 gap-1 text-xs">
              {ndviData.historical.slice(0, 7).map((point, index) => (
                <div key={index} className="text-center">
                  <div className="font-medium">{new Date(point.date).getDate()}</div>
                  <div className={`w-2 h-2 rounded-full mx-auto mt-1 ${getHealthColor(
                    point.ndvi_value >= 0.4 ? 'good' : 
                    point.ndvi_value >= 0.3 ? 'moderate' : 
                    point.ndvi_value >= 0.2 ? 'poor' : 'critical'
                  )}`} />
                  <div className="text-gray-500">{point.ndvi_value.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Cache Info */}
        <div className="text-xs text-gray-500 border-t pt-4">
          <p>
            Data cached: {formatDate(ndviData.cached_at)} | 
            Expires: {formatDate(ndviData.cache_expires)}
          </p>
          <p className="mt-1">
            Location: {ndviData.current.location.lat.toFixed(4)}, {ndviData.current.location.lng.toFixed(4)}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
