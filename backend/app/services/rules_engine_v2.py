"""Rules Engine v2 - DB-backed, cached, filterable"""

import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import redis.asyncio as redis
import structlog

from app.core.config import settings
from app.core.database import get_prisma

logger = structlog.get_logger()


class DiscrepancyType(StrEnum):
    # CT-e Rules (existing)
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

    # NF-e Rules (CRITICAL)
    NFE_ICMS_CALCULO = "NFE_ICMS_CALCULO"
    NFE_ICMS_ST = "NFE_ICMS_ST"
    NFE_DIFAL = "NFE_DIFAL"
    NFE_FRETE_NA_BASE = "NFE_FRETE_NA_BASE"
    NFE_CTE_CROSS = "NFE_CTE_CROSS"

    # NF-e Rules (HIGH)
    NFE_FCP = "NFE_FCP"
    NFE_CFOP_FRETE = "NFE_CFOP_FRETE"
    NFE_CFOP_INTERSTADUAL = "NFE_CFOP_INTERSTADUAL"
    NFE_NCM_CEST = "NFE_NCM_CEST"
    NFE_VALOR_TOTAL = "NFE_VALOR_TOTAL"
    NFE_TRANSPORTADORA = "NFE_TRANSPORTADORA"
    NFE_DESTINATARIO = "NFE_DESTINATARIO"

    # NF-e Rules (MEDIUM)
    NFE_PESO_VOLUME = "NFE_PESO_VOLUME"
    NFE_COMPLEMENTAR = "NFE_COMPLEMENTAR"
    NFE_CARTA_CORRECAO = "NFE_CARTA_CORRECAO"
    NFE_CANCELAMENTO = "NFE_CANCELAMENTO"
    NFE_INUTILIZACAO = "NFE_INUTILIZACAO"
    NFE_REGIME_ESPECIAL = "NFE_REGIME_ESPECIAL"

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
    severity: str = "MEDIUM"


