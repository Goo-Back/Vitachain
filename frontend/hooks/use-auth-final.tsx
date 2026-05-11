'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

// Types sérialisables purs
export interface SerializableUser {
  id: string
  email: string
  role: string
  full_name?: string
  phone?: string
  created_at?: string
  updated_at?: string
}

export interface AuthState {
  user: SerializableUser | null
  loading: boolean
  error: string | null
  isAuthenticated: boolean
}

export interface AuthContextValue extends AuthState {
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  signOut: () => Promise<void>
  clearError: () => void
}

// Contexte d'authentification
const AuthContext = createContext<AuthContextValue | undefined>(undefined)

// Provider d'authentification avec sérialisation
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false
  })

  const router = useRouter()

  // Helper pour transformer les données API en objets sérialisables
  const serializeUserData = (userData: any): SerializableUser => {
    return {
      id: userData.id || '',
      email: userData.email || '',
      role: userData.role || 'CITIZEN',
      full_name: userData.full_name,
      phone: userData.phone,
      created_at: userData.created_at,
      updated_at: userData.updated_at
    }
  }

  // Vérifier la session existante au montage
  useEffect(() => {
    const checkExistingSession = async () => {
      setState(prev => ({ ...prev, loading: true, error: null }))
      
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include',
          cache: 'no-store'
        })

        if (response.ok) {
          const userData = await response.json()
          
          // Transformer les données en objet sérialisable
          const serializableUser = serializeUserData(userData)
          
          setState(prev => ({
            ...prev,
            user: serializableUser,
            isAuthenticated: true,
            loading: false
          }))
        } else {
          setState(prev => ({
            ...prev,
            user: null,
            isAuthenticated: false,
            loading: false
          }))
        }
      } catch (error) {
        console.error('Error checking session:', error)
        setState(prev => ({
          ...prev,
          error: 'Session check failed',
          loading: false
        }))
      }
    }

    checkExistingSession()
  }, [])

  // Fonction de connexion avec sérialisation
  const signIn = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error?.message || 'Login failed')
      }

      const data = await response.json()
      
      // Transformer les données en objet sérialisable
      const serializableUser = serializeUserData(data.user)

      setState(prev => ({
        ...prev,
        user: serializableUser,
        isAuthenticated: true,
        loading: false
      }))
      
      // Redirection selon le rôle
      const dashboardRoutes: Record<string, string> = {
        'ADMIN': '/dashboard/admin',
        'RESTAURANT': '/dashboard/restaurant',
        'FARMER': '/dashboard/farmer',
        'CITIZEN': '/dashboard/citizen'
      }
      
      const redirectRoute = dashboardRoutes[serializableUser.role] || '/dashboard/citizen'
      router.push(redirectRoute)
      
      return { success: true }
    } catch (error) {
      const errorMessage = (error as Error).message
      setState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }))
      return { success: false, error: errorMessage }
    }
  }

  // Fonction de déconnexion
  const signOut = async (): Promise<void> => {
    setState(prev => ({ ...prev, loading: true }))

    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setState(prev => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        loading: false
      }))
      router.push('/auth/login')
    }
  }

  // Fonction pour effacer les erreurs
  const clearError = (): void => {
    setState(prev => ({ ...prev, error: null }))
  }

  const value: AuthContextValue = {
    ...state,
    signIn,
    signOut,
    clearError,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook pour utiliser l'authentification
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Hook pour vérifier si l'utilisateur est authentifié
export function useRequireAuth() {
  const auth = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!auth.loading && !auth.isAuthenticated) {
      router.push('/auth/login')
    }
  }, [auth.loading, auth.isAuthenticated, router])

  return auth
}

// Hook pour vérifier les rôles
export function useRequireRole(requiredRole: string) {
  const auth = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!auth.loading && auth.isAuthenticated && auth.user) {
      const roleHierarchy: Record<string, number> = {
        'ADMIN': 4,
        'RESTAURANT': 3,
        'FARMER': 2,
        'CITIZEN': 1
      }

      const userLevel = roleHierarchy[auth.user.role] || 0
      const requiredLevel = roleHierarchy[requiredRole] || 0

      if (userLevel < requiredLevel) {
        router.push('/unauthorized')
      }
    }
  }, [auth.loading, auth.isAuthenticated, auth.user, requiredRole, router])

  return auth
}
