"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  ShoppingCart, 
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
  Heart,
  Plus,
  Filter,
  Search,
  BarChart3,
  DollarSign,
  Truck,
  Leaf,
  Gift,
  Bell
} from "lucide-react"

export default function ConsumerDashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [searchQuery, setSearchQuery] = useState("")

  // Mock data
  const stats = {
    totalOrders: 24,
    favoriteFarmers: 8,
    monthlySpending: 3200,
    savedAmount: 480
  }

  const recentOrders = [
    {
      id: "ORD-2024-001",
      farmer: "Ferme El Kalam",
      products: ["Tomates bio (2kg)", "Laitues (1kg)"],
      amount: 75,
      status: "delivered",
      date: "2024-05-05",
      rating: 5,
      review: "Produits excellents et très frais!"
    },
    {
      id: "ORD-2024-002",
      farmer: "Domaine Atlas",
      products: ["Huile d'olive (1L)"],
      amount: 85,
      status: "in_transit",
      date: "2024-05-04",
      rating: null,
      review: null
    },
    {
      id: "ORD-2024-003",
      farmer: "Citrus Souss",
      products: ["Agrumes (3kg)"],
      amount: 195,
      status: "pending",
      date: "2024-05-03",
      rating: null,
      review: null
    }
  ]

  const favoriteProducts = [
    {
      id: 1,
      name: "Tomates Bio Premium",
      farmer: "Ferme El Kalam",
      category: "Légumes",
      price: 25,
      unit: "kg",
      rating: 4.8,
      image: "🍅",
      location: "Marrakech",
      organic: true,
      inStock: true
    },
    {
      id: 2,
      name: "Huile d'Olive Extra Vierge",
      farmer: "Domaine Atlas",
      category: "Huiles",
      price: 85,
      unit: "L",
      rating: 4.9,
      image: "🫒",
      location: "Fès",
      organic: true,
      inStock: true
    },
    {
      id: 3,
      name: "Miel de Thym Sauvage",
      farmer: "Rucher Azilal",
      category: "Miels",
      price: 150,
      unit: "kg",
      rating: 5.0,
      image: "🍯",
      location: "Azilal",
      organic: true,
      inStock: false
    }
  ]

  const favoriteFarmers = [
    {
      id: 1,
      name: "Ferme El Kalam",
      location: "Marrakech",
      rating: 4.8,
      products: 15,
      specialty: "Légumes bio",
      image: "👨‍🌾",
      years: 12,
      certified: true,
      orders: 248
    },
    {
      id: 2,
      name: "Domaine Atlas",
      location: "Fès",
      rating: 4.9,
      products: 8,
      specialty: "Huile d'olive",
      image: "👩‍🌾",
      years: 25,
      certified: true,
      orders: 189
    },
    {
      id: 3,
      name: "Rucher Azilal",
      location: "Azilal",
      rating: 5.0,
      products: 6,
      specialty: "Miels artisanaux",
      image: "👩‍🌾",
      years: 15,
      certified: true,
      orders: 156
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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Tableau de Bord Consommateur</h1>
              <p className="text-lg text-gray-600">Découvrez et achetez les meilleurs produits locaux</p>
            </motion.div>

            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-sm mb-6">
              <div className="border-b border-gray-200">
                <div className="flex space-x-8 px-6">
                  {[
                    { id: "overview", label: "Aperçu", icon: BarChart3 },
                    { id: "products", label: "Produits", icon: Package },
                    { id: "orders", label: "Commandes", icon: ShoppingCart },
                    { id: "farmers", label: "Agriculteurs", icon: Users }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab.id
                          ? "border-blue-500 text-blue-600"
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
                          <p className="text-sm text-gray-600 mb-1">Commandes totales</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.totalOrders}</p>
                        </div>
                        <ShoppingCart className="w-8 h-8 text-blue-600" />
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
                          <p className="text-sm text-gray-600 mb-1">Agriculteurs favoris</p>
                          <p className="text-2xl font-bold text-gray-900">{stats.favoriteFarmers}</p>
                        </div>
                        <Heart className="w-8 h-8 text-red-600" />
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
                          <p className="text-2xl font-bold text-green-600">{stats.savedAmount} DH</p>
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
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Voir tout
                      </button>
                    </div>
                    <div className="space-y-4">
                      {recentOrders.map((order) => (
                        <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="font-medium text-gray-900">{order.farmer}</p>
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
                              {order.rating && (
                                <div className="flex items-center space-x-1">
                                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                                  <span className="text-sm text-gray-600">{order.rating}</span>
                                </div>
                              )}
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
                    <button className="bg-blue-600 text-white rounded-xl p-6 hover:bg-blue-700 transition-colors">
                      <Search className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Explorer les produits</p>
                    </button>
                    <button className="bg-green-600 text-white rounded-xl p-6 hover:bg-green-700 transition-colors">
                      <Heart className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Mes favoris</p>
                    </button>
                    <button className="bg-orange-600 text-white rounded-xl p-6 hover:bg-orange-700 transition-colors">
                      <Gift className="w-8 h-8 mx-auto mb-3" />
                      <p className="font-semibold">Offres spéciales</p>
                    </button>
                  </motion.div>
                </div>
              )}

              {/* Products Tab */}
              {activeTab === "products" && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Produits disponibles</h3>
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          placeholder="Rechercher un produit..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <Filter className="w-4 h-4" />
                        <span>Filtrer</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {favoriteProducts.map((product) => (
                      <motion.div
                        key={product.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * product.id }}
                        className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="text-3xl">{product.image}</div>
                          <button className="text-red-600 hover:text-red-700">
                            <Heart className="w-5 h-5 fill-current" />
                          </button>
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-2">{product.name}</h4>
                        <p className="text-sm text-gray-600 mb-4">{product.category}</p>
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <p className="text-lg font-bold text-gray-900">{product.price} DH/{product.unit}</p>
                            <p className="text-sm text-gray-600">
                              {product.location} • {product.organic ? "Bio" : "Conventionnel"}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center space-x-1">
                              <Star className="w-4 h-4 text-yellow-400 fill-current" />
                              <span className="text-sm text-gray-600">{product.rating}</span>
                            </div>
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              product.inStock 
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {product.inStock ? 'Disponible' : 'Rupture'}
                            </span>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Voir</span>
                          </button>
                          <button className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            <ShoppingCart className="w-4 h-4" />
                            <span className="text-sm">Ajouter</span>
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
                    <h3 className="text-lg font-semibold text-gray-900">Historique d'achats</h3>
                    <div className="flex items-center space-x-4">
                      <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
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
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Agriculteur</th>
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
                              <p className="font-medium text-gray-900">{order.farmer}</p>
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
                              <p className="text-sm text-gray-600">{order.date}</p>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex space-x-2">
                                <button className="text-blue-600 hover:text-blue-700">
                                  <Eye className="w-4 h-4" />
                                </button>
                                {order.status === "delivered" && !order.rating && (
                                  <button className="text-yellow-600 hover:text-yellow-700">
                                    <Star className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Farmers Tab */}
              {activeTab === "farmers" && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Agriculteurs partenaires</h3>
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          placeholder="Rechercher un agriculteur..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <Filter className="w-4 h-4" />
                        <span>Filtrer</span>
                      </button>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900">Protection de la vie privée</h4>
                        <p className="text-sm text-blue-700 mt-1">
                          Pour protéger la vie privée de nos agriculteurs, certaines informations sensibles ne sont pas affichées aux consommateurs.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {favoriteFarmers.map((farmer) => (
                      <motion.div
                        key={farmer.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * farmer.id }}
                        className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="text-3xl">{farmer.image}</div>
                          <button className="text-red-600 hover:text-red-700">
                            <Heart className="w-5 h-5 fill-current" />
                          </button>
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-2">{farmer.name}</h4>
                        <p className="text-sm text-gray-600 mb-4">{farmer.specialty}</p>
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Localisation</span>
                            <span className="text-sm font-medium text-gray-900">{farmer.location}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Expérience</span>
                            <span className="text-sm font-medium text-gray-900">{farmer.years} ans</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Produits disponibles</span>
                            <span className="text-sm font-medium text-gray-900">{farmer.products}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600">{farmer.rating}</span>
                          </div>
                          <span className="text-sm text-gray-500">{farmer.orders} commandes</span>
                        </div>
                        {farmer.certified && (
                          <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            Certifié Bio
                          </span>
                        )}
                        <div className="flex space-x-2">
                          <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                            <Eye className="w-4 h-4" />
                            <span className="text-sm">Voir produits</span>
                          </button>
                          <button className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            <ShoppingCart className="w-4 h-4" />
                            <span className="text-sm">Commander</span>
                          </button>
                        </div>
                      </motion.div>
                    ))}
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
