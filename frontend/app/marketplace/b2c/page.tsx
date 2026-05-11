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
  Heart,
  Utensils
} from "lucide-react"

export default function B2CMarketplace() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedCity, setSelectedCity] = useState("all")
  const [priceRange, setPriceRange] = useState({ min: "", max: "" })

  const categories = [
    { id: "all", name: "Toutes les catégories" },
    { id: "appetizers", name: "Entrées" },
    { id: "mains", name: "Plats principaux" },
    { id: "desserts", name: "Desserts" },
    { id: "beverages", name: "Boissons" },
    { id: "specialties", name: "Spécialités" }
  ]

  const cities = [
    { id: "all", name: "Toutes les villes" },
    { id: "casablanca", name: "Casablanca" },
    { id: "rabat", name: "Rabat" },
    { id: "marrakech", name: "Marrakech" },
    { id: "fes", name: "Fès" },
    { id: "tangier", name: "Tanger" },
    { id: "agadir", name: "Agadir" }
  ]

  const restaurants = [
    {
      id: 1,
      name: "Restaurant Le Terroir",
      location: "Casablanca",
      city: "casablanca",
      rating: 4.8,
      totalOrders: 1250,
      deliveryTime: "30-45 min",
      deliveryFee: 15,
      minOrder: 50,
      specialties: ["Cuisine marocaine", "Tagine", "Couscous"],
      image: "🍽️",
      certified: true,
      yearsOpen: 8,
      popularDishes: ["Tagine d'agneau", "Couscous royal", "Pastilla"],
      lastOrder: "Il y a 10 minutes",
      priceRange: "80-250 DH"
    },
    {
      id: 2,
      name: "Saveurs d'Orient",
      location: "Rabat",
      city: "rabat",
      rating: 4.9,
      totalOrders: 890,
      deliveryTime: "25-40 min",
      deliveryFee: 12,
      minOrder: 40,
      specialties: ["Cuisine orientale", "Grillades", "Salades"],
      image: "🥘",
      certified: true,
      yearsOpen: 5,
      popularDishes: ["Brochettes", "Tajine poulet", "Salade marocaine"],
      lastOrder: "Il y a 25 minutes",
      priceRange: "60-200 DH"
    },
    {
      id: 3,
      name: "La Table du Sud",
      location: "Marrakech",
      city: "marrakech",
      rating: 4.7,
      totalOrders: 670,
      deliveryTime: "35-50 min",
      deliveryFee: 18,
      minOrder: 60,
      specialties: ["Cuisine du sud", "Berbère", "Traditionnelle"],
      image: "🍲",
      certified: false,
      yearsOpen: 12,
      popularDishes: ["Mrouzia", "Bastilla", "Harira"],
      lastOrder: "Il y a 45 minutes",
      priceRange: "70-180 DH"
    }
  ]

  const dishes = [
    {
      id: 1,
      name: "Tagine d'Agneau",
      restaurantId: 1,
      restaurantName: "Restaurant Le Terroir",
      category: "mains",
      price: 120,
      rating: 4.8,
      orders: 245,
      image: "🍖",
      description: "Tagine traditionnel avec agneau tendre, pruneaux et amandes",
      preparationTime: "45 min",
      spicy: false,
      vegetarian: false,
      popular: true,
      ingredients: ["Agneau", "Pruneaux", "Amandes", "Épices marocaines"],
      allergens: ["Fruits à coque"]
    },
    {
      id: 2,
      name: "Couscous Royal",
      restaurantId: 1,
      restaurantName: "Restaurant Le Terroir",
      category: "mains",
      price: 150,
      rating: 4.9,
      orders: 189,
      image: "🍲",
      description: "Couscous royal avec légumes, viande et boulettes",
      preparationTime: "50 min",
      spicy: false,
      vegetarian: false,
      popular: true,
      ingredients: ["Semoule", "Légumes", "Viande", "Boulettes"],
      allergens: ["Gluten"]
    },
    {
      id: 3,
      name: "Salade Marocaine",
      restaurantId: 2,
      restaurantName: "Saveurs d'Orient",
      category: "appetizers",
      price: 35,
      rating: 4.7,
      orders: 156,
      image: "🥗",
      description: "Salade fraîche avec tomates, concombres, oignons et herbes",
      preparationTime: "15 min",
      spicy: false,
      vegetarian: true,
      popular: false,
      ingredients: ["Tomates", "Concombres", "Oignons", "Herbes aromatiques"],
      allergens: []
    },
    {
      id: 4,
      name: "Pastilla au Poulet",
      restaurantId: 1,
      restaurantName: "Restaurant Le Terroir",
      category: "mains",
      price: 85,
      rating: 4.8,
      orders: 178,
      image: "🥧",
      description: "Pastilla feuilletée au poulet et amandes",
      preparationTime: "40 min",
      spicy: false,
      vegetarian: false,
      popular: true,
      ingredients: ["Poulet", "Amandes", "Feuilles de brick", "Cannelle"],
      allergens: ["Œufs", "Fruits à coque", "Gluten"]
    }
  ]

  const stats = {
    totalRestaurants: 45,
    totalDishes: 1200,
    activeOrders: 234,
    avgDeliveryTime: "35 min"
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
                <Link href="/marketplace/b2b" className="text-gray-600 hover:text-gray-900">
                  Marketplace B2B
                </Link>
                <Link href="/marketplace/b2c" className="text-green-600 font-medium">
                  Marketplace B2C
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login" className="text-gray-700 hover:text-gray-900 font-medium">
                Se connecter
              </Link>
              <Link
                href="/signup/consumer"
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
                <p className="text-sm text-gray-600 mb-1">Restaurants partenaires</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalRestaurants}</p>
              </div>
              <Store className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Plats disponibles</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalDishes}</p>
              </div>
              <Utensils className="w-8 h-8 text-orange-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Commandes actives</p>
                <p className="text-2xl font-bold text-gray-900">{stats.activeOrders}</p>
              </div>
              <ShoppingCart className="w-8 h-8 text-blue-600" />
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
                  placeholder="Rechercher des plats ou restaurants..."
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
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {cities.map(city => (
                <option key={city.id} value={city.id}>
                  {city.name}
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
            <span className="text-sm text-gray-600">DH</span>
          </div>
        </motion.div>

        {/* Featured Restaurants */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Restaurants partenaires</h2>
            <Link href="/marketplace/b2c/restaurants" className="text-green-600 hover:text-green-700 font-medium flex items-center space-x-1">
              <span>Voir tout</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <motion.div
                key={restaurant.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + (restaurant.id * 0.1) }}
                className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl">{restaurant.image}</div>
                  <div className="flex items-center space-x-2">
                    {restaurant.certified && (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        Certifié
                      </span>
                    )}
                    <span className="text-sm text-gray-500">{restaurant.lastOrder}</span>
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{restaurant.name}</h3>
                <div className="flex items-center text-sm text-gray-600 mb-3">
                  <MapPin className="w-4 h-4 mr-1" />
                  {restaurant.location}
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Spécialités</span>
                    <span className="font-medium text-gray-900">{restaurant.specialties[0]}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Expérience</span>
                    <span className="font-medium text-gray-900">{restaurant.yearsOpen} ans</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Commandes</span>
                    <span className="font-medium text-gray-900">{restaurant.totalOrders}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm font-medium text-gray-900">{restaurant.rating}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="w-3 h-3" />
                    <span>{restaurant.deliveryTime}</span>
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Livraison</span>
                    <span className="font-medium text-gray-900">{restaurant.deliveryFee} DH</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Commande min.</span>
                    <span className="font-medium text-gray-900">{restaurant.minOrder} DH</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Prix moyen</span>
                    <span className="font-medium text-gray-900">{restaurant.priceRange}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Store className="w-4 h-4" />
                    <span className="text-sm">Voir menu</span>
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

        {/* Popular Dishes */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Plats populaires</h2>
            <div className="flex items-center space-x-4">
              <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500">
                <option value="popularity">Popularité</option>
                <option value="price-low">Prix croissant</option>
                <option value="price-high">Prix décroissant</option>
                <option value="rating">Meilleures notes</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {dishes.map((dish) => (
              <motion.div
                key={dish.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + (dish.id * 0.1) }}
                className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">{dish.image}</div>
                  <div className="flex items-center space-x-1">
                    {dish.popular && (
                      <span className="inline-flex items-center px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">
                        Populaire
                      </span>
                    )}
                    {dish.vegetarian && (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        Végétarien
                      </span>
                    )}
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{dish.name}</h3>
                <p className="text-sm text-gray-600 mb-1">{dish.restaurantName}</p>
                <p className="text-xs text-gray-500 mb-4 line-clamp-2">{dish.description}</p>
                
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xl font-bold text-gray-900">{dish.price} DH</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600">{dish.rating}</span>
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Préparation</span>
                    <span className="font-medium text-gray-900">{dish.preparationTime}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Commandes</span>
                    <span className="font-medium text-gray-900">{dish.orders}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Heart className="w-4 h-4" />
                    <span className="text-sm">Favoris</span>
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
          <h2 className="text-3xl font-bold mb-4">Commandez les meilleurs plats locaux</h2>
          <p className="text-xl mb-6 max-w-2xl mx-auto">
            Découvrez des restaurants qui utilisent des ingrédients frais et locaux
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup/consumer"
              className="bg-white text-green-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Créer un compte
            </Link>
            <Link
              href="/signup/restaurant"
              className="bg-emerald-700 text-white px-6 py-3 rounded-lg hover:bg-emerald-800 transition-colors font-medium"
            >
              Devenir restaurant partenaire
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
