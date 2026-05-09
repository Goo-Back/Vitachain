"use client"

import { motion } from "framer-motion"
import ProductCard from "@/components/cards/ProductCard"
import { Clock, Heart, TrendingUp } from "lucide-react"

const recentlyViewed = [
  {
    id: 1,
    name: "Tomates Cerise",
    farmer: "Ferme El Kalam",
    price: 45,
    rating: 4.8,
    reviews: 124,
    location: "Marrakech",
    image: "🍅",
    badge: "BIO"
  },
  {
    id: 2,
    name: "Concombre Frais",
    farmer: "Domaine Atlas",
    price: 25,
    rating: 4.9,
    reviews: 89,
    location: "Fès",
    image: "🥒",
    badge: "LOCAL"
  },
  {
    id: 3,
    name: "Poivron Rouge",
    farmer: "Citrus Souss",
    price: 35,
    rating: 4.7,
    reviews: 201,
    location: "Agadir",
    image: "🫑",
    badge: "FRESH"
  },
  {
    id: 4,
    name: "Carottes Bio",
    farmer: "Rucher Rif",
    price: 30,
    rating: 5.0,
    reviews: 67,
    location: "Al Hoceima",
    image: "🥕",
    badge: "PREMIUM"
  },
  {
    id: 5,
    name: "Aubergine",
    farmer: "Terres Souss",
    price: 28,
    rating: 4.6,
    reviews: 145,
    location: "Meknès",
    image: "🍆",
    badge: "ORGANIC"
  }
]

const suggestions = [
  {
    id: 6,
    name: "Lait Frais",
    farmer: "Ferme Tadla",
    price: 15,
    originalPrice: 20,
    rating: 4.9,
    reviews: 234,
    location: "Béni Mellal",
    image: "🥛",
    badge: "DEAL"
  },
  {
    id: 7,
    name: "Fromage Chèvre",
    farmer: "Domaine Rif",
    price: 85,
    rating: 4.8,
    reviews: 78,
    location: "Taza",
    image: "🧀",
    badge: "ARTISANAL"
  },
  {
    id: 8,
    name: "Yaourt Nature",
    farmer: "Laiterie Atlas",
    price: 12,
    rating: 4.7,
    reviews: 156,
    location: "Rabat",
    image: "🥛",
    badge: "FRESH"
  },
  {
    id: 9,
    name: "Beurre Bio",
    farmer: "Ferme El Kalam",
    price: 45,
    originalPrice: 55,
    rating: 5.0,
    reviews: 89,
    location: "Marrakech",
    image: "🧈",
    badge: "PREMIUM"
  },
  {
    id: 10,
    name: "Crème Fraîche",
    farmer: "Domaine Atlas",
    price: 25,
    rating: 4.6,
    reviews: 123,
    location: "Fès",
    image: "🥛",
    badge: "LOCAL"
  }
]

export default function PersonalizedSections() {
  return (
    <div className="space-y-16">
      {/* Recently Viewed */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center justify-between mb-8"
          >
            <div className="flex items-center space-x-3">
              <Clock className="w-6 h-6 text-green-600" />
              <h2 className="text-2xl font-bold text-gray-900">Recently Viewed</h2>
            </div>
            <button className="text-green-600 hover:text-green-700 font-medium transition-colors">
              View All
            </button>
          </motion.div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {recentlyViewed.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.05 }}
              >
                <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-3">
                  <div className="w-full h-20 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center mb-3">
                    <span className="text-3xl">{product.image}</span>
                  </div>
                  <h4 className="font-medium text-gray-900 text-sm mb-1 line-clamp-1">
                    {product.name}
                  </h4>
                  <p className="text-xs text-gray-500 mb-2">{product.farmer}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-green-600">{product.price} DH</span>
                    <div className="flex items-center space-x-1">
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${
                              i < Math.floor(product.rating)
                                ? "bg-yellow-400"
                                : "bg-gray-300"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-xs text-gray-500">({product.reviews})</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Suggestions for You */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center justify-between mb-8"
          >
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-6 h-6 text-green-600" />
              <h2 className="text-2xl font-bold text-gray-900">Suggestions for You</h2>
            </div>
            <button className="text-green-600 hover:text-green-700 font-medium transition-colors">
              See More
            </button>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {suggestions.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="lg:col-span-1"
              >
                <ProductCard {...product} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Favourites */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center justify-between mb-8"
          >
            <div className="flex items-center space-x-3">
              <Heart className="w-6 h-6 text-red-500" />
              <h2 className="text-2xl font-bold text-gray-900">Your Favourites</h2>
            </div>
            <button className="text-green-600 hover:text-green-700 font-medium transition-colors">
              Manage Favourites
            </button>
          </motion.div>

          <div className="flex space-x-4 overflow-x-auto pb-4">
            {recentlyViewed.slice(0, 5).map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="flex-shrink-0 w-32"
              >
                <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-3">
                  <div className="w-full h-20 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center mb-2">
                    <span className="text-2xl">{product.image}</span>
                  </div>
                  <h4 className="font-medium text-gray-900 text-xs mb-1 line-clamp-1">
                    {product.name}
                  </h4>
                  <span className="text-sm font-bold text-green-600">{product.price} DH</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
