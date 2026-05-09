"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Store, 
  TrendingUp, 
  Package, 
  Users, 
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  Star,
  MapPin,
  Eye,
  Edit,
  Plus,
  Filter,
  Search,
  BarChart3,
  DollarSign,
  Truck,
  ShoppingCart,
  Utensils,
  Timer
} from "lucide-react"

export default function RestaurantDashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [searchQuery, setSearchQuery] = useState("")

  // Mock data
  const stats = {
    totalSuppliers: 12,
    activeOrders: 6,
    monthlySpending: 8500,
    savingsRate: 25
  }

  const recentOrders = [
    {
      id: "ORD-2024-001",
      supplier: "Ferme El Kalam",
      products: ["Tomates bio (10kg)", "Laitues (5kg)"],
      amount: 325,
      status: "delivered",
      date: "2024-05-05",
      deliveryDate: "2024-05-06"
    },
    {
      id: "ORD-2024-002",
      supplier: "Domaine Atlas",
      products: ["Huile d'olive (5L)"],
      amount: 425,
      status: "in_transit",
      date: "2024-05-04",
      deliveryDate: "2024-05-07"
    },
    {
      id: "ORD-2024-003",
      supplier: "Citrus Souss",
      products: ["Agrumes (15kg)", "Oranges (8kg)"],
      amount: 1250,
      status: "pending",
      date: "2024-05-03",
      deliveryDate: "2024-05-08"
    }
  ]

  const suppliers = [
    {
      id: 1,
      name: "Ferme El Kalam",
      location: "Marrakech",
      rating: 4.8,
      products: 15,
      status: "active",
      image: "👨‍🌾",
      specialty: "Légumes bio",
      orders: 23,
      reliability: 98
    },
    {
      id: 2,
      name: "Domaine Atlas",
      location: "Fès",
      rating: 4.9,
      products: 8,
      status: "active",
      image: "👩‍🌾",
      specialty: "Huile d'olive",
      orders: 15,
      reliability: 99
    },
    {
      id: 3,
      name: "Rucher Azilal",
      location: "Azilal",
      rating: 5.0,
      products: 6,
      status: "active",
      image: "👩‍🌾",
      specialty: "Miels artisanaux",
      orders: 8,
      reliability: 100
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "delivered":
        return "bg-green-100 text-green-800 border-green-200"
      case "in_transit":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "cancelled":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "delivered":
        return "Livré"
      case "in_transit":
        return "En livraison"
      case "pending":
        return "En attente"
      case "cancelled":
        return "Annulé"
      default:
        return status
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <div style={{ 
          width: '256px', 
          backgroundColor: 'white', 
          borderRight: '1px solid #e5e7eb',
          minHeight: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          zIndex: 40
        }}>
          <Sidebar />
        </div>
        
        {/* Main Content */}
        <div style={{ flex: 1, marginLeft: '256px' }}>
          {/* Top Header */}
          <div style={{ 
            backgroundColor: 'white', 
            borderBottom: '1px solid #e5e7eb',
            position: 'sticky',
            top: 0,
            zIndex: 30
          }}>
            <TopHeader />
          </div>
          
          <main className="p-6">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Tableau de Bord Restaurant</h1>
              <p className="text-lg text-gray-600">Gérez vos approvisionnements et vos fournisseurs</p>
            </motion.div>

            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-sm mb-6">
              <div className="border-b border-gray-200">
                <div className="flex space-x-8 px-6">
                  {[
                    { id: "overview", label: "Aperçu", icon: BarChart3 },
                    { id: "suppliers", label: "Fournisseurs", icon: Users },
                    { id: "orders", label: "Commandes", icon: ShoppingCart },
                    { id: "menu", label: "Menu", icon: Utensils }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab.id
                          ? "border-orange-500 text-orange-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <tab.icon className="w-4 h-4" />
                        <span>{tab.label}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Tab Content */}
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Overview Tab */}
              {activeTab === "overview" && (
                <div className="space-y-6">
                  {/* Stats Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Fournisseurs actifs</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.totalSuppliers}</p>
                        </div>
                        <Users className="w-8 h-8 text-orange-600" />
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Commandes actives</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.activeOrders}</p>
                        </div>
                        <ShoppingCart className="w-8 h-8 text-blue-600" />
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Dépenses mensuelles</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.monthlySpending} DH</p>
                        </div>
                        <DollarSign className="w-8 h-8 text-yellow-600" />
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Économies réalisées</p>
                          <p className="text-2xl font-bold text-green-600">{stats.savingsRate}%</p>
                        </div>
                        <TrendingUp className="w-8 h-8 text-green-600" />
                      </div>
                    </motion.div>
                  </div>

                  {/* Recent Orders */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-white rounded-xl shadow-sm p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Commandes récentes</h3>
                      <button className="text-orange-600 hover:text-orange-700 text-sm font-medium">
                        Voir tout
                      </button>
                    </div>
                    <div className="space-y-4">
                      {recentOrders.map((order) => (
                        <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="font-medium text-gray-900">{order.supplier}</p>
                              <p className="text-sm text-gray-600">{order.id}</p>
                            </div>
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                              {getStatusLabel(order.status)}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-gray-600">{order.products.join(", ")}</p>
                              <p className="text-xs text-gray-500">{order.date}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-gray-900">{order.amount} DH</p>
                              <p className="text-xs text-gray-500">Livraison: {order.deliveryDate}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Quick Actions */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6"
                  >
                    <button className="bg-orange-600 text-white rounded-xl p-6 hover:bg-orange-700 transition-colors">
                      <Plus className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Nouvelle commande</p>
                    </button>
                    <button className="bg-blue-600 text-white rounded-xl p-6 hover:bg-blue-700 transition-colors">
                      <Search className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Trouver des fournisseurs</p>
                    </button>
                    <button className="bg-green-600 text-white rounded-xl p-6 hover:bg-green-700 transition-colors">
                      <Utensils className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Mettre à jour le menu</p>
                    </button>
                  </motion.div>
                </div>
              )}

              {/* Suppliers Tab */}
              {activeTab === "suppliers" && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Mes Fournisseurs</h3>
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          placeholder="Rechercher un fournisseur..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      </div>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <Filter className="w-4 h-4" />
                        <span>Filtrer</span>
                      </button>
                      <button className="flex items-center space-x-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
                        <Plus className="w-4 h-4" />
                        <span>Ajouter</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {suppliers.map((supplier) => (
                      <motion.div
                        key={supplier.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * supplier.id }}
                        className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="text-3xl">{supplier.image}</div>
                          <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            Actif
                          </span>
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-2">{supplier.name}</h4>
                        <p className="text-sm text-gray-600 mb-4">{supplier.specialty}</p>
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Localisation</span>
                            <span className="text-sm font-medium text-gray-900">{supplier.location}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Fiabilité</span>
                            <span className="text-sm font-medium text-green-600">{supplier.reliability}%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Produits</span>
                            <span className="text-sm font-medium text-gray-900">{supplier.products}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600">{supplier.rating}</span>
                          </div>
                          <span className="text-sm text-gray-500">{supplier.orders} commandes</span>
                        </div>
                        <div className="flex space-x-2">
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Voir</span>
                          </button>
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">
                            <ShoppingCart className="w-4 h-4" />
                            <span className="text-sm">Commander</span>
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* Orders Tab */}
              {activeTab === "orders" && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Commandes Fournisseurs</h3>
                    <div className="flex items-center space-x-4">
                      <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500">
                        <option value="all">Toutes</option>
                        <option value="pending">En attente</option>
                        <option value="in_transit">En livraison</option>
                        <option value="delivered">Livrées</option>
                      </select>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <Calendar className="w-4 h-4" />
                        <span>Période</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Commande</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Fournisseur</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Produits</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Montant</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Statut</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentOrders.map((order) => (
                          <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4">
                              <p className="font-medium text-gray-900">{order.id}</p>
                              <p className="text-sm text-gray-600">{order.date}</p>
                            </td>
                            <td className="py-3 px-4">
                              <p className="font-medium text-gray-900">{order.supplier}</p>
                            </td>
                            <td className="py-3 px-4">
                              <p className="text-sm text-gray-600">{order.products.join(", ")}</p>
                            </td>
                            <td className="py-3 px-4">
                              <p className="font-semibold text-gray-900">{order.amount} DH</p>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                                {getStatusLabel(order.status)}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <p className="text-sm text-gray-600">{order.deliveryDate}</p>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex space-x-2">
                                <button className="text-blue-600 hover:text-blue-700">
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button className="text-orange-600 hover:text-orange-700">
                                  <Truck className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Menu Tab */}
              {activeTab === "menu" && (
                <div className="space-y-6">
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-lg font-semibold text-gray-900">Gestion du Menu</h3>
                      <button className="flex items-center space-x-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
                        <Plus className="w-4 h-4" />
                        <span>Ajouter un plat</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-4">Plats actuels</h4>
                        <div className="space-y-3">
                          {[
                            { name: "Tagine d'agneau", category: "Plat principal", price: 120, available: true },
                            { name: "Couscous royal", category: "Plat principal", price: 150, available: true },
                            { name: "Salade marocaine", category: "Entrée", price: 45, available: true },
                            { name: "Pastilla au poulet", category: "Plat principal", price: 85, available: false }
                          ].map((dish, index) => (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.1 * index }}
                              className="border border-gray-200 rounded-lg p-4"
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium text-gray-900">{dish.name}</p>
                                  <p className="text-sm text-gray-600">{dish.category}</p>
                                </div>
                                <div className="text-right">
                                  <p className="font-semibold text-gray-900">{dish.price} DH</p>
                                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    dish.available 
                                      ? 'bg-green-100 text-green-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {dish.available ? 'Disponible' : 'Indisponible'}
                                  </span>
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold text-gray-900 mb-4">Sourcing actuel</h4>
                        <div className="space-y-3">
                          {[
                            { ingredient: "Tomates bio", supplier: "Ferme El Kalam", quantity: "10kg/semaine" },
                            { ingredient: "Huile d'olive", supplier: "Domaine Atlas", quantity: "5L/mois" },
                            { ingredient: "Miel sauvage", supplier: "Rucher Azilal", quantity: "2kg/mois" }
                          ].map((item, index) => (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.1 * index }}
                              className="bg-orange-50 border border-orange-200 rounded-lg p-4"
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium text-gray-900">{item.ingredient}</p>
                                  <p className="text-sm text-orange-700">{item.supplier}</p>
                                </div>
                                <p className="text-sm text-gray-600">{item.quantity}</p>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
