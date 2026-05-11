'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

// Types purs sérialisables
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
  signUp: (email: string, password: string, metadata?: any) => Promise<{ success: boolean; error?: string }>
  signOut: () => Promise<void>
  resetPassword: (email: string) => Promise<{ success: boolean; error?: string }>
  refreshSession: () => Promise<void>
}

// Contexte d'authentification
const AuthContext = createContext<AuthContextValue | undefined>(undefined)

// Provider d'authentification
export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
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
      setAuthState(prev => ({ ...prev, loading: true, error: null }))
      
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include',
          cache: 'no-store'
        })

        if (response.ok) {
          const userData = await response.json()
          
          // Transformer les données en objet sérialisable
          const serializableUser = serializeUserData(userData)
          
          setAuthState(prev => ({
            ...prev,
            user: serializableUser,
            isAuthenticated: true,
            loading: false
          }))
        } else {
          setAuthState(prev => ({
            ...prev,
            user: null,
            isAuthenticated: false,
            loading: false
          }))
        }
      } catch (error) {
        console.error('Error checking session:', error)
        setAuthState(prev => ({
          ...prev,
          error: 'Session check failed',
          loading: false
        }))
      }
    }

    checkExistingSession()
  }, [])

  // Fonction de connexion
  const signIn = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }))

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

      setAuthState(prev => ({
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
      setAuthState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }))
      return { success: false, error: errorMessage }
    }
  }

  // Fonction d'inscription
  const signUp = async (email: string, password: string, metadata?: any): Promise<{ success: boolean; error?: string }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          role: metadata?.role || 'CITIZEN',
          full_name: metadata?.full_name,
          phone: metadata?.phone,
          ...metadata
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error?.message || 'Registration failed')
      }

      setAuthState(prev => ({ ...prev, loading: false }))
      return { success: true }
    } catch (error) {
      const errorMessage = (error as Error).message
      setAuthState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }))
      return { success: false, error: errorMessage }
    }
  }

  // Fonction de déconnexion
  const signOut = async (): Promise<void> => {
    setAuthState(prev => ({ ...prev, loading: true }))

    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setAuthState(prev => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        loading: false
      }))
      router.push('/auth/login')
    }
  }

  // Fonction de réinitialisation de mot de passe
  const resetPassword = async (email: string): Promise<{ success: boolean; error?: string }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error?.message || 'Reset password failed')
      }

      setAuthState(prev => ({ ...prev, loading: false }))
      return { success: true }
    } catch (error) {
      const errorMessage = (error as Error).message
      setAuthState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }))
      return { success: false, error: errorMessage }
    }
  }

  // Rafraîchir la session manuellement
  const refreshSession = async (): Promise<void> => {
    setAuthState(prev => ({ ...prev, loading: true }))

    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include',
        cache: 'no-store'
      })

      if (response.ok) {
        const userData = await response.json()
        const serializableUser = serializeUserData(userData)
        
        setAuthState(prev => ({
          ...prev,
          user: serializableUser,
          isAuthenticated: true,
          loading: false
        }))
      } else {
        setAuthState(prev => ({
          ...prev,
          user: null,
          isAuthenticated: false,
          loading: false
        }))
      }
    } catch (error) {
      console.error('Session refresh error:', error)
      setAuthState(prev => ({
        ...prev,
        error: 'Session refresh failed',
        loading: false
      }))
    }
  }

  const value: AuthContextValue = {
    ...authState,
    signIn,
    signUp,
    signOut,
    resetPassword,
    refreshSession
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
