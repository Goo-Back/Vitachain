// Configuration Supabase sécurisée
export const supabaseConfig = {
  url: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  options: {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      flowType: 'pkce', // Recommended for web apps
      debug: process.env.NODE_ENV === 'development'
    },
    db: {
      schema: 'public'
    },
    global: {
      headers: {
        'X-Client-Info': 'vitachain-web/1.0.0'
      }
    }
  }
}

// Validation de configuration
if (!supabaseConfig.url || !supabaseConfig.anonKey) {
  throw new Error(
    'Missing Supabase configuration. Please check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY environment variables.'
  )
}

export default supabaseConfig
