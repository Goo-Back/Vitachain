"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function SecondserveDashboard() {
  const [meals, setMeals] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setMeals([
        { id: "1", name: "Tajine d'Agneau", originalPrice: 120, discountedPrice: 60, available: 8 },
        { id: "2", name: "Couscous Royal", originalPrice: 150, discountedPrice: 75, available: 12 }
      ]);
      setReservations([
        { id: "1", meal: "Tajine d'Agneau", customer: "Mohamed", quantity: 2, status: "confirmed" },
        { id: "2", meal: "Couscous Royal", customer: "Amina", quantity: 4, status: "pending" }
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
              <span className="ml-4 text-gray-500">SECONDSERVE Dashboard</span>
            </div>
            <nav className="flex space-x-4">
              <Link href="/dashboard/secondserve" className="text-green-600 font-medium">
                Surplus
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
          <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord SECONDSERVE</h1>
          <p className="mt-2 text-gray-600">Réduction du gaspillage alimentaire</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">15</div>
            <div className="text-gray-500">Repas Disponibles</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">23</div>
            <div className="text-gray-500">Réservations Aujourd'hui</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">45%</div>
            <div className="text-gray-500">Réduction du Gaspillage</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">₿1,250</div>
            <div className="text-gray-500">Économies Réalisées</div>
          </div>
        </div>

        {/* Meals and Reservations Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Repas en Surplus</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {meals.map((meal) => (
                  <div key={meal.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{meal.name}</div>
                        <div className="text-sm text-gray-500">Disponible: {meal.available} portions</div>
                      </div>
                      <div className="text-right">
                        <div className="line-through text-gray-400">{meal.originalPrice} MAD</div>
                        <div className="font-bold text-green-600">{meal.discountedPrice} MAD</div>
                        <div className="text-xs text-green-600">-50%</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Réservations Récentes</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {reservations.map((reservation) => (
                  <div key={reservation.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{reservation.meal}</div>
                        <div className="text-sm text-gray-500">{reservation.customer}</div>
                        <div className="text-sm text-gray-500">{reservation.quantity} portions</div>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        reservation.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {reservation.status === 'confirmed' ? 'Confirmée' : 'En attente'}
                      </span>
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
