"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { 
  Search, 
  Filter, 
  MapPin, 
  Star, 
  Package, 
  Users,
  ShoppingCart,
  TrendingUp,
  Truck,
  Leaf,
  Store,
  ChevronRight,
  Clock,
  CheckCircle,
  Eye
} from "lucide-react"

export default function B2BMarketplace() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedRegion, setSelectedRegion] = useState("all")
  const [priceRange, setPriceRange] = useState({ min: "", max: "" })

  const categories = [
    { id: "all", name: "Toutes les catégories" },
    { id: "vegetables", name: "Légumes" },
    { id: "fruits", name: "Fruits" },
    { id: "dairy", name: "Produits laitiers" },
    { id: "meat", name: "Viandes" },
    { id: "grains", name: "Céréales" },
    { id: "honey", name: "Miels" },
    { id: "oils", name: "Huiles" }
  ]

  const regions = [
    { id: "all", name: "Toutes les régions" },
    { id: "casablanca", name: "Casablanca-Settat" },
    { id: "rabat", name: "Rabat-Salé-Kénitra" },
    { id: "marrakech", name: "Marrakech-Safi" },
    { id: "fes", name: "Fès-Meknès" },
    { id: "tangier", name: "Tanger-Tétouan-Al Hoceïma" }
  ]

  const farmers = [
    {
      id: 1,
      name: "Ferme El Kalam",
      location: "Marrakech",
      region: "marrakech",
      rating: 4.8,
      totalOrders: 156,
      responseTime: "2h",
      deliveryTime: "24h",
      specialties: ["Légumes bio", "Tomates", "Poivrons"],
      image: "👨‍🌾",
      certified: true,
      yearsExperience: 12,
      totalProducts: 15,
      lastOrder: "Il y a 2 heures"
    },
    {
      id: 2,
      name: "Domaine Atlas",
      location: "Fès",
      region: "fes",
      rating: 4.9,
      totalOrders: 203,
      responseTime: "1h",
      deliveryTime: "48h",
      specialties: ["Huile d'olive", "Olives", "Conserves"],
      image: "👩‍🌾",
      certified: true,
      yearsExperience: 25,
      totalProducts: 8,
      lastOrder: "Il y a 30 minutes"
    },
    {
      id: 3,
      name: "Rucher Azilal",
      location: "Azilal",
      region: "marrakech",
      rating: 5.0,
      totalOrders: 89,
      responseTime: "3h",
      deliveryTime: "72h",
      specialties: ["Miel sauvage", "Miel de thym", "Propolis"],
      image: "👩‍🌾",
      certified: true,
      yearsExperience: 15,
      totalProducts: 6,
      lastOrder: "Il y a 5 heures"
    }
  ]

  const products = [
    {
      id: 1,
      name: "Tomates Bio Premium",
      farmerId: 1,
      farmerName: "Ferme El Kalam",
      category: "vegetables",
      price: 25,
      unit: "kg",
      minOrder: 10,
      stock: 150,
      rating: 4.8,
      orders: 45,
      image: "🍅",
      organic: true,
      seasonal: true,
      delivery: "24h",
      description: "Tomates cultivées sans pesticides, récoltées à maturité"
    },
    {
      id: 2,
      name: "Huile d'Olive Extra Vierge",
      farmerId: 2,
      farmerName: "Domaine Atlas",
      category: "oils",
      price: 85,
      unit: "L",
      minOrder: 5,
      stock: 50,
      rating: 4.9,
      orders: 67,
      image: "🫒",
      organic: true,
      seasonal: false,
      delivery: "48h",
      description: "Huile d'olive pressée à froid, première pression"
    },
    {
      id: 3,
      name: "Miel de Thym Sauvage",
      farmerId: 3,
      farmerName: "Rucher Azilal",
      category: "honey",
      price: 150,
      unit: "kg",
      minOrder: 1,
      stock: 20,
      rating: 5.0,
      orders: 23,
      image: "🍯",
      organic: true,
      seasonal: true,
      delivery: "72h",
      description: "Miel récolté dans les montagnes de l'Atlas"
    }
  ]

  const stats = {
    totalFarmers: 156,
    totalProducts: 1240,
    activeOrders: 89,
    avgDeliveryTime: "36h"
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center space-x-2">
                <Leaf className="w-8 h-8 text-green-600" />
                <span className="text-xl font-bold text-gray-900">VitaChain</span>
              </Link>
              <div className="hidden md:flex items-center space-x-6">
                <Link href="/marketplace/b2b" className="text-green-600 font-medium">
                  Marketplace B2B
                </Link>
                <Link href="/marketplace/b2c" className="text-gray-600 hover:text-gray-900">
                  Marketplace B2C
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login" className="text-gray-700 hover:text-gray-900 font-medium">
                Se connecter
              </Link>
              <Link
                href="/signup/farmer"
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                S'inscrire
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Agriculteurs partenaires</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalFarmers}</p>
              </div>
              <Users className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Produits disponibles</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
              </div>
              <Package className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Commandes actives</p>
                <p className="text-2xl font-bold text-gray-900">{stats.activeOrders}</p>
              </div>
              <ShoppingCart className="w-8 h-8 text-orange-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Livraison moyenne</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avgDeliveryTime}</p>
              </div>
              <Truck className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg p-6 shadow-sm mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Rechercher des produits ou agriculteurs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>

            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {regions.map(region => (
                <option key={region.id} value={region.id}>
                  {region.name}
                </option>
              ))}
            </select>

            <button className="flex items-center justify-center space-x-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Filter className="w-4 h-4" />
              <span>Filtres avancés</span>
            </button>
          </div>

          {/* Price Range */}
          <div className="mt-4 flex items-center space-x-4">
            <span className="text-sm text-gray-600">Prix:</span>
            <input
              type="number"
              placeholder="Min"
              value={priceRange.min}
              onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <span className="text-gray-500">-</span>
            <input
              type="number"
              placeholder="Max"
              value={priceRange.max}
              onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <span className="text-sm text-gray-600">DH/unité</span>
          </div>
        </motion.div>

        {/* Featured Farmers */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Agriculteurs partenaires</h2>
            <Link href="/marketplace/b2b/farmers" className="text-green-600 hover:text-green-700 font-medium flex items-center space-x-1">
              <span>Voir tout</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {farmers.map((farmer) => (
              <motion.div
                key={farmer.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + (farmer.id * 0.1) }}
                className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl">{farmer.image}</div>
                  <div className="flex items-center space-x-2">
                    {farmer.certified && (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        Certifié
                      </span>
                    )}
                    <span className="text-sm text-gray-500">{farmer.lastOrder}</span>
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{farmer.name}</h3>
                <div className="flex items-center text-sm text-gray-600 mb-3">
                  <MapPin className="w-4 h-4 mr-1" />
                  {farmer.location}
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Expérience</span>
                    <span className="font-medium text-gray-900">{farmer.yearsExperience} ans</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Produits</span>
                    <span className="font-medium text-gray-900">{farmer.totalProducts}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Commandes</span>
                    <span className="font-medium text-gray-900">{farmer.totalOrders}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm font-medium text-gray-900">{farmer.rating}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="w-3 h-3" />
                    <span>{farmer.responseTime}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Store className="w-4 h-4" />
                    <span className="text-sm">Voir produits</span>
                  </button>
                  <button className="flex-1 flex items-center justify-center space-x-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    <ShoppingCart className="w-4 h-4" />
                    <span className="text-sm">Commander</span>
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Products Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Produits disponibles</h2>
            <div className="flex items-center space-x-4">
              <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500">
                <option value="relevance">Pertinence</option>
                <option value="price-low">Prix croissant</option>
                <option value="price-high">Prix décroissant</option>
                <option value="rating">Meilleures notes</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((product) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + (product.id * 0.1) }}
                className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">{product.image}</div>
                  <div className="flex items-center space-x-1">
                    {product.organic && (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        Bio
                      </span>
                    )}
                    {product.seasonal && (
                      <span className="inline-flex items-center px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">
                        Saison
                      </span>
                    )}
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{product.name}</h3>
                <p className="text-sm text-gray-600 mb-1">{product.farmerName}</p>
                <p className="text-xs text-gray-500 mb-4 line-clamp-2">{product.description}</p>
                
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xl font-bold text-gray-900">{product.price} DH</p>
                    <p className="text-sm text-gray-600">/{product.unit}</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600">{product.rating}</span>
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Stock</span>
                    <span className="font-medium text-green-600">{product.stock} {product.unit}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Min. commande</span>
                    <span className="font-medium text-gray-900">{product.minOrder} {product.unit}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Livraison</span>
                    <span className="font-medium text-blue-600">{product.delivery}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Eye className="w-4 h-4" />
                    <span className="text-sm">Détails</span>
                  </button>
                  <button className="flex-1 flex items-center justify-center space-x-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    <ShoppingCart className="w-4 h-4" />
                    <span className="text-sm">Ajouter</span>
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-8 text-center text-white"
        >
          <h2 className="text-3xl font-bold mb-4">Rejoignez notre marketplace B2B</h2>
          <p className="text-xl mb-6 max-w-2xl mx-auto">
            Connectez-vous avec les meilleurs agriculteurs et transformez votre approvisionnement
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup/farmer"
              className="bg-white text-green-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Devenir agriculteur partenaire
            </Link>
            <Link
              href="/signup/restaurant"
              className="bg-emerald-700 text-white px-6 py-3 rounded-lg hover:bg-emerald-800 transition-colors font-medium"
            >
              S'inscrire comme restaurant
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
