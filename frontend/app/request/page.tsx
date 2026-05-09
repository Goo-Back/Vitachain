"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Package, 
  Search, 
  Plus, 
  X, 
  CheckCircle,
  AlertCircle,
  Upload,
  Calendar,
  MapPin,
  Users,
  Clock,
  TrendingUp,
  Star,
  ChevronDown
} from "lucide-react"

const categories = [
  "Légumes", "Fruits", "Huiles", "Miels", "Fruits Secs", "Herbes", "Céréales", "Produits Laitiers", "Viandes", "Autres"
]

const urgencyLevels = [
  { value: "low", label: "Basse - 2-3 semaines", color: "blue" },
  { value: "medium", label: "Moyenne - 1-2 semaines", color: "yellow" },
  { value: "high", label: "Haute - 3-7 jours", color: "orange" },
  { value: "urgent", label: "Urgente - 24-48h", color: "red" }
]

const qualityStandards = [
  { id: "organic", label: "Biologique (BIO)", description: "Certifié agriculture biologique" },
  { id: "local", label: "Local", description: "Produit localement (rayon < 100km)" },
  { id: "fair-trade", label: "Commerce équitable", description: "Certifié commerce équitable" },
  { id: "halal", label: "Halal", description: "Certifié halal" },
  { id: "gmo-free", label: "Sans OGM", description: "Garanti sans organismes génétiquement modifiés" }
]

const recentRequests = [
  {
    id: "REQ-2024-001",
    product: "Tomates cerises bio",
    quantity: "50 kg",
    urgency: "high",
    date: "2024-05-05",
    status: "open",
    responses: 3,
    budget: "15-20 DH/kg"
  },
  {
    id: "REQ-2024-002", 
    product: "Huile d'olive extra vierge",
    quantity: "20 L",
    urgency: "medium",
    date: "2024-05-04",
    status: "in-review",
    responses: 7,
    budget: "80-100 DH/L"
  },
  {
    id: "REQ-2024-003",
    product: "Miel de thym sauvage",
    quantity: "10 kg",
    urgency: "low",
    date: "2024-05-03",
    status: "fulfilled",
    responses: 5,
    budget: "150-180 DH/kg"
  }
]

