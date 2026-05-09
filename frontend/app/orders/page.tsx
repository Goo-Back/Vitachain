"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Package, 
  Truck, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Calendar,
  MapPin,
  Phone,
  Mail,
  Eye,
  Download,
  Filter,
  Search,
  ChevronDown,
  Star,
  User
} from "lucide-react"

const orders = [
  {
    id: "ORD-2024-001",
    date: "2024-05-05",
    status: "delivered",
    farmer: "Ferme El Kalam",
    farmerPhone: "+212 5XX-XXXXXX",
    farmerEmail: "contact@fermeelkalam.ma",
    farmerLocation: "Marrakech",
    items: [
      { name: "Tomates Bio Premium", quantity: 5, unit: "kg", price: 120, image: "🍅" },
      { name: "Laitues Fraîches", quantity: 3, unit: "botte", price: 25, image: "🥬" }
    ],
    total: 675,
    deliveryAddress: "123 Avenue Hassan II, Casablanca",
    deliveryDate: "2024-05-06",
    trackingNumber: "TRK-789456123",
    paymentMethod: "Carte bancaire",
    paymentStatus: "paid",
    rating: 5,
    review: "Produits frais et livraison ponctuelle. Très satisfait!"
  },
  {
    id: "ORD-2024-002",
    date: "2024-05-03",
    status: "in-transit",
    farmer: "Domaine Atlas",
    farmerPhone: "+212 5XX-XXXXXX",
    farmerEmail: "info@domaineatlas.ma",
    farmerLocation: "Fès",
    items: [
      { name: "Huile d'Olive Extra Vierge", quantity: 2, unit: "L", price: 85, image: "🫒" }
    ],
    total: 170,
    deliveryAddress: "45 Rue Mohammed V, Rabat",
    deliveryDate: "2024-05-07",
    trackingNumber: "TRK-789456124",
    paymentMethod: "Espèces à la livraison",
    paymentStatus: "pending",
    rating: null,
    review: null
  },
  {
    id: "ORD-2024-003",
    date: "2024-05-01",
    status: "processing",
    farmer: "Citrus Souss",
    farmerPhone: "+212 5XX-XXXXXX",
    farmerEmail: "sales@citrus-souss.ma",
    farmerLocation: "Agadir",
    items: [
      { name: "Agrumes Medjool", quantity: 10, unit: "kg", price: 65, image: "🍊" },
      { name: "Oranges Valencia", quantity: 8, unit: "kg", price: 45, image: "🍊" }
    ],
    total: 1010,
    deliveryAddress: "78 Boulevard Zerktouni, Marrakech",
    deliveryDate: "2024-05-08",
    trackingNumber: "TRK-789456125",
    paymentMethod: "Virement bancaire",
    paymentStatus: "paid",
    rating: null,
    review: null
  },
  {
    id: "ORD-2024-004",
    date: "2024-04-28",
    status: "cancelled",
    farmer: "Rucher Azilal",
    farmerPhone: "+212 5XX-XXXXXX",
    farmerEmail: "contact@rucherazilal.ma",
    farmerLocation: "Azilal",
    items: [
      { name: "Miel de Thym Sauvage", quantity: 1, unit: "kg", price: 150, image: "🍯" }
    ],
    total: 150,
    deliveryAddress: "12 Rue d'Agadir, Tanger",
    deliveryDate: "2024-05-02",
    trackingNumber: "TRK-789456126",
    paymentMethod: "Carte bancaire",
    paymentStatus: "refunded",
    rating: null,
    review: null,
    cancellationReason: "Produit en rupture de stock"
  }
]

const statusOptions = [
  { value: "all", label: "Toutes les commandes", color: "gray" },
  { value: "processing", label: "En traitement", color: "blue" },
  { value: "in-transit", label: "En livraison", color: "yellow" },
  { value: "delivered", label: "Livré", color: "green" },
  { value: "cancelled", label: "Annulé", color: "red" }
]

