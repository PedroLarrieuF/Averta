"""Contests module router"""
from fastapi import APIRouter, Depends, status, Query
from typing import List
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAdmin,
    RequireAuditor,
    CompanyIdDep,
    PaginationDep,
    SortDep,
)
from app.core.rate_limit import contests_limiter
from app.modules.contests.schemas import (
    ContestCreate,
    ContestUpdate,
    ContestResponse,
    ContestListResponse,
    ContestItemCreate,
    ContestItemUpdate,
    ContestItemResponse,
    CommunicationCreate,
    CommunicationResponse,
    PaymentCreate,
    PaymentResponse,
    ContestGeneratePDFRequest,
    ContestSendRequest,
    ContestPaymentRequest,
)
from app.modules.contests.service import ContestsService

router = APIRouter(prefix="/contests", tags=["Contests"])


def get_contests_service(db: Prisma = Depends(get_database)) -> ContestsService:
    return ContestsService(db)


# ============================================
# CONTEST CRUD
# ============================================

@router.post(
    "",
    response_model=ContestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new contest",
)
@contests_limiter
async def create_contest(
    data: ContestCreate,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Create a new contest from approved discrepancies"""
    return await contests_service.create_contest(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=ContestListResponse,
    status_code=status.HTTP_200_OK,
    summary="List contests",
)
@contests_limiter
async def list_contests(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    status: str | None = Query(None, pattern="^(DRAFT|SENT|ACKNOWLEDGED|NEGOTIATING|ACCEPTED|PARTIAL|REJECTED|EXPIRED)$"),
    client_id: str | None = Query(None),
    carrier_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    contests_service: ContestsService = Depends(get_contests_service),
):
    """List contests with pagination and filters"""
    from datetime import datetime
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    return await contests_service.list_contests(company_id, pagination, sort, status, client_id, carrier_id, df, dt)


@router.get(
    "/{contest_id}",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contest by ID with relations",
)
@contests_limiter
async def get_contest(
    contest_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Get contest details with items, communications, payments"""
    return await contests_service.get_contest_detail(contest_id, company_id)


@router.patch(
    "/{contest_id}",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Update contest",
)
async def update_contest(
    contest_id: str,
    data: ContestUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Update contest (admin only)"""
    return await contests_service.update_contest(contest_id, data, company_id)


# ============================================
# WORKFLOW ACTIONS
# ============================================

@router.post(
    "/{contest_id}/generate-pdf",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Generate contest letter PDF",
)
@contests_limiter
async def generate_pdf(
    contest_id: str,
    data: ContestGeneratePDFRequest,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Generate contest letter PDF"""
    pdf_bytes = await contests_service.generate_letter_pdf(contest_id, company_id, data.template)
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="contestacao_{contest_id}.pdf"'},
    )


@router.post(
    "/{contest_id}/send",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Send contest to carrier",
)
@contests_limiter
async def send_contest(
    contest_id: str,
    data: ContestSendRequest,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Send contest (changes status to SENT)"""
    return await contests_service.send_contest(contest_id, company_id, data.send_via, data.recipient_emails)


@router.post(
    "/{contest_id}/acknowledge",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark contest as acknowledged",
)
async def acknowledge_contest(
    contest_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Mark contest as acknowledged by carrier"""
    return await contests_service.acknowledge_contest(contest_id, company_id)


@router.post(
    "/{contest_id}/respond",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Process carrier response",
)
async def respond_contest(
    contest_id: str,
    item_updates: List[dict],
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Process carrier response (accepted/partial/rejected per item)"""
    return await contests_service.respond_contest(contest_id, company_id, item_updates)


@router.post(
    "/{contest_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record payment",
)
async def record_payment(
    contest_id: str,
    data: ContestPaymentRequest,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Record payment received (recovery, success fee, net payout)"""
    payment_data = PaymentCreate(
        item_id=data.item_id,
        type=data.type,
        amount=data.amount,
        reference=data.reference,
    )
    return await contests_service.record_payment(contest_id, company_id, payment_data)


# ============================================
# ITEM MANAGEMENT
# ============================================

@router.post(
    "/{contest_id}/items",
    response_model=ContestItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to contest",
)
async def add_item(
    contest_id: str,
    data: ContestItemCreate,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Add item to draft contest"""
    return await contests_service.add_item(contest_id, data, company_id)


@router.patch(
    "/{contest_id}/items/{item_id}",
    response_model=ContestItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update contest item",
)
async def update_item(
    contest_id: str,
    item_id: str,
    data: ContestItemUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Update contest item (admin only)"""
    return await contests_service.update_item(contest_id, item_id, data, company_id)


# ============================================
# COMMUNICATIONS
# ============================================

@router.post(
    "/{contest_id}/communications",
    response_model=CommunicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add communication",
)
async def add_communication(
    contest_id: str,
    data: CommunicationCreate,
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Add communication (email, letter, call, meeting)"""
    return await contests_service.add_communication(contest_id, data, company_id, current_user.sub)


@router.get(
    "/{contest_id}/communications",
    response_model=List[CommunicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List communications",
)
async def list_communications(
    contest_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """List all communications for contest"""
    contest = await contests_service.get_contest_detail(contest_id, company_id)
    return contest.communications


@router.post(
    "/{contest_id}/recalculate-fee",
    response_model=ContestResponse,
    status_code=status.HTTP_200_OK,
    summary="Recalculate progressive success fee",
)
async def recalculate_fee(
    contest_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contests_service: ContestsService = Depends(get_contests_service),
):
    """Recalculate success fee based on progressive pricing model (month 1: 5%, month 2+: 10%)"""
    return await contests_service.recalculate_success_fee(contest_id, company_id)