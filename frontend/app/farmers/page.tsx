"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { Search, MapPin, Star, Leaf, Users, Award, Calendar, ChevronDown, Mail, Phone, Globe } from "lucide-react"

const farmers = [
  {
    id: 1,
    name: "Ferme El Kalam",
    owner: "Mohamed Ben Ali",
    location: "Marrakech",
    rating: 4.8,
    reviews: 124,
    products: 15,
    years: 12,
    image: "👨‍🌾",
    certified: true,
    organic: true,
    description: "Spécialisée dans les légumes biologiques et les herbes aromatiques",
    specialties: ["Tomates", "Laitues", "Herbes"],
    email: "contact@fermeelkalam.ma",
    phone: "+212 5XX-XXXXXX",
    website: "www.fermeelkalam.ma"
  },
  {
    id: 2,
    name: "Domaine Atlas",
    owner: "Fatima Zahra",
    location: "Fès",
    rating: 4.9,
    reviews: 89,
    products: 8,
    years: 25,
    image: "👩‍🌾",
    certified: true,
    organic: true,
    description: "Producteur d'huile d'olive extra vierge AOP depuis 1998",
    specialties: ["Huile d'Olive", "Olives", "Produits dérivés"],
    email: "info@domaineatlas.ma",
    phone: "+212 5XX-XXXXXX",
    website: "www.domaineatlas.ma"
  },
  {
    id: 3,
    name: "Citrus Souss",
    owner: "Youssef Amrani",
    location: "Agadir",
    rating: 4.7,
    reviews: 56,
    products: 12,
    years: 8,
    image: "👨‍🌾",
    certified: false,
    organic: false,
    description: "Agrumes de qualité supérieure du Souss-Massa",
    specialties: ["Oranges", "Mandarines", "Citrons"],
    email: "sales@citrus-souss.ma",
    phone: "+212 5XX-XXXXXX",
    website: null
  },
  {
    id: 4,
    name: "Rucher Azilal",
    owner: "Khadija Idrissi",
    location: "Azilal",
    rating: 5.0,
    reviews: 203,
    products: 6,
    years: 15,
    image: "👩‍🌾",
    certified: true,
    organic: true,
    description: "Miels artisanaux des montagnes de l'Atlas",
    specialties: ["Miel de Thym", "Miel de Fleurs Sauvages", "Propolis"],
    email: "contact@rucherazilal.ma",
    phone: "+212 5XX-XXXXXX",
    website: "www.rucherazilal.ma"
  },
  {
    id: 5,
    name: "Ferme Ifrane",
    owner: "Abdelkrim Ouazzani",
    location: "Ifrane",
    rating: 4.6,
    reviews: 78,
    products: 10,
    years: 20,
    image: "👨‍🌾",
    certified: true,
    organic: true,
    description: "Fruits secs et noix de la région d'Ifrane",
    specialties: ["Noix", "Amandes", "Noisettes"],
    email: "info@fermeifrane.ma",
    phone: "+212 5XX-XXXXXX",
    website: null
  },
  {
    id: 6,
    name: "Jardin Rif",
    owner: "Samira El Mouti",
    location: "Taza",
    rating: 4.5,
    reviews: 45,
    products: 18,
    years: 6,
    image: "👩‍🌾",
    certified: false,
    organic: true,
    description: "Herbes aromatiques et plantes médicinales du Rif",
    specialties: ["Menthe", "Romarin", "Sauge"],
    email: "herbes@jardinrif.ma",
    phone: "+212 5XX-XXXXXX",
    website: null
  }
]

const regions = ["Tous", "Marrakech", "Fès", "Agadir", "Azilal", "Ifrane", "Taza", "Casablanca", "Rabat"]
const sortOptions = ["Pertinence", "Meilleures notes", "Plus de produits", "Plus d'expérience", "Plus récents"]

