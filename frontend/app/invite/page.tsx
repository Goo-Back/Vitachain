"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/Sidebar"
import TopHeader from "@/components/layout/TopHeader"
import { motion } from "framer-motion"
import { 
  Users, 
  Mail, 
  Copy, 
  CheckCircle, 
  Link,
  UserPlus,
  Crown,
  Shield,
  Star,
  Gift,
  TrendingUp,
  Calendar,
  Clock,
  Filter,
  Search,
  ChevronDown,
  MoreVertical,
  Download,
  RefreshCw
} from "lucide-react"

const memberRoles = [
  { value: "farmer", label: "Agriculteur", description: "Peut vendre des produits", icon: "👨‍🌾", color: "green" },
  { value: "buyer", label: "Acheteur", description: "Peut acheter des produits", icon: "🛒", color: "blue" },
  { value: "admin", label: "Administrateur", description: "Accès complet à la plateforme", icon: "👑", color: "purple" },
  { value: "moderator", label: "Modérateur", description: "Peut gérer les contenus", icon: "🛡️", color: "orange" }
]

const inviteMethods = [
  { value: "email", label: "Invitation par email", description: "Envoyer une invitation directe par email", icon: Mail },
  { value: "link", label: "Lien d'invitation", description: "Générer un lien à partager", icon: Link },
  { value: "bulk", label: "Invitations en masse", description: "Importer plusieurs adresses email", icon: Users }
]

const existingMembers = [
  {
    id: 1,
    name: "Mohamed Ben Ali",
    email: "mohamed@example.com",
    role: "farmer",
    joinedDate: "2024-03-15",
    status: "active",
    invitedBy: "Admin",
    lastActive: "2024-05-05",
    avatar: "👨‍🌾"
  },
  {
    id: 2,
    name: "Fatima Zahra",
    email: "fatima@example.com",
    role: "buyer",
    joinedDate: "2024-04-02",
    status: "active",
    invitedBy: "Admin",
    lastActive: "2024-05-04",
    avatar: "👩‍💼"
  },
  {
    id: 3,
    name: "Youssef Amrani",
    email: "youssef@example.com",
    role: "admin",
    joinedDate: "2024-02-20",
    status: "active",
    invitedBy: "Super Admin",
    lastActive: "2024-05-05",
    avatar: "👨‍💼"
  },
  {
    id: 4,
    name: "Khadija Idrissi",
    email: "khadija@example.com",
    role: "farmer",
    joinedDate: "2024-04-18",
    status: "pending",
    invitedBy: "Mohamed",
    lastActive: "Jamais",
    avatar: "👩‍🌾"
  }
]

const invitationStats = [
  { label: "Total des invitations", value: "156", change: "+12%", icon: Mail, color: "blue" },
  { label: "Invitations acceptées", value: "142", change: "+8%", icon: CheckCircle, color: "green" },
  { label: "Taux de conversion", value: "91%", change: "+2%", icon: TrendingUp, color: "purple" },
  { label: "Invitations en attente", value: "14", change: "-5%", icon: Clock, color: "orange" }
]

