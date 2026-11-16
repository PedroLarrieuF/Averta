"""
WhatsApp Business API Client and Web Automation Fallback.

Supports:
- Official WhatsApp Business Cloud API (Meta)
- Web automation fallback using Playwright
- Intelligent message personalization
- Campaign management with smart scheduling
- Conversation tracking and follow-up logic
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import asyncio
import json
import time
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id, normalize_phone
from storage.models import QualifiedLead, LeadClassification, DecisionMaker
from .templates import TemplateManager, WhatsAppTemplate, TemplateLanguage, TemplateCategory

logger = get_logger(__name__)


class WhatsAppProvider(str, Enum):
    """WhatsApp provider types."""
    CLOUD_API = "cloud_api"       # Meta WhatsApp Business Cloud API
    ON_PREMISE = "on_premise"     # Self-hosted WhatsApp Business API
    WEB_AUTOMATION = "web"        # WhatsApp Web automation (Playwright)


class MessageStatus(str, Enum):
    """Message delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    REJECTED = "rejected"
    OPTED_OUT = "opted_out"


class ConversationStage(str, Enum):
    """Conversation stage for follow-up logic."""
    INITIAL = "initial"
    FOLLOW_UP_1 = "follow_up_1"
    FOLLOW_UP_2 = "follow_up_2"
    FOLLOW_UP_3 = "follow_up_3"
    REPLIED = "replied"
    MEETING_SCHEDULED = "meeting_scheduled"
    NOT_INTERESTED = "not_interested"
    OPTED_OUT = "opted_out"


@dataclass
class PersonalizationContext:
    """Context for message personalization."""
    # Company info (our company)
    our_company_name: str = "Averta"
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

    # Lead info
    lead_score: float = 0
    lead_classification: str = ""
    lead_id: str = ""

    # Custom fields
    custom_fields: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_lead(cls, lead: QualifiedLead, decision_maker: Optional[DecisionMaker] = None) -> 'PersonalizationContext':
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

        if decision_maker:
            ctx.decision_maker_name = decision_maker.name or ""
            ctx.decision_maker_role = decision_maker.role or ""
            # Extract first name
            if ctx.decision_maker_name:
                ctx.decision_maker_first_name = ctx.decision_maker_name.split()[0]

        # Add case studies based on segment
        ctx.custom_fields['case_study'] = cls._get_case_study(lead.segment)
        ctx.custom_fields['competitor_reference'] = cls._get_competitor_reference(lead.segment)

        return ctx

    @staticmethod
    def _get_case_study(segment: str) -> str:
        """Get relevant case study for segment."""
        case_studies = {
            'distribuidoras': 'uma distribuidora de alimentos em SP reduziu 28% no frete',
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
        return "empresas do seu segmento"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for template substitution."""
        return {
            'our_company': self.our_company_name,
            'company_name': self.prospect_company_name or self.prospect_trade_name or "sua empresa",
            'trade_name': self.prospect_trade_name or self.prospect_company_name or "sua empresa",
            'segment': self.prospect_segment or "seu segmento",
            'city': self.prospect_city or "sua cidade",
            'state': self.prospect_state or "",
            'contact_name': self.decision_maker_first_name or self.decision_maker_name or "lá",
            'full_name': self.decision_maker_name or "prezado(a)",
            'role': self.decision_maker_role or "responsável pela logística",
            'score': f"{self.lead_score:.0f}",
            'classification': self.lead_classification,
            'case_study': self.custom_fields.get('case_study', ''),
            'competitor_reference': self.custom_fields.get('competitor_reference', ''),
            'value_prop_1': self.our_value_props[0] if self.our_value_props else '',
            'value_prop_2': self.our_value_props[1] if len(self.our_value_props) > 1 else '',
            'value_prop_3': self.our_value_props[2] if len(self.our_value_props) > 2 else '',
            **self.custom_fields
        }


@dataclass
class WhatsAppMessage:
    """WhatsApp message to send."""
    id: str = field(default_factory=lambda: f"msg_{generate_id()}")
    lead_id: str = ""
    contact_phone: str = ""
    contact_whatsapp: str = ""

    # Template or custom
    template_name: Optional[str] = None
    template_language: str = "pt_BR"
    custom_text: Optional[str] = None

    # Personalization
    variables: Dict[str, str] = field(default_factory=dict)

    # Media (optional)
    media_url: Optional[str] = None
    media_type: Optional[str] = None  # image, document, video
    media_caption: Optional[str] = None

    # Interactive (optional)
    buttons: List[Dict] = field(default_factory=list)
    list_sections: List[Dict] = field(default_factory=list)

    # Scheduling
    scheduled_at: Optional[datetime] = None
    send_after: Optional[datetime] = None  # For follow-ups

    # Tracking
    status: MessageStatus = MessageStatus.PENDING
    provider: WhatsAppProvider = WhatsAppProvider.CLOUD_API
    external_id: Optional[str] = None  # Meta message ID
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    # Metadata
    conversation_stage: ConversationStage = ConversationStage.INITIAL
    campaign_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to WhatsApp Cloud API format."""
        phone = self.contact_whatsapp or self.contact_phone
        if not phone:
            raise ValueError("No phone number provided")

        # Normalize to E.164 without + for API
        clean_phone = phone.replace('+', '')

        if self.template_name:
            # Template message
            components = []

            # Body variables
            if self.variables:
                body_params = [
                    {"type": "text", "text": str(v)}
                    for v in self.variables.values()
                ]
                components.append({
                    "type": "body",
                    "parameters": body_params
                })

            # Header variables (if template has header)
            header_vars = {k: v for k, v in self.variables.items() if k.startswith('header_')}
            if header_vars:
                components.append({
                    "type": "header",
                    "parameters": [
                        {"type": "text", "text": str(v)}
                        for v in header_vars.values()
                    ]
                })

            return {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {"code": self.template_language},
                    "components": components
                }
            }
        else:
            # Custom text message
            text = self.custom_text or ""
            for key, value in self.variables.items():
                text = text.replace(f"{{{{{key}}}}}", str(value))
                text = text.replace(f"{{{key}}}", str(value))

            message = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {"body": text}
            }

            # Add interactive buttons if present
            if self.buttons:
                message["type"] = "interactive"
                message["interactive"] = {
                    "type": "button",
                    "body": {"text": text},
                    "action": {
                        "buttons": self.buttons[:3]  # Max 3 buttons
                    }
                }

            return message


