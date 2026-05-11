'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'

interface SignupFormData {
  email: string
  password: string
  confirmPassword: string
  fullName: string
  role: 'CITIZEN' | 'FARMER' | 'RESTAURANT'
}

const roleOptions = [
  { value: 'CITIZEN', label: 'Citoyen', description: 'Accéder aux produits locaux' },
  { value: 'FARMER', label: 'Agriculteur', description: 'Vendre vos produits' },
  { value: 'RESTAURANT', label: 'Restaurant', description: 'Acheter en gros' }
] as const

export function SignupForm() {
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: 'CITIZEN'
  })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const { signUp, loading } = useAuth()
  const router = useRouter()

  const validateForm = (): string | null => {
    if (!formData.email || !formData.password || !formData.fullName) {
      return 'Veuillez remplir tous les champs obligatoires'
    }

    if (formData.password.length < 8) {
      return 'Le mot de passe doit contenir au moins 8 caractères'
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Les mots de passe ne correspondent pas'
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      return 'Veuillez entrer une adresse email valide'
    }

    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      const result = await signUp(formData.email, formData.password, {
        full_name: formData.fullName,
        role: formData.role
      })
      
      if (!result.success) {
        setError(result.error || 'Erreur lors de l\'inscription')
        return
      }

      setSuccess('Inscription réussie! Veuillez vérifier votre email pour activer votre compte.')
      
      // Rediriger vers login après 3 secondes
      setTimeout(() => {
        router.push('/auth/login?message=signup_success')
      }, 3000)
      
    } catch (error) {
      setError('Une erreur inattendue est survenue')
      console.error('Signup error:', error)
    }
  }

  const handleInputChange = (field: keyof SignupFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (error) setError(null)
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          Créer un compte
        </CardTitle>
        <CardDescription className="text-center">
          Rejoignez la communauté VitaChain
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Messages d'erreur et succès */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {success && (
          <Alert>
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">Nom complet</Label>
            <Input
              id="fullName"
              type="text"
              placeholder="Jean Dupont"
              value={formData.fullName}
              onChange={(e) => handleInputChange('fullName', e.target.value)}
              required
              disabled={loading}
              autoComplete="name"
            />
          </div>

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
            <Label htmlFor="role">Type de compte</Label>
            <select
              id="role"
              value={formData.role}
              onChange={(e) => handleInputChange('role', e.target.value)}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              {roleOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label} - {option.description}
                </option>
              ))}
            </select>
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
              autoComplete="new-password"
            />
            <p className="text-xs text-muted-foreground">
              Minimum 8 caractères
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              required
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading || !!success}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Inscription en cours...
              </>
            ) : (
              'Créer mon compte'
            )}
          </Button>
        </form>

        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Déjà un compte?{' '}
            <Button 
              variant="ghost" 
              className="p-0 h-auto font-normal"
              onClick={() => router.push('/auth/login')}
            >
              Se connecter
            </Button>
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
