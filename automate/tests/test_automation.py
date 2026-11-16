"""Tests for the automation modules."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from datetime import datetime, date

from src.utils.config_loader import get_settings, Settings
from src.utils.helpers import (
    generate_id, clean_string, normalize_phone, normalize_email,
    is_valid_email, extract_domain, is_business_email, format_date
)
from src.storage.models import (
    QualifiedLead, DecisionMaker, InstitutionalContact,
    LeadClassification, ContactType, EnrichmentStatus, DailyReport
)
from src.qualification.icp import get_icp_definition, ICPSegment
from src.qualification.scorer import LeadScorer, LeadQualificationPipeline
from src.scraper.queries import QueryGenerator


class TestHelpers:
    """Test helper functions."""

    def test_generate_id(self):
        id1 = generate_id("test", "123")
        id2 = generate_id("test", "123")
        id3 = generate_id("test", "456")

        assert id1 == id2  # Same input = same ID
        assert id1 != id3  # Different input = different ID
        assert len(id1) == 12  # MD5 truncated to 12 chars

    def test_clean_string(self):
        assert clean_string("  hello  world  ") == "hello world"
        assert clean_string("test@#$%") == "test"
        assert clean_string("") is None
        assert clean_string(None) is None

    def test_normalize_phone(self):
        # Brazilian numbers
        assert normalize_phone("+55 11 99999-9999") == "+5511999999999"
        assert normalize_phone("(11) 99999-9999") == "+5511999999999"
        assert normalize_phone("11 99999-9999") == "+5511999999999"
        assert normalize_phone("invalid") is None

    def test_normalize_email(self):
        assert normalize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"
        assert normalize_email("invalid") is None
        assert normalize_email("") is None

    def test_is_valid_email(self):
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("invalid") is False
        assert is_valid_email("@example.com") is False

    def test_extract_domain(self):
        assert extract_domain("https://www.example.com/path") == "example.com"
        assert extract_domain("http://example.com") == "example.com"
        assert extract_domain("www.example.com") == "example.com"
        assert extract_domain("") is None

    def test_is_business_email(self):
        assert is_business_email("contato@empresa.com.br") is True
        assert is_business_email("test@gmail.com") is False
        assert is_business_email("test@yahoo.com") is False
        assert is_business_email("test@outlook.com") is False

    def test_format_date(self):
        dt = datetime(2024, 1, 15, 10, 30, 45)
        assert format_date(dt, "%Y-%m-%d") == "2024-01-15"
        assert format_date(dt, "%d/%m/%Y") == "15/01/2024"

        d = date(2024, 1, 15)
        assert format_date(d) == "2024-01-15"


class TestModels:
    """Test data models."""

    def test_qualified_lead_creation(self):
        lead = QualifiedLead(
            id="test_123",
            name="Empresa Teste",
            segment="distribuidoras",
            city="São Paulo",
            state="SP",
            score=85.5,
            classification=LeadClassification.A,
        )

        assert lead.id == "test_123"
        assert lead.name == "Empresa Teste"
        assert lead.classification == LeadClassification.A
        assert lead.score == 85.5

    def test_qualified_lead_to_dict(self):
        lead = QualifiedLead(
            id="test_123",
            name="Empresa Teste",
            segment="distribuidoras",
            city="São Paulo",
            state="SP",
            score=85.5,
            classification=LeadClassification.A,
        )

        data = lead.to_dict()
        assert data['id'] == "test_123"
        assert data['name'] == "Empresa Teste"
        assert data['classification'] == "A"
        assert data['score'] == 85.5

    def test_qualified_lead_from_dict(self):
        data = {
            'id': 'test_123',
            'name': 'Empresa Teste',
            'segment': 'distribuidoras',
            'city': 'São Paulo',
            'state': 'SP',
            'score': 85.5,
            'classification': 'A',
            'operational_fit_score': 80.0,
            'commercial_fit_score': 90.0,
            'data_confidence_score': 85.0,
            'decision_makers': [],
            'institutional_contacts': [],
        }

        lead = QualifiedLead.from_dict(data)
        assert lead.id == "test_123"
        assert lead.classification == LeadClassification.A

    def test_decision_maker(self):
        dm = DecisionMaker(
            lead_id="lead_123",
            name="João Silva",
            role="Diretor de Logística",
            email="joao@empresa.com",
            confidence=0.9,
        )

        assert dm.name == "João Silva"
        assert dm.role == "Diretor de Logística"
        assert dm.confidence == 0.9

    def test_institutional_contact(self):
        ic = InstitutionalContact(
            lead_id="lead_123",
            contact_type=ContactType.BUSINESS_PHONE,
            value="+55 11 99999-9999",
            label="Telefone comercial",
            verified=True,
        )

        assert ic.contact_type == ContactType.BUSINESS_PHONE
        assert ic.value == "+55 11 99999-9999"
        assert ic.verified is True

    def test_daily_report(self):
        report = DailyReport(
            date=date(2024, 1, 15),
            queries_executed=100,
            companies_found=500,
            unique_companies=450,
            leads_classified_a=50,
            leads_classified_b=100,
            leads_classified_c=50,
            leads_classified_d=250,
        )

        data = report.to_dict()
        assert data['date'] == "2024-01-15"
        assert data['queries_executed'] == 100
        assert data['leads_classified_a'] == 50


class TestICP:
    """Test ICP definition."""

    def test_icp_definition_loads(self):
        icp = get_icp_definition()
        assert icp is not None
        assert hasattr(icp, 'criteria')

    def test_negative_keywords(self):
        icp = get_icp_definition()

        # Should match negative keywords
        assert icp.is_negative_match("restaurante delivery") is True
        assert icp.is_negative_match("pessoa fisica MEI") is True
        assert icp.is_negative_match("clinica medica") is True

        # Should not match
        assert icp.is_negative_match("distribuidora de alimentos") is False
        assert icp.is_negative_match("industria de bebidas") is False

    def test_segment_classification(self):
        icp = get_icp_definition()

        # Test segment detection from categories
        assert icp.get_segment_from_categories(['distribuidor', 'food']) == ICPSegment.DISTRIBUIDORAS
        assert icp.get_segment_from_categories(['atacadista', 'wholesale']) == ICPSegment.ATACADISTAS
        assert icp.get_segment_from_categories(['fabrica', 'industrial']) == ICPSegment.INDUSTRIAS
        assert icp.get_segment_from_categories(['farmacia', 'hospitalar']) == ICPSegment.FARMA_HOSPITALAR
        assert icp.get_segment_from_categories(['unknown']) == ICPSegment.OUTROS


class TestScorer:
    """Test lead scoring."""

    def test_scorer_initialization(self):
        scorer = LeadScorer()
        assert scorer is not None
        assert hasattr(scorer, 'weights')
        assert hasattr(scorer, 'thresholds')

    def test_score_high_fit_lead(self):
        scorer = LeadScorer()

        lead_data = {
            'name': 'Grande Distribuidora de Alimentos LTDA',
            'trade_name': 'Distribuidora Alimentos',
            'description': 'Distribuidora de alimentos e bebidas com frota própria, contrata transportadoras terceirizadas, possui centro de distribuição e expedição diária',
            'categories': ['distribuidor', 'alimentos', 'logistica'],
            'website': 'https://www.distribuidora.com.br',
            'website_verified': True,
            'phone': '+55 11 99999-9999',
            'phone_verified': True,
            'email': 'contato@distribuidora.com.br',
            'email_verified': True,
            'linkedin': 'https://linkedin.com/company/distribuidora',
            'linkedin_verified': True,
            'source_query': 'distribuidora de alimentos em São Paulo SP',
            'raw_data': {},
        }

        result = scorer.score_lead(lead_data)

        assert result.total_score > 0
        assert result.classification in [LeadClassification.A, LeadClassification.B, LeadClassification.C, LeadClassification.D]
        assert 0 <= result.operational_fit_score <= 100
        assert 0 <= result.commercial_fit_score <= 100
        assert 0 <= result.data_confidence_score <= 100

    def test_score_low_fit_lead(self):
        scorer = LeadScorer()

        lead_data = {
            'name': 'Restaurante do João',
            'trade_name': 'Restaurante do João',
            'description': 'Restaurante familiar com delivery próprio',
            'categories': ['restaurante', 'food'],
            'website': None,
            'phone': '+55 11 99999-9999',
            'phone_verified': False,
            'email': 'joao@gmail.com',
            'email_verified': False,
            'linkedin': None,
            'source_query': 'restaurante em São Paulo SP',
            'raw_data': {},
        }

        result = scorer.score_lead(lead_data)

        # Should be classified as D due to negative keywords
        assert result.classification == LeadClassification.D
        assert result.details.get('negative_match') is True

    def test_qualify_scraped_lead(self):
        scorer = LeadScorer()

        lead_data = {
            'id': 'scraped_123',
            'name': 'Distribuidora de Bebidas LTDA',
            'trade_name': 'Distribuidora Bebidas',
            'segment': 'bebidas',
            'city': 'Campinas',
            'state': 'SP',
            'phone': '+55 19 99999-9999',
            'phone_verified': True,
            'email': 'contato@distribuidorabebidas.com.br',
            'email_verified': True,
            'website': 'https://www.distribuidorabebidas.com.br',
            'website_verified': True,
            'categories': ['distribuidor', 'bebidas'],
            'source_query': 'distribuidora de bebidas em Campinas SP',
            'scraped_at': datetime.utcnow(),
        }

        qualified = scorer.qualify_scraped_lead(lead_data)

        assert qualified is not None
        assert qualified.name == 'Distribuidora de Bebidas LTDA'
        assert qualified.classification in [LeadClassification.A, LeadClassification.B, LeadClassification.C, LeadClassification.D]
        assert qualified.scraped_lead_id == 'scraped_123'


class TestQueryGenerator:
    """Test query generation."""

    def test_generator_initialization(self):
        gen = QueryGenerator()
        assert gen is not None
        assert hasattr(gen, 'icp_config')
        assert hasattr(gen, 'brazil_config')

    def test_generate_queries_for_state(self):
        gen = QueryGenerator()

        queries = gen.generate_queries_for_state('SP', max_queries=10)

        assert len(queries) > 0
        assert len(queries) <= 10
        # Check queries contain state code
        for q in queries:
            assert 'SP' in q or 'São Paulo' in q

    def test_generate_all_queries(self):
        gen = QueryGenerator()

        queries = gen.generate_all_queries(priorities=[1], max_per_state=2, max_total=20)

        assert len(queries) > 0
        assert len(queries) <= 20

    def test_get_states_by_priority(self):
        gen = QueryGenerator()

        states_p1 = gen.get_states_by_priority(1)
        states_p2 = gen.get_states_by_priority(2)
        states_p3 = gen.get_states_by_priority(3)

        assert len(states_p1) > 0
        assert len(states_p2) > 0
        assert len(states_p3) > 0

        # Check SP is priority 1
        sp_found = any(s['code'] == 'SP' for s in states_p1)
        assert sp_found


class TestConfig:
    """Test configuration loading."""

    def test_settings_load(self):
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings, Settings)
        assert settings.project_name == "Averta Lead Generation"

    def test_settings_values(self):
        settings = get_settings()

        # Check key settings exist
        assert settings.scraper_execution_mode in ['binary', 'rest-api', 'docker']
        assert settings.qual_weights_operational_fit + settings.qual_weights_commercial_fit + settings.qual_weights_data_confidence == 1.0
        assert settings.qual_thresholds_A_min > settings.qual_thresholds_B_min
        assert settings.qual_thresholds_B_min > settings.qual_thresholds_C_min


if __name__ == "__main__":
    pytest.main([__file__, "-v"])