export default function RequestProductPage() {
  const [formData, setFormData] = useState({
    productName: "",
    category: "",
    quantity: "",
    unit: "kg",
    urgency: "medium",
    budgetMin: "",
    budgetMax: "",
    description: "",
    specifications: "",
    deliveryLocation: "",
    deliveryDate: "",
    qualityStandards: [] as string[],
    contactMethod: "email",
    attachments: [] as File[]
  })

  const [showSuccess, setShowSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleQualityStandardToggle = (standardId: string) => {
    setFormData(prev => ({
      ...prev,
      qualityStandards: prev.qualityStandards.includes(standardId)
        ? prev.qualityStandards.filter(id => id !== standardId)
        : [...prev.qualityStandards, standardId]
    }))
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }))
  }

  const removeFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setIsSubmitting(false)
    setShowSuccess(true)
    
    // Reset form after 3 seconds
    setTimeout(() => {
      setShowSuccess(false)
      setFormData({
        productName: "",
        category: "",
        quantity: "",
        unit: "kg",
        urgency: "medium",
        budgetMin: "",
        budgetMax: "",
        description: "",
        specifications: "",
        deliveryLocation: "",
        deliveryDate: "",
        qualityStandards: [],
        contactMethod: "email",
        attachments: []
      })
    }, 3000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "in-review":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "fulfilled":
        return "bg-green-100 text-green-800 border-green-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "open":
        return "Ouverte"
      case "in-review":
        return "En examen"
      case "fulfilled":
        return "Satisfaite"
      default:
        return status
    }
  }

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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Demander un Produit</h1>
              <p className="text-lg text-gray-600">Trouvez les meilleurs produits agricoles auprès de nos partenaires</p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Request Form */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="lg:col-span-2"
              >
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Information */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations de base</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Nom du produit *
                          </label>
                          <input
                            type="text"
                            name="productName"
                            value={formData.productName}
                            onChange={handleInputChange}
                            required
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="Ex: Tomates bio"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Catégorie *
                          </label>
                          <select
                            name="category"
                            value={formData.category}
                            onChange={handleInputChange}
                            required
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          >
                            <option value="">Sélectionner une catégorie</option>
                            {categories.map(category => (
                              <option key={category} value={category}>{category}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    {/* Quantity and Budget */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantité et budget</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Quantité *
                          </label>
                          <input
                            type="number"
                            name="quantity"
                            value={formData.quantity}
                            onChange={handleInputChange}
                            required
                            min="1"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="100"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Unité
                          </label>
                          <select
                            name="unit"
                            value={formData.unit}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          >
                            <option value="kg">Kilogrammes (kg)</option>
                            <option value="L">Litres (L)</option>
                            <option value="unités">Unités</option>
                            <option value="botte">Bottes</option>
                            <option value="caisse">Caisses</option>
                            <option value="tonne">Tonnes</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Urgence *
                          </label>
                          <select
                            name="urgency"
                            value={formData.urgency}
                            onChange={handleInputChange}
                            required
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          >
                            {urgencyLevels.map(level => (
                              <option key={level.value} value={level.value}>{level.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Budget minimum (DH/unité)
                          </label>
                          <input
                            type="number"
                            name="budgetMin"
                            value={formData.budgetMin}
                            onChange={handleInputChange}
                            min="0"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="50"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Budget maximum (DH/unité)
                          </label>
                          <input
                            type="number"
                            name="budgetMax"
                            value={formData.budgetMax}
                            onChange={handleInputChange}
                            min="0"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="100"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description détaillée *
                      </label>
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        required
                        rows={4}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="Décrivez le produit que vous recherchez, ses caractéristiques, etc."
                      />
                    </div>

                    {/* Specifications */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Spécifications techniques
                      </label>
                      <textarea
                        name="specifications"
                        value={formData.specifications}
                        onChange={handleInputChange}
                        rows={3}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="Calibre, taille, maturité, conditionnement, etc."
                      />
                    </div>

                    {/* Quality Standards */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-4">
                        Standards de qualité requis
                      </label>
                      <div className="space-y-3">
                        {qualityStandards.map(standard => (
                          <label key={standard.id} className="flex items-start space-x-3 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={formData.qualityStandards.includes(standard.id)}
                              onChange={() => handleQualityStandardToggle(standard.id)}
                              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500 mt-1"
                            />
                            <div>
                              <p className="font-medium text-gray-900">{standard.label}</p>
                              <p className="text-sm text-gray-600">{standard.description}</p>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Delivery Information */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations de livraison</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Lieu de livraison *
                          </label>
                          <input
                            type="text"
                            name="deliveryLocation"
                            value={formData.deliveryLocation}
                            onChange={handleInputChange}
                            required
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="Adresse complète"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Date souhaitée *
                          </label>
                          <input
                            type="date"
                            name="deliveryDate"
                            value={formData.deliveryDate}
                            onChange={handleInputChange}
                            required
                            min={new Date().toISOString().split('T')[0]}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Attachments */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Pièces jointes (optionnel)
                      </label>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-sm text-gray-600 mb-2">
                          Glissez-déposez des fichiers ou cliquez pour parcourir
                        </p>
                        <p className="text-xs text-gray-500 mb-4">
                          PDF, JPG, PNG (max 10MB par fichier)
                        </p>
                        <input
                          type="file"
                          multiple
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="file-upload"
                        />
                        <label
                          htmlFor="file-upload"
                          className="inline-flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer"
                        >
                          <Plus className="w-5 h-5" />
                          <span>Ajouter des fichiers</span>
                        </label>
                      </div>
                      
                      {formData.attachments.length > 0 && (
                        <div className="mt-4 space-y-2">
                          {formData.attachments.map((file, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div className="flex items-center space-x-3">
                                <Package className="w-5 h-5 text-gray-400" />
                                <span className="text-sm text-gray-700">{file.name}</span>
                                <span className="text-xs text-gray-500">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                              </div>
                              <button
                                type="button"
                                onClick={() => removeFile(index)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="w-5 h-5" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Contact Method */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Méthode de contact préférée *
                      </label>
                      <div className="flex space-x-4">
                        {["email", "phone", "both"].map(method => (
                          <label key={method} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="radio"
                              name="contactMethod"
                              value={method}
                              checked={formData.contactMethod === method}
                              onChange={handleInputChange}
                              className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
                            />
                            <span className="text-gray-700">
                              {method === "email" ? "Email" : method === "phone" ? "Téléphone" : "Les deux"}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-end space-x-4">
                      <button
                        type="button"
                        className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Annuler
                      </button>
                      <button
                        type="submit"
                        disabled={isSubmitting}
                        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isSubmitting ? "Envoi en cours..." : "Envoyer la demande"}
                      </button>
                    </div>
                  </form>
                </div>
              </motion.div>

              {/* Sidebar */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="space-y-6"
              >
                {/* Stats */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistiques</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <span className="text-sm text-gray-600">Demandes ce mois</span>
                      </div>
                      <span className="font-semibold text-gray-900">47</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-5 h-5 text-blue-600" />
                        <span className="text-sm text-gray-600">Satisfaites</span>
                      </div>
                      <span className="font-semibold text-gray-900">38</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Users className="w-5 h-5 text-purple-600" />
                        <span className="text-sm text-gray-600">Partenaires actifs</span>
                      </div>
                      <span className="font-semibold text-gray-900">156</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-5 h-5 text-orange-600" />
                        <span className="text-sm text-gray-600">Temps moyen</span>
                      </div>
                      <span className="font-semibold text-gray-900">2.5 jours</span>
                    </div>
                  </div>
                </div>

                {/* Recent Requests */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Demandes récentes</h3>
                  <div className="space-y-4">
                    {recentRequests.map(request => (
                      <div key={request.id} className="border-b border-gray-200 pb-4 last:border-0">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-medium text-gray-900">{request.product}</p>
                            <p className="text-sm text-gray-600">{request.quantity}</p>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(request.status)}`}>
                            {getStatusLabel(request.status)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{request.date}</span>
                          <span>{request.responses} réponses</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tips */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Conseils</h3>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <Star className="w-5 h-5 text-yellow-500 mt-0.5" />
                      <p className="text-sm text-gray-700">Soyez précis dans votre description pour obtenir de meilleures réponses</p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <Star className="w-5 h-5 text-yellow-500 mt-0.5" />
                      <p className="text-sm text-gray-700">Spécifiez votre budget pour filtrer les offres pertinentes</p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <Star className="w-5 h-5 text-yellow-500 mt-0.5" />
                      <p className="text-sm text-gray-700">Les demandes urgentes reçoivent plus rapidement des réponses</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Success Modal */}
            {showSuccess && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="bg-white rounded-xl p-8 max-w-md mx-4 text-center"
                >
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Demande envoyée!</h3>
                  <p className="text-gray-600 mb-6">
                    Votre demande a été envoyée avec succès. Vous recevrez des réponses dans les prochaines heures.
                  </p>
                  <div className="text-sm text-gray-500">
                    ID de demande: REQ-2024-{Math.floor(Math.random() * 1000).toString().padStart(3, '0')}
                  </div>
                </motion.div>
              </motion.div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
