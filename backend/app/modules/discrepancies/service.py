"""Discrepancies module service"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from prisma import Prisma
import structlog

from app.modules.base import BaseService
from app.modules.discrepancies.schemas import (
    DiscrepancyCreate,
    DiscrepancyUpdate,
    DiscrepancyResponse,
    DiscrepancyListResponse,
    DiscrepancyStatus,
    DiscrepancySeverity,
    DiscrepancySummary,
)
from app.core.dependencies import PaginationParams
from app.core.exceptions import NotFoundError

logger = structlog.get_logger()


class DiscrepanciesService:
    def __init__(self, db: Prisma):
        self.db = db

    def _to_response(self, discrepancy) -> DiscrepancyResponse:
        return DiscrepancyResponse(
            id=discrepancy.id,
            document_id=discrepancy.documentId,
            company_id=discrepancy.companyId,
            rule_code=discrepancy.ruleCode,
            rule_name=discrepancy.ruleName,
            discrepancy_type=discrepancy.discrepancyType,
            expected_value=discrepancy.expectedValue,
            actual_value=discrepancy.actualValue,
            difference=discrepancy.difference,
            difference_pct=discrepancy.differencePct,
            details=discrepancy.details,
            evidence=discrepancy.evidence,
            status=discrepancy.status,
            severity=discrepancy.severity,
            reviewed_by=discrepancy.reviewedBy,
            reviewed_at=discrepancy.reviewedAt,
            resolution_notes=discrepancy.resolutionNotes,
            contest_id=discrepancy.contestId,
            created_at=discrepancy.createdAt,
            updated_at=discrepancy.updatedAt,
        )

    async def create_discrepancy(self, data: DiscrepancyCreate) -> DiscrepancyResponse:
        """Create new discrepancy"""
        discrepancy = await self.db.discrepancy.create(
            data={
                "documentId": data.document_id,
                "companyId": data.company_id,
                "ruleCode": data.rule_code,
                "ruleName": data.rule_name,
                "discrepancyType": data.discrepancy_type,
                "expectedValue": data.expected_value,
                "actualValue": data.actual_value,
                "difference": data.difference,
                "differencePct": data.difference_pct,
                "details": data.details,
                "evidence": data.evidence,
                "status": DiscrepancyStatus.OPEN.value,
                "severity": data.severity.value,
            }
        )

        logger.info("discrepancy_created", id=discrepancy.id, rule_code=data.rule_code)
        return self._to_response(discrepancy)

    async def get_by_id(self, discrepancy_id: str, company_id: str) -> DiscrepancyResponse:
        """Get discrepancy by ID"""
        discrepancy = await self.db.discrepancy.find_unique(
            where={"id": discrepancy_id, "companyId": company_id}
        )
        if not discrepancy:
            raise NotFoundError("Discrepancy", discrepancy_id)
        return self._to_response(discrepancy)

    async def list_discrepancies(
        self,
        company_id: str,
        pagination: PaginationParams,
        document_id: Optional[str] = None,
        status: Optional[DiscrepancyStatus] = None,
        severity: Optional[DiscrepancySeverity] = None,
        discrepancy_type: Optional[str] = None,
        rule_code: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> DiscrepancyListResponse:
        """List discrepancies with filters"""
        where = {"companyId": company_id}
        if document_id:
            where["documentId"] = document_id
        if status:
            where["status"] = status.value
        if severity:
            where["severity"] = severity.value
        if discrepancy_type:
            where["discrepancyType"] = discrepancy_type
        if rule_code:
            where["ruleCode"] = rule_code
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to

        total = await self.db.discrepancy.count(where=where)
        discrepancies = await self.db.discrepancy.find_many(
            where=where,
            skip=pagination.offset,
            take=pagination.limit,
            order={"createdAt": "desc"},
        )

        return DiscrepancyListResponse(
            items=[self._to_response(d) for d in discrepancies],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def update_discrepancy(self, discrepancy_id: str, company_id: str, data: DiscrepancyUpdate) -> DiscrepancyResponse:
        """Update discrepancy"""
        discrepancy = await self.db.discrepancy.update(
            where={"id": discrepancy_id, "companyId": company_id},
            data=data.model_dump(exclude_unset=True),
        )
        if not discrepancy:
            raise NotFoundError("Discrepancy", discrepancy_id)
        return self._to_response(discrepancy)

    async def bulk_update_status(self, discrepancy_ids: List[str], company_id: str, status: DiscrepancyStatus, user_id: str) -> int:
        """Bulk update discrepancy status"""
        count = await self.db.discrepancy.update_many(
            where={"id": {"in": discrepancy_ids}, "companyId": company_id},
            data={
                "status": status.value,
                "reviewedBy": user_id,
                "reviewedAt": datetime.utcnow(),
            },
        )
        return count

    async def get_summary(self, company_id: str, client_id: Optional[str] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> DiscrepancySummary:
        """Get discrepancy summary for dashboard"""
        where = {"companyId": company_id}
        if client_id:
            where["document"] = {"clientId": client_id}
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to

        # Total count
        total = await self.db.discrepancy.count(where=where)

        # By status
        by_status = {}
        for status in DiscrepancyStatus:
            count = await self.db.discrepancy.count(where={**where, "status": status.value})
            if count > 0:
                by_status[status.value] = count

        # By severity
        by_severity = {}
        for severity in DiscrepancySeverity:
            count = await self.db.discrepancy.count(where={**where, "severity": severity.value})
            if count > 0:
                by_severity[severity.value] = count

        # By type
        type_counts = await self.db.discrepancy.group_by(
            by=["discrepancyType"],
            where=where,
            _count={"id": True},
        )
        by_type = {item["discrepancyType"]: item["_count"]["id"] for item in type_counts}

        # Total recoverable (OPEN + IN_REVIEW discrepancies)
        recoverable = await self.db.discrepancy.aggregate(
            where={**where, "status": {"in": [DiscrepancyStatus.OPEN.value, DiscrepancyStatus.IN_REVIEW.value]}},
            _sum={"difference": True},
        )
        total_recoverable = recoverable._sum.difference or 0

        return DiscrepancySummary(
            total=total,
            by_status=by_status,
            by_severity=by_severity,
            by_type=by_type,
            total_recoverable=total_recoverable,
        )