class BaseRule(ABC):
    """Base class for all audit rules"""

    rule_code: str = ""
    rule_name: str = ""
    discrepancy_type: DiscrepancyType = DiscrepancyType.OTHER
    severity: str = "MEDIUM"
    requires_contract: bool = False
    requires_freight_table: bool = False
    relevance_tags: list[str] = field(default_factory=list)  # para filtro

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        pass

    def _create_result(
        self,
        triggered: bool,
        expected: float | None = None,
        actual: float | None = None,
        details: dict[str, Any] | None = None,
        evidence: dict[str, Any] | None = None,
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

    def _safe_get(self, data: dict[str, Any], path: str, default: Any = None) -> Any:
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


class RulesEngineV2:
    """Rules Engine v2 - DB-backed with Redis cache"""

    # TTL configuration per rule (seconds)
    DEFAULT_TTL = 3600  # 1 hour
    RULE_TTL_CONFIG = {
        # CT-e Rules (existing)
        "SICOBAN_TABLE_REAL": 86400,  # 24 hours
        "ICMS_ST": 21600,  # 6 hours
        "ICMS_DIFAL": 3600,  # 1 hour
        "ICMS_FCP": 3600,  # 1 hour
        "FRETE_PESO_VALOR": 3600,  # 1 hour
        "FRETE_CUBAGE": 3600,  # 1 hour
        "VALOR_MINIMO_FRETE": 3600,  # 1 hour
        "PESO_REAL_VS_FATURADO": 3600,  # 1 hour
        "AD_VALOREM": 3600,  # 1 hour
        "GRIS": 3600,  # 1 hour
        "REDESPACHO_VALIDACAO": 3600,  # 1 hour
        "PEDAGIO_CONFERENCIA": 3600,  # 1 hour
        "CTE_ANULACAO": 3600,  # 1 hour
        "CTE_SUBSTITUICAO": 3600,  # 1 hour
        "CTE_COMPLEMENTO_VALOR": 3600,  # 1 hour
        # NF-e Rules (CRITICAL - shorter TTL for accuracy)
        "NFE_ICMS_CALCULO": 1800,  # 30 min
        "NFE_ICMS_ST": 1800,  # 30 min
        "NFE_DIFAL": 1800,  # 30 min
        "NFE_FRETE_NA_BASE": 1800,  # 30 min
        "NFE_CTE_CROSS": 1800,  # 30 min
        # NF-e Rules (HIGH)
        "NFE_FCP": 3600,  # 1 hour
        "NFE_CFOP_FRETE": 3600,  # 1 hour
        "NFE_CFOP_INTERSTADUAL": 3600,  # 1 hour
        "NFE_NCM_CEST": 3600,  # 1 hour
        "NFE_VALOR_TOTAL": 3600,  # 1 hour
        "NFE_TRANSPORTADORA": 3600,  # 1 hour
        "NFE_DESTINATARIO": 3600,  # 1 hour
        # NF-e Rules (MEDIUM)
        "NFE_PESO_VOLUME": 7200,  # 2 hours
        "NFE_COMPLEMENTAR": 7200,  # 2 hours
        "NFE_CARTA_CORRECAO": 7200,  # 2 hours
        "NFE_CANCELAMENTO": 7200,  # 2 hours
        "NFE_INUTILIZACAO": 7200,  # 2 hours
        "NFE_REGIME_ESPECIAL": 7200,  # 2 hours
    }

    def __init__(self) -> None:
        self._rules: list[BaseRule] = []
        self._rule_map: dict[str, BaseRule] = {}
        self._rule_index: dict[str, list[BaseRule]] = {}  # tag -> rules
        self._cache: redis.Redis | None = None
        self._cache_version = self._get_deploy_version()
        self._local_cache: dict[str, tuple[DiscrepancyResult, float]] = {}  # fallback in-memory cache
        self._local_cache_ttl = 300  # 5 minutes for local cache

    def _get_deploy_version(self) -> str:
        """Get deploy version for cache invalidation on new deploys."""
        # Try to get from env, fallback to git commit or timestamp
        return os.environ.get("DEPLOY_VERSION", "v1")

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

    def register_many(self, rules: list[BaseRule]) -> "RulesEngineV2":
        for rule in rules:
            self.register(rule)
        return self

    def get_rule(self, rule_code: str) -> BaseRule | None:
        return self._rule_map.get(rule_code)

    def get_rules_by_tag(self, tag: str) -> list[BaseRule]:
        return self._rule_index.get(tag, [])

    def list_rules(self) -> list[dict[str, Any]]:
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

    # ============================================
    # REDIS CACHE METHODS
    # ============================================

    async def _init_cache(self) -> None:
        """Initialize Redis connection lazily."""
        if self._cache is None:
            try:
                self._cache = redis.from_url(  # type: ignore[no-untyped-call]
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=10,
                )
                # Test connection
                await self._cache.ping()
                logger.info("redis_cache_initialized", url=settings.REDIS_URL)
            except Exception as e:
                logger.warning("redis_cache_unavailable", error=str(e))
                self._cache = None

    def _get_rule_ttl(self, rule_code: str) -> int:
        """Get TTL for a specific rule."""
        return self.RULE_TTL_CONFIG.get(rule_code, self.DEFAULT_TTL)

    def _cache_key(self, rule: BaseRule, context: RuleContext) -> str:
        """Generate cache key based on rule and relevant context fields."""
        relevant_data: dict[str, Any] = {}

        # Extract only fields relevant to this rule's tags
        for tag in rule.relevance_tags:
            relevant_data[tag] = self._extract_tag_data(context, tag)

        # Include rule version in key for deploy invalidation
        relevant_data["_version"] = self._cache_version

        # Hash the relevant data
        data_str = json.dumps(relevant_data, sort_keys=True, default=str)
        hash_val = hashlib.md5(data_str.encode()).hexdigest()[:16]
        return f"rule:{rule.rule_code}:{self._cache_version}:{hash_val}"

    def _extract_tag_data(self, context: RuleContext, tag: str) -> dict[str, Any] | None:
        """Extract data relevant to a specific tag from context."""
        doc = context.document

        tag_extractors: dict[str, Callable[[], dict[str, Any] | None]] = {
            "icms": lambda: {
                "v_icms": self._safe_get(doc, "icms.v_icms"),
                "v_bc": self._safe_get(doc, "icms.v_bc"),
                "cst": self._safe_get(doc, "icms.cst"),
            },
            "interstate": lambda: {
                "uf_origem": self._safe_get(doc, "uf_inicio"),
                "uf_destino": self._safe_get(doc, "uf_fim"),
            },
            "icms_st": lambda: {
                "v_bc_st": self._safe_get(doc, "icms.v_bc_st"),
                "v_icms_st": self._safe_get(doc, "icms.v_icms_st"),
                "ncm": self._safe_get(doc, "ncm"),
                "cst": self._safe_get(doc, "icms.cst"),
            },
            "freight": lambda: {
                "freight_value": self._safe_get(doc, "freight_value"),
            },
            "weight": lambda: {
                "weight": self._safe_get(doc, "weight"),
            },
            "cubage": lambda: {
                "volume": self._safe_get(doc, "volume"),
            },
            "advalorem": lambda: {
                "total_value": self._safe_get(doc, "total_value"),
                "v_advalorem": self._safe_get(doc, "components.v_advalorem"),
            },
            "gris": lambda: {
                "total_value": self._safe_get(doc, "total_value"),
                "v_gris": self._safe_get(doc, "components.v_gris"),
            },
            "sicoban": lambda: {
                "cep_origem": self._safe_get(doc, "cep_origem")
                or self._safe_get(doc, "rem_endereco.cep"),
                "cep_destino": self._safe_get(doc, "cep_destino")
                or self._safe_get(doc, "dest_endereco.cep"),
                "tipo_carga": self._safe_get(doc, "tipo_carga", "G"),
                "modalidade": self._safe_get(doc, "modalidade", "R"),
            },
            "redespacho": lambda: {
                "has_redespacho": self._safe_get(doc, "has_redespacho"),
                "redespacho_details": self._safe_get(doc, "redespacho_details"),
            },
            "toll": lambda: {
                "pedagios": self._safe_get(doc, "modal_rodoviario.pedagio"),
            },
            "cte_complementar": lambda: {
                "tp_emis": self._safe_get(doc, "tp_emis"),
                "ch_cte_ref": self._safe_get(doc, "ch_cte_ref"),
            },
            # NF-e Tags
            "nfe_icms": lambda: {
                "icms_cst": self._safe_get(doc, "icms.cst"),
                "icms_csosn": self._safe_get(doc, "icms.csosn"),
                "v_bc": self._safe_get(doc, "icms.v_bc"),
                "v_icms": self._safe_get(doc, "icms.v_icms"),
                "v_icms_st": self._safe_get(doc, "icms.v_icms_st"),
                "v_bc_st": self._safe_get(doc, "icms.v_bc_st"),
                "p_icms": self._safe_get(doc, "icms.p_icms"),
                "p_mva_st": self._safe_get(doc, "icms.p_mva_st"),
                "p_icms_st": self._safe_get(doc, "icms.p_icms_st"),
            },
            "nfe_difal": lambda: {
                "uf_origem": self._safe_get(doc, "emit.enderEmit.UF"),
                "uf_destino": self._safe_get(doc, "dest.enderDest.UF"),
                "ind_ie_dest": self._safe_get(doc, "dest.indIEDest"),
                "v_bc": self._safe_get(doc, "icms.v_bc"),
                "v_icms": self._safe_get(doc, "icms.v_icms"),
            },
            "nfe_fcp": lambda: {
                "v_fcp": self._safe_get(doc, "icms.v_fcp"),
                "v_fcp_st": self._safe_get(doc, "icms.v_fcp_st"),
                "v_fcp_st_ret": self._safe_get(doc, "icms.v_fcp_st_ret"),
                "p_fcp": self._safe_get(doc, "icms.p_fcp"),
                "p_fcp_st": self._safe_get(doc, "icms.p_fcp_st"),
                "uf_destino": self._safe_get(doc, "dest.enderDest.UF"),
            },
            "nfe_frete": lambda: {
                "mod_frete": self._safe_get(doc, "transp.modFrete"),
                "v_frete": self._safe_get(doc, "total.ICMSTot.vFrete"),
                "v_seg": self._safe_get(doc, "total.ICMSTot.vSeg"),
            },
            "nfe_cfop": lambda: {
                "cfop": self._safe_get(doc, "det.prod.CFOP"),
                "mod_frete": self._safe_get(doc, "transp.modFrete"),
            },
            "nfe_ncm_cest": lambda: {
                "ncm": self._safe_get(doc, "det.prod.NCM"),
                "cest": self._safe_get(doc, "det.prod.CEST"),
                "cst": self._safe_get(doc, "icms.cst"),
                "csosn": self._safe_get(doc, "icms.csosn"),
            },
            "nfe_valor_total": lambda: {
                "v_nf": self._safe_get(doc, "total.ICMSTot.vNF"),
                "v_prod": self._safe_get(doc, "total.ICMSTot.vProd"),
                "v_frete": self._safe_get(doc, "total.ICMSTot.vFrete"),
                "v_seg": self._safe_get(doc, "total.ICMSTot.vSeg"),
                "v_desc": self._safe_get(doc, "total.ICMSTot.vDesc"),
                "v_outro": self._safe_get(doc, "total.ICMSTot.vOutro"),
                "v_icms": self._safe_get(doc, "total.ICMSTot.vICMS"),
                "v_icms_st": self._safe_get(doc, "total.ICMSTot.vST"),
                "v_fcp": self._safe_get(doc, "total.ICMSTot.vFCP"),
                "v_fcp_st": self._safe_get(doc, "total.ICMSTot.vFCPST"),
                "v_fcp_st_ret": self._safe_get(doc, "total.ICMSTot.vFCPSTRet"),
            },
            "nfe_transportadora": lambda: {
                "mod_frete": self._safe_get(doc, "transp.modFrete"),
                "transportadora_cnpj": self._safe_get(doc, "transp.transporta.CNPJ"),
                "transportadora_cpf": self._safe_get(doc, "transp.transporta.CPF"),
                "transportadora_rntrc": self._safe_get(doc, "transp.transporta.RNTRC"),
                "veic_transp_placa": self._safe_get(doc, "transp.veicTransp.placa"),
            },
            "nfe_destinatario": lambda: {
                "dest_cnpj": self._safe_get(doc, "dest.CNPJ"),
                "dest_cpf": self._safe_get(doc, "dest.CPF"),
                "dest_ie": self._safe_get(doc, "dest.IE"),
                "ind_ie_dest": self._safe_get(doc, "dest.indIEDest"),
                "dest_uf": self._safe_get(doc, "dest.enderDest.UF"),
                "dest_cmun": self._safe_get(doc, "dest.enderDest.cMun"),
            },
            "nfe_peso_volume": lambda: {
                "peso_bruto": self._safe_get(doc, "transp.vol.pesoB"),
                "peso_liquido": self._safe_get(doc, "transp.vol.pesoL"),
                "q_vol": self._safe_get(doc, "transp.vol.qVol"),
            },
            "nfe_complementar": lambda: {
                "ref_nfe": self._safe_get(doc, "infNFeSupl.refNFe"),
                "tp_emis": self._safe_get(doc, "ide.tpEmis"),
            },
            "nfe_cancelamento": lambda: {
                "ch_nfe": self._safe_get(doc, "protNFe.infProt.chNFe"),
                "dh_emi": self._safe_get(doc, "ide.dhEmi"),
                "dh_evento": self._safe_get(doc, "evento.dhEvento"),
            },
            "nfe_regime_especial": lambda: {
                "crt": self._safe_get(doc, "emit.CRT"),
                "csosn": self._safe_get(doc, "icms.csosn"),
                "cst": self._safe_get(doc, "icms.cst"),
                "cfop": self._safe_get(doc, "det.prod.CFOP"),
            },
        }

        extractor = tag_extractors.get(tag)
        if extractor:
            return extractor()
        return None

    async def _get_cached_result(
        self, rule: BaseRule, context: RuleContext
    ) -> DiscrepancyResult | None:
        """Get cached result for a rule evaluation."""
        cache_key = self._cache_key(rule, context)

        # Try Redis first
        if self._cache:
            try:
                cached = await self._cache.get(cache_key)
                if cached:
                    logger.debug("cache_hit_redis", rule_code=rule.rule_code, key=cache_key)
                    return DiscrepancyResult(**json.loads(cached))
            except Exception as e:
                logger.warning("redis_cache_get_error", rule_code=rule.rule_code, error=str(e))

        # Fallback to local in-memory cache
        if cache_key in self._local_cache:
            result, expiry = self._local_cache[cache_key]

            if time.time() < expiry:
                logger.debug("cache_hit_local", rule_code=rule.rule_code, key=cache_key)
                return result
            else:
                del self._local_cache[cache_key]

        logger.debug("cache_miss", rule_code=rule.rule_code, key=cache_key)
        return None

    async def _set_cached_result(
        self, rule: BaseRule, context: RuleContext, result: DiscrepancyResult
    ) -> None:
        """Cache a rule evaluation result."""
        cache_key = self._cache_key(rule, context)
        ttl = self._get_rule_ttl(rule.rule_code)

        # Serialize result
        result_dict = {
            "rule_code": result.rule_code,
            "rule_name": result.rule_name,
            "discrepancy_type": result.discrepancy_type.value,
            "triggered": result.triggered,
            "expected_value": result.expected_value,
            "actual_value": result.actual_value,
            "difference": result.difference,
            "difference_pct": result.difference_pct,
            "details": result.details,
            "evidence": result.evidence,
            "severity": result.severity,
        }
        result_json = json.dumps(result_dict, default=str)

        # Try Redis first
        if self._cache:
            try:
                await self._cache.setex(cache_key, ttl, result_json)
                logger.debug("cache_set_redis", rule_code=rule.rule_code, key=cache_key, ttl=ttl)
                return
            except Exception as e:
                logger.warning("redis_cache_set_error", rule_code=rule.rule_code, error=str(e))

        # Fallback to local in-memory cache
        self._local_cache[cache_key] = (result, time.time() + min(ttl, self._local_cache_ttl))
        logger.debug(
            "cache_set_local",
            rule_code=rule.rule_code,
            key=cache_key,
            ttl=min(ttl, self._local_cache_ttl),
        )

    async def invalidate_cache(self, rule_code: str | None = None, tag: str | None = None) -> int:
        """Invalidate cache entries. Can invalidate by rule_code, tag, or all."""
        if not self._cache:
            # Clear local cache
            if rule_code:
                keys_to_del = [k for k in self._local_cache if f"rule:{rule_code}:" in k]
            elif tag:
                # Find rules with this tag and clear their cache
                rule_codes = [r.rule_code for r in self._rule_index.get(tag, [])]
                keys_to_del = [
                    k for k in self._local_cache if any(f"rule:{rc}:" in k for rc in rule_codes)
                ]
            else:
                keys_to_del = list(self._local_cache.keys())

            for k in keys_to_del:
                del self._local_cache[k]
            logger.info(
                "local_cache_invalidated", count=len(keys_to_del), rule_code=rule_code, tag=tag
            )
            return len(keys_to_del)

        try:
            if rule_code:
                pattern = f"rule:{rule_code}:*"
            elif tag:
                rule_codes = [r.rule_code for r in self._rule_index.get(tag, [])]
                if not rule_codes:
                    return 0
                pattern = f"rule:({','.join(rule_codes)}):*"
            else:
                pattern = "rule:*"

            # Use SCAN to find keys (non-blocking)
            deleted = 0
            async for key in self._cache.scan_iter(match=pattern):
                await self._cache.delete(key)
                deleted += 1

            logger.info("redis_cache_invalidated", count=deleted, pattern=pattern)
            return deleted
        except Exception as e:
            logger.error("redis_cache_invalidate_error", error=str(e))
            return 0

    async def invalidate_freight_table_cache(self) -> int:
        """Invalidate all freight-related rule caches when freight table is updated."""
        freight_tags = ["freight", "weight", "cubage", "sicoban", "advalorem", "gris", "toll"]
        total = 0
        for tag in freight_tags:
            total += await self.invalidate_cache(tag=tag)
        logger.info("freight_table_cache_invalidated", total_cleared=total)
        return total

    async def invalidate_reference_data_cache(self) -> int:
        """Invalidate ICMS and SICOBAN reference data caches."""
        total = 0
        # ICMS rules
        total += await self.invalidate_cache(rule_code="ICMS_DIFAL")
        total += await self.invalidate_cache(rule_code="ICMS_FCP")
        total += await self.invalidate_cache(rule_code="ICMS_ST")
        # SICOBAN
        total += await self.invalidate_cache(rule_code="SICOBAN_TABLE_REAL")
        logger.info("reference_data_cache_invalidated", total_cleared=total)
        return total

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats: dict[str, Any] = {
            "local_cache_size": len(self._local_cache),
            "redis_connected": self._cache is not None,
            "cache_version": self._cache_version,
        }

        if self._cache:
            try:
                info = await self._cache.info("memory")
                stats["redis_memory_used"] = info.get("used_memory_human", "unknown")
                stats["redis_connected"] = True
            except Exception:
                stats["redis_connected"] = False

        return stats

    def get_relevant_rules(self, context: RuleContext) -> list[BaseRule]:
        """Filter rules based on document context for performance"""
        relevant = []
        doc = context.document

        # Determine relevant tags from document
        tags = self._determine_relevant_tags(doc)

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

        logger.debug(
            "rules_filtered", total=len(self._rules), relevant=len(relevant), tags=list(tags)
        )
        return relevant

    def _determine_relevant_tags(self, doc: dict[str, Any]) -> set[str]:
        """Determine relevant tags based on document content."""
        tags: set[str] = set()

        # ICMS tags (CT-e)
        self._add_cte_tags(doc, tags)

        # Freight tags
        self._add_freight_tags(doc, tags)

        # Redespacho
        if self._safe_get(doc, "has_redespacho"):
            tags.add("redespacho")

        # Pedágio
        if self._safe_get(doc, "modal_rodoviario.pedagio"):
            tags.add("toll")

        # CT-e Complementar
        if self._safe_get(doc, "modelo") in ["57", "67"]:
            tags.add("cte_complementar")

        # NF-e Tags
        if self._is_nfe_document(doc):
            self._add_nfe_tags(doc, tags)

        return tags

    def _add_cte_tags(self, doc: dict[str, Any], tags: set[str]) -> None:
        """Add CT-e specific tags."""
        if self._safe_get(doc, "icms.v_icms") is not None:
            tags.add("icms")
        if self._safe_get(doc, "uf_inicio") and self._safe_get(doc, "uf_fim"):
            tags.add("interstate")
        if self._safe_get(doc, "icms.cst") in ["10", "30", "60", "70", "90"]:
            tags.add("icms_st")

    def _add_freight_tags(self, doc: dict[str, Any], tags: set[str]) -> None:
        """Add freight-related tags."""
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

    def _is_nfe_document(self, doc: dict[str, Any]) -> bool:
        """Check if document is NF-e (modelo 55) or has NF-e structure."""
        modelo = self._safe_get(doc, "modelo") or self._safe_get(doc, "ide.mod")
        return modelo == "55" or "ide" in doc or "emit" in doc or "dest" in doc or "det" in doc

    def _add_nfe_tags(self, doc: dict[str, Any], tags: set[str]) -> None:
        """Add NF-e specific tags."""
        # ICMS tags
        if self._safe_get(doc, "icms.cst") or self._safe_get(doc, "icms.csosn"):
            tags.add("nfe_icms")
        if self._safe_get(doc, "emit.enderEmit.UF") and self._safe_get(
            doc, "dest.enderDest.UF"
        ):
            tags.add("nfe_difal")
        if self._safe_get(doc, "icms.v_fcp") is not None:
            tags.add("nfe_fcp")

        # Frete tags
        if self._safe_get(doc, "transp.modFrete") is not None:
            tags.add("nfe_frete")
            tags.add("nfe_cfop")

        # NCM/CEST
        if self._safe_get(doc, "det.prod.NCM") or self._safe_get(doc, "det.prod.CEST"):
            tags.add("nfe_ncm_cest")

        # Valor total
        if self._safe_get(doc, "total.ICMSTot.vNF") is not None:
            tags.add("nfe_valor_total")

        # Transportadora
        if self._safe_get(doc, "transp.modFrete") in ["0", "1", "2", "3"]:
            tags.add("nfe_transportadora")

        # Destinatário
        if self._safe_get(doc, "dest.CNPJ") or self._safe_get(doc, "dest.CPF"):
            tags.add("nfe_destinatario")

        # Peso/Volume
        if self._safe_get(doc, "transp.vol.pesoB") or self._safe_get(doc, "transp.vol.qVol"):
            tags.add("nfe_peso_volume")

        # Complementar/Cancelamento
        if self._safe_get(doc, "infNFeSupl.refNFe"):
            tags.add("nfe_complementar")
        if self._safe_get(doc, "protNFe.infProt.chNFe"):
            tags.add("nfe_cancelamento")

        # Regime especial
        if self._safe_get(doc, "emit.CRT"):
            tags.add("nfe_regime_especial")

    async def evaluate_all(self, context: RuleContext) -> list[DiscrepancyResult]:
        """Run all relevant rules with Redis caching"""
        # Initialize cache lazily
        await self._init_cache()

        results = []
        relevant_rules = self.get_relevant_rules(context)
        cache_hits = 0
        cache_misses = 0

        logger.info("rules_evaluation_start", total_rules=len(relevant_rules))

        for rule in relevant_rules:
            try:
                # Try to get cached result first
                cached_result = await self._get_cached_result(rule, context)
                if cached_result is not None:
                    cache_hits += 1
                    if cached_result.triggered:
                        results.append(cached_result)
                        logger.info(
                            "discrepancy_found_cached",
                            rule_code=rule.rule_code,
                            difference=cached_result.difference,
                            severity=cached_result.severity,
                        )
                    continue

                cache_misses += 1

                # Evaluate rule if not cached
                result = await rule.evaluate(context)

                # Cache the result (even if not triggered, to avoid re-evaluation)
                await self._set_cached_result(rule, context, result)

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

        logger.info(
            "rules_evaluation_complete",
            triggered=len(results),
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            hit_rate=round(cache_hits / max(1, cache_hits + cache_misses) * 100, 1),
        )
        return results

    def _safe_get(self, data: dict[str, Any], path: str, default: Any = None) -> Any:
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


# ============================================
# DEFAULT ENGINE FACTORY (Singleton)
# ============================================


class _EngineSingleton:
    """Singleton container for the rules engine instance."""

    def __init__(self) -> None:
        self._instance: RulesEngineV2 | None = None

    @property
    def instance(self) -> RulesEngineV2 | None:
        return self._instance

    @instance.setter
    def instance(self, value: RulesEngineV2) -> None:
        self._instance = value


# Module-level singleton container
_engine_singleton = _EngineSingleton()

# Built-in rule classes map for fallback - populated lazily to avoid circular imports
_BUILTIN_RULES: dict[str, type] = {}
_builtin_rules_loaded: list[bool] = [False]  # Use list as mutable container


def _load_builtin_rules() -> dict[str, type]:
    """Lazy load built-in rule classes."""
    if not _builtin_rules_loaded[0]:
        # Import here to avoid circular imports
        from app.services.rules_critical import (  # noqa: PLC0415
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

        _BUILTIN_RULES.update({
            "ICMS_DIFAL": ICMSDifferentialRule,
            "ICMS_FCP": FCPRule,
            "ICMS_ST": ICMSSTRule,
            "FRETE_PESO_VALOR": FreightWeightValueRule,
            "FRETE_CUBAGE": FreightCubageRule,
            "PESO_REAL_VS_FATURADO": PesoRealVsFaturadoRule,
            "VALOR_MINIMO_FRETE": ValorMinimoFreteRule,
            "REDESPACHO_VALIDACAO": RedespachoRule,
            "PEDAGIO_CONFERENCIA": TollPlazaRule,
            "AD_VALOREM": AdValoremRule,
            "GRIS": GRISRule,
            "SICOBAN_TABLE_REAL": SicobanTableRuleReal,
            "CTE_ANULACAO": ComplementaryCTEAnulationRule,
            "CTE_SUBSTITUICAO": ComplementaryCTESubstitutionRule,
            "CTE_COMPLEMENTO_VALOR": ComplementaryCTEComplementRule,
            "ML_ANOMALY": MLAnomalyRule,
        })
        _builtin_rules_loaded[0] = True
    return _BUILTIN_RULES


async def _load_rules_from_db(engine: RulesEngineV2) -> int:
    """Load active rules from database and register them in the engine."""

    db = await get_prisma()
    try:
        rules = await db.rule.find_many(where={"isActive": True})

        builtin = _load_builtin_rules()
        loaded = 0

        for rule_record in rules:
            rule_class = builtin.get(rule_record.code)
            if not rule_class:
                logger.warning("rule_class_not_found", rule_code=rule_record.code)
                continue

            # Create instance with DB config
            config = rule_record.configJson or {}
            config["_db_version"] = rule_record.version
            rule_instance = rule_class(config=config)

            engine.register(rule_instance)
            loaded += 1

        logger.info("rules_loaded_from_db", count=loaded)
        return loaded

    except Exception as e:
        logger.warning("db_rules_load_failed", error=str(e))
        return 0


async def _register_builtin_fallback(engine: RulesEngineV2) -> int:
    """Register all built-in rules as fallback."""
    builtin = _load_builtin_rules()
    loaded = 0

    for rule_code, rule_class in builtin.items():
        try:
            rule_instance = rule_class()
            engine.register(rule_instance)
            loaded += 1
        except Exception as e:
            logger.error("builtin_rule_registration_failed", rule_code=rule_code, error=str(e))

    logger.info("builtin_fallback_registered", count=loaded)
    return loaded


async def create_engine_v2() -> RulesEngineV2:
    """Create or get singleton engine with DB rules + built-in fallback"""
    if _engine_singleton.instance is not None:
        return _engine_singleton.instance

    engine = RulesEngineV2()

    # Try to load from DB first
    loaded = await _load_rules_from_db(engine)

    # If no rules loaded from DB, use built-in fallback
    if loaded == 0:
        logger.info("using_builtin_fallback_rules")
        await _register_builtin_fallback(engine)

    _engine_singleton.instance = engine
    return engine


async def reload_engine_rules() -> RulesEngineV2:
    """Force reload rules from DB (e.g., after rule updates via API)."""
    engine = RulesEngineV2()
    loaded = await _load_rules_from_db(engine)

    if loaded == 0:
        logger.info("fallback_to_builtin_on_reload")
        await _register_builtin_fallback(engine)

    _engine_singleton.instance = engine
    logger.info("engine_reloaded", rules_loaded=loaded)
    return engine


def get_engine_instance() -> RulesEngineV2 | None:
    """Get the singleton engine instance (for cache invalidation from other services)"""
    return _engine_singleton.instance
