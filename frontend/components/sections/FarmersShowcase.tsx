"use client"

import { motion } from "framer-motion"
import { useInView } from "react-intersection-observer"
import Link from "next/link"
import { 
  Users, 
  Award, 
  MapPin, 
  Star, 
  CheckCircle, 
  Leaf,
  Heart,
  TrendingUp
} from "lucide-react"

const farmers = [
  {
    id: 1,
    name: "Mohammed El Amrani",
    farm: "Ferme Tadla",
    location: "Béni Mellal",
    specialty: "Agrumes Bio",
    experience: "15 ans",
    rating: 4.9,
    products: 45,
    certified: true,
    image: "👨‍🌾"
  },
  {
    id: 2,
    name: "Fatima Zahra",
    farm: "Domaine Atlas",
    location: "Fès",
    specialty: "Huile d'Olive",
    experience: "20 ans",
    rating: 5.0,
    products: 12,
    certified: true,
    image: "👩‍🌾"
  },
  {
    id: 3,
    name: "Youssef Benali",
    farm: "Terres Souss",
    location: "Agadir",
    specialty: "Légumes Saisonniers",
    experience: "8 ans",
    rating: 4.8,
    products: 67,
    certified: false,
    image: "👨‍🌾"
  },
  {
    id: 4,
    name: "Khadija Rizki",
    farm: "Jardin Rif",
    location: "Taza",
    specialty: "Herbes Aromatiques",
    experience: "12 ans",
    rating: 4.9,
    products: 23,
    certified: true,
    image: "👩‍🌾"
  },
]

const benefits = [
  {
    icon: CheckCircle,
    title: "Qualité Garantie",
    description: "Tous nos agriculteurs sont vérifiés et suivent des standards de qualité stricts"
  },
  {
    icon: Leaf,
    title: "Agriculture Durable",
    description: "Pratiques agricoles respectueuses de l'environnement et des ressources naturelles"
  },
  {
    icon: Heart,
    title: "Support Local",
    description: "Soutenez directement les producteurs marocains et l'économie locale"
  },
  {
    icon: TrendingUp,
    title: "Croissance Mutuelle",
    description: "Accompagnement et formation pour nos agriculteurs partenaires"
  },
]

export default function FarmersShowcase() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <section ref={ref} className="py-20 bg-gradient-to-br from-emerald-50 to-green-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Nos Agriculteurs
            <span className="block bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mt-2">
              Partenaires de Confiance
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Découvrez les hommes et les femmes qui travaillent la terre marocaine 
            avec passion et expertise pour vous apporter les meilleurs produits.
          </p>
        </motion.div>

        {/* Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-xl mb-4">
                <benefit.icon className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{benefit.title}</h3>
              <p className="text-sm text-gray-600">{benefit.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Farmers Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {farmers.map((farmer, index) => (
            <motion.div
              key={farmer.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group"
            >
              <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
                {/* Profile Header */}
                <div className="relative h-32 bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center">
                  <span className="text-6xl">{farmer.image}</span>
                  {farmer.certified && (
                    <div className="absolute top-2 right-2">
                      <div className="bg-white rounded-full p-1">
                        <Award className="w-4 h-4 text-green-600" />
                      </div>
                    </div>
                  )}
                </div>

                {/* Profile Info */}
                <div className="p-4">
                  <h4 className="font-bold text-gray-900 mb-1">{farmer.name}</h4>
                  <p className="text-sm text-gray-600 mb-3">{farmer.farm}</p>

                  {/* Location */}
                  <div className="flex items-center text-sm text-gray-500 mb-3">
                    <MapPin className="w-4 h-4 mr-1" />
                    {farmer.location}
                  </div>

                  {/* Specialty */}
                  <div className="mb-3">
                    <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      {farmer.specialty}
                    </span>
                  </div>

                  {/* Stats */}
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Expérience</span>
                      <span className="font-medium text-gray-900">{farmer.experience}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Produits</span>
                      <span className="font-medium text-gray-900">{farmer.products}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Note</span>
                      <div className="flex items-center">
                        <div className="flex items-center mr-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < Math.floor(farmer.rating)
                                  ? "text-yellow-400 fill-current"
                                  : "text-gray-300"
                              }`}
                            />
                          ))}
                        </div>
                        <span className="font-medium text-gray-900">{farmer.rating}</span>
                      </div>
                    </div>
                  </div>

                  {/* CTA */}
                  <Link
                    href={`/farmers/${farmer.id}`}
                    className="block w-full text-center bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                  >
                    Voir le Profil
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Join CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-white rounded-3xl shadow-xl p-8 lg:p-12 text-center"
        >
          <div className="max-w-3xl mx-auto">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Vous êtes Agriculteur ?
            </h3>
            <p className="text-gray-600 mb-8">
              Rejoignez notre communauté de plus de 1000 agriculteurs et 
              développez votre activité avec des outils modernes et un accès direct au marché.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/farmers/join"
                className="inline-flex items-center justify-center px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all transform hover:scale-105"
              >
                <Users className="mr-2 w-5 h-5" />
                Devenir Partenaire
              </Link>
              <Link
                href="/farmers/stories"
                className="inline-flex items-center justify-center px-8 py-3 bg-white border-2 border-gray-200 text-gray-700 font-medium rounded-xl hover:border-green-600 hover:text-green-600 transition-all"
              >
                Voir les Success Stories
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
