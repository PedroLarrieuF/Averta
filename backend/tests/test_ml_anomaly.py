"""Tests for ML Anomaly Detection"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.rules_critical import MLAnomalyRule
from app.services.rules_engine_v2 import RuleContext


class TestMLAnomalyRule:
    """Tests for ML Anomaly Detection rule"""

    @pytest.fixture
    def ml_context(self):
        return RuleContext(
            document={
                "type": "CTE",
                "carrier_id": "carrier-123",
                "client_id": "client-456",
                "uf_inicio": "SP",
                "uf_fim": "RJ",
                "total_value": 50000.0,
                "weight": 10000.0,
                "volume": 20.0,
                "freight_value": 5000.0,
                "icms_value": 9000.0,
                "distancia_km": 500.0,
                "modal_rodoviario_veiculo_eixos": 4,
            },
            metadata={
                "rule_code": "FRETE_PESO_VALOR",
                "difference_pct": 15.0,
                "severity": "MEDIUM",
            },
        )

    @pytest.mark.asyncio
    async def test_ml_anomaly_rule_triggered(self, ml_context):
        """Test ML anomaly rule triggers when ML service returns anomaly"""
        rule = MLAnomalyRule(
            config={
                "anomaly_threshold": -0.5,
                "ml_endpoint": "http://localhost:8001/ml/anomaly-score",
            }
        )

        # Mock httpx response for anomaly
        mock_response = Mock()
        mock_response.json.return_value = {
            "anomaly_score": -0.8,
            "is_anomaly": True,
            "threshold": -0.5,
            "model_version": "v20260101_120000",
        }
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await rule.evaluate(ml_context)

        assert result.triggered is True
        assert result.rule_code == "ML_ANOMALY"
        assert result.actual_value == -0.8
        assert result.details["is_anomaly"] is True
        assert result.severity == "HIGH"  # Score < -0.7

    @pytest.mark.asyncio
    async def test_ml_anomaly_rule_not_triggered(self, ml_context):
        """Test ML anomaly rule doesn't trigger for normal scores"""
        rule = MLAnomalyRule(
            config={
                "anomaly_threshold": -0.5,
                "ml_endpoint": "http://localhost:8001/ml/anomaly-score",
            }
        )

        # Mock httpx response for normal
        mock_response = Mock()
        mock_response.json.return_value = {
            "anomaly_score": 0.2,
            "is_anomaly": False,
            "threshold": -0.5,
            "model_version": "v20260101_120000",
        }
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await rule.evaluate(ml_context)

        assert result.triggered is False
        assert result.actual_value == 0.2
        assert result.details["is_anomaly"] is False

    @pytest.mark.asyncio
    async def test_ml_anomaly_rule_timeout_fallback(self, ml_context):
        """Test ML anomaly rule falls back gracefully on timeout"""
        import httpx

        rule = MLAnomalyRule(
            config={
                "anomaly_threshold": -0.5,
                "ml_endpoint": "http://localhost:8001/ml/anomaly-score",
                "timeout": 5.0,
            }
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timeout")
            result = await rule.evaluate(ml_context)

        assert result.triggered is False
        assert "fallback" in result.details
        assert result.details["fallback"] is True

    @pytest.mark.asyncio
    async def test_ml_anomaly_rule_http_error_fallback(self, ml_context):
        """Test ML anomaly rule falls back gracefully on HTTP error"""
        import httpx

        rule = MLAnomalyRule(
            config={
                "anomaly_threshold": -0.5,
                "ml_endpoint": "http://localhost:8001/ml/anomaly-score",
            }
        )

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await rule.evaluate(ml_context)

        assert result.triggered is False
        assert "fallback" in result.details

    def test_extract_features(self, ml_context):
        """Test feature extraction from context"""
        rule = MLAnomalyRule()
        features = rule._extract_features(ml_context)

        # Check all expected features present
        expected_features = [
            "rule_type_hash",
            "carrier_id_hash",
            "client_id_hash",
            "value",
            "weight",
            "volume",
            "uf_origem_encoded",
            "uf_destino_encoded",
            "diff_pct",
            "severity_encoded",
            "document_type_encoded",
            "distance_km",
            "eixos",
            "has_icms",
            "has_freight_value",
        ]

        for feat in expected_features:
            assert feat in features, f"Missing feature: {feat}"

        # Check specific values
        assert features["value"] == 50000.0
        assert features["weight"] == 10000.0
        assert features["diff_pct"] == 15.0
        assert features["uf_origem_encoded"] == 25  # SP
        assert features["uf_destino_encoded"] == 19  # RJ
        assert features["severity_encoded"] == 1  # MEDIUM
        assert features["document_type_encoded"] == 1  # CTE
        assert features["has_icms"] == 1
        assert features["has_freight_value"] == 1

    def test_extract_features_missing_data(self):
        """Test feature extraction with minimal data"""
        rule = MLAnomalyRule()
        context = RuleContext(document={}, metadata={})
        features = rule._extract_features(context)

        # Should not crash, all features should have defaults
        assert all(isinstance(v, float) for v in features.values())
        assert features["uf_origem_encoded"] == 0
        assert features["uf_destino_encoded"] == 0
        assert features["severity_encoded"] == 1  # Default MEDIUM


class TestMLInferenceService:
    """Tests for ML Inference Service (FastAPI endpoint)"""

    def test_feature_order_constant(self):
        """Test that FEATURE_ORDER matches expected features"""
        from app.services.ml.inference import FEATURE_ORDER

        expected = [
            "rule_type_hash",
            "carrier_id_hash",
            "client_id_hash",
            "value",
            "weight",
            "volume",
            "uf_origem_encoded",
            "uf_destino_encoded",
            "diff_pct",
            "severity_encoded",
            "document_type_encoded",
            "distance_km",
            "eixos",
            "has_icms",
            "has_freight_value",
        ]

        assert FEATURE_ORDER == expected

    def test_uf_encoding(self):
        """Test UF encoding consistency"""
        from app.services.ml.inference import UF_ENCODING

        assert UF_ENCODING["SP"] == 25
        assert UF_ENCODING["RJ"] == 19
        assert UF_ENCODING["MG"] == 13
        assert UF_ENCODING.get("XX", 0) == 0  # Unknown UF defaults to 0

    def test_severity_encoding(self):
        """Test severity encoding"""
        from app.services.ml.inference import SEVERITY_ENCODING

        assert SEVERITY_ENCODING["LOW"] == 0
        assert SEVERITY_ENCODING["MEDIUM"] == 1
        assert SEVERITY_ENCODING["HIGH"] == 2
        assert SEVERITY_ENCODING["CRITICAL"] == 3

    def test_document_type_encoding(self):
        """Test document type encoding"""
        from app.services.ml.inference import DOCUMENT_TYPE_ENCODING

        assert DOCUMENT_TYPE_ENCODING["CTE"] == 1
        assert DOCUMENT_TYPE_ENCODING["NFE"] == 2
        assert DOCUMENT_TYPE_ENCODING["CTE_COMPLEMENTAR"] == 3
        assert DOCUMENT_TYPE_ENCODING.get("UNKNOWN", 8) == 8


class TestRulesEngineIntegration:
    """Integration tests with ML rule in engine"""

    @pytest.mark.asyncio
    async def test_engine_includes_ml_rule(self):
        """Test that create_engine_v2 includes MLAnomalyRule"""
        from app.services.rules_engine_v2 import create_engine_v2

        engine = await create_engine_v2()
        rules = engine.list_rules()
        rule_codes = [r["code"] for r in rules]

        assert "ML_ANOMALY" in rule_codes
        ml_rule = next(r for r in rules if r["code"] == "ML_ANOMALY")
        assert ml_rule["name"] == "ML Anomaly Detection (Isolation Forest)"
        assert "ml" in ml_rule["tags"]
        assert "anomaly" in ml_rule["tags"]

    @pytest.mark.asyncio
    async def test_ml_rule_relevance_filtering(self):
        """Test ML rule is included in relevant rules (generic tag)"""
        from app.services.rules_engine_v2 import RuleContext, create_engine_v2

        engine = await create_engine_v2()

        # ML rule has tags ["ml", "anomaly"] - should be included when document has freight data
        context = RuleContext(
            document={
                "freight_value": 5000.0,
                "weight": 1000.0,
            }
        )

        relevant = engine.get_relevant_rules(context)
        rule_codes = [r.rule_code for r in relevant]

        # ML rule should be included because it has relevance tags that match
        # (freight tag matches)
        assert "ML_ANOMALY" in rule_codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
