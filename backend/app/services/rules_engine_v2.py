"""Rules Engine v2 - DB-backed, cached, filterable"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from enum import Enum
import structlog
import json

from app.core.database import get_prisma
from app.core.config import settings

logger = structlog.get_logger()


class DiscrepancyType(str, Enum):
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


@dataclass
class RuleContext:
    """Context passed to all rules during evaluation"""
    document: dict
    contract: Optional[dict] = None
    freight_table: Optional[dict] = None
    carrier: Optional[dict] = None
    client_settings: Optional[dict] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DiscrepancyResult:
    """Result of a rule evaluation"""
    rule_code: str
    rule_name: str
    discrepancy_type: DiscrepancyType
    triggered: bool
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    difference: Optional[float] = None
    difference_pct: Optional[float] = None
    details: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)
    severity: str = "MEDIUM"


class BaseRule(ABC):
    """Base class for all audit rules"""

    rule_code: str = ""
    rule_name: str = ""
    discrepancy_type: DiscrepancyType = DiscrepancyType.OTHER
    severity: str = "MEDIUM"
    requires_contract: bool = False
    requires_freight_table: bool = False
    relevance_tags: List[str] = field(default_factory=list)  # para filtro

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    @abstractmethod
    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        pass

    def _create_result(
        self,
        triggered: bool,
        expected: Optional[float] = None,
        actual: Optional[float] = None,
        details: dict | None = None,
        evidence: dict | None = None,
    ) -> DiscrepancyResult:
        diff = diff_pct = None
        if expected is not None and actual is not None:
            diff = round(float(actual - expected), 2)
            if expected != 0:
                diff_pct = round(abs(diff / expected * 100), 2)

        return DiscrepancyResult(
            rule_code=self.rule_code,
            rule_name=self.rule_name,
            discrepancy_type=self.discrepancy_type,
            triggered=triggered,
            expected_value=expected,
            actual_value=actual,
            difference=diff,
            difference_pct=diff_pct,
            details=details or {},
            evidence=evidence or {},
            severity=self.severity,
        )

    def _safe_get(self, data: dict, path: str, default=None):
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
            if current is None:
                return default
        return current


class RulesEngineV2:
    """Rules Engine v2 - DB-backed with Redis cache"""

    def __init__(self):
        self._rules: List[BaseRule] = []
        self._rule_map: dict[str, BaseRule] = {}
        self._rule_index: dict[str, List[BaseRule]] = {}  # tag -> rules
        self._cache = None  # Redis cache

    def register(self, rule: BaseRule) -> "RulesEngineV2":
        if rule.rule_code in self._rule_map:
            logger.warning("rule_overwritten", rule_code=rule.rule_code)
        self._rules.append(rule)
        self._rule_map[rule.rule_code] = rule

        # Index by relevance tags
        for tag in rule.relevance_tags:
            if tag not in self._rule_index:
                self._rule_index[tag] = []
            self._rule_index[tag].append(rule)

        logger.info("rule_registered", rule_code=rule.rule_code, tags=rule.relevance_tags)
        return self

    def register_many(self, rules: List[BaseRule]) -> "RulesEngineV2":
        for rule in rules:
            self.register(rule)
        return self

    def get_rule(self, rule_code: str) -> Optional[BaseRule]:
        return self._rule_map.get(rule_code)

    def get_rules_by_tag(self, tag: str) -> List[BaseRule]:
        return self._rule_index.get(tag, [])

    def list_rules(self) -> List[dict]:
        return [
            {
                "code": r.rule_code,
                "name": r.rule_name,
                "type": r.discrepancy_type.value,
                "severity": r.severity,
                "requires_contract": r.requires_contract,
                "requires_freight_table": r.requires_freight_table,
                "tags": r.relevance_tags,
            }
            for r in self._rules
        ]

    def get_relevant_rules(self, context: RuleContext) -> List[BaseRule]:
        """Filter rules based on document context for performance"""
        relevant = []
        doc = context.document

        # Determine relevant tags from document
        tags = set()

        # ICMS tags
        if self._safe_get(doc, "icms.v_icms") is not None:
            tags.add("icms")
        if self._safe_get(doc, "uf_inicio") and self._safe_get(doc, "uf_fim"):
            tags.add("interstate")
        if self._safe_get(doc, "icms.cst") in ["10", "30", "60", "70", "90"]:
            tags.add("icms_st")

        # Freight tags
        if self._safe_get(doc, "freight_value") is not None:
            tags.add("freight")
        if self._safe_get(doc, "weight") is not None:
            tags.add("weight")
        if self._safe_get(doc, "volume") is not None:
            tags.add("cubage")
        if self._safe_get(doc, "components.v_advalorem") is not None:
            tags.add("advalorem")
        if self._safe_get(doc, "components.v_gris") is not None:
            tags.add("gris")

        # Redespacho
        if self._safe_get(doc, "has_redespacho"):
            tags.add("redespacho")

        # Pedágio
        if self._safe_get(doc, "modal_rodoviario.pedagio"):
            tags.add("toll")

        # CT-e Complementar
        if self._safe_get(doc, "modelo") in ["57", "67"]:
            tags.add("cte_complementar")

        # Collect rules matching tags
        seen = set()
        for tag in tags:
            for rule in self._rule_index.get(tag, []):
                if rule.rule_code not in seen:
                    seen.add(rule.rule_code)
                    relevant.append(rule)

        # Always include rules with no tags (generic)
        for rule in self._rules:
            if not rule.relevance_tags and rule.rule_code not in seen:
                relevant.append(rule)

        logger.debug("rules_filtered", total=len(self._rules), relevant=len(relevant), tags=list(tags))
        return relevant

    async def evaluate_all(self, context: RuleContext) -> List[DiscrepancyResult]:
        """Run all relevant rules"""
        results = []
        relevant_rules = self.get_relevant_rules(context)

        logger.info("rules_evaluation_start", total_rules=len(relevant_rules))

        for rule in relevant_rules:
            try:
                result = await rule.evaluate(context)
                if result.triggered:
                    results.append(result)
                    logger.info(
                        "discrepancy_found",
                        rule_code=rule.rule_code,
                        difference=result.difference,
                        severity=result.severity,
                    )
            except Exception as e:
                logger.exception("rule_evaluation_error", rule_code=rule.rule_code, error=str(e))

        logger.info("rules_evaluation_complete", triggered=len(results))
        return results

    def _safe_get(self, data: dict, path: str, default=None):
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
            if current is None:
                return default
        return current


# ============================================
# DEFAULT ENGINE FACTORY
# ============================================

async def create_engine_v2() -> RulesEngineV2:
    """Create engine with all built-in rules + DB config"""
    from app.services.rules_critical import (
        ICMSDifferentialRule,
        FCPRule,
        ICMSSTRule,
        FreightWeightValueRule,
        FreightCubageRule,
        RedespachoRule,
        TollPlazaRule,
        AdValoremRule,
        GRISRule,
        SicobanTableRuleReal,
        ComplementaryCTEAnulationRule,
        ComplementaryCTESubstitutionRule,
        ComplementaryCTEComplementRule,
        PesoRealVsFaturadoRule,
        ValorMinimoFreteRule,
    )

    engine = RulesEngineV2()
    engine.register_many([
        # ICMS Rules
        ICMSDifferentialRule(),
        FCPRule(),
        ICMSSTRule(),
        # Freight Rules
        FreightWeightValueRule(),
        FreightCubageRule(),
        PesoRealVsFaturadoRule(),
        ValorMinimoFreteRule(),
        # Other Rules
        RedespachoRule(),
        TollPlazaRule(),
        AdValoremRule(),
        GRISRule(),
        SicobanTableRuleReal(),
        # CT-e Complementar (3 rules)
        ComplementaryCTEAnulationRule(),
        ComplementaryCTESubstitutionRule(),
        ComplementaryCTEComplementRule(),
    ])
    return engine