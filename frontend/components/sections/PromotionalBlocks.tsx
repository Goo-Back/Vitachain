"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { ArrowRight, Truck, Shield, Leaf, Clock } from "lucide-react"

const promotionalBlocks = [
  {
    id: 1,
    title: "New customers get 75% off",
    subtitle: "First order discount",
    description: "Join VitaChain today and save on your first purchase",
    icon: Leaf,
    bgColor: "from-green-500 to-emerald-600",
    cta: "Get Started",
    href: "/register"
  },
  {
    id: 2,
    title: "Free IoT setup",
    subtitle: "Smart farming solutions",
    description: "Add Katara IoT sensors to any farm for free",
    icon: Shield,
    bgColor: "from-blue-500 to-cyan-600",
    cta: "Learn More",
    href: "/services/katara"
  },
  {
    id: 3,
    title: "Free freight",
    subtitle: "On orders over 250 DH",
    description: "Fast delivery across Morocco for qualified orders",
    icon: Truck,
    bgColor: "from-orange-500 to-red-600",
    cta: "Shop Now",
    href: "/marketplace"
  }
]

export default function PromotionalBlocks() {
  return (
    <section className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {promotionalBlocks.map((block, index) => (
            <motion.div
              key={block.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative overflow-hidden rounded-xl"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${block.bgColor}`} />
              
              <div className="relative h-32 p-6 text-white">
                {/* Icon */}
                <div className="mb-4">
                  <block.icon className="w-8 h-8" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-bold mb-1">
                  {block.title}
                </h3>
                <p className="text-sm text-white/90 mb-3">
                  {block.subtitle}
                </p>
                <p className="text-xs text-white/80 mb-4 line-clamp-2">
                  {block.description}
                </p>

                {/* CTA */}
                <Link
                  href={block.href}
                  className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg text-sm font-medium hover:bg-white/30 transition-colors"
                >
                  <span>{block.cta}</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>

              {/* Hover Effect */}
              <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
