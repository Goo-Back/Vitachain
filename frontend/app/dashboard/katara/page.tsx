"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function KataraDashboard() {
  const [devices, setDevices] = useState([]);
  const [telemetry, setTelemetry] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setDevices([
        { id: "1", name: "Capteur d'humidité", type: "esp32", status: "active" },
        { id: "2", name: "Station météo", type: "sensor", status: "active" }
      ]);
      setTelemetry([
        { timestamp: "2024-01-01T12:00:00Z", temperature: 25, humidity: 60 },
        { timestamp: "2024-01-01T12:30:00Z", temperature: 26, humidity: 58 }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord KATARA</h1>
          <p className="mt-2 text-gray-600">Agriculture intelligente avec IoT</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">5</div>
            <div className="text-gray-500">Appareils Actifs</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">23°C</div>
            <div className="text-gray-500">Température Moyenne</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">65%</div>
            <div className="text-gray-500">Humidité Moyenne</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">98%</div>
            <div className="text-gray-500">Uptime</div>
          </div>
        </div>

        {/* Devices Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Appareils IoT</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {devices.map((device) => (
                  <div key={device.id} className="flex justify-between items-center p-3 border rounded">
                    <div>
                      <div className="font-medium">{device.name}</div>
                      <div className="text-sm text-gray-500">{device.type}</div>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${
                      device.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {device.status === 'active' ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Données Télémétriques</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {telemetry.map((data, index) => (
                  <div key={index} className="p-3 border rounded">
                    <div className="text-sm text-gray-500">
                      {new Date(data.timestamp).toLocaleString()}
                    </div>
                    <div className="flex justify-between mt-1">
                      <span>Temp: {data.temperature}°C</span>
                      <span>Humidité: {data.humidity}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
