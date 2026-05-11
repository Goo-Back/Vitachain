import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/database'
import { cookies } from 'next/headers'

// Configuration avec fallback pour le build
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ymogoemuzqyjsdjhzpnz.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'

// Client Supabase pour les composants serveur
export const createServerSupabaseClient = () => {
  const cookieStore = cookies()
  return createServerComponentClient<Database>({
    cookies: () => cookieStore
  })
}

// Helper pour obtenir la session côté serveur avec sérialisation
export const getServerSession = async () => {
  const supabase = createServerSupabaseClient()
  const { data: { session }, error } = await supabase.auth.getSession()
  
  // Retourner un objet sérialisable
  return {
    session: session ? {
      user: session.user ? {
        id: session.user.id,
        email: session.user.email || '',
        role: session.user.user_metadata?.role || 'CITIZEN',
        full_name: session.user.user_metadata?.full_name,
        phone: session.user.user_metadata?.phone,
        created_at: session.user.created_at,
        updated_at: session.user.updated_at
      } : null,
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      expires_at: session.expires_at
    } : null,
    error: error ? {
      message: error.message,
      status: error.status
    } : null
  }
}

// Helper pour obtenir l'utilisateur courant côté serveur
export const getServerUser = async () => {
  const { session } = await getServerSession()
  return session?.user || null
}

// Helper pour vérifier le rôle côté serveur
export const getServerUserRole = async () => {
  const user = await getServerUser()
  return user?.role || 'CITIZEN'
}

// Helper pour vérifier si l'utilisateur est authentifié côté serveur
export const isServerAuthenticated = async () => {
  const { session } = await getServerSession()
  return !!session?.user
}

// Helper pour créer un client avec fallback
export const createFallbackClient = () => {
  return createClient<Database>(supabaseUrl, supabaseAnonKey)
}
