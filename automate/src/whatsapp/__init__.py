"""
WhatsApp package for lead generation automation.

Exports:
- prepare: WhatsApp contact preparation and scheduling
- templates: Template management for WhatsApp Business API
- client: WhatsApp messaging engine (Cloud API, Web Automation, Campaigns)
"""

from .prepare import WhatsAppPreparator
from .templates import TemplateManager, WhatsAppTemplate, TemplateLanguage, TemplateCategory
from .client import (
    WhatsAppProvider,
    MessageStatus,
    ConversationStage,
    PersonalizationContext,
    WhatsAppMessage,
    Campaign,
    CloudAPIProvider,
    WebAutomationProvider,
    IntelligentMessagingEngine,
    CampaignBuilder,
    create_messaging_engine,
)

__all__ = [
    # prepare.py
    "WhatsAppPreparator",
    # templates.py
    "TemplateManager",
    "WhatsAppTemplate",
    "TemplateLanguage",
    "TemplateCategory",
    # client.py
    "WhatsAppProvider",
    "MessageStatus",
    "ConversationStage",
    "PersonalizationContext",
    "WhatsAppMessage",
    "Campaign",
    "CloudAPIProvider",
    "WebAutomationProvider",
    "IntelligentMessagingEngine",
    "CampaignBuilder",
    "create_messaging_engine",
]