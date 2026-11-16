"""Data models for the automation."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class LeadClassification(str, Enum):
    """Lead classification based on score."""
    A = "A"      # 85-100: Excellent
    B = "B"      # 70-84: Qualified
    C = "C"      # 50-69: Needs enrichment
    D = "D"      # <50: Not qualified


class ContactType(str, Enum):
    """Type of contact."""
    INSTITUTIONAL = "institutional"
    BUSINESS_PHONE = "business_phone"
    WHATSAPP_BUSINESS = "whatsapp_business"
    DECISION_MAKER_DIRECT = "decision_maker_direct"
    DECISION_MAKER_EMAIL = "decision_maker_email"
    DECISION_MAKER_PHONE = "decision_maker_phone"
    DECISION_MAKER_LINKEDIN = "decision_maker_linkedin"
    UNKNOWN = "unknown"


class EnrichmentStatus(str, Enum):
    """Enrichment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_NEEDED = "not_needed"


@dataclass
class ScrapedLead:
    """Raw lead from scraper."""
    # Required fields
    source_query: str
    scraped_at: datetime = field(default_factory=datetime.now)

    # Basic info
    place_id: Optional[str] = None
    name: Optional[str] = None
    trade_name: Optional[str] = None

    # Address
    address: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Brasil"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Contact
    phone: Optional[str] = None
    phone_verified: bool = False
    whatsapp: Optional[str] = None
    whatsapp_verified: bool = False
    email: Optional[str] = None
    email_verified: bool = False
    website: Optional[str] = None
    website_verified: bool = False
    linkedin: Optional[str] = None
    linkedin_verified: bool = False

    # Business info
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    price_level: Optional[int] = None
    categories: List[str] = field(default_factory=list)
    description: Optional[str] = None

    # Hours
    opening_hours: Optional[Dict] = None
    permanently_closed: bool = False
    temporarily_closed: bool = False

    # Additional
    photos: List[str] = field(default_factory=list)
    reviews: List[Dict] = field(default_factory=list)
    emails_from_website: List[str] = field(default_factory=list)
    social_media: Dict[str, str] = field(default_factory=dict)

    # Metadata
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'place_id': self.place_id,
            'name': self.name,
            'trade_name': self.trade_name,
            'address': self.address,
            'street': self.street,
            'number': self.number,
            'complement': self.complement,
            'neighborhood': self.neighborhood,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'phone_verified': self.phone_verified,
            'whatsapp': self.whatsapp,
            'whatsapp_verified': self.whatsapp_verified,
            'email': self.email,
            'email_verified': self.email_verified,
            'website': self.website,
            'website_verified': self.website_verified,
            'linkedin': self.linkedin,
            'linkedin_verified': self.linkedin_verified,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'price_level': self.price_level,
            'categories': self.categories,
            'description': self.description,
            'opening_hours': self.opening_hours,
            'permanently_closed': self.permanently_closed,
            'temporarily_closed': self.temporarily_closed,
            'photos': self.photos,
            'reviews': self.reviews,
            'emails_from_website': self.emails_from_website,
            'social_media': self.social_media,
            'source_query': self.source_query,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'raw_data': self.raw_data,
        }


@dataclass
class DecisionMaker:
    """Decision maker information."""
    id: str = field(default_factory=lambda: f"dm_{datetime.now().timestamp()}")
    lead_id: str = ""

    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None

    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None
    phone_verified: bool = False
    whatsapp: Optional[str] = None
    whatsapp_verified: bool = False
    linkedin: Optional[str] = None
    linkedin_verified: bool = False

    source: str = "unknown"
    source_url: Optional[str] = None
    confidence: float = 0.0  # 0-1

    identified_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'name': self.name,
            'role': self.role,
            'department': self.department,
            'email': self.email,
            'email_verified': self.email_verified,
            'phone': self.phone,
            'phone_verified': self.phone_verified,
            'whatsapp': self.whatsapp,
            'whatsapp_verified': self.whatsapp_verified,
            'linkedin': self.linkedin,
            'linkedin_verified': self.linkedin_verified,
            'source': self.source,
            'source_url': self.source_url,
            'confidence': self.confidence,
            'identified_at': self.identified_at.isoformat() if self.identified_at else None,
            'notes': self.notes,
        }


