"""Notifications module schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    DISCREPANCY_FOUND = "DISCREPANCY_FOUND"
    CONTEST_APPROVED = "CONTEST_APPROVED"
    CONTEST_SENT = "CONTEST_SENT"
    CONTEST_RESPONSE = "CONTEST_RESPONSE"
    RECOVERY_CONFIRMED = "RECOVERY_CONFIRMED"
    WEEKLY_REPORT = "WEEKLY_REPORT"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    CONTRACT_EXPIRING = "CONTRACT_EXPIRING"
    WELCOME = "WELCOME"
    PASSWORD_RESET = "PASSWORD_RESET"


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    IN_APP = "IN_APP"
    SMS = "SMS"


class NotificationCreate(BaseModel):
    client_id: str
    user_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]


class NotificationUpdate(BaseModel):
    read_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    id: str
    client_id: str
    user_id: Optional[str]
    type: str
    title: str
    message: str
    data: Optional[dict]
    read_at: Optional[datetime]
    sent_at: datetime
    channels: List[str]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    total_pages: int


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    sms_enabled: bool = False
    # Per-type preferences
    discrepancy_found: bool = True
    contest_approved: bool = True
    contest_sent: bool = True
    contest_response: bool = True
    recovery_confirmed: bool = True
    weekly_report: bool = True
    system_alert: bool = True
    contract_expiring: bool = True
    welcome: bool = True
    password_reset: bool = True
    # Frequency
    email_frequency: str = Field(default="immediate", pattern="^(immediate|daily|weekly)$")
    digest_time: str = "09:00"  # HH:MM for daily/weekly digest


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response"""
    user_id: str
    preferences: NotificationPreferences
    updated_at: datetime