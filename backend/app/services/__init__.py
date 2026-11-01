"""Services package"""
from app.services.xml_parser import xml_parser
from app.services.rules_engine_v2 import (
    RulesEngineV2,
    RuleContext,
    DiscrepancyResult,
    DiscrepancyType,
    BaseRule,
    create_engine_v2,
)
from app.services.rules_critical import (
    ICMSDifferentialRule,
    FCPRule,
    ICMSSTRule,
    FreightWeightValueRule,
    FreightCubageRule,
    PesoRealVsFaturadoRule,
    ValorMinimoFreteRule,
    SicobanTableRuleReal,
    ComplementaryCTEAnulationRule,
    ComplementaryCTESubstitutionRule,
    ComplementaryCTEComplementRule,
    RedespachoRule,
    TollPlazaRule,
    AdValoremRule,
    GRISRule,
)
from app.services.pdf_generator import pdf_generator
from app.services.storage import storage_service
from app.services.email_service import email_service

__all__ = [
    # XML Parser
    "xml_parser",
    # Rules Engine v2
    "RulesEngineV2",
    "RuleContext",
    "DiscrepancyResult",
    "DiscrepancyType",
    "BaseRule",
    "create_engine_v2",
    # Critical Rules
    "ICMSDifferentialRule",
    "FCPRule",
    "ICMSSTRule",
    "FreightWeightValueRule",
    "FreightCubageRule",
    "PesoRealVsFaturadoRule",
    "ValorMinimoFreteRule",
    "SicobanTableRuleReal",
    "ComplementaryCTEAnulationRule",
    "ComplementaryCTESubstitutionRule",
    "ComplementaryCTEComplementRule",
    "RedespachoRule",
    "TollPlazaRule",
    "AdValoremRule",
    "GRISRule",
    # Other Services
    "pdf_generator",
    "storage_service",
    "email_service",
]