"""Lead scoring and qualification logic."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id
from storage.models import (
    QualifiedLead, DecisionMaker, InstitutionalContact,
    LeadClassification, ContactType, EnrichmentStatus
)
from .icp import get_icp_definition, ICPSegment

logger = get_logger(__name__)


@dataclass
class ScoringResult:
    """Result of lead scoring."""
    total_score: float
    classification: LeadClassification
    operational_fit_score: float
    commercial_fit_score: float
    data_confidence_score: float
    details: Dict[str, Any]


class LeadScorer:
    """Scores and classifies leads based on ICP criteria."""

    def __init__(self):
        self.settings = get_settings()
        self.icp = get_icp_definition()

        # Scoring weights
        self.weights = {
            'operational_fit': self.settings.qual_weights_operational_fit,
            'commercial_fit': self.settings.qual_weights_commercial_fit,
            'data_confidence': self.settings.qual_weights_data_confidence,
        }

        # Classification thresholds
        self.thresholds = {
            'A': self.settings.qual_thresholds_A_min,
            'B': self.settings.qual_thresholds_B_min,
            'C': self.settings.qual_thresholds_C_min,
        }

    def score_lead(self, lead_data: Dict) -> ScoringResult:
        """Score a lead based on all criteria."""
        # Calculate dimensional scores
        operational_fit = self.icp.calculate_operational_fit(lead_data)
        commercial_fit = self.icp.calculate_commercial_fit(lead_data)
        data_confidence = self.icp.calculate_data_confidence(lead_data)

        # Calculate weighted total
        total_score = (
            operational_fit * self.weights['operational_fit'] +
            commercial_fit * self.weights['commercial_fit'] +
            data_confidence * self.weights['data_confidence']
        )

        # Determine classification
        classification = self._classify(total_score)

        # Determine segment
        segment = self.icp.get_segment_from_categories(
            lead_data.get('categories', [])
        )

        details = {
            'segment': segment.value,
            'operational_fit_details': self._get_operational_fit_details(lead_data),
            'commercial_fit_details': self._get_commercial_fit_details(lead_data),
            'data_confidence_details': self._get_data_confidence_details(lead_data),
            'negative_match': self.icp.is_negative_match(
                " ".join(filter(None, [
                    lead_data.get('name', ''),
                    lead_data.get('description', ''),
                ]))
            ),
        }

        return ScoringResult(
            total_score=round(total_score, 2),
            classification=classification,
            operational_fit_score=round(operational_fit, 2),
            commercial_fit_score=round(commercial_fit, 2),
            data_confidence_score=round(data_confidence, 2),
            details=details,
        )

    def _classify(self, score: float) -> LeadClassification:
        """Classify lead based on score."""
        if score >= self.thresholds['A']:
            return LeadClassification.A
        elif score >= self.thresholds['B']:
            return LeadClassification.B
        elif score >= self.thresholds['C']:
            return LeadClassification.C
        else:
            return LeadClassification.D

    def _get_operational_fit_details(self, lead_data: Dict) -> Dict:
        """Get detailed operational fit breakdown."""
        searchable = " ".join(filter(None, [
            lead_data.get('name', ''),
            lead_data.get('trade_name', ''),
            lead_data.get('description', ''),
            " ".join(lead_data.get('categories', [])),
        ])).lower()

        details = {}
        for category, keywords in self.icp.criteria.operational_keywords.items():
            matches = [kw for kw in keywords if kw.lower() in searchable]
            details[category] = {
                'matches': matches,
                'count': len(matches),
            }
        return details

    def _get_commercial_fit_details(self, lead_data: Dict) -> Dict:
        """Get detailed commercial fit breakdown."""
        searchable = " ".join(filter(None, [
            lead_data.get('name', ''),
            lead_data.get('trade_name', ''),
            lead_data.get('description', ''),
            " ".join(lead_data.get('categories', [])),
        ])).lower()

        details = {}
        for category, keywords in self.icp.criteria.commercial_keywords.items():
            if isinstance(keywords, dict):
                # Porte keywords
                sub_details = {}
                for sub_cat, sub_kws in keywords.items():
                    matches = [kw for kw in sub_kws if kw.lower() in searchable]
                    sub_details[sub_cat] = {
                        'matches': matches,
                        'count': len(matches),
                    }
                details[category] = sub_details
            else:
                matches = [kw for kw in keywords if kw.lower() in searchable]
                details[category] = {
                    'matches': matches,
                    'count': len(matches),
                }
        return details

    def _get_data_confidence_details(self, lead_data: Dict) -> Dict:
        """Get detailed data confidence breakdown."""
        return {
            'has_website': bool(lead_data.get('website')),
            'website_verified': bool(lead_data.get('website_verified')),
            'has_phone': bool(lead_data.get('phone')),
            'phone_verified': bool(lead_data.get('phone_verified')),
            'has_categories': bool(lead_data.get('categories')),
            'has_linkedin': bool(lead_data.get('linkedin')),
            'linkedin_verified': bool(lead_data.get('linkedin_verified')),
            'has_source_query': bool(lead_data.get('source_query')),
            'has_raw_data': bool(lead_data.get('raw_data')),
        }

    def qualify_scraped_lead(self, scraped_lead_data: Dict) -> QualifiedLead:
        """Convert scraped lead data to qualified lead."""
        # Score the lead
        scoring_result = self.score_lead(scraped_lead_data)

        # Create qualified lead
        qualified = QualifiedLead(
            id=generate_id("ql"),
            scraped_lead_id=scraped_lead_data.get('id'),

            # Basic info
            name=scraped_lead_data.get('name'),
            trade_name=scraped_lead_data.get('trade_name'),
            segment=scoring_result.details.get('segment', 'outros'),
            address=scraped_lead_data.get('address'),
            city=scraped_lead_data.get('city'),
            state=scraped_lead_data.get('state'),
            postal_code=scraped_lead_data.get('postal_code'),
            phone=scraped_lead_data.get('phone'),
            phone_verified=scraped_lead_data.get('phone_verified', False),
            whatsapp=scraped_lead_data.get('whatsapp'),
            whatsapp_verified=scraped_lead_data.get('whatsapp_verified', False),
            email=scraped_lead_data.get('email'),
            email_verified=scraped_lead_data.get('email_verified', False),
            website=scraped_lead_data.get('website'),
            website_verified=scraped_lead_data.get('website_verified', False),
            linkedin=scraped_lead_data.get('linkedin'),
            linkedin_verified=scraped_lead_data.get('linkedin_verified', False),
            rating=scraped_lead_data.get('rating'),
            reviews_count=scraped_lead_data.get('reviews_count'),
            latitude=scraped_lead_data.get('latitude'),
            longitude=scraped_lead_data.get('longitude'),

            # Scoring
            score=scoring_result.total_score,
            classification=scoring_result.classification,
            operational_fit_score=scoring_result.operational_fit_score,
            commercial_fit_score=scoring_result.commercial_fit_score,
            data_confidence_score=scoring_result.data_confidence_score,

            # Metadata
            source_query=scraped_lead_data.get('source_query'),
            scraped_at=scraped_lead_data.get('scraped_at'),
            qualified_at=datetime.utcnow(),
            enrichment_status=EnrichmentStatus.PENDING,
            enrichment_priority=self._determine_enrichment_priority(scoring_result),
            notes=self._generate_notes(scoring_result, scraped_lead_data),
        )

        # Prepare for WhatsApp if qualified
        if scoring_result.classification in [LeadClassification.A, LeadClassification.B]:
            qualified.whatsapp_ready = self._is_whatsapp_ready(qualified)
            if qualified.whatsapp_ready:
                qualified.whatsapp_template_suggested = self._suggest_whatsapp_template(qualified)

        return qualified

    def _determine_enrichment_priority(self, scoring: ScoringResult) -> str:
        """Determine enrichment priority based on score and missing data."""
        if scoring.classification == LeadClassification.C:
            return "high"
        elif scoring.classification == LeadClassification.B:
            return "medium"
        elif scoring.classification == LeadClassification.A:
            return "low"
        return "low"

    def _generate_notes(self, scoring: ScoringResult, lead_data: Dict) -> str:
        """Generate qualification notes."""
        notes = []

        if scoring.details.get('negative_match'):
            notes.append("⚠️ Negative keyword match detected")

        if scoring.classification == LeadClassification.D:
            notes.append("Below qualification threshold")
        elif scoring.classification == LeadClassification.C:
            notes.append("Needs enrichment - missing key data")
        elif scoring.classification == LeadClassification.B:
            notes.append("Qualified lead - good fit")
        elif scoring.classification == LeadClassification.A:
            notes.append("Excellent opportunity - high fit")

        # Add dimensional notes
        if scoring.operational_fit_score < 40:
            notes.append("Low operational fit indicators")
        if scoring.commercial_fit_score < 40:
            notes.append("Low commercial fit indicators")
        if scoring.data_confidence_score < 40:
            notes.append("Low data confidence - verify contacts")

        return "; ".join(notes)

    def _is_whatsapp_ready(self, lead: QualifiedLead) -> bool:
        """Check if lead is ready for WhatsApp outreach."""
        # Must have phone or WhatsApp
        if not lead.phone and not lead.whatsapp:
            return False

        # Must be A or B classification
        if lead.classification not in [LeadClassification.A, LeadClassification.B]:
            return False

        # Should have at least one verified contact
        if not (lead.phone_verified or lead.whatsapp_verified or lead.email_verified):
            return False

        return True

    def _suggest_whatsapp_template(self, lead: QualifiedLead) -> str:
        """Suggest WhatsApp template based on lead segment."""
        templates = {
            'distribuidoras': "Olá {name}, sou da Averta. Vi que a {company} atua com distribuição de {segment} em {city}. Gostaria de apresentar nossa solução de gestão de fretes que reduz custos em até 30%. Podemos conversar?",
            'atacadistas': "Oi {name}, tudo bem? A Averta ajuda atacadistas como a {company} a otimizar a logística de entrega. Temos cases no segmento de {segment} com excelente resultado. Tem 15 min essa semana?",
            'industrias': "Olá {name}, a {company} parece ter uma operação industrial relevante em {city}. Nossa plataforma gerencia fretes de carga industrial com tracking em tempo real. Quer ver como funciona?",
            'farma_hospitalar': "Oi {name}, a Averta tem solução especializada para distribuição farmacêutica/hospitalar. A {company} em {city} pode se beneficiar de controle de temperatura e rastreamento validado. Vamos conversar?",
            'alimenticias': "Olá {name}, vi que a {company} atua no setor alimentício em {city}. Temos experiência com logística de alimentos perecíveis e congelados. Podemos apresentar cases?",
            'bebidas': "Oi {name}, a Averta ajuda distribuidoras de bebidas como a {company} a otimizar rotas e reduzir avarias. Temos cases com redução de 25% no custo de frete. Interesse?",
            'autopeças': "Olá {name}, a {company} em {city} distribui autopeças? Nossa solução gerencia fretes de peças com rastreamento por SKU. Vamos agendar uma demo?",
            'material_construcao': "Oi {name}, a Averta atende várias distribuidoras de material de construção. A {company} pode reduzir custos logísticos com nossa plataforma. Tem 15 min?",
            'ecommerce_logistica': "Olá {name}, vi que a {company} opera e-commerce/logística em {city}. Nossa API integra com seu TMS/ERP para gestão unificada de fretes. Quer ver a integração?",
            'grande_volume': "Oi {name}, a {company} tem grande volume de expedição em {city}? Nossa plataforma otimiza roteirização e auditoria de fretes em escala. Vamos conversar?",
        }

        template = templates.get(lead.segment, templates['distribuidoras'])

        return template.format(
            name="[Nome do Decisor]",
            company=lead.name or lead.trade_name or "[Empresa]",
            segment=lead.segment,
            city=lead.city or "[Cidade]",
        )


class LeadQualificationPipeline:
    """Pipeline for qualifying multiple leads."""

    def __init__(self):
        self.scorer = LeadScorer()
        self.stats = {
            'total': 0,
            'classified_a': 0,
            'classified_b': 0,
            'classified_c': 0,
            'classified_d': 0,
            'errors': 0,
        }

    def qualify_batch(self, leads_data: List[Dict]) -> List[QualifiedLead]:
        """Qualify a batch of leads."""
        qualified_leads = []

        for lead_data in leads_data:
            try:
                self.stats['total'] += 1
                qualified = self.scorer.qualify_scraped_lead(lead_data)
                qualified_leads.append(qualified)

                # Update stats
                if qualified.classification == LeadClassification.A:
                    self.stats['classified_a'] += 1
                elif qualified.classification == LeadClassification.B:
                    self.stats['classified_b'] += 1
                elif qualified.classification == LeadClassification.C:
                    self.stats['classified_c'] += 1
                else:
                    self.stats['classified_d'] += 1

            except Exception as e:
                logger.error(f"Error qualifying lead: {e}")
                self.stats['errors'] += 1

        return qualified_leads

    def get_stats(self) -> Dict:
        """Get qualification statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics."""
        for key in self.stats:
            self.stats[key] = 0