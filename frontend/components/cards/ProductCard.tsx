"use client"

import { useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Heart, Star, ShoppingCart, MapPin, Eye, Leaf } from "lucide-react"

interface ProductCardProps {
  id: number
  name: string
  farmer: string
  price: number
  originalPrice?: number
  rating: number
  reviews: number
  location: string
  image: string
  badge?: string
  isFavourite?: boolean
  category?: string
}

export default function ProductCard({
  id,
  name,
  farmer,
  price,
  originalPrice,
  rating,
  reviews,
  location,
  image,
  badge,
  isFavourite = false,
  category = "produce"
}: ProductCardProps) {
  const [favourite, setFavourite] = useState(isFavourite)
  const [isHovered, setIsHovered] = useState(false)

  const toggleFavourite = (e: React.MouseEvent) => {
    e.preventDefault()
    setFavourite(!favourite)
  }

  const discount = originalPrice ? Math.round(((originalPrice - price) / originalPrice) * 100) : 0

  return (
    <motion.div
      whileHover={{ y: -4 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="group relative bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden"
    >
      {/* Product Image */}
      <div className="relative h-48 bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center overflow-hidden">
        <span className="text-6xl transform transition-transform duration-300 group-hover:scale-110">
          {image}
        </span>
        
        {/* Badge */}
        {badge && (
          <div className="absolute top-2 left-2">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              {badge}
            </span>
          </div>
        )}

        {/* Discount Badge */}
        {discount > 0 && (
          <div className="absolute top-2 right-2">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
              -{discount}%
            </span>
          </div>
        )}

        {/* Favourite Button */}
        <button
          onClick={toggleFavourite}
          className="absolute top-2 right-2 p-2 bg-white/80 backdrop-blur-sm rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Heart
            className={`w-4 h-4 transition-colors ${
              favourite ? "fill-red-500 text-red-500" : "text-gray-600"
            }`}
          />
        </button>

        {/* Quick Actions Overlay */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={isHovered ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
          transition={{ duration: 0.2 }}
          className="absolute bottom-2 left-2 right-2 flex space-x-2"
        >
          <button className="flex-1 bg-white/90 backdrop-blur-sm text-gray-800 py-2 px-3 rounded-lg text-xs font-medium hover:bg-white transition-colors flex items-center justify-center">
            <Eye className="w-3 h-3 mr-1" />
            Quick View
          </button>
          <button className="flex-1 bg-green-600 text-white py-2 px-3 rounded-lg text-xs font-medium hover:bg-green-700 transition-colors flex items-center justify-center">
            <ShoppingCart className="w-3 h-3 mr-1" />
            Add
          </button>
        </motion.div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Title */}
        <Link href={`/products/${id}`}>
          <h3 className="font-semibold text-gray-900 mb-1 hover:text-green-600 transition-colors line-clamp-1">
            {name}
          </h3>
        </Link>

        {/* Farmer */}
        <p className="text-sm text-gray-600 mb-2">
          by <span className="font-medium">{farmer}</span>
        </p>

        {/* Rating */}
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex items-center">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-4 h-4 ${
                  i < Math.floor(rating)
                    ? "text-yellow-400 fill-current"
                    : "text-gray-300"
                }`}
              />
            ))}
          </div>
          <span className="text-sm text-gray-600">
            {rating} ({reviews})
          </span>
        </div>

        {/* Location */}
        <div className="flex items-center text-sm text-gray-500 mb-3">
          <MapPin className="w-4 h-4 mr-1" />
          {location}
        </div>

        {/* Price */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-green-600">
              {price} DH
            </span>
            {originalPrice && (
              <span className="text-sm text-gray-400 line-through">
                {originalPrice} DH
              </span>
            )}
          </div>
          
          {/* Category Icon */}
          <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
            <Leaf className="w-4 h-4 text-green-600" />
          </div>
        </div>
      </div>

      {/* Hover Gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </motion.div>
  )
}
