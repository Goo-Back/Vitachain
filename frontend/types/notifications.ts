// Notification and alert TypeScript interfaces

export enum AlertType {
  SYSTEM = "system",
  TELEMETRY = "telemetry",
  ORDER = "order",
  RESERVATION = "reservation",
  SECURITY = "security"
}

export enum NotificationStatus {
  PENDING = "pending",
  SENT = "sent",
  FAILED = "failed"
}

export interface Alert {
  id: string;
  user_id?: string;
  type: AlertType;
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  is_read: boolean;
  metadata: Record<string, any>;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EmailNotification {
  id: string;
  user_id: string;
  subject: string;
  content: string;
  template_name?: string;
  template_data: Record<string, any>;
  status: NotificationStatus;
  sent_at?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
}

export interface InAppNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  action_url?: string;
  metadata: Record<string, any>;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferences {
  user_id: string;
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  alert_types: {
    system: boolean;
    telemetry: boolean;
    order: boolean;
    reservation: boolean;
    security: boolean;
  };
  updated_at: string;
}

export interface AlertCreateRequest {
  user_id?: string;
  type: AlertType;
  title: string;
  message: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  metadata?: Record<string, any>;
  expires_at?: string;
}

export interface AlertResponse {
  message: string;
  alert: Alert;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  unread_count: number;
  page: number;
  limit: number;
}

export interface NotificationListResponse {
  email_notifications: EmailNotification[];
  in_app_notifications: InAppNotification[];
  total_email: number;
  total_in_app: number;
  unread_count: number;
}

export interface MarkAsReadRequest {
  notification_ids: string[];
  notification_type: 'alerts' | 'in_app' | 'all';
}

export interface NotificationStats {
  total_alerts: number;
  unread_alerts: number;
  total_emails: number;
  pending_emails: number;
  failed_emails: number;
  total_in_app: number;
  unread_in_app: number;
  alerts_by_type: Record<AlertType, number>;
  alerts_by_severity: Record<string, number>;
}
