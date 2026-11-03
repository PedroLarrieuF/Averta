"""Notifications module"""

from app.modules.notifications.router import router
from app.modules.notifications.schemas import (
    NotificationChannel,
    NotificationCreate,
    NotificationListResponse,
    NotificationPreferences,
    NotificationPreferencesResponse,
    NotificationResponse,
    NotificationType,
    NotificationUpdate,
)
from app.modules.notifications.service import NotificationsService

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
