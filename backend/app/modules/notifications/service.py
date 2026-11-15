"""Notifications module service"""

from datetime import datetime, timedelta
from typing import Any

import structlog

from app.core.dependencies import PaginationParams
from app.core.exceptions import NotFoundError
from app.modules.notifications.schemas import (
    NotificationChannel,
    NotificationCreate,
    NotificationListResponse,
    NotificationPreferences,
    NotificationPreferencesResponse,
    NotificationResponse,
    NotificationType,
)
from app.services.email_service import email_service
from generated.prisma import Prisma
from generated.prisma.models import Notification as NotificationModel

logger = structlog.get_logger()


class NotificationsService:
    def __init__(self, db: Prisma):
        self.db = db

    def _to_response(self, notification: NotificationModel) -> NotificationResponse:
        return NotificationResponse(
            id=notification.id,
            client_id=notification.clientId,
            user_id=notification.userId,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            read_at=notification.readAt,
            sent_at=notification.sentAt,
            channels=notification.channels,
        )

    async def create_notification(self, data: NotificationCreate) -> NotificationResponse:
        """Create new notification"""
        notification = await self.db.notification.create(
            data={
                "clientId": data.client_id,
                "userId": data.user_id,
                "type": data.type.value,
                "title": data.title,
                "message": data.message,
                "data": data.data,
                "channels": [c.value for c in data.channels],
            }
        )

        # Send email/push if channels include them
        await self._send_notification(notification)

        logger.info("notification_created", id=notification.id, type=notification.type)
        return self._to_response(notification)

    async def _send_notification(self, notification: NotificationModel) -> None:
        """Send notification via configured channels"""
        channels = notification.channels or []

        if NotificationChannel.EMAIL.value in channels:
            await self._send_email_notification(notification)

        if NotificationChannel.PUSH.value in channels:
            await self._send_push_notification(notification)

    async def _send_email_notification(self, notification: NotificationModel) -> None:
        """Send email via SendGrid"""
        try:
            # Get user email
            user = await self.db.user.find_unique(where={"id": notification.userId})
            if not user or not user.email:
                logger.warning("user_email_not_found", user_id=notification.userId)
                return

            template_map = {
                NotificationType.DISCREPANCY_FOUND.value: "discrepancy_alert",
                NotificationType.CONTEST_APPROVED.value: "contest_created",
                NotificationType.CONTEST_SENT.value: "contest_created",
                NotificationType.RECOVERY_CONFIRMED.value: "payment_received",
                NotificationType.WEEKLY_REPORT.value: "weekly_report",
                NotificationType.CONTRACT_EXPIRING.value: "contract_expiring",
                NotificationType.WELCOME.value: "welcome",
                NotificationType.PASSWORD_RESET.value: "password_reset",
            }

            template_name = template_map.get(notification.type)
            if not template_name:
                logger.warning("no_email_template_for_type", type=notification.type)
                return

            # Build context from notification data
            context = {
                "client_name": user.name or user.email,
                "to_name": user.name or user.email,
                "dashboard_url": f"{user.company.domain if user.company else ''}/dashboard",
                "logo_url": "https://averta.com.br/logo.png",
                "unsubscribe_url": f"{user.company.domain if user.company else ''}/unsubscribe",
                **notification.data,
            }

            await email_service.send_email(
                to_email=user.email,
                to_name=user.name or user.email,
                subject=notification.title,
                template_name=template_name,
                context=context,
            )

            # Update notification with sent timestamp
            await self.db.notification.update(
                where={"id": notification.id},
                data={"sentAt": datetime.utcnow()},
            )

        except Exception as e:
            logger.exception("email_send_failed", notification_id=notification.id, error=str(e))

    async def _send_push_notification(self, notification: NotificationModel) -> None:
        """Send push notification (Firebase, OneSignal, etc.)"""
        # TODO: Implement push notification service
        pass

    async def get_notifications(
        self,
        client_id: str,
        pagination: PaginationParams,
        user_id: str | None = None,
        unread_only: bool = False,
        type: NotificationType | None = None,
    ) -> NotificationListResponse:
        """Get notifications for client/user"""
        where: dict[str, Any] = {"clientId": client_id}
        if user_id:
            where["userId"] = user_id
        if unread_only:
            where["readAt"] = None
        if type:
            where["type"] = type.value

        total = await self.db.notification.count(where=where)
        unread_count = await self.db.notification.count(where={**where, "readAt": None})

        notifications = await self.db.notification.find_many(
            where=where,
            skip=pagination.offset,
            take=pagination.limit,
            order={"sentAt": "desc"},
        )

        return NotificationListResponse(
            items=[self._to_response(n) for n in notifications],
            total=total,
            unread_count=unread_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def mark_as_read(self, notification_id: str, client_id: str) -> NotificationResponse:
        """Mark notification as read"""
        notification = await self.db.notification.update(
            where={"id": notification_id, "clientId": client_id},
            data={"readAt": datetime.utcnow()},
        )
        if not notification:
            raise NotFoundError("Notification", notification_id)
        return self._to_response(notification)

    async def mark_all_as_read(self, client_id: str, user_id: str | None = None) -> int:
        """Mark all notifications as read"""
        where: dict[str, Any] = {"clientId": client_id, "readAt": None}
        if user_id:
            where["userId"] = user_id

        count = await self.db.notification.count(where=where)
        await self.db.notification.update_many(
            where=where,
            data={"readAt": datetime.utcnow()},
        )
        return count  # type: ignore[no-any-return]

    async def delete_notification(self, notification_id: str, client_id: str) -> None:
        """Delete notification"""
        await self.db.notification.delete(where={"id": notification_id, "clientId": client_id})

    # ============================================
    # PREFERENCES
    # ============================================

    async def get_preferences(self, user_id: str) -> NotificationPreferencesResponse:
        """Get user notification preferences"""
        user = await self.db.user.find_unique(
            where={"id": user_id},
            include={"client": True},
        )
        if not user:
            raise NotFoundError("User", user_id)

        settings = user.client.settings if user.client else user.settings or {}
        prefs = settings.get("notification_preferences", {})

        return NotificationPreferencesResponse(
            user_id=user_id,
            preferences=NotificationPreferences(**prefs) if prefs else NotificationPreferences(),
            updated_at=user.updatedAt,
        )

    async def update_preferences(
        self, user_id: str, prefs: NotificationPreferences
    ) -> NotificationPreferencesResponse:
        """Update user notification preferences"""
        user = await self.db.user.find_unique(where={"id": user_id})
        if not user:
            raise NotFoundError("User", user_id)

        settings = user.settings or {}
        settings["notification_preferences"] = prefs.model_dump()

        await self.db.user.update(
            where={"id": user_id},
            data={"settings": settings},
        )

        return NotificationPreferencesResponse(
            user_id=user_id,
            preferences=prefs,
            updated_at=datetime.utcnow(),
        )

    # ============================================
    # HELPER METHODS FOR OTHER MODULES
    # ============================================

    async def notify_discrepancy_found(
        self, client_id: str, discrepancy_id: str, discrepancy_type: str, value: float
    ) -> None:
        """Notify about new discrepancy"""
        client = await self.db.client.find_unique(where={"id": client_id})
        if not client:
            return

        users = await self.db.user.find_many(
            where={
                "OR": [
                    {"clientId": client_id},
                    {
                        "companyId": client.companyId,
                        "role": {"in": ["ADMIN", "AUDITOR", "MANAGER"]},
                    },
                ],
                "status": "ACTIVE",
            }
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.DISCREPANCY_FOUND,
                    title="Nova DivergÃªncia Detectada",
                    message=f"DivergÃªncia de {discrepancy_type} no valor de R$ {value:,.2f} foi detectada.",
                    data={
                        "discrepancy_id": discrepancy_id,
                        "type": discrepancy_type,
                        "value": value,
                    },
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                )
            )

    async def notify_contest_approved(
        self, client_id: str, contest_id: str, contest_number: str, value: float
    ) -> None:
        """Notify contest approved"""
        users = await self.db.user.find_many(
            where={"clientId": client_id, "status": "ACTIVE"},
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.CONTEST_APPROVED,
                    title="ContestaÃ§Ã£o Aprovada",
                    message=f"ContestaÃ§Ã£o {contest_number} foi aprovada. Valor: R$ {value:,.2f}",
                    data={"contest_id": contest_id, "number": contest_number, "value": value},
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                )
            )

    async def notify_contest_sent(
        self, client_id: str, contest_id: str, contest_number: str, carrier: str
    ) -> None:
        """Notify contest sent to carrier"""
        users = await self.db.user.find_many(
            where={"clientId": client_id, "status": "ACTIVE"},
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.CONTEST_SENT,
                    title="ContestaÃ§Ã£o Enviada",
                    message=f"ContestaÃ§Ã£o {contest_number} enviada para {carrier}.",
                    data={"contest_id": contest_id, "number": contest_number, "carrier": carrier},
                    channels=[NotificationChannel.IN_APP],
                )
            )

    async def notify_recovery_confirmed(
        self, client_id: str, contest_id: str, contest_number: str, recovered: float
    ) -> None:
        """Notify recovery confirmed"""
        users = await self.db.user.find_many(
            where={"clientId": client_id, "status": "ACTIVE"},
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.RECOVERY_CONFIRMED,
                    title="RecuperaÃ§Ã£o Confirmada",
                    message=f"ContestaÃ§Ã£o {contest_number}: R$ {recovered:,.2f} recuperados.",
                    data={
                        "contest_id": contest_id,
                        "number": contest_number,
                        "recovered": recovered,
                    },
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                )
            )

    async def notify_contract_expiring(
        self, client_id: str, contract_id: str, contract_number: str, carrier: str, days: int
    ) -> None:
        """Notify contract expiring"""
        users = await self.db.user.find_many(
            where={
                "OR": [
                    {"clientId": client_id},
                    {
                        "companyId": (
                            await self.db.client.find_unique(where={"id": client_id})
                        ).companyId,
                        "role": {"in": ["ADMIN", "MANAGER"]},
                    },
                ],
                "status": "ACTIVE",
            }
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.CONTRACT_EXPIRING,
                    title="Contrato PrÃ³ximo ao Vencimento",
                    message=f"Contrato {contract_number} com {carrier} vence em {days} dias.",
                    data={
                        "contract_id": contract_id,
                        "number": contract_number,
                        "carrier": carrier,
                        "days": days,
                    },
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                )
            )

    async def send_weekly_report(self, client_id: str) -> None:
        """Send weekly summary report"""
        week_ago = datetime.utcnow() - timedelta(days=7)

        discrepancies = await self.db.discrepancy.find_many(
            where={"clientId": client_id, "createdAt": {"gte": week_ago}},
        )
        contests = await self.db.contest.find_many(
            where={"clientId": client_id, "createdAt": {"gte": week_ago}},
        )

        users = await self.db.user.find_many(
            where={"clientId": client_id, "status": "ACTIVE"},
        )

        for user in users:
            await self.create_notification(
                NotificationCreate(
                    client_id=client_id,
                    user_id=user.id,
                    type=NotificationType.WEEKLY_REPORT,
                    title="RelatÃ³rio Semanal",
                    message=(
                        f"Resumo da semana: {len(discrepancies)} divergÃªncias, "
                        f"{len(contests)} contestaÃ§Ãµes, "
                        f"R$ {sum(c.totalRecovered for c in contests):,.2f} recuperados."
                    ),
                    data={
                        "discrepancies": len(discrepancies),
                        "contests": len(contests),
                        "recovered": sum(c.totalRecovered for c in contests),
                    },
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                )
            )
