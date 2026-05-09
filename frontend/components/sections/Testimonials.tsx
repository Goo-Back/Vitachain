"use client"

import { motion } from "framer-motion"
import { useInView } from "react-intersection-observer"
import { Star, Quote } from "lucide-react"

const testimonials = [
  {
    id: 1,
    name: "Karim Alaoui",
    role: "Restaurant Le Jardin Secret",
    location: "Marrakech",
    content: "VitaChain a transformé notre approvisionnement. Produits frais, livraison ponctuelle et prix équitables. C'est un partenaire stratégique pour notre restaurant.",
    rating: 5,
    avatar: "👨‍🍳"
  },
  {
    id: 2,
    name: "Aicha Benjelloun",
    role: "Agriculteur Bio",
    location: "Fès",
    content: "Grâce à Katara IoT, j'ai optimisé ma production de 30% tout en réduisant ma consommation d'eau. VitaChain me connecte directement aux meilleurs clients.",
    rating: 5,
    avatar: "👩‍🌾"
  },
  {
    id: 3,
    name: "Youssef Amrani",
    role: "Chef de Cuisine",
    location: "Casablanca",
    content: "SecondServe nous permet de réduire le gaspillage tout en proposant des offres attractives. Nos clients adorent et notre impact environnemental est positif.",
    rating: 5,
    avatar: "👨‍🍳"
  },
  {
    id: 4,
    name: "Fatima Zahra",
    role: "Responsable Achats",
    location: "Rabat",
    content: "La transparence de la chaîne d'approvisionnement est remarquable. Je sais exactement d'où viennent mes produits et à qui je bénéficie.",
    rating: 5,
    avatar: "👩‍💼"
  },
  {
    id: 5,
    name: "Mohammed El Khamlichi",
    role: "Producteur Laitier",
    location: "Meknès",
    content: "VitaChain m'a permis de doubler mes ventes en 6 mois. L'accès direct aux restaurants et citoyens a changé la donne pour ma petite exploitation.",
    rating: 5,
    avatar: "👨‍🌾"
  },
  {
    id: 6,
    name: "Samira Rhazi",
    role: "Consommatrice",
    location: "Tanger",
    content: "Je adore pouvoir acheter directement des producteurs locaux. Les produits sont frais, les prix sont justes et je soutiens l'économie marocaine.",
    rating: 5,
    avatar: "👩‍🦰"
  }
]

export default function Testimonials() {
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
            Ils Nous Font
            <span className="block bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mt-2">
              Confiance
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Découvrez les témoignages de nos partenaires qui transforment 
            l'agriculture marocaine avec VitaChain.
          </p>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group"
            >
              <div className="h-full bg-gradient-to-br from-gray-50 to-green-50 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
                {/* Quote Icon */}
                <div className="flex items-start justify-between mb-4">
                  <Quote className="w-8 h-8 text-green-600 opacity-50" />
                  <div className="flex items-center">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 text-yellow-400 fill-current"
                      />
                    ))}
                  </div>
                </div>

                {/* Content */}
                <p className="text-gray-700 mb-6 leading-relaxed">
                  "{testimonial.content}"
                </p>

                {/* Author */}
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-2xl">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {testimonial.name}
                    </div>
                    <div className="text-sm text-gray-600">
                      {testimonial.role}
                    </div>
                    <div className="text-xs text-gray-500">
                      📍 {testimonial.location}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 text-white"
        >
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold mb-2">98%</div>
              <div className="text-green-100">Satisfaction Client</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">4.9/5</div>
              <div className="text-green-100">Note Moyenne</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">2M+</div>
              <div className="text-green-100">Transactions</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">85%</div>
              <div className="text-green-100">Réduction Gaspi</div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