@dataclass
class Campaign:
    """WhatsApp campaign configuration."""
    id: str = field(default_factory=lambda: f"camp_{generate_id()}")
    name: str = ""
    description: str = ""

    # Targeting
    lead_classifications: List[LeadClassification] = field(default_factory=lambda: [LeadClassification.A, LeadClassification.B])
    min_score: float = 70
    max_messages_per_lead: int = 3
    segments: List[str] = field(default_factory=list)  # Empty = all
    states: List[str] = field(default_factory=list)    # Empty = all

    # Message sequence
    initial_template: str = "initial_contact"
    follow_up_templates: List[str] = field(default_factory=lambda: ["follow_up_1", "follow_up_2", "value_proposition"])
    follow_up_intervals_hours: List[int] = field(default_factory=lambda: [24, 72, 168])  # 1d, 3d, 7d

    # Scheduling
    business_hours_only: bool = True
    business_hours_start: int = 8
    business_hours_end: int = 18
    timezone: str = "America/Sao_Paulo"
    rate_limit_per_minute: int = 20
    rate_limit_per_hour: int = 500
    rate_limit_per_day: int = 2000

    # Opt-out handling
    respect_opt_out: bool = True
    opt_out_keywords: List[str] = field(default_factory=lambda: [
        "não quero", "nao quero", "parar", "cancelar", "remover",
        "não tenho interesse", "nao tenho interesse", "descadastrar"
    ])

    # Status
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Stats
    stats: Dict[str, int] = field(default_factory=lambda: {
        'total_leads': 0,
        'messages_sent': 0,
        'messages_delivered': 0,
        'messages_read': 0,
        'replies_received': 0,
        'opt_outs': 0,
        'errors': 0,
    })