const getStatusIcon = (status: string) => {
  switch (status) {
    case "delivered":
      return <CheckCircle className="w-5 h-5 text-green-600" />
    case "in-transit":
      return <Truck className="w-5 h-5 text-yellow-600" />
    case "processing":
      return <Clock className="w-5 h-5 text-blue-600" />
    case "cancelled":
      return <XCircle className="w-5 h-5 text-red-600" />
    default:
      return <Package className="w-5 h-5 text-gray-600" />
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "delivered":
      return "bg-green-100 text-green-800 border-green-200"
    case "in-transit":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "processing":
      return "bg-blue-100 text-blue-800 border-blue-200"
    case "cancelled":
      return "bg-red-100 text-red-800 border-red-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

export default function OrdersPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedStatus, setSelectedStatus] = useState("all")
  const [dateRange, setDateRange] = useState({ start: "", end: "" })
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null)

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.farmer.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.items.some(item => item.name.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesStatus = selectedStatus === "all" || order.status === selectedStatus
    const matchesDate = (!dateRange.start || order.date >= dateRange.start) &&
                        (!dateRange.end || order.date <= dateRange.end)
    
    return matchesSearch && matchesStatus && matchesDate
  })

  const totalSpent = orders
    .filter(order => order.status === "delivered")
    .reduce((sum, order) => sum + order.total, 0)

  const totalOrders = orders.filter(order => order.status === "delivered").length

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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Mes Commandes</h1>
              <p className="text-lg text-gray-600">Suivez et gérez toutes vos commandes</p>
            </motion.div>

            {/* Stats Cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
            >
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total des commandes</p>
                    <p className="text-2xl font-bold text-gray-900">{orders.length}</p>
                  </div>
                  <Package className="w-8 h-8 text-blue-600" />
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Commandes livrées</p>
                    <p className="text-2xl font-bold text-green-600">{totalOrders}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">En cours</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {orders.filter(o => o.status === "processing" || o.status === "in-transit").length}
                    </p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-600" />
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total dépensé</p>
                    <p className="text-2xl font-bold text-gray-900">{totalSpent} DH</p>
                  </div>
                  <span className="text-2xl">💰</span>
                </div>
              </div>
            </motion.div>

            {/* Filters */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl shadow-sm p-6 mb-6"
            >
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Rechercher par numéro de commande, agriculteur, produit..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                {/* Status Filter */}
                <div className="relative">
                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                </div>

                {/* Date Range */}
                <div className="flex gap-2">
                  <input
                    type="date"
                    value={dateRange.start}
                    onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                    className="px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Début"
                  />
                  <input
                    type="date"
                    value={dateRange.end}
                    onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                    className="px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Fin"
                  />
                </div>
              </div>
            </motion.div>

            {/* Results Count */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                {filteredOrders.length} commande{filteredOrders.length > 1 ? 's' : ''} trouvée{filteredOrders.length > 1 ? 's' : ''}
              </p>
              <button className="flex items-center space-x-2 text-green-600 hover:text-green-700">
                <Download className="w-5 h-5" />
                <span>Exporter</span>
              </button>
            </div>

            {/* Orders List */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="space-y-4"
            >
              {filteredOrders.map((order, index) => (
                <motion.div
                  key={order.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="bg-white rounded-xl shadow-sm overflow-hidden"
                >
                  {/* Order Header */}
                  <div 
                    className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                    onClick={() => setExpandedOrder(expandedOrder === order.id ? null : order.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(order.status)}
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">{order.id}</h3>
                          <p className="text-sm text-gray-600">{order.date} • {order.farmer}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-xl font-bold text-gray-900">{order.total} DH</p>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                            {statusOptions.find(s => s.value === order.status)?.label}
                          </span>
                        </div>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expandedOrder === order.id ? 'rotate-180' : ''}`} />
                      </div>
                    </div>
                  </div>

                  {/* Order Details */}
                  {expandedOrder === order.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="border-t border-gray-200"
                    >
                      <div className="p-6">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* Items */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-4">Articles commandés</h4>
                            <div className="space-y-3">
                              {order.items.map((item, idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                  <div className="flex items-center space-x-3">
                                    <span className="text-2xl">{item.image}</span>
                                    <div>
                                      <p className="font-medium text-gray-900">{item.name}</p>
                                      <p className="text-sm text-gray-600">{item.quantity} {item.unit}</p>
                                    </div>
                                  </div>
                                  <p className="font-semibold text-gray-900">{item.price * item.quantity} DH</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Order Info */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-4">Informations de livraison</h4>
                            <div className="space-y-3">
                              <div className="flex items-start space-x-3">
                                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">Adresse de livraison</p>
                                  <p className="text-sm text-gray-600">{order.deliveryAddress}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <Calendar className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">Date de livraison</p>
                                  <p className="text-sm text-gray-600">{order.deliveryDate}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <Truck className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">Numéro de suivi</p>
                                  <p className="text-sm text-gray-600">{order.trackingNumber}</p>
                                </div>
                              </div>
                            </div>

                            {/* Farmer Info */}
                            <h4 className="font-semibold text-gray-900 mb-4 mt-6">Informations du producteur</h4>
                            <div className="space-y-3">
                              <div className="flex items-center space-x-3">
                                <User className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{order.farmer}</p>
                                  <p className="text-sm text-gray-600">{order.farmerLocation}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <Phone className="w-5 h-5 text-gray-400" />
                                <p className="text-sm text-gray-600">{order.farmerPhone}</p>
                              </div>
                              <div className="flex items-center space-x-3">
                                <Mail className="w-5 h-5 text-gray-400" />
                                <p className="text-sm text-gray-600">{order.farmerEmail}</p>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Payment Info */}
                        <div className="mt-6 pt-6 border-t border-gray-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-gray-600">Méthode de paiement</p>
                              <p className="font-medium text-gray-900">{order.paymentMethod}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Statut du paiement</p>
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${
                                order.paymentStatus === 'paid' ? 'bg-green-100 text-green-800 border-green-200' :
                                order.paymentStatus === 'pending' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                                'bg-red-100 text-red-800 border-red-200'
                              }`}>
                                {order.paymentStatus === 'paid' ? 'Payé' :
                                 order.paymentStatus === 'pending' ? 'En attente' : 'Remboursé'}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Cancellation Reason */}
                        {order.status === 'cancelled' && order.cancellationReason && (
                          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <div className="flex items-start space-x-3">
                              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                              <div>
                                <p className="text-sm font-medium text-red-900">Raison de l'annulation</p>
                                <p className="text-sm text-red-700">{order.cancellationReason}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Review */}
                        {order.status === 'delivered' && order.rating && (
                          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-start space-x-3">
                              <div className="flex items-center">
                                {[...Array(5)].map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`w-4 h-4 ${i < order.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                                  />
                                ))}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-green-900">Votre avis</p>
                                <p className="text-sm text-green-700">{order.review}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="mt-6 flex flex-wrap gap-3">
                          <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                            <Eye className="w-4 h-4" />
                            <span>Voir détails</span>
                          </button>
                          {order.status === 'delivered' && !order.rating && (
                            <button className="flex items-center space-x-2 px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
                              <Star className="w-4 h-4" />
                              <span>Laisser un avis</span>
                            </button>
                          )}
                          {order.status === 'processing' && (
                            <button className="flex items-center space-x-2 px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                              <XCircle className="w-4 h-4" />
                              <span>Annuler la commande</span>
                            </button>
                          )}
                          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                            <Download className="w-4 h-4" />
                            <span>Télécharger facture</span>
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </motion.div>

            {/* Empty State */}
            {filteredOrders.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="text-6xl mb-4">📦</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune commande trouvée</h3>
                <p className="text-gray-600">Essayez de modifier vos filtres ou votre recherche</p>
              </motion.div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
