"""
Email Sending Engine for Averta Outreach Campaigns.

Supports:
- SMTP (Zoho, Gmail, Outlook, custom)
- SendGrid API
- Intelligent personalization with variables
- Campaign management with scheduling
- Rate limiting and business hours
- Tracking (opens, clicks, replies)
- Opt-out handling (LGPD compliant)
"""

import asyncio
import smtplib
import ssl
import time
import os
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, make_msgid

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# Try to import certifi for better SSL handling on Windows
try:
    import certifi
    HAS_CERTIFI = True
except ImportError:
    HAS_CERTIFI = False

# Add src to path for imports
import sys
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.utils.config_loader import get_settings
from src.utils.logging import get_logger
from src.utils.helpers import generate_id, normalize_email
from storage.models import QualifiedLead, LeadClassification, DecisionMaker
from .templates import EmailTemplateManager, EmailTemplate, EmailType

logger = get_logger(__name__)


class EmailProvider(str, Enum):
    """Email provider types."""
    SMTP = "smtp"              # Zoho, Gmail, Outlook, custom SMTP
    SENDGRID = "sendgrid"      # SendGrid API
    MAILGUN = "mailgun"        # Mailgun API (futuro)
    SES = "ses"                # AWS SES (futuro)


class EmailStatus(str, Enum):
    """Email delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"
    SPAM_COMPLAINT = "spam_complaint"
    UNSUBSCRIBED = "unsubscribed"


class CampaignStage(str, Enum):
    """Campaign stage for follow-up logic."""
    INITIAL = "initial"
    FOLLOW_UP_1 = "follow_up_1"
    FOLLOW_UP_2 = "follow_up_2"
    FOLLOW_UP_3 = "follow_up_3"
    REPLIED = "replied"
    MEETING_SCHEDULED = "meeting_scheduled"
    NOT_INTERESTED = "not_interested"
    UNSUBSCRIBED = "unsubscribed"


@dataclass
class PersonalizationContext:
    """Context for email personalization."""
    # Our company info
    our_company_name: str = "Averta"
    our_website: str = "https://averta.com.br"
    our_email: str = "contato@avertabrasil.com.br"
    our_phone: str = "(11) 99999-9999"
    our_address: str = "Av. Paulista, 1000 - São Paulo/SP"
    our_cnpj: str = "00.000.000/0001-00"

    # Value propositions
    our_value_props: List[str] = field(default_factory=lambda: [
        "redução de até 30% no custo logístico",
        "gestão completa de fretes em uma plataforma",
        "tracking em tempo real e auditoria automática",
        "integração nativa com ERP/TMS via API"
    ])

    # Prospect info
    prospect_company_name: str = ""
    prospect_trade_name: str = ""
    prospect_segment: str = ""
    prospect_city: str = ""
    prospect_state: str = ""

    # Decision maker info
    decision_maker_name: str = ""
    decision_maker_role: str = ""
    decision_maker_first_name: str = ""
    decision_maker_email: str = ""

    # Lead info
    lead_score: float = 0
    lead_classification: str = ""
    lead_id: str = ""

    # Tracking links
    meeting_link: str = "https://calendly.com/averta/15min"
    case_study_link: str = "https://averta.com.br/cases"
    material_link: str = "https://averta.com.br/materiais"
    unsubscribe_link: str = "https://averta.com.br/unsubscribe"
    preferences_link: str = "https://averta.com.br/preferences"

    # Custom fields
    custom_fields: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_lead(cls, lead: QualifiedLead, decision_maker: Optional[DecisionMaker] = None,
                  base_url: str = "https://averta.com.br") -> 'PersonalizationContext':
        """Create context from qualified lead."""
        ctx = cls(
            prospect_company_name=lead.name or "",
            prospect_trade_name=lead.trade_name or "",
            prospect_segment=lead.segment or "",
            prospect_city=lead.city or "",
            prospect_state=lead.state or "",
            lead_score=lead.score,
            lead_classification=lead.classification.value,
            lead_id=lead.id,
        )

        # Meeting and tracking links with lead ID for tracking
        ctx.meeting_link = f"{base_url}/meeting?lead={lead.id}"
        ctx.case_study_link = f"{base_url}/cases?lead={lead.id}"
        ctx.material_link = f"{base_url}/materiais?lead={lead.id}"
        ctx.unsubscribe_link = f"{base_url}/unsubscribe?lead={lead.id}&email={{email}}"
        ctx.preferences_link = f"{base_url}/preferences?lead={lead.id}"

        if decision_maker:
            ctx.decision_maker_name = decision_maker.name or ""
            ctx.decision_maker_role = decision_maker.role or ""
            ctx.decision_maker_email = decision_maker.email or ""
            if ctx.decision_maker_name:
                ctx.decision_maker_first_name = ctx.decision_maker_name.split()[0]

        # Add case studies based on segment
        ctx.custom_fields['case_study'] = cls._get_case_study(lead.segment)
        ctx.custom_fields['competitor_reference'] = cls._get_competitor_reference(lead.segment)
        ctx.custom_fields['value_prop_1'] = ctx.our_value_props[0] if ctx.our_value_props else ''
        ctx.custom_fields['value_prop_2'] = ctx.our_value_props[1] if len(ctx.our_value_props) > 1 else ''
        ctx.custom_fields['value_prop_3'] = ctx.our_value_props[2] if len(ctx.our_value_props) > 2 else ''

        return ctx

    @staticmethod
    def _get_case_study(segment: str) -> str:
        """Get relevant case study for segment."""
        case_studies = {
            'distribuidoras': 'uma distribuidora de alimentos em SP reduziu 28% no frete em 60 dias',
            'atacadistas': 'um atacarejo no RJ otimizou 35% das rotas de entrega',
            'industrias': 'uma indústria automotiva no RS eliminou 40% das divergências de frete',
            'farma_hospitalar': 'uma distribuidora farmacêutica em MG garantiu 100% compliance temperatura',
            'alimenticias': 'uma indústria de congelados em SC reduziu avarias em 45%',
            'bebidas': 'uma distribuidora de bebidas no PR cortou 25% do custo logístico',
            'autopeças': 'um distribuidor de autopeças em SP ganhou visibilidade total da frota',
            'material_construcao': 'uma rede de material de construção no RS integrou 15 filiais',
            'ecommerce_logistica': 'um e-commerce em SP automatizou 90% da cotação de fretes',
            'grande_volume': 'uma operação com 500+ entregas/dia no RJ otimizou roteirização',
        }
        return case_studies.get(segment, 'empresas similares reduziram custos logísticos em média 25%')

    @staticmethod
    def _get_competitor_reference(segment: str) -> str:
        """Get competitor reference for segment."""
        references = {
            'distribuidoras': 'distribuidoras do seu porte',
            'atacadistas': 'atacadistas da região',
            'industrias': 'indústrias do setor',
            'farma_hospitalar': 'distribuidoras farmacêuticas',
            'alimenticias': 'indústrias alimentícias',
            'bebidas': 'distribuidoras de bebidas',
            'autopeças': 'distribuidores de autopeças',
            'material_construcao': 'redes de material de construção',
            'ecommerce_logistica': 'e-commerces de grande porte',
            'grande_volume': 'operadoras de grande volume',
        }
        return references.get(segment, 'empresas do seu segmento')

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for template substitution."""
        base = {
            'our_company': self.our_company_name,
            'our_website': self.our_website,
            'our_email': self.our_email,
            'our_phone': self.our_phone,
            'our_address': self.our_address,
            'our_cnpj': self.our_cnpj,
            'company_name': self.prospect_company_name or self.prospect_trade_name or "sua empresa",
            'trade_name': self.prospect_trade_name or self.prospect_company_name or "sua empresa",
            'segment': self.prospect_segment or "seu segmento",
            'city': self.prospect_city or "sua cidade",
            'state': self.prospect_state or "",
            'contact_name': self.decision_maker_first_name or self.decision_maker_name or "lá",
            'full_name': self.decision_maker_name or "Prezado(a)",
            'role': self.decision_maker_role or "responsável pela logística",
            'dm_email': self.decision_maker_email or "",
            'score': f"{self.lead_score:.0f}",
            'classification': self.lead_classification,
            'meeting_link': self.meeting_link,
            'case_study_link': self.case_study_link,
            'material_link': self.material_link,
            'unsubscribe_link': self.unsubscribe_link,
            'preferences_link': self.preferences_link,
            **self.custom_fields
        }

        # Add value props individually
        for i, vp in enumerate(self.our_value_props, 1):
            base[f'value_prop_{i}'] = vp

        return base


