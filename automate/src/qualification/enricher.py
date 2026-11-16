"""Data enrichment for leads."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse

from utils.logging import get_logger
from utils.helpers import (
    normalize_phone, normalize_email, extract_domain,
    is_business_email, generate_id
)
from storage.models import QualifiedLead, DecisionMaker, InstitutionalContact, ContactType

logger = get_logger(__name__)


@dataclass
class EnrichmentResult:
    """Result of enrichment process."""
    lead_id: str
    enriched_fields: Dict[str, Any]
    new_decision_makers: List[DecisionMaker]
    new_contacts: List[InstitutionalContact]
    success: bool
    errors: List[str]


class LeadEnricher:
    """Enriches lead data from various sources."""

    def __init__(self):
        self.settings = None  # Will be loaded when needed

    def enrich_lead(self, lead: QualifiedLead) -> EnrichmentResult:
        """Enrich a single lead."""
        result = EnrichmentResult(
            lead_id=lead.id,
            enriched_fields={},
            new_decision_makers=[],
            new_contacts=[],
            success=True,
            errors=[]
        )

        try:
            # Enrich website data
            if lead.website and not lead.website_verified:
                website_data = self._enrich_from_website(lead.website)
                if website_data:
                    result.enriched_fields.update(website_data)

            # Enrich phone
            if lead.phone and not lead.phone_verified:
                normalized = normalize_phone(lead.phone)
                if normalized:
                    result.enriched_fields['phone'] = normalized
                    result.enriched_fields['phone_verified'] = True

            # Enrich email
            if lead.email and not lead.email_verified:
                normalized = normalize_email(lead.email)
                if normalized and is_business_email(normalized):
                    result.enriched_fields['email'] = normalized
                    result.enriched_fields['email_verified'] = True

            # Try to find decision makers from website
            if lead.website and not lead.decision_makers:
                decision_makers = self._extract_decision_makers(lead)
                result.new_decision_makers.extend(decision_makers)

            # Extract institutional contacts
            contacts = self._extract_institutional_contacts(lead)
            result.new_contacts.extend(contacts)

            # Mark as completed
            lead.enrichment_status = "completed"
            lead.last_updated = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error enriching lead {lead.id}: {e}")
            result.success = False
            result.errors.append(str(e))
            lead.enrichment_status = "failed"

        return result

    def _enrich_from_website(self, website: str) -> Optional[Dict]:
        """Enrich data from company website."""
        # This would require web scraping or API calls
        # For now, return basic domain info
        domain = extract_domain(website)
        if domain:
            return {
                'website_domain': domain,
                'website_verified': True,
            }
        return None

    def _extract_decision_makers(self, lead: QualifiedLead) -> List[DecisionMaker]:
        """Extract decision makers from available data."""
        decision_makers = []

        # This would typically involve:
        # 1. Scraping the website "team" or "about" page
        # 2. Searching LinkedIn for employees
        # 3. Using APIs like Hunter.io, Apollo, etc.

        # For now, return empty list - to be implemented with actual enrichment sources
        return decision_makers

    def _extract_institutional_contacts(self, lead: QualifiedLead) -> List[InstitutionalContact]:
        """Extract institutional contacts from lead data."""
        contacts = []

        # Phone contact
        if lead.phone:
            contacts.append(InstitutionalContact(
                id=generate_id("ic"),
                lead_id=lead.id,
                contact_type=ContactType.BUSINESS_PHONE,
                value=lead.phone,
                label="Telefone comercial",
                verified=lead.phone_verified,
                source="google_maps",
                confidence=0.8 if lead.phone_verified else 0.5,
            ))

        # WhatsApp contact
        if lead.whatsapp:
            contacts.append(InstitutionalContact(
                id=generate_id("ic"),
                lead_id=lead.id,
                contact_type=ContactType.WHATSAPP_BUSINESS,
                value=lead.whatsapp,
                label="WhatsApp Business",
                verified=lead.whatsapp_verified,
                source="google_maps",
                confidence=0.9 if lead.whatsapp_verified else 0.6,
            ))

        # Email contact
        if lead.email:
            contacts.append(InstitutionalContact(
                id=generate_id("ic"),
                lead_id=lead.id,
                contact_type=ContactType.INSTITUTIONAL,
                value=lead.email,
                label="E-mail institucional",
                verified=lead.email_verified,
                source="google_maps",
                confidence=0.8 if lead.email_verified else 0.5,
            ))

        # Website contact
        if lead.website:
            contacts.append(InstitutionalContact(
                id=generate_id("ic"),
                lead_id=lead.id,
                contact_type=ContactType.INSTITUTIONAL,
                value=lead.website,
                label="Site institucional",
                verified=lead.website_verified,
                source="google_maps",
                confidence=0.7 if lead.website_verified else 0.4,
            ))

        # LinkedIn contact
        if lead.linkedin:
            contacts.append(InstitutionalContact(
                id=generate_id("ic"),
                lead_id=lead.id,
                contact_type=ContactType.INSTITUTIONAL,
                value=lead.linkedin,
                label="LinkedIn da empresa",
                verified=lead.linkedin_verified,
                source="google_maps",
                confidence=0.7 if lead.linkedin_verified else 0.4,
            ))

        return contacts

    def enrich_batch(self, leads: List[QualifiedLead]) -> List[EnrichmentResult]:
        """Enrich a batch of leads."""
        results = []

        for lead in leads:
            if lead.enrichment_status in ["pending", "failed"]:
                result = self.enrich_lead(lead)
                results.append(result)

                # Apply enriched fields to lead
                for key, value in result.enriched_fields.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)

                # Add new decision makers
                lead.decision_makers.extend(result.new_decision_makers)

                # Add new contacts
                lead.institutional_contacts.extend(result.new_contacts)

        return results


class ExternalEnrichmentService:
    """Interface for external enrichment services (Hunter, Apollo, etc.)."""

    def __init__(self):
        self.api_keys = {}

    def set_api_key(self, service: str, api_key: str):
        """Set API key for enrichment service."""
        self.api_keys[service] = api_key

    def enrich_email(self, domain: str, service: str = "hunter") -> List[Dict]:
        """Find emails for a domain."""
        # Placeholder for external API integration
        return []

    def enrich_linkedin(self, company_name: str, domain: str) -> List[Dict]:
        """Find LinkedIn profiles for company."""
        # Placeholder for external API integration
        return []

    def enrich_phone(self, company_name: str, address: str) -> List[Dict]:
        """Find phone numbers for company."""
        # Placeholder for external API integration
        return []


def create_enrichment_pipeline() -> LeadEnricher:
    """Create enrichment pipeline."""
    return LeadEnricher()