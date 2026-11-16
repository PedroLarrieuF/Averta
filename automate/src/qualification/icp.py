"""ICP (Ideal Customer Profile) definition and rules."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum

from utils.config_loader import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)


class ICPSegment(str, Enum):
    """ICP Segment categories."""
    DISTRIBUIDORAS = "distribuidoras"
    ATACADISTAS = "atacadistas"
    INDUSTRIAS = "industrias"
    FARMA_HOSPITALAR = "farma_hospitalar"
    ALIMENTICIAS = "alimenticias"
    BEBIDAS = "bebidas"
    AUTOPECAS = "autopeças"
    MATERIAL_CONSTRUCAO = "material_construcao"
    ECOMMERCE_LOGISTICA = "ecommerce_logistica"
    GRANDE_VOLUME = "grande_volume"
    OUTROS = "outros"


@dataclass
class ICPCriteria:
    """ICP matching criteria."""
    # Operational Fit keywords (weight: 40%)
    operational_keywords: Dict[str, List[str]] = field(default_factory=dict)

    # Commercial Fit keywords (weight: 35%)
    commercial_keywords: Dict[str, List[str]] = field(default_factory=dict)

    # Data Confidence indicators (weight: 25%)
    confidence_indicators: Dict[str, List[str]] = field(default_factory=dict)

    # Negative keywords (exclude)
    negative_keywords: List[str] = field(default_factory=list)

    # Decision maker roles
    decision_maker_roles: List[str] = field(default_factory=list)

    # Priority segments
    priority_segments: List[ICPSegment] = field(default_factory=list)


class ICPDefinition:
    """ICP Definition loaded from configuration."""

    def __init__(self):
        self.settings = get_settings()
        self.criteria = self._load_criteria()

    def _load_criteria(self) -> ICPCriteria:
        """Load ICP criteria from settings."""
        criteria = ICPCriteria()

        # Operational Fit keywords
        op_fit = self.settings.__dict__.get('qualification_operational_fit', {})
        if op_fit:
            criteria.operational_keywords = {
                'embarcadora': op_fit.get('keywords_embarcadora', {}).get('terms', []),
                'volume': op_fit.get('keywords_volume', {}).get('terms', []),
                'estrutura': op_fit.get('keywords_estrutura', {}).get('terms', []),
                'recorrencia': op_fit.get('keywords_recorrencia', {}).get('terms', []),
            }

        # Commercial Fit keywords
        com_fit = self.settings.__dict__.get('qualification_commercial_fit', {})
        if com_fit:
            criteria.commercial_keywords = {
                'porte': {
                    'grande': com_fit.get('porte_keywords', {}).get('grande', []),
                    'medio': com_fit.get('porte_keywords', {}).get('medio', []),
                    'pequeno': com_fit.get('porte_keywords', {}).get('pequeno', []),
                },
                'estrutura': com_fit.get('estrutura_keywords', {}).get('terms', []),
                'decisores': com_fit.get('decisores_keywords', {}).get('terms', []),
                'canais': com_fit.get('canais_institucionais', {}).get('terms', []),
            }

        # Data Confidence indicators
        data_conf = self.settings.__dict__.get('qualification_data_confidence', {})
        if data_conf:
            criteria.confidence_indicators = {
                'site_verificado': ['website', 'site'],
                'telefone_verificado': ['phone', 'telefone'],
                'segmento_confirmado': ['categories', 'types'],
                'linkedin_verificavel': ['linkedin'],
                'fontes_registradas': ['source_query', 'raw_data'],
            }

        # Negative keywords
        criteria.negative_keywords = self.settings.__dict__.get(
            'icp_keywords_negative_keywords', []
        )

        # Decision maker roles
        criteria.decision_maker_roles = self.settings.__dict__.get(
            'icp_keywords_decision_maker_keywords', {}
        ).get('roles', [])

        # Priority segments
        criteria.priority_segments = [
            ICPSegment.DISTRIBUIDORAS,
            ICPSegment.ATACADISTAS,
            ICPSegment.INDUSTRIAS,
            ICPSegment.FARMA_HOSPITALAR,
            ICPSegment.ALIMENTICIAS,
            ICPSegment.BEBIDAS,
            ICPSegment.AUTOPECAS,
            ICPSegment.MATERIAL_CONSTRUCAO,
            ICPSegment.ECOMMERCE_LOGISTICA,
            ICPSegment.GRANDE_VOLUME,
        ]

        return criteria

    def is_negative_match(self, text: str) -> bool:
        """Check if text matches negative keywords."""
        text_lower = text.lower()
        for keyword in self.criteria.negative_keywords:
            if keyword.lower() in text_lower:
                return True
        return False

    def get_segment_from_categories(self, categories: List[str]) -> ICPSegment:
        """Determine ICP segment from Google categories."""
        if not categories:
            return ICPSegment.OUTROS

        categories_lower = [c.lower() for c in categories]

        # Check each priority segment
        segment_keywords = {
            ICPSegment.DISTRIBUIDORAS: ['distribuidor', 'distribuidora', 'distribuicao', 'distribution'],
            ICPSegment.ATACADISTAS: ['atacadista', 'atacado', 'atacarejo', 'wholesale', 'cash and carry'],
            ICPSegment.INDUSTRIAS: ['industria', 'industrial', 'fabrica', 'manufacturing', 'factory'],
            ICPSegment.FARMA_HOSPITALAR: ['farmacia', 'farmaceutica', 'hospitalar', 'medicamento', 'drogaria', 'pharmacy'],
            ICPSegment.ALIMENTICIAS: ['alimentos', 'alimenticia', 'food', 'frigorifico', 'bebidas', 'beverages'],
            ICPSegment.BEBIDAS: ['bebidas', 'cerveja', 'vinho', 'refrigerante', 'distribuidora de bebidas'],
            ICPSegment.AUTOPECAS: ['autopeças', 'auto pecas', 'automotive', 'pecas automotivas'],
            ICPSegment.MATERIAL_CONSTRUCAO: ['construcao', 'material de construcao', 'building material', 'casa da construcao'],
            ICPSegment.ECOMMERCE_LOGISTICA: ['ecommerce', 'e-commerce', 'logistica', 'fulfillment', 'entrega', 'delivery'],
            ICPSegment.GRANDE_VOLUME: ['logistica', 'transportes', 'fretes', 'cargas', 'expedicao', 'armazem', 'deposito'],
        }

        for segment, keywords in segment_keywords.items():
            for cat in categories_lower:
                for kw in keywords:
                    if kw in cat:
                        return segment

        return ICPSegment.OUTROS

    def calculate_operational_fit(self, lead_data: Dict) -> float:
        """Calculate operational fit score (0-100)."""
        score = 0.0
        max_score = 100.0

        # Combine searchable text
        searchable_text = " ".join(filter(None, [
            lead_data.get('name', ''),
            lead_data.get('trade_name', ''),
            lead_data.get('description', ''),
            " ".join(lead_data.get('categories', [])),
            " ".join(lead_data.get('emails_from_website', [])),
        ])).lower()

        if not searchable_text:
            return 0.0

        weights = {
            'embarcadora': 0.30,
            'volume': 0.25,
            'estrutura': 0.25,
            'recorrencia': 0.20,
        }

        for category, weight in weights.items():
            keywords = self.criteria.operational_keywords.get(category, [])
            if not keywords:
                continue

            matches = sum(1 for kw in keywords if kw.lower() in searchable_text)
            if matches > 0:
                # Normalize: max 5 matches = full weight
                category_score = min(matches / 5.0, 1.0) * weight * 100
                score += category_score

        return min(score, max_score)

    def calculate_commercial_fit(self, lead_data: Dict) -> float:
        """Calculate commercial fit score (0-100)."""
        score = 0.0
        max_score = 100.0

        searchable_text = " ".join(filter(None, [
            lead_data.get('name', ''),
            lead_data.get('trade_name', ''),
            lead_data.get('description', ''),
            " ".join(lead_data.get('categories', [])),
        ])).lower()

        if not searchable_text:
            return 0.0

        # Porte (30%)
        porte_keywords = self.criteria.commercial_keywords.get('porte', {})
        porte_score = 0.0

        grande_matches = sum(1 for kw in porte_keywords.get('grande', []) if kw.lower() in searchable_text)
        medio_matches = sum(1 for kw in porte_keywords.get('medio', []) if kw.lower() in searchable_text)
        pequeno_matches = sum(1 for kw in porte_keywords.get('pequeno', []) if kw.lower() in searchable_text)

        if grande_matches > 0:
            porte_score = 1.0
        elif medio_matches > 0:
            porte_score = 0.6
        elif pequeno_matches > 0:
            porte_score = 0.3

        score += porte_score * 0.30 * 100

        # Estrutura (25%)
        estrutura_kws = self.criteria.commercial_keywords.get('estrutura', [])
        estrutura_matches = sum(1 for kw in estrutura_kws if kw.lower() in searchable_text)
        estrutura_score = min(estrutura_matches / 3.0, 1.0)
        score += estrutura_score * 0.25 * 100

        # Decisores (25%)
        decisor_kws = self.criteria.commercial_keywords.get('decisores', [])
        decisor_matches = sum(1 for kw in decisor_kws if kw.lower() in searchable_text)
        decisor_score = min(decisor_matches / 3.0, 1.0)
        score += decisor_score * 0.25 * 100

        # Canais institucionais (20%)
        canal_kws = self.criteria.commercial_keywords.get('canais', [])
        canal_matches = sum(1 for kw in canal_kws if kw.lower() in searchable_text)
        canal_score = min(canal_matches / 3.0, 1.0)
        score += canal_score * 0.20 * 100

        return min(score, max_score)

    def calculate_data_confidence(self, lead_data: Dict) -> float:
        """Calculate data confidence score (0-100)."""
        score = 0.0
        max_score = 100.0

        # Site verificado (35%)
        if lead_data.get('website') and lead_data.get('website_verified'):
            score += 0.35 * 100
        elif lead_data.get('website'):
            score += 0.20 * 100

        # Telefone verificado (25%)
        if lead_data.get('phone') and lead_data.get('phone_verified'):
            score += 0.25 * 100
        elif lead_data.get('phone'):
            score += 0.15 * 100

        # Segmento confirmado (20%)
        if lead_data.get('categories'):
            score += 0.20 * 100

        # LinkedIn verificável (10%)
        if lead_data.get('linkedin') and lead_data.get('linkedin_verified'):
            score += 0.10 * 100
        elif lead_data.get('linkedin'):
            score += 0.05 * 100

        # Fontes registradas (10%)
        if lead_data.get('source_query') and lead_data.get('raw_data'):
            score += 0.10 * 100

        return min(score, max_score)


# Global instance
_icp_definition: Optional[ICPDefinition] = None


def get_icp_definition() -> ICPDefinition:
    """Get global ICP definition instance."""
    global _icp_definition
    if _icp_definition is None:
        _icp_definition = ICPDefinition()
    return _icp_definition