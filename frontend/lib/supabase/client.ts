import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/database'

// Configuration avec fallback pour le build
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ymogoemuzqyjsdjhzpnz.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'

// Client Supabase pour les composants client
export const supabase = createClientComponentClient<Database>() || createClient<Database>(supabaseUrl, supabaseAnonKey)

// Helper pour les opérations authentifiées
export const createAuthenticatedClient = () => {
  return supabase
}

// Helper pour vérifier la session côté client
export const getCurrentSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// Helper pour rafraîchir la session
export const refreshSession = async () => {
  const { data, error } = await supabase.auth.refreshSession()
  return { session: data.session, error }
}

// Helper pour le logout
export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}
