import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { Database } from '@/types/database'

// Client Supabase pour les composants serveur
export const createServerSupabaseClient = () => {
  const cookieStore = cookies()
  return createServerComponentClient<Database>({
    cookies: () => cookieStore
  })
}

// Helper pour vérifier la session côté serveur
export const getServerSession = async () => {
  const supabase = createServerSupabaseClient()
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// Helper pour récupérer le profil utilisateur côté serveur
export const getServerUserProfile = async (userId: string) => {
  const supabase = createServerSupabaseClient()
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single()
  
  return { profile: data, error }
}

// Helper pour vérifier les permissions côté serveur
export const checkServerRole = async (userId: string, requiredRole: string) => {
  const { profile, error } = await getServerUserProfile(userId)
  
  if (error || !profile) {
    return { hasPermission: false, error }
  }
  
  const roleHierarchy = {
    'ADMIN': 4,
    'RESTAURANT': 3,
    'FARMER': 2,
    'CITIZEN': 1
  }
  
  const userLevel = roleHierarchy[(profile as any).role as keyof typeof roleHierarchy] || 0
  const requiredLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 0
  
  return { 
    hasPermission: userLevel >= requiredLevel, 
    userRole: (profile as any).role,
    error: null 
  }
}
