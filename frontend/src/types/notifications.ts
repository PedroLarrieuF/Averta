import type { NotificationType, NotificationChannel } from './enums';
import type { PaginatedResponse } from './common';

// Re-export enums for convenience
export type { NotificationType, NotificationChannel } from './enums';

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
}

export type NotificationListResponse = PaginatedResponse<Notification>;

export interface NotificationFilters {
  read?: boolean;
  type?: NotificationType[];
  channel?: NotificationChannel[];
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  in_app_enabled: boolean;
  weekly_report: boolean;
  discrepancy_alerts: boolean;
  contest_updates: boolean;
  push_enabled?: boolean;
  sms_enabled?: boolean;
}

export interface NotificationPreferencesUpdateRequest {
  email_enabled?: boolean;
  in_app_enabled?: boolean;
  weekly_report?: boolean;
  discrepancy_alerts?: boolean;
  contest_updates?: boolean;
  push_enabled?: boolean;
  sms_enabled?: boolean;
}

export interface NotificationMarkReadRequest {
  notificationIds: string[];
}

export interface NotificationMarkAllReadRequest {
  // No body needed
}

export interface UnreadNotificationCountResponse {
  count: number;
}