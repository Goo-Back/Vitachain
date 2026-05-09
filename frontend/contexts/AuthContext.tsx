"use client";

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { UserRole, getDashboardRoute } from '@/types/auth';
import { ApiErrorHandler } from '@/utils/errorHandler';

// Types for the auth context
interface User {
  id: string;
  email: string;
  role: UserRole;
  full_name?: string;
  phone?: string;
  created_at?: string;
  updated_at?: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, role: UserRole, fullName: string) => Promise<void>;
  clearError: () => void;
}

// Action types
type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

// Initial state
const initialState: AuthState = {
  user: null,
  loading: false,
  error: null,
};

// Reducer function
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        loading: true,
        error: null,
      };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        loading: false,
        error: null,
      };
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        loading: false,
        error: action.payload,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        loading: false,
        error: null,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing session on mount
  useEffect(() => {
    checkExistingSession();
  }, []);

  const checkExistingSession = async () => {
    try {
      // Check if user is already logged in via cookie/session
      const response = await fetch('http://localhost:8000/api/auth/me', {
        credentials: 'include', // Important for cookies
      });

      if (response.ok) {
        const userData = await response.json();
        dispatch({ type: 'LOGIN_SUCCESS', payload: userData });
      }
    } catch (error) {
      console.error('Error checking existing session:', error);
      dispatch({ type: 'LOGOUT' });
    }
  };

  const login = async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for cookies
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw data;
      }

      dispatch({ type: 'LOGIN_SUCCESS', payload: data.user });

      // Redirect to appropriate dashboard
      const dashboardRoute = getDashboardRoute(data.user.role);
      window.location.href = dashboardRoute;

    } catch (error) {
      const apiError = ApiErrorHandler.handleError(error);
      const userMessage = ApiErrorHandler.getUserFriendlyMessage(apiError);
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: userMessage
      });
    }
  };

  const logout = async (): Promise<void> => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
      window.location.href = '/auth/login';
    }
  };

  const register = async (
    email: string, 
    password: string, 
    role: UserRole, 
    fullName: string
  ): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          role,
          full_name: fullName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw data;
      }

      // Registration successful, redirect to login
      window.location.href = '/auth/login?message=registration_success';

    } catch (error) {
      const apiError = ApiErrorHandler.handleError(error);
      const userMessage = ApiErrorHandler.getUserFriendlyMessage(apiError);
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: userMessage
      });
    }
  };

  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    register,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;