export default function InvitePage() {
  const [activeTab, setActiveTab] = useState("invite")
  const [inviteMethod, setInviteMethod] = useState("email")
  const [selectedRole, setSelectedRole] = useState("farmer")
  const [inviteLink, setInviteLink] = useState("")
  const [linkCopied, setLinkCopied] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")

  const [emailForm, setEmailForm] = useState({
    emails: "",
    subject: "Invitation à rejoindre VitaChain",
    message: "Je vous invite à rejoindre notre plateforme VitaChain pour découvrir les meilleurs produits agricoles locaux."
  })

  const [bulkEmails, setBulkEmails] = useState("")

  const handleGenerateLink = () => {
    const link = `https://vitachain.ma/invite?token=${Math.random().toString(36).substring(2, 15)}&role=${selectedRole}`
    setInviteLink(link)
  }

  const handleCopyLink = () => {
    navigator.clipboard.writeText(inviteLink)
    setLinkCopied(true)
    setTimeout(() => setLinkCopied(false), 3000)
  }

  const handleSendEmailInvitation = async (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
    setEmailForm({
      emails: "",
      subject: "Invitation à rejoindre VitaChain",
      message: "Je vous invite à rejoindre notre plateforme VitaChain pour découvrir les meilleurs produits agricoles locaux."
    })
  }

  const handleBulkInvitation = async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
    setBulkEmails("")
  }

  const filteredMembers = existingMembers.filter(member => {
    const matchesSearch = member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         member.email.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = roleFilter === "all" || member.role === roleFilter
    return matchesSearch && matchesRole
  })

  const getRoleColor = (role: string) => {
    switch (role) {
      case "farmer":
        return "bg-green-100 text-green-800 border-green-200"
      case "buyer":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "admin":
        return "bg-purple-100 text-purple-800 border-purple-200"
      case "moderator":
        return "bg-orange-100 text-orange-800 border-orange-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 border-green-200"
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "inactive":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
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
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Inviter des Membres</h1>
              <p className="text-lg text-gray-600">Faites grandir votre communauté VitaChain</p>
            </motion.div>

            {/* Stats Cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
            >
              {invitationStats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="bg-white rounded-xl shadow-sm p-6"
                >
                  <div className="flex items-center justify-between mb-2">
                    <stat.icon className={`w-8 h-8 text-${stat.color}-600`} />
                    <span className={`text-sm font-medium ${
                      stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-sm mb-6">
              <div className="border-b border-gray-200">
                <div className="flex space-x-8 px-6">
                  {["invite", "members"].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab
                          ? "border-green-500 text-green-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      }`}
                    >
                      {tab === "invite" ? "Nouvelle Invitation" : "Membres Existant"}
                    </button>
                  ))}
                </div>
              </div>

              {/* Invite Tab Content */}
              {activeTab === "invite" && (
                <div className="p-6">
                  {/* Invite Method Selection */}
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Méthode d'invitation</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {inviteMethods.map((method) => (
                        <button
                          key={method.value}
                          onClick={() => setInviteMethod(method.value)}
                          className={`p-4 rounded-lg border-2 transition-all ${
                            inviteMethod === method.value
                              ? "border-green-500 bg-green-50"
                              : "border-gray-200 hover:border-gray-300"
                          }`}
                        >
                          <method.icon className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                          <h4 className="font-medium text-gray-900">{method.label}</h4>
                          <p className="text-sm text-gray-600 mt-1">{method.description}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Role Selection */}
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Rôle à assigner</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {memberRoles.map((role) => (
                        <button
                          key={role.value}
                          onClick={() => setSelectedRole(role.value)}
                          className={`p-4 rounded-lg border-2 transition-all ${
                            selectedRole === role.value
                              ? "border-green-500 bg-green-50"
                              : "border-gray-200 hover:border-gray-300"
                          }`}
                        >
                          <div className="text-3xl mb-2">{role.icon}</div>
                          <h4 className="font-medium text-gray-900">{role.label}</h4>
                          <p className="text-sm text-gray-600 mt-1">{role.description}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Email Invitation Form */}
                  {inviteMethod === "email" && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-50 rounded-lg p-6"
                    >
                      <h4 className="font-semibold text-gray-900 mb-4">Invitation par Email</h4>
                      <form onSubmit={handleSendEmailInvitation} className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Adresses email (séparées par des virgules)
                          </label>
                          <textarea
                            value={emailForm.emails}
                            onChange={(e) => setEmailForm(prev => ({ ...prev, emails: e.target.value }))}
                            rows={3}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="email1@example.com, email2@example.com, email3@example.com"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Sujet
                          </label>
                          <input
                            type="text"
                            value={emailForm.subject}
                            onChange={(e) => setEmailForm(prev => ({ ...prev, subject: e.target.value }))}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Message personnalisé
                          </label>
                          <textarea
                            value={emailForm.message}
                            onChange={(e) => setEmailForm(prev => ({ ...prev, message: e.target.value }))}
                            rows={4}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            required
                          />
                        </div>
                        <button
                          type="submit"
                          className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                        >
                          Envoyer les invitations
                        </button>
                      </form>
                    </motion.div>
                  )}

                  {/* Link Invitation */}
                  {inviteMethod === "link" && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-50 rounded-lg p-6"
                    >
                      <h4 className="font-semibold text-gray-900 mb-4">Lien d'invitation</h4>
                      <div className="space-y-4">
                        <button
                          onClick={handleGenerateLink}
                          className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                        >
                          Générer un lien d'invitation
                        </button>
                        
                        {inviteLink && (
                          <div className="bg-white p-4 rounded-lg border border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Lien d'invitation:</span>
                              <button
                                onClick={handleCopyLink}
                                className="flex items-center space-x-2 text-green-600 hover:text-green-700"
                              >
                                {linkCopied ? (
                                  <>
                                    <CheckCircle className="w-4 h-4" />
                                    <span className="text-sm">Copié!</span>
                                  </>
                                ) : (
                                  <>
                                    <Copy className="w-4 h-4" />
                                    <span className="text-sm">Copier</span>
                                  </>
                                )}
                              </button>
                            </div>
                            <div className="p-3 bg-gray-50 rounded-lg break-all">
                              <code className="text-sm text-gray-600">{inviteLink}</code>
                            </div>
                            <div className="mt-3 flex items-center space-x-2 text-sm text-gray-600">
                              <Shield className="w-4 h-4" />
                              <span>Ce lien expirera dans 30 jours</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {/* Bulk Invitation */}
                  {inviteMethod === "bulk" && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-50 rounded-lg p-6"
                    >
                      <h4 className="font-semibold text-gray-900 mb-4">Invitations en masse</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Importer des adresses email
                          </label>
                          <textarea
                            value={bulkEmails}
                            onChange={(e) => setBulkEmails(e.target.value)}
                            rows={6}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            placeholder="email1@example.com&#10;email2@example.com&#10;email3@example.com&#10;..."
                          />
                          <p className="text-sm text-gray-600 mt-2">
            Une adresse email par ligne, ou séparées par des virgules
                          </p>
                        </div>
                        <div className="flex space-x-4">
                          <button
                            onClick={handleBulkInvitation}
                            className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                          >
                            Envoyer les invitations
                          </button>
                          <button className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                            <Download className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              )}

              {/* Members Tab Content */}
              {activeTab === "members" && (
                <div className="p-6">
                  {/* Filters */}
                  <div className="flex flex-col md:flex-row gap-4 mb-6">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="text"
                        placeholder="Rechercher par nom ou email..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      />
                    </div>
                    <select
                      value={roleFilter}
                      onChange={(e) => setRoleFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="all">Tous les rôles</option>
                      <option value="farmer">Agriculteurs</option>
                      <option value="buyer">Acheteurs</option>
                      <option value="admin">Administrateurs</option>
                      <option value="moderator">Modérateurs</option>
                    </select>
                  </div>

                  {/* Members Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Membre</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Rôle</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Statut</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Date d'inscription</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Dernière activité</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Invité par</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredMembers.map((member) => (
                          <tr key={member.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-3">
                                <div className="text-2xl">{member.avatar}</div>
                                <div>
                                  <p className="font-medium text-gray-900">{member.name}</p>
                                  <p className="text-sm text-gray-600">{member.email}</p>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getRoleColor(member.role)}`}>
                                {memberRoles.find(r => r.value === member.role)?.label}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(member.status)}`}>
                                {member.status === "active" ? "Actif" : member.status === "pending" ? "En attente" : "Inactif"}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">{member.joinedDate}</td>
                            <td className="py-3 px-4 text-sm text-gray-600">{member.lastActive}</td>
                            <td className="py-3 px-4 text-sm text-gray-600">{member.invitedBy}</td>
                            <td className="py-3 px-4">
                              <button className="text-gray-400 hover:text-gray-600">
                                <MoreVertical className="w-5 h-5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Success Message */}
            {showSuccess && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="fixed top-4 right-4 bg-green-600 text-white px-6 py-4 rounded-lg shadow-lg z-50"
              >
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6" />
                  <div>
                    <p className="font-semibold">Invitation envoyée!</p>
                    <p className="text-sm text-green-100">Les invitations ont été envoyées avec succès.</p>
                  </div>
                </div>
              </motion.div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