class WhatsAppProviderBase(ABC):
    """Abstract base for WhatsApp providers."""

    @abstractmethod
    async def send_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send message and return result with external_id."""
        pass

    @abstractmethod
    async def get_message_status(self, external_id: str) -> MessageStatus:
        """Get message status."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate provider connection."""
        pass

    @abstractmethod
    def get_provider_type(self) -> WhatsAppProvider:
        """Get provider type."""
        pass


class CloudAPIProvider(WhatsAppProviderBase):
    """Meta WhatsApp Business Cloud API Provider."""

    def __init__(self):
        self.settings = get_settings()
        self.access_token = self.settings.__dict__.get('whatsapp_access_token', '')
        self.phone_number_id = self.settings.__dict__.get('whatsapp_phone_number_id', '')
        self.business_account_id = self.settings.__dict__.get('whatsapp_business_account_id', '')
        self.api_version = self.settings.__dict__.get('whatsapp_api_version', 'v18.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )

    def get_provider_type(self) -> WhatsAppProvider:
        return WhatsAppProvider.CLOUD_API

    async def validate_connection(self) -> bool:
        """Validate API connection."""
        if not self.access_token or not self.phone_number_id:
            logger.warning("Cloud API credentials not configured")
            return False

        try:
            response = await self.client.get(
                f"{self.base_url}/{self.phone_number_id}",
                params={"fields": "verified_name,display_phone_number"}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cloud API validation failed: {e}")
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3)
    )
    async def send_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send message via Cloud API."""
        if not self.phone_number_id:
            raise ValueError("Phone number ID not configured")

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = message.to_api_format()

        logger.debug(f"Sending message to {message.contact_phone}: {payload}")

        response = await self.client.post(url, json=payload)

        if response.status_code >= 400:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
            raise Exception(f"API Error {response.status_code}: {error_data}")

        result = response.json()
        external_id = result.get('messages', [{}])[0].get('id')

        return {
            "success": True,
            "external_id": external_id,
            "response": result
        }

    async def get_message_status(self, external_id: str) -> MessageStatus:
        """Get message status (not directly available via API, use webhooks)."""
        # Status comes via webhook, not polling
        return MessageStatus.SENT

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class WebAutomationProvider(WhatsAppProviderBase):
    """WhatsApp Web Automation using Playwright."""

    def __init__(self):
        self.settings = get_settings()
        self.browser = None
        self.page = None
        self.context = None
        self.logged_in = False
        self.session_file = Path("whatsapp_session.json")

    def get_provider_type(self) -> WhatsAppProvider:
        return WhatsAppProvider.WEB_AUTOMATION

    async def validate_connection(self) -> bool:
        """Validate by checking if logged in."""
        try:
            await self._ensure_browser()
            return self.logged_in
        except Exception:
            return False

    async def _ensure_browser(self):
        """Initialize browser if needed."""
        if self.browser is None:
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                # Restore session if exists
                if self.session_file.exists():
                    self.context = await self.browser.new_context(
                        storage_state=str(self.session_file)
                    )
                else:
                    self.context = await self.browser.new_context()

                self.page = await self.context.new_page()

                # Check if logged in
                await self.page.goto("https://web.whatsapp.com")
                await self.page.wait_for_timeout(3000)

                # Check for QR code (not logged in) or chat list (logged in)
                try:
                    await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
                    self.logged_in = True
                    logger.info("WhatsApp Web session restored")
                except:
                    self.logged_in = False
                    logger.info("WhatsApp Web needs QR code login")

            except ImportError:
                logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
                raise
            except Exception as e:
                logger.error(f"Browser initialization failed: {e}")
                raise

    async def login_with_qr(self, timeout_seconds: int = 120) -> bool:
        """Login via QR code."""
        await self._ensure_browser()

        if self.logged_in:
            return True

        logger.info("Waiting for QR code scan...")

        try:
            # Wait for QR code to appear
            await self.page.wait_for_selector('[data-testid="qr-code"]', timeout=10000)

            # Take screenshot of QR code for user
            qr_path = "whatsapp_qr.png"
            await self.page.screenshot(path=qr_path)
            logger.info(f"QR code saved to {qr_path}")

            # Wait for login (chat list appears)
            await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=timeout_seconds * 1000)

            # Save session
            await self.context.storage_state(path=str(self.session_file))
            self.logged_in = True
            logger.info("WhatsApp Web login successful")
            return True

        except Exception as e:
            logger.error(f"QR login failed: {e}")
            return False

    async def send_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send message via WhatsApp Web."""
        await self._ensure_browser()

        if not self.logged_in:
            raise Exception("Not logged in. Run login_with_qr() first.")

        phone = message.contact_whatsapp or message.contact_phone
        if not phone:
            raise ValueError("No phone number provided")

        # Normalize phone for WhatsApp Web (remove + and spaces)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('55'):
            clean_phone = clean_phone[2:]  # Remove country code for search

        try:
            # Search for contact
            search_box = await self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=5000)
            await search_box.fill(clean_phone)
            await self.page.wait_for_timeout(1000)

            # Click on first result
            chat_item = await self.page.wait_for_selector('[data-testid="chat-list-item"]', timeout=5000)
            await chat_item.click()
            await self.page.wait_for_timeout(1000)

            # Type message
            text = message.custom_text or ""
            for key, value in message.variables.items():
                text = text.replace(f"{{{{{key}}}}}", str(value))
                text = text.replace(f"{{{key}}}", str(value))

            if message.template_name:
                # Would need to render template - simplified here
                text = f"[Template: {message.template_name}]\n{text}"

            input_box = await self.page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=5000)
            await input_box.fill(text)

            # Send
            send_button = await self.page.wait_for_selector('[data-testid="compose-btn-send"]', timeout=5000)
            await send_button.click()

            # Wait for sent confirmation
            await self.page.wait_for_timeout(2000)

            # Generate fake external ID
            external_id = f"web_{generate_id()}"

            return {
                "success": True,
                "external_id": external_id,
                "provider": "web"
            }

        except Exception as e:
            logger.error(f"Web automation send failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_message_status(self, external_id: str) -> MessageStatus:
        """Not available via web automation."""
        return MessageStatus.SENT

    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


class IntelligentMessagingEngine:
    """Intelligent messaging engine with personalization and campaign logic."""

    def __init__(self, provider: WhatsAppProviderBase = None):
        self.settings = get_settings()
        self.provider = provider or CloudAPIProvider()
        self.template_manager = TemplateManager()
        self.campaigns: Dict[str, Campaign] = {}
        self.conversation_states: Dict[str, Dict] = {}  # lead_id -> state

        # Message queue for rate limiting
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False

        # Rate limiting
        self.minute_counts: List[datetime] = []
        self.hour_counts: List[datetime] = []
        self.day_counts: List[datetime] = []

    async def initialize(self) -> bool:
        """Initialize provider connection."""
        return await self.provider.validate_connection()

    def create_personalized_message(
        self,
        lead: QualifiedLead,
        template_name: str,
        decision_maker: Optional[DecisionMaker] = None,
        custom_variables: Dict[str, str] = None,
        campaign_id: str = None,
        conversation_stage: ConversationStage = ConversationStage.INITIAL
    ) -> WhatsAppMessage:
        """Create personalized message for a lead."""

        # Build personalization context
        context = PersonalizationContext.from_lead(lead, decision_maker)

        # Get template
        template = self.template_manager.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Merge variables
        variables = context.to_dict()
        if custom_variables:
            variables.update(custom_variables)

        # Determine best phone
        phone = lead.whatsapp or lead.phone
        whatsapp = lead.whatsapp if lead.whatsapp_verified else None

        if not phone:
            raise ValueError(f"No phone number for lead {lead.id}")

        # Create message
        message = WhatsAppMessage(
            lead_id=lead.id,
            contact_phone=phone,
            contact_whatsapp=whatsapp or phone,
            template_name=template_name,
            template_language=template.language.value,
            variables=variables,
            conversation_stage=conversation_stage,
            campaign_id=campaign_id,
        )

        return message

    def create_custom_message(
        self,
        lead: QualifiedLead,
        text: str,
        decision_maker: Optional[DecisionMaker] = None,
        custom_variables: Dict[str, str] = None,
        campaign_id: str = None,
        conversation_stage: ConversationStage = ConversationStage.INITIAL
    ) -> WhatsAppMessage:
        """Create custom (non-template) message."""

        context = PersonalizationContext.from_lead(lead, decision_maker)
        variables = context.to_dict()
        if custom_variables:
            variables.update(custom_variables)

        phone = lead.whatsapp or lead.phone
        whatsapp = lead.whatsapp if lead.whatsapp_verified else None

        if not phone:
            raise ValueError(f"No phone number for lead {lead.id}")

        message = WhatsAppMessage(
            lead_id=lead.id,
            contact_phone=phone,
            contact_whatsapp=whatsapp or phone,
            custom_text=text,
            variables=variables,
            conversation_stage=conversation_stage,
            campaign_id=campaign_id,
        )

        return message

    def _check_rate_limits(self, campaign: Campaign) -> bool:
        """Check if we can send more messages within rate limits."""
        now = datetime.utcnow()

        # Clean old counts
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        self.minute_counts = [t for t in self.minute_counts if t > minute_ago]
        self.hour_counts = [t for t in self.hour_counts if t > hour_ago]
        self.day_counts = [t for t in self.day_counts if t > day_ago]

        # Check limits
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

    def _is_business_hours(self, campaign: Campaign) -> bool:
        """Check if current time is within business hours."""
        if not campaign.business_hours_only:
            return True

        # Would need timezone conversion - simplified
        now = datetime.utcnow()
        # Assuming UTC-3 for Brazil
        local_hour = (now.hour - 3) % 24

        return campaign.business_hours_start <= local_hour < campaign.business_hours_end

    def _check_opt_out(self, text: str, campaign: Campaign) -> bool:
        """Check if message contains opt-out keywords."""
        text_lower = text.lower()
        for keyword in campaign.opt_out_keywords:
            if keyword in text_lower:
                return True
        return False

    async def send_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send a single message with retry logic."""
        for attempt in range(message.max_retries + 1):
            try:
                result = await self.provider.send_message(message)

                if result.get("success"):
                    message.status = MessageStatus.SENT
                    message.external_id = result.get("external_id")
                    message.sent_at = datetime.utcnow()
                    message.retry_count = attempt
                    self._record_send()

                    # Update conversation state
                    self._update_conversation_state(message)

                    return result
                else:
                    raise Exception(result.get("error", "Unknown error"))

            except Exception as e:
                message.retry_count = attempt + 1
                message.error = str(e)
                logger.warning(f"Send attempt {attempt + 1} failed: {e}")

                if attempt < message.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    message.status = MessageStatus.FAILED
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": "Max retries exceeded"}

    def _update_conversation_state(self, message: WhatsAppMessage):
        """Update conversation tracking."""
        lead_id = message.lead_id
        if lead_id not in self.conversation_states:
            self.conversation_states[lead_id] = {
                'stage': ConversationStage.INITIAL,
                'messages_sent': 0,
                'last_sent_at': None,
                'replies': 0,
                'opt_out': False,
            }

        state = self.conversation_states[lead_id]
        state['messages_sent'] += 1
        state['last_sent_at'] = datetime.utcnow()
        state['stage'] = message.conversation_stage

    def get_conversation_state(self, lead_id: str) -> Dict:
        """Get conversation state for a lead."""
        return self.conversation_states.get(lead_id, {
            'stage': ConversationStage.INITIAL,
            'messages_sent': 0,
            'last_sent_at': None,
            'replies': 0,
            'opt_out': False,
        })

    async def process_incoming_message(self, webhook_data: Dict[str, Any]) -> Optional[Dict]:
        """Process incoming webhook message."""
        try:
            # Extract message info from webhook
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})

            messages = value.get('messages', [])
            if not messages:
                return None

            msg = messages[0]
            from_phone = msg.get('from', '')
            msg_id = msg.get('id', '')
            msg_type = msg.get('type', '')
            timestamp = msg.get('timestamp', '')

            # Find lead by phone
            # This would need a phone -> lead_id lookup
            lead_id = await self._find_lead_by_phone(from_phone)

            if not lead_id:
                logger.warning(f"Incoming message from unknown phone: {from_phone}")
                return None

            # Extract text content
            text = ""
            if msg_type == 'text':
                text = msg.get('text', {}).get('body', '')
            elif msg_type == 'interactive':
                interactive = msg.get('interactive', {})
                if interactive.get('type') == 'button_reply':
                    text = interactive.get('button_reply', {}).get('title', '')
                elif interactive.get('type') == 'list_reply':
                    text = interactive.get('list_reply', {}).get('title', '')

            # Check for opt-out
            state = self.get_conversation_state(lead_id)
            campaign = self._get_active_campaign_for_lead(lead_id)

            if campaign and self._check_opt_out(text, campaign):
                state['opt_out'] = True
                state['stage'] = ConversationStage.OPTED_OUT
                logger.info(f"Lead {lead_id} opted out")
                return {"action": "opt_out", "lead_id": lead_id}

            # Update state
            state['replies'] += 1
            state['stage'] = ConversationStage.REPLIED
            state['last_reply_at'] = datetime.utcnow()
            state['last_reply_text'] = text

            return {
                "lead_id": lead_id,
                "message": text,
                "timestamp": timestamp,
                "action": "reply_received"
            }

        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            return None

    async def _find_lead_by_phone(self, phone: str) -> Optional[str]:
        """Find lead ID by phone number."""
        # This would query the database
        # Simplified for now
        return None

    def _get_active_campaign_for_lead(self, lead_id: str) -> Optional[Campaign]:
        """Get active campaign for lead."""
        for campaign in self.campaigns.values():
            if campaign.active:
                return campaign
        return None

    def register_campaign(self, campaign: Campaign) -> str:
        """Register a campaign."""
        self.campaigns[campaign.id] = campaign
        return campaign.id

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID."""
        return self.campaigns.get(campaign_id)

    async def run_campaign(
        self,
        campaign: Campaign,
        leads: List[QualifiedLead],
        decision_makers_map: Dict[str, DecisionMaker] = None
    ) -> Dict[str, Any]:
        """Run a campaign against a list of leads."""
        campaign.started_at = datetime.utcnow()

        results = {
            "campaign_id": campaign.id,
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
                if state.get('opt_out'):
                    results['skipped'] += 1
                    continue

                # Check max messages per lead
                if state.get('messages_sent', 0) >= campaign.max_messages_per_lead:
                    results['skipped'] += 1
                    continue

                # Check business hours
                if not self._is_business_hours(campaign):
                    logger.info("Outside business hours, pausing campaign")
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

                # Determine which template to use
                template_name = self._select_template_for_stage(
                    campaign, state.get('stage', ConversationStage.INITIAL)
                )

                # Create and send message
                message = self.create_personalized_message(
                    lead=lead,
                    template_name=template_name,
                    decision_maker=dm,
                    campaign_id=campaign.id,
                    conversation_stage=state.get('stage', ConversationStage.INITIAL)
                )

                result = await self.send_message(message)

                if result.get("success"):
                    results['sent'] += 1
                    campaign.stats['messages_sent'] += 1
                else:
                    results['failed'] += 1
                    campaign.stats['errors'] += 1
                    results['errors'].append(f"Lead {lead.id}: {result.get('error')}")

                # Small delay between messages
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error processing lead {lead.id}: {e}")
                results['failed'] += 1
                results['errors'].append(f"Lead {lead.id}: {str(e)}")

        campaign.completed_at = datetime.utcnow()
        return results

    def _select_template_for_stage(
        self,
        campaign: Campaign,
        stage: ConversationStage
    ) -> str:
        """Select appropriate template for conversation stage."""
        if stage == ConversationStage.INITIAL:
            return campaign.initial_template
        elif stage == ConversationStage.FOLLOW_UP_1 and len(campaign.follow_up_templates) > 0:
            return campaign.follow_up_templates[0]
        elif stage == ConversationStage.FOLLOW_UP_2 and len(campaign.follow_up_templates) > 1:
            return campaign.follow_up_templates[1]
        elif stage == ConversationStage.FOLLOW_UP_3 and len(campaign.follow_up_templates) > 2:
            return campaign.follow_up_templates[2]
        elif stage == ConversationStage.REPLIED:
            return "value_proposition"  # Custom response would be better
        return campaign.initial_template


class CampaignBuilder:
    """Builder for creating campaigns with fluent interface."""

    def __init__(self, name: str):
        self.campaign = Campaign(name=name)

    def with_description(self, desc: str) -> 'CampaignBuilder':
        self.campaign.description = desc
        return self

    def targeting_classifications(self, *classifications: LeadClassification) -> 'CampaignBuilder':
        self.campaign.lead_classifications = list(classifications)
        return self

    def targeting_min_score(self, score: float) -> 'CampaignBuilder':
        self.campaign.min_score = score
        return self

    def targeting_segments(self, *segments: str) -> 'CampaignBuilder':
        self.campaign.segments = list(segments)
        return self

    def targeting_states(self, *states: str) -> 'CampaignBuilder':
        self.campaign.states = list(states)
        return self

    def with_templates(
        self,
        initial: str,
        follow_ups: List[str] = None,
        intervals_hours: List[int] = None
    ) -> 'CampaignBuilder':
        self.campaign.initial_template = initial
        if follow_ups:
            self.campaign.follow_up_templates = follow_ups
        if intervals_hours:
            self.campaign.follow_up_intervals_hours = intervals_hours
        return self

    def with_schedule(
        self,
        business_hours_only: bool = True,
        start_hour: int = 8,
        end_hour: int = 18,
        timezone: str = "America/Sao_Paulo",
        rate_per_minute: int = 20,
        rate_per_hour: int = 500,
        rate_per_day: int = 2000
    ) -> 'CampaignBuilder':
        self.campaign.business_hours_only = business_hours_only
        self.campaign.business_hours_start = start_hour
        self.campaign.business_hours_end = end_hour
        self.campaign.timezone = timezone
        self.campaign.rate_limit_per_minute = rate_per_minute
        self.campaign.rate_limit_per_hour = rate_per_hour
        self.campaign.rate_limit_per_day = rate_per_day
        return self

    def with_opt_out_keywords(self, *keywords: str) -> 'CampaignBuilder':
        self.campaign.opt_out_keywords.extend(keywords)
        return self

    def max_messages_per_lead(self, max_msgs: int) -> 'CampaignBuilder':
        self.campaign.max_messages_per_lead = max_msgs
        return self

    def build(self) -> Campaign:
        return self.campaign


async def create_messaging_engine(
    provider_type: WhatsAppProvider = WhatsAppProvider.CLOUD_API
) -> IntelligentMessagingEngine:
    """Factory to create messaging engine with provider."""
    provider = None

    if provider_type == WhatsAppProvider.CLOUD_API:
        provider = CloudAPIProvider()
    elif provider_type == WhatsAppProvider.WEB_AUTOMATION:
        provider = WebAutomationProvider()

    engine = IntelligentMessagingEngine(provider)
    await engine.initialize()
    return engine


# Example usage and testing
async def example_usage():
    """Example of how to use the messaging engine."""

    # Create engine
    engine = await create_messaging_engine(WhatsAppProvider.CLOUD_API)

    # Create campaign
    campaign = (CampaignBuilder("Q1_2024_Prospecção_Distribuidoras")
        .with_description("Prospecção de distribuidoras no Sudeste")
        .targeting_classifications(LeadClassification.A, LeadClassification.B)
        .targeting_min_score(75)
        .targeting_segments("distribuidoras", "atacadistas")
        .targeting_states("SP", "RJ", "MG", "ES")
        .with_templates(
            initial="initial_contact",
            follow_ups=["follow_up_1", "value_proposition", "case_study"],
            intervals_hours=[24, 72, 168]
        )
        .with_schedule(
            business_hours_only=True,
            start_hour=8,
            end_hour=18,
            rate_per_minute=20,
            rate_per_hour=500,
            rate_per_day=2000
        )
        .max_messages_per_lead(3)
        .build())

    engine.register_campaign(campaign)

    # Would get leads from database
    # leads = db.get_leads_for_campaign(campaign)
    # decision_makers = {lead.id: lead.decision_makers[0] for lead in leads if lead.decision_makers}

    # Run campaign
    # results = await engine.run_campaign(campaign, leads, decision_makers)
    # print(f"Campaign results: {results}")


if __name__ == "__main__":
    asyncio.run(example_usage())