@dataclass
class EmailMessage:
    """Email message to send."""
    id: str = field(default_factory=lambda: f"email_{generate_id()}")
    lead_id: str = ""
    to_email: str = ""
    to_name: str = ""

    # Template or custom
    template_name: Optional[str] = None
    custom_subject: Optional[str] = None
    custom_html: Optional[str] = None
    custom_text: Optional[str] = None

    # Personalization
    variables: Dict[str, str] = field(default_factory=dict)

    # Attachments
    attachments: List[Dict[str, Any]] = field(default_factory=list)  # {filename, content, mimetype}

    # Scheduling
    scheduled_at: Optional[datetime] = None
    send_after: Optional[datetime] = None  # For follow-ups

    # Tracking
    status: EmailStatus = EmailStatus.PENDING
    provider: EmailProvider = EmailProvider.SMTP
    external_id: Optional[str] = None  # Message-ID or provider ID
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    # Metadata
    campaign_stage: CampaignStage = CampaignStage.INITIAL
    campaign_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    # Tracking pixel and link IDs
    tracking_pixel_id: str = field(default_factory=lambda: generate_id())
    tracking_links: Dict[str, str] = field(default_factory=dict)  # url -> tracking_id

    def render(self, template: EmailTemplate) -> tuple:
        """Render email with template."""
        # Subject
        subject = template.render_subject(self.variables) if template else self.custom_subject or ""

        # HTML body
        if template:
            html_body = template.render_html(self.variables)
            text_body = template.render_text(self.variables)
        else:
            html_body = self.custom_html or ""
            text_body = self.custom_text or ""

        # Inject tracking pixel
        tracking_pixel = f'<img src="https://averta.com.br/track/open/{self.tracking_pixel_id}" width="1" height="1" alt="" style="display:none;">'
        if '</body>' in html_body:
            html_body = html_body.replace('</body>', f'{tracking_pixel}</body>')
        else:
            html_body += tracking_pixel

        # Wrap links for click tracking
        for original_url, tracking_id in self.tracking_links.items():
            tracked_url = f"https://averta.com.br/track/click/{tracking_id}?url={original_url}"
            html_body = html_body.replace(original_url, tracked_url)
            text_body = text_body.replace(original_url, tracked_url)

        return subject, html_body, text_body

    def to_mime(self, template: EmailTemplate, from_email: str, from_name: str) -> MIMEMultipart:
        """Convert to MIME message."""
        subject, html_body, text_body = self.render(template)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr((from_name, from_email))
        msg['To'] = formataddr((self.to_name, self.to_email)) if self.to_name else self.to_email
        msg['Message-ID'] = make_msgid(domain='averta.com.br')
        msg['List-Unsubscribe'] = f'<{self.variables.get("unsubscribe_link", "https://averta.com.br/unsubscribe")}>'
        msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'

        # Add custom headers for tracking
        msg['X-Campaign-ID'] = self.campaign_id or ""
        msg['X-Lead-ID'] = self.lead_id
        msg['X-Message-ID'] = self.id

        # Attach parts
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Attachments
        for att in self.attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(att['content'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{att["filename"]}"')
            msg.attach(part)

        return msg


@dataclass
class EmailCampaign:
    """Email campaign configuration."""
    id: str = field(default_factory=lambda: f"camp_{generate_id()}")
    name: str = ""
    description: str = ""

    # Targeting
    lead_classifications: List[LeadClassification] = field(default_factory=lambda: [LeadClassification.A, LeadClassification.B])
    min_score: float = 70
    max_emails_per_lead: int = 4
    segments: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    has_email_only: bool = True  # Only leads with email

    # Sequence
    sequence: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"template": "initial_outreach", "delay_days": 0, "stage": CampaignStage.INITIAL},
        {"template": "follow_up_1", "delay_days": 3, "stage": CampaignStage.FOLLOW_UP_1},
        {"template": "follow_up_2", "delay_days": 7, "stage": CampaignStage.FOLLOW_UP_2},
        {"template": "value_proposition", "delay_days": 14, "stage": CampaignStage.FOLLOW_UP_3},
        {"template": "breakup", "delay_days": 30, "stage": CampaignStage.FOLLOW_UP_3},
    ])

    # Scheduling
    business_hours_only: bool = True
    business_hours_start: int = 8
    business_hours_end: int = 18
    timezone: str = "America/Sao_Paulo"
    days_of_week: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon-Fri
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 200
    rate_limit_per_day: int = 1000

    # Opt-out
    respect_opt_out: bool = True
    opt_out_keywords: List[str] = field(default_factory=lambda: [
        "não quero", "nao quero", "parar", "cancelar", "remover",
        "não tenho interesse", "nao tenho interesse", "descadastrar",
        "unsubscribe", "opt out", "pare de mandar"
    ])

    # Status
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Stats
    stats: Dict[str, int] = field(default_factory=lambda: {
        'total_leads': 0,
        'emails_sent': 0,
        'emails_delivered': 0,
        'emails_opened': 0,
        'emails_clicked': 0,
        'replies_received': 0,
        'unsubscribes': 0,
        'bounces': 0,
        'errors': 0,
    })


