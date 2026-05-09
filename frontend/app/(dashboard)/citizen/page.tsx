"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function CitizenDashboard() {
  const [reservations, setReservations] = useState([]);
  const [availableMeals, setAvailableMeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setReservations([
        { id: "1", restaurant: "Restaurant ABC", meal: "Tajine d'Agneau", status: "confirmed", pickupTime: "19:00" },
        { id: "2", restaurant: "Restaurant XYZ", meal: "Couscous Royal", status: "pending", pickupTime: "20:30" }
      ]);
      setAvailableMeals([
        { id: "1", restaurant: "Restaurant ABC", meal: "Tajine d'Agneau", price: 60, discount: 50 },
        { id: "2", restaurant: "Restaurant XYZ", meal: "Couscous Royal", price: 75, discount: 50 }
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
              <span className="ml-4 text-gray-500">CITIZEN Dashboard</span>
            </div>
            <nav className="flex space-x-4">
              <Link href="/dashboard/farmarket" className="text-green-600 font-medium">
                Marketplace
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
          <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord Citoyen</h1>
          <p className="mt-2 text-gray-600">Accès aux produits agricoles et repas locaux</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">8</div>
            <div className="text-gray-500">Réservations Actives</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">15</div>
            <div className="text-gray-500">Repas Disponibles</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">₿420</div>
            <div className="text-gray-500">Économies Totales</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">4.9</div>
            <div className="text-gray-500">Note Moyenne</div>
          </div>
        </div>

        {/* Available Meals and Reservations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Repas Disponibles</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {availableMeals.map((meal) => (
                  <div key={meal.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{meal.meal}</div>
                        <div className="text-sm text-gray-500">{meal.restaurant}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">{meal.price} MAD</div>
                        <div className="text-xs text-green-600">-{meal.discount}%</div>
                        <button className="mt-1 text-xs bg-blue-500 text-white px-2 py-1 rounded">
                          Réserver
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Mes Réservations</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {reservations.map((reservation) => (
                  <div key={reservation.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{reservation.meal}</div>
                        <div className="text-sm text-gray-500">{reservation.restaurant}</div>
                        <div className="text-sm text-gray-500">Retrait: {reservation.pickupTime}</div>
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
