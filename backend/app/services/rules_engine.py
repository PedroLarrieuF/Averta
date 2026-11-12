"""Rules Engine for Freight Audit - Pluggable, testable, extensible"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import structlog

from app.core.database import get_prisma

logger = structlog.get_logger()

# Constants for rule evaluation
# Float comparison tolerance (for currency values in BRL)
FLOAT_TOLERANCE: float = 0.01

# Toll plaza tolerance
PEDAGIO_TOLERANCE: float = 0.50


class DiscrepancyType(StrEnum):
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
    OTHER = "OTHER"


@dataclass
class RuleContext:
    """Context passed to all rules during evaluation"""

    document: dict[str, Any]
    contract: dict[str, Any] | None = None
    freight_table: dict[str, Any] | None = None
    carrier: dict[str, Any] | None = None
    client_settings: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscrepancyResult:
    """Result of a rule evaluation"""

    rule_code: str
    rule_name: str
    discrepancy_type: DiscrepancyType
    triggered: bool
    expected_value: float | None = None
    actual_value: float | None = None
    difference: float | None = None
    difference_pct: float | None = None
    details: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL


class BaseRule(ABC):
    """Base class for all audit rules"""

    # Class attributes (override in subclasses)
    rule_code: str = ""
    rule_name: str = ""
    discrepancy_type: DiscrepancyType = DiscrepancyType.OTHER
    severity: str = "MEDIUM"
    requires_contract: bool = False
    requires_freight_table: bool = False

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        """Evaluate the rule against the context"""
        pass

    def _create_result(
        self,
        triggered: bool,
        **kwargs: Any,
    ) -> DiscrepancyResult:
        expected = kwargs.get("expected")
        actual = kwargs.get("actual")
        details = kwargs.get("details")
        evidence = kwargs.get("evidence")
        severity = kwargs.get("severity")

        diff = None
        diff_pct = None
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
            severity=severity or self.severity,
        )

    def _safe_get(self, data: dict[str, Any], path: str, default: Any = None) -> Any:
        """Safely get nested dict value using dot notation"""
        keys = path.split(".")
        current: Any = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
            if current is None:
                return default
        return current


class RulesEngine:
    """Main rules engine - manages and executes all rules"""

    def __init__(self) -> None:
        self._rules: list[BaseRule] = []
        self._rule_map: dict[str, BaseRule] = {}

    def register(self, rule: BaseRule) -> "RulesEngine":
        """Register a rule"""
        if rule.rule_code in self._rule_map:
            logger.warning("rule_overwritten", rule_code=rule.rule_code)
        self._rules.append(rule)
        self._rule_map[rule.rule_code] = rule
        logger.info("rule_registered", rule_code=rule.rule_code, rule_name=rule.rule_name)
        return self

    def register_many(self, rules: list[BaseRule]) -> "RulesEngine":
        for rule in rules:
            self.register(rule)
        return self

    def get_rule(self, rule_code: str) -> BaseRule | None:
        return self._rule_map.get(rule_code)

    def list_rules(self) -> list[dict[str, Any]]:
        return [
            {
                "code": r.rule_code,
                "name": r.rule_name,
                "type": r.discrepancy_type.value,
                "severity": r.severity,
                "requires_contract": r.requires_contract,
                "requires_freight_table": r.requires_freight_table,
            }
            for r in self._rules
        ]

    async def evaluate_all(self, context: RuleContext) -> list[DiscrepancyResult]:
        """Run all applicable rules"""
        results = []

        # Filter rules based on context availability
        applicable_rules = [
            r
            for r in self._rules
            if (not r.requires_contract or context.contract)
            and (not r.requires_freight_table or context.freight_table)
        ]

        logger.info("rules_evaluation_start", total_rules=len(applicable_rules))

        for rule in applicable_rules:
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
                # Continue with other rules

        logger.info("rules_evaluation_complete", triggered=len(results))
        return results


# ============================================
# BUILT-IN RULES
# ============================================


class ICMSDifferentialRule(BaseRule):
    """ICMS Differential (DIFAL) - Interstate operations"""

    rule_code = "ICMS_DIFAL"
    rule_name = "ICMS Diferencial de Alíquota (DIFAL)"
    discrepancy_type = DiscrepancyType.ICMS_DIFFERENTIAL
    severity = "HIGH"
    requires_contract = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        contract = context.contract

        if not contract:
            return self._create_result(False, details={"reason": "No contract"})

        # Get UF origin/destination
        uf_origem = self._safe_get(doc, "uf_inicio")
        uf_destino = self._safe_get(doc, "uf_fim")

        if not uf_origem or not uf_destino or uf_origem == uf_destino:
            return self._create_result(False, details={"reason": "Same UF or missing"})

        # Get ICMS from document
        icms_doc = self._safe_get(doc, "icms.v_icms", 0)
        bc_doc = self._safe_get(doc, "icms.v_bc", 0)

        # Get expected from contract/table
        # This would come from the freight table rules
        tabela = context.freight_table
        if not tabela:
            return self._create_result(False, details={"reason": "No freight table"})

        # Look up DIFAL rule in table
        difal_rule = self._lookup_difal(tabela.get("rules", {}), uf_origem, uf_destino)
        if not difal_rule:
            return self._create_result(False, details={"reason": "No DIFAL rule for UF pair"})

        # Calculate expected
        p_difal = difal_rule.get("aliquota_difal", 0)
        p_fcp = difal_rule.get("aliquota_fcp", 0)
        expected_icms = round(bc_doc * (p_difal + p_fcp) / 100, 2)

        triggered = abs(icms_doc - expected_icms) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_icms,
            actual=icms_doc,
            details={
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "base_calculo": bc_doc,
                "aliquota_difal": p_difal,
                "aliquota_fcp": p_fcp,
            },
            evidence={"table_rule": difal_rule},
        )

    def _lookup_difal(
        self, rules: dict[str, Any], uf_origem: str, uf_destino: str
    ) -> dict[str, Any] | None:
        difal_rules = rules.get("difal", [])
        for rule in difal_rules:
            if isinstance(rule, dict):
                if rule.get("uf_origem") == uf_origem and rule.get("uf_destino") == uf_destino:
                    return rule
        return None


class FCPRule(BaseRule):
    """FCP - Fundo de Combate à Pobreza"""

    rule_code = "ICMS_FCP"
    rule_name = "FCP - Fundo de Combate à Pobreza"
    discrepancy_type = DiscrepancyType.ICMS_FCP
    severity = "HIGH"
    requires_contract = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        uf_destino = self._safe_get(doc, "uf_fim")

        if not uf_destino:
            return self._create_result(False)

        # FCP applies to certain UFs
        fcp_ufs = {
            "AC": 2.0,
            "AL": 2.0,
            "AM": 2.0,
            "AP": 2.0,
            "BA": 2.0,
            "CE": 2.0,
            "MA": 2.0,
            "PA": 2.0,
            "PB": 2.0,
            "PE": 2.0,
            "PI": 2.0,
            "RN": 2.0,
            "RR": 2.0,
            "SE": 2.0,
        }

        if uf_destino not in fcp_ufs:
            return self._create_result(False)

        bc = self._safe_get(doc, "icms.v_bc", 0)
        icms_doc = self._safe_get(doc, "icms.v_icms", 0)
        p_fcp = fcp_ufs[uf_destino]
        expected_fcp = round(bc * p_fcp / 100, 2)

        # Check if FCP is included in ICMS
        triggered = icms_doc < expected_fcp - 0.01

        return self._create_result(
            triggered=triggered,
            expected=expected_fcp,
            actual=icms_doc,
            details={"uf_destino": uf_destino, "aliquota_fcp": p_fcp, "base_calculo": bc},
        )


class FreightWeightValueRule(BaseRule):
    """Freight by Weight vs Value validation"""

    rule_code = "FRETE_PESO_VALOR"
    rule_name = "Frete Peso vs Valor (Cubagem)"
    discrepancy_type = DiscrepancyType.FREIGHT_WEIGHT_VALUE
    severity = "HIGH"
    requires_contract = True
    requires_freight_table = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        weight = self._safe_get(doc, "weight", 0)
        volume = self._safe_get(doc, "volume", 0)
        freight_charged = self._safe_get(doc, "freight_value", 0)

        if not table or weight <= 0:
            return self._create_result(False, details={"reason": "Missing table or weight"})

        rules = table.get("rules", {})
        faixas = rules.get("faixas_peso", [])

        # Find applicable faixa
        faixa = None
        for f in faixas:
            if f.get("peso_inicial", 0) <= weight <= f.get("peso_final", 999999):
                faixa = f
                break

        if not faixa:
            return self._create_result(False, details={"reason": "No matching weight range"})

        # Calculate expected
        rate_per_kg = faixa.get("valor_kg", 0)
        min_freight = faixa.get("valor_minimo", 0)

        expected_by_weight = round(weight * rate_per_kg, 2)
        expected = max(expected_by_weight, min_freight)

        # Also check cubage if volume provided
        if volume > 0:
            cubage_rate = faixa.get("valor_m3", 0)
            if cubage_rate:
                expected_by_cubage = round(volume * cubage_rate, 2)
                expected = max(expected, expected_by_cubage)

        triggered = abs(freight_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=freight_charged,
            details={
                "peso": weight,
                "volume": volume,
                "faixa": faixa.get("descricao"),
                "valor_kg": rate_per_kg,
                "valor_minimo": min_freight,
            },
        )


class RedespachoRule(BaseRule):
    """Redespacho validation - CT-e complementar"""

    rule_code = "REDESPACHO_VALIDACAO"
    rule_name = "Validação de Redespacho (CT-e Complementar)"
    discrepancy_type = DiscrepancyType.REDESPACHO
    severity = "HIGH"

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        has_redespacho = self._safe_get(doc, "has_redespacho", False)
        if not has_redespacho:
            return self._create_result(False)

        redespacho_details = self._safe_get(doc, "redespacho_details", [])
        if not redespacho_details:
            return self._create_result(
                True,
                details={"reason": "Redespacho indicado mas sem CT-e complementar"},
                severity="CRITICAL",
            )

        # Check if values match
        total_redespacho = sum(r.get("valor", 0) for r in redespacho_details)
        freight_value = self._safe_get(doc, "freight_value", 0)

        # Redespacho value should not exceed main freight
        triggered = total_redespacho > freight_value * 1.1  # 10% tolerance

        return self._create_result(
            triggered=triggered,
            expected=freight_value,
            actual=total_redespacho,
            details={
                "total_redespacho": total_redespacho,
                "frete_principal": freight_value,
                "quantidade_ctes": len(redespacho_details),
            },
            evidence={"redespachos": redespacho_details},
        )


class TollPlazaRule(BaseRule):
    """Pedágio validation"""

    rule_code = "PEDAGIO_CONFERENCIA"
    rule_name = "Conferência de Pedágio"
    discrepancy_type = DiscrepancyType.TOLL_PLAZA
    severity = "MEDIUM"
    requires_freight_table = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        pedagios_doc = self._safe_get(doc, "modal_rodoviario.pedagio", [])
        if not pedagios_doc:
            return self._create_result(False)

        if not table:
            return self._create_result(False, details={"reason": "No freight table"})

        # Get expected tolls from table
        expected_tolls = table.get("rules", {}).get("pedagios", [])

        total_charged = sum(p.get("valor", 0) for p in pedagios_doc)
        total_expected = 0

        for p_doc in pedagios_doc:
            praca = p_doc.get("praça")
            eixos = p_doc.get("eixos", 0)

            for p_exp in expected_tolls:
                if p_exp.get("praca") == praca and p_exp.get("eixos") == eixos:
                    total_expected += p_exp.get("valor", 0)
                    break

        triggered = abs(total_charged - total_expected) > PEDAGIO_TOLERANCE  # R$ 0,50 tolerance

        return self._create_result(
            triggered=triggered,
            expected=total_expected,
            actual=total_charged,
            details={
                "pedagios_documento": pedagios_doc,
                "pedagios_tabela": expected_tolls,
            },
        )


class AdValoremRule(BaseRule):
    """Ad Valorem - % sobre valor da mercadoria"""

    rule_code = "AD_VALOREM"
    rule_name = "Ad Valorem (Seguro sobre Valor)"
    discrepancy_type = DiscrepancyType.AD_VALOREM
    severity = "MEDIUM"
    requires_contract = True
    requires_freight_table = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        total_value = self._safe_get(doc, "total_value", 0)
        advalorem_charged = self._safe_get(doc, "components.v_advalorem", 0)

        if total_value <= 0:
            return self._create_result(False)

        if not table:
            return self._create_result(False)

        rules = table.get("rules", {})
        advalorem_config = rules.get("advalorem", {})

        rate = advalorem_config.get("aliquota", 0)
        teto = advalorem_config.get("teto", None)

        expected = round(total_value * rate / 100, 2)
        if teto:
            expected = min(expected, teto)

        triggered = abs(advalorem_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=advalorem_charged,
            details={
                "valor_mercadoria": total_value,
                "aliquota": rate,
                "teto": teto,
            },
        )


class GRISRule(BaseRule):
    """GRIS - Gerenciamento de Risco"""

    rule_code = "GRIS"
    rule_name = "GRIS - Gerenciamento de Risco"
    discrepancy_type = DiscrepancyType.GRIS
    severity = "MEDIUM"
    requires_contract = True
    requires_freight_table = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        total_value = self._safe_get(doc, "total_value", 0)
        gris_charged = self._safe_get(doc, "components.v_gris", 0)

        if total_value <= 0:
            return self._create_result(False)

        if not table:
            return self._create_result(False)

        rules = table.get("rules", {})
        gris_config = rules.get("gris", {})

        rate = gris_config.get("aliquota", 0)
        teto = gris_config.get("teto", None)

        expected = round(total_value * rate / 100, 2)
        if teto:
            expected = min(expected, teto)

        triggered = abs(gris_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=gris_charged,
            details={
                "valor_mercadoria": total_value,
                "aliquota": rate,
                "teto": teto,
            },
        )


class SicobanTableRule(BaseRule):
    """Sicoban / Tabela de Frete validation"""

    rule_code = "SICOABAN_TABELA"
    rule_name = "Conferência Tabela Sicoban/Frete"
    discrepancy_type = DiscrepancyType.SICOBAN_TABLE
    severity = "HIGH"
    requires_contract = True
    requires_freight_table = True

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        table = context.freight_table

        if not table:
            return self._create_result(False)

        # This would implement full table lookup based on:
        # - CEP origem/destino
        # - Peso/Volume
        # - Tipo de carga
        # - Modalidade

        # For now, delegate to weight/value rule
        return self._create_result(
            False,
            details={"note": "Implemented via FRETE_PESO_VALOR and specific table lookups"},
        )


class ComplementaryCTERule(BaseRule):
    """CT-e Complementar validation"""

    rule_code = "CTE_COMPLEMENTAR"
    rule_name = "CT-e Complementar (Anulação/Substituição)"
    discrepancy_type = DiscrepancyType.COMPLEMENTARY_CTE
    severity = "HIGH"

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        # Check if this is a complementary CT-e
        modelo = self._safe_get(doc, "modelo", "57")
        if modelo not in ["57", "67"]:  # 57=CTe, 67=CTeOS
            return self._create_result(False)

        # Look for complementary references
        # This would need access to document history

        return self._create_result(
            False,
            details={"note": "Requires document history cross-reference"},
        )


# ============================================
# DEFAULT ENGINE INSTANCE
# ============================================


def create_default_engine() -> RulesEngine:
    """Create engine with all built-in rules"""
    engine = RulesEngine()
    engine.register_many(
        [
            ICMSDifferentialRule(),
            FCPRule(),
            FreightWeightValueRule(),
            RedespachoRule(),
            TollPlazaRule(),
            AdValoremRule(),
            GRISRule(),
            SicobanTableRule(),
            ComplementaryCTERule(),
        ]
    )
    return engine


# Global instance
default_engine = create_default_engine()


async def run_rules(
    document_id: str, parsed_data: dict[str, Any], company_id: str, client_id: str
) -> list[DiscrepancyResult]:
    """Main entry point for running rules (called from Celery task)"""
    db = await get_prisma()

    # Fetch contract and freight table
    contract = None
    freight_table = None

    if parsed_data.get("emit_cnpj"):
        contract = await db.contract.find_first(
            where={
                "companyId": company_id,
                "carrier": {"cnpj": parsed_data["emit_cnpj"]},
                "status": "ACTIVE",
            },
            include={"tables": {"where": {"isActive": True}}},
        )

        if contract and contract.tables:
            freight_table = contract.tables[0]

    # Build context
    context = RuleContext(
        document=parsed_data,
        contract=contract,
        freight_table=freight_table,
    )

    # Run rules
    results = await default_engine.evaluate_all(context)

    # Save discrepancies
    for result in results:
        await db.discrepancy.create(
            data={
                "companyId": company_id,
                "clientId": client_id,
                "documentId": document_id,
                "carrierId": contract.carrierId if contract else None,
                "contractId": contract.id if contract else None,
                "type": result.discrepancy_type.value,
                "status": "DETECTED",
                "ruleCode": result.rule_code,
                "ruleDescription": result.rule_name,
                "expectedValue": result.expected_value or 0,
                "actualValue": result.actual_value or 0,
                "difference": result.difference or 0,
                "differencePct": result.difference_pct or 0,
                "details": result.details,
                "evidence": result.evidence,
            }
        )

    logger.info("rules_completed", document_id=document_id, discrepancies=len(results))
    return results