export default function FarmersPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedRegion, setSelectedRegion] = useState("Tous")
  const [sortBy, setSortBy] = useState("Pertinence")
  const [certifiedOnly, setCertifiedOnly] = useState(false)
  const [organicOnly, setOrganicOnly] = useState(false)

  const filteredFarmers = farmers.filter(farmer => {
    const matchesSearch = farmer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         farmer.owner.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         farmer.specialties.some(spec => spec.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesRegion = selectedRegion === "Tous" || farmer.location === selectedRegion
    const matchesCertified = !certifiedOnly || farmer.certified
    const matchesOrganic = !organicOnly || farmer.organic
    
    return matchesSearch && matchesRegion && matchesCertified && matchesOrganic
  })

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
          
          <main className="p-6">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Nos Agriculteurs</h1>
              <p className="text-lg text-gray-600">Découvrez les producteurs passionnés derrière nos produits</p>
            </motion.div>

            {/* Search and Filters */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6 mb-6"
            >
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search Bar */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Rechercher des agriculteurs, produits..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                {/* Region Filter */}
                <div className="relative">
                  <select
                    value={selectedRegion}
                    onChange={(e) => setSelectedRegion(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {regions.map(region => (
                      <option key={region} value={region}>{region}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                </div>

                {/* Sort */}
                <div className="relative">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {sortOptions.map(option => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                </div>
              </div>

              {/* Advanced Filters */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex flex-wrap gap-6">
                  {/* Certified Only */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="certified"
                      checked={certifiedOnly}
                      onChange={(e) => setCertifiedOnly(e.target.checked)}
                      className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    />
                    <label htmlFor="certified" className="ml-2 text-sm font-medium text-gray-700">
                      Certifiés uniquement
                    </label>
                  </div>

                  {/* Organic Only */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="organic"
                      checked={organicOnly}
                      onChange={(e) => setOrganicOnly(e.target.checked)}
                      className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    />
                    <label htmlFor="organic" className="ml-2 text-sm font-medium text-gray-700">
                      Biologiques uniquement
                    </label>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Results Count */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                {filteredFarmers.length} agriculteur{filteredFarmers.length > 1 ? 's' : ''} trouvé{filteredFarmers.length > 1 ? 's' : ''}
              </p>
            </div>

            {/* Farmers Grid */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
            >
              {filteredFarmers.map((farmer, index) => (
                <motion.div
                  key={farmer.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow overflow-hidden group"
                >
                  {/* Farmer Header */}
                  <div className="relative h-32 bg-gradient-to-br from-green-50 to-emerald-50 p-6">
                    <div className="flex items-center space-x-4">
                      <div className="text-5xl group-hover:scale-110 transition-transform">
                        {farmer.image}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-xl text-gray-900 mb-1">{farmer.name}</h3>
                        <p className="text-sm text-gray-600 flex items-center">
                          <MapPin className="w-4 h-4 mr-1" />
                          {farmer.location}
                        </p>
                      </div>
                    </div>

                    {/* Badges */}
                    <div className="absolute top-3 right-3 flex flex-col space-y-2">
                      {farmer.certified && (
                        <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">
                          Certifié
                        </span>
                      )}
                      {farmer.organic && (
                        <span className="px-2 py-1 bg-green-600 text-white text-xs font-semibold rounded-full">
                          BIO
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Farmer Info */}
                  <div className="p-6">
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">{farmer.description}</p>
                      
                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <div className="flex items-center justify-center space-x-1 text-yellow-500">
                            <Star className="w-4 h-4 fill-current" />
                            <span className="font-semibold text-gray-900">{farmer.rating}</span>
                          </div>
                          <p className="text-xs text-gray-500">{farmer.reviews} avis</p>
                        </div>
                        <div className="text-center">
                          <div className="flex items-center justify-center space-x-1 text-green-600">
                            <Leaf className="w-4 h-4" />
                            <span className="font-semibold text-gray-900">{farmer.products}</span>
                          </div>
                          <p className="text-xs text-gray-500">produits</p>
                        </div>
                        <div className="text-center">
                          <div className="flex items-center justify-center space-x-1 text-blue-600">
                            <Calendar className="w-4 h-4" />
                            <span className="font-semibold text-gray-900">{farmer.years}</span>
                          </div>
                          <p className="text-xs text-gray-500">années</p>
                        </div>
                      </div>

                      {/* Specialties */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Spécialités:</h4>
                        <div className="flex flex-wrap gap-2">
                          {farmer.specialties.map((specialty, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                            >
                              {specialty}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Contact */}
                      <div className="space-y-2">
                        <div className="flex items-center text-sm text-gray-600">
                          <Users className="w-4 h-4 mr-2" />
                          <span>{farmer.owner}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Mail className="w-4 h-4 mr-2" />
                          <span className="truncate">{farmer.email}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Phone className="w-4 h-4 mr-2" />
                          <span>{farmer.phone}</span>
                        </div>
                        {farmer.website && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Globe className="w-4 h-4 mr-2" />
                            <span className="truncate">{farmer.website}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* CTA Buttons */}
                    <div className="flex space-x-2">
                      <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors font-medium">
                        Voir les produits
                      </button>
                      <button className="flex-1 border border-green-600 text-green-600 py-2 px-4 rounded-lg hover:bg-green-50 transition-colors font-medium">
                        Contacter
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Empty State */}
            {filteredFarmers.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="text-6xl mb-4">👨‍🌾</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun agriculteur trouvé</h3>
                <p className="text-gray-600">Essayez de modifier vos filtres ou votre recherche</p>
              </motion.div>
            )}

            {/* Join CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-8 text-center text-white"
            >
              <Award className="w-12 h-12 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Devenez Partenaire VitaChain</h2>
              <p className="text-green-100 mb-6 max-w-2xl mx-auto">
                Rejoignez notre communauté d'agriculteurs passionnés et faites découvrir vos produits à des milliers de clients
              </p>
              <button className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Postuler maintenant
              </button>
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
