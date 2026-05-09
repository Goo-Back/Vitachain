"use client"

import React, { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Wifi, 
  Package, 
  Truck, 
  Clock, 
  CheckCircle, 
  ArrowRight, 
  BarChart3,
  Smartphone,
  Shield,
  Zap,
  Users,
  TrendingUp,
  Leaf
} from "lucide-react"
import Link from "next/link"

const services = [
  {
    id: 1,
    name: "Katara IoT",
    title: "Smart Agriculture Solution",
    description: "Système de monitoring intelligent pour l'agriculture moderne",
    image: "🌐",
    icon: Wifi,
    color: "from-blue-600 to-cyan-700",
    features: [
      "Surveillance en temps réel des cultures",
      "Capteurs intelligents d'humidité et température",
      "Alertes automatiques et notifications",
      "Tableau de bord analytique avancé",
      "Optimisation de l'irrigation",
      "Prévisions météo intégrées"
    ],
    benefits: [
      "Réduction de 30% de la consommation d'eau",
      "Augmentation de 25% du rendement",
      "Maintenance prédictive",
      "Suivi mobile 24/7"
    ],
    cta: "Découvrir Katara IoT",
    href: "/services/katara",
    stats: [
      { label: "Agriculteurs connectés", value: "500+" },
      { label: "Hectares monitorés", value: "10,000+" },
      { label: "Economie d'eau", value: "30%" },
      { label: "Satisfaction", value: "98%" }
    ]
  },
  {
    id: 2,
    name: "SecondServe",
    title: "Food Recovery Platform",
    description: "Plateforme de récupération et redistribution des invendus alimentaires",
    image: "📦",
    icon: Package,
    color: "from-green-600 to-emerald-700",
    features: [
      "Collecte automatique des invendus",
      "Matching intelligent avec les associations",
      "Traçabilité complète des produits",
      "Gestion des dates de péremption",
      "Optimisation logistique",
      "Rapports d'impact social"
    ],
    benefits: [
      "Réduction du gaspillage alimentaire",
      "Impact social positif",
      "Avantages fiscaux",
      "Amélioration de l'image de marque"
    ],
    cta: "Explorer SecondServe",
    href: "/services/seconds",
    stats: [
      { label: "Tonnes récupérées", value: "50+" },
      { label: "Partenaires", value: "100+" },
      { label: "Repas distribués", value: "5,000+" },
      { label: "CO2 économisé", value: "15%" }
    ]
  },
  {
    id: 3,
    name: "Livraison Express",
    title: "Fast Delivery Service",
    description: "Service de livraison rapide et fiable pour tous vos produits agricoles",
    image: "🚚",
    icon: Truck,
    color: "from-orange-600 to-red-700",
    features: [
      "Livraison en 24h express",
      "Suivi GPS en temps réel",
      "Conditionnement spécialisé",
      "Assurance transport complète",
      "Planning flexible",
      "Notification de livraison"
    ],
    benefits: [
      "Garantie de fraîcheur",
      "Réduction des pertes",
      "Satisfaction client maximale",
      "Optimisation des coûts"
    ],
    cta: "Configurer la livraison",
    href: "/services/delivery",
    stats: [
      { label: "Livraisons/jour", value: "200+" },
      { label: "Temps moyen", value: "4h" },
      { label: "Taux de ponctualité", value: "99%" },
      { label: "Couverture", value: "National" }
    ]
  }
]

const testimonials = [
  {
    id: 1,
    name: "Mohamed Ben Ali",
    farm: "Ferme El Kalam",
    service: "Katara IoT",
    content: "Katara IoT a transformé notre façon de cultiver. Nous avons optimisé notre irrigation et augmenté notre rendement de 25%.",
    rating: 5
  },
  {
    id: 2,
    name: "Fatima Zahra",
    farm: "Domaine Atlas",
    service: "SecondServe",
    content: "SecondServe nous permet de donner une seconde vie à nos produits. C'est bon pour la planète et pour notre image.",
    rating: 5
  },
  {
    id: 3,
    name: "Youssef Amrani",
    farm: "Citrus Souss",
    service: "Livraison Express",
    content: "Le service de livraison nous a permis d'élargir notre clientèle. Nos produits arrivent toujours frais et à temps.",
    rating: 5
  }
]

