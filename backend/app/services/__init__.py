"""Services package"""

# XML Parser - import module
# Other Services - import modules (avoid module-level instantiation)
from app.services import pdf_generator, xml_parser

# Critical Rules
from app.services.rules_critical import (
    AdValoremRule,
    ComplementaryCTEAnulationRule,
    ComplementaryCTEComplementRule,
    ComplementaryCTESubstitutionRule,
    FCPRule,
    FreightCubageRule,
    FreightWeightValueRule,
    GRISRule,
    ICMSDifferentialRule,
    ICMSSTRule,
    MLAnomalyRule,
    PesoRealVsFaturadoRule,
    RedespachoRule,
    SicobanTableRuleReal,
    TollPlazaRule,
    ValorMinimoFreteRule,
)

# Rules Engine v2
from app.services.rules_engine_v2 import (
    BaseRule,
    DiscrepancyResult,
    DiscrepancyType,
    RuleContext,
    RulesEngineV2,
    create_engine_v2,
    get_engine_instance,
)

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
