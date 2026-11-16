"""
Email package for lead generation automation.

Exports:
- prepare: Email contact preparation and scheduling
- templates: Email template management (HTML + Text)
- client: Email sending engine (SMTP, SendGrid, etc.)
"""

from .prepare import EmailPreparator
from .templates import EmailTemplateManager, EmailTemplate, EmailType
from .client import (
    EmailProvider,
    EmailStatus,
    EmailCampaign,
    EmailMessage,
    SMTPEmailProvider,
    SendGridEmailProvider,
    IntelligentEmailEngine,
    EmailCampaignBuilder,
    create_email_engine,
)

__all__ = [
    # prepare.py
    "EmailPreparator",
    # templates.py
    "EmailTemplateManager",
    "EmailTemplate",
    "EmailType",
    # client.py
    "EmailProvider",
    "EmailStatus",
    "EmailCampaign",
    "EmailMessage",
    "SMTPEmailProvider",
    "SendGridEmailProvider",
    "IntelligentEmailEngine",
    "EmailCampaignBuilder",
    "create_email_engine",
]