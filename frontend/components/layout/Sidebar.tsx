"use client"

import { useState } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Leaf, 
  ShoppingCart, 
  Users, 
  Package, 
  TrendingUp, 
  Settings, 
  ChevronRight,
  ChevronDown,
  Home,
  Heart,
  Clock,
  Star,
  LogOut,
  Menu
} from "lucide-react"

const categories = [
  {
    name: "Marketplace",
    icon: ShoppingCart,
    href: "/marketplace",
    subcategories: [
      { name: "Produits Frais", href: "/marketplace/fresh" },
      { name: "Produits Locaux", href: "/marketplace/local" },
      { name: "Offres Spéciales", href: "/marketplace/deals" },
    ]
  },
  {
    name: "Agriculteurs",
    icon: Users,
    href: "/farmers",
    subcategories: [
      { name: "Nos Producteurs", href: "/farmers/directory" },
      { name: "Devenir Partenaire", href: "/farmers/join" },
      { name: "Success Stories", href: "/farmers/stories" },
    ]
  },
  {
    name: "Services",
    icon: TrendingUp,
    href: "/services",
    subcategories: [
      { name: "Katara IoT", href: "/services/katara" },
      { name: "SecondServe", href: "/services/seconds" },
      { name: "Livraison", href: "/services/delivery" },
    ]
  },
  {
    name: "Orders",
    icon: Package,
    href: "/orders",
    subcategories: [
      { name: "Mes Commandes", href: "/orders/my" },
      { name: "Historique", href: "/orders/history" },
      { name: "Suivi", href: "/orders/tracking" },
    ]
  },
]

const quickActions = [
  { name: "Request Product", icon: Package, href: "/request" },
  { name: "Add Member", icon: Users, href: "/invite" },
]

const recentActivity = [
  { id: 1, product: "Tomates Bio", farmer: "Ferme El Kalam", price: "120 DH", time: "2h ago" },
  { id: 2, product: "Huile d'Olive", farmer: "Domaine Atlas", price: "85 DH", time: "5h ago" },
  { id: 3, product: "Agrumes Frais", farmer: "Citrus Souss", price: "65 DH", time: "1d ago" },
]

export default function Sidebar() {
  const [expandedCategories, setExpandedCategories] = useState<string[]>(["Marketplace"])
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories(prev =>
      prev.includes(categoryName)
        ? prev.filter(c => c !== categoryName)
        : [...prev, categoryName]
    )
  }

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Sidebar */}
      <div className={`fixed lg:relative inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center space-x-2 p-6 border-b border-gray-200">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
              className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg"
            >
              <Leaf className="w-5 h-5 text-white" />
            </motion.div>
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              VitaChain
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {/* Home */}
            <Link
              href="/"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-green-50 text-gray-700 hover:text-green-600 transition-colors"
            >
              <Home className="w-5 h-5" />
              <span className="font-medium">Dashboard</span>
            </Link>

            {/* Categories */}
            {categories.map((category) => (
              <div key={category.name} className="space-y-1">
                <button
                  onClick={() => toggleCategory(category.name)}
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-green-50 text-gray-700 hover:text-green-600 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <category.icon className="w-5 h-5" />
                    <span className="font-medium">{category.name}</span>
                  </div>
                  {expandedCategories.includes(category.name) ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>

                <AnimatePresence>
                  {expandedCategories.includes(category.name) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="ml-8 space-y-1"
                    >
                      {category.subcategories.map((sub) => (
                        <Link
                          key={sub.name}
                          href={sub.href}
                          className="block p-2 text-sm text-gray-600 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
                        >
                          {sub.name}
                        </Link>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}

            {/* Quick Actions */}
            <div className="pt-4 mt-4 border-t border-gray-200">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Quick Actions
              </h3>
              {quickActions.map((action) => (
                <Link
                  key={action.name}
                  href={action.href}
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-green-50 text-gray-700 hover:text-green-600 transition-colors"
                >
                  <action.icon className="w-5 h-5" />
                  <span className="font-medium">{action.name}</span>
                </Link>
              ))}
            </div>

            {/* Recent Activity */}
            <div className="pt-4 mt-4 border-t border-gray-200">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Last Orders
              </h3>
              <div className="space-y-2">
                {recentActivity.map((order) => (
                  <div key={order.id} className="p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {order.product}
                        </p>
                        <p className="text-xs text-gray-500">
                          {order.farmer} • {order.time}
                        </p>
                      </div>
                      <div className="text-sm font-semibold text-green-600">
                        {order.price}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200">
            <Link
              href="/profile"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-green-50 text-gray-700 hover:text-green-600 transition-colors mb-2"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">JD</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">John Doe</p>
                <p className="text-xs text-gray-500">Premium Member</p>
              </div>
            </Link>
            <button className="flex items-center space-x-3 p-3 rounded-lg hover:bg-red-50 text-gray-700 hover:text-red-600 transition-colors w-full">
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Log out</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </>
  )
}
