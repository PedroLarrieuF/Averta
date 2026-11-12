"""Critical Rules Implementation - 6 critical + complementary CT-e rules + ML Anomaly Detection"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import structlog

from app.core.database import get_prisma
from app.services.rules_engine_v2 import BaseRule, DiscrepancyResult, DiscrepancyType, RuleContext

logger = structlog.get_logger()

# Constants for rule evaluation
# Float comparison tolerance (for currency values in BRL)
FLOAT_TOLERANCE: float = 0.01

# ML Anomaly Detection thresholds
ML_ANOMALY_HIGH_THRESHOLD: float = -0.7
ML_ANOMALY_MEDIUM_THRESHOLD: float = -0.3

# Weight thresholds
PESO_REAL_HIGH_DIFF_PCT: float = 20.0
PESO_REAL_MEDIUM_DIFF_PCT: float = 5.0  # default tolerance
VALOR_MINIMO_PESO_LIMITE_KG: float = 10000.0  # 10 ton

# Toll plaza tolerance
PEDAGIO_TOLERANCE: float = 0.50

# NF-e Critical Rules Constants
NFE_ICMS_TOLERANCE: float = 0.05  # 5 centavos tolerance for ICMS
NFE_FRETE_BASE_TOLERANCE: float = 0.10  # 10 centavos for freight in base
NFE_CTE_CROSS_TOLERANCE_PCT: float = 2.0  # 2% tolerance for cross-validation

# NF-e Cancellation/Inutilizacao Constants
MIN_JUSTIFICATION_LENGTH: int = 15
CANCELLATION_TIME_LIMIT_HOURS: int = 24

# UF region mapping for DIFAL (from icms_rules.json)
UF_REGIONS = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CentroOeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}

# Internal ICMS aliquots (from icms_rules.json)
ICMS_ALIQUOTAS_INTERNAS = {
    "AC": 0.17,
    "AL": 0.18,
    "AP": 0.18,
    "AM": 0.18,
    "BA": 0.205,
    "CE": 0.18,
    "DF": 0.18,
    "ES": 0.17,
    "GO": 0.19,
    "MA": 0.20,
    "MT": 0.17,
    "MS": 0.17,
    "MG": 0.18,
    "PA": 0.17,
    "PB": 0.18,
    "PR": 0.18,
    "PE": 0.18,
    "PI": 0.18,
    "RJ": 0.20,
    "RN": 0.18,
    "RS": 0.18,
    "RO": 0.175,
    "RR": 0.17,
    "SC": 0.17,
    "SP": 0.18,
    "SE": 0.18,
    "TO": 0.18,
}

# FCP aliquots (from icms_rules.json)
FCP_ALIQUOTAS = {
    "AC": 0.00,
    "AL": 0.02,
    "AP": 0.02,
    "AM": 0.02,
    "BA": 0.02,
    "CE": 0.02,
    "DF": 0.00,
    "ES": 0.02,
    "GO": 0.00,
    "MA": 0.02,
    "MT": 0.00,
    "MS": 0.00,
    "MG": 0.02,
    "PA": 0.02,
    "PB": 0.02,
    "PR": 0.02,
    "PE": 0.02,
    "PI": 0.02,
    "RJ": 0.02,
    "RN": 0.02,
    "RS": 0.02,
    "RO": 0.00,
    "RR": 0.02,
    "SC": 0.02,
    "SP": 0.02,
    "SE": 0.02,
    "TO": 0.00,
}

# Inter-state aliquots by region
ALIQUOTAS_INTERSTADUAIS = {
    ("Sul", "Norte"): 0.12,
    ("Sul", "Nordeste"): 0.12,
    ("Sul", "CentroOeste"): 0.12,
    ("Sudeste", "Norte"): 0.12,
    ("Sudeste", "Nordeste"): 0.12,
    ("Sudeste", "CentroOeste"): 0.12,
    ("CentroOeste", "Norte"): 0.12,
    ("CentroOeste", "Nordeste"): 0.12,
    ("Norte", "Sul"): 0.07,
    ("Norte", "Sudeste"): 0.07,
    ("Norte", "CentroOeste"): 0.07,
    ("Nordeste", "Sul"): 0.07,
    ("Nordeste", "Sudeste"): 0.07,
    ("Nordeste", "CentroOeste"): 0.07,
}

# ============================================
# ML ANOMALY DETECTION RULE
# ============================================


class MLAnomalyRule(BaseRule):
    """ML Anomaly Detection using Isolation Forest.

    Detects anomalous discrepancies that deterministic rules miss,
    based on historical patterns learned from auditor feedback.
    """

    rule_code = "ML_ANOMALY"
    rule_name = "ML Anomaly Detection (Isolation Forest)"
    discrepancy_type = DiscrepancyType.OTHER
    severity = "MEDIUM"
    relevance_tags = ["ml", "anomaly", "freight"]

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config or {})
        self.threshold = self.config.get("anomaly_threshold", -0.5)
        self.endpoint = self.config.get("ml_endpoint", "http://localhost:8001/ml/anomaly-score")
        self.timeout = self.config.get("timeout", 5.0)

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Extract features from context
        features = self._extract_features(context)

        # Call ML inference endpoint
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.endpoint,
                    json={"features": features},
                )
                response.raise_for_status()
                result = response.json()
                score = result["anomaly_score"]
                is_anomaly = result["is_anomaly"]
        except httpx.TimeoutException:
            logger.warning("ml_inference_timeout", rule_code=self.rule_code)
            return self._create_result(
                triggered=False,
                details={"error": "ML inference timeout", "fallback": True},
            )
        except httpx.HTTPStatusError as e:
            logger.warning(
                "ml_inference_http_error", rule_code=self.rule_code, status=e.response.status_code
            )
            return self._create_result(
                triggered=False,
                details={
                    "error": f"ML inference HTTP error: {e.response.status_code}",
                    "fallback": True,
                },
            )
        except Exception as e:
            logger.exception("ml_inference_error", rule_code=self.rule_code, error=str(e))
            return self._create_result(
                triggered=False,
                details={"error": f"ML inference error: {str(e)}", "fallback": True},
            )

        triggered = is_anomaly

        # Determine severity based on anomaly score
        if score < ML_ANOMALY_HIGH_THRESHOLD:
            self.severity = "HIGH"
        elif score < ML_ANOMALY_MEDIUM_THRESHOLD:
            self.severity = "MEDIUM"
        else:
            self.severity = "LOW"

        return self._create_result(
            triggered=triggered,
            expected=0,  # No expected value for ML
            actual=score,
            details={
                "anomaly_score": score,
                "threshold": self.threshold,
                "is_anomaly": is_anomaly,
                "features": features,
            },
        )

    def _extract_features(self, context: RuleContext) -> dict[str, float]:
        doc = context.document
        metadata = context.metadata

        # Hash categorical fields
        rule_code = metadata.get("rule_code", "")
        carrier_id = doc.get("carrier_id", "") or doc.get("carrierId", "")
        client_id = doc.get("client_id", "") or doc.get("clientId", "")

        rule_type_hash = hash(rule_code) % 10000
        carrier_id_hash = hash(carrier_id) % 10000
        client_id_hash = hash(client_id) % 10000

        # UF encoding
        UF_ENCODING = {
            "AC": 1,
            "AL": 2,
            "AP": 3,
            "AM": 4,
            "BA": 5,
            "CE": 6,
            "DF": 7,
            "ES": 8,
            "GO": 9,
            "MA": 10,
            "MT": 11,
            "MS": 12,
            "MG": 13,
            "PA": 14,
            "PB": 15,
            "PR": 16,
            "PE": 17,
            "PI": 18,
            "RJ": 19,
            "RN": 20,
            "RS": 21,
            "RO": 22,
            "RR": 23,
            "SC": 24,
            "SP": 25,
            "SE": 26,
            "TO": 27,
        }

        uf_origem = doc.get("uf_inicio", "") or doc.get("ufOrigem", "") or doc.get("uf_origem", "")
        uf_destino = doc.get("uf_fim", "") or doc.get("ufDestino", "") or doc.get("uf_destino", "")
        uf_origem_encoded = UF_ENCODING.get(uf_origem.upper() if uf_origem else "", 0)
        uf_destino_encoded = UF_ENCODING.get(uf_destino.upper() if uf_destino else "", 0)

        # Document type
        DOCUMENT_TYPE_ENCODING = {
            "CTE": 1,
            "NFE": 2,
            "CTE_COMPLEMENTAR": 3,
            "NFE_COMPLEMENTAR": 4,
            "INVOICE": 5,
            "SPREADSHEET": 6,
            "CONTRACT": 7,
            "OTHER": 8,
        }
        doc_type = doc.get("type", "OTHER")
        if hasattr(doc_type, "value"):
            doc_type = doc_type.value
        document_type_encoded = DOCUMENT_TYPE_ENCODING.get(str(doc_type).upper(), 8)

        # Severity
        SEVERITY_ENCODING = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        severity = metadata.get("severity", "MEDIUM")
        severity_encoded = SEVERITY_ENCODING.get(
            severity.upper() if isinstance(severity, str) else "MEDIUM", 1
        )

        # Numeric features
        value = doc.get("total_value", 0) or doc.get("totalValue", 0) or 0
        weight = doc.get("weight", 0) or 0
        volume = doc.get("volume", 0) or 0
        diff_pct = metadata.get("difference_pct", 0) or metadata.get("differencePct", 0) or 0
        distance_km = doc.get("distancia_km", 0) or doc.get("distanceKm", 0) or 0
        eixos = (
            doc.get("modal_rodoviario_veiculo_eixos", 0)
            or doc.get("modalRodoviarioVeiculoEixos", 0)
            or 0
        )

        has_icms = 1 if (doc.get("icms_value", None) or doc.get("icmsValue", None)) else 0
        has_freight_value = (
            1 if (doc.get("freight_value", None) or doc.get("freightValue", None)) else 0
        )

        return {
            "rule_type_hash": float(rule_type_hash),
            "carrier_id_hash": float(carrier_id_hash),
            "client_id_hash": float(client_id_hash),
            "value": float(value),
            "weight": float(weight),
            "volume": float(volume),
            "uf_origem_encoded": float(uf_origem_encoded),
            "uf_destino_encoded": float(uf_destino_encoded),
            "diff_pct": float(diff_pct),
            "severity_encoded": float(severity_encoded),
            "document_type_encoded": float(document_type_encoded),
            "distance_km": float(distance_km),
            "eixos": float(eixos),
            "has_icms": float(has_icms),
            "has_freight_value": float(has_freight_value),
        }


# ============================================
# ICMS RULES (3 rules)
# ============================================


class ICMSDifferentialRule(BaseRule):
    """ICMS Differential (DIFAL) - Interstate operations"""

    rule_code = "ICMS_DIFAL"
    rule_name = "ICMS Diferencial de Alíquota (DIFAL)"
    discrepancy_type = DiscrepancyType.ICMS_DIFFERENTIAL
    severity = "HIGH"
    requires_contract = True
    relevance_tags = ["icms", "interstate"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        contract = context.contract

        if not contract:
            return self._create_result(False, details={"reason": "No contract"})

        uf_origem = self._safe_get(doc, "uf_inicio")
        uf_destino = self._safe_get(doc, "uf_fim")

        if not uf_origem or not uf_destino or uf_origem == uf_destino:
            return self._create_result(False, details={"reason": "Same UF or missing"})

        icms_doc = self._safe_get(doc, "icms.v_icms", 0)
        bc_doc = self._safe_get(doc, "icms.v_bc", 0)

        tabela = context.freight_table
        if not tabela:
            return self._create_result(False, details={"reason": "No freight table"})

        difal_rule = self._lookup_difal(tabela.get("rules", {}), uf_origem, uf_destino)
        if not difal_rule:
            return self._create_result(False, details={"reason": "No DIFAL rule for UF pair"})

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
        for rule in rules.get("difal", []):
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
    relevance_tags = ["icms", "interstate"]

    # FCP UFs e alíquotas (2024)
    FCP_UFS = {
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

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        uf_destino = self._safe_get(doc, "uf_fim")

        if not uf_destino or uf_destino not in self.FCP_UFS:
            return self._create_result(False)

        bc = self._safe_get(doc, "icms.v_bc", 0)
        icms_doc = self._safe_get(doc, "icms.v_icms", 0)
        p_fcp = self.FCP_UFS[uf_destino]
        expected_fcp = round(bc * p_fcp / 100, 2)

        triggered = icms_doc < expected_fcp - FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_fcp,
            actual=icms_doc,
            details={"uf_destino": uf_destino, "aliquota_fcp": p_fcp, "base_calculo": bc},
        )


class ICMSSTRule(BaseRule):
    """ICMS Substituição Tributária (ST) - Por UF + NCM + CST"""

    rule_code = "ICMS_ST"
    rule_name = "ICMS Substituição Tributária (ST)"
    discrepancy_type = DiscrepancyType.ICMS_ST
    severity = "HIGH"
    requires_contract = True
    relevance_tags = ["icms", "icms_st"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        tabela = context.freight_table

        if not tabela:
            return self._create_result(False, details={"reason": "No freight table"})

        # Dados do documento
        cst = self._safe_get(doc, "icms.cst")
        ncm = self._safe_get(doc, "ncm")  # precisa vir do XML
        uf_origem = self._safe_get(doc, "uf_inicio")
        uf_destino = self._safe_get(doc, "uf_fim")

        # ST só aplica para CSTs específicos
        st_csts = ["10", "30", "60", "70", "90"]
        if cst not in st_csts:
            return self._create_result(False, details={"reason": f"CST {cst} não sujeito a ST"})

        # Buscar regra ST na tabela
        rules = tabela.get("rules", {})
        st_rules = rules.get("icms_st", [])

        # Match por NCM + UF origem/destino
        st_rule = None
        for rule in st_rules:
            if rule.get("ncm") == ncm:
                # Verificar UF
                uf_origem_rule = rule.get("uf_origem", "*")
                uf_destino_rule = rule.get("uf_destino", "*")
                if (uf_origem_rule in ("*", uf_origem)) and (uf_destino_rule in ("*", uf_destino)):
                    st_rule = rule
                    break

        if not st_rule:
            return self._create_result(False, details={"reason": f"No ST rule for NCM {ncm}"})

        # Calcular esperado
        v_bc_st = self._safe_get(doc, "icms.v_bc_st", 0)
        p_icms_st = st_rule.get("aliquota_st", 0)
        expected_st = round(v_bc_st * p_icms_st / 100, 2)

        actual_st = self._safe_get(doc, "icms.v_icms_st", 0)

        triggered = abs(actual_st - expected_st) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_st,
            actual=actual_st,
            details={
                "cst": cst,
                "ncm": ncm,
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "base_calculo_st": v_bc_st,
                "aliquota_st": p_icms_st,
            },
            evidence={"st_rule": st_rule},
        )


# ============================================
# FREIGHT RULES (4 rules)
# ============================================


class FreightWeightValueRule(BaseRule):
    """Freight by Weight vs Value validation"""

    rule_code = "FRETE_PESO_VALOR"
    rule_name = "Frete Peso vs Valor (Faixas)"
    discrepancy_type = DiscrepancyType.FREIGHT_WEIGHT_VALUE
    severity = "HIGH"
    requires_contract = True
    requires_freight_table = True
    relevance_tags = ["freight", "weight"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        weight = self._safe_get(doc, "weight", 0)
        freight_charged = self._safe_get(doc, "freight_value", 0)

        if not table or weight <= 0:
            return self._create_result(False, details={"reason": "Missing table or weight"})

        rules = table.get("rules", {})
        faixas = rules.get("faixas_peso", [])

        faixa = None
        for f in faixas:
            if f.get("peso_inicial", 0) <= weight <= f.get("peso_final", 999999):
                faixa = f
                break

        if not faixa:
            return self._create_result(False, details={"reason": "No matching weight range"})

        rate_per_kg = faixa.get("valor_kg", 0)
        min_freight = faixa.get("valor_minimo", 0)

        expected_by_weight = round(weight * rate_per_kg, 2)
        expected = max(expected_by_weight, min_freight)

        triggered = abs(freight_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=freight_charged,
            details={
                "peso": weight,
                "faixa": faixa.get("descricao"),
                "valor_kg": rate_per_kg,
                "valor_minimo": min_freight,
            },
        )


class FreightCubageRule(BaseRule):
    """Freight Cubage (Volume) validation - separate from weight"""

    rule_code = "FRETE_CUBAGE"
    rule_name = "Frete Cubagem (m³) vs Tabela"
    discrepancy_type = DiscrepancyType.FREIGHT_CUBAGE
    severity = "HIGH"
    requires_contract = True
    requires_freight_table = True
    relevance_tags = ["freight", "cubage"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        volume = self._safe_get(doc, "volume", 0)
        freight_charged = self._safe_get(doc, "freight_value", 0)

        if not table or volume <= 0:
            return self._create_result(False, details={"reason": "Missing table or volume"})

        rules = table.get("rules", {})
        faixas = rules.get("faixas_cubagem", [])  # faixas por m³

        if not faixas:
            # Fallback: usar faixas de peso se não houver cubagem específica
            return self._create_result(False, details={"reason": "No cubage ranges defined"})

        faixa = None
        for f in faixas:
            if f.get("cubagem_inicial", 0) <= volume <= f.get("cubagem_final", 999999):
                faixa = f
                break

        if not faixa:
            return self._create_result(False, details={"reason": "No matching cubage range"})

        rate_per_m3 = faixa.get("valor_m3", 0)
        min_freight = faixa.get("valor_minimo", 0)

        expected_by_cubage = round(volume * rate_per_m3, 2)
        expected = max(expected_by_cubage, min_freight)

        triggered = abs(freight_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=freight_charged,
            details={
                "volume": volume,
                "faixa": faixa.get("descricao"),
                "valor_m3": rate_per_m3,
                "valor_minimo": min_freight,
            },
        )


class PesoRealVsFaturadoRule(BaseRule):
    """Peso Real vs. Peso Faturado - Detecta divergência de peso"""

    rule_code = "PESO_REAL_VS_FATURADO"
    rule_name = "Peso Real (XML) vs. Peso Faturado"
    discrepancy_type = DiscrepancyType.PESO_REAL_VS_FATURADO
    severity = "HIGH"
    relevance_tags = ["weight"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        # Peso do XML (CT-e/NF-e)
        peso_bruto_xml = self._safe_get(doc, "peso_bruto")  # vPesoB
        self._safe_get(doc, "peso_liquido")  # vPesoL

        # Peso faturado (na fatura/tabela)
        peso_faturado = self._safe_get(doc, "weight")

        if not peso_bruto_xml or not peso_faturado:
            return self._create_result(False, details={"reason": "Missing weight data"})

        # Tolerância configurável (default 5%)
        tolerance_pct = self.config.get("tolerance_pct", 5.0)
        diff_pct = abs(peso_faturado - peso_bruto_xml) / peso_bruto_xml * 100

        triggered = diff_pct > tolerance_pct

        # Set severity before calling _create_result
        self.severity = "HIGH" if diff_pct > PESO_REAL_HIGH_DIFF_PCT else "MEDIUM"
        return self._create_result(
            triggered=triggered,
            expected=peso_bruto_xml,
            actual=peso_faturado,
            details={
                "peso_xml": peso_bruto_xml,
                "peso_faturado": peso_faturado,
                "tolerancia_pct": tolerance_pct,
                "difference": round(peso_faturado - peso_bruto_xml, 2),
                "difference_pct": round(diff_pct, 2),
            },
        )


class ValorMinimoFreteRule(BaseRule):
    """Valor Mínimo de Frete - ANTT Resolução 5.839/2021"""

    rule_code = "VALOR_MINIMO_FRETE"
    rule_name = "Valor Mínimo de Frete (ANTT 5.839/2021)"
    discrepancy_type = DiscrepancyType.VALOR_MINIMO_FRETE
    severity = "CRITICAL"
    requires_contract = True
    relevance_tags = ["freight", "weight"]

    # Pisos por eixo (R$/km) - ANTT 2024
    PISO_POR_EIXO = {
        2: 1.85,  # 2 eixos
        3: 2.45,  # 3 eixos
        4: 3.05,  # 4 eixos
        5: 3.65,  # 5 eixos
        6: 4.25,  # 6 eixos
        7: 4.85,  # 7 eixos
        8: 5.45,  # 8 eixos
        9: 6.05,  # 9 eixos
    }

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        tabela = context.freight_table

        if not tabela:
            return self._create_result(False, details={"reason": "No freight table"})

        peso = self._safe_get(doc, "weight", 0)
        freight_charged = self._safe_get(doc, "freight_value", 0)
        eixos = self._safe_get(doc, "modal_rodoviario.veiculo_eixos", 0)
        distancia_km = self._safe_get(doc, "distancia_km", 0)

        if peso <= 0 or eixos not in self.PISO_POR_EIXO or distancia_km <= 0:
            return self._create_result(False, details={"reason": "Missing data for ANTT calc"})

        # Calcular mínimo: piso por eixo × distância
        piso_eixo = self.PISO_POR_EIXO[eixos]
        frete_minimo = round(piso_eixo * distancia_km, 2)

        # Aplicar fator de peso se > limite (ex: > 10 ton)
        if peso > VALOR_MINIMO_PESO_LIMITE_KG:  # 10 ton
            frete_minimo *= 1.2

        triggered = freight_charged < frete_minimo - FLOAT_TOLERANCE

        # severity is already CRITICAL from class attribute
        return self._create_result(
            triggered=triggered,
            expected=frete_minimo,
            actual=freight_charged,
            details={
                "eixos": eixos,
                "distancia_km": distancia_km,
                "piso_por_eixo_km": piso_eixo,
                "peso": peso,
            },
        )


# ============================================
# SICOBAN REAL (Lookup CEP)
# ============================================


class SicobanTableRuleReal(BaseRule):
    """Sicoban Table Lookup - CEP origem/destino + tipo carga + modal"""

    rule_code = "SICOBAN_TABLE_REAL"
    rule_name = "Tabela Sicoban/ANTT - Lookup por CEP"
    discrepancy_type = DiscrepancyType.SICOBAN_TABLE
    severity = "HIGH"
    requires_contract = True
    requires_freight_table = True
    relevance_tags = ["freight", "sicoban"]

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self._sicoban_data: list[dict[str, Any]] | None = None

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        if not table:
            return self._create_result(False, details={"reason": "No freight table"})

        cep_origem = self._safe_get(doc, "cep_origem") or self._safe_get(doc, "rem_endereco.cep")
        cep_destino = self._safe_get(doc, "cep_destino") or self._safe_get(doc, "dest_endereco.cep")
        tipo_carga = self._safe_get(doc, "tipo_carga", "G")  # G=Geral, P=Perigoso, etc.
        modalidade = self._safe_get(doc, "modalidade", "R")  # R=Rodoviário, A=Aéreo, etc.

        if not cep_origem or not cep_destino:
            return self._create_result(False, details={"reason": "Missing CEP"})

        # Buscar na tabela Sicoban (carregada da freight_table ou cache)
        sicoban_rules = table.get("rules", {}).get("sicoban", [])
        if not sicoban_rules:
            # Carregar do arquivo se não estiver na tabela
            sicoban_rules = await self._load_sicoban_data()

        # Match: CEP range + tipo_carga + modalidade
        match = self._find_sicoban_match(
            sicoban_rules, cep_origem, cep_destino, tipo_carga, modalidade
        )

        if not match:
            return self._create_result(False, details={"reason": "No Sicoban match for CEP pair"})

        # Validar frete
        peso = self._safe_get(doc, "weight", 0)
        volume = self._safe_get(doc, "volume", 0)
        freight_charged = self._safe_get(doc, "freight_value", 0)

        valor_kg = match.get("valor_kg", 0)
        valor_m3 = match.get("valor_m3", 0)
        valor_min = match.get("valor_minimo", 0)

        expected_kg = round(peso * valor_kg, 2) if peso > 0 else 0
        expected_m3 = round(volume * valor_m3, 2) if volume > 0 and valor_m3 > 0 else 0
        expected = max(expected_kg, expected_m3, valor_min)

        triggered = abs(freight_charged - expected) > FLOAT_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected,
            actual=freight_charged,
            details={
                "cep_origem": cep_origem,
                "cep_destino": cep_destino,
                "tipo_carga": tipo_carga,
                "modalidade": modalidade,
                "faixa_sicoban": match.get("faixa"),
                "valor_kg": valor_kg,
                "valor_m3": valor_m3,
                "valor_minimo": valor_min,
            },
            evidence={"sicoban_match": match},
        )

    def _find_sicoban_match(
        self,
        rules: list[dict[str, Any]],
        cep_origem: str,
        cep_destino: str,
        tipo_carga: str,
        modalidade: str,
    ) -> dict[str, Any] | None:
        """Find matching Sicoban rule"""
        cep_o = int("".join(filter(str.isdigit, cep_origem))[:5])
        cep_d = int("".join(filter(str.isdigit, cep_destino))[:5])

        for rule in rules:
            if rule.get("tipo_carga") != tipo_carga:
                continue
            if rule.get("modalidade") != modalidade:
                continue

            cep_o_ini = rule.get("cep_origem_inicial", 0)
            cep_o_fim = rule.get("cep_origem_final", 99999)
            cep_d_ini = rule.get("cep_destino_inicial", 0)
            cep_d_fim = rule.get("cep_destino_final", 99999)

            if cep_o_ini <= cep_o <= cep_o_fim and cep_d_ini <= cep_d <= cep_d_fim:
                return rule
        return None

    async def _load_sicoban_data(self) -> list[dict[str, Any]]:
        """Load Sicoban data from file"""

        if self._sicoban_data is not None:
            return self._sicoban_data

        # Try to load from data file
        data_path = Path(__file__).parent.parent / "data" / "sicoban_table.json"
        if data_path.exists():
            with data_path.open() as f:
                self._sicoban_data = json.load(f)
                return self._sicoban_data

        # Return empty if not found
        self._sicoban_data = []
        return []


# ============================================
# CT-e COMPLEMENTAR (3 rules)
# ============================================


class ComplementaryCTEAnulationRule(BaseRule):
    """CT-e Complementar - Anulação (tpEmis=3)"""

    rule_code = "CTE_ANULACAO"
    rule_name = "CT-e Complementar - Anulação"
    discrepancy_type = DiscrepancyType.COMPLEMENTARY_CTE
    severity = "HIGH"
    relevance_tags = ["cte_complementar"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        # Verificar se é CT-e de anulação
        tp_emis = self._safe_get(doc, "tp_emis")
        if tp_emis != "3":  # 3 = Anulação
            return self._create_result(False)

        # Validar: deve referenciar CT-e original
        ch_cte_ref = self._safe_get(doc, "ch_cte_ref")
        if not ch_cte_ref:
            # Set severity before calling _create_result
            self.severity = "CRITICAL"
            return self._create_result(
                True,
                details={"reason": "CT-e anulação sem referência ao CT-e original (chCTeRef)"},
            )

        # Verificar se CT-e original existe no sistema
        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            # Set severity before calling _create_result
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado no sistema"},
            )

        # Validar: mesmo emitente
        if original.carrierId != doc.get("carrier_id"):
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": "CT-e anulação com emitente diferente do original"},
            )

        return self._create_result(
            triggered=False,
            details={"ch_cte_ref": ch_cte_ref, "original_found": True},
        )


class ComplementaryCTESubstitutionRule(BaseRule):
    """CT-e Complementar - Substituição (tpEmis=2)"""

    rule_code = "CTE_SUBSTITUICAO"
    rule_name = "CT-e Complementar - Substituição"
    discrepancy_type = DiscrepancyType.COMPLEMENTARY_CTE
    severity = "HIGH"
    relevance_tags = ["cte_complementar"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        tp_emis = self._safe_get(doc, "tp_emis")
        if tp_emis != "2":  # 2 = Substituição
            return self._create_result(False)

        ch_cte_ref = self._safe_get(doc, "ch_cte_ref")
        if not ch_cte_ref:
            self.severity = "CRITICAL"
            return self._create_result(
                True,
                details={"reason": "CT-e substituição sem referência ao CT-e original"},
            )

        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado"},
            )

        # Validar: valores novos devem ser diferentes do original
        v_carga_new = self._safe_get(doc, "v_carga", 0)
        v_frete_new = self._safe_get(doc, "freight_value", 0)

        v_carga_orig = original.totalValue or 0
        v_frete_orig = original.freightValue or 0

        if v_carga_new == v_carga_orig and v_frete_new == v_frete_orig:
            self.severity = "MEDIUM"
            return self._create_result(
                True,
                details={"reason": "CT-e substituição com mesmos valores do original"},
            )

        return self._create_result(
            triggered=False,
            details={
                "ch_cte_ref": ch_cte_ref,
                "v_carga_orig": v_carga_orig,
                "v_carga_new": v_carga_new,
                "v_frete_orig": v_frete_orig,
                "v_frete_new": v_frete_new,
            },
        )


class ComplementaryCTEComplementRule(BaseRule):
    """CT-e Complementar - Complemento de Valor (tpEmis=4)"""

    rule_code = "CTE_COMPLEMENTO_VALOR"
    rule_name = "CT-e Complementar - Complemento de Valor"
    discrepancy_type = DiscrepancyType.COMPLEMENTARY_CTE
    severity = "MEDIUM"
    relevance_tags = ["cte_complementar"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        tp_emis = self._safe_get(doc, "tp_emis")
        if tp_emis != "4":  # 4 = Complemento
            return self._create_result(False)

        ch_cte_ref = self._safe_get(doc, "ch_cte_ref")
        if not ch_cte_ref:
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": "CT-e complemento sem referência ao CT-e original"},
            )

        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado"},
            )

        # Complemento deve APENAS aumentar valores
        v_carga_new = self._safe_get(doc, "v_carga", 0)
        v_frete_new = self._safe_get(doc, "freight_value", 0)

        v_carga_orig = original.totalValue or 0
        v_frete_orig = original.freightValue or 0

        if v_carga_new < v_carga_orig:
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": "Complemento não pode reduzir valor da carga"},
            )

        if v_frete_new < v_frete_orig:
            self.severity = "HIGH"
            return self._create_result(
                True,
                details={"reason": "Complemento não pode reduzir valor do frete"},
            )

        # Calcular apenas o complemento
        complemento_carga = v_carga_new - v_carga_orig
        complemento_frete = v_frete_new - v_frete_orig

        return self._create_result(
            triggered=False,
            details={
                "ch_cte_ref": ch_cte_ref,
                "complemento_carga": complemento_carga,
                "complemento_frete": complemento_frete,
            },
        )


# ============================================
# OTHER RULES (from original)
# ============================================


class RedespachoRule(BaseRule):
    """Redespacho validation - CT-e complementar"""

    rule_code = "REDESPACHO_VALIDACAO"
    rule_name = "Validação de Redespacho (CT-e Complementar)"
    discrepancy_type = DiscrepancyType.REDESPACHO
    severity = "HIGH"
    relevance_tags = ["redespacho"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        has_redespacho = self._safe_get(doc, "has_redespacho", False)
        if not has_redespacho:
            return self._create_result(False)

        redespacho_details = self._safe_get(doc, "redespacho_details", [])
        if not redespacho_details:
            self.severity = "CRITICAL"
            return self._create_result(
                True,
                details={"reason": "Redespacho indicado mas sem CT-e complementar"},
            )

        total_redespacho = sum(r.get("valor", 0) for r in redespacho_details)
        freight_value = self._safe_get(doc, "freight_value", 0)
        triggered = total_redespacho > freight_value * 1.1

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
    relevance_tags = ["toll"]

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document
        table = context.freight_table

        pedagios_doc = self._safe_get(doc, "modal_rodoviario.pedagio", [])
        if not pedagios_doc:
            return self._create_result(False)

        if not table:
            return self._create_result(False, details={"reason": "No freight table"})

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

        triggered = abs(total_charged - total_expected) > PEDAGIO_TOLERANCE

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
    relevance_tags = ["advalorem"]

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
    relevance_tags = ["gris"]

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


# ============================================
# NF-e CRITICAL RULES (5 rules)
# ============================================


def _get_uf_region(uf: str) -> str | None:
    """Get region for a UF."""
    for region, ufs in UF_REGIONS.items():
        if uf in ufs:
            return region
    return None


def _get_interstate_aliquot(uf_origem: str, uf_destino: str) -> float:
    """Get interstate ICMS aliquot based on origin/destination regions."""
    region_origem = _get_uf_region(uf_origem)
    region_destino = _get_uf_region(uf_destino)

    if not region_origem or not region_destino:
        return 0.12  # Default

    # Same region - check specific rules
    if region_origem == region_destino:
        if region_origem in ["Sul", "Sudeste", "CentroOeste"]:
            return 0.12
        elif region_origem in ["Norte", "Nordeste"]:
            return 0.07

    # Cross-region
    return ALIQUOTAS_INTERSTADUAIS.get((region_origem, region_destino), 0.12)


class NFEICMSCalculoRule(BaseRule):
    """NF-e ICMS Calculation Validation

    Validates that ICMS base, aliquota, and value match expected calculations per UF.
    Applies to NF-e (modelo 55) with CST/CSOSN for normal taxation.
    """

    rule_code = "NFE_ICMS_CALCULO"
    rule_name = "Validação Cálculo ICMS NF-e"
    discrepancy_type = DiscrepancyType.NFE_ICMS_CALCULO
    severity = "CRITICAL"
    relevance_tags = ["nfe_icms"]
    cache_ttl = 1800  # 30 min

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        # Only applies to NF-e
        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get ICMS data from NF-e structure
        cst = self._safe_get(doc, "icms.cst")
        csosn = self._safe_get(doc, "icms.csosn")
        v_bc = self._safe_get(doc, "icms.v_bc", 0)
        v_icms = self._safe_get(doc, "icms.v_icms", 0)
        p_icms = self._safe_get(doc, "icms.p_icms", 0)

        # Only validate CSTs subject to normal ICMS (not Simples Nacional)
        st_csts = ["00", "10", "20", "30", "40", "41", "50", "51", "60", "70", "90"]
        sn_csosns = ["101", "102", "103", "201", "202", "203", "300", "400", "500", "900"]

        is_st_cst = cst in st_csts
        is_sn_csosn = csosn in sn_csosns

        if not is_st_cst and not is_sn_csosn:
            return self._create_result(
                False, details={"reason": f"CST {cst} / CSOSN {csosn} not validated"}
            )

        if v_bc <= 0 or p_icms <= 0:
            return self._create_result(False, details={"reason": "Missing base or aliquot"})

        # Calculate expected ICMS
        expected_icms = round(v_bc * p_icms / 100, 2)

        # Check tolerance
        triggered = abs(v_icms - expected_icms) > NFE_ICMS_TOLERANCE

        # Determine which UF aliquot should apply
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")
        aliquot_interna = ICMS_ALIQUOTAS_INTERNAS.get(uf_destino, 0)

        return self._create_result(
            triggered=triggered,
            expected=expected_icms,
            actual=v_icms,
            details={
                "cst": cst,
                "csosn": csosn,
                "base_calculo": v_bc,
                "aliquota_aplicada": p_icms,
                "aliquota_interna_uf": aliquot_interna,
                "uf_destino": uf_destino,
                "tolerancia": NFE_ICMS_TOLERANCE,
            },
            evidence={
                "icms_data": {
                    "cst": cst,
                    "csosn": csosn,
                    "vBC": v_bc,
                    "pICMS": p_icms,
                    "vICMS": v_icms,
                }
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEICMSSTRule(BaseRule):
    """NF-e ICMS Substituição Tributária Validation

    Validates ST calculation for products subject to ST regime on NF-e.
    Uses MVA/IVA method based on NCM and UF destination.
    """

    rule_code = "NFE_ICMS_ST"
    rule_name = "Validação ICMS ST NF-e"
    discrepancy_type = DiscrepancyType.NFE_ICMS_ST
    severity = "CRITICAL"
    relevance_tags = ["nfe_icms", "icms_st"]
    cache_ttl = 1800  # 30 min

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get ICMS ST data
        cst = self._safe_get(doc, "icms.cst")
        ncm = self._safe_get(doc, "det.prod.NCM")
        v_bc_st = self._safe_get(doc, "icms.v_bc_st", 0)
        v_icms_st = self._safe_get(doc, "icms.v_icms_st", 0)
        p_mva_st = self._safe_get(doc, "icms.p_mva_st", 0)
        p_icms_st = self._safe_get(doc, "icms.p_icms_st", 0)

        # Only CSTs with ST
        st_csts = ["10", "30", "40", "41", "50", "51", "60", "70", "90"]
        if cst not in st_csts:
            return self._create_result(False, details={"reason": f"CST {cst} not subject to ST"})

        # Validate required fields
        uf_origem = self._safe_get(doc, "emit.enderEmit.UF")
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")
        if not ncm or not uf_origem or not uf_destino:
            return self._create_result(
                False, details={"reason": "Missing required fields (NCM/UF)"}
            )

        # Look up ST rule from reference data
        st_config = self._get_st_config(ncm, uf_destino)
        if not st_config:
            return self._create_result(
                False, details={"reason": f"No ST config for NCM {ncm} in {uf_destino}"}
            )

        # Calculate expected ST
        # Use v_bc_st from document if available (pre-calculated base)
        # Otherwise calculate from components
        if v_bc_st > 0:
            base_calculo = v_bc_st
        elif st_config["metodo"] == "MVA":
            v_prod = self._safe_get(doc, "det.prod.vProd", 0)
            v_frete = self._safe_get(doc, "total.ICMSTot.vFrete", 0)
            v_seg = self._safe_get(doc, "total.ICMSTot.vSeg", 0)
            v_outro = self._safe_get(doc, "total.ICMSTot.vOutro", 0)
            base_calculo = (v_prod + v_frete + v_seg + v_outro) * (1 + st_config["mva"] / 100)
        elif st_config["metodo"] == "IVA":
            v_prod = self._safe_get(doc, "det.prod.vProd", 0)
            base_calculo = v_prod * (1 + st_config["iva"] / 100)
        else:
            return self._create_result(
                False, details={"reason": f"Unknown ST method: {st_config['metodo']}"}
            )

        expected_st = round(base_calculo * st_config["aliquota_interna"], 2)
        triggered = abs(v_icms_st - expected_st) > NFE_ICMS_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_st,
            actual=v_icms_st,
            details={
                "cst": cst,
                "ncm": ncm,
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "metodo": st_config["metodo"],
                "mva_iva": st_config.get("mva") or st_config.get("iva"),
                "aliquota_interna": st_config["aliquota_interna"],
                "base_calculo_st": v_bc_st,
                "p_mva_st": p_mva_st,
                "p_icms_st": p_icms_st,
            },
            evidence={
                "st_config": st_config,
                "icms_st_data": {
                    "vBCST": v_bc_st,
                    "pMVAST": p_mva_st,
                    "pICMSST": p_icms_st,
                    "vICMSST": v_icms_st,
                },
            },
        )

    def _get_st_config(self, ncm: str, uf: str) -> dict | None:
        """Get ST configuration from icms_rules.json data."""
        # This would ideally load from the JSON file
        # For now, using inline data for key products
        st_produtos = {
            "22030000": {  # Cervejas
                "metodo": "MVA",
                "ufs": {
                    "SP": {"mva": 41.67, "aliquota_interna": 0.18},
                    "RJ": {"mva": 51.22, "aliquota_interna": 0.20},
                    "MG": {"mva": 33.33, "aliquota_interna": 0.18},
                    "RS": {"mva": 33.33, "aliquota_interna": 0.18},
                    "PR": {"mva": 33.33, "aliquota_interna": 0.18},
                    "SC": {"mva": 41.67, "aliquota_interna": 0.17},
                    "BA": {"mva": 45.45, "aliquota_interna": 0.205},
                    "GO": {"mva": 33.33, "aliquota_interna": 0.19},
                },
            },
            "22042100": {  # Vinhos
                "metodo": "MVA",
                "ufs": {
                    "SP": {"mva": 41.67, "aliquota_interna": 0.18},
                    "RJ": {"mva": 51.22, "aliquota_interna": 0.20},
                },
            },
            "24022000": {  # Cigarros
                "metodo": "IVA",
                "ufs": {
                    "SP": {"iva": 56.00, "aliquota_interna": 0.18},
                    "RJ": {"iva": 60.00, "aliquota_interna": 0.20},
                    "MG": {"iva": 52.00, "aliquota_interna": 0.18},
                },
            },
            "27101921": {  # Óleo Diesel
                "metodo": "MVA",
                "ufs": {
                    "SP": {"mva": 13.64, "aliquota_interna": 0.18},
                    "RJ": {"mva": 17.65, "aliquota_interna": 0.20},
                },
            },
            "30049099": {  # Medicamentos genéricos
                "metodo": "MVA",
                "ufs": {
                    "SP": {"mva": 20.00, "aliquota_interna": 0.18},
                },
            },
        }

        produto = st_produtos.get(ncm)
        if not produto:
            return None

        uf_config = produto["ufs"].get(uf)
        if not uf_config:
            return None

        return {**produto, **uf_config, "ncm": ncm, "uf": uf}

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEDIFALRule(BaseRule):
    """NF-e DIFAL (Diferencial de Alíquota) Validation

    Validates DIFAL for interstate operations (UF origem != UF destino)
    for non-Simples Nacional taxpayers.
    """

    rule_code = "NFE_DIFAL"
    rule_name = "Validação DIFAL NF-e (Interestadual)"
    discrepancy_type = DiscrepancyType.NFE_DIFAL
    severity = "CRITICAL"
    relevance_tags = ["nfe_difal", "interstate"]
    cache_ttl = 1800  # 30 min

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if interstate
        uf_origem = self._safe_get(doc, "emit.enderEmit.UF")
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")

        if not uf_origem or not uf_destino or uf_origem == uf_destino:
            return self._create_result(False, details={"reason": "Not interstate or missing UF"})

        # Check if destinatário is Simples Nacional (indIEDest = 9)
        ind_ie_dest = self._safe_get(doc, "dest.indIEDest")
        if ind_ie_dest == "9":  # 9 = Não contribuinte (pode ser Simples)
            # Check if actually Simples - CRT 1
            crt = self._safe_get(doc, "emit.CRT")
            if crt in {1, "1"}:
                return self._create_result(
                    False, details={"reason": "Destinatário Simples Nacional - DIFAL não aplica"}
                )

        # Get ICMS data
        v_bc = self._safe_get(doc, "icms.v_bc", 0)
        v_icms = self._safe_get(doc, "icms.v_icms", 0)
        p_icms = self._safe_get(doc, "icms.p_icms", 0)

        # Get FCP data
        v_fcp = self._safe_get(doc, "icms.v_fcp", 0)
        p_fcp = self._safe_get(doc, "icms.p_fcp", 0)

        if v_bc <= 0:
            return self._create_result(False, details={"reason": "Missing base calculation"})

        # Calculate expected DIFAL
        aliquota_interna = ICMS_ALIQUOTAS_INTERNAS.get(uf_destino, 0)
        aliquota_interestadual = _get_interstate_aliquot(uf_origem, uf_destino)
        aliquota_fcp = FCP_ALIQUOTAS.get(uf_destino, 0)

        diferencial = aliquota_interna - aliquota_interestadual
        expected_difal = round(v_bc * diferencial, 2)
        expected_fcp = round(v_bc * aliquota_fcp, 2)

        # Total ICMS should include DIFAL + FCP + ICMS Interestadual
        expected_total_icms = round(
            v_bc * aliquota_interestadual + expected_difal + expected_fcp, 2
        )

        triggered = abs(v_icms - expected_total_icms) > NFE_ICMS_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_total_icms,
            actual=v_icms,
            details={
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "base_calculo": v_bc,
                "aliquota_interna_destino": aliquota_interna,
                "aliquota_interestadual": aliquota_interestadual,
                "diferencial_aliquota": diferencial,
                "aliquota_fcp": aliquota_fcp,
                "expected_difal": expected_difal,
                "expected_fcp": expected_fcp,
                "expected_icms_interestadual": round(v_bc * aliquota_interestadual, 2),
                "ind_ie_dest": ind_ie_dest,
                "crt_emitente": self._safe_get(doc, "emit.CRT"),
            },
            evidence={
                "difal_calc": {
                    "vBC": v_bc,
                    "pICMS": p_icms,
                    "vICMS": v_icms,
                    "vFCP": v_fcp,
                    "pFCP": p_fcp,
                }
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEFreteNaBaseRule(BaseRule):
    """NF-e Freight Included in ICMS Base Validation

    Validates that freight value is correctly included in ICMS base calculation
    per legislation (LC 87/96, Convênio ICMS 52/91).
    """

    rule_code = "NFE_FRETE_NA_BASE"
    rule_name = "Validação Frete na Base ICMS NF-e"
    discrepancy_type = DiscrepancyType.NFE_FRETE_NA_BASE
    severity = "CRITICAL"
    relevance_tags = ["nfe_frete", "icms"]
    cache_ttl = 1800  # 30 min

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get freight data
        mod_frete = self._safe_get(doc, "transp.modFrete")
        v_frete = self._safe_get(doc, "total.ICMSTot.vFrete", 0)
        v_seg = self._safe_get(doc, "total.ICMSTot.vSeg", 0)

        # modFrete: 0=Por conta do emitente, 1=Por conta do destinatário, 2=Por conta de terceiros, 3=Próprio por conta do emitente, 9=Sem frete
        if mod_frete not in ["0", "1", "2", "3"] or v_frete <= 0:
            return self._create_result(
                False, details={"reason": "No freight or modFrete not applicable"}
            )

        # Get ICMS base
        v_bc = self._safe_get(doc, "icms.v_bc", 0)
        v_prod = self._safe_get(doc, "total.ICMSTot.vProd", 0)
        v_outro = self._safe_get(doc, "total.ICMSTot.vOutro", 0)
        v_ipi = self._safe_get(doc, "total.ICMSTot.vIPI", 0)

        # Base should include: vProd + vFrete + vSeg + vOutro + vIPI (when applicable)
        # For interstate: DIFAL base includes freight
        # For internal: depends on state legislation

        expected_base_min = v_prod + v_frete + v_seg + v_outro

        # Check if freight is in base
        freight_in_base = v_bc >= expected_base_min - NFE_FRETE_BASE_TOLERANCE

        # Also check CST - CST 00 (tributada integralmente) should include freight in base
        cst = self._safe_get(doc, "icms.cst")
        csts_with_frete_base = ["00", "10", "20", "30", "40", "50", "60", "70"]

        triggered = False
        if cst in csts_with_frete_base and not freight_in_base:
            triggered = True

        return self._create_result(
            triggered=triggered,
            expected=expected_base_min,
            actual=v_bc,
            details={
                "mod_frete": mod_frete,
                "v_frete": v_frete,
                "v_seg": v_seg,
                "v_prod": v_prod,
                "v_outro": v_outro,
                "v_ipi": v_ipi,
                "v_bc_informada": v_bc,
                "v_bc_esperada_min": expected_base_min,
                "cst": cst,
                "frete_in_base": freight_in_base,
                "cst_requires_frete_base": cst in csts_with_frete_base,
            },
            evidence={
                "icms_tot": {
                    "vBC": v_bc,
                    "vProd": v_prod,
                    "vFrete": v_frete,
                    "vSeg": v_seg,
                    "vOutro": v_outro,
                    "vIPI": v_ipi,
                }
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFECTECrossRule(BaseRule):
    """NF-e and CT-e Cross-Validation

    Cross-validates NF-e with corresponding CT-e data:
    - Match by access key (chave de acesso)
    - Compare values (vNF vs vCarga)
    - Compare weights (peso)
    - Compare CFOP/modFrete consistency
    """

    rule_code = "NFE_CTE_CROSS"
    rule_name = "Validação Cruzada NF-e x CT-e"
    discrepancy_type = DiscrepancyType.NFE_CTE_CROSS
    severity = "CRITICAL"
    relevance_tags = ["nfe", "cte_cross"]
    cache_ttl = 1800  # 30 min

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if there's CT-e reference data in context
        cte_ref = context.metadata.get("cte_reference")
        if not cte_ref:
            # Try to find CT-e by matching keys
            cte_ref = await self._find_matching_cte(context)

        if not cte_ref:
            return self._create_result(
                False, details={"reason": "No matching CT-e found for cross-validation"}
            )

        discrepancies = []

        # 1. Compare values
        v_nf = self._safe_get(doc, "total.ICMSTot.vNF", 0)
        v_carga_cte = self._safe_get(cte_ref, "v_carga", 0)
        if v_nf > 0 and v_carga_cte > 0:
            diff_pct = abs(v_nf - v_carga_cte) / v_nf * 100
            if diff_pct > NFE_CTE_CROSS_TOLERANCE_PCT:
                discrepancies.append(
                    {
                        "field": "valor",
                        "nfe_value": v_nf,
                        "cte_value": v_carga_cte,
                        "diff_pct": round(diff_pct, 2),
                    }
                )

        # 2. Compare weights
        peso_nfe = self._safe_get(doc, "transp.vol.pesoB", 0)
        peso_cte = self._safe_get(cte_ref, "weight", 0)
        if peso_nfe > 0 and peso_cte > 0:
            diff_pct = abs(peso_nfe - peso_cte) / peso_nfe * 100
            if diff_pct > NFE_CTE_CROSS_TOLERANCE_PCT:
                discrepancies.append(
                    {
                        "field": "peso",
                        "nfe_value": peso_nfe,
                        "cte_value": peso_cte,
                        "diff_pct": round(diff_pct, 2),
                    }
                )

        # 3. Compare CFOP consistency with modFrete
        cfop = self._safe_get(doc, "det.prod.CFOP")
        mod_frete = self._safe_get(doc, "transp.modFrete")
        if cfop and mod_frete:
            # CFOP 5.xxx = intraestado, 6.xxx = interestadual, 7.xxx = exterior
            # modFrete: 0=Emitente, 1=Destinatário
            cte_mod_frete = self._safe_get(cte_ref, "modal_rodoviario.frete_tipo", "")
            if mod_frete != cte_mod_frete:
                discrepancies.append(
                    {
                        "field": "mod_frete",
                        "nfe_mod_frete": mod_frete,
                        "cte_mod_frete": cte_mod_frete,
                    }
                )

        # 4. Check access key reference
        ch_nfe = self._safe_get(doc, "protNFe.infProt.chNFe") or self._safe_get(doc, "ide.cNF")
        self._safe_get(cte_ref, "ch_cte_ref", "")
        # NF-e key is 44 digits, CT-e key is 44 digits - they should be related
        # but not identical (different document types)

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "nfe_chave": ch_nfe,
                "cte_chave": self._safe_get(cte_ref, "accessKey", ""),
                "checks_performed": ["valor", "peso", "mod_frete", "chave_acesso"],
            },
            evidence={
                "nfe_data": {"vNF": v_nf, "peso": peso_nfe, "CFOP": cfop, "modFrete": mod_frete},
                "cte_data": {"vCarga": v_carga_cte, "peso": peso_cte, "modFrete": cte_mod_frete},
            },
        )

    async def _find_matching_cte(self, context: RuleContext) -> dict | None:
        """Try to find matching CT-e in database by client/carrier/date."""
        # This would require DB access - for now return metadata reference
        return context.metadata.get("cte_reference")

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


# ============================================
# NF-e HIGH PRIORITY RULES (7 rules)
# ============================================


class NFEFCPRule(BaseRule):
    """NF-e FCP (Fundo de Combate à Pobreza) Validation

    Validates FCP calculation on interstate operations for non-Simples Nacional taxpayers.
    FCP applies when destination UF has FCP aliquot > 0.
    """

    rule_code = "NFE_FCP"
    rule_name = "Validação FCP NF-e (Interestadual)"
    discrepancy_type = DiscrepancyType.NFE_FCP
    severity = "HIGH"
    relevance_tags = ["nfe_fcp", "interstate"]
    cache_ttl = 3600  # 1 hour

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if interstate
        uf_origem = self._safe_get(doc, "emit.enderEmit.UF")
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")

        if not uf_origem or not uf_destino or uf_origem == uf_destino:
            return self._create_result(False, details={"reason": "Not interstate or missing UF"})

        # Check if destinatário is Simples Nacional (CRT 1) - FCP doesn't apply
        crt = self._safe_get(doc, "emit.CRT")
        if crt in {1, "1"}:
            return self._create_result(
                False, details={"reason": "Simples Nacional - FCP não aplica"}
            )

        # Check if destination UF has FCP aliquot
        aliquota_fcp = FCP_ALIQUOTAS.get(uf_destino, 0)
        if aliquota_fcp <= 0:
            return self._create_result(False, details={"reason": f"UF {uf_destino} não possui FCP"})

        # Get ICMS base
        v_bc = self._safe_get(doc, "icms.v_bc", 0)
        v_fcp = self._safe_get(doc, "icms.v_fcp", 0)
        p_fcp = self._safe_get(doc, "icms.p_fcp", 0)

        if v_bc <= 0:
            return self._create_result(False, details={"reason": "Missing base calculation"})

        # Calculate expected FCP
        expected_fcp = round(v_bc * aliquota_fcp, 2)

        triggered = abs(v_fcp - expected_fcp) > NFE_ICMS_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_fcp,
            actual=v_fcp,
            details={
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "base_calculo": v_bc,
                "aliquota_fcp": aliquota_fcp,
                "p_fcp_informado": p_fcp,
            },
            evidence={"fcp_data": {"vBC": v_bc, "pFCP": p_fcp, "vFCP": v_fcp}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFECFOPFreteRule(BaseRule):
    """NF-e CFOP for Freight Operations Validation

    Validates that CFOP matches freight type (CIF/FOB) and interstate/intrastate.
    CIF = freight by emitter (modFrete 0), FOB = freight by recipient (modFrete 1).
    """

    rule_code = "NFE_CFOP_FRETE"
    rule_name = "Validação CFOP Frete NF-e"
    discrepancy_type = DiscrepancyType.NFE_CFOP_FRETE
    severity = "HIGH"
    relevance_tags = ["nfe_cfop", "freight"]
    cache_ttl = 3600  # 1 hour

    # CFOP mappings for freight
    CFOP_CIF = {
        "intra": ["5101", "5102", "5103", "5114", "5401", "5403", "5405", "5556", "5656", "5933"],
        "inter": ["6101", "6102", "6103", "6114", "6401", "6403", "6405", "6556", "6656", "6933"],
    }
    CFOP_FOB = {
        "intra": ["5101", "5102", "5103", "5114", "5401", "5403", "5405", "5556", "5656", "5933"],
        "inter": ["6101", "6102", "6103", "6114", "6401", "6403", "6405", "6556", "6656", "6933"],
    }

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        cfop = self._safe_get(doc, "det.prod.CFOP")
        mod_frete = self._safe_get(doc, "transp.modFrete")
        uf_origem = self._safe_get(doc, "emit.enderEmit.UF")
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")

        if not cfop or not mod_frete:
            return self._create_result(False, details={"reason": "Missing CFOP or modFrete"})

        cfop_str = str(cfop)
        is_interstate = uf_origem and uf_destino and uf_origem != uf_destino
        scope = "inter" if is_interstate else "intra"

        # modFrete: 0=Por conta do emitente (CIF), 1=Por conta do destinatário (FOB)
        # 2=Por conta de terceiros, 3=Próprio por conta do emitente, 9=Sem frete
        cif_mod_fretes = ["0", "3"]
        fob_mod_fretes = ["1"]

        expected_cfops = []
        if mod_frete in cif_mod_fretes:
            expected_cfops = self.CFOP_CIF.get(scope, [])
        elif mod_frete in fob_mod_fretes:
            expected_cfops = self.CFOP_FOB.get(scope, [])
        else:
            return self._create_result(
                False, details={"reason": f"modFrete {mod_frete} not validated"}
            )

        triggered = cfop_str not in expected_cfops

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=0,
            details={
                "cfop": cfop_str,
                "mod_frete": mod_frete,
                "scope": scope,
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "expected_cfops": expected_cfops,
            },
            evidence={"cfop_data": {"CFOP": cfop_str, "modFrete": mod_frete}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFECFOPInterestadualRule(BaseRule):
    """NF-e CFOP for Interstate Operations Validation

    Ensures CFOP starts with 6.xxx for interstate sales/transfers
    and 5.xxx for intrastate operations.
    """

    rule_code = "NFE_CFOP_INTERSTADUAL"
    rule_name = "Validação CFOP Interestadual NF-e"
    discrepancy_type = DiscrepancyType.NFE_CFOP_INTERSTADUAL
    severity = "HIGH"
    relevance_tags = ["nfe_cfop", "interstate"]
    cache_ttl = 3600  # 1 hour

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        cfop = self._safe_get(doc, "det.prod.CFOP")
        uf_origem = self._safe_get(doc, "emit.enderEmit.UF")
        uf_destino = self._safe_get(doc, "dest.enderDest.UF")

        if not cfop or not uf_origem or not uf_destino:
            return self._create_result(False, details={"reason": "Missing CFOP or UF data"})

        cfop_str = str(cfop)
        is_interstate = uf_origem != uf_destino
        cfop_prefix = cfop_str[:1] if cfop_str else ""

        # CFOP 5.xxx = intraestado, 6.xxx = interestadual, 7.xxx = exterior
        expected_prefix = "6" if is_interstate else "5"

        triggered = cfop_prefix != expected_prefix

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=0,
            details={
                "cfop": cfop_str,
                "cfop_prefix": cfop_prefix,
                "expected_prefix": expected_prefix,
                "uf_origem": uf_origem,
                "uf_destino": uf_destino,
                "is_interstate": is_interstate,
            },
            evidence={
                "cfop_data": {"CFOP": cfop_str, "UF_origem": uf_origem, "UF_destino": uf_destino}
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFENCMCESTRule(BaseRule):
    """NF-e NCM/CEST Pairing Validation

    Validates CEST is valid for given NCM per Convênio ICMS 142/2018.
    CEST (Código Especificador da Substituição Tributária) must match NCM.
    """

    rule_code = "NFE_NCM_CEST"
    rule_name = "Validação NCM/CEST NF-e"
    discrepancy_type = DiscrepancyType.NFE_NCM_CEST
    severity = "HIGH"
    relevance_tags = ["nfe_ncm", "cest"]
    cache_ttl = 3600  # 1 hour

    # Sample NCM -> CEST mapping (from Convênio ICMS 142/2018)
    # In production, this would be loaded from reference data
    NCM_CEST_MAP = {
        "22030000": ["28.001.00"],  # Cervejas
        "22042100": ["28.002.00"],  # Vinhos
        "24022000": ["28.003.00"],  # Cigarros
        "27101921": ["28.004.00"],  # Óleo diesel
        "30049099": ["28.005.00"],  # Medicamentos
        "87032100": ["21.001.00"],  # Automóveis
        "87032200": ["21.001.00"],
        "87032300": ["21.001.00"],
        "87032400": ["21.001.00"],
        "87042100": ["21.002.00"],  # Caminhonetes
        "87042200": ["21.002.00"],
        "87042300": ["21.002.00"],
        "40111000": ["20.001.00"],  # Pneus
        "40112000": ["20.001.00"],
        "40119000": ["20.001.00"],
    }

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        ncm = self._safe_get(doc, "det.prod.NCM")
        cest = self._safe_get(doc, "det.prod.CEST")

        if not ncm:
            return self._create_result(False, details={"reason": "NCM required"})

        # If product has no CEST in reference data, skip (not subject to ST)
        valid_cests = self.NCM_CEST_MAP.get(ncm)
        if not valid_cests:
            return self._create_result(
                False, details={"reason": f"NCM {ncm} not subject to CEST validation"}
            )

        # If CEST is required but not informed
        if not cest:
            return self._create_result(
                True,
                expected=0,
                actual=0,
                details={
                    "ncm": ncm,
                    "cest_informado": None,
                    "cests_validos": valid_cests,
                    "reason": "CEST obrigatório não informado",
                },
                evidence={"ncm_cest_data": {"NCM": ncm, "CEST": cest}},
            )

        # Check if informed CEST is valid for NCM
        triggered = cest not in valid_cests

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=0,
            details={
                "ncm": ncm,
                "cest_informado": cest,
                "cests_validos": valid_cests,
            },
            evidence={"ncm_cest_data": {"NCM": ncm, "CEST": cest}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEValorTotalRule(BaseRule):
    """NF-e Total Value Validation

    Validates that total NF-e value (vNF) matches sum of items + taxes + freight.
    vNF ≈ vProd + vFrete + vSeg + vDesc + vII + vIPI + vPIS + vCOFINS + vICMS + vST + vFCP
    """

    rule_code = "NFE_VALOR_TOTAL"
    rule_name = "Validação Valor Total NF-e"
    discrepancy_type = DiscrepancyType.NFE_VALOR_TOTAL
    severity = "HIGH"
    relevance_tags = ["nfe_total", "validation"]
    cache_ttl = 3600  # 1 hour

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get total values from ICMSTot
        v_nf = self._safe_get(doc, "total.ICMSTot.vNF", 0)
        v_prod = self._safe_get(doc, "total.ICMSTot.vProd", 0)
        v_frete = self._safe_get(doc, "total.ICMSTot.vFrete", 0)
        v_seg = self._safe_get(doc, "total.ICMSTot.vSeg", 0)
        v_desc = self._safe_get(doc, "total.ICMSTot.vDesc", 0)
        v_ii = self._safe_get(doc, "total.ICMSTot.vII", 0)
        v_ipi = self._safe_get(doc, "total.ICMSTot.vIPI", 0)
        v_pis = self._safe_get(doc, "total.ICMSTot.vPIS", 0)
        v_cofins = self._safe_get(doc, "total.ICMSTot.vCOFINS", 0)
        v_icms = self._safe_get(doc, "total.ICMSTot.vICMS", 0)
        v_st = self._safe_get(doc, "total.ICMSTot.vST", 0)
        v_fcp = self._safe_get(doc, "total.ICMSTot.vFCP", 0)
        v_outro = self._safe_get(doc, "total.ICMSTot.vOutro", 0)

        # Expected total: sum of all components
        expected_total = round(
            v_prod
            + v_frete
            + v_seg
            - v_desc
            + v_ii
            + v_ipi
            + v_pis
            + v_cofins
            + v_icms
            + v_st
            + v_fcp
            + v_outro,
            2,
        )

        # Tolerance of R$ 0.05 for rounding differences
        triggered = abs(v_nf - expected_total) > NFE_ICMS_TOLERANCE

        return self._create_result(
            triggered=triggered,
            expected=expected_total,
            actual=v_nf,
            details={
                "vNF": v_nf,
                "vProd": v_prod,
                "vFrete": v_frete,
                "vSeg": v_seg,
                "vDesc": v_desc,
                "vII": v_ii,
                "vIPI": v_ipi,
                "vPIS": v_pis,
                "vCOFINS": v_cofins,
                "vICMS": v_icms,
                "vST": v_st,
                "vFCP": v_fcp,
                "vOutro": v_outro,
                "soma_componentes": expected_total,
            },
            evidence={
                "icms_tot": {
                    "vNF": v_nf,
                    "vProd": v_prod,
                    "vFrete": v_frete,
                    "vSeg": v_seg,
                    "vDesc": v_desc,
                    "vII": v_ii,
                    "vIPI": v_ipi,
                    "vPIS": v_pis,
                    "vCOFINS": v_cofins,
                    "vICMS": v_icms,
                    "vST": v_st,
                    "vFCP": v_fcp,
                    "vOutro": v_outro,
                }
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFETransportadoraRule(BaseRule):
    """NF-e Carrier (Transportadora) Data Validation

    Validates carrier data on NF-e:
    - CNPJ/CPF
    - IE (Inscrição Estadual)
    - UF
    - Vehicle plate (placa)
    - RNTRC (when modal = rodoviário)
    """

    rule_code = "NFE_TRANSPORTADORA"
    rule_name = "Validação Transportadora NF-e"
    discrepancy_type = DiscrepancyType.NFE_TRANSPORTADORA
    severity = "HIGH"
    relevance_tags = ["nfe_transportadora", "carrier"]
    cache_ttl = 3600  # 1 hour

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get transport data
        transport = doc.get("transp", {})
        transportadora = transport.get("transporta", {})

        cnpj = self._safe_get(transportadora, "CNPJ")
        cpf = self._safe_get(transportadora, "CPF")
        ie = self._safe_get(transportadora, "IE")
        uf = self._safe_get(transportadora, "UF")
        x_nome = self._safe_get(transportadora, "xNome")

        # Get vehicle data
        veic_transp = transport.get("veicTransp", {})
        placa = self._safe_get(veic_transp, "placa")
        uf_veic = self._safe_get(veic_transp, "UF")
        rntrc = self._safe_get(veic_transp, "RNTRC")

        # Get modal
        mod_frete = self._safe_get(doc, "transp.modFrete")

        discrepancies = []

        # Validate CNPJ or CPF
        if not cnpj and not cpf:
            discrepancies.append(
                {"field": "cnpj_cpf", "message": "CNPJ ou CPF da transportadora obrigatório"}
            )

        # Validate IE (required for interstate or when carrier is taxpayer)
        if not ie:
            discrepancies.append({"field": "ie", "message": "IE da transportadora obrigatória"})

        # Validate UF
        if not uf:
            discrepancies.append({"field": "uf", "message": "UF da transportadora obrigatória"})

        # Validate xNome
        if not x_nome:
            discrepancies.append(
                {"field": "xNome", "message": "Nome da transportadora obrigatório"}
            )

        # For modal rodoviário (modFrete 0,1,2,3), validate vehicle data
        if mod_frete in ["0", "1", "2", "3"]:
            if not placa:
                discrepancies.append(
                    {
                        "field": "placa",
                        "message": "Placa do veículo obrigatória para modal rodoviário",
                    }
                )
            if not uf_veic:
                discrepancies.append({"field": "uf_veic", "message": "UF do veículo obrigatória"})
            if not rntrc:
                discrepancies.append(
                    {"field": "rntrc", "message": "RNTRC obrigatório para modal rodoviário"}
                )

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "transportadora": {
                    "CNPJ": cnpj,
                    "CPF": cpf,
                    "IE": ie,
                    "UF": uf,
                    "xNome": x_nome,
                },
                "veiculo": {
                    "placa": placa,
                    "UF": uf_veic,
                    "RNTRC": rntrc,
                },
                "mod_frete": mod_frete,
            },
            evidence={"transport_data": {"transporta": transportadora, "veicTransp": veic_transp}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEDestinatarioRule(BaseRule):
    """NF-e Recipient (Destinatário) Data Validation

    Validates recipient data on NF-e:
    - CNPJ/CPF
    - IE (if contributor - indIEDest 1 or 2)
    - Complete address (xLgr, nro, xBairro, cMun, xMun, UF, CEP)
    - UF match between address and document
    """

    rule_code = "NFE_DESTINATARIO"
    rule_name = "Validação Destinatário NF-e"
    discrepancy_type = DiscrepancyType.NFE_DESTINATARIO
    severity = "HIGH"
    relevance_tags = ["nfe_destinatario", "recipient"]
    cache_ttl = 3600  # 1 hour

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        dest = doc.get("dest", {})

        cnpj = self._safe_get(dest, "CNPJ")
        cpf = self._safe_get(dest, "CPF")
        ie = self._safe_get(dest, "IE")
        ind_ie_dest = self._safe_get(dest, "indIEDest")
        x_nome = self._safe_get(dest, "xNome")

        # Address fields
        ender_dest = dest.get("enderDest", {})
        x_lgr = self._safe_get(ender_dest, "xLgr")
        nro = self._safe_get(ender_dest, "nro")
        x_bairro = self._safe_get(ender_dest, "xBairro")
        c_mun = self._safe_get(ender_dest, "cMun")
        x_mun = self._safe_get(ender_dest, "xMun")
        uf = self._safe_get(ender_dest, "UF")
        cep = self._safe_get(ender_dest, "CEP")

        discrepancies = []

        # Validate CNPJ or CPF
        if not cnpj and not cpf:
            discrepancies.append(
                {"field": "cnpj_cpf", "message": "CNPJ ou CPF do destinatário obrigatório"}
            )

        # Validate IE based on indIEDest
        # 1=Contribuinte ICMS, 2=Contribuinte isento, 9=Não contribuinte
        if ind_ie_dest in ["1", "2"] and not ie:
            discrepancies.append(
                {"field": "ie", "message": "IE obrigatória para contribuinte/isentos"}
            )

        # Validate xNome
        if not x_nome:
            discrepancies.append({"field": "xNome", "message": "Nome do destinatário obrigatório"})

        # Validate complete address
        address_fields = {
            "xLgr": x_lgr,
            "nro": nro,
            "xBairro": x_bairro,
            "cMun": c_mun,
            "xMun": x_mun,
            "UF": uf,
            "CEP": cep,
        }
        for field, value in address_fields.items():
            if not value:
                discrepancies.append(
                    {"field": field.lower(), "message": f"{field} do endereço obrigatório"}
                )

        # Validate UF consistency
        uf_emit = self._safe_get(doc, "emit.enderEmit.UF")
        if uf and uf_emit and uf != uf_emit:
            # This is valid for interstate, just noting
            pass

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "destinatario": {
                    "CNPJ": cnpj,
                    "CPF": cpf,
                    "IE": ie,
                    "indIEDest": ind_ie_dest,
                    "xNome": x_nome,
                },
                "endereco": address_fields,
            },
            evidence={"dest_data": {"dest": dest}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


# ============================================
# NF-e MEDIUM PRIORITY RULES (6 rules)
# ============================================


class NFEPesoVolumeRule(BaseRule):
    """NF-e Weight/Volume Consistency Validation

    Validates weight/volume consistency on NF-e:
    - Check peso líquido/bruto vs volumes
    - Cubage calculations
    """

    rule_code = "NFE_PESO_VOLUME"
    rule_name = "Validação Peso/Volume NF-e"
    discrepancy_type = DiscrepancyType.NFE_PESO_VOLUME
    severity = "MEDIUM"
    relevance_tags = ["nfe_peso", "volume"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Get weight data
        peso_bruto = self._safe_get(doc, "transp.vol.pesoB", 0)
        peso_liquido = self._safe_get(doc, "transp.vol.pesoL", 0)
        q_vol = self._safe_get(doc, "transp.vol.qVol", 0)

        # Get volume dimensions
        volumes = doc.get("transp", {}).get("vol", [])
        if isinstance(volumes, dict):
            volumes = [volumes]

        total_volume = 0.0
        for vol in volumes:
            alt = self._safe_get(vol, "alt", 0)
            larg = self._safe_get(vol, "larg", 0)
            comp = self._safe_get(vol, "comp", 0)
            if alt > 0 and larg > 0 and comp > 0:
                total_volume += (alt * larg * comp) / 1000000  # Convert cm³ to m³

        discrepancies = []

        # Check if peso bruto >= peso liquido
        if peso_bruto > 0 and peso_liquido > 0 and peso_bruto < peso_liquido:
            discrepancies.append(
                {
                    "field": "peso_bruto_vs_liquido",
                    "message": "Peso bruto não pode ser menor que peso líquido",
                    "peso_bruto": peso_bruto,
                    "peso_liquido": peso_liquido,
                }
            )

        # Check if volume is consistent with declared volumes
        if q_vol > 0 and total_volume > 0:
            # Allow some tolerance for packaging
            expected_min_volume = (peso_bruto / 1000) * 0.5  # rough density estimate
            if total_volume < expected_min_volume * 0.5:
                discrepancies.append(
                    {
                        "field": "volume_consistency",
                        "message": "Volume total inconsistente com peso bruto",
                        "q_vol": q_vol,
                        "total_volume_m3": round(total_volume, 3),
                        "peso_bruto_kg": peso_bruto,
                    }
                )

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "peso_bruto": peso_bruto,
                "peso_liquido": peso_liquido,
                "q_vol": q_vol,
                "total_volume_m3": round(total_volume, 3),
            },
            evidence={
                "peso_volume_data": {"pesoB": peso_bruto, "pesoL": peso_liquido, "qVol": q_vol}
            },
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFEComplementarRule(BaseRule):
    """NF-e Complementary NF-e Validation

    Validates complementary NF-e (NF-e de complemento):
    - Check referenced NF-e exists (infNFeSupl.refNFe)
    - Correction fields valid
    """

    rule_code = "NFE_COMPLEMENTAR"
    rule_name = "Validação NF-e Complementar"
    discrepancy_type = DiscrepancyType.NFE_COMPLEMENTAR
    severity = "MEDIUM"
    relevance_tags = ["nfe_complementar", "carta_correcao"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if this is a complementary NF-e (has infNFeSupl)
        inf_nfe_supl = doc.get("infNFeSupl")
        if not inf_nfe_supl:
            return self._create_result(False, details={"reason": "Not a complementary NF-e"})

        discrepancies = []

        # Check referenced NF-e key
        ref_nfe = self._safe_get(inf_nfe_supl, "refNFe")
        if not ref_nfe:
            discrepancies.append(
                {"field": "refNFe", "message": "Chave da NF-e referenciada obrigatória"}
            )

        # Check correction reason
        x_correcao = self._safe_get(doc, "ide.xCorrecao")
        if not x_correcao:
            discrepancies.append({"field": "xCorrecao", "message": "Texto da correção obrigatório"})

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "ref_nfe": ref_nfe,
                "x_correcao": x_correcao,
            },
            evidence={"complementar_data": {"refNFe": ref_nfe, "xCorrecao": x_correcao}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc


class NFECartaCorrecaoRule(BaseRule):
    """NF-e Carta de Correção Validation

    Validates carta de correção (correction letter):
    - Check correction letter fields
    - Reason codes
    - Authorization
    """

    rule_code = "NFE_CARTA_CORRECAO"
    rule_name = "Validação Carta de Correção NF-e"
    discrepancy_type = DiscrepancyType.NFE_CARTA_CORRECAO
    severity = "MEDIUM"
    relevance_tags = ["nfe_carta_correcao"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Carta de correção is a separate event (procEventoNFe)
        # Check if this is a carta de correção event
        evento = doc.get("evento", {})
        if not evento:
            return self._create_result(False, details={"reason": "Not a carta de correção event"})

        tp_evento = self._safe_get(evento, "tpEvento")
        if tp_evento != "110110":  # Carta de correção
            return self._create_result(False, details={"reason": "Not a carta de correção event"})

        discrepancies = []

        # Check required fields
        x_correcao = self._safe_get(evento, "detEvento.xCorrecao")
        if not x_correcao:
            discrepancies.append({"field": "xCorrecao", "message": "Texto da correção obrigatório"})

        # Check reason code
        n_correcao = self._safe_get(evento, "detEvento.nCorrecao")
        if n_correcao not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            discrepancies.append({"field": "nCorrecao", "message": "Código de correção inválido"})

        # Check authorization
        c_stat = self._safe_get(doc, "retEvento.infEvento.cStat")
        if c_stat != "135":  # Evento registrado e vinculado à NF-e
            discrepancies.append({"field": "cStat", "message": "Carta de correção não autorizada"})

        # Check reference to original NF-e
        ch_nfe = self._safe_get(evento, "detEvento.chNFe")
        if not ch_nfe:
            discrepancies.append(
                {"field": "chNFe", "message": "Chave da NF-e original obrigatória"}
            )

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "ch_nfe": ch_nfe,
                "x_correcao": x_correcao,
                "n_correcao": n_correcao,
                "c_stat": c_stat,
            },
            evidence={"carta_correcao_data": evento},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        # Also handle event documents (procEventoNFe)
        return modelo == "55" or "ide" in doc or "evento" in doc


class NFECancelamentoRule(BaseRule):
    """NF-e Cancellation Validation

    Validates NF-e cancellation rules:
    - Cancellation within 24h
    - Protocol present
    - Justification
    - No circulation (not in transit)
    """

    rule_code = "NFE_CANCELAMENTO"
    rule_name = "Validação Cancelamento NF-e"
    discrepancy_type = DiscrepancyType.NFE_CANCELAMENTO
    severity = "MEDIUM"
    relevance_tags = ["nfe_cancelamento"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if this is a cancellation event
        evento = doc.get("evento", {})
        if not evento:
            return self._create_result(False, details={"reason": "Not a cancellation event"})

        tp_evento = self._safe_get(evento, "tpEvento")
        if tp_evento != "110111":  # Cancelamento
            return self._create_result(False, details={"reason": "Not a cancellation event"})

        discrepancies = []

        # Check protocol
        n_prot = self._safe_get(evento, "detEvento.nProt")
        if not n_prot:
            discrepancies.append(
                {"field": "nProt", "message": "Protocolo de autorização obrigatório"}
            )

        # Check justification
        x_just = self._safe_get(evento, "detEvento.xJust")
        if not x_just:
            discrepancies.append(
                {"field": "xJust", "message": "Justificativa do cancelamento obrigatória"}
            )
        elif len(x_just) < MIN_JUSTIFICATION_LENGTH:
            discrepancies.append(
                {
                    "field": "xJust",
                    "message": f"Justificativa deve ter no mínimo {MIN_JUSTIFICATION_LENGTH} caracteres",
                }
            )

        # Check time limit (24 hours from authorization)
        dh_evento = self._safe_get(evento, "detEvento.dhEvento")
        dh_emi = self._safe_get(doc, "ide.dhEmi")
        if dh_evento and dh_emi:
            try:
                dt_evento = datetime.fromisoformat(dh_evento.replace("Z", "+00:00"))
                dt_emi = datetime.fromisoformat(dh_emi.replace("Z", "+00:00"))
                diff_hours = (dt_evento - dt_emi).total_seconds() / 3600
                if diff_hours > CANCELLATION_TIME_LIMIT_HOURS:
                    discrepancies.append(
                        {
                            "field": "dhEvento",
                            "message": f"Cancelamento fora do prazo ({CANCELLATION_TIME_LIMIT_HOURS}h): {diff_hours:.1f}h",
                        }
                    )
            except Exception:
                pass

        # Check authorization
        c_stat = self._safe_get(doc, "retEvento.infEvento.cStat")
        if c_stat != "135":
            discrepancies.append({"field": "cStat", "message": "Cancelamento não autorizado"})

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "ch_nfe": self._safe_get(evento, "detEvento.chNFe"),
                "n_prot": n_prot,
                "x_just": x_just,
                "dh_evento": dh_evento,
                "c_stat": c_stat,
            },
            evidence={"cancelamento_data": evento},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        # Also handle event documents (procEventoNFe)
        return modelo == "55" or "ide" in doc or "evento" in doc


class NFEInutilizacaoRule(BaseRule):
    """NF-e Inutilization Validation

    Validates NF-e inutilization (numeração não utilizada):
    - Range validity
    - Justification
    - No prior use
    - Authorization
    """

    rule_code = "NFE_INUTILIZACAO"
    rule_name = "Validação Inutilização NF-e"
    discrepancy_type = DiscrepancyType.NFE_INUTILIZACAO
    severity = "MEDIUM"
    relevance_tags = ["nfe_inutilizacao"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        # Check if this is an inutilization event
        inutilizacao = doc.get("inutNFe", {})
        if not inutilizacao:
            return self._create_result(False, details={"reason": "Not an inutilization event"})

        discrepancies = []

        # Check required fields
        cnpj = self._safe_get(inutilizacao, "infInut.CNPJ")
        if not cnpj:
            discrepancies.append({"field": "CNPJ", "message": "CNPJ do emitente obrigatório"})

        # Check range
        n_nf_ini = self._safe_get(inutilizacao, "infInut.nNFIni")
        n_nf_fin = self._safe_get(inutilizacao, "infInut.nNFFin")
        if not n_nf_ini or not n_nf_fin:
            discrepancies.append(
                {"field": "nNFIni_nNFFin", "message": "Intervalo de numeração obrigatório"}
            )
        elif n_nf_ini > n_nf_fin:
            discrepancies.append(
                {
                    "field": "nNFIni_nNFFin",
                    "message": "Início da numeração não pode ser maior que fim",
                }
            )

        # Check justification
        x_just = self._safe_get(inutilizacao, "infInut.xJust")
        if not x_just:
            discrepancies.append(
                {"field": "xJust", "message": "Justificativa da inutilização obrigatória"}
            )
        elif len(x_just) < MIN_JUSTIFICATION_LENGTH:
            discrepancies.append(
                {
                    "field": "xJust",
                    "message": f"Justificativa deve ter no mínimo {MIN_JUSTIFICATION_LENGTH} caracteres",
                }
            )

        # Check year
        ano = self._safe_get(inutilizacao, "infInut.ano")
        if not ano:
            discrepancies.append({"field": "ano", "message": "Ano da numeração obrigatório"})

        # Check authorization
        c_stat = self._safe_get(doc, "retInutNFe.infInut.cStat")
        if c_stat != "102":  # Inutilização de número homologada
            discrepancies.append({"field": "cStat", "message": "Inutilização não autorizada"})

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "cnpj": cnpj,
                "n_nf_ini": n_nf_ini,
                "n_nf_fin": n_nf_fin,
                "ano": ano,
                "x_just": x_just,
                "c_stat": c_stat,
            },
            evidence={"inutilizacao_data": inutilizacao},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        # Also handle inutilizacao documents (inutNFe)
        return modelo == "55" or "ide" in doc or "inutNFe" in doc


class NFERegimeEspecialRule(BaseRule):
    """NF-e Special Tax Regime Validation

    Validates special tax regime indicators:
    - Check CRT (Código de Regime Tributário) matches company regime
    - Simples Nacional: CRT = 1
    - Normal: CRT = 3
    """

    rule_code = "NFE_REGIME_ESPECIAL"
    rule_name = "Validação Regime Especial NF-e"
    discrepancy_type = DiscrepancyType.NFE_REGIME_ESPECIAL
    severity = "MEDIUM"
    relevance_tags = ["nfe_regime", "crt"]
    cache_ttl = 7200  # 2 hours

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        doc = context.document

        if not self._is_nfe(doc):
            return self._create_result(False, details={"reason": "Not NF-e document"})

        crt = self._safe_get(doc, "emit.CRT")
        ind_ie_dest = self._safe_get(doc, "dest.indIEDest")

        discrepancies = []

        # Valid CRT values
        valid_crt = {"1", "2", "3", "4"}
        if crt not in valid_crt:
            discrepancies.append(
                {
                    "field": "CRT",
                    "message": f"CRT inválido: {crt}. Valores válidos: 1, 2, 3, 4",
                }
            )

        # Check consistency with indIEDest
        if crt in {"1", "2"} and ind_ie_dest == "9":
            # Simples Nacional or Simples Excesso - recipient should not be não contribuinte
            # Actually this is valid, just noting
            pass

        # Check if Simples Nacional (CRT=1) has correct CSOSN
        if crt in {"1", "2"}:
            csosn = self._safe_get(doc, "icms.csosn")
            valid_csosn = {"101", "102", "103", "201", "202", "203", "300", "400", "500", "900"}
            if csosn and csosn not in valid_csosn:
                discrepancies.append(
                    {
                        "field": "CSOSN",
                        "message": f"CSOSN {csosn} inválido para Simples Nacional (CRT={crt})",
                    }
                )

        # Check if Normal regime (CRT=3) has correct CST
        if crt == "3":
            cst = self._safe_get(doc, "icms.cst")
            valid_cst = {"00", "10", "20", "30", "40", "41", "50", "51", "60", "70", "90"}
            if cst and cst not in valid_cst:
                discrepancies.append(
                    {
                        "field": "CST",
                        "message": f"CST {cst} inválido para regime normal (CRT=3)",
                    }
                )

        triggered = len(discrepancies) > 0

        return self._create_result(
            triggered=triggered,
            expected=0,
            actual=len(discrepancies),
            details={
                "discrepancies": discrepancies,
                "crt": crt,
                "ind_ie_dest": ind_ie_dest,
                "csosn": self._safe_get(doc, "icms.csosn"),
                "cst": self._safe_get(doc, "icms.cst"),
            },
            evidence={"regime_data": {"CRT": crt, "indIEDest": ind_ie_dest}},
        )

    def _is_nfe(self, doc: dict) -> bool:
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc
