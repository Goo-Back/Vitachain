// Configuration des headers de sécurité pour Next.js

export const securityHeaders = {
  // Content Security Policy
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://js.stripe.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://ymogoemuzqyjsdjhzpnz.supabase.co ws://ymogoemuzqyjsdjhzpnz.supabase.co",
    "media-src 'self' https:",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests"
  ].join('; '),

  // Prévenir le clickjacking
  'X-Frame-Options': 'DENY',

  // Prévenir le MIME sniffing
  'X-Content-Type-Options': 'nosniff',

  // Contrôler les informations de référent
  'Referrer-Policy': 'strict-origin-when-cross-origin',

  // Politique de permissions
  'Permissions-Policy': [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'payment=()',
    'usb=()',
    'magnetometer=()',
    'gyroscope=()',
    'accelerometer=()',
    'ambient-light-sensor=()',
    'autoplay=()',
    'encrypted-media=()',
    'fullscreen=(self)',
    'picture-in-picture=(self)'
  ].join(', '),

  // HSTS (uniquement en HTTPS)
  ...(process.env.NODE_ENV === 'production' ? {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
  } : {}),

  // Cache control pour les pages sensibles
  'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
  'Pragma': 'no-cache',
  'Expires': '0'
}

// Headers pour les API routes
export const apiSecurityHeaders = {
  ...securityHeaders,
  'Access-Control-Allow-Origin': process.env.NODE_ENV === 'production' 
    ? 'https://vitachain.ma' 
    : 'http://localhost:3000',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-CSRF-Token',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400', // 24 hours
}

// Middleware pour ajouter les headers de sécurité
export function addSecurityHeaders(response: Response): Response {
  Object.entries(securityHeaders).forEach(([key, value]) => {
    response.headers.set(key, value)
  })
  return response
}

// Middleware pour les API routes
export function addAPISecurityHeaders(response: Response): Response {
  Object.entries(apiSecurityHeaders).forEach(([key, value]) => {
    response.headers.set(key, value)
  })
  return response
}

// Validation des headers entrants
export function validateSecurityHeaders(headers: Headers): boolean {
  // Vérifier l'origine
  const origin = headers.get('origin')
  const referer = headers.get('referer')
  
  const allowedOrigins = process.env.NODE_ENV === 'production'
    ? ['https://vitachain.ma']
    : ['http://localhost:3000', 'https://localhost:3000']

  if (origin && !allowedOrigins.includes(origin)) {
    return false
  }

  if (referer && !allowedOrigins.some(allowed => referer.startsWith(allowed))) {
    return false
  }

  // Vérifier le User-Agent (optionnel)
  const userAgent = headers.get('user-agent')
  if (!userAgent || userAgent.length < 10) {
    return false
  }

  return true
}

// Configuration CORS sécurisée
export const corsConfig = {
  origin: process.env.NODE_ENV === 'production'
    ? ['https://vitachain.ma']
    : ['http://localhost:3000', 'https://localhost:3000'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-CSRF-Token',
    'X-Requested-With'
  ],
  credentials: true,
  maxAge: 86400, // 24 hours
  optionsSuccessStatus: 200
}

// Rate limiting par IP
export class RateLimitStore {
  private store: Map<string, { count: number; resetTime: number }> = new Map()

  isAllowed(ip: string, limit: number, windowMs: number): boolean {
    const now = Date.now()
    const record = this.store.get(ip)

    if (!record || now > record.resetTime) {
      this.store.set(ip, {
        count: 1,
        resetTime: now + windowMs
      })
      return true
    }

    if (record.count >= limit) {
      return false
    }

    record.count++
    return true
  }

  getRemaining(ip: string, limit: number): number {
    const record = this.store.get(ip)
    if (!record) return limit

    return Math.max(0, limit - record.count)
  }

  getResetTime(ip: string): number {
    const record = this.store.get(ip)
    return record?.resetTime || 0
  }

  // Nettoyer les anciennes entrées
  cleanup(): void {
    const now = Date.now()
    const entries = Array.from(this.store.entries())
    for (const [ip, record] of entries) {
      if (now > record.resetTime) {
        this.store.delete(ip)
      }
    }
  }
}

export const rateLimitStore = new RateLimitStore()

// Nettoyage périodique
if (typeof setInterval !== 'undefined') {
  setInterval(() => {
    rateLimitStore.cleanup()
  }, 60000) // Nettoyer chaque minute
}
