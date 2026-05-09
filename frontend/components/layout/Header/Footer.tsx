"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { 
  Leaf, 
  Mail, 
  Phone, 
  MapPin, 
  Heart
} from "lucide-react"

const footerLinks = {
  produit: [
    { name: "Marketplace", href: "/marketplace" },
    { name: "Katara IoT", href: "/services/katara" },
    { name: "SecondServe", href: "/services/seconds" },
    { name: "Livraison", href: "/services/delivery" },
  ],
  entreprise: [
    { name: "À Propos", href: "/about" },
    { name: "Carrières", href: "/careers" },
    { name: "Presse", href: "/press" },
    { name: "Blog", href: "/blog" },
  ],
  support: [
    { name: "Aide Centre", href: "/help" },
    { name: "Contact", href: "/contact" },
    { name: "FAQ", href: "/faq" },
    { name: "Livraison", href: "/shipping" },
  ],
  legal: [
    { name: "Conditions Générales", href: "/terms" },
    { name: "Politique de Confidentialité", href: "/privacy" },
    { name: "Politique Cookies", href: "/cookies" },
    { name: "Mentions Légales", href: "/legal" },
  ],
}

const socialLinks = [
  { icon: "📘", href: "#", label: "Facebook" },
  { icon: "📷", href: "#", label: "Instagram" },
  { icon: "🐦", href: "#", label: "Twitter" },
  { icon: "💼", href: "#", label: "LinkedIn" },
]

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-6 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
                className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg"
              >
                <Leaf className="w-5 h-5 text-white" />
              </motion.div>
              <span className="text-xl font-bold">VitaChain</span>
            </div>
            <p className="text-gray-300 mb-6 leading-relaxed">
              La première plateforme agritech marocaine qui connecte les agriculteurs 
              aux restaurants et citoyens pour une alimentation durable et locale.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-gray-300">
                <Mail className="w-5 h-5 text-green-500" />
                <span>contact@vitachain.ma</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-300">
                <Phone className="w-5 h-5 text-green-500" />
                <span>+212 522 123 456</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-300">
                <MapPin className="w-5 h-5 text-green-500" />
                <span>Casablanca, Maroc</span>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex space-x-4 mt-6">
              {socialLinks.map((social) => (
                <motion.a
                  key={social.label}
                  href={social.href}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="flex items-center justify-center w-10 h-10 bg-gray-800 rounded-lg hover:bg-green-600 transition-colors"
                  aria-label={social.label}
                >
                  <span className="text-lg">{social.icon}</span>
                </motion.a>
              ))}
            </div>
          </div>

          {/* Links Sections */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="text-lg font-semibold mb-4 capitalize">
                {category === 'produit' ? 'Produit' : 
                 category === 'entreprise' ? 'Entreprise' : 
                 category === 'support' ? 'Support' : 'Légal'}
              </h3>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.name}>
                    <Link
                      href={link.href}
                      className="text-gray-300 hover:text-green-400 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mt-12 p-6 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl"
        >
          <div className="max-w-2xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-2">
              Restez Connecté
            </h3>
            <p className="text-green-100 mb-6">
              Recevez nos dernières actualités et offres exclusives directement dans votre boîte mail.
            </p>
            <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Votre adresse email"
                className="flex-1 px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-white text-green-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors"
              >
                S'inscrire
              </button>
            </form>
          </div>
        </motion.div>
      </div>

      {/* Bottom Footer */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-gray-400 text-sm">
              © 2024 VitaChain. Tous droits réservés.
            </div>
            <div className="flex items-center space-x-2 text-gray-400 text-sm">
              <span>Fait avec</span>
              <Heart className="w-4 h-4 text-red-500 fill-current" />
              <span>au 🇲🇦 Maroc</span>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <Link href="/terms" className="text-gray-400 hover:text-green-400 transition-colors">
                Conditions
              </Link>
              <Link href="/privacy" className="text-gray-400 hover:text-green-400 transition-colors">
                Confidentialité
              </Link>
              <Link href="/cookies" className="text-gray-400 hover:text-green-400 transition-colors">
                Cookies
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
