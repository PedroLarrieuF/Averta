"""WhatsApp Business preparation for future integration."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id, normalize_phone
from storage.models import QualifiedLead, LeadClassification

logger = get_logger(__name__)


class WhatsAppStatus(str, Enum):
    """WhatsApp contact status."""
    UNKNOWN = "unknown"
    OPTED_IN = "opted_in"
    OPTED_OUT = "opted_out"
    BLOCKED = "blocked"
    INVALID = "invalid"


class MessageTemplate(str, Enum):
    """Pre-approved message templates."""
    INITIAL_CONTACT = "initial_contact"
    FOLLOW_UP = "follow_up"
    VALUE_PROPOSITION = "value_proposition"
    CASE_STUDY = "case_study"
    DEMO_INVITE = "demo_invite"


@dataclass
class WhatsAppContact:
    """WhatsApp contact ready for messaging."""
    id: str = field(default_factory=lambda: f"wc_{datetime.now().timestamp()}")
    lead_id: str = ""

    # Company info
    company_name: str = ""
    company_segment: str = ""
    company_city: str = ""
    company_state: str = ""
    lead_score: float = 0.0
    lead_classification: str = ""

    # Contact info
    phone: str = ""
    whatsapp: str = ""
    email: str = ""
    contact_name: str = ""
    contact_role: str = ""

    # WhatsApp specific
    whatsapp_status: WhatsAppStatus = WhatsAppStatus.UNKNOWN
    template_suggested: MessageTemplate = MessageTemplate.INITIAL_CONTACT
    template_variables: Dict[str, str] = field(default_factory=dict)
    opt_in_timestamp: Optional[datetime] = None
    opt_in_source: str = ""

    # Scheduling
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'company_segment': self.company_segment,
            'company_city': self.company_city,
            'company_state': self.company_state,
            'lead_score': self.lead_score,
            'lead_classification': self.lead_classification,
            'phone': self.phone,
            'whatsapp': self.whatsapp,
            'email': self.email,
            'contact_name': self.contact_name,
            'contact_role': self.contact_role,
            'whatsapp_status': self.whatsapp_status.value,
            'template_suggested': self.template_suggested.value,
            'template_variables': self.template_variables,
            'opt_in_timestamp': self.opt_in_timestamp.isoformat() if self.opt_in_timestamp else None,
            'opt_in_source': self.opt_in_source,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
        }


class WhatsAppPreparator:
    """Prepares leads for WhatsApp Business integration."""

    def __init__(self):
        self.settings = get_settings()
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[MessageTemplate, str]:
        """Load message templates from config."""
        whatsapp_config = self.settings.__dict__.get('whatsapp_templates', {})

        templates = {}
        for tmpl in whatsapp_config.get('templates', []):
            # This would load from config - for now use defaults
            pass

        # Default templates
        return {
            MessageTemplate.INITIAL_CONTACT: (
                "Olá {contact_name}, sou da Averta. Vi que a {company_name} atua com "
                "{company_segment} em {company_city}. Gostaria de apresentar nossa solução "
                "de gestão de fretes que reduz custos em até 30%. Podemos conversar?"
            ),
            MessageTemplate.FOLLOW_UP: (
                "Oi {contact_name}, passando para saber se teve chance de avaliar nossa "
                "proposta. A {company_name} pode economizar significativamente nos fretes. "
                "Vamos agendar?"
            ),
            MessageTemplate.VALUE_PROPOSITION: (
                "Olá {contact_name}, a Averta ajuda empresas como a {company_name} a "
                "otimizar a logística: cotação, contratação, tracking e auditoria de fretes "
                "em uma plataforma. Temos cases no segmento de {company_segment} com "
                "redução de 25% no custo logístico. Quer ver os números?"
            ),
            MessageTemplate.CASE_STUDY: (
                "Oi {contact_name}, seguindo nosso papo sobre logística. Tenho um case "
                "similar à {company_name} que reduziu 30% no custo de frete com nossa "
                "plataforma. Quer ver os detalhes?"
            ),
            MessageTemplate.DEMO_INVITE: (
                "Olá {contact_name}, gostaria de convidar você para uma demo rápida (15 min) "
                "da nossa plataforma de gestão de fretes. A {company_name} veria na prática "
                "como reduzir custos e ganhar visibilidade total das cargas. Qual melhor horário?"
            ),
        }

    def prepare_leads(self, leads: List[QualifiedLead]) -> List[WhatsAppContact]:
        """Prepare qualified leads for WhatsApp."""
        whatsapp_contacts = []

        for lead in leads:
            if not lead.whatsapp_ready:
                continue

            # Determine best phone number
            phone = lead.whatsapp or lead.phone
            if not phone:
                continue

            # Normalize phone
            normalized_phone = normalize_phone(phone)
            if not normalized_phone:
                logger.warning(f"Invalid phone for lead {lead.id}: {phone}")
                continue

            # Get best contact name
            contact_name = ""
            contact_role = ""
            if lead.decision_makers:
                dm = lead.decision_makers[0]
                contact_name = dm.name or ""
                contact_role = dm.role or ""

            # Select best template
            template = self._select_template(lead)

            # Prepare template variables
            variables = {
                'contact_name': contact_name or "lá",
                'company_name': lead.name or lead.trade_name or "sua empresa",
                'company_segment': lead.segment or "seu segmento",
                'company_city': lead.city or "sua cidade",
                'company_state': lead.state or "",
            }

            # Create WhatsApp contact
            wa_contact = WhatsAppContact(
                lead_id=lead.id,
                company_name=lead.name or lead.trade_name or "",
                company_segment=lead.segment or "",
                company_city=lead.city or "",
                company_state=lead.state or "",
                lead_score=lead.score,
                lead_classification=lead.classification.value,
                phone=normalized_phone,
                whatsapp=normalize_phone(lead.whatsapp) if lead.whatsapp else normalized_phone,
                email=lead.email or "",
                contact_name=contact_name,
                contact_role=contact_role,
                template_suggested=template,
                template_variables=variables,
                whatsapp_status=WhatsAppStatus.UNKNOWN,
                notes=f"Prepared from lead {lead.id} - Score: {lead.score:.1f} - Class: {lead.classification.value}",
            )

            whatsapp_contacts.append(wa_contact)

        logger.info(f"Prepared {len(whatsapp_contacts)} WhatsApp contacts from {len(leads)} leads")
        return whatsapp_contacts

    def _select_template(self, lead: QualifiedLead) -> MessageTemplate:
        """Select best template based on lead characteristics."""
        if lead.classification == LeadClassification.A:
            if lead.segment in ['distribuidoras', 'atacadistas', 'industrias']:
                return MessageTemplate.VALUE_PROPOSITION
            return MessageTemplate.INITIAL_CONTACT
        elif lead.classification == LeadClassification.B:
            if lead.decision_makers:
                return MessageTemplate.CASE_STUDY
            return MessageTemplate.FOLLOW_UP
        return MessageTemplate.INITIAL_CONTACT

    def validate_phone_for_whatsapp(self, phone: str) -> bool:
        """Validate if phone can be used for WhatsApp."""
        normalized = normalize_phone(phone)
        if not normalized:
            return False

        # Check if Brazilian mobile (starts with 55 + 2 digit area code + 9xxxxxxxx)
        if normalized.startswith('55'):
            # Brazilian format: 55 + DD + 9XXXXXXXX
            number_part = normalized[2:]  # Remove 55
            if len(number_part) >= 10:
                area_code = number_part[:2]
                mobile_part = number_part[2:]
                # Mobile numbers in Brazil have 9 digits after area code and start with 9
                if len(mobile_part) == 9 and mobile_part[0] == '9':
                    return True

        return False

    def get_sending_schedule(
        self,
        contacts: List[WhatsAppContact],
        business_hours_only: bool = True,
        rate_limit_per_minute: int = 20
    ) -> List[WhatsAppContact]:
        """Calculate sending schedule for contacts."""
        from datetime import timedelta

        if not contacts:
            return []

        # Business hours
        start_hour = 8
        end_hour = 18

        now = datetime.utcnow()
        scheduled = now

        for i, contact in enumerate(contacts):
            # Calculate send time
            if business_hours_only:
                # Ensure within business hours
                if scheduled.hour < start_hour:
                    scheduled = scheduled.replace(hour=start_hour, minute=0, second=0)
                elif scheduled.hour >= end_hour:
                    # Next business day
                    scheduled = scheduled.replace(hour=start_hour, minute=0, second=0) + timedelta(days=1)
                    # Skip weekends
                    while scheduled.weekday() >= 5:
                        scheduled += timedelta(days=1)

            # Rate limiting
            if i > 0:
                interval = 60 / rate_limit_per_minute  # seconds between messages
                scheduled += timedelta(seconds=interval)

            contact.scheduled_at = scheduled

        return contacts

    def export_for_whatsapp_api(self, contacts: List[WhatsAppContact], filename: str = None) -> str:
        """Export contacts in format ready for WhatsApp Business API."""
        import json
        from pathlib import Path

        if filename is None:
            filename = f"whatsapp_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_dir = Path(self.settings.output_dir) / "whatsapp_ready"
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / filename

        # Convert to API format
        api_data = []
        for contact in contacts:
            api_data.append({
                'contact_id': contact.id,
                'phone': contact.whatsapp,
                'template_name': contact.template_suggested.value,
                'template_language': 'pt_BR',
                'variables': contact.template_variables,
                'metadata': {
                    'lead_id': contact.lead_id,
                    'company_name': contact.company_name,
                    'score': contact.lead_score,
                    'classification': contact.lead_classification,
                }
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(api_data)} WhatsApp API contacts to {filepath}")
        return str(filepath)

    def process_webhook_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming WhatsApp webhook event."""
        # This would handle:
        # - Message delivery confirmations
        # - Read receipts
        # - Incoming replies
        # - Opt-out requests
        # - Failed deliveries

        event_type = event.get('type', '')

        if event_type == 'message_delivered':
            return self._handle_delivered(event)
        elif event_type == 'message_read':
            return self._handle_read(event)
        elif event_type == 'message_received':
            return self._handle_reply(event)
        elif event_type == 'opt_out':
            return self._handle_opt_out(event)

        return None

    def _handle_delivered(self, event: Dict) -> Dict:
        """Handle delivery confirmation."""
        return {'action': 'update_status', 'status': 'delivered', 'timestamp': datetime.utcnow().isoformat()}

    def _handle_read(self, event: Dict) -> Dict:
        """Handle read receipt."""
        return {'action': 'update_status', 'status': 'read', 'timestamp': datetime.utcnow().isoformat()}

    def _handle_reply(self, event: Dict) -> Dict:
        """Handle incoming reply."""
        return {
            'action': 'process_reply',
            'message': event.get('message', {}),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _handle_opt_out(self, event: Dict) -> Dict:
        """Handle opt-out request."""
        return {
            'action': 'opt_out',
            'phone': event.get('phone'),
            'timestamp': datetime.utcnow().isoformat()
        }


def create_whatsapp_preparator() -> WhatsAppPreparator:
    """Create WhatsApp preparator instance."""
    return WhatsAppPreparator()