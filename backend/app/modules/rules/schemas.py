"""Rules module schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RuleSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleType(str, Enum):
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
    configJson: Optional[Dict[str, Any]] = Field(default_factory=dict)
    description: Optional[str] = None


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[RuleType] = None
    severity: Optional[RuleSeverity] = None
    configJson: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None


class RuleResponse(BaseModel):
    id: str
    code: str
    name: str
    type: str
    severity: str
    configJson: Dict[str, Any]
    version: int
    isActive: bool
    description: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class RuleListResponse(BaseModel):
    items: List[RuleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RuleEngineStatus(BaseModel):
    rulesLoaded: int
    dbRules: int
    builtinFallback: int
    cacheStats: Dict[str, Any]