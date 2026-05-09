// Standardized error handling utilities for VitaChain frontend

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface ErrorResponse {
  error: ApiError;
}

export class ApiErrorHandler {
  /**
   * Parse and handle API error responses
   */
  static handleError(error: any): ApiError {
    // If it's a Response object, try to parse JSON
    if (error instanceof Response) {
      return this.handleSyncResponseError(error);
    }

    // If it's already an error object with our structure
    if (error && typeof error === 'object' && error.error) {
      return error.error as ApiError;
    }

    // If it's a standard Error object
    if (error instanceof Error) {
      return {
        code: 'CLIENT_ERROR',
        message: error.message || 'An unexpected error occurred'
      };
    }

    // Fallback for unknown error types
    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred'
    };
  }

  /**
   * Handle HTTP response errors (synchronous)
   */
  private static handleSyncResponseError(response: Response): ApiError {
    // For synchronous handling, we can't parse JSON, so return based on status
    return {
      code: `HTTP_${response.status}`,
      message: this.getDefaultMessage(response.status)
    };
  }

  /**
   * Handle HTTP response errors (asynchronous)
   */
  private static async handleResponseError(response: Response): Promise<ApiError> {
    try {
      const data = await response.json();
      
      // If the response has our expected error structure
      if (data.error) {
        return data.error as ApiError;
      }
      
      // Otherwise create a generic error based on status
      return {
        code: `HTTP_${response.status}`,
        message: data.message || this.getDefaultMessage(response.status)
      };
    } catch {
      // If JSON parsing fails, return a generic error
      return {
        code: `HTTP_${response.status}`,
        message: this.getDefaultMessage(response.status)
      };
    }
  }

  /**
   * Get default error messages based on HTTP status codes
   */
  private static getDefaultMessage(status: number): string {
    switch (status) {
      case 400:
        return 'Invalid request data';
      case 401:
        return 'Authentication required';
      case 403:
        return 'Access denied';
      case 404:
        return 'Resource not found';
      case 409:
        return 'Resource conflict';
      case 422:
        return 'Validation error';
      case 429:
        return 'Too many requests';
      case 500:
        return 'Server error';
      case 502:
        return 'Service temporarily unavailable';
      case 503:
        return 'Service unavailable';
      default:
        return 'Request failed';
    }
  }

  /**
   * Get user-friendly error messages
   */
  static getUserFriendlyMessage(error: ApiError): string {
    const messageMap: Record<string, string> = {
      'VALIDATION_ERROR': 'Please check your input and try again',
      'EMAIL_EXISTS': 'An account with this email already exists',
      'INVALID_CREDENTIALS': 'Invalid email or password',
      'EMAIL_NOT_VERIFIED': 'Please verify your email before continuing',
      'USER_NOT_FOUND': 'Account not found',
      'ACCOUNT_BLOCKED': 'Your account has been temporarily blocked',
      'RATE_LIMIT_EXCEEDED': 'Too many attempts. Please try again later',
      'WEAK_PASSWORD': 'Password does not meet security requirements',
      'PROFILE_NOT_FOUND': 'Profile not found',
      'DEVICE_NOT_FOUND': 'Device not found',
      'ALERT_NOT_FOUND': 'Alert not found',
      'UNAUTHORIZED': 'Please log in to continue',
      'FORBIDDEN': 'You do not have permission to perform this action',
      'INTERNAL_ERROR': 'Something went wrong. Please try again',
      'DATABASE_ERROR': 'Database error. Please try again',
      'NETWORK_ERROR': 'Network connection error',
      'TIMEOUT_ERROR': 'Request timed out',
      'HTTP_400': 'Invalid request',
      'HTTP_401': 'Authentication required',
      'HTTP_403': 'Access denied',
      'HTTP_404': 'Resource not found',
      'HTTP_429': 'Too many requests',
      'HTTP_500': 'Server error',
      'HTTP_503': 'Service unavailable'
    };

    return messageMap[error.code] || error.message || 'An error occurred';
  }

  /**
   * Check if error is recoverable (user can retry)
   */
  static isRecoverable(error: ApiError): boolean {
    const recoverableCodes = [
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'HTTP_500',
      'HTTP_502',
      'HTTP_503',
      'DATABASE_ERROR',
      'INTERNAL_ERROR'
    ];

    return recoverableCodes.includes(error.code);
  }

  /**
   * Check if error requires authentication
   */
  static requiresAuth(error: ApiError): boolean {
    const authCodes = [
      'UNAUTHORIZED',
      'HTTP_401',
      'EMAIL_NOT_VERIFIED',
      'ACCOUNT_BLOCKED'
    ];

    return authCodes.includes(error.code);
  }

  /**
   * Check if error is validation related
   */
  static isValidationError(error: ApiError): boolean {
    const validationCodes = [
      'VALIDATION_ERROR',
      'WEAK_PASSWORD',
      'HTTP_400',
      'HTTP_422'
    ];

    return validationCodes.includes(error.code);
  }
}

/**
 * Enhanced fetch wrapper with error handling
 */
export async function apiRequest<T = any>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw response;
    }

    // For 204 No Content responses
    if (response.status === 204) {
      return null as T;
    }

    return await response.json();
  } catch (error) {
    throw ApiErrorHandler.handleError(error);
  }
}

/**
 * Hook for handling API errors in React components
 */
export function useApiError() {
  const getErrorMessage = (error: any): string => {
    const apiError = ApiErrorHandler.handleError(error);
    return ApiErrorHandler.getUserFriendlyMessage(apiError);
  };

  const isRecoverable = (error: any): boolean => {
    const apiError = ApiErrorHandler.handleError(error);
    return ApiErrorHandler.isRecoverable(apiError);
  };

  const requiresAuth = (error: any): boolean => {
    const apiError = ApiErrorHandler.handleError(error);
    return ApiErrorHandler.requiresAuth(apiError);
  };

  const isValidationError = (error: any): boolean => {
    const apiError = ApiErrorHandler.handleError(error);
    return ApiErrorHandler.isValidationError(apiError);
  };

  return {
    getErrorMessage,
    isRecoverable,
    requiresAuth,
    isValidationError,
    handleError: ApiErrorHandler.handleError
  };
}
