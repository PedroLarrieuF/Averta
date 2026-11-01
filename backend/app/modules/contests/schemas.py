"""Contests module schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ContestItemCreate(BaseModel):
    discrepancy_id: str
    contested_value: float = Field(..., ge=0)


class ContestItemUpdate(BaseModel):
    contested_value: Optional[float] = Field(None, ge=0)
    recovered_value: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(DRAFT|SENT|ACKNOWLEDGED|NEGOTIATING|ACCEPTED|PARTIAL|REJECTED|EXPIRED)$")
    notes: Optional[str] = None


class ContestItemResponse(BaseModel):
    id: str
    contest_id: str
    discrepancy_id: str
    expected_value: float
    contested_value: float
    recovered_value: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationCreate(BaseModel):
    type: str = Field(..., pattern="^(EMAIL|LETTER|PHONE|MEETING|PORTAL)$")
    direction: str = Field(..., pattern="^(OUTBOUND|INBOUND)$")
    subject: Optional[str] = None
    content: str
    attachments: Optional[List[str]] = None


class CommunicationResponse(BaseModel):
    id: str
    contest_id: str
    type: str
    direction: str
    subject: Optional[str]
    content: str
    attachments: Optional[List[str]]
    sent_by_id: Optional[str]
    sent_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    item_id: Optional[str] = None
    type: str = Field(..., pattern="^(RECOVERY|SUCCESS_FEE|NET_PAYOUT)$")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    reference: Optional[str] = None
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    id: str
    contest_id: str
    item_id: Optional[str]
    type: str
    amount: float
    currency: str
    status: str
    reference: Optional[str]
    paid_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ContestCreate(BaseModel):
    client_id: str
    carrier_id: str
    contract_id: Optional[str] = None
    items: List[ContestItemCreate]
    notes: Optional[str] = None


class ContestUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(DRAFT|SENT|ACKNOWLEDGED|NEGOTIATING|ACCEPTED|PARTIAL|REJECTED|EXPIRED)$")
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class ContestResponse(BaseModel):
    id: str
    company_id: str
    client_id: str
    carrier_id: str
    contract_id: Optional[str]
    number: str
    status: str
    total_expected: float
    total_recovered: float
    success_fee_pct: float
    success_fee_value: float
    net_recovery: float
    sent_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    responded_at: Optional[datetime]
    resolved_at: Optional[datetime]
    expired_at: Optional[datetime]
    notes: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime
    items: List[ContestItemResponse] = []
    communications: List[CommunicationResponse] = []
    payments: List[PaymentResponse] = []
    # Progressive pricing info
    pricing_model: str = "FIXED"
    progressive_month: Optional[int] = None  # 1 for first month, 2+ for subsequent

    class Config:
        from_attributes = True


class ContestListResponse(BaseModel):
    items: List[ContestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ContestGeneratePDFRequest(BaseModel):
    contest_id: str
    template: Optional[str] = "default"  # default, formal, summary


class ContestSendRequest(BaseModel):
    contest_id: str
    send_via: str = Field(default="PORTAL", pattern="^(EMAIL|PORTAL|BOTH)$")
    recipient_emails: Optional[List[EmailStr]] = None


class ContestPaymentRequest(BaseModel):
    contest_id: str
    item_id: Optional[str] = None
    type: str = Field(..., pattern="^(RECOVERY|SUCCESS_FEE|NET_PAYOUT)$")
    amount: float = Field(..., gt=0)
    reference: Optional[str] = None