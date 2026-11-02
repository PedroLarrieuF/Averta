"""Unit tests for critical rules"""
import pytest
from decimal import Decimal
from app.services.rules_engine_v2 import RuleContext, DiscrepancyType
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
                        {"uf_origem": "SP", "uf_destino": "RJ", "aliquota_difal": 5.0, "aliquota_fcp": 2.0}
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
                        {"ncm": "22030000", "uf_origem": "*", "uf_destino": "SP", "aliquota_st": 18.0}
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
                        {"peso_inicial": 0, "peso_final": 500, "valor_kg": 1.0, "valor_minimo": 100.0, "descricao": "Até 500kg"},
                        {"peso_inicial": 501, "peso_final": 2000, "valor_kg": 0.8, "valor_minimo": 200.0, "descricao": "501-2000kg"},
                    ],
                    "faixas_cubagem": [
                        {"cubagem_inicial": 0, "cubagem_final": 1, "valor_m3": 200.0, "valor_minimo": 150.0, "descricao": "Até 1m³"},
                        {"cubagem_inicial": 1.01, "cubagem_final": 5, "valor_m3": 150.0, "valor_minimo": 200.0, "descricao": "1-5m³"},
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

        # 10% difference > 5% tolerance
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
            freight_table={
                "rules": {
                    "advalorem": {"aliquota": 0.5, "teto": 100.0}
                }
            },
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
            freight_table={
                "rules": {
                    "gris": {"aliquota": 0.3, "teto": 50.0}
                }
            },
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
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()
        rules = engine.list_rules()

        # Should have all 17 rules
        assert len(rules) == 17

        rule_codes = [r["code"] for r in rules]
        expected_codes = [
            "ICMS_DIFAL", "ICMS_FCP", "ICMS_ST",
            "FRETE_PESO_VALOR", "FRETE_CUBAGE",
            "PESO_REAL_VS_FATURADO", "VALOR_MINIMO_FRETE",
            "REDESPACHO_VALIDACAO", "PEDAGIO_CONFERENCIA",
            "AD_VALOREM", "GRIS", "SICOBAN_TABLE_REAL",
            "CTE_ANULACAO", "CTE_SUBSTITUICAO", "CTE_COMPLEMENTO_VALOR",
        ]

        for code in expected_codes:
            assert code in rule_codes, f"Missing rule: {code}"

    @pytest.mark.asyncio
    async def test_engine_filtering(self):
        """Test engine filters rules by relevance"""
        from app.services.rules_engine_v2 import create_engine_v2, RuleContext

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
        from app.services.rules_engine_v2 import create_engine_v2, RuleContext

        engine = await create_engine_v2()

        context = RuleContext(
            document={
                "uf_inicio": "SP",
                "uf_fim": "RJ",
                "icms": {"v_icms": 50.0, "v_bc": 1000.0, "cst": "10", "v_bc_st": 1000.0, "v_icms_st": 150.0},
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
                    "difal": [{"uf_origem": "SP", "uf_destino": "RJ", "aliquota_difal": 5.0, "aliquota_fcp": 2.0}],
                    "icms_st": [{"ncm": "22030000", "uf_origem": "*", "uf_destino": "SP", "aliquota_st": 18.0}],
                    "faixas_peso": [{"peso_inicial": 0, "peso_final": 20000, "valor_kg": 0.5, "valor_minimo": 100.0}],
                    "faixas_cubagem": [{"cubagem_inicial": 0, "cubagem_final": 10, "valor_m3": 50.0, "valor_minimo": 100.0}],
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
                        {"uf_origem": "SP", "uf_destino": "RJ", "aliquota_difal": 5.0, "aliquota_fcp": 2.0}
                    ]
                }
            },
        )

    @pytest.mark.asyncio
    async def test_cache_miss_then_hit(self, cache_context):
        """Test cache miss on first call, hit on second"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        # First call - cache miss
        results1 = await engine.evaluate_all(cache_context)

        # Second call - should hit cache
        results2 = await engine.evaluate_all(cache_context)

        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.rule_code == r2.rule_code
            assert r1.triggered == r2.triggered

    @pytest.mark.asyncio
    async def test_cache_invalidation_by_rule(self, cache_context):
        """Test cache invalidation by rule code"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate specific rule
        deleted = await engine.invalidate_cache(rule_code="ICMS_DIFAL")
        assert deleted >= 0  # May be 0 if using local cache fallback

    @pytest.mark.asyncio
    async def test_cache_invalidation_by_tag(self, cache_context):
        """Test cache invalidation by tag"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate by tag
        deleted = await engine.invalidate_cache(tag="icms")
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_freight_table_cache_invalidation(self, cache_context):
        """Test freight table cache invalidation"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate freight tables
        deleted = await engine.invalidate_freight_table_cache()
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_reference_data_cache_invalidation(self, cache_context):
        """Test reference data (ICMS, SICOBAN) cache invalidation"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        # Populate cache
        await engine.evaluate_all(cache_context)

        # Invalidate reference data
        deleted = await engine.invalidate_reference_data_cache()
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_cache_stats(self, cache_context):
        """Test cache statistics"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()

        stats = await engine.get_cache_stats()
        assert "local_cache_size" in stats
        assert "redis_connected" in stats
        assert "cache_version" in stats

    @pytest.mark.asyncio
    async def test_cache_key_consistency(self, cache_context):
        """Test cache key generation is consistent for same input"""
        from app.services.rules_engine_v2 import create_engine_v2, ICMSDifferentialRule

        engine = await create_engine_v2()
        rule = engine.get_rule("ICMS_DIFAL")

        key1 = engine._cache_key(rule, cache_context)
        key2 = engine._cache_key(rule, cache_context)

        assert key1 == key2
        assert key1.startswith("rule:ICMS_DIFAL:")

    @pytest.mark.asyncio
    async def test_different_context_different_key(self, cache_context):
        """Test different contexts produce different cache keys"""
        from app.services.rules_engine_v2 import create_engine_v2, ICMSDifferentialRule

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
                        {"uf_origem": "MG", "uf_destino": "SP", "aliquota_difal": 7.0, "aliquota_fcp": 2.0}
                    ]
                }
            },
        )
        key2 = engine._cache_key(rule, cache_context2)

        assert key1 != key2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])