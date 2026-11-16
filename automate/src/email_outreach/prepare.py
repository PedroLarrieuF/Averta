"""
Email contact preparation for Averta outreach campaigns.

This module prepares qualified leads for email campaigns:
- Filters leads with valid emails
- Extracts decision makers
- Suggests optimal email templates
- Schedules sends respecting business hours
- Exports for email API/platform integration
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
import json

from src.utils.config_loader import get_settings
from src.utils.logging import get_logger
from src.utils.helpers import normalize_email, is_business_email
from storage.models import QualifiedLead, LeadClassification, DecisionMaker
from .templates import EmailTemplateManager, EmailType

logger = get_logger(__name__)


class EmailStatus(str, Enum):
    """Email contact status."""
    UNKNOWN = "unknown"
    VERIFIED = "verified"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"
    INVALID = "invalid"


@dataclass
class EmailContact:
    """Prepared email contact for campaign."""
    # Lead identification
    lead_id: str = ""
    company_name: str = ""
    trade_name: str = ""
    segment: str = ""
    city: str = ""
    state: str = ""
    score: float = 0
    classification: str = ""

    # Contact info
    email: str = ""
    email_status: EmailStatus = EmailStatus.UNKNOWN
    email_source: str = ""  # website, linkedin, scraped, enriched

    # Decision maker
    contact_name: str = ""
    contact_role: str = ""
    contact_first_name: str = ""
    contact_email: str = ""  # Direct email if different from company
    contact_linkedin: str = ""

    # Campaign
    template_suggested: str = "initial_outreach"
    template_alternatives: List[str] = field(default_factory=list)

    # Scheduling
    scheduled_at: Optional[datetime] = None
    priority: int = 1  # 1=high, 2=medium, 3=low
    timezone: str = "America/Sao_Paulo"

    # Tracking
    opt_in_status: str = "unknown"  # unknown, opted_in, opted_out
    last_contact_at: Optional[datetime] = None
    contact_count: int = 0

    # Metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'trade_name': self.trade_name,
            'segment': self.segment,
            'city': self.city,
            'state': self.state,
            'score': self.score,
            'classification': self.classification,
            'email': self.email,
            'email_status': self.email_status.value,
            'email_source': self.email_source,
            'contact_name': self.contact_name,
            'contact_role': self.contact_role,
            'contact_first_name': self.contact_first_name,
            'contact_email': self.contact_email,
            'contact_linkedin': self.contact_linkedin,
            'template_suggested': self.template_suggested,
            'template_alternatives': ', '.join(self.template_alternatives),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else '',
            'priority': self.priority,
            'timezone': self.timezone,
            'opt_in_status': self.opt_in_status,
            'last_contact_at': self.last_contact_at.isoformat() if self.last_contact_at else '',
            'contact_count': self.contact_count,
            'notes': self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailContact':
        """Create from dictionary."""
        contact = cls(
            lead_id=data.get('lead_id', ''),
            company_name=data.get('company_name', ''),
            trade_name=data.get('trade_name', ''),
            segment=data.get('segment', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            score=data.get('score', 0),
            classification=data.get('classification', ''),
            email=data.get('email', ''),
            email_status=EmailStatus(data.get('email_status', 'unknown')),
            email_source=data.get('email_source', ''),
            contact_name=data.get('contact_name', ''),
            contact_role=data.get('contact_role', ''),
            contact_first_name=data.get('contact_first_name', ''),
            contact_email=data.get('contact_email', ''),
            contact_linkedin=data.get('contact_linkedin', ''),
            template_suggested=data.get('template_suggested', 'initial_outreach'),
            template_alternatives=data.get('template_alternatives', '').split(', ') if data.get('template_alternatives') else [],
            priority=data.get('priority', 1),
            timezone=data.get('timezone', 'America/Sao_Paulo'),
            opt_in_status=data.get('opt_in_status', 'unknown'),
            contact_count=data.get('contact_count', 0),
            notes=data.get('notes', ''),
        )

        # Parse dates
        for field_name in ['scheduled_at', 'last_contact_at']:
            val = data.get(field_name)
            if val:
                try:
                    setattr(contact, field_name, datetime.fromisoformat(val))
                except:
                    pass

        return contact


class EmailPreparator:
    """Prepares qualified leads for email campaigns."""

    def __init__(self):
        self.settings = get_settings()
        self.template_manager = EmailTemplateManager()

        # Default scheduling config
        self.business_hours_start = time(8, 0)
        self.business_hours_end = time(18, 0)
        self.timezone = "America/Sao_Paulo"
        self.rate_limit_per_minute = 10
        self.rate_limit_per_hour = 200
        self.rate_limit_per_day = 1000

        # Template mapping by segment and classification
        self.template_mapping = {
            # High-priority segments
            ('distribuidoras', 'A'): 'initial_outreach',
            ('distribuidoras', 'B'): 'initial_outreach',
            ('atacadistas', 'A'): 'initial_outreach',
            ('atacadistas', 'B'): 'initial_outreach',
            ('industrias', 'A'): 'value_proposition',
            ('industrias', 'B'): 'initial_outreach',
            ('farma_hospitalar', 'A'): 'value_proposition',
            ('farma_hospitalar', 'B'): 'initial_outreach',
            ('alimenticias', 'A'): 'case_study',
            ('alimenticias', 'B'): 'initial_outreach',
            ('bebidas', 'A'): 'initial_outreach',
            ('bebidas', 'B'): 'follow_up_1',
            ('autopeças', 'A'): 'value_proposition',
            ('autopeças', 'B'): 'initial_outreach',
            ('material_construcao', 'A'): 'initial_outreach',
            ('material_construcao', 'B'): 'follow_up_1',
            ('ecommerce_logistica', 'A'): 'value_proposition',
            ('ecommerce_logistica', 'B'): 'initial_outreach',
            ('grande_volume', 'A'): 'value_proposition',
            ('grande_volume', 'B'): 'initial_outreach',
        }

        # Alternative templates for A/B testing
        self.alternative_templates = {
            'initial_outreach': ['value_proposition', 'case_study'],
            'follow_up_1': ['case_study', 'value_proposition'],
            'follow_up_2': ['meeting_request', 'case_study'],
            'value_proposition': ['initial_outreach', 'case_study'],
            'case_study': ['value_proposition', 'meeting_request'],
        }

    def prepare_leads(
        self,
        leads: List[QualifiedLead],
        classifications: List[LeadClassification] = None,
        min_score: float = 50,
        only_with_email: bool = True,
        segment_filter: List[str] = None,
        state_filter: List[str] = None
    ) -> List[EmailContact]:
        """Prepare leads for email campaigns."""

        # Default to A and B classifications
        if classifications is None:
            classifications = [LeadClassification.A, LeadClassification.B]

        contacts = []

        for lead in leads:
            # Filter by classification
            if lead.classification not in classifications:
                continue

            # Filter by score
            if lead.score < min_score:
                continue

            # Filter by segment
            if segment_filter and lead.segment not in segment_filter:
                continue

            # Filter by state
            if state_filter and lead.state not in state_filter:
                continue

            # Must have email
            if only_with_email and not lead.email:
                continue

            # Normalize and validate email
            normalized_email = normalize_email(lead.email)
            if not normalized_email or not is_business_email(normalized_email):
                continue

            # Get primary decision maker
            decision_maker = None
            if lead.decision_makers:
                # Prefer decision makers with email
                for dm in lead.decision_makers:
                    if dm.email and normalize_email(dm.email):
                        decision_maker = dm
                        break
                if not decision_maker:
                    decision_maker = lead.decision_makers[0]

            # Create contact
            contact = self._create_contact(lead, decision_maker, normalized_email)
            contacts.append(contact)

        # Sort by priority (score desc, classification A first)
        contacts.sort(key=lambda c: (-c.score, c.classification != 'A'))

        logger.info(f"Prepared {len(contacts)} email contacts from {len(leads)} leads")
        return contacts

    def _create_contact(
        self,
        lead: QualifiedLead,
        decision_maker: Optional[DecisionMaker],
        email: str
    ) -> EmailContact:
        """Create email contact from lead."""

        # Determine suggested template
        template_key = (lead.segment or '', lead.classification.value)
        template_suggested = self.template_mapping.get(template_key, 'initial_outreach')

        # Get alternatives
        alternatives = self.alternative_templates.get(template_suggested, [])

        # Extract contact name
        contact_name = ""
        contact_role = ""
        contact_first_name = ""
        contact_email = ""
        contact_linkedin = ""

        if decision_maker:
            contact_name = decision_maker.name or ""
            contact_role = decision_maker.role or ""
            contact_email = decision_maker.email or ""
            contact_linkedin = decision_maker.linkedin or ""
            if contact_name:
                contact_first_name = contact_name.split()[0]

        # Determine priority
        priority = 1 if lead.classification == LeadClassification.A else 2
        if lead.score >= 90:
            priority = 1
        elif lead.score < 60:
            priority = 3

        return EmailContact(
            lead_id=lead.id,
            company_name=lead.name or "",
            trade_name=lead.trade_name or "",
            segment=lead.segment or "",
            city=lead.city or "",
            state=lead.state or "",
            score=lead.score,
            classification=lead.classification.value,
            email=email,
            email_status=EmailStatus.VERIFIED if lead.email_verified else EmailStatus.UNKNOWN,
            email_source="scraped" if not lead.email_verified else "verified",
            contact_name=contact_name,
            contact_role=contact_role,
            contact_first_name=contact_first_name,
            contact_email=contact_email,
            contact_linkedin=contact_linkedin,
            template_suggested=template_suggested,
            template_alternatives=alternatives,
            priority=priority,
            timezone=self.timezone,
        )

    def get_sending_schedule(
        self,
        contacts: List[EmailContact],
        start_date: datetime = None,
        business_hours_only: bool = True,
        rate_limit_per_minute: int = None,
        rate_limit_per_hour: int = None,
        rate_limit_per_day: int = None,
        max_per_day: int = None
    ) -> List[EmailContact]:
        """Schedule email sends respecting business hours and rate limits."""

        if not contacts:
            return []

        # Use provided limits or defaults
        rl_min = rate_limit_per_minute or self.rate_limit_per_minute
        rl_hour = rate_limit_per_hour or self.rate_limit_per_hour
        rl_day = rate_limit_per_day or self.rate_limit_per_day
        max_day = max_per_day or rl_day

        # Start from next business hour
        if start_date is None:
            start_date = datetime.now()

        # Adjust to business hours
        scheduled = self._adjust_to_business_hours(start_date, business_hours_only)

        # Schedule each contact
        minute_count = 0
        hour_count = 0
        day_count = 0
        current_day = scheduled.date()

        for i, contact in enumerate(contacts):
            # Check daily limit
            if day_count >= max_day:
                # Move to next business day
                scheduled = self._next_business_day(scheduled, business_hours_only)
                scheduled = scheduled.replace(hour=self.business_hours_start.hour, minute=0, second=0, microsecond=0)
                current_day = scheduled.date()
                day_count = 0
                hour_count = 0
                minute_count = 0

            # Check hourly limit
            if hour_count >= rl_hour:
                # Wait until next hour
                scheduled = scheduled.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                scheduled = self._adjust_to_business_hours(scheduled, business_hours_only)
                hour_count = 0
                minute_count = 0

            # Check minute limit
            if minute_count >= rl_min:
                scheduled = scheduled + timedelta(minutes=1)
                scheduled = self._adjust_to_business_hours(scheduled, business_hours_only)
                minute_count = 0

            contact.scheduled_at = scheduled

            # Increment counters
            minute_count += 1
            hour_count += 1
            day_count += 1

            # Add small random delay (0-30 seconds) to avoid exact patterns
            import random
            scheduled = scheduled + timedelta(seconds=random.randint(0, 30))

        logger.info(f"Scheduled {len(contacts)} emails over {(contacts[-1].scheduled_at - contacts[0].scheduled_at).days + 1} days")
        return contacts

    def _adjust_to_business_hours(self, dt: datetime, business_hours_only: bool) -> datetime:
        """Adjust datetime to business hours."""
        if not business_hours_only:
            return dt

        # Check if weekend
        if dt.weekday() >= 5:  # Saturday=5, Sunday=6
            dt = self._next_business_day(dt)
            return dt.replace(hour=self.business_hours_start.hour, minute=0, second=0, microsecond=0)

        # Check if before business hours
        if dt.time() < self.business_hours_start:
            return dt.replace(hour=self.business_hours_start.hour, minute=0, second=0, microsecond=0)

        # Check if after business hours
        if dt.time() >= self.business_hours_end:
            dt = self._next_business_day(dt)
            return dt.replace(hour=self.business_hours_start.hour, minute=0, second=0, microsecond=0)

        return dt

    def _next_business_day(self, dt: datetime, business_hours_only: bool = True) -> datetime:
        """Get next business day."""
        if not business_hours_only:
            return dt + timedelta(days=1)

        next_day = dt + timedelta(days=1)
        while next_day.weekday() >= 5:  # Skip weekends
            next_day += timedelta(days=1)
        return next_day

    def export_for_email_api(
        self,
        contacts: List[EmailContact],
        output_path: str = None
    ) -> str:
        """Export contacts for email API (CSV format)."""
        import csv

        if output_path is None:
            date_str = datetime.now().strftime('%Y%m%d')
            output_path = f"output/email_ready/leads_email_{date_str}.csv"

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Fieldnames for CSV
        fieldnames = [
            'lead_id', 'company_name', 'trade_name', 'segment', 'city', 'state',
            'score', 'classification', 'email', 'email_status', 'email_source',
            'contact_name', 'contact_role', 'contact_first_name', 'contact_email',
            'contact_linkedin', 'template_suggested', 'template_alternatives',
            'scheduled_at', 'priority', 'timezone', 'opt_in_status',
            'last_contact_at', 'contact_count', 'notes'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for contact in contacts:
                row = contact.to_dict()
                writer.writerow(row)

        logger.info(f"Exported {len(contacts)} email contacts to {output_path}")
        return output_path

    def export_for_sendgrid(
        self,
        contacts: List[EmailContact],
        output_path: str = None
    ) -> str:
        """Export contacts in SendGrid CSV format."""
        import csv

        if output_path is None:
            date_str = datetime.now().strftime('%Y%m%d')
            output_path = f"output/email_ready/leads_sendgrid_{date_str}.csv"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # SendGrid format: email, first_name, last_name, custom_fields...
        fieldnames = [
            'email', 'first_name', 'last_name', 'company_name', 'segment',
            'city', 'state', 'score', 'classification', 'lead_id',
            'template_suggested', 'custom_role', 'custom_city', 'custom_case_study'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for contact in contacts:
                # Split name
                first = contact.contact_first_name
                last = ""
                if contact.contact_name and contact.contact_name != contact.contact_first_name:
                    parts = contact.contact_name.split()
                    if len(parts) > 1:
                        last = " ".join(parts[1:])

                # Get case study from custom fields or template
                case_study = contact.custom_fields.get('case_study', '')

                row = {
                    'email': contact.email,
                    'first_name': first,
                    'last_name': last,
                    'company_name': contact.company_name,
                    'segment': contact.segment,
                    'city': contact.city,
                    'state': contact.state,
                    'score': contact.score,
                    'classification': contact.classification,
                    'lead_id': contact.lead_id,
                    'template_suggested': contact.template_suggested,
                    'custom_role': contact.contact_role,
                    'custom_city': contact.city,
                    'custom_case_study': case_study,
                }
                writer.writerow(row)

        logger.info(f"Exported {len(contacts)} contacts for SendGrid to {output_path}")
        return output_path

    def get_stats(self, contacts: List[EmailContact]) -> Dict[str, Any]:
        """Get statistics about prepared contacts."""
        if not contacts:
            return {'total': 0}

        by_classification = {}
        by_segment = {}
        by_state = {}
        by_template = {}
        by_priority = {}

        for c in contacts:
            by_classification[c.classification] = by_classification.get(c.classification, 0) + 1
            by_segment[c.segment] = by_segment.get(c.segment, 0) + 1
            by_state[c.state] = by_state.get(c.state, 0) + 1
            by_template[c.template_suggested] = by_template.get(c.template_suggested, 0) + 1
            by_priority[c.priority] = by_priority.get(c.priority, 0) + 1

        return {
            'total': len(contacts),
            'by_classification': by_classification,
            'by_segment': by_segment,
            'by_state': by_state,
            'by_template': by_template,
            'by_priority': by_priority,
            'avg_score': sum(c.score for c in contacts) / len(contacts),
            'with_decision_maker': sum(1 for c in contacts if c.contact_name),
            'with_direct_email': sum(1 for c in contacts if c.contact_email),
        }

    def preview_contacts(self, contacts: List[EmailContact], limit: int = 10) -> List[Dict]:
        """Preview contacts for review."""
        return [
            {
                'lead_id': c.lead_id,
                'company': c.company_name or c.trade_name,
                'segment': c.segment,
                'city_state': f"{c.city}/{c.state}",
                'score': c.score,
                'class': c.classification,
                'email': c.email,
                'decision_maker': f"{c.contact_name} ({c.contact_role})" if c.contact_name else "N/A",
                'template': c.template_suggested,
                'priority': c.priority,
                'scheduled': c.scheduled_at.strftime('%Y-%m-%d %H:%M') if c.scheduled_at else "Not scheduled",
            }
            for c in contacts[:limit]
        ]


# Example usage
if __name__ == "__main__":
    # This would be used with actual leads from database
    preparator = EmailPreparator()

    # Example: prepare leads
    # contacts = preparator.prepare_leads(leads, classifications=[LeadClassification.A, LeadClassification.B])

    # Schedule
    # contacts = preparator.get_sending_schedule(contacts)

    # Export
    # csv_file = preparator.export_for_email_api(contacts)
    # sendgrid_file = preparator.export_for_sendgrid(contacts)

    # Stats
    # stats = preparator.get_stats(contacts)
    # print(f"Prepared {stats['total']} contacts")

    print("EmailPreparator ready for use")