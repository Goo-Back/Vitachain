import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ymogoemuzqyjsdjhzpnz.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Alternative export for compatibility with existing code
export const createSupabaseClient = () => createClient(supabaseUrl, supabaseAnonKey)
