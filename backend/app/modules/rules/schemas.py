"""Rules module schemas"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RuleSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleType(StrEnum):
    ICMS_DIFFERENTIAL = "ICMS_DIFFERENTIAL"
    ICMS_FCP = "ICMS_FCP"
    ICMS_ST = "ICMS_ST"
    FREIGHT_WEIGHT_VALUE = "FREIGHT_WEIGHT_VALUE"
    FREIGHT_CUBAGE = "FREIGHT_CUBAGE"
    REDESPACHO = "REDESPACHO"
    TOLL_PLAZA = "TOLL_PLAZA"
    AD_VALOREM = "AD_VALOREM"
    GRIS = "GRIS"
    SICOBAN_TABLE = "SICOBAN_TABLE"
    COMPLEMENTARY_CTE = "COMPLEMENTARY_CTE"
    PESO_REAL_VS_FATURADO = "PESO_REAL_VS_FATURADO"
    VALOR_MINIMO_FRETE = "VALOR_MINIMO_FRETE"
    OTHER = "OTHER"


class RuleCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, pattern="^[A-Z0-9_]+$")
    name: str = Field(..., min_length=1, max_length=100)
    type: RuleType
    severity: RuleSeverity = RuleSeverity.MEDIUM
    configJson: dict[str, Any] | None = Field(default_factory=dict)
    description: str | None = None


class RuleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    type: RuleType | None = None
    severity: RuleSeverity | None = None
    configJson: dict[str, Any] | None = None
    description: str | None = None
    isActive: bool | None = None


class RuleResponse(BaseModel):
    id: str
    code: str
    name: str
    type: str
    severity: str
    configJson: dict[str, Any]
    version: int
    isActive: bool
    description: str | None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class RuleListResponse(BaseModel):
    items: list[RuleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RuleEngineStatus(BaseModel):
    rulesLoaded: int
    dbRules: int
    builtinFallback: int
    cacheStats: dict[str, Any]