class EmailProviderBase(ABC):
    """Abstract base for email providers."""

    @abstractmethod
    async def send_email(self, message: EmailMessage, template: EmailTemplate) -> Dict[str, Any]:
        """Send email and return result with external_id."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate provider connection."""
        pass

    @abstractmethod
    def get_provider_type(self) -> EmailProvider:
        """Get provider type."""
        pass


class SMTPEmailProvider(EmailProviderBase):
    """SMTP Email Provider (Zoho, Gmail, Outlook, custom)."""

    def __init__(self):
        self.settings = get_settings()

        # Load from environment or settings
        self.smtp_host = os.getenv('ZOHO_SMTP_HOST') or self.settings.__dict__.get('smtp_host', 'smtppro.zoho.com')
        self.smtp_port = int(os.getenv('ZOHO_SMTP_PORT') or self.settings.__dict__.get('smtp_port', 465))
        self.smtp_user = os.getenv('ZOHO_EMAIL') or self.settings.__dict__.get('smtp_user', 'pedrolarrieuceo@avertabrasil.com.br')
        self.smtp_password = os.getenv('ZOHO_PASSWORD') or self.settings.__dict__.get('smtp_password', '')
        self.from_email = self.settings.__dict__.get('smtp_from_email', self.smtp_user)
        self.from_name = self.settings.__dict__.get('smtp_from_name', 'Averta Logística')
        self.use_tls = self.smtp_port == 587
        self.use_ssl = self.smtp_port == 465

        logger.info(f"SMTP Provider initialized: {self.smtp_host}:{self.smtp_port} as {self.from_email}")

    def get_provider_type(self) -> EmailProvider:
        return EmailProvider.SMTP

    def _create_ssl_context(self):
        """Create SSL context with proper certificate handling for Windows."""
        if HAS_CERTIFI:
            context = ssl.create_default_context(cafile=certifi.where())
        else:
            context = ssl.create_default_context()
        # On Windows, sometimes we need to be more permissive for testing
        # In production, you should use proper certificates
        return context

    async def validate_connection(self) -> bool:
        """Validate SMTP connection."""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        try:
            if self.use_ssl:
                context = self._create_ssl_context()
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                if self.use_tls:
                    context = self._create_ssl_context()
                    server.starttls(context=context)

            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            logger.info("SMTP connection validated successfully")
            return True
        except ssl.SSLError as e:
            # Try without verification as fallback (for testing on Windows)
            logger.warning(f"SSL error, trying without verification: {e}")
            try:
                if self.use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=10)
                else:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                    if self.use_tls:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        server.starttls(context=context)

                server.login(self.smtp_user, self.smtp_password)
                server.quit()
                logger.info("SMTP connection validated successfully (with relaxed SSL)")
                return True
            except Exception as e2:
                logger.error(f"SMTP validation failed even with relaxed SSL: {e2}")
                return False
        except Exception as e:
            logger.error(f"SMTP validation failed: {e}")
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3)
    )
    async def send_email(self, message: EmailMessage, template: EmailTemplate) -> Dict[str, Any]:
        """Send email via SMTP."""
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP credentials not configured")

        mime_msg = message.to_mime(template, self.from_email, self.from_name)

        def _try_send(use_relaxed_ssl=False):
            if self.use_ssl:
                if use_relaxed_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                else:
                    context = self._create_ssl_context()
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                if self.use_tls:
                    if use_relaxed_ssl:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                    else:
                        context = self._create_ssl_context()
                    server.starttls(context=context)

            server.login(self.smtp_user, self.smtp_password)

            # Send
            recipients = [self._extract_email(message.to_email)]
            server.sendmail(self.from_email, recipients, mime_msg.as_string())
            server.quit()

        try:
            _try_send(use_relaxed_ssl=False)
        except ssl.SSLError as e:
            logger.warning(f"SSL error, retrying with relaxed SSL: {e}")
            _try_send(use_relaxed_ssl=True)

        # Extract message ID
        external_id = mime_msg['Message-ID']

        logger.info(f"Email sent via SMTP to {message.to_email}: {external_id}")

        return {
            "success": True,
            "external_id": external_id,
            "provider": "smtp"
        }

        # Note: The @retry decorator handles retries for exceptions
        # Specific exceptions are caught and returned as error dicts above
        # If we reach here, it's a success

    @staticmethod
    def _extract_email(email_str: str) -> str:
        """Extract email address from 'Name <email@domain.com>' format."""
        import re
        match = re.search(r'<(.+?)>', email_str)
        return match.group(1) if match else email_str


