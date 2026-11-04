"""Notifications module router"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    ClientIdDep,
    CompanyIdDep,
    CurrentUserDep,
    PaginationDep,
    RequireAdmin,
    RequireManager,
    get_database,
)
from app.core.exceptions import ForbiddenError
from app.modules.clients.service import ClientsService
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationListResponse,
    NotificationPreferences,
    NotificationPreferencesResponse,
    NotificationResponse,
    NotificationType,
)
from app.modules.notifications.service import NotificationsService
from prisma import Prisma

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notifications_service(db: Prisma = Depends(get_database)) -> NotificationsService:
    return NotificationsService(db)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification",
)
async def create_notification(
    data: NotificationCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Create a new notification (admin/manager)"""
    # Verify client belongs to company
    clients_service = ClientsService(current_user.db)
    await clients_service.get_by_id(data.client_id, company_id)

    return await notifications_service.create_notification(data)


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notifications",
)
async def list_notifications(  # noqa: PLR0913, PLR0917
    current_user: CurrentUserDep,
    client_id: ClientIdDep,
    pagination: PaginationDep,
    unread_only: bool = Query(False),
    type: NotificationType | None = Query(None),
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """List notifications for current user/client"""
    # If user is CLIENT role, use their client_id; otherwise use provided client_id
    effective_client_id = current_user.client_id or client_id
    if not effective_client_id:
        raise ForbiddenError("Client access required")

    return await notifications_service.get_notifications(
        effective_client_id, pagination, current_user.sub, unread_only, type
    )


@router.get(
    "/unread-count",
    status_code=status.HTTP_200_OK,
    summary="Get unread count",
)
async def get_unread_count(
    current_user: CurrentUserDep,
    client_id: ClientIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Get unread notification count"""
    effective_client_id = current_user.client_id or client_id
    if not effective_client_id:
        return {"unread_count": 0}

    notifications = await notifications_service.get_notifications(
        effective_client_id, PaginationDep(page=1, page_size=1), current_user.sub, unread_only=True
    )
    return {"unread_count": notifications.unread_count}


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
)
async def mark_as_read(
    notification_id: str,
    current_user: CurrentUserDep,
    client_id: ClientIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Mark notification as read"""
    effective_client_id = current_user.client_id or client_id
    if not effective_client_id:
        raise ForbiddenError("Client access required")
    return await notifications_service.mark_as_read(notification_id, effective_client_id)


@router.post(
    "/read-all",
    status_code=status.HTTP_200_OK,
    summary="Mark all as read",
)
async def mark_all_as_read(
    current_user: CurrentUserDep,
    client_id: ClientIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Mark all notifications as read"""
    effective_client_id = current_user.client_id or client_id
    if not effective_client_id:
        raise ForbiddenError("Client access required")

    count = await notifications_service.mark_all_as_read(effective_client_id, current_user.sub)
    return {"marked_count": count}


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
)
async def delete_notification(
    notification_id: str,
    current_user: CurrentUserDep,
    client_id: ClientIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Delete notification"""
    effective_client_id = current_user.client_id or client_id
    if not effective_client_id:
        raise ForbiddenError("Client access required")
    await notifications_service.delete_notification(notification_id, effective_client_id)


# ============================================
# PREFERENCES
# ============================================


@router.get(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notification preferences",
)
async def get_preferences(
    current_user: CurrentUserDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Get current user's notification preferences"""
    return await notifications_service.get_preferences(current_user.sub)


@router.put(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="Update notification preferences",
)
async def update_preferences(
    prefs: NotificationPreferences,
    current_user: CurrentUserDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Update current user's notification preferences"""
    return await notifications_service.update_preferences(current_user.sub, prefs)


# ============================================
# ADMIN HELPERS (for other modules to call)
# ============================================


@router.post(
    "/system/weekly-reports",
    status_code=status.HTTP_200_OK,
    summary="Send weekly reports (cron job)",
)
async def send_weekly_reports(
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    notifications_service: NotificationsService = Depends(get_notifications_service),
):
    """Send weekly reports to all active clients (called by cron)"""
    clients_service = ClientsService(current_user.db)

    clients = await clients_service.db.client.find_many(
        where={"companyId": company_id, "isActive": True},
    )

    for client in clients:
        await notifications_service.send_weekly_report(client.id)

    return {"sent_to": len(clients)}
