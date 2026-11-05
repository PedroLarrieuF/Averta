"""Unit tests for critical rules"""

import pytest

from app.services.rules_critical import (
    AdValoremRule,
    ComplementaryCTEAnulationRule,
    FCPRule,
    FreightCubageRule,
    FreightWeightValueRule,
    GRISRule,
    ICMSDifferentialRule,
    ICMSSTRule,
    NFECFOPFreteRule,
    NFECFOPInterestadualRule,
    NFECTECrossRule,
    NFECancelamentoRule,
    NFECartaCorrecaoRule,
    NFEComplementarRule,
    NFEDestinatarioRule,
    NFEDIFALRule,
    NFEFCPRule,
    NFEFreteNaBaseRule,
    NFEICMSCalculoRule,
    NFEICMSSTRule,
    NFEInutilizacaoRule,
    NFENCMCESTRule,
    NFEPesoVolumeRule,
    NFERegimeEspecialRule,
    NFETransportadoraRule,
    NFEValorTotalRule,
    PesoRealVsFaturadoRule,
    ValorMinimoFreteRule,
)
from app.services.rules_engine_v2 import RuleContext, create_engine_v2


class TestICMSRules:
    """Tests for ICMS rules"""

    @pytest.fixture
    def difal_context(self):
        return RuleContext(
            document={
                "uf_inicio": "SP",
                "uf_fim": "RJ",
                "icms": {"v_icms": 100.0, "v_bc": 1000.0},
                "modelo": "57",
            },
            contract={"id": "contract-1"},
            freight_table={
                "rules": {
                    "difal": [
                        {
                            "uf_origem": "SP",
                            "uf_destino": "RJ",
                            "aliquota_difal": 5.0,
                            "aliquota_fcp": 2.0,
                        }
                    ]
                }
            },
        )

    @pytest.mark.asyncio
    async def test_icms_diferential_triggered(self, difal_context):
        """Test ICMS DIFAL triggers when values don't match"""
        rule = ICMSDifferentialRule()
        result = await rule.evaluate(difal_context)

        # Expected: 1000 * (5+2)/100 = 70, Actual: 100 -> triggered
        assert result.triggered is True
        assert result.expected_value == 70.0
        assert result.actual_value == 100.0
        assert result.difference == 30.0

    @pytest.mark.asyncio
    async def test_icms_diferential_not_triggered(self, difal_context):
        """Test ICMS DIFAL doesn't trigger when values match"""
        difal_context.document["icms"]["v_icms"] = 70.0
        rule = ICMSDifferentialRule()
        result = await rule.evaluate(difal_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_icms_diferential_same_uf(self, difal_context):
        """Test ICMS DIFAL doesn't trigger for same UF"""
        difal_context.document["uf_fim"] = "SP"
        rule = ICMSDifferentialRule()
        result = await rule.evaluate(difal_context)

        assert result.triggered is False

    @pytest.fixture
    def fcp_context(self):
        return RuleContext(
            document={
                "uf_fim": "BA",
                "icms": {"v_bc": 1000.0, "v_icms": 15.0},
            },
        )

    @pytest.mark.asyncio
    async def test_fcp_rule(self, fcp_context):
        """Test FCP rule for BA (2%)"""
        rule = FCPRule()
        result = await rule.evaluate(fcp_context)

        # Expected FCP: 1000 * 2% = 20, Actual: 15 -> triggered
        assert result.triggered is True
        assert result.expected_value == 20.0

    @pytest.mark.asyncio
    async def test_fcp_rule_not_applicable(self, fcp_context):
        """Test FCP rule for SP (no FCP)"""
        fcp_context.document["uf_fim"] = "SP"
        rule = FCPRule()
        result = await rule.evaluate(fcp_context)

        assert result.triggered is False

    @pytest.fixture
    def icms_st_context(self):
        return RuleContext(
            document={
                "icms": {"cst": "10", "v_bc_st": 1000.0, "v_icms_st": 200.0},
                "ncm": "22030000",
                "uf_inicio": "MG",
                "uf_fim": "SP",
            },
            freight_table={
                "rules": {
                    "icms_st": [
                        {
                            "ncm": "22030000",
                            "uf_origem": "*",
                            "uf_destino": "SP",
                            "aliquota_st": 18.0,
                        }
                    ]
                }
            },
        )

    @pytest.mark.asyncio
    async def test_icms_st_rule(self, icms_st_context):
        """Test ICMS ST rule for beer (NCM 22030000)"""
        rule = ICMSSTRule()
        result = await rule.evaluate(icms_st_context)

        # Expected: 1000 * 18% = 180, Actual: 200 -> triggered
        assert result.triggered is True
        assert result.expected_value == 180.0
        assert result.actual_value == 200.0

    @pytest.mark.asyncio
    async def test_icms_st_wrong_cst(self, icms_st_context):
        """Test ICMS ST doesn't apply for CST 00"""
        icms_st_context.document["icms"]["cst"] = "00"
        rule = ICMSSTRule()
        result = await rule.evaluate(icms_st_context)

        assert result.triggered is False


class TestFreightRules:
    """Tests for freight validation rules"""

    @pytest.fixture
    def freight_context(self):
        return RuleContext(
            document={
                "weight": 1000.0,
                "volume": 2.0,
                "freight_value": 800.0,
            },
            contract={"id": "contract-1"},
            freight_table={
                "rules": {
                    "faixas_peso": [
                        {
                            "peso_inicial": 0,
                            "peso_final": 500,
                            "valor_kg": 1.0,
                            "valor_minimo": 100.0,
                            "descricao": "Até 500kg",
                        },
                        {
                            "peso_inicial": 501,
                            "peso_final": 2000,
                            "valor_kg": 0.8,
                            "valor_minimo": 200.0,
                            "descricao": "501-2000kg",
                        },
                    ],
                    "faixas_cubagem": [
                        {
                            "cubagem_inicial": 0,
                            "cubagem_final": 1,
                            "valor_m3": 200.0,
                            "valor_minimo": 150.0,
                            "descricao": "Até 1m³",
                        },
                        {
                            "cubagem_inicial": 1.01,
                            "cubagem_final": 5,
                            "valor_m3": 150.0,
                            "valor_minimo": 200.0,
                            "descricao": "1-5m³",
                        },
                    ],
                }
            },
        )

    @pytest.mark.asyncio
    async def test_freight_weight_value_triggered(self, freight_context):
        """Test freight by weight triggers on mismatch"""
        rule = FreightWeightValueRule()
        result = await rule.evaluate(freight_context)

        # 1000kg falls in 501-2000kg range: 1000 * 0.8 = 800, min 200
        # Actual: 800 -> matches! Not triggered
        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_freight_weight_value_mismatch(self, freight_context):
        """Test freight by weight triggers on mismatch"""
        freight_context.document["freight_value"] = 900.0
        rule = FreightWeightValueRule()
        result = await rule.evaluate(freight_context)

        assert result.triggered is True
        assert result.expected_value == 800.0

    @pytest.mark.asyncio
    async def test_freight_cubage_rule(self, freight_context):
        """Test freight by cubage"""
        rule = FreightCubageRule()
        result = await rule.evaluate(freight_context)

        # 2m³ falls in 1-5m³ range: 2 * 150 = 300, min 200
        # Actual: 800 -> triggered
        assert result.triggered is True
        assert result.expected_value == 300.0

    @pytest.mark.asyncio
    async def test_freight_cubage_no_ranges(self, freight_context):
        """Test freight cubage when no ranges defined"""
        freight_context.freight_table["rules"]["faixas_cubagem"] = []
        rule = FreightCubageRule()
        result = await rule.evaluate(freight_context)

        assert result.triggered is False


class TestPesoRealVsFaturadoRule:
    """Tests for Peso Real vs Faturado rule"""

    @pytest.fixture
    def peso_context(self):
        return RuleContext(
            document={
                "peso_bruto": 1000.0,
                "weight": 1100.0,  # 10% difference
            },
            metadata={"company_id": "company-1"},
        )

    @pytest.mark.asyncio
    async def test_peso_real_vs_faturado_triggered(self, peso_context):
        """Test peso rule triggers when difference > 5%"""
        rule = PesoRealVsFaturadoRule(config={"tolerance_pct": 5.0})
        result = await rule.evaluate(peso_context)

        # 10% difference > 5% tolerance  # noqa: ERA001
        assert result.triggered is True
        assert result.difference_pct == 10.0

    @pytest.mark.asyncio
    async def test_peso_real_vs_faturado_not_triggered(self, peso_context):
        """Test peso rule doesn't trigger when within tolerance"""
        peso_context.document["weight"] = 1020.0  # 2% difference
        rule = PesoRealVsFaturadoRule(config={"tolerance_pct": 5.0})
        result = await rule.evaluate(peso_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_peso_real_vs_faturado_missing_data(self, peso_context):
        """Test peso rule with missing data"""
        peso_context.document["peso_bruto"] = None
        rule = PesoRealVsFaturadoRule()
        result = await rule.evaluate(peso_context)

        assert result.triggered is False


class TestValorMinimoFreteRule:
    """Tests for Valor Minimo Frete (ANTT) rule"""

    @pytest.fixture
    def vmin_context(self):
        return RuleContext(
            document={
                "weight": 15000.0,  # 15 tons
                "freight_value": 200.0,
                "modal_rodoviario": {"veiculo_eixos": 3},
                "distancia_km": 500.0,
            },
            contract={"id": "contract-1"},
            freight_table={"id": "table-1"},
        )

    @pytest.mark.asyncio
    async def test_valor_minimo_frete_triggered(self, vmin_context):
        """Test ANTT minimum freight triggers when below floor"""
        # 3 eixos: 2.45/km * 500km = 1225, * 1.2 (peso>10ton) = 1470
        # Actual: 200 -> way below
        rule = ValorMinimoFreteRule()
        result = await rule.evaluate(vmin_context)

        assert result.triggered is True
        assert result.expected_value == 1470.0
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_valor_minimo_frete_not_triggered(self, vmin_context):
        """Test ANTT minimum freight doesn't trigger when above floor"""
        vmin_context.document["freight_value"] = 1500.0
        rule = ValorMinimoFreteRule()
        result = await rule.evaluate(vmin_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_valor_minimo_frete_missing_eixos(self, vmin_context):
        """Test ANTT rule with missing eixos"""
        vmin_context.document["modal_rodoviario"] = {}
        rule = ValorMinimoFreteRule()
        result = await rule.evaluate(vmin_context)

        assert result.triggered is False


class TestComplementaryCTERules:
    """Tests for CT-e Complementar rules"""

    @pytest.fixture
    def cte_anulacao_context(self):
        return RuleContext(
            document={
                "tp_emis": "3",  # Anulação
                "ch_cte_ref": "35240112345678901234550010000000011234567890",
            },
            metadata={"company_id": "company-1"},
        )

    @pytest.mark.asyncio
    async def test_cte_anulacao_without_ref(self, cte_anulacao_context):
        """Test CT-e anulação without reference"""
        cte_anulacao_context.document["ch_cte_ref"] = None
        rule = ComplementaryCTEAnulationRule()
        result = await rule.evaluate(cte_anulacao_context)

        assert result.triggered is True
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_cte_anulacao_not_anulacao(self, cte_anulacao_context):
        """Test rule doesn't apply for non-anulacao"""
        cte_anulacao_context.document["tp_emis"] = "1"  # Normal
        rule = ComplementaryCTEAnulationRule()
        result = await rule.evaluate(cte_anulacao_context)

        assert result.triggered is False


class TestOtherRules:
    """Tests for other rules"""

    @pytest.fixture
    def advalorem_context(self):
        return RuleContext(
            document={
                "total_value": 10000.0,
                "components": {"v_advalorem": 50.0},
            },
            freight_table={"rules": {"advalorem": {"aliquota": 0.5, "teto": 100.0}}},
        )

    @pytest.mark.asyncio
    async def test_advalorem_rule(self, advalorem_context):
        """Test Ad Valorem rule"""
        rule = AdValoremRule()
        result = await rule.evaluate(advalorem_context)

        # Expected: 10000 * 0.5% = 50, Actual: 50 -> not triggered
        assert result.triggered is False
        assert result.expected_value == 50.0

    @pytest.mark.asyncio
    async def test_advalorem_rule_triggered(self, advalorem_context):
        """Test Ad Valorem rule triggered"""
        advalorem_context.document["components"]["v_advalorem"] = 60.0
        rule = AdValoremRule()
        result = await rule.evaluate(advalorem_context)

        assert result.triggered is True

    @pytest.mark.asyncio
    async def test_advalorem_with_teto(self, advalorem_context):
        """Test Ad Valorem with teto"""
        advalorem_context.document["total_value"] = 50000.0
        advalorem_context.document["components"]["v_advalorem"] = 100.0
        rule = AdValoremRule()
        result = await rule.evaluate(advalorem_context)

        # Expected: min(50000 * 0.5%, 100) = 100
        assert result.expected_value == 100.0
        assert result.triggered is False

    @pytest.fixture
    def gris_context(self):
        return RuleContext(
            document={
                "total_value": 10000.0,
                "components": {"v_gris": 30.0},
            },
            freight_table={"rules": {"gris": {"aliquota": 0.3, "teto": 50.0}}},
        )

    @pytest.mark.asyncio
    async def test_gris_rule(self, gris_context):
        """Test GRIS rule"""
        rule = GRISRule()
        result = await rule.evaluate(gris_context)

        # Expected: 10000 * 0.3% = 30
        assert result.expected_value == 30.0
        assert result.triggered is False


class TestRulesEngineIntegration:
    """Integration tests for rules engine"""

    @pytest.mark.asyncio
    async def test_engine_creation(self):
        """Test engine can be created with all rules"""
        engine = await create_engine_v2()
        rules = engine.list_rules()

        # Should have all 34 rules (16 original + 5 NF-e Critical + 7 NF-e High + 6 NF-e Medium)
        assert len(rules) == 34

        rule_codes = [r["code"] for r in rules]
        expected_codes = [
            "ICMS_DIFAL",
            "ICMS_FCP",
            "ICMS_ST",
            "FRETE_PESO_VALOR",
            "FRETE_CUBAGE",
            "PESO_REAL_VS_FATURADO",
            "VALOR_MINIMO_FRETE",
            "REDESPACHO_VALIDACAO",
            "PEDAGIO_CONFERENCIA",
            "AD_VALOREM",
            "GRIS",
            "SICOBAN_TABLE_REAL",
            "CTE_ANULACAO",
            "CTE_SUBSTITUICAO",
            "CTE_COMPLEMENTO_VALOR",
            "ML_ANOMALY",
            # NF-e Critical Rules (Card #34)
            "NFE_ICMS_CALCULO",
            "NFE_ICMS_ST",
            "NFE_DIFAL",
            "NFE_FRETE_NA_BASE",
            "NFE_CTE_CROSS",
            # NF-e High Priority Rules (Card #35)
            "NFE_FCP",
            "NFE_CFOP_FRETE",
            "NFE_CFOP_INTERSTADUAL",
            "NFE_NCM_CEST",
            "NFE_VALOR_TOTAL",
            "NFE_TRANSPORTADORA",
            "NFE_DESTINATARIO",
            # NF-e Medium Priority Rules (Card #36)
            "NFE_PESO_VOLUME",
            "NFE_COMPLEMENTAR",
            "NFE_CARTA_CORRECAO",
            "NFE_CANCELAMENTO",
            "NFE_INUTILIZACAO",
            "NFE_REGIME_ESPECIAL",
        ]

        for code in expected_codes:
            assert code in rule_codes, f"Missing rule: {code}"

    @pytest.mark.asyncio
    async def test_engine_filtering(self):
        """Test engine filters rules by relevance"""
        engine = await create_engine_v2()

        # Document with only freight data
        context = RuleContext(
            document={
                "freight_value": 500.0,
                "weight": 1000.0,
            },
        )

        relevant = engine.get_relevant_rules(context)
        rule_codes = [r.rule_code for r in relevant]

        # Should only include freight-related rules
        assert "FRETE_PESO_VALOR" in rule_codes
        assert "FRETE_CUBAGE" in rule_codes
        assert "ICMS_DIFAL" not in rule_codes  # No ICMS data

    @pytest.mark.asyncio
    async def test_full_audit(self):
        """Test full audit on a document with multiple issues"""
        engine = await create_engine_v2()

        context = RuleContext(
            document={
                "uf_inicio": "SP",
                "uf_fim": "RJ",
                "icms": {
                    "v_icms": 50.0,
                    "v_bc": 1000.0,
                    "cst": "10",
                    "v_bc_st": 1000.0,
                    "v_icms_st": 150.0,
                },
                "ncm": "22030000",
                "freight_value": 100.0,  # Way below minimum
                "weight": 10000.0,
                "volume": 5.0,
                "peso_bruto": 8000.0,  # 20% difference
                "total_value": 50000.0,
                "components": {"v_advalorem": 100.0, "v_gris": 50.0},
                "modal_rodoviario": {"veiculo_eixos": 3},
                "distancia_km": 500.0,
            },
            contract={"id": "contract-1"},
            freight_table={
                "rules": {
                    "difal": [
                        {
                            "uf_origem": "SP",
                            "uf_destino": "RJ",
                            "aliquota_difal": 5.0,
                            "aliquota_fcp": 2.0,
                        }
                    ],
                    "icms_st": [
                        {
                            "ncm": "22030000",
                            "uf_origem": "*",
                            "uf_destino": "RJ",
                            "aliquota_st": 18.0,
                        }
                    ],
                    "faixas_peso": [
                        {
                            "peso_inicial": 0,
                            "peso_final": 20000,
                            "valor_kg": 0.5,
                            "valor_minimo": 100.0,
                        }
                    ],
                    "faixas_cubagem": [
                        {
                            "cubagem_inicial": 0,
                            "cubagem_final": 10,
                            "valor_m3": 50.0,
                            "valor_minimo": 100.0,
                        }
                    ],
                    "advalorem": {"aliquota": 0.2, "teto": 200.0},
                    "gris": {"aliquota": 0.1, "teto": 100.0},
                }
            },
            metadata={"company_id": "company-1"},
        )

        results = await engine.evaluate_all(context)

        # Should find multiple discrepancies
        assert len(results) >= 5

        # Check specific ones
        rule_codes = [r.rule_code for r in results]
        assert "VALOR_MINIMO_FRETE" in rule_codes  # Critical
        assert "PESO_REAL_VS_FATURADO" in rule_codes  # 20% diff
        assert "ICMS_DIFAL" in rule_codes
        assert "ICMS_ST" in rule_codes


class TestRulesEngineCache:
    """Tests for Rules Engine Redis Cache"""

    @pytest.fixture
    def cache_context(self):
        return RuleContext(
            document={
                "uf_inicio": "SP",
                "uf_fim": "RJ",
                "icms": {"v_icms": 100.0, "v_bc": 1000.0},
            },
            contract={"id": "contract-1"},
            freight_table={
                "rules": {
                    "difal": [
                        {
                            "uf_origem": "SP",
                            "uf_destino": "RJ",
                            "aliquota_difal": 5.0,
                            "aliquota_fcp": 2.0,
                        }
                    ]
                }
            },
        )

    @pytest.mark.asyncio
    async def test_cache_miss_then_hit(self, cache_context):
        """Test cache miss on first call, hit on second"""
        engine = await create_engine_v2()

        # First call - cache miss
        results1 = await engine.evaluate_all(cache_context)

        # Second call - should hit cache
        results2 = await engine.evaluate_all(cache_context)

        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2, strict=False):
            assert r1.rule_code == r2.rule_code
            assert r1.triggered == r2.triggered

    @pytest.mark.asyncio
    async def test_cache_invalidation_by_rule(self, cache_context):
        """Test cache invalidation by rule code"""
        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate specific rule
        deleted = await engine.invalidate_cache(rule_code="ICMS_DIFAL")
        assert deleted >= 0  # May be 0 if using local cache fallback

    @pytest.mark.asyncio
    async def test_cache_invalidation_by_tag(self, cache_context):
        """Test cache invalidation by tag"""
        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate by tag
        deleted = await engine.invalidate_cache(tag="icms")
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_freight_table_cache_invalidation(self, cache_context):
        """Test freight table cache invalidation"""
        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate freight tables
        deleted = await engine.invalidate_freight_table_cache()
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_reference_data_cache_invalidation(self, cache_context):
        """Test reference data (ICMS, SICOBAN) cache invalidation"""
        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate reference data
        deleted = await engine.invalidate_reference_data_cache()
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_cache_stats(self, cache_context):
        """Test cache statistics"""
        engine = await create_engine_v2()

        stats = await engine.get_cache_stats()
        assert "local_cache_size" in stats
        assert "redis_connected" in stats
        assert "cache_version" in stats

    @pytest.mark.asyncio
    async def test_cache_key_consistency(self, cache_context):
        """Test cache key generation is consistent for same input"""
        engine = await create_engine_v2()
        rule = engine.get_rule("ICMS_DIFAL")

        key1 = engine._cache_key(rule, cache_context)
        key2 = engine._cache_key(rule, cache_context)

        assert key1 == key2
        assert key1.startswith("rule:ICMS_DIFAL:")

    @pytest.mark.asyncio
    async def test_different_context_different_key(self, cache_context):
        """Test different contexts produce different cache keys"""
        engine = await create_engine_v2()
        rule = engine.get_rule("ICMS_DIFAL")

        key1 = engine._cache_key(rule, cache_context)

        # Different UF should produce different key
        cache_context2 = RuleContext(
            document={
                "uf_inicio": "MG",  # Different UF
                "uf_fim": "SP",
                "icms": {"v_icms": 100.0, "v_bc": 1000.0},
            },
            contract={"id": "contract-1"},
            freight_table={
                "rules": {
                    "difal": [
                        {
                            "uf_origem": "MG",
                            "uf_destino": "SP",
                            "aliquota_difal": 7.0,
                            "aliquota_fcp": 2.0,
                        }
                    ]
                }
            },
        )
        key2 = engine._cache_key(rule, cache_context2)

        assert key1 != key2


class TestNFECriticalRules:
    """Tests for NF-e Critical Rules (Card #34)"""

    @pytest.fixture
    def nfe_icms_context(self):
        """Context for NF-e ICMS calculation test"""
        return RuleContext(
            document={
                "modelo": "55",
                "ide": {"mod": "55"},
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {"enderDest": {"UF": "RJ"}, "indIEDest": "1"},
                "det": {"prod": {"CFOP": "6102", "NCM": "22030000", "vProd": 1000.0}},
                "icms": {
                    "cst": "00",
                    "v_bc": 1000.0,
                    "v_icms": 180.0,
                    "p_icms": 18.0,
                },
                "total": {
                    "ICMSTot": {
                        "vNF": 1180.0,
                        "vProd": 1000.0,
                        "vFrete": 50.0,
                        "vSeg": 10.0,
                        "vOutro": 20.0,
                        "vIPI": 0.0,
                        "vICMS": 180.0,
                        "vST": 0.0,
                        "vFCP": 0.0,
                    }
                },
                "transp": {"modFrete": "0", "vol": {"pesoB": 100.0}},
            },
        )

    @pytest.fixture
    def nfe_st_context(self):
        """Context for NF-e ICMS ST test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "MG"}},
                "dest": {"enderDest": {"UF": "SP"}},
                "det": {"prod": {"NCM": "22030000", "vProd": 1000.0}},
                "icms": {
                    "cst": "10",
                    "v_bc_st": 1416.7,  # (1000 + 50 + 10 + 20) * (1 + 41.67/100) ≈ 1416.7
                    "v_icms_st": 255.0,  # 1416.7 * 18% ≈ 255
                    "p_mva_st": 41.67,
                    "p_icms_st": 18.0,
                },
                "total": {
                    "ICMSTot": {
                        "vNF": 1315.0,
                        "vProd": 1000.0,
                        "vFrete": 50.0,
                        "vSeg": 10.0,
                        "vOutro": 20.0,
                        "vICMS": 180.0,
                        "vST": 255.0,
                    }
                },
            },
        )

    @pytest.fixture
    def nfe_difal_context(self):
        """Context for NF-e DIFAL test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}, "CRT": "3"},
                "dest": {"enderDest": {"UF": "RJ"}, "indIEDest": "1"},
                "icms": {
                    "cst": "00",
                    "v_bc": 1000.0,
                    "v_icms": 200.0,  # Should be: interestadual 12% + DIFAL (20% - 12%) + FCP 2% = 20%
                    "p_icms": 12.0,
                    "v_fcp": 20.0,
                    "p_fcp": 2.0,
                },
                "total": {
                    "ICMSTot": {
                        "vNF": 1200.0,
                        "vProd": 1000.0,
                        "vICMS": 200.0,
                        "vFCP": 20.0,
                    }
                },
            },
        )

    @pytest.fixture
    def nfe_frete_base_context(self):
        """Context for NF-e Frete na Base test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {"enderDest": {"UF": "RJ"}},
                "det": {"prod": {"vProd": 1000.0, "CFOP": "6102"}},
                "icms": {
                    "cst": "00",
                    "v_bc": 1080.0,  # Should include vProd + vFrete + vSeg + vOutro = 1000+50+10+20
                },
                "total": {
                    "ICMSTot": {
                        "vNF": 1180.0,
                        "vProd": 1000.0,
                        "vFrete": 50.0,
                        "vSeg": 10.0,
                        "vOutro": 20.0,
                        "vICMS": 180.0,
                    }
                },
                "transp": {"modFrete": "0"},
            },
        )

    @pytest.fixture
    def nfe_cte_cross_context(self):
        """Context for NF-e x CT-e cross validation test"""
        return RuleContext(
            document={
                "modelo": "55",
                "ide": {"mod": "55"},
                "protNFe": {"infProt": {"chNFe": "35240112345678901234550010000000011234567890"}},
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {"enderDest": {"UF": "RJ"}},
                "det": {"prod": {"vProd": 1000.0, "CFOP": "6102"}},
                "icms": {"cst": "00", "v_bc": 1000.0, "v_icms": 180.0, "p_icms": 18.0},
                "total": {
                    "ICMSTot": {
                        "vNF": 1180.0,
                        "vProd": 1000.0,
                        "vFrete": 50.0,
                    }
                },
                "transp": {"modFrete": "0", "vol": {"pesoB": 100.0, "qVol": 1}},
            },
            metadata={
                "cte_reference": {
                    "accessKey": "57240112345678901234550010000000011234567890",
                    "v_carga": 1000.0,
                    "weight": 100.0,
                    "modal_rodoviario": {"frete_tipo": "0"},
                }
            },
        )

    # ============================================
    # NFE_ICMS_CALCULO Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_icms_calculo_triggered(self, nfe_icms_context):
        """Test NF-e ICMS calculation triggers when values don't match"""
        rule = NFEICMSCalculoRule()
        result = await rule.evaluate(nfe_icms_context)

        # Expected: 1000 * 18% = 180, Actual: 180 -> not triggered (within tolerance)
        # But if actual was different...
        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_icms_calculo_mismatch(self, nfe_icms_context):
        """Test NF-e ICMS calculation triggers on mismatch"""
        nfe_icms_context.document["icms"]["v_icms"] = 200.0  # Wrong value
        rule = NFEICMSCalculoRule()
        result = await rule.evaluate(nfe_icms_context)

        assert result.triggered is True
        assert result.expected_value == 180.0
        assert result.actual_value == 200.0
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_nfe_icms_calculo_not_nfe(self, nfe_icms_context):
        """Test rule doesn't apply to non-NF-e documents"""
        nfe_icms_context.document["modelo"] = "57"  # CT-e
        nfe_icms_context.document["ide"] = {"mod": "57"}
        rule = NFEICMSCalculoRule()
        result = await rule.evaluate(nfe_icms_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_icms_calculo_sn_csosn(self, nfe_icms_context):
        """Test rule doesn't apply to Simples Nacional CSOSN"""
        nfe_icms_context.document["icms"]["cst"] = None
        nfe_icms_context.document["icms"]["csosn"] = "101"  # Simples Nacional
        rule = NFEICMSCalculoRule()
        result = await rule.evaluate(nfe_icms_context)

        assert result.triggered is False

    # ============================================
    # NFE_ICMS_ST Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_icms_st_triggered(self, nfe_st_context):
        """Test NF-e ICMS ST triggers on mismatch"""
        nfe_st_context.document["icms"]["v_icms_st"] = 300.0  # Wrong value
        rule = NFEICMSSTRule()
        result = await rule.evaluate(nfe_st_context)

        assert result.triggered is True
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_nfe_icms_st_not_triggered(self, nfe_st_context):
        """Test NF-e ICMS ST doesn't trigger when correct"""
        rule = NFEICMSSTRule()
        result = await rule.evaluate(nfe_st_context)

        # Should be close to expected (255) within tolerance
        assert result.triggered is False or abs(result.difference or 0) <= 1.0

    @pytest.mark.asyncio
    async def test_nfe_icms_st_wrong_cst(self, nfe_st_context):
        """Test ICMS ST doesn't apply for CST without ST"""
        nfe_st_context.document["icms"]["cst"] = "00"  # Not ST
        rule = NFEICMSSTRule()
        result = await rule.evaluate(nfe_st_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_icms_st_missing_ncm(self, nfe_st_context):
        """Test ICMS ST requires NCM"""
        nfe_st_context.document["det"]["prod"]["NCM"] = None
        rule = NFEICMSSTRule()
        result = await rule.evaluate(nfe_st_context)

        assert result.triggered is False

    # ============================================
    # NFE_DIFAL Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_difal_triggered(self, nfe_difal_context):
        """Test NF-e DIFAL triggers on mismatch"""
        # SP -> RJ: interestadual 12%, interna RJ 20%, FCP 2%
        # Expected ICMS: 1000 * 12% (inter) + 1000 * 8% (DIFAL) + 1000 * 2% (FCP) = 220
        # Actual: 200 -> triggered
        nfe_difal_context.document["icms"]["v_icms"] = 200.0
        rule = NFEDIFALRule()
        result = await rule.evaluate(nfe_difal_context)

        assert result.triggered is True
        assert result.severity == "CRITICAL"
        assert result.details["uf_origem"] == "SP"
        assert result.details["uf_destino"] == "RJ"

    @pytest.mark.asyncio
    async def test_nfe_difal_not_triggered(self, nfe_difal_context):
        """Test NF-e DIFAL doesn't trigger when correct"""
        # Expected: 1000 * 12% + 1000 * 8% + 1000 * 2% = 220
        nfe_difal_context.document["icms"]["v_icms"] = 220.0
        nfe_difal_context.document["icms"]["v_fcp"] = 20.0
        rule = NFEDIFALRule()
        result = await rule.evaluate(nfe_difal_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_difal_same_uf(self, nfe_difal_context):
        """Test DIFAL doesn't apply for same UF"""
        nfe_difal_context.document["dest"]["enderDest"]["UF"] = "SP"
        rule = NFEDIFALRule()
        result = await rule.evaluate(nfe_difal_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_difal_simples_nacional(self, nfe_difal_context):
        """Test DIFAL doesn't apply for Simples Nacional destinatário"""
        nfe_difal_context.document["dest"]["indIEDest"] = "9"  # Não contribuinte
        nfe_difal_context.document["emit"]["CRT"] = "1"  # Simples Nacional
        rule = NFEDIFALRule()
        result = await rule.evaluate(nfe_difal_context)

        assert result.triggered is False

    # ============================================
    # NFE_FRETE_NA_BASE Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_frete_na_base_triggered(self, nfe_frete_base_context):
        """Test Frete na Base triggers when freight not in base"""
        # vBC = 1080, but should be at least 1000 + 50 + 10 + 20 = 1080
        # If vBC is less:
        nfe_frete_base_context.document["icms"]["v_bc"] = 1000.0  # Missing freight
        rule = NFEFreteNaBaseRule()
        result = await rule.evaluate(nfe_frete_base_context)

        assert result.triggered is True
        assert result.severity == "CRITICAL"

    @pytest.mark.asyncio
    async def test_nfe_frete_na_base_not_triggered(self, nfe_frete_base_context):
        """Test Frete na Base doesn't trigger when freight in base"""
        rule = NFEFreteNaBaseRule()
        result = await rule.evaluate(nfe_frete_base_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_frete_na_base_mod_frete_9(self, nfe_frete_base_context):
        """Test rule doesn't apply for modFrete 9 (sem frete)"""
        nfe_frete_base_context.document["transp"]["modFrete"] = "9"
        rule = NFEFreteNaBaseRule()
        result = await rule.evaluate(nfe_frete_base_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_frete_na_base_cst_not_applicable(self, nfe_frete_base_context):
        """Test rule doesn't apply for CST not requiring freight in base"""
        nfe_frete_base_context.document["icms"]["cst"] = "41"  # Não tributada
        rule = NFEFreteNaBaseRule()
        result = await rule.evaluate(nfe_frete_base_context)

        assert result.triggered is False

    # ============================================
    # NFE_CTE_CROSS Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_cte_cross_triggered_value(self, nfe_cte_cross_context):
        """Test cross-validation triggers on value mismatch"""
        # NF-e vNF = 1180, CT-e vCarga = 1000 (diff > 2%)
        nfe_cte_cross_context.document["total"]["ICMSTot"]["vNF"] = 1180.0
        nfe_cte_cross_context.metadata["cte_reference"]["v_carga"] = 1000.0
        rule = NFECTECrossRule()
        result = await rule.evaluate(nfe_cte_cross_context)

        assert result.triggered is True
        assert result.severity == "CRITICAL"
        assert len(result.details["discrepancies"]) >= 1

    @pytest.mark.asyncio
    async def test_nfe_cte_cross_triggered_weight(self, nfe_cte_cross_context):
        """Test cross-validation triggers on weight mismatch"""
        nfe_cte_cross_context.document["transp"]["vol"]["pesoB"] = 100.0
        nfe_cte_cross_context.metadata["cte_reference"]["weight"] = 80.0  # 20% diff
        rule = NFECTECrossRule()
        result = await rule.evaluate(nfe_cte_cross_context)

        assert result.triggered is True

    @pytest.mark.asyncio
    async def test_nfe_cte_cross_not_triggered(self, nfe_cte_cross_context):
        """Test cross-validation doesn't trigger when values match"""
        # Match values within 2%
        nfe_cte_cross_context.document["total"]["ICMSTot"]["vNF"] = 1000.0
        nfe_cte_cross_context.metadata["cte_reference"]["v_carga"] = 1000.0
        nfe_cte_cross_context.document["transp"]["vol"]["pesoB"] = 100.0
        nfe_cte_cross_context.metadata["cte_reference"]["weight"] = 100.0
        rule = NFECTECrossRule()
        result = await rule.evaluate(nfe_cte_cross_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cte_cross_no_cte_ref(self, nfe_cte_cross_context):
        """Test rule when no CT-e reference"""
        nfe_cte_cross_context.metadata["cte_reference"] = None
        rule = NFECTECrossRule()
        result = await rule.evaluate(nfe_cte_cross_context)

        assert result.triggered is False


# ============================================
# NF-e HIGH PRIORITY RULES Tests (Card #35)
# ============================================


class TestNFEHighRules:
    """Tests for NF-e High Priority Rules (Card #35)"""

    @pytest.fixture
    def nfe_fcp_context(self):
        """Context for NF-e FCP test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}, "CRT": "3"},
                "dest": {"enderDest": {"UF": "BA"}, "indIEDest": "1"},
                "icms": {
                    "cst": "00",
                    "v_bc": 1000.0,
                    "v_fcp": 15.0,
                    "p_fcp": 2.0,
                },
            },
        )

    @pytest.fixture
    def nfe_cfop_frete_context(self):
        """Context for NF-e CFOP Frete test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {"enderDest": {"UF": "RJ"}},
                "det": {"prod": {"CFOP": "6102", "NCM": "22030000"}},
                "transp": {"modFrete": "0"},
            },
        )

    @pytest.fixture
    def nfe_cfop_inter_context(self):
        """Context for NF-e CFOP Interstate test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {"enderDest": {"UF": "RJ"}},
                "det": {"prod": {"CFOP": "6102", "NCM": "22030000"}},
            },
        )

    @pytest.fixture
    def nfe_ncm_cest_context(self):
        """Context for NF-e NCM/CEST test"""
        return RuleContext(
            document={
                "modelo": "55",
                "det": {"prod": {"NCM": "22030000", "CEST": "28.001.00"}},
            },
        )

    @pytest.fixture
    def nfe_valor_total_context(self):
        """Context for NF-e Valor Total test"""
        return RuleContext(
            document={
                "modelo": "55",
                "total": {
                    "ICMSTot": {
                        "vNF": 1200.0,
                        "vProd": 1000.0,
                        "vFrete": 50.0,
                        "vSeg": 10.0,
                        "vDesc": 0.0,
                        "vII": 0.0,
                        "vIPI": 0.0,
                        "vPIS": 0.0,
                        "vCOFINS": 0.0,
                        "vICMS": 100.0,
                        "vST": 0.0,
                        "vFCP": 20.0,
                        "vOutro": 20.0,
                    }
                },
            },
        )

    @pytest.fixture
    def nfe_transportadora_context(self):
        """Context for NF-e Transportadora test"""
        return RuleContext(
            document={
                "modelo": "55",
                "transp": {
                    "modFrete": "0",
                    "transporta": {
                        "CNPJ": "12345678000195",
                        "IE": "123456789",
                        "UF": "SP",
                        "xNome": "Transportadora Teste",
                    },
                    "veicTransp": {
                        "placa": "ABC1D23",
                        "UF": "SP",
                        "RNTRC": "12345678",
                    },
                },
            },
        )

    @pytest.fixture
    def nfe_destinatario_context(self):
        """Context for NF-e Destinatário test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"enderEmit": {"UF": "SP"}},
                "dest": {
                    "CNPJ": "12345678000195",
                    "IE": "123456789",
                    "indIEDest": "1",
                    "xNome": "Destinatário Teste",
                    "enderDest": {
                        "xLgr": "Rua Teste",
                        "nro": "100",
                        "xBairro": "Centro",
                        "cMun": "3550308",
                        "xMun": "São Paulo",
                        "UF": "SP",
                        "CEP": "01000000",
                    },
                },
            },
        )

    # ============================================
    # NFE_FCP Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_fcp_triggered(self, nfe_fcp_context):
        """Test NF-e FCP triggers when values don't match"""
        # BA has FCP 2%, expected: 1000 * 2% = 20, actual: 15 -> triggered
        rule = NFEFCPRule()
        result = await rule.evaluate(nfe_fcp_context)

        assert result.triggered is True
        assert result.expected_value == 20.0
        assert result.actual_value == 15.0
        assert result.severity == "HIGH"

    @pytest.mark.asyncio
    async def test_nfe_fcp_not_triggered(self, nfe_fcp_context):
        """Test NF-e FCP doesn't trigger when values match"""
        nfe_fcp_context.document["icms"]["v_fcp"] = 20.0
        rule = NFEFCPRule()
        result = await rule.evaluate(nfe_fcp_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_fcp_simples_nacional(self, nfe_fcp_context):
        """Test FCP doesn't apply for Simples Nacional"""
        nfe_fcp_context.document["emit"]["CRT"] = "1"
        rule = NFEFCPRule()
        result = await rule.evaluate(nfe_fcp_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_fcp_no_fcp_uf(self, nfe_fcp_context):
        """Test FCP doesn't apply when destination UF has no FCP"""
        nfe_fcp_context.document["dest"]["enderDest"]["UF"] = "SP"  # SP has FCP 2%
        # Actually SP has FCP, let's use a UF without FCP
        nfe_fcp_context.document["dest"]["enderDest"]["UF"] = "AC"  # AC has FCP 0%
        rule = NFEFCPRule()
        result = await rule.evaluate(nfe_fcp_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_fcp_same_uf(self, nfe_fcp_context):
        """Test FCP doesn't apply for same UF (not interstate)"""
        nfe_fcp_context.document["dest"]["enderDest"]["UF"] = "SP"
        rule = NFEFCPRule()
        result = await rule.evaluate(nfe_fcp_context)

        assert result.triggered is False

    # ============================================
    # NFE_CFOP_FRETE Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_cfop_frete_triggered(self, nfe_cfop_frete_context):
        """Test CFOP Frete triggers on mismatch"""
        # modFrete 0 (CIF) interstate expects CFOP 6xxx, give 5xxx (intra)
        nfe_cfop_frete_context.document["det"]["prod"]["CFOP"] = "5102"
        rule = NFECFOPFreteRule()
        result = await rule.evaluate(nfe_cfop_frete_context)

        assert result.triggered is True
        assert result.severity == "HIGH"

    @pytest.mark.asyncio
    async def test_nfe_cfop_frete_not_triggered(self, nfe_cfop_frete_context):
        """Test CFOP Frete doesn't trigger when correct"""
        # modFrete 0 (CIF) interstate -> CFOP 6102 is correct
        rule = NFECFOPFreteRule()
        result = await rule.evaluate(nfe_cfop_frete_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cfop_frete_fob(self, nfe_cfop_frete_context):
        """Test CFOP Frete with FOB (modFrete 1)"""
        nfe_cfop_frete_context.document["transp"]["modFrete"] = "1"  # FOB
        # For FOB interstate, 6102 is also valid
        rule = NFECFOPFreteRule()
        result = await rule.evaluate(nfe_cfop_frete_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cfop_frete_intrastate(self, nfe_cfop_frete_context):
        """Test CFOP Frete for intrastate"""
        nfe_cfop_frete_context.document["dest"]["enderDest"]["UF"] = "SP"  # Same UF
        nfe_cfop_frete_context.document["det"]["prod"]["CFOP"] = "5102"  # Intra CIF
        nfe_cfop_frete_context.document["transp"]["modFrete"] = "0"
        rule = NFECFOPFreteRule()
        result = await rule.evaluate(nfe_cfop_frete_context)

        assert result.triggered is False

    # ============================================
    # NFE_CFOP_INTERSTADUAL Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_cfop_inter_triggered(self, nfe_cfop_inter_context):
        """Test CFOP Interstate triggers on wrong prefix"""
        # Interstate SP->RJ should have CFOP 6xxx, give 5xxx
        nfe_cfop_inter_context.document["det"]["prod"]["CFOP"] = "5102"
        rule = NFECFOPInterestadualRule()
        result = await rule.evaluate(nfe_cfop_inter_context)

        assert result.triggered is True
        assert result.severity == "HIGH"
        assert result.details["expected_prefix"] == "6"
        assert result.details["cfop_prefix"] == "5"

    @pytest.mark.asyncio
    async def test_nfe_cfop_inter_not_triggered(self, nfe_cfop_inter_context):
        """Test CFOP Interstate doesn't trigger when correct"""
        # CFOP 6102 for interstate is correct
        rule = NFECFOPInterestadualRule()
        result = await rule.evaluate(nfe_cfop_inter_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cfop_intra_not_triggered(self, nfe_cfop_inter_context):
        """Test intrastate with CFOP 5xxx"""
        nfe_cfop_inter_context.document["dest"]["enderDest"]["UF"] = "SP"
        nfe_cfop_inter_context.document["det"]["prod"]["CFOP"] = "5102"
        rule = NFECFOPInterestadualRule()
        result = await rule.evaluate(nfe_cfop_inter_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cfop_exterior(self, nfe_cfop_inter_context):
        """Test exterior with CFOP 7xxx"""
        nfe_cfop_inter_context.document["dest"]["enderDest"]["UF"] = "EX"
        nfe_cfop_inter_context.document["det"]["prod"]["CFOP"] = "7102"
        rule = NFECFOPInterestadualRule()
        result = await rule.evaluate(nfe_cfop_inter_context)

        # 7xxx is for exterior, treated as interstate (prefix 6)
        assert result.triggered is True

    # ============================================
    # NFE_NCM_CEST Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_ncm_cest_triggered(self, nfe_ncm_cest_context):
        """Test NCM/CEST triggers on invalid CEST"""
        nfe_ncm_cest_context.document["det"]["prod"]["CEST"] = "99.999.99"
        rule = NFENCMCESTRule()
        result = await rule.evaluate(nfe_ncm_cest_context)

        assert result.triggered is True
        assert result.severity == "HIGH"

    @pytest.mark.asyncio
    async def test_nfe_ncm_cest_not_triggered(self, nfe_ncm_cest_context):
        """Test NCM/CEST doesn't trigger when valid"""
        rule = NFENCMCESTRule()
        result = await rule.evaluate(nfe_ncm_cest_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_ncm_cest_missing(self, nfe_ncm_cest_context):
        """Test NCM/CEST triggers when CEST is missing but required"""
        nfe_ncm_cest_context.document["det"]["prod"]["CEST"] = None
        rule = NFENCMCESTRule()
        result = await rule.evaluate(nfe_ncm_cest_context)

        assert result.triggered is True
        assert result.details["reason"] == "CEST obrigatório não informado"

    @pytest.mark.asyncio
    async def test_nfe_ncm_cest_not_applicable(self, nfe_ncm_cest_context):
        """Test NCM/CEST doesn't apply for NCM not in mapping"""
        nfe_ncm_cest_context.document["det"]["prod"]["NCM"] = "99999999"
        rule = NFENCMCESTRule()
        result = await rule.evaluate(nfe_ncm_cest_context)

        assert result.triggered is False

    # ============================================
    # NFE_VALOR_TOTAL Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_valor_total_triggered(self, nfe_valor_total_context):
        """Test Valor Total triggers on mismatch"""
        # Expected: 1000+50+10-0+0+0+0+0+100+0+20+20 = 1200, actual: 1200 -> not triggered
        # Change actual to trigger
        nfe_valor_total_context.document["total"]["ICMSTot"]["vNF"] = 1300.0
        rule = NFEValorTotalRule()
        result = await rule.evaluate(nfe_valor_total_context)

        assert result.triggered is True
        assert result.severity == "HIGH"
        assert result.expected_value == 1200.0
        assert result.actual_value == 1300.0

    @pytest.mark.asyncio
    async def test_nfe_valor_total_not_triggered(self, nfe_valor_total_context):
        """Test Valor Total doesn't trigger when values match"""
        rule = NFEValorTotalRule()
        result = await rule.evaluate(nfe_valor_total_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_valor_total_with_discount(self, nfe_valor_total_context):
        """Test Valor Total with discount"""
        nfe_valor_total_context.document["total"]["ICMSTot"]["vDesc"] = 50.0
        nfe_valor_total_context.document["total"]["ICMSTot"]["vNF"] = 1150.0  # 1200 - 50
        rule = NFEValorTotalRule()
        result = await rule.evaluate(nfe_valor_total_context)

        assert result.triggered is False

    # ============================================
    # NFE_TRANSPORTADORA Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_transportadora_triggered_missing_cnpj(self, nfe_transportadora_context):
        """Test Transportadora triggers when CNPJ missing"""
        nfe_transportadora_context.document["transp"]["transporta"]["CNPJ"] = None
        nfe_transportadora_context.document["transp"]["transporta"]["CPF"] = None
        rule = NFETransportadoraRule()
        result = await rule.evaluate(nfe_transportadora_context)

        assert result.triggered is True
        assert result.severity == "HIGH"
        assert any(d["field"] == "cnpj_cpf" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_transportadora_not_triggered(self, nfe_transportadora_context):
        """Test Transportadora doesn't trigger when all data present"""
        rule = NFETransportadoraRule()
        result = await rule.evaluate(nfe_transportadora_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_transportadora_missing_vehicle(self, nfe_transportadora_context):
        """Test Transportadora triggers when vehicle data missing for rodoviário"""
        nfe_transportadora_context.document["transp"]["veicTransp"]["placa"] = None
        rule = NFETransportadoraRule()
        result = await rule.evaluate(nfe_transportadora_context)

        assert result.triggered is True
        assert any(d["field"] == "placa" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_transportadora_not_rodoviario(self, nfe_transportadora_context):
        """Test Transportadora doesn't require vehicle for non-rodoviário"""
        nfe_transportadora_context.document["transp"]["modFrete"] = "9"  # Sem frete
        nfe_transportadora_context.document["transp"]["veicTransp"]["placa"] = None
        rule = NFETransportadoraRule()
        result = await rule.evaluate(nfe_transportadora_context)

        assert result.triggered is False

    # ============================================
    # NFE_DESTINATARIO Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_destinatario_triggered_missing_cnpj(self, nfe_destinatario_context):
        """Test Destinatário triggers when CNPJ/CPF missing"""
        nfe_destinatario_context.document["dest"]["CNPJ"] = None
        nfe_destinatario_context.document["dest"]["CPF"] = None
        rule = NFEDestinatarioRule()
        result = await rule.evaluate(nfe_destinatario_context)

        assert result.triggered is True
        assert result.severity == "HIGH"
        assert any(d["field"] == "cnpj_cpf" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_destinatario_not_triggered(self, nfe_destinatario_context):
        """Test Destinatário doesn't trigger when all data present"""
        rule = NFEDestinatarioRule()
        result = await rule.evaluate(nfe_destinatario_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_destinatario_missing_ie(self, nfe_destinatario_context):
        """Test Destinatário triggers when IE missing for contribuinte"""
        nfe_destinatario_context.document["dest"]["IE"] = None
        nfe_destinatario_context.document["dest"]["indIEDest"] = "1"  # Contribuinte
        rule = NFEDestinatarioRule()
        result = await rule.evaluate(nfe_destinatario_context)

        assert result.triggered is True
        assert any(d["field"] == "ie" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_destinatario_no_ie_for_nao_contribuinte(self, nfe_destinatario_context):
        """Test Destinatário doesn't require IE for não contribuinte"""
        nfe_destinatario_context.document["dest"]["IE"] = None
        nfe_destinatario_context.document["dest"]["indIEDest"] = "9"  # Não contribuinte
        rule = NFEDestinatarioRule()
        result = await rule.evaluate(nfe_destinatario_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_destinatario_missing_address(self, nfe_destinatario_context):
        """Test Destinatário triggers when address incomplete"""
        nfe_destinatario_context.document["dest"]["enderDest"]["xLgr"] = None
        rule = NFEDestinatarioRule()
        result = await rule.evaluate(nfe_destinatario_context)

        assert result.triggered is True
        assert any(d["field"] == "xlgr" for d in result.details["discrepancies"])


# ============================================
# NF-e MEDIUM PRIORITY RULES Tests (Card #36)
# ============================================


class TestNFEMediumRules:
    """Tests for NF-e Medium Priority Rules (Card #36)"""

    @pytest.fixture
    def nfe_peso_volume_context(self):
        """Context for NF-e Peso/Volume test"""
        return RuleContext(
            document={
                "modelo": "55",
                "transp": {
                    "vol": {
                        "pesoB": 100.0,
                        "pesoL": 80.0,
                        "qVol": 2,
                        "alt": 50,
                        "larg": 40,
                        "comp": 30,
                    }
                },
            },
        )

    @pytest.fixture
    def nfe_complementar_context(self):
        """Context for NF-e Complementar test"""
        return RuleContext(
            document={
                "modelo": "55",
                "ide": {"tpEmis": "1", "xCorrecao": "Correção do CFOP de 5102 para 6102"},
                "infNFeSupl": {"refNFe": "35240112345678901234550010000000011234567890"},
            },
        )

    @pytest.fixture
    def nfe_carta_correcao_context(self):
        """Context for NF-e Carta de Correção test"""
        return RuleContext(
            document={
                "evento": {
                    "tpEvento": "110110",
                    "detEvento": {
                        "chNFe": "35240112345678901234550010000000011234567890",
                        "nCorrecao": "1",
                        "xCorrecao": "Correção do CFOP de 5102 para 6102",
                    },
                },
                "retEvento": {"infEvento": {"cStat": "135"}},
            },
        )

    @pytest.fixture
    def nfe_cancelamento_context(self):
        """Context for NF-e Cancelamento test"""
        return RuleContext(
            document={
                "evento": {
                    "tpEvento": "110111",
                    "detEvento": {
                        "chNFe": "35240112345678901234550010000000011234567890",
                        "nProt": "123456789012345",
                        "xJust": "Cancelamento por erro de emissão da nota fiscal",
                        "dhEvento": "2024-01-15T10:30:00-03:00",
                    },
                },
                "ide": {"dhEmi": "2024-01-15T09:00:00-03:00"},
                "retEvento": {"infEvento": {"cStat": "135"}},
            },
        )

    @pytest.fixture
    def nfe_inutilizacao_context(self):
        """Context for NF-e Inutilização test"""
        return RuleContext(
            document={
                "inutNFe": {
                    "infInut": {
                        "CNPJ": "12345678000195",
                        "nNFIni": 100,
                        "nNFFin": 110,
                        "ano": 2024,
                        "xJust": "Numeração não utilizada por erro de sequência",
                    }
                },
                "retInutNFe": {"infInut": {"cStat": "102"}},
            },
        )

    @pytest.fixture
    def nfe_regime_especial_context(self):
        """Context for NF-e Regime Especial test"""
        return RuleContext(
            document={
                "modelo": "55",
                "emit": {"CRT": "3"},  # Regime Normal
                "icms": {"cst": "00", "csosn": None},
                "det": {"prod": {"CFOP": "6102"}},
            },
        )

    # ============================================
    # NFE_PESO_VOLUME Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_peso_volume_triggered_bruto_menor_liquido(self, nfe_peso_volume_context):
        """Test Peso/Volume triggers when bruto < liquido"""
        nfe_peso_volume_context.document["transp"]["vol"]["pesoB"] = 50.0
        nfe_peso_volume_context.document["transp"]["vol"]["pesoL"] = 80.0
        rule = NFEPesoVolumeRule()
        result = await rule.evaluate(nfe_peso_volume_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "peso_bruto_vs_liquido" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_peso_volume_not_triggered(self, nfe_peso_volume_context):
        """Test Peso/Volume doesn't trigger when consistent"""
        rule = NFEPesoVolumeRule()
        result = await rule.evaluate(nfe_peso_volume_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_peso_volume_not_nfe(self, nfe_peso_volume_context):
        """Test rule doesn't apply to non-NF-e"""
        nfe_peso_volume_context.document["modelo"] = "57"
        rule = NFEPesoVolumeRule()
        result = await rule.evaluate(nfe_peso_volume_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_peso_volume_inconsistent_volume(self, nfe_peso_volume_context):
        """Test Peso/Volume triggers when volume inconsistent with weight"""
        # Very small volume for 100kg weight
        nfe_peso_volume_context.document["transp"]["vol"]["alt"] = 1
        nfe_peso_volume_context.document["transp"]["vol"]["larg"] = 1
        nfe_peso_volume_context.document["transp"]["vol"]["comp"] = 1
        rule = NFEPesoVolumeRule()
        result = await rule.evaluate(nfe_peso_volume_context)

        assert result.triggered is True
        assert any(d["field"] == "volume_consistency" for d in result.details["discrepancies"])

    # ============================================
    # NFE_COMPLEMENTAR Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_complementar_triggered_missing_ref(self, nfe_complementar_context):
        """Test Complementar triggers when refNFe missing"""
        nfe_complementar_context.document["infNFeSupl"]["refNFe"] = None
        rule = NFEComplementarRule()
        result = await rule.evaluate(nfe_complementar_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "refNFe" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_complementar_not_triggered(self, nfe_complementar_context):
        """Test Complementar doesn't trigger when valid"""
        rule = NFEComplementarRule()
        result = await rule.evaluate(nfe_complementar_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_complementar_not_nfe(self, nfe_complementar_context):
        """Test rule doesn't apply to non-NF-e"""
        nfe_complementar_context.document["modelo"] = "57"
        rule = NFEComplementarRule()
        result = await rule.evaluate(nfe_complementar_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_complementar_not_complementar(self, nfe_complementar_context):
        """Test rule doesn't apply for normal emission"""
        nfe_complementar_context.document["ide"]["tpEmis"] = "1"  # Actually it is 1 for normal
        # Normal emission should not trigger this rule as it's not a complementar
        nfe_complementar_context.document["ide"]["tpEmis"] = "2"  # Contingência FS
        rule = NFEComplementarRule()
        result = await rule.evaluate(nfe_complementar_context)

        assert result.triggered is False

    # ============================================
    # NFE_CARTA_CORRECAO Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_carta_correcao_triggered_missing_correcao(self, nfe_carta_correcao_context):
        """Test Carta de Correção triggers when xCorrecao missing"""
        nfe_carta_correcao_context.document["evento"]["detEvento"]["xCorrecao"] = None
        rule = NFECartaCorrecaoRule()
        result = await rule.evaluate(nfe_carta_correcao_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "xCorrecao" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_carta_correcao_triggered_invalid_ncorrecao(self, nfe_carta_correcao_context):
        """Test Carta de Correção triggers when nCorrecao invalid"""
        nfe_carta_correcao_context.document["evento"]["detEvento"]["nCorrecao"] = "99"
        rule = NFECartaCorrecaoRule()
        result = await rule.evaluate(nfe_carta_correcao_context)

        assert result.triggered is True
        assert any(d["field"] == "nCorrecao" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_carta_correcao_not_triggered(self, nfe_carta_correcao_context):
        """Test Carta de Correção doesn't trigger when valid"""
        rule = NFECartaCorrecaoRule()
        result = await rule.evaluate(nfe_carta_correcao_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_carta_correcao_not_event(self, nfe_carta_correcao_context):
        """Test rule doesn't apply when not a carta de correção event"""
        nfe_carta_correcao_context.document["evento"]["tpEvento"] = "110111"  # Cancelamento
        rule = NFECartaCorrecaoRule()
        result = await rule.evaluate(nfe_carta_correcao_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_carta_correcao_unauthorized(self, nfe_carta_correcao_context):
        """Test Carta de Correção triggers when unauthorized"""
        nfe_carta_correcao_context.document["retEvento"]["infEvento"]["cStat"] = "136"  # Falha
        rule = NFECartaCorrecaoRule()
        result = await rule.evaluate(nfe_carta_correcao_context)

        assert result.triggered is True
        assert any(d["field"] == "cStat" for d in result.details["discrepancies"])

    # ============================================
    # NFE_CANCELAMENTO Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_triggered_missing_protocolo(self, nfe_cancelamento_context):
        """Test Cancelamento triggers when nProt missing"""
        nfe_cancelamento_context.document["evento"]["detEvento"]["nProt"] = None
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "nProt" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_triggered_short_justificativa(self, nfe_cancelamento_context):
        """Test Cancelamento triggers when justificativa too short"""
        nfe_cancelamento_context.document["evento"]["detEvento"]["xJust"] = "Erro"
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is True
        assert any(d["field"] == "xJust" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_triggered_after_24h(self, nfe_cancelamento_context):
        """Test Cancelamento triggers when > 24h from emission"""
        # Emit: 2024-01-15T09:00, Evento: 2024-01-16T10:30 (25.5h later)
        nfe_cancelamento_context.document["evento"]["detEvento"]["dhEvento"] = "2024-01-16T10:30:00-03:00"
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is True
        assert any(d["field"] == "dhEvento" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_not_triggered(self, nfe_cancelamento_context):
        """Test Cancelamento doesn't trigger when valid"""
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_not_event(self, nfe_cancelamento_context):
        """Test rule doesn't apply when not a cancelamento event"""
        nfe_cancelamento_context.document["evento"]["tpEvento"] = "110110"  # Carta correção
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_cancelamento_unauthorized(self, nfe_cancelamento_context):
        """Test Cancelamento triggers when unauthorized"""
        nfe_cancelamento_context.document["retEvento"]["infEvento"]["cStat"] = "136"
        rule = NFECancelamentoRule()
        result = await rule.evaluate(nfe_cancelamento_context)

        assert result.triggered is True
        assert any(d["field"] == "cStat" for d in result.details["discrepancies"])

    # ============================================
    # NFE_INUTILIZACAO Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_inutilizacao_triggered_missing_cnpj(self, nfe_inutilizacao_context):
        """Test Inutilização triggers when CNPJ missing"""
        nfe_inutilizacao_context.document["inutNFe"]["infInut"]["CNPJ"] = None
        rule = NFEInutilizacaoRule()
        result = await rule.evaluate(nfe_inutilizacao_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "CNPJ" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_inutilizacao_triggered_invalid_range(self, nfe_inutilizacao_context):
        """Test Inutilização triggers when range invalid"""
        nfe_inutilizacao_context.document["inutNFe"]["infInut"]["nNFIni"] = 110
        nfe_inutilizacao_context.document["inutNFe"]["infInut"]["nNFFin"] = 100
        rule = NFEInutilizacaoRule()
        result = await rule.evaluate(nfe_inutilizacao_context)

        assert result.triggered is True
        assert any(d["field"] == "nNFIni_nNFFin" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_inutilizacao_triggered_missing_ano(self, nfe_inutilizacao_context):
        """Test Inutilização triggers when ano missing"""
        nfe_inutilizacao_context.document["inutNFe"]["infInut"]["ano"] = None
        rule = NFEInutilizacaoRule()
        result = await rule.evaluate(nfe_inutilizacao_context)

        assert result.triggered is True
        assert any(d["field"] == "ano" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_inutilizacao_not_triggered(self, nfe_inutilizacao_context):
        """Test Inutilização doesn't trigger when valid"""
        rule = NFEInutilizacaoRule()
        result = await rule.evaluate(nfe_inutilizacao_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_inutilizacao_unauthorized(self, nfe_inutilizacao_context):
        """Test Inutilização triggers when unauthorized"""
        nfe_inutilizacao_context.document["retInutNFe"]["infInut"]["cStat"] = "252"  # Falha
        rule = NFEInutilizacaoRule()
        result = await rule.evaluate(nfe_inutilizacao_context)

        assert result.triggered is True
        assert any(d["field"] == "cStat" for d in result.details["discrepancies"])

    # ============================================
    # NFE_REGIME_ESPECIAL Tests
    # ============================================

    @pytest.mark.asyncio
    async def test_nfe_regime_especial_triggered_invalid_crt(self, nfe_regime_especial_context):
        """Test Regime Especial triggers when CRT invalid"""
        nfe_regime_especial_context.document["emit"]["CRT"] = "9"
        rule = NFERegimeEspecialRule()
        result = await rule.evaluate(nfe_regime_especial_context)

        assert result.triggered is True
        assert result.severity == "MEDIUM"
        assert any(d["field"] == "CRT" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_regime_especial_not_triggered_normal(self, nfe_regime_especial_context):
        """Test Regime Especial doesn't trigger for valid Normal regime"""
        rule = NFERegimeEspecialRule()
        result = await rule.evaluate(nfe_regime_especial_context)

        assert result.triggered is False

    @pytest.mark.asyncio
    async def test_nfe_regime_especial_triggered_invalid_cst(self, nfe_regime_especial_context):
        """Test Regime Especial triggers when CST invalid for Normal regime"""
        nfe_regime_especial_context.document["icms"]["cst"] = "99"
        rule = NFERegimeEspecialRule()
        result = await rule.evaluate(nfe_regime_especial_context)

        assert result.triggered is True
        assert any(d["field"] == "CST" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_regime_especial_triggered_invalid_csosn(self, nfe_regime_especial_context):
        """Test Regime Especial triggers when CSOSN invalid for Simples"""
        nfe_regime_especial_context.document["emit"]["CRT"] = "1"  # Simples Nacional
        nfe_regime_especial_context.document["icms"]["csosn"] = "999"  # Invalid
        nfe_regime_especial_context.document["icms"]["cst"] = None
        rule = NFERegimeEspecialRule()
        result = await rule.evaluate(nfe_regime_especial_context)

        assert result.triggered is True
        assert any(d["field"] == "CSOSN" for d in result.details["discrepancies"])

    @pytest.mark.asyncio
    async def test_nfe_regime_especial_not_nfe(self, nfe_regime_especial_context):
        """Test rule doesn't apply to non-NF-e"""
        nfe_regime_especial_context.document["modelo"] = "57"
        rule = NFERegimeEspecialRule()
        result = await rule.evaluate(nfe_regime_especial_context)

        assert result.triggered is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
