"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { 
  Leaf, 
  Users, 
  Store, 
  ShoppingCart,
  ArrowRight,
  CheckCircle,
  TrendingUp,
  Globe,
  Shield,
  Heart,
  Star,
  ChevronRight
} from "lucide-react"

export default function LandingPage() {
  const [selectedRole, setSelectedRole] = useState("")

  const roles = [
    {
      id: "farmer",
      title: "Agriculteur",
      description: "Vendez vos produits directement aux consommateurs et restaurants",
      icon: "👨‍🌾",
      features: [
        "Vente directe sans intermédiaire",
        "Gestion intelligente des stocks",
        "Suivi des commandes en temps réel",
        "Accès aux analytics de vente"
      ],
      color: "from-green-600 to-emerald-700",
      href: "/signup/farmer"
    },
    {
      id: "restaurant",
      title: "Restaurant",
      description: "Sourcing local et frais pour votre cuisine",
      icon: "🍽️",
      features: [
        "Produits locaux certifiés",
        "Commandes groupées optimisées",
        "Livraison express",
        "Traçabilité complète"
      ],
      color: "from-orange-600 to-red-700",
      href: "/signup/restaurant"
    },
    {
      id: "consumer",
      title: "Consommateur",
      description: "Accédez aux meilleurs produits agricoles locaux",
      icon: "🛒",
      features: [
        "Produits frais et de saison",
        "Support aux agriculteurs locaux",
        "Prix équitables",
        "Livraison à domicile"
      ],
      color: "from-blue-600 to-cyan-700",
      href: "/signup/consumer"
    }
  ]

  const stats = [
    { label: "Agriculteurs partenaires", value: "500+", icon: Users },
    { label: "Produits disponibles", value: "2,000+", icon: Leaf },
    { label: "Restaurants clients", value: "150+", icon: Store },
    { label: "Consommateurs satisfaits", value: "10,000+", icon: Heart }
  ]

  const testimonials = [
    {
      name: "Mohamed Ben Ali",
      role: "Agriculteur",
      content: "VitaChain a transformé mon activité. Je vends 30% plus et je suis en contact direct avec mes clients.",
      rating: 5,
      avatar: "👨‍🌾"
    },
    {
      name: "Fatima Zahra",
      role: "Restaurateur",
      content: "La qualité des produits et la fiabilité des livraisons sont exceptionnelles. Mes clients adorent!",
      rating: 5,
      avatar: "👩‍🍳"
    },
    {
      name: "Youssef Amrani",
      role: "Consommateur",
      content: "Je trouve les produits les plus frais directement des agriculteurs de ma région. C'est révolutionnaire!",
      rating: 5,
      avatar: "👨‍💼"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <Leaf className="w-8 h-8 text-green-600" />
              <span className="text-xl font-bold text-gray-900">VitaChain</span>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#roles" className="text-gray-700 hover:text-green-600 transition-colors font-medium">
                S'inscrire
              </a>
              <a href="#about" className="text-gray-700 hover:text-green-600 transition-colors font-medium">
                À propos
              </a>
              <Link href="/marketplace/b2b" className="text-gray-700 hover:text-green-600 transition-colors font-medium">
                Marketplace B2B
              </Link>
              <Link href="/marketplace/b2c" className="text-gray-700 hover:text-green-600 transition-colors font-medium">
                Marketplace B2C
              </Link>
            </div>

            {/* CTA Button */}
            <div className="hidden md:flex items-center space-x-4">
              <Link
                href="/auth/login"
                className="text-gray-700 hover:text-gray-900 transition-colors font-medium"
              >
                Se connecter
              </Link>
              <Link
                href="#roles"
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Commencer
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button className="text-gray-700 hover:text-gray-900">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-green-600/10 to-emerald-600/10" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full mb-6"
            >
              <Leaf className="w-10 h-10 text-white" />
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6"
            >
              VitaChain
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            >
              La plateforme qui connecte directement les agriculteurs, les restaurants et les consommateurs 
              pour une alimentation locale, fraîche et équitable.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                href="#roles"
                className="inline-flex items-center space-x-2 bg-green-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-green-700 transition-all transform hover:scale-105 shadow-lg"
              >
                <span>Commencer maintenant</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="#about"
                className="inline-flex items-center space-x-2 border-2 border-green-600 text-green-600 px-8 py-4 rounded-lg font-semibold hover:bg-green-50 transition-colors"
              >
                <span>En savoir plus</span>
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className="text-center"
              >
                <stat.icon className="w-12 h-12 text-green-600 mx-auto mb-4" />
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section id="roles" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Rejoignez VitaChain selon votre profil
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choisissez votre rôle et découvrez comment VitaChain peut transformer votre activité
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {roles.map((role, index) => (
              <motion.div
                key={role.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={{ scale: 1.05 }}
                className="bg-white rounded-2xl shadow-xl overflow-hidden cursor-pointer group"
                onClick={() => setSelectedRole(role.id)}
              >
                <div className={`h-2 bg-gradient-to-r ${role.color}`} />
                <div className="p-8">
                  <div className="text-6xl mb-6 group-hover:scale-110 transition-transform">
                    {role.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{role.title}</h3>
                  <p className="text-gray-600 mb-6">{role.description}</p>
                  
                  <ul className="space-y-3 mb-8">
                    {role.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Link
                    href={role.href}
                    className={`inline-flex items-center space-x-2 bg-gradient-to-r ${role.color} text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity w-full justify-center`}
                  >
                    <span>S'inscrire comme {role.title}</span>
                    <ChevronRight className="w-5 h-5" />
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Pourquoi VitaChain ?
              </h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Impact Économique Positif
                    </h3>
                    <p className="text-gray-600">
                      Les agriculteurs gagnent 30% de plus en éliminant les intermédiaires.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Globe className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Durabilité Environnementale
                    </h3>
                    <p className="text-gray-600">
                      Réduction de 40% des émissions CO2 grâce aux circuits courts.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Qualité Garantie
                    </h3>
                    <p className="text-gray-600">
                      Traçabilité complète de la ferme à la table.
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative"
            >
              <div className="bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl p-8">
                <div className="text-center">
                  <div className="text-8xl mb-6">🌱</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    Rejoignez la révolution agricole locale
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Ensemble, construisons un système alimentaire plus juste, 
                    plus durable et plus transparent.
                  </p>
                  <Link
                    href="#roles"
                    className="inline-flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                  >
                    <span>Commencer maintenant</span>
                    <ArrowRight className="w-5 h-5" />
                  </Link>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Ils nous font confiance
            </h2>
            <p className="text-xl text-gray-600">
              Découvrez les témoignages de notre communauté
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className="bg-white rounded-xl shadow-sm p-6"
              >
                <div className="flex items-center mb-4">
                  <div className="text-3xl mr-3">{testimonial.avatar}</div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 italic">"{testimonial.content}"</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-green-600 to-emerald-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Prêt à rejoindre VitaChain ?
            </h2>
            <p className="text-xl text-green-100 mb-8 max-w-2xl mx-auto">
              Rejoignez des milliers d'agriculteurs, de restaurants et de consommateurs 
              qui transforment déjà l'alimentation locale.
            </p>
            <Link
              href="#roles"
              className="inline-flex items-center space-x-2 bg-white text-green-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
            >
              <span>Commencer maintenant</span>
              <ArrowRight className="w-6 h-6" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
