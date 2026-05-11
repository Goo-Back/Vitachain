"use client";

import { useState, useEffect } from 'react';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    farmers: 0,
    restaurants: 0,
    citizens: 0,
    total_products: 0,
    total_orders: 0,
    system_uptime: "0%",
    storage_used: "0%"
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading admin data
    setTimeout(() => {
      setUsers([
        { id: "1", email: "farmer.test@vitachain.ma", role: "FARMER", status: "active", created_at: "2024-01-01" },
        { id: "2", email: "restaurant.test@vitachain.ma", role: "RESTAURANT", status: "active", created_at: "2024-01-02" },
        { id: "3", email: "citizen.test@vitachain.ma", role: "CITIZEN", status: "active", created_at: "2024-01-03" },
        { id: "4", email: "admin.test@vitachain.ma", role: "ADMIN", status: "active", created_at: "2024-01-04" }
      ]);
      setStats({
        total_users: 156,
        active_users: 142,
        farmers: 45,
        restaurants: 28,
        citizens: 83,
        total_products: 234,
        total_orders: 567,
        system_uptime: "99.9%",
        storage_used: "67%"
      });
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="border-b pb-4 mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              🛡️ Dashboard ADMIN
            </h1>
            <p className="text-gray-600 mt-2">
              Panneau d'administration système
            </p>
          </div>
          
          {/* Statistiques principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                👥 Utilisateurs totaux
              </h3>
              <p className="text-3xl font-bold text-blue-900">{stats.total_users}</p>
              <p className="text-blue-600 text-sm mt-1">
                {stats.active_users} actifs
              </p>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                🌾 Agriculteurs
              </h3>
              <p className="text-3xl font-bold text-green-900">{stats.farmers}</p>
              <p className="text-green-600 text-sm mt-1">
                Actifs sur la plateforme
              </p>
            </div>
            
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-orange-800 mb-2">
                🍽 Restaurateurs
              </h3>
              <p className="text-3xl font-bold text-orange-900">{stats.restaurants}</p>
              <p className="text-orange-600 text-sm mt-1">
                Partenaires actifs
              </p>
            </div>
            
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-purple-800 mb-2">
                👥 Consommateurs
              </h3>
              <p className="text-3xl font-bold text-purple-900">{stats.citizens}</p>
              <p className="text-purple-600 text-sm mt-1">
                Utilisateurs enregistrés
              </p>
            </div>
          </div>
          
          {/* Statistiques de plateforme */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                🛒 Produits
              </h3>
              <p className="text-2xl font-bold text-red-900">{stats.total_products}</p>
              <p className="text-red-600 text-sm mt-1">
                Dans la marketplace
              </p>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                📦 Commandes
              </h3>
              <p className="text-2xl font-bold text-yellow-900">{stats.total_orders}</p>
              <p className="text-yellow-600 text-sm mt-1">
                Total traitées
              </p>
            </div>
            
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-indigo-800 mb-2">
                📊 Taux de disponibilité
              </h3>
              <p className="text-2xl font-bold text-indigo-900">{stats.system_uptime}</p>
              <p className="text-indigo-600 text-sm mt-1">
                Uptime du système
              </p>
            </div>
          </div>
          
          {/* Gestion des utilisateurs */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              👥 Gestion des utilisateurs
            </h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rôle
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date d'inscription
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.role === 'FARMER' ? 'bg-green-100 text-green-800' :
                          user.role === 'RESTAURANT' ? 'bg-orange-100 text-orange-800' :
                          user.role === 'CITIZEN' ? 'bg-purple-100 text-purple-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.status === 'active' ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.created_at}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-indigo-600 hover:text-indigo-900 mr-3">
                          Modifier
                        </button>
                        <button className="text-red-600 hover:text-red-900">
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Actions administratives */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                📊 Rapports
              </h3>
              <p className="text-gray-600">
                Générer des rapports détaillés
              </p>
            </div>
            
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                🔧 Configuration
              </h3>
              <p className="text-gray-600">
                Paramètres système
              </p>
            </div>
            
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                🛡️ Sécurité
              </h3>
              <p className="text-gray-600">
                Gestion des accès
              </p>
            </div>
            
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                💾 Sauvegarde
              </h3>
              <p className="text-gray-600">
                Backup et restauration
              </p>
            </div>
          </div>
          
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🎯 Fonctionnalités administratives
            </h2>
            
            <ul className="space-y-3">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Gestion complète des utilisateurs et rôles</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Surveillance de l'activité plateforme</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Configuration des permissions d'accès</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Gestion des contenus et modérations</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Analyse des performances et statistiques</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                <span>Gestion des sauvegardes et récupérations</span>
              </li>
            </ul>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-500">
              🚀 Le dashboard ADMIN est en cours de développement
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Les fonctionnalités seront progressivement intégrées
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
