"use client";

import { AlertPattern } from "../hooks/useTelemetryHistory";

interface AlertPatternsProps {
  alertPatterns: AlertPattern[];
}

export default function AlertPatterns({ alertPatterns }: AlertPatternsProps) {
  const getTotalAlerts = () => {
    return alertPatterns.reduce((total, pattern) => 
      total + pattern.high_alerts + pattern.medium_alerts + pattern.low_alerts, 0
    );
  };

  const getAlertSeverityColor = (severity: "high" | "medium" | "low") => {
    switch (severity) {
      case "high":
        return "bg-red-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getAlertSeverityTextColor = (severity: "high" | "medium" | "low") => {
    switch (severity) {
      case "high":
        return "text-red-700";
      case "medium":
        return "text-yellow-700";
      case "low":
        return "text-blue-700";
      default:
        return "text-gray-700";
    }
  };

  const getMostCommonCause = () => {
    const causeCount: Record<string, number> = {};
    
    alertPatterns.forEach(pattern => {
      pattern.main_causes.forEach(cause => {
        causeCount[cause] = (causeCount[cause] || 0) + 1;
      });
    });

    return Object.entries(causeCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3);
  };

  const totalAlerts = getTotalAlerts();
  const mostCommonCauses = getMostCommonCause();

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Alert Patterns</h2>

      {alertPatterns.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-2">🔔</div>
          <p className="text-gray-500">No alerts recorded in this period</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{totalAlerts}</div>
              <div className="text-sm text-gray-600">Total Alerts</div>
            </div>
            
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-600">
                {alertPatterns.reduce((sum, p) => sum + p.high_alerts, 0)}
              </div>
              <div className="text-sm text-red-600">High Severity</div>
            </div>
            
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {alertPatterns.reduce((sum, p) => sum + p.medium_alerts, 0)}
              </div>
              <div className="text-sm text-yellow-600">Medium Severity</div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {alertPatterns.reduce((sum, p) => sum + p.low_alerts, 0)}
              </div>
              <div className="text-sm text-blue-600">Low Severity</div>
            </div>
          </div>

          {/* Alert Timeline Chart */}
          <div>
            <h3 className="text-md font-medium text-gray-800 mb-4">Alert Timeline</h3>
            <div className="h-48 bg-gray-50 rounded-lg p-4">
              <div className="h-full flex items-end justify-between space-x-1">
                {alertPatterns.slice(0, 30).map((pattern, index) => {
                  const totalDayAlerts = pattern.high_alerts + pattern.medium_alerts + pattern.low_alerts;
                  const maxHeight = Math.max(...alertPatterns.map(p => 
                    p.high_alerts + p.medium_alerts + p.low_alerts
                  ), 1);
                  
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div className="w-full flex flex-col-reverse space-y-reverse space-y-1">
                        {pattern.high_alerts > 0 && (
                          <div
                            className="bg-red-500 rounded-t"
                            style={{ height: `${(pattern.high_alerts / maxHeight) * 100}%` }}
                            title={`${new Date(pattern.date).toLocaleDateString()}: ${pattern.high_alerts} high alerts`}
                          />
                        )}
                        {pattern.medium_alerts > 0 && (
                          <div
                            className="bg-yellow-500 rounded-t"
                            style={{ height: `${(pattern.medium_alerts / maxHeight) * 100}%` }}
                            title={`${new Date(pattern.date).toLocaleDateString()}: ${pattern.medium_alerts} medium alerts`}
                          />
                        )}
                        {pattern.low_alerts > 0 && (
                          <div
                            className="bg-blue-500 rounded-t"
                            style={{ height: `${(pattern.low_alerts / maxHeight) * 100}%` }}
                            title={`${new Date(pattern.date).toLocaleDateString()}: ${pattern.low_alerts} low alerts`}
                          />
                        )}
                      </div>
                      {index % 5 === 0 && (
                        <div className="text-xs text-gray-500 mt-1 rotate-45 origin-left">
                          {new Date(pattern.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Most Common Causes */}
          {mostCommonCauses.length > 0 && (
            <div>
              <h3 className="text-md font-medium text-gray-800 mb-4">Most Common Alert Causes</h3>
              <div className="space-y-2">
                {mostCommonCauses.map(([cause, count], index) => (
                  <div key={cause} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-green-600 font-medium text-sm">{index + 1}</span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {cause.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{count} occurrences</span>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${(count / Math.max(...mostCommonCauses.map(([, c]) => c))) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Alert Table */}
          <div>
            <h3 className="text-md font-medium text-gray-800 mb-4">Daily Alert Breakdown</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      High
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Medium
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Low
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Main Causes
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {alertPatterns.slice(0, 10).map((pattern, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(pattern.date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {pattern.high_alerts > 0 ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            {pattern.high_alerts}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {pattern.medium_alerts > 0 ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            {pattern.medium_alerts}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {pattern.low_alerts > 0 ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {pattern.low_alerts}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {pattern.high_alerts + pattern.medium_alerts + pattern.low_alerts}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex flex-wrap gap-1">
                          {pattern.main_causes.slice(0, 2).map((cause, causeIndex) => (
                            <span
                              key={causeIndex}
                              className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700"
                            >
                              {cause.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          ))}
                          {pattern.main_causes.length > 2 && (
                            <span className="text-xs text-gray-500">+{pattern.main_causes.length - 2}</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {alertPatterns.length > 10 && (
                <div className="px-6 py-3 bg-gray-50 text-center text-sm text-gray-500">
                  Showing 10 of {alertPatterns.length} days
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
