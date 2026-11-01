"""Discrepancy processing tasks"""
from celery import Task
from app.core.celery_app import celery_app
import structlog

logger = structlog.get_logger()


class AsyncTask(Task):
    def __call__(self, *args, **kwargs):
        import asyncio
        return asyncio.run(self.run_async(*args, **kwargs))

    async def run_async(self, *args, **kwargs):
        raise NotImplementedError


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def run_rules(self, document_id: str, parsed_data: dict, company_id: str, client_id: str):
    """Run discrepancy detection rules on processed document"""
    from app.services.rules_engine import run_rules as run_rules_engine

    try:
        results = await run_rules_engine(document_id, parsed_data, company_id, client_id)
        logger.info("discrepancy_detection_complete", document_id=document_id, found=len(results))
        return {"discrepancies_found": len(results)}
    except Exception as e:
        logger.exception("discrepancy_detection_failed", document_id=document_id, error=str(e))
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def reprocess_discrepancies(self, company_id: str, document_ids: list[str] | None = None):
    """Reprocess discrepancies for documents (e.g., after rule update)"""
    from app.core.database import get_prisma
    from app.services.rules_engine import run_rules as run_rules_engine

    db = await get_prisma()

    where = {"companyId": company_id, "status": "PROCESSED"}
    if document_ids:
        where["id"] = {"in": document_ids}

    documents = await db.document.find_many(where=where)

    for doc in documents:
        if doc.parsedData:
            await run_rules_engine(doc.id, doc.parsedData, company_id, doc.clientId or "")

    logger.info("discrepancies_reprocessed", company_id=company_id, count=len(documents))


@celery_app.task(base=AsyncTask, bind=True)
async def auto_approve_low_risk(self, company_id: str):
    """Auto-approve low-risk discrepancies based on client settings"""
    from app.core.database import get_prisma

    db = await get_prisma()

    # Get client settings for auto-approval
    clients = await db.client.find_many(
        where={"companyId": company_id, "isActive": True},
        include={"settings": True},
    )

    for client in clients:
        settings = client.settings or {}
        auto_approve = settings.get("autoApprove", {})
        if not auto_approve.get("enabled"):
            continue

        max_value = auto_approve.get("maxValue", 100)
        allowed_types = auto_approve.get("allowedTypes", [])

        discrepancies = await db.discrepancy.find_many(
            where={
                "clientId": client.id,
                "status": "DETECTED",
                "difference": {"lte": max_value},
                "type": {"in": allowed_types} if allowed_types else undefined,
            }
        )

        for disc in discrepancies:
            await db.discrepancy.update(
                where={"id": disc.id},
                data={"status": "APPROVED", "reviewedAt": "now()"},
            )

        logger.info("auto_approved", client_id=client.id, count=len(discrepancies))


# Helper for undefined in where clause
undefined = object()


@celery_app.task(base=AsyncTask, bind=True)
async def recalculate_progressive_success_fees(self, company_id: str):
    """
    Recalculate success fees for contests with progressive pricing model.
    Runs daily to update contests that moved from month 1 (5%) to month 2+ (10%).
    """
    from app.core.database import get_prisma
    from app.modules.contracts.service import ContractsService
    from datetime import datetime as dt

    db = await get_prisma()
    contracts_service = ContractsService(db)

    # Find contests with progressive pricing contracts that are not resolved
    contests = await db.contest.find_many(
        where={
            "companyId": company_id,
            "status": {"in": ["DRAFT", "SENT", "ACKNOWLEDGED", "NEGOTIATING"]},
            "contract": {
                "pricingModel": "PROGRESSIVE"
            }
        },
        include={"contract": True}
    )

    updated_count = 0
    for contest in contests:
        if not contest.contract:
            continue

        contract = contest.contract
        start_date = contract.progressiveStartDate or contract.startDate
        if not start_date:
            continue

        days_diff = (dt.utcnow() - start_date).days
        current_month = 1 if days_diff < 30 else (days_diff // 30) + 1

        # Determine expected fee percentage
        expected_pct = contract.progressiveMonth1Pct if current_month == 1 else contract.progressiveMonth2Pct

        # Check if fee needs update
        if abs(contest.successFeePct - expected_pct) > 0.01:
            new_fee_value = round(contest.totalRecovered * expected_pct / 100, 2)
            new_net_recovery = round(contest.totalRecovered - new_fee_value, 2)

            await db.contest.update(
                where={"id": contest.id},
                data={
                    "successFeePct": expected_pct,
                    "successFeeValue": new_fee_value,
                    "netRecovery": new_net_recovery,
                }
            )
            updated_count += 1
            logger.info("contest_progressive_fee_updated",
                       contest_id=contest.id,
                       month=current_month,
                       new_pct=expected_pct)

    logger.info("progressive_fees_recalculated", company_id=company_id, updated=updated_count)
    return {"updated": updated_count}