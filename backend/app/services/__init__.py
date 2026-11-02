"""Services package"""
# XML Parser - import module
from app.services import xml_parser

# Rules Engine v2
from app.services.rules_engine_v2 import (
    RulesEngineV2,
    RuleContext,
    DiscrepancyResult,
    DiscrepancyType,
    BaseRule,
    create_engine_v2,
    get_engine_instance,
)

# Critical Rules
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
    MLAnomalyRule,
)

# Other Services - import modules (avoid module-level instantiation)
from app.services import pdf_generator

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
    "get_engine_instance",
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
    "MLAnomalyRule",
    # Other Services
    "pdf_generator",
]