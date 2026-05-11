'use client'

import { useState, useEffect } from 'react'

// Configuration CSRF
const CSRF_TOKEN_NAME = 'csrf-token'
const CSRF_HEADER_NAME = 'X-CSRF-Token'

// Génération de token CSRF sécurisé
function generateCSRFToken(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

// Stockage du token CSRF en mémoire (pas localStorage pour sécurité)
let csrfToken: string | null = null

// Hook pour gérer la protection CSRF
export function useCSRFProtection() {
  const [token, setToken] = useState<string | null>(null)
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
    
    // Générer le token côté client
    if (!csrfToken) {
      csrfToken = generateCSRFToken()
      setToken(csrfToken)
    }
  }, [])

  // Ajouter le token CSRF aux headers de requête
  const addCSRFToHeaders = (headers: Record<string, string>): Record<string, string> => {
    if (csrfToken && isClient) {
      return {
        ...headers,
        [CSRF_HEADER_NAME]: csrfToken
      }
    }
    return headers
  }

  // Valider le token CSRF côté client
  const validateCSRFToken = (receivedToken: string): boolean => {
    return csrfToken === receivedToken
  }

  return {
    token,
    addCSRFToHeaders,
    validateCSRFToken,
    CSRF_HEADER_NAME
  }
}

// Middleware côté client pour les fetch
export function secureFetch(url: string, options: RequestInit = {}): Promise<Response> {
  // Récupérer le token CSRF
  const getCSRFToken = (): string | null => {
    return csrfToken
  }

  // Préparer les headers sécurisés
  const secureHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // Protection CSRF basique
  }

  // Ajouter le token CSRF pour les requêtes non-GET
  if (!['GET', 'HEAD', 'OPTIONS'].includes(options.method?.toUpperCase() || 'GET')) {
    const token = getCSRFToken()
    if (token) {
      secureHeaders[CSRF_HEADER_NAME] = token
    }
  }

  // Fusionner avec les headers existants
  const headers = {
    ...secureHeaders,
    ...(options.headers as Record<string, string>)
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Pour les cookies HTTP-only
  })
}

// Validation de l'origine pour les requêtes API
export function validateOrigin(origin: string, allowedOrigins: string[]): boolean {
  try {
    const originURL = new URL(origin)
    return allowedOrigins.some(allowed => {
      const allowedURL = new URL(allowed)
      return originURL.origin === allowedURL.origin
    })
  } catch {
    return false
  }
}

// Rate limiting simple côté client
class ClientRateLimiter {
  private requests: Map<string, number[]> = new Map()

  isAllowed(key: string, limit: number, windowMs: number): boolean {
    const now = Date.now()
    const requests = this.requests.get(key) || []
    
    // Nettoyer les anciennes requêtes
    const validRequests = requests.filter(timestamp => now - timestamp < windowMs)
    
    if (validRequests.length >= limit) {
      return false
    }
    
    validRequests.push(now)
    this.requests.set(key, validRequests)
    return true
  }

  getRemainingRequests(key: string, limit: number, windowMs: number): number {
    const now = Date.now()
    const requests = this.requests.get(key) || []
    const validRequests = requests.filter(timestamp => now - timestamp < windowMs)
    return Math.max(0, limit - validRequests.length)
  }

  getResetTime(key: string, windowMs: number): number {
    const requests = this.requests.get(key) || []
    if (requests.length === 0) return 0
    
    const oldestRequest = Math.min(...requests)
    return oldestRequest + windowMs
  }
}

export const rateLimiter = new ClientRateLimiter()

// Protection contre le brute force
export class BruteForceProtection {
  private attempts: Map<string, { count: number; lastAttempt: number; lockedUntil?: number }> = new Map()

  private MAX_ATTEMPTS = 5
  private LOCKOUT_DURATION = 15 * 60 * 1000 // 15 minutes
  private ATTEMPT_WINDOW = 60 * 60 * 1000 // 1 hour

  recordAttempt(identifier: string): { allowed: boolean; remainingAttempts: number; lockoutTime?: number } {
    const now = Date.now()
    const record = this.attempts.get(identifier) || { count: 0, lastAttempt: 0 }

    // Vérifier si l'utilisateur est bloqué
    if (record.lockedUntil && record.lockedUntil > now) {
      return {
        allowed: false,
        remainingAttempts: 0,
        lockoutTime: record.lockedUntil
      }
    }

    // Nettoyer les anciennes tentatives
    if (now - record.lastAttempt > this.ATTEMPT_WINDOW) {
      record.count = 0
    }

    // Enregistrer la nouvelle tentative
    record.count++
    record.lastAttempt = now

    // Vérifier si on doit bloquer
    if (record.count >= this.MAX_ATTEMPTS) {
      record.lockedUntil = now + this.LOCKOUT_DURATION
      this.attempts.set(identifier, record)
      return {
        allowed: false,
        remainingAttempts: 0,
        lockoutTime: record.lockedUntil
      }
    }

    this.attempts.set(identifier, record)
    return {
      allowed: true,
      remainingAttempts: this.MAX_ATTEMPTS - record.count
    }
  }

  resetAttempts(identifier: string): void {
    this.attempts.delete(identifier)
  }

  isLocked(identifier: string): boolean {
    const record = this.attempts.get(identifier)
    if (!record || !record.lockedUntil) return false
    
    const now = Date.now()
    if (record.lockedUntil > now) {
      return true
    }
    
    // Le blocage a expiré, nettoyer
    this.attempts.delete(identifier)
    return false
  }
}

export const bruteForceProtection = new BruteForceProtection()

// Validation des entrées
export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Enlever les chevrons
    .trim()
    .substring(0, 1000) // Limiter la longueur
}

// Validation d'email sécurisée
export function validateEmail(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email) && email.length <= 254
}

// Validation de mot de passe
export function validatePassword(password: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Le mot de passe doit contenir au moins 8 caractères')
  }

  if (password.length > 128) {
    errors.push('Le mot de passe ne peut pas dépasser 128 caractères')
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins une lettre minuscule')
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins une lettre majuscule')
  }

  if (!/\d/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins un chiffre')
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins un caractère spécial')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}
