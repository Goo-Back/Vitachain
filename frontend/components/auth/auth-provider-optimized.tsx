'use client'

import { createContext, useContext, useEffect, useReducer, ReactNode } from 'react'
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

// Contexte d'authentification optimisé
const AuthContext = createContext<AuthContextValue | undefined>(undefined)

// Action types pour le reducer
type AuthAction = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: SerializableUser | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SIGN_OUT' }

// Reducer simple pour éviter les problèmes de sérialisation
const authReducer = (prevState: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...prevState, loading: action.payload }
    case 'SET_USER':
      return { 
        ...prevState, 
        user: action.payload, 
        isAuthenticated: !!action.payload,
        loading: false 
      }
    case 'SET_ERROR':
      return { ...prevState, error: action.payload, loading: false }
    case 'SIGN_OUT':
      return { user: null, loading: false, error: null, isAuthenticated: false }
    default:
      return prevState
  }
}

// Provider d'authentification avec sérialisation
export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, dispatch] = useReducer(authReducer, {
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false
  })

  const router = useRouter()

  // Vérifier la session existante au montage
  useEffect(() => {
    const checkExistingSession = async () => {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include',
          cache: 'no-store'
        })

        if (response.ok) {
          const userData = await response.json()
          
          // Transformer les données en objet sérialisable
          const serializableUser: SerializableUser = {
            id: userData.id || '',
            email: userData.email || '',
            role: userData.role || 'CITIZEN',
            full_name: userData.full_name,
            phone: userData.phone,
            created_at: userData.created_at,
            updated_at: userData.updated_at
          }
          
          dispatch({ type: 'SET_USER', payload: serializableUser })
        } else {
          dispatch({ type: 'SET_USER', payload: null })
        }
      } catch (error) {
        console.error('Error checking session:', error)
        dispatch({ type: 'SET_ERROR', payload: 'Session check failed' })
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false })
      }
    }

    checkExistingSession()
  }, [])

  // Fonction de connexion avec sérialisation
  const signIn = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    dispatch({ type: 'SET_LOADING', payload: true })
    dispatch({ type: 'SET_ERROR', payload: null })

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
      const serializableUser: SerializableUser = {
        id: data.user.id || '',
        email: data.user.email || '',
        role: data.user.role || 'CITIZEN',
        full_name: data.user.full_name,
        phone: data.user.phone,
        created_at: data.user.created_at,
        updated_at: data.user.updated_at
      }

      dispatch({ type: 'SET_USER', payload: serializableUser })
      
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
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      return { success: false, error: errorMessage }
    }
  }

  // Fonction de déconnexion
  const signOut = async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true })

    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      dispatch({ type: 'SIGN_OUT' })
      router.push('/auth/login')
    }
  }

  // Fonction pour effacer les erreurs
  const clearError = (): void => {
    dispatch({ type: 'SET_ERROR', payload: null })
  }

  const value: AuthContextValue = {
    ...authState,
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
