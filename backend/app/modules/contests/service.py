"""Contests module service"""

import uuid
from datetime import datetime

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.base import BaseService
from app.modules.contests.schemas import (
    CommunicationCreate,
    CommunicationResponse,
    ContestCreate,
    ContestItemCreate,
    ContestItemResponse,
    ContestItemUpdate,
    ContestListResponse,
    ContestResponse,
    ContestUpdate,
    PaymentCreate,
    PaymentResponse,
)
from app.modules.contracts.service import ContractsService
from app.services.pdf_generator import generate_contest_letter
from app.services.storage import upload_file
from prisma import Prisma

logger = structlog.get_logger()

# Constants
PROGRESSIVE_MONTH_DAYS = 30
FEE_PCT_TOLERANCE = 0.01


class ContestsService(BaseService):
    def __init__(self, db: Prisma):
        super().__init__(db, "Contest")
        self.contracts_service = ContractsService(db)

    async def _to_response(self, contest, include_relations: bool = False) -> ContestResponse:
        items = []
        communications = []
        payments = []

        if include_relations:
            items = [
                ContestItemResponse(
                    id=i.id,
                    contest_id=i.contestId,
                    discrepancy_id=i.discrepancyId,
                    expected_value=i.expectedValue,
                    contested_value=i.contestedValue,
                    recovered_value=i.recoveredValue,
                    status=i.status,
                    notes=i.notes,
                    created_at=i.createdAt,
                    updated_at=i.updatedAt,
                )
                for i in getattr(contest, "items", [])
            ]
            communications = [
                CommunicationResponse(
                    id=c.id,
                    contest_id=c.contestId,
                    type=c.type,
                    direction=c.direction,
                    subject=c.subject,
                    content=c.content,
                    attachments=c.attachments,
                    sent_by_id=c.sentById,
                    sent_at=c.sentAt,
                    read_at=c.readAt,
                )
                for c in getattr(contest, "communications", [])
            ]
            payments = [
                PaymentResponse(
                    id=p.id,
                    contest_id=p.contestId,
                    item_id=p.itemId,
                    type=p.type,
                    amount=p.amount,
                    currency=p.currency,
                    status=p.status,
                    reference=p.reference,
                    paid_at=p.paidAt,
                    confirmed_at=p.confirmedAt,
                    created_at=p.createdAt,
                )
                for p in getattr(contest, "payments", [])
            ]

        # Determine pricing model info for response
        pricing_model = "FIXED"
        progressive_month = None
        if contest.contractId:
            contract = await self.db.contract.find_unique(where={"id": contest.contractId})
            if contract:
                pricing_model = contract.pricingModel
                if contract.pricingModel == "PROGRESSIVE":
                    start_date = contract.progressiveStartDate or contract.startDate
                    check_date = datetime.utcnow()
                    days_diff = (check_date - start_date).days
                    progressive_month = 1 if days_diff < PROGRESSIVE_MONTH_DAYS else (days_diff // PROGRESSIVE_MONTH_DAYS) + 1

        return ContestResponse(
            id=contest.id,
            company_id=contest.companyId,
            client_id=contest.clientId,
            carrier_id=contest.carrierId,
            contract_id=contest.contractId,
            number=contest.number,
            status=contest.status,
            total_expected=contest.totalExpected,
            total_recovered=contest.totalRecovered,
            success_fee_pct=contest.successFeePct,
            success_fee_value=contest.successFeeValue,
            net_recovery=contest.netRecovery,
            sent_at=contest.sentAt,
            acknowledged_at=contest.acknowledgedAt,
            responded_at=contest.respondedAt,
            resolved_at=contest.resolvedAt,
            expired_at=contest.expiredAt,
            notes=contest.notes,
            metadata=contest.metadata,
            created_at=contest.createdAt,
            updated_at=contest.updatedAt,
            items=items,
            communications=communications,
            payments=payments,
            pricing_model=pricing_model,
            progressive_month=progressive_month,
        )

    async def recalculate_success_fee(
        self, contest_id: str, company_id: str, reference_date: datetime | None = None
    ) -> ContestResponse:
        """
        Recalculate contest success fee based on progressive pricing model.
        Call this when the contest spans into a new pricing month.
        """

        contest = await self.get_contest_detail(contest_id, company_id)

        if not contest.contract_id:
            return await self._to_response(contest, include_relations=True)

        contract = await self.db.contract.find_unique(where={"id": contest.contractId})
        if not contract:
            return await self._to_response(contest, include_relations=True)

        # Calculate new fee percentage
        new_fee_pct = self.contracts_service.calculate_progressive_fee_pct(contract, reference_date)

        # Only update if changed
        if abs(new_fee_pct - contest.success_fee_pct) > FEE_PCT_TOLERANCE:
            new_fee_value = round(contest.total_recovered * new_fee_pct / 100, 2)
            new_net_recovery = round(contest.total_recovered - new_fee_value, 2)

            contest = await self.db.contest.update(
                where={"id": contest_id},
                data={
                    "successFeePct": new_fee_pct,
                    "successFeeValue": new_fee_value,
                    "netRecovery": new_net_recovery,
                },
                include={"items": True, "communications": True, "payments": True},
            )
            logger.info(
                "contest_success_fee_recalculated", contest_id=contest_id, new_pct=new_fee_pct
            )

        return await self._to_response(contest, include_relations=True)

    def _generate_contest_number(self) -> str:
        """Generate unique contest number: CTST-YYYY-NNNNN"""
        year = datetime.utcnow().year
        # In production, use a sequence or atomic counter
        suffix = str(uuid.uuid4().int)[:5]
        return f"CTST-{year}-{suffix}"

    async def create_contest(
        self, data: ContestCreate, company_id: str, user_id: str
    ) -> ContestResponse:
        """Create new contest from discrepancies"""
        # Validate client, carrier, contract belong to company
        client = await self.db.client.find_first(
            where={"id": data.client_id, "companyId": company_id}
        )
        if not client:
            raise NotFoundError("Client", data.client_id)

        carrier = await self.db.carrier.find_first(
            where={"id": data.carrier_id, "companyId": company_id}
        )
        if not carrier:
            raise NotFoundError("Carrier", data.carrier_id)

        contract = None
        success_fee_pct = 25.0
        if data.contract_id:
            contract = await self.db.contract.find_first(
                where={"id": data.contract_id, "companyId": company_id}
            )
            if not contract:
                raise NotFoundError("Contract", data.contract_id)
            success_fee_pct = contract.successFeePct

        # Validate discrepancies exist and belong to client/carrier
        discrepancy_ids = [item.discrepancy_id for item in data.items]
        discrepancies = await self.db.discrepancy.find_many(
            where={
                "id": {"in": discrepancy_ids},
                "clientId": data.client_id,
                "carrierId": data.carrier_id,
                "status": {"in": ["APPROVED", "DETECTED", "UNDER_REVIEW"]},
            }
        )
        if len(discrepancies) != len(discrepancy_ids):
            raise BadRequestError("Some discrepancies not found or not eligible")

        # Calculate totals
        total_expected = sum(item.contested_value for item in data.items)

        # Calculate success fee using progressive model if applicable
        if contract:
            success_fee_pct = self.contracts_service.calculate_progressive_fee_pct(contract)

        success_fee_value = round(total_expected * success_fee_pct / 100, 2)
        net_recovery = round(total_expected - success_fee_value, 2)

        # Generate contest number
        number = self._generate_contest_number()
        while await self.db.contest.find_first(where={"number": number, "companyId": company_id}):
            number = self._generate_contest_number()

        # Create contest with items in transaction
        async with self.db.tx() as tx:
            contest = await tx.contest.create(
                data={
                    "companyId": company_id,
                    "clientId": data.client_id,
                    "carrierId": data.carrier_id,
                    "contractId": data.contract_id,
                    "number": number,
                    "status": "DRAFT",
                    "totalExpected": total_expected,
                    "totalRecovered": 0,
                    "successFeePct": success_fee_pct,
                    "successFeeValue": success_fee_value,
                    "netRecovery": net_recovery,
                    "notes": data.notes,
                }
            )

            for item in data.items:
                disc = next(d for d in discrepancies if d.id == item.discrepancy_id)
                await tx.contestItem.create(
                    data={
                        "contestId": contest.id,
                        "discrepancyId": item.discrepancy_id,
                        "expectedValue": disc.difference,
                        "contestedValue": item.contested_value,
                        "recoveredValue": 0,
                        "status": "DRAFT",
                    }
                )

                # Update discrepancy status
                await tx.discrepancy.update(
                    where={"id": item.discrepancy_id},
                    data={"status": "CONTESTED"},
                )

        logger.info(
            "contest_created",
            id=contest.id,
            number=number,
            company_id=company_id,
            created_by=user_id,
        )
        return await self.get_by_id(contest.id, company_id)

    async def update_contest(
        self, contest_id: str, data: ContestUpdate, company_id: str
    ) -> ContestResponse:
        """Update contest"""
        await self.get_by_id(contest_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        contest = await self.db.contest.update(
            where={"id": contest_id},
            data=update_data,
            include={"items": True, "communications": True, "payments": True},
        )
        logger.info("contest_updated", id=contest_id, company_id=company_id)
        return await self._to_response(contest, include_relations=True)

    async def list_contests(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        status: str | None = None,
        client_id: str | None = None,
        carrier_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> ContestListResponse:
        """List contests"""
        where: dict = {"companyId": company_id}
        if status:
            where["status"] = status
        if client_id:
            where["clientId"] = client_id
        if carrier_id:
            where["carrierId"] = carrier_id
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to

        items, total = await self.list(company_id, pagination, sort, where)

        return ContestListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def get_contest_detail(self, contest_id: str, company_id: str) -> ContestResponse:
        """Get contest with all relations"""
        contest = await self.db.contest.find_first(
            where={"id": contest_id, "companyId": company_id},
            include={"items": True, "communications": True, "payments": True},
        )
        if not contest:
            raise NotFoundError("Contest", contest_id)
        return await self._to_response(contest, include_relations=True)

    # ============================================
    # WORKFLOW ACTIONS
    # ============================================

    async def generate_letter_pdf(
        self, contest_id: str, company_id: str, template: str = "default"
    ) -> bytes:
        """Generate contest letter PDF"""
        contest = await self.get_contest_detail(contest_id, company_id)

        # Fetch related data for PDF
        client = await self.db.client.find_unique(where={"id": contest.client_id})
        carrier = await self.db.carrier.find_unique(where={"id": contest.carrier_id})
        company = await self.db.company.find_unique(where={"id": company_id})

        pdf_bytes = await generate_contest_letter(
            contest=contest,
            client=client,
            carrier=carrier,
            company=company,
            template=template,
        )

        # Save PDF to storage and create communication record
        object_name = f"contests/{company_id}/{contest_id}/letter_{contest.number}.pdf"
        await upload_file(pdf_bytes, object_name, "application/pdf")

        await self.db.communication.create(
            data={
                "contestId": contest_id,
                "type": "LETTER",
                "direction": "OUTBOUND",
                "subject": f"Carta de Contestação {contest.number}",
                "content": f"Carta de contestação gerada para {carrier.name}",
                "attachments": [object_name],
            }
        )

        logger.info("contest_letter_generated", contest_id=contest_id, template=template)
        return pdf_bytes

    async def send_contest(
        self,
        contest_id: str,
        company_id: str,
        send_via: str = "PORTAL",
        recipient_emails: list[str] | None = None,
    ) -> ContestResponse:
        """Send contest to carrier (changes status to SENT)"""
        contest = await self.get_contest_detail(contest_id, company_id)

        if contest.status != "DRAFT":
            raise BadRequestError("Only DRAFT contests can be sent")

        # Generate PDF if not exists
        await self.generate_letter_pdf(contest_id, company_id)

        # Update status
        contest = await self.db.contest.update(
            where={"id": contest_id},
            data={
                "status": "SENT",
                "sentAt": datetime.utcnow(),
            },
            include={"items": True, "communications": True, "payments": True},
        )

        # Create communication record
        carrier = await self.db.carrier.find_unique(where={"id": contest.carrierId})
        await self.db.communication.create(
            data={
                "contestId": contest_id,
                "type": "EMAIL" if send_via in ["EMAIL", "BOTH"] else "PORTAL",
                "direction": "OUTBOUND",
                "subject": f"Contestação {contest.number} - {carrier.name}",
                "content": f"Contestação enviada via {send_via}",
            }
        )

        logger.info("contest_sent", contest_id=contest_id, send_via=send_via)
        return await self._to_response(contest, include_relations=True)

    async def acknowledge_contest(self, contest_id: str, company_id: str) -> ContestResponse:
        """Mark contest as acknowledged by carrier"""
        contest = await self.db.contest.update(
            where={"id": contest_id, "companyId": company_id},
            data={
                "status": "ACKNOWLEDGED",
                "acknowledgedAt": datetime.utcnow(),
            },
            include={"items": True, "communications": True, "payments": True},
        )
        if not contest:
            raise NotFoundError("Contest", contest_id)
        return await self._to_response(contest, include_relations=True)

    async def respond_contest(
        self, contest_id: str, company_id: str, item_updates: list[dict]
    ) -> ContestResponse:
        """Process carrier response (accepted/partial/rejected per item)"""
        contest = await self.get_contest_detail(contest_id, company_id)

        total_recovered = 0
        for update in item_updates:
            item_id = update.get("item_id")
            status = update.get("status")  # ACCEPTED, PARTIAL, REJECTED
            recovered = update.get("recovered_value", 0)

            await self.db.contestItem.update(
                where={"id": item_id, "contestId": contest_id},
                data={
                    "status": status,
                    "recoveredValue": recovered,
                    "notes": update.get("notes"),
                },
            )
            total_recovered += recovered

        # Calculate success fee using progressive model if applicable
        if contest.contractId:
            contract = await self.db.contract.find_unique(where={"id": contest.contractId})
            if contract:
                success_fee_pct = self.contracts_service.calculate_progressive_fee_pct(contract)
            else:
                success_fee_pct = contest.successFeePct
        else:
            success_fee_pct = contest.successFeePct

        success_fee_value = round(total_recovered * success_fee_pct / 100, 2)
        net_recovery = round(total_recovered - success_fee_value, 2)

        # Determine overall contest status
        item_statuses = [u.get("status") for u in item_updates]
        if all(s == "ACCEPTED" for s in item_statuses):
            overall_status = "ACCEPTED"
        elif any(s == "ACCEPTED" for s in item_statuses) or any(
            s == "PARTIAL" for s in item_statuses
        ):
            overall_status = "PARTIAL"
        else:
            overall_status = "REJECTED"

        contest = await self.db.contest.update(
            where={"id": contest_id},
            data={
                "status": overall_status,
                "totalRecovered": total_recovered,
                "successFeeValue": success_fee_value,
                "netRecovery": net_recovery,
                "respondedAt": datetime.utcnow(),
                "resolvedAt": datetime.utcnow()
                if overall_status in ["ACCEPTED", "REJECTED"]
                else None,
            },
            include={"items": True, "communications": True, "payments": True},
        )

        # Update discrepancies
        for update in item_updates:
            item = await self.db.contestItem.find_unique(where={"id": update["item_id"]})
            if item:
                disc_status = "RECOVERED" if update["status"] == "ACCEPTED" else "LOST"
                await self.db.discrepancy.update(
                    where={"id": item.discrepancyId},
                    data={"status": disc_status, "reviewedAt": datetime.utcnow()},
                )

        logger.info(
            "contest_responded",
            contest_id=contest_id,
            status=overall_status,
            recovered=total_recovered,
        )
        return await self._to_response(contest, include_relations=True)

    async def record_payment(
        self, contest_id: str, company_id: str, data: PaymentCreate
    ) -> PaymentResponse:
        """Record payment received"""
        await self.get_contest_detail(contest_id, company_id)

        payment = await self.db.payment.create(
            data={
                "contestId": contest_id,
                "itemId": data.item_id,
                "type": data.type,
                "amount": data.amount,
                "currency": data.currency,
                "status": "CONFIRMED",
                "reference": data.reference,
                "metadata": data.metadata,
                "paidAt": datetime.utcnow(),
                "confirmedAt": datetime.utcnow(),
            }
        )

        logger.info("payment_recorded", contest_id=contest_id, type=data.type, amount=data.amount)
        return PaymentResponse(
            id=payment.id,
            contest_id=payment.contestId,
            item_id=payment.itemId,
            type=payment.type,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            reference=payment.reference,
            paid_at=payment.paidAt,
            confirmed_at=payment.confirmedAt,
            created_at=payment.createdAt,
        )

    # ============================================
    # ITEM & COMMUNICATION MANAGEMENT
    # ============================================

    async def add_item(
        self, contest_id: str, data: ContestItemCreate, company_id: str
    ) -> ContestItemResponse:
        """Add item to draft contest"""
        contest = await self.get_by_id(contest_id, company_id)
        if contest.status != "DRAFT":
            raise BadRequestError("Can only add items to DRAFT contests")

        item = await self.db.contestItem.create(
            data={
                "contestId": contest_id,
                "discrepancyId": data.discrepancy_id,
                "expectedValue": 0,  # Will be filled from discrepancy
                "contestedValue": data.contested_value,
                "recoveredValue": 0,
                "status": "DRAFT",
            }
        )
        return ContestItemResponse(
            id=item.id,
            contest_id=item.contestId,
            discrepancy_id=item.discrepancyId,
            expected_value=item.expectedValue,
            contested_value=item.contestedValue,
            recovered_value=item.recoveredValue,
            status=item.status,
            notes=item.notes,
            created_at=item.createdAt,
            updated_at=item.updatedAt,
        )

    async def update_item(
        self, contest_id: str, item_id: str, data: ContestItemUpdate, company_id: str
    ) -> ContestItemResponse:
        """Update contest item"""
        await self.get_by_id(contest_id, company_id)
        item = await self.db.contestItem.update(
            where={"id": item_id, "contestId": contest_id},
            data=data.model_dump(exclude_unset=True),
        )
        return ContestItemResponse(
            id=item.id,
            contest_id=item.contestId,
            discrepancy_id=item.discrepancyId,
            expected_value=item.expectedValue,
            contested_value=item.contestedValue,
            recovered_value=item.recoveredValue,
            status=item.status,
            notes=item.notes,
            created_at=item.createdAt,
            updated_at=item.updatedAt,
        )

    async def add_communication(
        self, contest_id: str, data: CommunicationCreate, company_id: str, user_id: str
    ) -> CommunicationResponse:
        """Add communication to contest"""
        await self.get_by_id(contest_id, company_id)
        comm = await self.db.communication.create(
            data={
                "contestId": contest_id,
                "type": data.type,
                "direction": data.direction,
                "subject": data.subject,
                "content": data.content,
                "attachments": data.attachments,
                "sentById": user_id,
            }
        )
        return CommunicationResponse(
            id=comm.id,
            contest_id=comm.contestId,
            type=comm.type,
            direction=comm.direction,
            subject=comm.subject,
            content=comm.content,
            attachments=comm.attachments,
            sent_by_id=comm.sentById,
            sent_at=comm.sentAt,
            read_at=comm.readAt,
        )
