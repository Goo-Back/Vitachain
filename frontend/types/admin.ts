// Admin-related TypeScript interfaces

export enum UserStatus {
  ACTIVE = "active",
  BLOCKED = "blocked", 
  PENDING = "pending"
}

export interface AdminUserView {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  account_status: UserStatus;
  created_at: string;
  updated_at: string;
  last_login?: string;
  devices_count: number;
  listings_count: number;
  reservations_count: number;
  orders_count: number;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  blocked_users: number;
  pending_users: number;
  users_by_role: Record<string, number>;
  registrations_today: number;
  registrations_this_week: number;
  registrations_this_month: number;
}

export interface UserFilters {
  search?: string;
  role?: string;
  status?: UserStatus;
  date_from?: string;
  date_to?: string;
  page: number;
  limit: number;
}

export interface UserStatusUpdateRequest {
  new_status: UserStatus;
  reason: string;
}

export interface UserRoleUpdateRequest {
  new_role: string;
  reason: string;
}

export interface BulkUserUpdateRequest {
  user_ids: string[];
  action: string;
  data: Record<string, any>;
}

export interface BulkUserUpdateResponse {
  message: string;
  updated_count: number;
  failed_count: number;
  results: any[];
}

export interface UserListResponse {
  users: AdminUserView[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  stats: UserStats;
}

export interface AdminAuditLog {
  id: string;
  admin_id: string;
  admin_email: string;
  action: string;
  target_user_id?: string;
  target_user_email?: string;
  details: Record<string, any>;
  ip_address: string;
  timestamp: string;
}

export interface AccountBlockRequest {
  block_reason: string;
  duration_hours: number;
  auto_block: boolean;
  metadata?: Record<string, any>;
}

export interface AccountUnblockRequest {
  unblock_reason: string;
}

export interface BlockResponse {
  block_id: string;
  user_id: string;
  blocked_until: string;
  block_reason: string;
  auto_block: boolean;
}

export interface UnblockResponse {
  user_id: string;
  unblocked_at: string;
  unblock_reason: string;
  previous_block_id: string;
}

export interface BlockedUserView {
  id: string;
  user_id: string;
  block_reason: string;
  block_duration_hours: number;
  blocked_at: string;
  blocked_until: string;
  auto_block: boolean;
  time_remaining_hours: number;
  time_remaining_minutes: number;
  user: AdminUserView;
}

export interface BlockedUsersListResponse {
  blocks: BlockedUserView[];
  total: number;
  limit: number;
  offset: number;
}
