"use client"

import { motion } from "framer-motion"
import { useInView } from "react-intersection-observer"
import Link from "next/link"
import { 
  ShoppingCart, 
  Tractor, 
  Store, 
  Package, 
  Star, 
  MapPin, 
  Clock,
  TrendingUp,
  Shield
} from "lucide-react"

const features = [
  {
    icon: ShoppingCart,
    title: "Marketplace B2B",
    description: "Achetez directement des producteurs locaux avec des prix transparents et équitables",
    color: "from-green-500 to-emerald-600",
    stats: { label: "Transactions", value: "50K+" }
  },
  {
    icon: Tractor,
    title: "Katara IoT",
    description: "Agriculture intelligente avec capteurs IoT pour optimiser les rendements",
    color: "from-blue-500 to-cyan-600",
    stats: { label: "Hectares", value: "10K+" }
  },
  {
    icon: Store,
    title: "SecondServe",
    description: "Réduisez le gaspillage alimentaire avec des offres spéciales restaurants",
    color: "from-orange-500 to-red-600",
    stats: { label: "Repas sauvés", value: "100K+" }
  },
]

const products = [
  {
    id: 1,
    name: "Tomates Bio",
    farmer: "Ferme El Kalam",
    price: "12 DH/kg",
    rating: 4.8,
    reviews: 124,
    location: "Marrakech",
    image: "🍅",
    badge: "Bio"
  },
  {
    id: 2,
    name: "Huile d'Olive",
    farmer: "Domaine Atlas",
    price: "85 DH/L",
    rating: 4.9,
    reviews: 89,
    location: "Fès",
    image: "🫒",
    badge: "AOP"
  },
  {
    id: 3,
    name: "Agrumes Frais",
    farmer: "Citrus Souss",
    price: "8 DH/kg",
    rating: 4.7,
    reviews: 201,
    location: "Agadir",
    image: "🍊",
    badge: "Local"
  },
  {
    id: 4,
    name: "Miel de Montagne",
    farmer: "Rucher Rif",
    price: "120 DH/kg",
    rating: 5.0,
    reviews: 67,
    location: "Al Hoceima",
    image: "🍯",
    badge: "Artisanal"
  },
]

export default function MarketplaceFeatures() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <section ref={ref} className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Notre Ecosysteme
            <span className="block bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mt-2">
              Agritech Complet
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Des solutions innovantes pour transformer l'agriculture marocaine 
            et créer une chaîne d'approvisionnement transparente et efficace.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 overflow-hidden">
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-5 group-hover:opacity-10 transition-opacity`} />
                
                {/* Content */}
                <div className="relative p-8">
                  {/* Icon */}
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} text-white mb-6`}>
                    <feature.icon className="w-8 h-8" />
                  </div>

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {feature.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 mb-6 leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Stats */}
                  <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                    <div>
                      <div className="text-2xl font-bold text-gray-900">
                        {feature.stats.value}
                      </div>
                      <div className="text-sm text-gray-500">
                        {feature.stats.label}
                      </div>
                    </div>
                    <Link
                      href="#"
                      className="inline-flex items-center text-green-600 hover:text-green-700 font-medium group"
                    >
                      Explorer
                      <TrendingUp className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Products Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-gradient-to-br from-gray-50 to-green-50 rounded-3xl p-8 lg:p-12"
        >
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Produits du Moment
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Découvrez les meilleurs produits de nos agriculteurs locaux, 
              fraîchement récoltés et livrés directement chez vous.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
                className="group"
              >
                <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden">
                  {/* Product Image */}
                  <div className="relative h-32 bg-gradient-to-br from-green-100 to-emerald-100 flex items-center justify-center">
                    <span className="text-5xl">{product.image}</span>
                    <div className="absolute top-2 right-2">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {product.badge}
                      </span>
                    </div>
                  </div>

                  {/* Product Info */}
                  <div className="p-4">
                    <h4 className="font-semibold text-gray-900 mb-1">
                      {product.name}
                    </h4>
                    <p className="text-sm text-gray-500 mb-2">
                      {product.farmer}
                    </p>

                    {/* Rating */}
                    <div className="flex items-center space-x-1 mb-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${
                              i < Math.floor(product.rating)
                                ? "text-yellow-400 fill-current"
                                : "text-gray-300"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-sm text-gray-500">
                        {product.rating} ({product.reviews})
                      </span>
                    </div>

                    {/* Location */}
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <MapPin className="w-4 h-4 mr-1" />
                      {product.location}
                    </div>

                    {/* Price and CTA */}
                    <div className="flex items-center justify-between">
                      <div className="text-lg font-bold text-green-600">
                        {product.price}
                      </div>
                      <button className="bg-green-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-green-700 transition-colors">
                        Commander
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* View All Button */}
          <div className="text-center mt-8">
            <Link
              href="/marketplace"
              className="inline-flex items-center justify-center px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all transform hover:scale-105"
            >
              Voir tous les produits
              <ShoppingCart className="ml-2 w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
