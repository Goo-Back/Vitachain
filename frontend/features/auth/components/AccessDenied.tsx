"use client";

interface AccessDeniedProps {
  message?: string;
  showBackButton?: boolean;
  showHomeButton?: boolean;
  userRole?: string; // Add user role prop
}

/**
 * AccessDenied component for unauthorized access
 */
export function AccessDenied({ 
  message = "Access denied. You don't have permission to access this page.",
  showBackButton = true,
  showHomeButton = true,
  userRole
}: AccessDeniedProps) {
  const handleGoBack = () => {
    window.history.back();
  };

  const handleGoHome = () => {
    // Navigate to appropriate dashboard based on user role
    const dashboardRoutes: Record<string, string> = {
      'FARMER': '/dashboard/katara',
      'RESTAURANT': '/dashboard/secondserve',
      'CITIZEN': '/dashboard/farmarket',
      'ADMIN': '/dashboard/admin',
      'SUPPORT': '/dashboard/support'
    };
    
    const route = userRole ? dashboardRoutes[userRole] : '/';
    window.location.href = route;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Accès Refusé
          </h1>
          
          <p className="text-gray-600 text-lg">
            {message}
          </p>

          {/* User role info */}
          {userRole && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Votre rôle:</span> {userRole}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Si vous pensez qu'il s'agit d'une erreur, veuillez contacter l'administrateur système.
              </p>
            </div>
          )}

          {/* Action buttons */}
          <div className="space-y-3">
            {showBackButton && (
              <button
                onClick={handleGoBack}
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Retour
              </button>
            )}
            
            {showHomeButton && (
              <button
                onClick={handleGoHome}
                className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Aller au Tableau de Bord
              </button>
            )}
          </div>
        </div>

        {/* Help section */}
        <div className="bg-gray-100 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">
            Besoin d'aide ?
          </h3>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Vérifiez que vous utilisez le bon compte utilisateur</li>
            <li>• Assurez-vous que votre rôle dispose des permissions nécessaires</li>
            <li>• Contactez votre administrateur si vous pensez qu'il s'agit d'une erreur</li>
            <li>• Pour le support technique, envoyez un email à support@vitachain.ma</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AccessDenied;