@dataclass
class InstitutionalContact:
    """Institutional contact information."""
    id: str = field(default_factory=lambda: f"ic_{datetime.now().timestamp()}")
    lead_id: str = ""

    contact_type: ContactType = ContactType.UNKNOWN
    value: str = ""
    label: Optional[str] = None
    verified: bool = False
    source: str = "unknown"
    source_url: Optional[str] = None
    confidence: float = 0.0

    identified_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'contact_type': self.contact_type.value,
            'value': self.value,
            'label': self.label,
            'verified': self.verified,
            'source': self.source,
            'source_url': self.source_url,
            'confidence': self.confidence,
            'identified_at': self.identified_at.isoformat() if self.identified_at else None,
            'notes': self.notes,
        }


@dataclass
class QualifiedLead:
    """Fully qualified lead with scoring."""
    # Identification
    id: str = field(default_factory=lambda: f"lead_{datetime.now().timestamp()}")
    scraped_lead_id: Optional[str] = None

    # Basic info (from scraped)
    name: Optional[str] = None
    trade_name: Optional[str] = None
    segment: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    phone_verified: bool = False
    whatsapp: Optional[str] = None
    whatsapp_verified: bool = False
    email: Optional[str] = None
    email_verified: bool = False
    website: Optional[str] = None
    website_verified: bool = False
    linkedin: Optional[str] = None
    linkedin_verified: bool = False
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Scoring
    score: float = 0.0
    classification: LeadClassification = LeadClassification.D
    operational_fit_score: float = 0.0
    commercial_fit_score: float = 0.0
    data_confidence_score: float = 0.0

    # Decision makers & contacts
    decision_makers: List[DecisionMaker] = field(default_factory=list)
    institutional_contacts: List[InstitutionalContact] = field(default_factory=list)

    # Metadata
    source_query: Optional[str] = None
    scraped_at: Optional[datetime] = None
    qualified_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    enrichment_status: EnrichmentStatus = EnrichmentStatus.PENDING
    enrichment_priority: str = "low"  # high, medium, low
    notes: Optional[str] = None

    # WhatsApp preparation
    whatsapp_ready: bool = False
    whatsapp_template_suggested: Optional[str] = None
    whatsapp_opt_in_status: str = "unknown"  # unknown, opted_in, opted_out
    whatsapp_last_contact_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'scraped_lead_id': self.scraped_lead_id,
            'name': self.name,
            'trade_name': self.trade_name,
            'segment': self.segment,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'phone_verified': self.phone_verified,
            'whatsapp': self.whatsapp,
            'whatsapp_verified': self.whatsapp_verified,
            'email': self.email,
            'email_verified': self.email_verified,
            'website': self.website,
            'website_verified': self.website_verified,
            'linkedin': self.linkedin,
            'linkedin_verified': self.linkedin_verified,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'score': self.score,
            'classification': self.classification.value,
            'operational_fit_score': self.operational_fit_score,
            'commercial_fit_score': self.commercial_fit_score,
            'data_confidence_score': self.data_confidence_score,
            'decision_makers': [dm.to_dict() for dm in self.decision_makers],
            'institutional_contacts': [ic.to_dict() for ic in self.institutional_contacts],
            'source_query': self.source_query,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'qualified_at': self.qualified_at.isoformat() if self.qualified_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'enrichment_status': self.enrichment_status.value,
            'enrichment_priority': self.enrichment_priority,
            'notes': self.notes,
            'whatsapp_ready': self.whatsapp_ready,
            'whatsapp_template_suggested': self.whatsapp_template_suggested,
            'whatsapp_opt_in_status': self.whatsapp_opt_in_status,
            'whatsapp_last_contact_at': self.whatsapp_last_contact_at.isoformat() if self.whatsapp_last_contact_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualifiedLead':
        """Create QualifiedLead from dictionary."""
        lead = cls()

        # Simple fields
        for key, value in data.items():
            if key in ['decision_makers', 'institutional_contacts']:
                continue
            if hasattr(lead, key):
                if key == 'classification' and isinstance(value, str):
                    setattr(lead, key, LeadClassification(value))
                elif key == 'enrichment_status' and isinstance(value, str):
                    setattr(lead, key, EnrichmentStatus(value))
                elif key in ['scraped_at', 'qualified_at', 'last_updated', 'whatsapp_last_contact_at'] and value:
                    setattr(lead, key, datetime.fromisoformat(value))
                else:
                    setattr(lead, key, value)

        # Decision makers
        for dm_data in data.get('decision_makers', []):
            dm = DecisionMaker(**dm_data)
            if isinstance(dm.identified_at, str):
                dm.identified_at = datetime.fromisoformat(dm.identified_at)
            lead.decision_makers.append(dm)

        # Institutional contacts
        for ic_data in data.get('institutional_contacts', []):
            ic = InstitutionalContact(**ic_data)
            if isinstance(ic.identified_at, str):
                ic.identified_at = datetime.fromisoformat(ic.identified_at)
            if isinstance(ic.contact_type, str):
                ic.contact_type = ContactType(ic.contact_type)
            lead.institutional_contacts.append(ic)

        return lead

    def get_decision_makers_summary(self) -> str:
        """Get summary of decision makers as JSON string."""
        return json.dumps([dm.to_dict() for dm in self.decision_makers], ensure_ascii=False)

    def get_institutional_contacts_summary(self) -> str:
        """Get summary of institutional contacts as JSON string."""
        return json.dumps([ic.to_dict() for ic in self.institutional_contacts], ensure_ascii=False)

    def get_missing_fields(self) -> List[str]:
        """Get list of missing important fields."""
        missing = []
        if not self.email:
            missing.append('email')
        if not self.phone:
            missing.append('phone')
        if not self.whatsapp:
            missing.append('whatsapp')
        if not self.linkedin:
            missing.append('linkedin')
        if not self.decision_makers:
            missing.append('decision_makers')
        if not self.website:
            missing.append('website')
        return missing


