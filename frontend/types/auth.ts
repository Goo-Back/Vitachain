export enum UserRole {
  FARMER = "FARMER",
  RESTAURANT = "RESTAURANT", 
  CITIZEN = "CITIZEN",
  ADMIN = "ADMIN"
}

export interface UserRegistrationRequest {
  email: string;
  role: UserRole;
  full_name: string;
}

export interface UserRegistrationResponse {
  message: string;
  user_id: string;
  email_sent: boolean;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface RoleInfo {
  value: UserRole;
  label: string;
  description: string;
  icon: string;
  benefits: string[];
}

export interface FormState {
  email: string;
  role: UserRole | "";
  full_name: string;
}

export interface FormErrors {
  email?: string;
  role?: string;
  full_name?: string;
  general?: string;
}

// Role-based permissions mapping
export const ROLE_PERMISSIONS: Record<UserRole, string[]> = {
  [UserRole.FARMER]: [
    'read:own_telemetry',
    'write:own_devices',
    'read:own_alerts',
    'write:own_alerts',
    'read:own_listings',
    'write:own_listings',
    'read:marketplace',
    'write:own_orders',
    'read:own_orders',
    'read:profiles',
    'write:profiles'
  ],
  [UserRole.RESTAURANT]: [
    'read:own_meals',
    'write:own_meals',
    'read:own_reservations',
    'write:own_reservations',
    'read:marketplace',
    'read:profiles',
    'write:profiles'
  ],
  [UserRole.CITIZEN]: [
    'read:marketplace',
    'write:own_reservations',
    'read:own_reservations',
    'read:profiles',
    'write:profiles'
  ],
  [UserRole.ADMIN]: ['*'] // Admin has all permissions
};

// Dashboard routes based on roles
export const ROLE_DASHBOARD_ROUTES: Record<UserRole, string> = {
  [UserRole.FARMER]: '/dashboard/katara',
  [UserRole.RESTAURANT]: '/dashboard/secondserve',
  [UserRole.CITIZEN]: '/dashboard/farmarket',
  [UserRole.ADMIN]: '/dashboard/admin'
};

// Helper function to check if user has permission
export const hasPermission = (userRole: UserRole, permission: string): boolean => {
  const permissions = ROLE_PERMISSIONS[userRole] || [];
  return permissions.includes('*') || permissions.includes(permission);
};

// Helper function to check if user has any of the specified permissions
export const hasAnyPermission = (userRole: UserRole, permissions: string[]): boolean => {
  return permissions.some(permission => hasPermission(userRole, permission));
};

// Helper function to get dashboard route for user role
export const getDashboardRoute = (userRole: UserRole): string => {
  return ROLE_DASHBOARD_ROUTES[userRole] || '/';
};
