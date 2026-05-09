"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function FarmarketDashboard() {
  const [listings, setListings] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setListings([
        { id: "1", title: "Tomates Bio", price: 15, quantity: "100kg", farmer: "Ahmed" },
        { id: "2", title: "Carottes Fraîches", price: 8, quantity: "50kg", farmer: "Fatima" }
      ]);
      setOrders([
        { id: "1", product: "Tomates Bio", quantity: "20kg", status: "confirmed", buyer: "Restaurant ABC" },
        { id: "2", product: "Carottes Fraîches", quantity: "10kg", status: "pending", buyer: "Restaurant XYZ" }
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
              <span className="ml-4 text-gray-500">FARMARKET Dashboard</span>
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
          <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord FARMARKET</h1>
          <p className="mt-2 text-gray-600">Marketplace B2B pour produits agricoles</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">12</div>
            <div className="text-gray-500">Annonces Actives</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">8</div>
            <div className="text-gray-500">Commandes en Cours</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">₿2,450</div>
            <div className="text-gray-500">Revenus du Mois</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">4.8</div>
            <div className="text-gray-500">Note Moyenne</div>
          </div>
        </div>

        {/* Listings and Orders Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Mes Annonces</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {listings.map((listing) => (
                  <div key={listing.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{listing.title}</div>
                        <div className="text-sm text-gray-500">{listing.farmer}</div>
                        <div className="text-sm text-gray-500">{listing.quantity}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">{listing.price} MAD/kg</div>
                        <button className="mt-1 text-xs bg-blue-500 text-white px-2 py-1 rounded">
                          Modifier
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Commandes Récentes</h2>
            {loading ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-3">
                {orders.map((order) => (
                  <div key={order.id} className="p-3 border rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{order.product}</div>
                        <div className="text-sm text-gray-500">{order.buyer}</div>
                        <div className="text-sm text-gray-500">{order.quantity}</div>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        order.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {order.status === 'confirmed' ? 'Confirmée' : 'En attente'}
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