class SendGridEmailProvider(EmailProviderBase):
    """SendGrid API Email Provider."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = os.getenv('SENDGRID_API_KEY') or self.settings.__dict__.get('sendgrid_api_key', '')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL') or self.settings.__dict__.get('sendgrid_from_email', 'noreply@averta.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME') or self.settings.__dict__.get('sendgrid_from_name', 'Averta Logística')
        self.base_url = "https://api.sendgrid.com/v3"

        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    def get_provider_type(self) -> EmailProvider:
        return EmailProvider.SENDGRID

    async def validate_connection(self) -> bool:
        """Validate SendGrid API connection."""
        if not self.api_key:
            logger.warning("SendGrid API key not configured")
            return False

        try:
            response = await self.client.get(f"{self.base_url}/user/profile")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"SendGrid validation failed: {e}")
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3)
    )
    async def send_email(self, message: EmailMessage, template: EmailTemplate) -> Dict[str, Any]:
        """Send email via SendGrid API."""
        if not self.api_key:
            raise ValueError("SendGrid API key not configured")

        subject, html_body, text_body = message.render(template)

        payload = {
            "personalizations": [{
                "to": [{"email": message.to_email, "name": message.to_name}],
                "subject": subject,
                "custom_args": {
                    "campaign_id": message.campaign_id or "",
                    "lead_id": message.lead_id,
                    "message_id": message.id,
                },
                "tracking_settings": {
                    "click_tracking": {"enable": True, "enable_text": True},
                    "open_tracking": {"enable": True}
                }
            }],
            "from": {"email": self.from_email, "name": self.from_name},
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body}
            ],
            "headers": {
                "X-Campaign-ID": message.campaign_id or "",
                "X-Lead-ID": message.lead_id,
                "X-Message-ID": message.id,
            },
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True, "substitution_tag": "%opentrack%"},
                "subscription_tracking": {"enable": True, "text": "Cancelar inscrição: ", "html": "Cancelar inscrição: "}
            }
        }

        # Add attachments if any
        if message.attachments:
            payload["attachments"] = []
            for att in message.attachments:
                import base64
                payload["attachments"].append({
                    "content": base64.b64encode(att['content']).decode(),
                    "filename": att['filename'],
                    "type": att.get('mimetype', 'application/octet-stream'),
                    "disposition": "attachment"
                })

        response = await self.client.post(f"{self.base_url}/mail/send", json=payload)

        if response.status_code >= 400:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
            raise Exception(f"SendGrid API Error {response.status_code}: {error_data}")

        # SendGrid returns 202 with X-Message-Id header
        external_id = response.headers.get('X-Message-Id', generate_id())

        return {
            "success": True,
            "external_id": external_id,
            "provider": "sendgrid"
        }

    async def close(self):
        await self.client.aclose()


class IntelligentEmailEngine:
    """Intelligent email engine with personalization and campaign logic."""

    def __init__(self, provider: EmailProviderBase = None):
        self.settings = get_settings()
        self.provider = provider or SMTPEmailProvider()
        self.template_manager = EmailTemplateManager()
        self.campaigns: Dict[str, EmailCampaign] = {}
        self.conversation_states: Dict[str, Dict] = {}  # lead_id -> state

        # Rate limiting
        self.minute_counts: List[datetime] = []
        self.hour_counts: List[datetime] = []
        self.day_counts: List[datetime] = []

        # Tracking
        self.sent_emails: Dict[str, EmailMessage] = {}  # message_id -> message

    async def initialize(self) -> bool:
        """Initialize provider connection."""
        return await self.provider.validate_connection()

    def create_personalized_email(
        self,
        lead: QualifiedLead,
        template_name: str,
        decision_maker: Optional[DecisionMaker] = None,
        custom_variables: Dict[str, str] = None,
        campaign_id: str = None,
        campaign_stage: CampaignStage = CampaignStage.INITIAL
    ) -> EmailMessage:
        """Create personalized email for a lead."""

        # Build personalization context
        context = PersonalizationContext.from_lead(lead, decision_maker)

        # Get template
        template = self.template_manager.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Determine best email
        email = lead.email
        if not email:
            raise ValueError(f"No email for lead {lead.id}")

        # Merge variables
        variables = context.to_dict()
        if custom_variables:
            variables.update(custom_variables)

        # Add tracking links for this message
        msg_id = generate_id()
        variables['tracking_pixel_id'] = msg_id

        # Create message
        message = EmailMessage(
            lead_id=lead.id,
            to_email=email,
            to_name=context.decision_maker_name or lead.name or "",
            template_name=template_name,
            variables=variables,
            campaign_stage=campaign_stage,
            campaign_id=campaign_id,
            tracking_pixel_id=msg_id,
        )

        # Add tracking links
        for link_name in ['meeting_link', 'case_study_link', 'material_link', 'unsubscribe_link', 'preferences_link']:
            if link_name in variables:
                tracking_id = generate_id()
                message.tracking_links[variables[link_name]] = tracking_id

        return message

    def create_custom_email(
        self,
        lead: QualifiedLead,
        subject: str,
        html_body: str,
        text_body: str,
        decision_maker: Optional[DecisionMaker] = None,
        custom_variables: Dict[str, str] = None,
        campaign_id: str = None,
        campaign_stage: CampaignStage = CampaignStage.INITIAL
    ) -> EmailMessage:
        """Create custom (non-template) email."""

        context = PersonalizationContext.from_lead(lead, decision_maker)
        variables = context.to_dict()
        if custom_variables:
            variables.update(custom_variables)

        msg_id = generate_id()
        variables['tracking_pixel_id'] = msg_id

        message = EmailMessage(
            lead_id=lead.id,
            to_email=lead.email or "",
            to_name=context.decision_maker_name or lead.name or "",
            custom_subject=subject,
            custom_html=html_body,
            custom_text=text_body,
            variables=variables,
            campaign_stage=campaign_stage,
            campaign_id=campaign_id,
            tracking_pixel_id=msg_id,
        )

        return message

    def _check_rate_limits(self, campaign: EmailCampaign) -> bool:
        """Check if we can send more emails within rate limits."""
        now = datetime.utcnow()

        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        self.minute_counts = [t for t in self.minute_counts if t > minute_ago]
        self.hour_counts = [t for t in self.hour_counts if t > hour_ago]
        self.day_counts = [t for t in self.day_counts if t > day_ago]

        if len(self.minute_counts) >= campaign.rate_limit_per_minute:
            return False
        if len(self.hour_counts) >= campaign.rate_limit_per_hour:
            return False
        if len(self.day_counts) >= campaign.rate_limit_per_day:
            return False

        return True

    def _record_send(self):
        """Record a send for rate limiting."""
        now = datetime.utcnow()
        self.minute_counts.append(now)
        self.hour_counts.append(now)
        self.day_counts.append(now)

    def _is_business_hours(self, campaign: EmailCampaign) -> bool:
        """Check if current time is within business hours."""
        if not campaign.business_hours_only:
            return True

        now = datetime.utcnow()
        # Simplified: assume UTC-3 for Brazil
        local_hour = (now.hour - 3) % 24

        return campaign.business_hours_start <= local_hour < campaign.business_hours_end

    def _is_business_day(self, campaign: EmailCampaign) -> bool:
        """Check if today is a business day."""
        now = datetime.utcnow()
        return now.weekday() in campaign.days_of_week

    def _check_opt_out(self, text: str, campaign: EmailCampaign) -> bool:
        """Check if message contains opt-out keywords."""
        text_lower = text.lower()
        for keyword in campaign.opt_out_keywords:
            if keyword in text_lower:
                return True
        return False

    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """Send a single email with retry logic."""
        template = None
        if message.template_name:
            template = self.template_manager.get_template(message.template_name)
            if not template:
                return {"success": False, "error": f"Template not found: {message.template_name}"}

        for attempt in range(message.max_retries + 1):
            try:
                result = await self.provider.send_email(message, template)

                if result.get("success"):
                    message.status = EmailStatus.SENT
                    message.external_id = result.get("external_id")
                    message.sent_at = datetime.utcnow()
                    message.retry_count = attempt
                    self._record_send()

                    # Store for tracking
                    self.sent_emails[message.id] = message

                    # Update conversation state
                    self._update_conversation_state(message)

                    return result
                else:
                    raise Exception(result.get("error", "Unknown error"))

            except Exception as e:
                message.retry_count = attempt + 1
                message.error = str(e)
                logger.warning(f"Email send attempt {attempt + 1} failed: {e}")

                if attempt < message.max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    message.status = EmailStatus.FAILED
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": "Max retries exceeded"}

    def _update_conversation_state(self, message: EmailMessage):
        """Update conversation tracking."""
        lead_id = message.lead_id
        if lead_id not in self.conversation_states:
            self.conversation_states[lead_id] = {
                'stage': CampaignStage.INITIAL,
                'emails_sent': 0,
                'last_sent_at': None,
                'replies': 0,
                'opens': 0,
                'clicks': 0,
                'unsubscribed': False,
            }

        state = self.conversation_states[lead_id]
        state['emails_sent'] += 1
        state['last_sent_at'] = datetime.utcnow()
        state['stage'] = message.campaign_stage

    def get_conversation_state(self, lead_id: str) -> Dict:
        """Get conversation state for a lead."""
        return self.conversation_states.get(lead_id, {
            'stage': CampaignStage.INITIAL,
            'emails_sent': 0,
            'last_sent_at': None,
            'replies': 0,
            'opens': 0,
            'clicks': 0,
            'unsubscribed': False,
        })

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Optional[Dict]:
        """Process incoming webhook event (SendGrid, etc.)."""
        try:
            event_type = event_data.get('event', '')
            email_id = event_data.get('message_id', '') or event_data.get('X-Message-ID', '')
            lead_id = event_data.get('lead_id', '') or event_data.get('X-Lead-ID', '')
            campaign_id = event_data.get('campaign_id', '') or event_data.get('X-Campaign-ID', '')

            if not lead_id:
                return None

            state = self.get_conversation_state(lead_id)

            if event_type in ['delivered', 'delivery']:
                state['delivered_at'] = datetime.utcnow()
                return {"action": "delivered", "lead_id": lead_id}

            elif event_type in ['open', 'opened']:
                state['opens'] += 1
                state['last_open_at'] = datetime.utcnow()
                return {"action": "opened", "lead_id": lead_id}

            elif event_type in ['click', 'clicked']:
                state['clicks'] += 1
                state['last_click_at'] = datetime.utcnow()
                url = event_data.get('url', '')
                return {"action": "clicked", "lead_id": lead_id, "url": url}

            elif event_type in ['bounce', 'blocked']:
                state['bounced'] = True
                return {"action": "bounced", "lead_id": lead_id}

            elif event_type in ['spam_report', 'spam']:
                state['spam_complaint'] = True
                return {"action": "spam_complaint", "lead_id": lead_id}

            elif event_type in ['unsubscribe', 'unsubscribed']:
                state['unsubscribed'] = True
                state['stage'] = CampaignStage.UNSUBSCRIBED
                return {"action": "unsubscribed", "lead_id": lead_id}

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")

        return None

    def register_campaign(self, campaign: EmailCampaign) -> str:
        """Register a campaign."""
        self.campaigns[campaign.id] = campaign
        return campaign.id

    def get_campaign(self, campaign_id: str) -> Optional[EmailCampaign]:
        """Get campaign by ID."""
        return self.campaigns.get(campaign_id)

    async def run_campaign_step(
        self,
        campaign: EmailCampaign,
        leads: List[QualifiedLead],
        decision_makers_map: Dict[str, DecisionMaker] = None,
        step_index: int = 0
    ) -> Dict[str, Any]:
        """Run a specific step of a campaign."""

        if step_index >= len(campaign.sequence):
            return {"success": True, "completed": True, "message": "Campaign sequence completed"}

        step = campaign.sequence[step_index]
        template_name = step["template"]
        stage = step["stage"]

        template = self.template_manager.get_template(template_name)
        if not template:
            return {"success": False, "error": f"Template not found: {template_name}"}

        results = {
            "campaign_id": campaign.id,
            "step": step_index,
            "template": template_name,
            "stage": stage.value,
            "total_leads": len(leads),
            "sent": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        for lead in leads:
            try:
                # Check opt-out
                state = self.get_conversation_state(lead.id)
                if state.get('unsubscribed'):
                    results['skipped'] += 1
                    continue

                # Check max emails per lead
                if state.get('emails_sent', 0) >= campaign.max_emails_per_lead:
                    results['skipped'] += 1
                    continue

                # Check business hours/day
                if not self._is_business_day(campaign) or not self._is_business_hours(campaign):
                    logger.info("Outside business hours/day, pausing")
                    break

                # Check rate limits
                if not self._check_rate_limits(campaign):
                    logger.info("Rate limit reached, waiting...")
                    await asyncio.sleep(60)
                    continue

                # Get decision maker
                dm = None
                if decision_makers_map:
                    dm = decision_makers_map.get(lead.id)
                elif lead.decision_makers:
                    dm = lead.decision_makers[0]

                # Create and send message
                message = self.create_personalized_email(
                    lead=lead,
                    template_name=template_name,
                    decision_maker=dm,
                    campaign_id=campaign.id,
                    campaign_stage=stage
                )

                result = await self.send_email(message)

                if result.get("success"):
                    results['sent'] += 1
                    campaign.stats['emails_sent'] += 1
                else:
                    results['failed'] += 1
                    campaign.stats['errors'] += 1
                    results['errors'].append(f"Lead {lead.id}: {result.get('error')}")

                # Small delay between emails
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing lead {lead.id}: {e}")
                results['failed'] += 1
                results['errors'].append(f"Lead {lead.id}: {str(e)}")

        return results

    async def run_full_campaign(
        self,
        campaign: EmailCampaign,
        leads: List[QualifiedLead],
        decision_makers_map: Dict[str, DecisionMaker] = None
    ) -> Dict[str, Any]:
        """Run full campaign sequence."""
        campaign.started_at = datetime.utcnow()
        campaign.stats['total_leads'] = len(leads)

        all_results = {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "total_leads": len(leads),
            "steps": [],
            "total_sent": 0,
            "total_failed": 0,
        }

        for step_index, step in enumerate(campaign.sequence):
            logger.info(f"Running campaign step {step_index + 1}/{len(campaign.sequence)}: {step['template']}")

            step_result = await self.run_campaign_step(
                campaign, leads, decision_makers_map, step_index
            )

            all_results["steps"].append(step_result)
            all_results["total_sent"] += step_result.get("sent", 0)
            all_results["total_failed"] += step_result.get("failed", 0)

            # Wait before next step (except last)
            if step_index < len(campaign.sequence) - 1:
                delay_days = step.get("delay_days", 0)
                if delay_days > 0:
                    logger.info(f"Waiting {delay_days} days before next step...")
                    # In production, this would be scheduled, not slept
                    # await asyncio.sleep(delay_days * 86400)

        campaign.completed_at = datetime.utcnow()
        return all_results


class EmailCampaignBuilder:
    """Builder for creating email campaigns with fluent interface."""

    def __init__(self, name: str):
        self.campaign = EmailCampaign(name=name)

    def with_description(self, desc: str) -> 'EmailCampaignBuilder':
        self.campaign.description = desc
        return self

    def targeting_classifications(self, *classifications: LeadClassification) -> 'EmailCampaignBuilder':
        self.campaign.lead_classifications = list(classifications)
        return self

    def targeting_min_score(self, score: float) -> 'EmailCampaignBuilder':
        self.campaign.min_score = score
        return self

    def targeting_segments(self, *segments: str) -> 'EmailCampaignBuilder':
        self.campaign.segments = list(segments)
        return self

    def targeting_states(self, *states: str) -> 'EmailCampaignBuilder':
        self.campaign.states = list(states)
        return self

    def with_sequence(self, sequence: List[Dict]) -> 'EmailCampaignBuilder':
        self.campaign.sequence = sequence
        return self

    def with_schedule(
        self,
        business_hours_only: bool = True,
        start_hour: int = 8,
        end_hour: int = 18,
        timezone: str = "America/Sao_Paulo",
        days_of_week: List[int] = None,
        rate_per_minute: int = 10,
        rate_per_hour: int = 200,
        rate_per_day: int = 1000
    ) -> 'EmailCampaignBuilder':
        self.campaign.business_hours_only = business_hours_only
        self.campaign.business_hours_start = start_hour
        self.campaign.business_hours_end = end_hour
        self.campaign.timezone = timezone
        self.campaign.days_of_week = days_of_week or [0, 1, 2, 3, 4]
        self.campaign.rate_limit_per_minute = rate_per_minute
        self.campaign.rate_limit_per_hour = rate_per_hour
        self.campaign.rate_limit_per_day = rate_per_day
        return self

    def with_opt_out_keywords(self, *keywords: str) -> 'EmailCampaignBuilder':
        self.campaign.opt_out_keywords.extend(keywords)
        return self

    def max_emails_per_lead(self, max_emails: int) -> 'EmailCampaignBuilder':
        self.campaign.max_emails_per_lead = max_emails
        return self

    def build(self) -> EmailCampaign:
        return self.campaign


async def create_email_engine(
    provider_type: EmailProvider = EmailProvider.SMTP
) -> IntelligentEmailEngine:
    """Factory to create email engine with provider."""
    provider = None

    if provider_type == EmailProvider.SMTP:
        provider = SMTPEmailProvider()
    elif provider_type == EmailProvider.SENDGRID:
        provider = SendGridEmailProvider()

    engine = IntelligentEmailEngine(provider)
    await engine.initialize()
    return engine


# Example usage
async def example_usage():
    """Example of how to use the email engine."""

    # Create engine
    engine = await create_email_engine(EmailProvider.SMTP)

    # Create campaign
    campaign = (EmailCampaignBuilder("Q1_2024_Outbound_Distribuidoras")
        .with_description("Prospecção ativa para distribuidoras no Sudeste via email")
        .targeting_classifications(LeadClassification.A, LeadClassification.B)
        .targeting_min_score(75)
        .targeting_segments("distribuidoras", "atacadistas")
        .targeting_states("SP", "RJ", "MG", "ES")
        .with_sequence([
            {"template": "initial_outreach", "delay_days": 0, "stage": CampaignStage.INITIAL},
            {"template": "follow_up_1", "delay_days": 3, "stage": CampaignStage.FOLLOW_UP_1},
            {"template": "follow_up_2", "delay_days": 7, "stage": CampaignStage.FOLLOW_UP_2},
            {"template": "value_proposition", "delay_days": 14, "stage": CampaignStage.FOLLOW_UP_3},
            {"template": "case_study", "delay_days": 21, "stage": CampaignStage.FOLLOW_UP_3},
            {"template": "meeting_request", "delay_days": 30, "stage": CampaignStage.FOLLOW_UP_3},
            {"template": "breakup", "delay_days": 45, "stage": CampaignStage.FOLLOW_UP_3},
        ])
        .with_schedule(
            business_hours_only=True,
            start_hour=8,
            end_hour=18,
            timezone="America/Sao_Paulo",
            rate_per_minute=10,
            rate_per_hour=200,
            rate_per_day=1000
        )
        .max_emails_per_lead(4)
        .with_opt_out_keywords("não quero", "parar", "cancelar", "descadastrar")
        .build())

    engine.register_campaign(campaign)

    # Would get leads from database
    # leads = db.get_leads_for_campaign(campaign)
    # decision_makers = {lead.id: lead.decision_makers[0] for lead in leads if lead.decision_makers}

    # Run campaign
    # results = await engine.run_full_campaign(campaign, leads, decision_makers)
    # print(f"Campaign results: {results}")


if __name__ == "__main__":
    asyncio.run(example_usage())