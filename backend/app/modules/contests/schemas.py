"""Contests module schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class ContestItemCreate(BaseModel):
    discrepancy_id: str
    contested_value: float = Field(..., ge=0)


class ContestItemUpdate(BaseModel):
    contested_value: float | None = Field(None, ge=0)
    recovered_value: float | None = Field(None, ge=0)
    status: str | None = Field(
        None, pattern="^(DRAFT|SENT|ACKNOWLEDGED|NEGOTIATING|ACCEPTED|PARTIAL|REJECTED|EXPIRED)$"
    )
    notes: str | None = None


class ContestItemResponse(BaseModel):
    id: str
    contest_id: str
    discrepancy_id: str
    expected_value: float
    contested_value: float
    recovered_value: float
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationCreate(BaseModel):
    type: str = Field(..., pattern="^(EMAIL|LETTER|PHONE|MEETING|PORTAL)$")
    direction: str = Field(..., pattern="^(OUTBOUND|INBOUND)$")
    subject: str | None = None
    content: str
    attachments: list[str] | None = None


class CommunicationResponse(BaseModel):
    id: str
    contest_id: str
    type: str
    direction: str
    subject: str | None
    content: str
    attachments: list[str] | None
    sent_by_id: str | None
    sent_at: datetime
    read_at: datetime | None

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    item_id: str | None = None
    type: str = Field(..., pattern="^(RECOVERY|SUCCESS_FEE|NET_PAYOUT)$")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    reference: str | None = None
    metadata: dict[str, Any] | None = None


class PaymentResponse(BaseModel):
    id: str
    contest_id: str
    item_id: str | None
    type: str
    amount: float
    currency: str
    status: str
    reference: str | None
    paid_at: datetime | None
    confirmed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ContestCreate(BaseModel):
    client_id: str
    carrier_id: str
    contract_id: str | None = None
    items: list[ContestItemCreate]
    notes: str | None = None


class ContestUpdate(BaseModel):
    status: str | None = Field(
        None, pattern="^(DRAFT|SENT|ACKNOWLEDGED|NEGOTIATING|ACCEPTED|PARTIAL|REJECTED|EXPIRED)$"
    )
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class ContestResponse(BaseModel):
    id: str
    company_id: str
    client_id: str
    carrier_id: str
    contract_id: str | None
    number: str
    status: str
    total_expected: float
    total_recovered: float
    success_fee_pct: float
    success_fee_value: float
    net_recovery: float
    sent_at: datetime | None
    acknowledged_at: datetime | None
    responded_at: datetime | None
    resolved_at: datetime | None
    expired_at: datetime | None
    notes: str | None
    metadata: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    items: list[ContestItemResponse] = []
    communications: list[CommunicationResponse] = []
    payments: list[PaymentResponse] = []
    # Progressive pricing info
    pricing_model: str = "FIXED"
    progressive_month: int | None = None  # 1 for first month, 2+ for subsequent

    class Config:
        from_attributes = True


class ContestListResponse(BaseModel):
    items: list[ContestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ContestGeneratePDFRequest(BaseModel):
    contest_id: str
    template: str | None = "default"  # default, formal, summary


class ContestSendRequest(BaseModel):
    contest_id: str
    send_via: str = Field(default="PORTAL", pattern="^(EMAIL|PORTAL|BOTH)$")
    recipient_emails: list[EmailStr] | None = None


class ContestPaymentRequest(BaseModel):
    contest_id: str
    item_id: str | None = None
    type: str = Field(..., pattern="^(RECOVERY|SUCCESS_FEE|NET_PAYOUT)$")
    amount: float = Field(..., gt=0)
    reference: str | None = None
