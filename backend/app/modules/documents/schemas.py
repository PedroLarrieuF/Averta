"""Documents module schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    CTE = "CTE"
    NFE = "NFE"
    CTE_COMPLEMENTAR = "CTE_COMPLEMENTAR"
    NFE_COMPLEMENTAR = "NFE_COMPLEMENTAR"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class DocumentCreate(BaseModel):
    client_id: str
    carrier_id: Optional[str] = None
    contract_id: Optional[str] = None
    type: DocumentType
    access_key: str
    number: Optional[str] = None
    series: Optional[str] = None
    issue_date: Optional[datetime] = None
    total_value: Optional[float] = None
    freight_value: Optional[float] = None
    weight: Optional[float] = None
    volume: Optional[float] = None
    xml_content: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None


class DocumentUpdate(BaseModel):
    carrier_id: Optional[str] = None
    contract_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    parsed_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    company_id: str
    client_id: str
    carrier_id: Optional[str]
    contract_id: Optional[str]
    type: str
    access_key: str
    number: Optional[str]
    series: Optional[str]
    issue_date: Optional[datetime]
    total_value: Optional[float]
    freight_value: Optional[float]
    weight: Optional[float]
    volume: Optional[float]
    status: str
    parsed_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentImport(BaseModel):
    client_id: str
    carrier_id: Optional[str] = None
    contract_id: Optional[str] = None
    files: List[str]  # Base64 encoded XML files or file paths
    auto_match_contract: bool = True
    auto_run_rules: bool = True


class DocumentImportResponse(BaseModel):
    imported: int
    failed: int
    documents: List[DocumentResponse]
    errors: List[Dict[str, Any]]