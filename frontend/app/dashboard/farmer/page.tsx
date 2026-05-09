"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Leaf, 
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
  ShoppingCart
} from "lucide-react"

export default function FarmerDashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [searchQuery, setSearchQuery] = useState("")

  // Mock data
  const stats = {
    totalProducts: 15,
    activeOrders: 8,
    monthlyRevenue: 12500,
    satisfactionRate: 4.8
  }

  const recentOrders = [
    {
      id: "ORD-2024-001",
      customer: "Restaurant Le Terroir",
      products: ["Tomates bio (5kg)", "Laitues (3kg)"],
      amount: 275,
      status: "pending",
      date: "2024-05-05",
      deliveryDate: "2024-05-07"
    },
    {
      id: "ORD-2024-002",
      customer: "Fatima Zahra",
      products: ["Huile d'olive (2L)"],
      amount: 170,
      status: "confirmed",
      date: "2024-05-04",
      deliveryDate: "2024-05-06"
    },
    {
      id: "ORD-2024-003",
      customer: "Youssef Amrani",
      products: ["Agrumes (10kg)", "Miel (1kg)"],
      amount: 650,
      status: "delivered",
      date: "2024-05-03",
      deliveryDate: "2024-05-04"
    }
  ]

  const products = [
    {
      id: 1,
      name: "Tomates Bio Premium",
      category: "Légumes",
      price: 25,
      unit: "kg",
      stock: 50,
      status: "available",
      image: "🍅",
      rating: 4.8,
      orders: 23
    },
    {
      id: 2,
      name: "Huile d'Olive Extra Vierge",
      category: "Huiles",
      price: 85,
      unit: "L",
      stock: 20,
      status: "available",
      image: "🫒",
      rating: 4.9,
      orders: 15
    },
    {
      id: 3,
      name: "Miel de Thym Sauvage",
      category: "Miels",
      price: 150,
      unit: "kg",
      stock: 5,
      status: "low_stock",
      image: "🍯",
      rating: 5.0,
      orders: 8
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "delivered":
        return "bg-green-100 text-green-800 border-green-200"
      case "confirmed":
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
      case "confirmed":
        return "Confirmé"
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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Tableau de Bord Agriculteur</h1>
              <p className="text-lg text-gray-600">Gérez votre ferme et vos ventes</p>
            </motion.div>

            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-sm mb-6">
              <div className="border-b border-gray-200">
                <div className="flex space-x-8 px-6">
                  {[
                    { id: "overview", label: "Aperçu", icon: BarChart3 },
                    { id: "products", label: "Produits", icon: Package },
                    { id: "orders", label: "Commandes", icon: ShoppingCart },
                    { id: "katara", label: "Katara IoT", icon: Leaf },
                    { id: "analytics", label: "Analytics", icon: TrendingUp }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab.id
                          ? "border-green-500 text-green-600"
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
                          <p className="text-sm text-gray-600 mb-1">Produits actifs</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
                        </div>
                        <Package className="w-8 h-8 text-green-600" />
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
                          <p className="text-sm text-gray-600 mb-1">Revenu mensuel</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.monthlyRevenue} DH</p>
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
                          <p className="text-sm text-gray-600 mb-1">Satisfaction</p>
                          <div className="flex items-center space-x-1">
                            <span className="text-2xl font-bold text-gray-900">{stats.satisfactionRate}</span>
                            <Star className="w-5 h-5 text-yellow-400 fill-current" />
                          </div>
                        </div>
                        <Users className="w-8 h-8 text-purple-600" />
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
                      <h3 className="text-lg font-semibold text-gray-900">Commandes B2B récentes</h3>
                      <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                        Voir tout
                      </button>
                    </div>
                    <div className="space-y-4">
                      {recentOrders.map((order) => (
                        <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="font-medium text-gray-900">{order.customer}</p>
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
                    <button className="bg-green-600 text-white rounded-xl p-6 hover:bg-green-700 transition-colors">
                      <Plus className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Ajouter un produit</p>
                    </button>
                    <button className="bg-blue-600 text-white rounded-xl p-6 hover:bg-blue-700 transition-colors">
                      <Eye className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Voir les analytics</p>
                    </button>
                    <button className="bg-orange-600 text-white rounded-xl p-6 hover:bg-orange-700 transition-colors">
                      <Truck className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Gérer les livraisons</p>
                    </button>
                  </motion.div>
                </div>
              )}

              {/* Products Tab */}
              {activeTab === "products" && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Mes Produits</h3>
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          placeholder="Rechercher un produit..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                      </div>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <Filter className="w-4 h-4" />
                        <span>Filtrer</span>
                      </button>
                      <button className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                        <Plus className="w-4 h-4" />
                        <span>Ajouter</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {products.map((product) => (
                      <motion.div
                        key={product.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * product.id }}
                        className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="text-3xl">{product.image}</div>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            product.status === 'available' 
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {product.status === 'available' ? 'Disponible' : 'Stock faible'}
                          </span>
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-2">{product.name}</h4>
                        <p className="text-sm text-gray-600 mb-4">{product.category}</p>
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <p className="text-lg font-bold text-gray-900">{product.price} DH/{product.unit}</p>
                            <p className="text-sm text-gray-600">Stock: {product.stock} {product.unit}</p>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center space-x-1">
                              <Star className="w-4 h-4 text-yellow-400 fill-current" />
                              <span className="text-sm text-gray-600">{product.rating}</span>
                            </div>
                            <p className="text-xs text-gray-500">{product.orders} commandes</p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Voir</span>
                          </button>
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                            <Edit className="w-4 h-4" />
                            <span className="text-sm">Modifier</span>
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
                    <h3 className="text-lg font-semibold text-gray-900">Toutes les commandes</h3>
                    <div className="flex items-center space-x-4">
                      <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500">
                        <option value="all">Toutes</option>
                        <option value="pending">En attente</option>
                        <option value="confirmed">Confirmées</option>
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
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Client</th>
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
                              <p className="font-medium text-gray-900">{order.customer}</p>
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
                                <button className="text-green-600 hover:text-green-700">
                                  <CheckCircle className="w-4 h-4" />
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

              {/* Katara IoT Tab */}
              {activeTab === "katara" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* NDVI Chart */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Analyse NDVI - Parcelle A1</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                          <div>
                            <p className="text-sm text-gray-600">NDVI Actuel</p>
                            <p className="text-2xl font-bold text-green-600">0.742</p>
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                              Bonne santé
                            </span>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-600">Tendance (7 jours)</p>
                            <div className="flex items-center space-x-1">
                              <span className="text-lg font-semibold text-green-600">+2.3%</span>
                              <TrendingUp className="w-4 h-4 text-green-600" />
                            </div>
                          </div>
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-600">Humidité du sol</p>
                            <p className="text-lg font-semibold text-blue-600">68%</p>
                          </div>
                        </div>

                        <div className="mt-4">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Recommandations</h4>
                          <div className="space-y-2">
                            <div className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                              <div>
                                <p className="text-sm font-medium text-blue-900">Irrigation optimale</p>
                                <p className="text-sm text-blue-700">Réduire l'irrigation de 15% cette semaine</p>
                              </div>
                            </div>
                            <div className="flex items-start space-x-2 p-3 bg-yellow-50 rounded-lg">
                              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                              <div>
                                <p className="text-sm font-medium text-yellow-900">Surveillance requise</p>
                                <p className="text-sm text-yellow-700">Zone Est montre un léger flétrissement</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Device Status */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">État des Capteurs</h3>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Capteur d'humidité</span>
                              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                Actif
                              </span>
                            </div>
                            <p className="text-lg font-semibold text-green-600">68%</p>
                            <p className="text-sm text-gray-600">Optimal: 60-75%</p>
                          </div>
                          
                          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Capteur de température</span>
                              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                Actif
                              </span>
                            </div>
                            <p className="text-lg font-semibold text-green-600">24.5°C</p>
                            <p className="text-sm text-gray-600">Optimal: 22-26°C</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Capteur de pH</span>
                              <span className="inline-flex items-center px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                                Attention
                              </span>
                            </div>
                            <p className="text-lg font-semibold text-yellow-600">6.8</p>
                            <p className="text-sm text-gray-600">Optimal: 6.0-7.0</p>
                          </div>
                          
                          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Capteur de lumière</span>
                              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                Actif
                              </span>
                            </div>
                            <p className="text-lg font-semibold text-green-600">85%</p>
                            <p className="text-sm text-gray-600">Optimal: &gt;70%</p>
                          </div>
                        </div>
                      </div>

                      <div className="mt-6">
                        <h4 className="text-sm font-medium text-gray-700 mb-3">Actions Rapides</h4>
                        <div className="grid grid-cols-2 gap-3">
                          <button className="flex items-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Voir détails</span>
                          </button>
                          <button className="flex items-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm">Configurer alertes</span>
                          </button>
                          <button className="flex items-center space-x-2 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                            <Calendar className="w-4 h-4" />
                            <span className="text-sm">Historique</span>
                          </button>
                          <button className="flex items-center space-x-2 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                            <BarChart3 className="w-4 h-4" />
                            <span className="text-sm">Rapports</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Weather Forecast */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Prévisions Météo (7 jours)</h3>
                    <div className="grid grid-cols-7 gap-4">
                      {[
                        { day: "Lun", date: "06/05", temp: 28, condition: "Ensoleillé", icon: "☀️" },
                        { day: "Mar", date: "07/05", temp: 26, condition: "Nuageux", icon: "⛅" },
                        { day: "Mer", date: "08/05", temp: 24, condition: "Pluie", icon: "🌧️" },
                        { day: "Jeu", date: "09/05", temp: 25, condition: "Partiellement nuageux", icon: "⛅" },
                        { day: "Ven", date: "10/05", temp: 27, condition: "Ensoleillé", icon: "☀️" },
                        { day: "Sam", date: "11/05", temp: 29, condition: "Ensoleillé", icon: "☀️" },
                        { day: "Dim", date: "12/05", temp: 26, condition: "Nuageux", icon: "⛅" }
                      ].map((day, index) => (
                        <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600 mb-1">{day.date}</p>
                          <div className="text-2xl mb-2">{day.icon}</div>
                          <p className="text-sm font-medium text-gray-900">{day.day}</p>
                          <p className="text-lg font-bold text-blue-600">{day.temp}°C</p>
                          <p className="text-xs text-gray-600">{day.condition}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Irrigation Planning */}
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Planification d'Irrigation</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                        <div>
                          <p className="text-sm font-medium text-blue-900">Prochaine irrigation</p>
                          <p className="text-lg font-bold text-blue-600">Aujourd'hui 18:00</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Durée estimée</p>
                          <p className="text-lg font-semibold text-gray-900">2h 30min</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600 mb-1">Volume d'eau</p>
                          <p className="text-lg font-semibold text-gray-900">1,200 L</p>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600 mb-1">Zone concernée</p>
                          <p className="text-lg font-semibold text-gray-900">Parcelle A1</p>
                        </div>
                      </div>

                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Historique récent</h4>
                        <div className="space-y-2">
                          {[
                            { date: "04/05", time: "06:00", duration: "2h 15min", volume: "1,200 L" },
                            { date: "02/05", time: "07:30", duration: "2h 45min", volume: "1,350 L" },
                            { date: "30/04", time: "06:45", duration: "2h 20min", volume: "1,100 L" }
                          ].map((irrigation, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div>
                                <p className="text-sm font-medium text-gray-900">{irrigation.date} à {irrigation.time}</p>
                                <p className="text-sm text-gray-600">{irrigation.duration} • {irrigation.volume}</p>
                              </div>
                              <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                Complétée
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Analytics Tab */}
              {activeTab === "analytics" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance des ventes</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Ventes ce mois</span>
                          <span className="text-xl font-bold text-green-600">+15%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Ventes dernier mois</span>
                          <span className="text-xl font-bold text-gray-900">10,875 DH</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Objectif mensuel</span>
                          <span className="text-xl font-bold text-gray-900">15,000 DH</span>
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="bg-white rounded-xl shadow-sm p-6"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Produits populaires</h3>
                      <div className="space-y-3">
                        {products.slice(0, 3).map((product, index) => (
                          <div key={product.id} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <span className="text-2xl">{product.image}</span>
                              <div>
                                <p className="font-medium text-gray-900">{product.name}</p>
                                <p className="text-sm text-gray-600">{product.orders} ventes</p>
                              </div>
                            </div>
                            <span className="font-semibold text-gray-900">{product.orders * product.price} DH</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  </div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white rounded-xl shadow-sm p-6"
                  >
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertes et recommandations</h3>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div>
                          <p className="font-medium text-yellow-900">Stock faible</p>
                          <p className="text-sm text-yellow-700">Le miel de thym sauvage a moins de 5 unités en stock</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <p className="font-medium text-blue-900">Opportunité</p>
                          <p className="text-sm text-blue-700">Les tomates bio sont très demandées ce mois-ci</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              )}
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
