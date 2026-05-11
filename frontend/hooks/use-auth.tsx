'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session, AuthError } from '@supabase/supabase-js'
import { supabase, getCurrentSession, refreshSession, signOut } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

// Types pour l'authentification
export interface SerializableUser {
  id: string
  email: string
  role?: string
  full_name?: string
  phone?: string
  created_at?: string
  updated_at?: string
}

export interface SerializableSession {
  user: SerializableUser | null
  access_token?: string
  refresh_token?: string
  expires_at?: number
}

export interface AuthState {
  user: SerializableUser | null
  session: SerializableSession | null
  loading: boolean
  error: AuthError | null
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
    session: null,
    loading: true,
    error: null,
    isAuthenticated: false
  })

  const router = useRouter()

  // Helper pour transformer les objets Supabase en objets sérialisables
  const serializeUser = (user: any) => {
    if (!user) return null
    
    return {
      id: user.id || '',
      email: user.email || '',
      role: user.user_metadata?.role || user.role || 'CITIZEN',
      full_name: user.user_metadata?.full_name || user.full_name,
      phone: user.user_metadata?.phone || user.phone,
      created_at: user.created_at,
      updated_at: user.updated_at
    }
  }

  const serializeSession = (session: any) => {
    if (!session) return null
    
    return {
      user: serializeUser(session.user),
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      expires_at: session.expires_at
    }
  }

  // Mise à jour de l'état d'authentification avec objets sérialisables
  const updateAuthState = (session: Session | null, error: AuthError | null = null) => {
    const serializedSession = serializeSession(session)
    setAuthState({
      user: serializedSession?.user || null,
      session: serializedSession,
      loading: false,
      error,
      isAuthenticated: !!serializedSession?.user
    })
  }

  // Initialisation et écoute des changements de session
  useEffect(() => {
    let mounted = true

    // Récupérer la session initiale
    const initializeAuth = async () => {
      try {
        const { session, error } = await getCurrentSession()
        if (mounted) {
          updateAuthState(session, error)
        }
      } catch (error) {
        if (mounted) {
          updateAuthState(null, error as AuthError)
        }
      }
    }

    initializeAuth()

    // Écouter les changements d'authentification
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (mounted) {
          updateAuthState(session)
          
          // Rediriger selon l'événement
          if (event === 'SIGNED_IN' && session) {
            router.push('/dashboard')
          } else if (event === 'SIGNED_OUT') {
            router.push('/auth/login')
          }
        }
      }
    )

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [router])

  // Fonction de connexion
  const signIn = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }))
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        setAuthState(prev => ({ ...prev, loading: false, error }))
        return { success: false, error: error.message }
      }

      updateAuthState(data.session)
      return { success: true }
    } catch (error) {
      const authError = error as AuthError
      setAuthState(prev => ({ ...prev, loading: false, error: authError }))
      return { success: false, error: authError.message }
    }
  }

  // Fonction d'inscription
  const signUp = async (email: string, password: string, metadata?: any) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }))
      
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      })

      if (error) {
        setAuthState(prev => ({ ...prev, loading: false, error }))
        return { success: false, error: error.message }
      }

      // Ne pas mettre à jour l'état immédiatement pour l'inscription
      // L'utilisateur doit vérifier son email d'abord
      setAuthState(prev => ({ ...prev, loading: false }))
      return { success: true }
    } catch (error) {
      const authError = error as AuthError
      setAuthState(prev => ({ ...prev, loading: false, error: authError }))
      return { success: false, error: authError.message }
    }
  }

  // Fonction de déconnexion
  const handleSignOut = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      await signOut()
      updateAuthState(null)
      router.push('/auth/login')
    } catch (error) {
      console.error('Sign out error:', error)
      // Forcer la déconnexion même en cas d'erreur
      updateAuthState(null)
      router.push('/auth/login')
    }
  }

  // Fonction de réinitialisation de mot de passe
  const resetPassword = async (email: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }))
      
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })

      setAuthState(prev => ({ ...prev, loading: false }))

      if (error) {
        return { success: false, error: error.message }
      }

      return { success: true }
    } catch (error) {
      const authError = error as AuthError
      setAuthState(prev => ({ ...prev, loading: false, error: authError }))
      return { success: false, error: authError.message }
    }
  }

  // Rafraîchir la session manuellement
  const handleRefreshSession = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      const { session, error } = await refreshSession()
      updateAuthState(session, error)
    } catch (error) {
      const authError = error as AuthError
      updateAuthState(null, authError)
    }
  }

  const value: AuthContextValue = {
    ...authState,
    signIn,
    signUp,
    signOut: handleSignOut,
    resetPassword,
    refreshSession: handleRefreshSession
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
      const userRole = auth.user.role
      const roleHierarchy: Record<string, number> = {
        'ADMIN': 4,
        'RESTAURANT': 3,
        'FARMER': 2,
        'CITIZEN': 1
      }

      const userLevel = roleHierarchy[userRole] || 0
      const requiredLevel = roleHierarchy[requiredRole] || 0

      if (userLevel < requiredLevel) {
        router.push('/unauthorized')
      }
    }
  }, [auth.loading, auth.isAuthenticated, auth.user, requiredRole, router])

  return auth
}