export default function ServicesPage() {
  const [activeService, setActiveService] = useState(0)

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
          
          <main>
            {/* Hero Section */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-green-600 to-emerald-700 text-white py-20"
            >
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full mb-6"
                  >
                    <Leaf className="w-10 h-10" />
                  </motion.div>
                  <h1 className="text-5xl font-bold mb-6">Nos Services</h1>
                  <p className="text-xl text-green-100 max-w-3xl mx-auto mb-8">
                    Des solutions innovantes pour optimiser votre production, réduire le gaspillage et livrer vos produits efficacement
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                      Demander une démo
                    </button>
                    <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
                      Contacter un expert
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Services Navigation */}
            <div className="bg-white border-b border-gray-200 sticky top-16 z-20">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex space-x-8 overflow-x-auto py-4">
                  {services.map((service, index) => (
                    <button
                      key={service.id}
                      onClick={() => setActiveService(index)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                        activeService === index
                          ? 'bg-green-100 text-green-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      {React.createElement(service.icon, { className: "w-5 h-5" })}
                      <span className="font-medium">{service.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Active Service Detail */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <motion.div
                key={activeService}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-2xl shadow-xl overflow-hidden"
              >
                {/* Service Header */}
                <div className={`bg-gradient-to-br ${services[activeService].color} p-8 lg:p-12`}>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                    <div className="text-white">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                          {React.createElement(services[activeService].icon, { className: "w-6 h-6" })}
                        </div>
                        <span className="text-white/80 text-sm font-medium">SERVICE</span>
                      </div>
                      <h2 className="text-4xl font-bold mb-4">{services[activeService].name}</h2>
                      <h3 className="text-xl text-white/90 mb-4">{services[activeService].title}</h3>
                      <p className="text-lg text-white/80 mb-6">{services[activeService].description}</p>
                      <Link
                        href={services[activeService].href}
                        className="inline-flex items-center space-x-2 bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                      >
                        <span>{services[activeService].cta}</span>
                        <ArrowRight className="w-5 h-5" />
                      </Link>
                    </div>
                    <div className="text-center">
                      <div className="text-9xl animate-bounce">
                        {services[activeService].image}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Service Content */}
                <div className="p-8 lg:p-12">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Features */}
                    <div className="lg:col-span-2">
                      <h3 className="text-2xl font-bold text-gray-900 mb-6">Fonctionnalités Principales</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {services[activeService].features.map((feature, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * index }}
                            className="flex items-start space-x-3"
                          >
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{feature}</span>
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    {/* Stats */}
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-6">Chiffres Clés</h3>
                      <div className="space-y-4">
                        {services[activeService].stats.map((stat, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.1 * index }}
                            className="bg-gray-50 rounded-lg p-4"
                          >
                            <div className="text-2xl font-bold text-green-600">{stat.value}</div>
                            <div className="text-sm text-gray-600">{stat.label}</div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Benefits */}
                  <div className="mt-8 pt-8 border-t border-gray-200">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Avantages</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      {services[activeService].benefits.map((benefit, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.1 * index }}
                          className="bg-green-50 border border-green-200 rounded-lg p-4 text-center"
                        >
                          <Zap className="w-8 h-8 text-green-600 mx-auto mb-2" />
                          <span className="text-gray-700">{benefit}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* All Services Overview */}
            <div className="bg-gray-50 py-12">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center mb-12"
                >
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">Tous Nos Services</h2>
                  <p className="text-lg text-gray-600">Découvrez comment nous pouvons transformer votre activité</p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {services.map((service, index) => (
                    <motion.div
                      key={service.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * index }}
                      className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow p-6"
                    >
                      <div className={`w-16 h-16 bg-gradient-to-br ${service.color} rounded-lg flex items-center justify-center mb-4`}>
                        {React.createElement(service.icon, { className: "w-8 h-8 text-white" })}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{service.name}</h3>
                      <p className="text-gray-600 mb-4">{service.description}</p>
                      <Link
                        href={service.href}
                        className="inline-flex items-center space-x-2 text-green-600 font-semibold hover:text-green-700"
                      >
                        <span>En savoir plus</span>
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            {/* Testimonials */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-12"
              >
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Témoignages Clients</h2>
                <p className="text-lg text-gray-600">Ce que nos partenaires disent de nos services</p>
              </motion.div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {testimonials.map((testimonial, index) => (
                  <motion.div
                    key={testimonial.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="bg-white rounded-xl shadow-sm p-6"
                  >
                    <div className="flex items-center mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <span key={i} className="text-yellow-400">⭐</span>
                      ))}
                    </div>
                    <p className="text-gray-700 mb-4 italic">"{testimonial.content}"</p>
                    <div>
                      <p className="font-semibold text-gray-900">{testimonial.name}</p>
                      <p className="text-sm text-gray-600">{testimonial.farm}</p>
                      <p className="text-xs text-green-600 font-medium">{testimonial.service}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* CTA Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 lg:p-12 text-center text-white max-w-4xl mx-auto mb-12"
            >
              <Smartphone className="w-16 h-16 mx-auto mb-6" />
              <h2 className="text-3xl font-bold mb-4">Prêt à Transformer Votre Agriculture?</h2>
              <p className="text-green-100 mb-8 max-w-2xl mx-auto">
                Contactez notre équipe d'experts pour une démonstration personnalisée et découvrez comment nos services peuvent optimiser votre production
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                  Planifier une démo
                </button>
                <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
                  Télécharger la brochure
                </button>
              </div>
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
