"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import ProductCard from "@/components/cards/ProductCard"
import { Filter, Grid3x3, List } from "lucide-react"

const categories = ["All", "Men", "Women", "Kids", "Home", "Seasonal"]
const sortBy = ["Popular", "Newest", "Price: Low to High", "Price: High to Low"]

const exploreProducts = [
  {
    id: 1,
    name: "Tomates Bio Premium",
    farmer: "Ferme El Kalam",
    price: 89,
    originalPrice: 120,
    rating: 4.8,
    reviews: 124,
    location: "Marrakech",
    image: "🍅",
    badge: "FLASH DEAL",
    height: "h-64"
  },
  {
    id: 2,
    name: "Huile d'Olive Extra",
    farmer: "Domaine Atlas",
    price: 65,
    rating: 4.9,
    reviews: 89,
    location: "Fès",
    image: "🫒",
    badge: "PREMIUM",
    height: "h-80"
  },
  {
    id: 3,
    name: "Agrumes Medley",
    farmer: "Citrus Souss",
    price: 45,
    originalPrice: 65,
    rating: 4.7,
    reviews: 201,
    location: "Agadir",
    image: "🍊",
    badge: "FRESH",
    height: "h-56"
  },
  {
    id: 4,
    name: "Miel de Montagne",
    farmer: "Rucher Rif",
    price: 95,
    originalPrice: 120,
    rating: 5.0,
    reviews: 67,
    location: "Al Hoceima",
    image: "🍯",
    badge: "RARE",
    height: "h-72"
  },
  {
    id: 5,
    name: "Légumes Mixtes",
    farmer: "Terres Souss",
    price: 55,
    rating: 4.6,
    reviews: 145,
    location: "Meknès",
    image: "🥬",
    badge: "BIO",
    height: "h-60"
  },
  {
    id: 6,
    name: "Fruits Rouges",
    farmer: "Ferme Tadla",
    price: 75,
    rating: 4.9,
    reviews: 234,
    location: "Béni Mellal",
    image: "🍓",
    badge: "SEASONAL",
    height: "h-68"
  },
  {
    id: 7,
    name: "Herbes Aromatiques",
    farmer: "Jardin Rif",
    price: 35,
    rating: 4.8,
    reviews: 156,
    location: "Taza",
    image: "🌿",
    badge: "FRESH",
    height: "h-52"
  },
  {
    id: 8,
    name: "Noix et Graines",
    farmer: "Domaine Atlas",
    price: 85,
    originalPrice: 100,
    rating: 4.7,
    reviews: 78,
    location: "Fès",
    image: "🥜",
    badge: "DEAL",
    height: "h-64"
  }
]

export default function ExploreGrid() {
  const [activeCategory, setActiveCategory] = useState("All")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")

  return (
    <section className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Explore</h2>
          <p className="text-gray-600">Discover fresh products from local farmers</p>
        </motion.div>

        {/* Filters and Controls */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8 space-y-4 lg:space-y-0"
        >
          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeCategory === category
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* View Controls */}
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
            
            <div className="flex items-center bg-gray-100 rounded-lg">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-l-lg transition-colors ${
                  viewMode === "grid" ? "bg-white shadow-sm" : "hover:bg-gray-200"
                }`}
              >
                <Grid3x3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-r-lg transition-colors ${
                  viewMode === "list" ? "bg-white shadow-sm" : "hover:bg-gray-200"
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Pinterest-style Grid */}
        <div className={`columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-4 space-y-4 ${
          viewMode === "list" ? "columns-1" : ""
        }`}>
          {exploreProducts.map((product, index) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`break-inside-avoid ${
                viewMode === "list" ? "mb-4" : ""
              }`}
            >
              <div className={`${viewMode === "list" ? "flex space-x-4" : ""}`}>
                {viewMode === "grid" ? (
                  <ProductCard {...product} />
                ) : (
                  <>
                    <div className="w-32 h-32 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <span className="text-4xl">{product.image}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{product.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">by {product.farmer}</p>
                      <p className="text-sm text-gray-500 mb-2">{product.location}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-bold text-green-600">{product.price} DH</span>
                        <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors">
                          Add to Cart
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Load More */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12"
        >
          <button className="inline-flex items-center space-x-2 bg-white border-2 border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:border-green-600 hover:text-green-600 transition-colors">
            <span>Load More Products</span>
          </button>
        </motion.div>
      </div>
    </section>
  )
}
