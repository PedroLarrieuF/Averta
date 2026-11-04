"""Celery configuration for async tasks"""

import structlog
from celery import Celery

from app.core.config import settings

logger = structlog.get_logger()

celery_app = Celery(
    "averta",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.documents",
        "app.tasks.discrepancies",
        "app.tasks.contests",
        "app.tasks.reports",
        "app.tasks.notifications",
    ],
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 min max
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=100,
    result_expires=3600,
    # Routing
    task_routes={
        "app.tasks.documents.*": {"queue": "documents"},
        "app.tasks.discrepancies.*": {"queue": "rules"},
        "app.tasks.contests.*": {"queue": "contests"},
        "app.tasks.reports.*": {"queue": "reports"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    },
    # Beat schedule (periodic tasks)
    beat_schedule={
        "check-stale-documents": {
            "task": "app.tasks.documents.check_stale_documents",
            "schedule": 300.0,  # every 5 minutes
        },
        "generate-daily-reports": {
            "task": "app.tasks.reports.generate_daily_reports",
            "schedule": 86400.0,  # daily
        },
        "send-weekly-summary": {
            "task": "app.tasks.notifications.send_weekly_summary",
            "schedule": 604800.0,  # weekly
        },
        "recalculate-progressive-fees": {
            "task": "app.tasks.discrepancies.recalculate_progressive_success_fees",
            "schedule": 86400.0,  # daily at midnight
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()


@celery_app.task(bind=True, ignore_result=True)  # type: ignore[untyped-decorator]
def debug_task(self: "Celery") -> None:
    logger.debug("celery_debug_task", request=repr(self.request))
