"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { Search, Filter, ShoppingCart, Star, Leaf, MapPin, Clock, ChevronDown } from "lucide-react"

const products = [
  {
    id: 1,
    name: "Tomates Bio Premium",
    farmer: "Ferme El Kalam",
    price: 120,
    unit: "kg",
    rating: 4.8,
    reviews: 124,
    image: "🍅",
    category: "Légumes",
    location: "Marrakech",
    organic: true,
    inStock: true,
    badge: "BIO"
  },
  {
    id: 2,
    name: "Huile d'Olive Extra Vierge",
    farmer: "Domaine Atlas",
    price: 85,
    unit: "L",
    rating: 4.9,
    reviews: 89,
    image: "🫒",
    category: "Huiles",
    location: "Fès",
    organic: true,
    inStock: true,
    badge: "AOP"
  },
  {
    id: 3,
    name: "Agrumes Medjool",
    farmer: "Citrus Souss",
    price: 65,
    unit: "kg",
    rating: 4.7,
    reviews: 56,
    image: "🍊",
    category: "Fruits",
    location: "Agadir",
    organic: false,
    inStock: true,
    badge: "LOCAL"
  },
  {
    id: 4,
    name: "Miel de Thym Sauvage",
    farmer: "Rucher Azilal",
    price: 150,
    unit: "kg",
    rating: 5.0,
    reviews: 203,
    image: "🍯",
    category: "Miels",
    location: "Azilal",
    organic: true,
    inStock: false,
    badge: "RARE"
  },
  {
    id: 5,
    name: "Noix de Grenoble",
    farmer: "Ferme Ifrane",
    price: 95,
    unit: "kg",
    rating: 4.6,
    reviews: 78,
    image: "🥜",
    category: "Fruits Secs",
    location: "Ifrane",
    organic: true,
    inStock: true,
    badge: "BIO"
  },
  {
    id: 6,
    name: "Herbes Aromatiques",
    farmer: "Jardin Rif",
    price: 25,
    unit: "botte",
    rating: 4.5,
    reviews: 45,
    image: "🌿",
    category: "Herbes",
    location: "Taza",
    organic: true,
    inStock: true,
    badge: "FRESH"
  }
]

const categories = ["Tous", "Légumes", "Fruits", "Huiles", "Miels", "Fruits Secs", "Herbes", "Céréales"]
const sortOptions = ["Pertinence", "Prix croissant", "Prix décroissant", "Meilleures notes", "Plus récents"]

export default function MarketplacePage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("Tous")
  const [sortBy, setSortBy] = useState("Pertinence")
  const [showFilters, setShowFilters] = useState(false)
  const [priceRange, setPriceRange] = useState({ min: 0, max: 500 })
  const [organicOnly, setOrganicOnly] = useState(false)

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.farmer.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === "Tous" || product.category === selectedCategory
    const matchesPrice = product.price >= priceRange.min && product.price <= priceRange.max
    const matchesOrganic = !organicOnly || product.organic
    
    return matchesSearch && matchesCategory && matchesPrice && matchesOrganic
  })

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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Marketplace</h1>
              <p className="text-lg text-gray-600">Découvrez les meilleurs produits de nos agriculteurs locaux</p>
            </motion.div>

            {/* Search and Filters */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6 mb-6"
            >
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search Bar */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Rechercher des produits, agriculteurs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                {/* Category Filter */}
                <div className="relative">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                </div>

                {/* Sort */}
                <div className="relative">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {sortOptions.map(option => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                </div>

                {/* Advanced Filters Toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Filter className="w-5 h-5" />
                  <span>Filtres</span>
                </button>
              </div>

              {/* Advanced Filters */}
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-6 pt-6 border-t border-gray-200"
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Price Range */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fourchette de prix (DH)
                      </label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          placeholder="Min"
                          value={priceRange.min}
                          onChange={(e) => setPriceRange(prev => ({ ...prev, min: parseInt(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                        <span>-</span>
                        <input
                          type="number"
                          placeholder="Max"
                          value={priceRange.max}
                          onChange={(e) => setPriceRange(prev => ({ ...prev, max: parseInt(e.target.value) || 500 }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                    </div>

                    {/* Organic Only */}
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="organic"
                        checked={organicOnly}
                        onChange={(e) => setOrganicOnly(e.target.checked)}
                        className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <label htmlFor="organic" className="ml-2 text-sm font-medium text-gray-700">
                        Produits biologiques uniquement
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>

            {/* Results Count */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                {filteredProducts.length} produit{filteredProducts.length > 1 ? 's' : ''} trouvé{filteredProducts.length > 1 ? 's' : ''}
              </p>
            </div>

            {/* Products Grid */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            >
              {filteredProducts.map((product, index) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow overflow-hidden group"
                >
                  {/* Product Image */}
                  <div className="relative h-48 bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center">
                    <div className="text-6xl group-hover:scale-110 transition-transform">
                      {product.image}
                    </div>
                    
                    {/* Badge */}
                    <div className="absolute top-3 left-3">
                      <span className="px-3 py-1 bg-green-600 text-white text-xs font-semibold rounded-full">
                        {product.badge}
                      </span>
                    </div>

                    {/* Stock Status */}
                    {!product.inStock && (
                      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                        <span className="text-white font-semibold">Rupture de stock</span>
                      </div>
                    )}
                  </div>

                  {/* Product Info */}
                  <div className="p-4">
                    <div className="mb-2">
                      <h3 className="font-semibold text-gray-900 text-lg mb-1">{product.name}</h3>
                      <p className="text-sm text-gray-600 flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        {product.farmer} • {product.location}
                      </p>
                    </div>

                    {/* Rating */}
                    <div className="flex items-center mb-3">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${i < Math.floor(product.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                          />
                        ))}
                      </div>
                      <span className="ml-2 text-sm text-gray-600">
                        {product.rating} ({product.reviews})
                      </span>
                    </div>

                    {/* Price and CTA */}
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-2xl font-bold text-gray-900">{product.price}</span>
                        <span className="text-gray-600 ml-1">DH/{product.unit}</span>
                      </div>
                      <button
                        disabled={!product.inStock}
                        className={`p-2 rounded-lg transition-colors ${
                          product.inStock
                            ? 'bg-green-600 text-white hover:bg-green-700'
                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        <ShoppingCart className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Empty State */}
            {filteredProducts.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun produit trouvé</h3>
                <p className="text-gray-600">Essayez de modifier vos filtres ou votre recherche</p>
              </motion.div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
