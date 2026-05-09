"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, X, ChevronDown, Leaf, ShoppingCart, Users, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  {
    name: "Marketplace",
    href: "/marketplace",
    icon: ShoppingCart,
    dropdown: [
      { name: "Produits Frais", href: "/marketplace/fresh" },
      { name: "Produits Locaux", href: "/marketplace/local" },
      { name: "Offres Spéciales", href: "/marketplace/deals" },
    ],
  },
  {
    name: "Agriculteurs",
    href: "/farmers",
    icon: Users,
    dropdown: [
      { name: "Nos Producteurs", href: "/farmers/directory" },
      { name: "Devenir Partenaire", href: "/farmers/join" },
      { name: "Success Stories", href: "/farmers/stories" },
    ],
  },
  {
    name: "Services",
    href: "/services",
    icon: TrendingUp,
    dropdown: [
      { name: "Katara IoT", href: "/services/katara" },
      { name: "SecondServe", href: "/services/seconds" },
      { name: "Livraison", href: "/services/delivery" },
    ],
  },
]

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)

  useEffect(() => {
    const handleScroll = () => {
      const header = document.getElementById("header")
      if (header) {
        if (window.scrollY > 10) {
          header.classList.add("shadow-lg")
        } else {
          header.classList.remove("shadow-lg")
        }
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header
      id="header"
      className="fixed top-0 w-full bg-white/95 backdrop-blur-sm z-50 transition-shadow duration-300"
    >
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
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
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:items-center lg:space-x-8">
            {navigation.map((item) => (
              <div key={item.name} className="relative">
                <button
                  onMouseEnter={() => setActiveDropdown(item.name)}
                  onMouseLeave={() => setActiveDropdown(null)}
                  className="flex items-center space-x-1 text-gray-700 hover:text-green-600 px-3 py-2 text-sm font-medium transition-colors"
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.name}</span>
                  <ChevronDown className="w-4 h-4" />
                </button>

                {/* Dropdown */}
                <AnimatePresence>
                  {activeDropdown === item.name && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                      className="absolute top-full left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-100"
                      onMouseEnter={() => setActiveDropdown(item.name)}
                      onMouseLeave={() => setActiveDropdown(null)}
                    >
                      {item.dropdown?.map((subItem) => (
                        <Link
                          key={subItem.name}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-green-50 hover:text-green-600 transition-colors"
                        >
                          {subItem.name}
                        </Link>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex lg:items-center lg:space-x-4">
            <Link
              href="/auth/login"
              className="text-gray-700 hover:text-green-600 px-4 py-2 text-sm font-medium transition-colors"
            >
              Connexion
            </Link>
            <Link
              href="/auth/register"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:from-green-700 hover:to-emerald-700 transition-all transform hover:scale-105"
            >
              S'inscrire
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-gray-700 hover:text-green-600"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="lg:hidden overflow-hidden"
            >
              <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t border-gray-100">
                {navigation.map((item) => (
                  <div key={item.name}>
                    <Link
                      href={item.href}
                      className="flex items-center space-x-2 text-gray-700 hover:text-green-600 hover:bg-green-50 px-3 py-2 rounded-lg text-base font-medium transition-colors"
                    >
                      <item.icon className="w-5 h-5" />
                      <span>{item.name}</span>
                    </Link>
                    {item.dropdown && (
                      <div className="ml-8 space-y-1">
                        {item.dropdown.map((subItem) => (
                          <Link
                            key={subItem.name}
                            href={subItem.href}
                            className="block text-gray-600 hover:text-green-600 hover:bg-green-50 px-3 py-2 rounded-lg text-sm transition-colors"
                          >
                            {subItem.name}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                <div className="pt-4 pb-2 border-t border-gray-100 space-y-2">
                  <Link
                    href="/auth/login"
                    className="block text-gray-700 hover:text-green-600 px-3 py-2 rounded-lg text-base font-medium transition-colors"
                  >
                    Connexion
                  </Link>
                  <Link
                    href="/auth/register"
                    className="block bg-gradient-to-r from-green-600 to-emerald-600 text-white px-3 py-2 rounded-lg text-base font-medium hover:from-green-700 hover:to-emerald-700 transition-all"
                  >
                    S'inscrire
                  </Link>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </header>
  )
}
