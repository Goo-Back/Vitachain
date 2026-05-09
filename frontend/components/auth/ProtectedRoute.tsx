"use client";

interface ProtectedRouteProps {
  children: any;
  allowedRoles: string[];
  fallback?: any;
}

// Mock auth context for development - in production would use real auth context
const useAuth = () => {
  // In production, this would integrate with actual auth context
  // For now, return mock user data for testing
  return {
    user: {
      role: 'FARMER', // Default role for testing
      id: 'test-user-123'
    },
    loading: false
  };
};

export function ProtectedRoute({ 
  children, 
  allowedRoles, 
  fallback 
}: ProtectedRouteProps) {
  const { user, loading } = useAuth();

  // Show loading spinner while authentication is being checked
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 w-8 h-8">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-4">Please log in to access this page.</p>
          <button 
            onClick={() => window.location.href = '/auth/login'}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Check if user has required role
  const hasAccess = allowedRoles.includes(user.role);

  if (!hasAccess) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center p-8">
          <h2 className="text-3xl font-bold text-red-600 mb-4">Access Denied</h2>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500">Your role: {user.role}</p>
          <p className="text-sm text-gray-500">Required roles: {allowedRoles.join(', ')}</p>
          <button 
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // User has access - render children
  return <>{children}</>;
}

export default ProtectedRoute;
