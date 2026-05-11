'use client'

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'

interface LoginFormProps {
  redirectTo?: string
}

export function LoginForm({ redirectTo }: LoginFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState<string | null>(null)
  
  const { signIn, loading } = useAuth()
  const router = useRouter()
  const searchParams = useSearchParams()
  
  // Récupérer les messages d'erreur des paramètres URL
  const urlError = searchParams.get('error')
  const urlRedirectTo = searchParams.get('redirectTo') || redirectTo

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs')
      return
    }

    try {
      const result = await signIn(formData.email, formData.password)
      
      if (!result.success) {
        setError(result.error || 'Erreur de connexion')
        return
      }

      // Rediriger vers la page demandée ou le dashboard
      const destination = urlRedirectTo || '/dashboard'
      router.push(destination)
    } catch (error) {
      setError('Une erreur inattendue est survenue')
      console.error('Login error:', error)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (error) setError(null)
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          Connexion
        </CardTitle>
        <CardDescription className="text-center">
          Accédez à votre compte VitaChain
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Messages d'erreur */}
        {(error || urlError) && (
          <Alert variant="destructive">
            <AlertDescription>
              {error || 
                (urlError === 'session_expired' && 'Votre session a expiré, veuillez vous reconnecter') ||
                'Une erreur est survenue lors de la connexion'
              }
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="votre@email.com"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Mot de passe</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              required
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connexion en cours...
              </>
            ) : (
              'Se connecter'
            )}
          </Button>
        </form>

        <div className="text-center space-y-2">
          <div className="text-sm text-muted-foreground">
            Pas encore de compte?{' '}
            <Button 
              variant="ghost" 
              className="p-0 h-auto font-normal"
              onClick={() => router.push('/auth/signup')}
            >
              Inscrivez-vous
            </Button>
          </div>
          
          <Button 
            variant="ghost" 
            className="p-0 h-auto text-sm"
            onClick={() => router.push('/auth/reset-password')}
          >
            Mot de passe oublié?
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
