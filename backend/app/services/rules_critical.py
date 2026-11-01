"""Critical Rules Implementation - 6 critical + complementary CT-e rules"""
from typing import Optional, List, Dict
from decimal import Decimal
import structlog

from app.services.rules_engine_v2 import (
    BaseRule, RuleContext, DiscrepancyResult, DiscrepancyType
)

logger = structlog.get_logger()


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

        triggered = abs(icms_doc - expected_icms) > 0.01

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

    def _lookup_difal(self, rules: dict, uf_origem: str, uf_destino: str) -> Optional[dict]:
        for rule in rules.get("difal", []):
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
        "AC": 2.0, "AL": 2.0, "AM": 2.0, "AP": 2.0, "BA": 2.0,
        "CE": 2.0, "MA": 2.0, "PA": 2.0, "PB": 2.0, "PE": 2.0,
        "PI": 2.0, "RN": 2.0, "RR": 2.0, "SE": 2.0,
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

        triggered = icms_doc < expected_fcp - 0.01

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
                if (uf_origem_rule == "*" or uf_origem_rule == uf_origem) and \
                   (uf_destino_rule == "*" or uf_destino_rule == uf_destino):
                    st_rule = rule
                    break

        if not st_rule:
            return self._create_result(False, details={"reason": f"No ST rule for NCM {ncm}"})

        # Calcular esperado
        v_bc_st = self._safe_get(doc, "icms.v_bc_st", 0)
        p_icms_st = st_rule.get("aliquota_st", 0)
        expected_st = round(v_bc_st * p_icms_st / 100, 2)

        actual_st = self._safe_get(doc, "icms.v_icms_st", 0)

        triggered = abs(actual_st - expected_st) > 0.01

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

        triggered = abs(freight_charged - expected) > 0.01

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

        triggered = abs(freight_charged - expected) > 0.01

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
        peso_liquido_xml = self._safe_get(doc, "peso_liquido")  # vPesoL

        # Peso faturado (na fatura/tabela)
        peso_faturado = self._safe_get(doc, "weight")

        if not peso_bruto_xml or not peso_faturado:
            return self._create_result(False, details={"reason": "Missing weight data"})

        # Tolerância configurável (default 5%)
        tolerance_pct = self.config.get("tolerance_pct", 5.0)
        diff_pct = abs(peso_faturado - peso_bruto_xml) / peso_bruto_xml * 100

        triggered = diff_pct > tolerance_pct

        return self._create_result(
            triggered=triggered,
            expected=peso_bruto_xml,
            actual=peso_faturado,
            difference=round(peso_faturado - peso_bruto_xml, 2),
            difference_pct=round(diff_pct, 2),
            details={
                "peso_xml": peso_bruto_xml,
                "peso_faturado": peso_faturado,
                "tolerancia_pct": tolerance_pct,
            },
            severity="HIGH" if diff_pct > 20 else "MEDIUM",
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
        if peso > 10000:  # 10 ton
            frete_minimo *= 1.2

        triggered = freight_charged < frete_minimo - 0.01

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
            severity="CRITICAL",
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

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self._sicoban_data: Optional[List[dict]] = None

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
        match = self._find_sicoban_match(sicoban_rules, cep_origem, cep_destino, tipo_carga, modalidade)

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

        triggered = abs(freight_charged - expected) > 0.01

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

    def _find_sicoban_match(self, rules: List[dict], cep_origem: str, cep_destino: str, tipo_carga: str, modalidade: str) -> Optional[dict]:
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

    async def _load_sicoban_data(self) -> List[dict]:
        """Load Sicoban data from file"""
        import json
        import os

        if self._sicoban_data is not None:
            return self._sicoban_data

        # Try to load from data file
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sicoban_table.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
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
            return self._create_result(
                True,
                details={"reason": "CT-e anulação sem referência ao CT-e original (chCTeRef)"},
                severity="CRITICAL",
            )

        # Verificar se CT-e original existe no sistema
        from app.core.database import get_prisma
        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado no sistema"},
                severity="HIGH",
            )

        # Validar: mesmo emitente
        if original.carrierId != doc.get("carrier_id"):
            return self._create_result(
                True,
                details={"reason": "CT-e anulação com emitente diferente do original"},
                severity="HIGH",
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
            return self._create_result(
                True,
                details={"reason": "CT-e substituição sem referência ao CT-e original"},
                severity="CRITICAL",
            )

        from app.core.database import get_prisma
        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado"},
                severity="HIGH",
            )

        # Validar: valores novos devem ser diferentes do original
        v_carga_new = self._safe_get(doc, "v_carga", 0)
        v_frete_new = self._safe_get(doc, "freight_value", 0)

        v_carga_orig = original.totalValue or 0
        v_frete_orig = original.freightValue or 0

        if v_carga_new == v_carga_orig and v_frete_new == v_frete_orig:
            return self._create_result(
                True,
                details={"reason": "CT-e substituição com mesmos valores do original"},
                severity="MEDIUM",
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
            return self._create_result(
                True,
                details={"reason": "CT-e complemento sem referência ao CT-e original"},
                severity="HIGH",
            )

        from app.core.database import get_prisma
        db = await get_prisma()

        original = await db.document.find_first(
            where={"accessKey": ch_cte_ref, "companyId": context.metadata.get("company_id")}
        )

        if not original:
            return self._create_result(
                True,
                details={"reason": f"CT-e original {ch_cte_ref} não encontrado"},
                severity="HIGH",
            )

        # Complemento deve APENAS aumentar valores
        v_carga_new = self._safe_get(doc, "v_carga", 0)
        v_frete_new = self._safe_get(doc, "freight_value", 0)

        v_carga_orig = original.totalValue or 0
        v_frete_orig = original.freightValue or 0

        if v_carga_new < v_carga_orig:
            return self._create_result(
                True,
                details={"reason": "Complemento não pode reduzir valor da carga"},
                severity="HIGH",
            )

        if v_frete_new < v_frete_orig:
            return self._create_result(
                True,
                details={"reason": "Complemento não pode reduzir valor do frete"},
                severity="HIGH",
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
            return self._create_result(
                True,
                details={"reason": "Redespacho indicado mas sem CT-e complementar"},
                severity="CRITICAL",
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

        triggered = abs(total_charged - total_expected) > 0.50

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

        triggered = abs(advalorem_charged - expected) > 0.01

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

        triggered = abs(gris_charged - expected) > 0.01

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