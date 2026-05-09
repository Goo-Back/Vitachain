"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

export default function MagicLinkCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const [userInfo, setUserInfo] = useState<any>(null);
  const [redirectTo, setRedirectTo] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    
    if (!token) {
      setStatus("error");
      setMessage("Lien magique invalide ou manquant");
      return;
    }

    verifyMagicLink(token);
  }, [searchParams]);

  const verifyMagicLink = async (token: string) => {
    try {
      const response = await fetch(`/api/auth/magic-link/verify?token=${encodeURIComponent(token)}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (response.ok) {
        setStatus("success");
        setMessage(data.message);
        setUserInfo(data.user);
        setRedirectTo(data.redirect_to);

        // Redirect to dashboard after a short delay
        setTimeout(() => {
          router.push(data.redirect_to);
        }, 2000);
      } else {
        setStatus("error");
        setMessage(data.error?.message || "Lien magique invalide ou expiré");
      }
    } catch (error) {
      console.error("Magic link verification error:", error);
      setStatus("error");
      setMessage("Erreur de connexion. Veuillez réessayer.");
    }
  };

  const renderStatusIcon = () => {
    switch (status) {
      case "loading":
        return (
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto"></div>
        );
      case "success":
        return (
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
            <svg
              className="h-8 w-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
          </div>
        );
      case "error":
        return (
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
            <svg
              className="h-8 w-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </div>
        );
    }
  };

  const renderStatusMessage = () => {
    switch (status) {
      case "loading":
        return "Vérification du lien magique...";
      case "success":
        return "Connexion réussie!";
      case "error":
        return "Échec de la connexion";
    }
  };

  const renderStatusColor = () => {
    switch (status) {
      case "loading":
        return "text-blue-600";
      case "success":
        return "text-green-600";
      case "error":
        return "text-red-600";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="flex justify-center items-center mb-6">
            <div className="text-3xl font-bold text-green-600">🌱 VitaChain</div>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900">
            Vérification du lien magique
          </h2>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Status Icon */}
          <div className="mb-6">
            {renderStatusIcon()}
          </div>

          {/* Status Message */}
          <div className="text-center">
            <h3 className={`text-xl font-semibold ${renderStatusColor()}`}>
              {renderStatusMessage()}
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              {message}
            </p>
          </div>

          {/* Success State */}
          {status === "success" && userInfo && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <div className="text-center">
                <p className="text-sm text-green-800">
                  Bienvenue <strong>{userInfo.full_name}</strong>!
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Vous êtes connecté en tant que <strong>{userInfo.role}</strong>
                </p>
                <p className="text-xs text-green-600 mt-2">
                  Redirection vers votre tableau de bord...
                </p>
              </div>
            </div>
          )}

          {/* Error State */}
          {status === "error" && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="text-center">
                  <p className="text-sm text-red-800">
                    Le lien magique est invalide ou a expiré.
                  </p>
                  <p className="text-xs text-red-700 mt-1">
                    Veuillez demander un nouveau lien magique.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <Link
                  href="/auth/login/magic-link"
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Demander un nouveau lien magique
                </Link>

                <Link
                  href="/auth/login"
                  className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Retour à la connexion classique
                </Link>
              </div>
            </div>
          )}

          {/* Loading State */}
          {status === "loading" && (
            <div className="mt-6">
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Veuillez patienter pendant que nous vérifions votre lien magique...
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Cette opération ne prend que quelques secondes.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Help Section */}
        {status === "error" && (
          <div className="mt-6 text-center">
            <div className="text-sm text-gray-600">
              <p className="mb-2">
                <strong>Besoin d'aide ?</strong>
              </p>
              <ul className="text-left space-y-1">
                <li>• Vérifiez que vous avez bien cliqué sur le lien complet</li>
                <li>• Assurez-vous que le lien n'a pas expiré (15 minutes)</li>
                <li>• Chaque lien magique ne peut être utilisé qu'une seule fois</li>
                <li>• Contactez le support si le problème persiste</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
