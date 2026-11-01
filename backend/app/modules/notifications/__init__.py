"""Notifications module"""
from app.modules.notifications.router import router
from app.modules.notifications.service import NotificationsService
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferences,
    NotificationPreferencesResponse,
    NotificationType,
    NotificationChannel,
)

__all__ = [
    "router",
    "NotificationsService",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationPreferences",
    "NotificationPreferencesResponse",
    "NotificationType",
    "NotificationChannel",
]