import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Routes publiques (ne nécessitent pas d'authentification)
const publicRoutes = [
  '/',
  '/auth/login',
  '/auth/register',
  '/auth/logout',
  '/auth/reset-password',
  '/auth/callback',
  '/api/auth/callback',
  '/signup',
  '/marketplace',
  '/farmers',
  '/services',
  '/health',
  '/_next',
  '/favicon.ico'
]

// Routes par rôle
const roleRoutes = {
  ADMIN: ['/dashboard/admin'],
  FARMER: ['/dashboard/farmer', '/dashboard/katara'],
  RESTAURANT: ['/dashboard/restaurant', '/dashboard/secondserve'],
  CITIZEN: ['/dashboard/citizen', '/dashboard/farmarket', '/dashboard/consumer', '/profile']
}

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const { pathname } = req.nextUrl

  // Skip middleware pour les routes statiques et publiques
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return res
  }

  // Créer client Supabase pour middleware
  const supabase = createMiddlewareClient({ req, res })

  // Vérifier la session
  const {
    data: { session },
    error: sessionError
  } = await supabase.auth.getSession()

  // Pas de session - rediriger vers login
  if (!session || sessionError) {
    const redirectUrl = new URL('/auth/login', req.url)
    redirectUrl.searchParams.set('redirectTo', pathname)
    return NextResponse.redirect(redirectUrl)
  }

  // Rafraîchir la session si nécessaire
  let currentSession = session
  if (session.expires_at && session.expires_at < Date.now() / 1000) {
    try {
      const { data: refreshedSession, error: refreshError } = 
        await supabase.auth.refreshSession()
      
      if (refreshError || !refreshedSession.session) {
        // Refresh failed - rediriger vers login
        const redirectUrl = new URL('/auth/login', req.url)
        redirectUrl.searchParams.set('redirectTo', pathname)
        redirectUrl.searchParams.set('error', 'session_expired')
        return NextResponse.redirect(redirectUrl)
      }

      // Mettre à jour la session
      currentSession = refreshedSession.session
    } catch (error) {
      console.error('Session refresh error:', error)
      const redirectUrl = new URL('/auth/login', req.url)
      redirectUrl.searchParams.set('redirectTo', pathname)
      return NextResponse.redirect(redirectUrl)
    }
  }

  // Récupérer le rôle de l'utilisateur
  const { data: profile, error: profileError } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', currentSession.user.id)
    .single()

  if (profileError || !profile) {
    // Profile non trouvé - rediriger vers complétion
    return NextResponse.redirect(new URL('/auth/complete-profile', req.url))
  }

  const userRole = profile.role

  // Vérifier les permissions de rôle pour les routes spécifiques
  for (const [role, routes] of Object.entries(roleRoutes)) {
    if (userRole !== role && routes.some(route => pathname.startsWith(route))) {
      // Accès non autorisé pour ce rôle
      return NextResponse.redirect(new URL('/unauthorized', req.url))
    }
  }

  // Ajouter des headers de sécurité
  res.headers.set('X-Frame-Options', 'DENY')
  res.headers.set('X-Content-Type-Options', 'nosniff')
  res.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  // Ajouter les informations de session dans les headers pour le serveur
  res.headers.set('x-user-id', currentSession.user.id)
  res.headers.set('x-user-role', userRole)

  return res
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * Feel free to modify this pattern to include more paths.
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