@dataclass
class ScrapingJob:
    """Scraping job tracking."""
    id: str = field(default_factory=lambda: f"job_{datetime.now().timestamp()}")
    query: str = ""
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results_count: int = 0
    error: Optional[str] = None
    output_file: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'query': self.query,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'results_count': self.results_count,
            'error': self.error,
            'output_file': self.output_file,
            'params': self.params,
        }


@dataclass
class DailyReport:
    """Daily execution report."""
    date: date = field(default_factory=date.today)

    # Counts
    queries_executed: int = 0
    companies_found: int = 0
    unique_companies: int = 0
    leads_classified_a: int = 0
    leads_classified_b: int = 0
    leads_classified_c: int = 0
    leads_classified_d: int = 0
    leads_discarded: int = 0

    # Contacts
    decision_makers_identified: int = 0
    institutional_contacts_valid: int = 0
    business_phones_valid: int = 0
    corporate_emails_found: int = 0
    linkedin_verified: int = 0

    # Coverage
    states_covered: int = 0
    segments_covered: int = 0

    # Performance
    cost_per_qualified_lead: float = 0.0
    qualification_rate: float = 0.0

    # Files generated
    leads_ab_file: Optional[str] = None
    leads_c_file: Optional[str] = None
    report_file: Optional[str] = None

    # Metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date.isoformat() if isinstance(self.date, date) else self.date,
            'queries_executed': self.queries_executed,
            'companies_found': self.companies_found,
            'unique_companies': self.unique_companies,
            'leads_classified_a': self.leads_classified_a,
            'leads_classified_b': self.leads_classified_b,
            'leads_classified_c': self.leads_classified_c,
            'leads_classified_d': self.leads_classified_d,
            'leads_discarded': self.leads_discarded,
            'decision_makers_identified': self.decision_makers_identified,
            'institutional_contacts_valid': self.institutional_contacts_valid,
            'business_phones_valid': self.business_phones_valid,
            'corporate_emails_found': self.corporate_emails_found,
            'linkedin_verified': self.linkedin_verified,
            'states_covered': self.states_covered,
            'segments_covered': self.segments_covered,
            'cost_per_qualified_lead': self.cost_per_qualified_lead,
            'qualification_rate': self.qualification_rate,
            'leads_ab_file': self.leads_ab_file,
            'leads_c_file': self.leads_c_file,
            'report_file': self.report_file,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'errors': self.errors,
            'warnings': self.warnings,
        }


from datetime import date