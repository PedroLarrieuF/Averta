"""Documents module schemas"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class DocumentType(StrEnum):
    CTE = "CTE"
    NFE = "NFE"
    CTE_COMPLEMENTAR = "CTE_COMPLEMENTAR"
    NFE_COMPLEMENTAR = "NFE_COMPLEMENTAR"
    OTHER = "OTHER"


class DocumentStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class DocumentCreate(BaseModel):
    client_id: str
    carrier_id: str | None = None
    contract_id: str | None = None
    type: DocumentType
    access_key: str
    number: str | None = None
    series: str | None = None
    issue_date: datetime | None = None
    total_value: float | None = None
    freight_value: float | None = None
    weight: float | None = None
    volume: float | None = None
    xml_content: str | None = None
    parsed_data: dict[str, Any] | None = None
    file_path: str | None = None
    file_size: int | None = None


class DocumentUpdate(BaseModel):
    carrier_id: str | None = None
    contract_id: str | None = None
    status: DocumentStatus | None = None
    parsed_data: dict[str, Any] | None = None
    error_message: str | None = None


class DocumentResponse(BaseModel):
    id: str
    company_id: str
    client_id: str
    carrier_id: str | None
    contract_id: str | None
    type: str
    access_key: str
    number: str | None
    series: str | None
    issue_date: datetime | None
    total_value: float | None
    freight_value: float | None
    weight: float | None
    volume: float | None
    status: str
    parsed_data: dict[str, Any] | None
    error_message: str | None
    file_path: str | None
    file_size: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentImport(BaseModel):
    client_id: str
    carrier_id: str | None = None
    contract_id: str | None = None
    files: list[str]  # Base64 encoded XML files or file paths
    auto_match_contract: bool = True
    auto_run_rules: bool = True


class DocumentImportResponse(BaseModel):
    imported: int
    failed: int
    documents: list[DocumentResponse]
    errors: list[dict[str, Any]]
