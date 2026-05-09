"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import ProductCard from "@/components/cards/ProductCard"
import { Clock, Zap, ArrowRight } from "lucide-react"

const deals = [
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
    badge: "FLASH DEAL"
  },
  {
    id: 2,
    name: "Huile d'Olive Extra",
    farmer: "Domaine Atlas",
    price: 65,
    originalPrice: 85,
    rating: 4.9,
    reviews: 89,
    location: "Fès",
    image: "🫒",
    badge: "LIMITED"
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
    badge: "HOT"
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
    badge: "RARE"
  }
]

export default function DealsOfTheDay() {
  const [timeLeft, setTimeLeft] = useState({
    hours: 23,
    minutes: 59,
    seconds: 59
  })

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        const totalSeconds = prev.hours * 3600 + prev.minutes * 60 + prev.seconds - 1
        
        if (totalSeconds <= 0) {
          return { hours: 23, minutes: 59, seconds: 59 }
        }

        return {
          hours: Math.floor(totalSeconds / 3600),
          minutes: Math.floor((totalSeconds % 3600) / 60),
          seconds: totalSeconds % 60
        }
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return (
    <section className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8"
        >
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex items-center space-x-2 bg-red-100 text-red-800 px-3 py-1 rounded-full">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-semibold">FLASH DEALS</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Ends in:</span>
              </div>
            </div>
            
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Deals of the Day
            </h2>
            <p className="text-gray-600">
              Limited time offers on premium agricultural products
            </p>
          </div>

          {/* Countdown Timer */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex items-center space-x-4 mt-4 lg:mt-0"
          >
            <div className="flex space-x-2">
              {[
                { value: timeLeft.hours, label: "Hours" },
                { value: timeLeft.minutes, label: "Mins" },
                { value: timeLeft.seconds, label: "Secs" }
              ].map((time, index) => (
                <div key={time.label} className="text-center">
                  <div className="w-16 h-16 bg-gray-900 text-white rounded-lg flex items-center justify-center">
                    <span className="text-xl font-bold">
                      {String(time.value).padStart(2, "0")}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 mt-1">{time.label}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* Deals Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {deals.map((deal, index) => (
            <motion.div
              key={deal.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <ProductCard {...deal} />
            </motion.div>
          ))}
        </div>

        {/* View All Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-8"
        >
          <button className="inline-flex items-center space-x-2 bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors">
            <span>View All Deals</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </section>
  )
}
