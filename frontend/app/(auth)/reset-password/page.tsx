"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Mail, ArrowLeft, Shield } from "lucide-react";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/auth/password-reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          setError("Trop de tentatives de réinitialisation. Veuillez réessayer plus tard.");
        } else if (response.status === 404) {
          setError("Aucun compte trouvé avec cette adresse email.");
        } else {
          setError(data.error?.message || "Une erreur est survenue. Veuillez réessayer.");
        }
        return;
      }

      setIsSuccess(true);
    } catch (err) {
      setError("Erreur de connexion. Veuillez vérifier votre connexion internet.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <Mail className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-2xl text-green-800">Email envoyé!</CardTitle>
            <CardDescription className="text-green-600">
              Nous avons envoyé un lien de réinitialisation à votre adresse email.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert className="bg-green-50 border-green-200">
              <Shield className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700">
                <strong>Important:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Le lien expirera dans 1 heure</li>
                  <li>Vérifiez votre dossier spam si vous ne recevez pas l'email</li>
                  <li>Ne partagez jamais ce lien avec d'autres personnes</li>
                </ul>
              </AlertDescription>
            </Alert>
            
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => window.location.href = "https://mail.google.com"}
              >
                <Mail className="h-4 w-4 mr-2" />
                Ouvrir ma boîte email
              </Button>
              
              <Button 
                variant="ghost" 
                className="w-full"
                onClick={() => setIsSuccess(false)}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Envoyer un autre email
              </Button>
            </div>
            
            <div className="text-center">
              <Link 
                href="/auth/login" 
                className="text-sm text-green-600 hover:text-green-800 underline"
              >
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Shield className="h-6 w-6 text-red-600" />
          </div>
          <CardTitle className="text-2xl text-gray-800">Réinitialiser le mot de passe</CardTitle>
          <CardDescription className="text-gray-600">
            Entrez votre adresse email pour recevoir un lien de réinitialisation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="bg-red-50 border-red-200">
                <AlertDescription className="text-red-700">
                  {error}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Adresse email</Label>
              <Input
                id="email"
                type="email"
                placeholder="nom@exemple.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="w-full"
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full bg-red-600 hover:bg-red-700"
              disabled={isLoading || !email}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Envoi en cours...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Envoyer le lien de réinitialisation
                </>
              )}
            </Button>
          </form>
          
          <div className="mt-6 text-center space-y-2">
            <Link 
              href="/auth/login" 
              className="text-sm text-green-600 hover:text-green-800 underline flex items-center justify-center"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Retour à la connexion
            </Link>
            
            <div className="text-xs text-gray-500">
              Pas encore de compte?{" "}
              <Link href="/auth/register" className="text-green-600 hover:text-green-800 underline">
                S'inscrire
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
