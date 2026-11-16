"""WhatsApp message templates management."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from utils.config_loader import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)


class TemplateCategory(str, Enum):
    """WhatsApp template categories."""
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"
    AUTHENTICATION = "AUTHENTICATION"


class TemplateLanguage(str, Enum):
    """Supported template languages."""
    PT_BR = "pt_BR"
    EN_US = "en_US"
    ES_ES = "es_ES"


@dataclass
class TemplateComponent:
    """WhatsApp template component."""
    type: str  # HEADER, BODY, FOOTER, BUTTONS
    text: Optional[str] = None
    format: Optional[str] = None  # TEXT, IMAGE, VIDEO, DOCUMENT
    example: Optional[Dict] = None
    buttons: Optional[List[Dict]] = None


@dataclass
class WhatsAppTemplate:
    """WhatsApp Business API template."""
    name: str
    language: TemplateLanguage
    category: TemplateCategory
    components: List[TemplateComponent] = field(default_factory=list)
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    rejection_reason: Optional[str] = None

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to WhatsApp Business API format."""
        return {
            'name': self.name,
            'language': self.language.value,
            'category': self.category.value,
            'components': [
                {
                    'type': c.type,
                    **({'text': c.text} if c.text else {}),
                    **({'format': c.format} if c.format else {}),
                    **({'example': c.example} if c.example else {}),
                    **({'buttons': c.buttons} if c.buttons else {}),
                }
                for c in self.components
            ],
        }

    @classmethod
    def from_api_format(cls, data: Dict[str, Any]) -> 'WhatsAppTemplate':
        """Create from WhatsApp Business API format."""
        components = []
        for c in data.get('components', []):
            components.append(TemplateComponent(
                type=c.get('type', ''),
                text=c.get('text'),
                format=c.get('format'),
                example=c.get('example'),
                buttons=c.get('buttons'),
            ))

        return cls(
            name=data.get('name', ''),
            language=TemplateLanguage(data.get('language', 'pt_BR')),
            category=TemplateCategory(data.get('category', 'MARKETING')),
            components=components,
            status=data.get('status', 'PENDING'),
            id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            rejection_reason=data.get('rejection_reason'),
        )


class TemplateManager:
    """Manages WhatsApp message templates."""

    def __init__(self):
        self.settings = get_settings()
        self.templates: Dict[str, WhatsAppTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default templates from config."""
        whatsapp_config = self.settings.__dict__.get('whatsapp_templates', {})

        # Default templates for Averta
        default_templates = [
            WhatsAppTemplate(
                name="initial_contact",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.MARKETING,
                components=[
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Olá {{1}}, sou da Averta. Vi que a {{2}} atua com {{3}} em {{4}}. "
                            "Gostaria de apresentar nossa solução de gestão de fretes que reduz "
                            "custos em até 30%. Podemos conversar?"
                        ),
                        example={
                            "body_text": [
                                ["João", "Empresa ABC", "distribuição de alimentos", "São Paulo"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Gestão Inteligente de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Sim, vamos conversar"},
                            {"type": "QUICK_REPLY", "text": "Não tenho interesse"},
                        ]
                    )
                ]
            ),
            WhatsAppTemplate(
                name="follow_up",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.MARKETING,
                components=[
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Oi {{1}}, passando para saber se teve chance de avaliar nossa "
                            "proposta. A {{2}} pode economizar significativamente nos fretes. "
                            "Vamos agendar?"
                        ),
                        example={
                            "body_text": [
                                ["João", "Empresa ABC"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Gestão Inteligente de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Sim, agendar"},
                            {"type": "QUICK_REPLY", "text": "Depois"},
                            {"type": "QUICK_REPLY", "text": "Não obrigado"},
                        ]
                    )
                ]
            ),
            WhatsAppTemplate(
                name="value_proposition",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.MARKETING,
                components=[
                    TemplateComponent(
                        type="HEADER",
                        format="TEXT",
                        text="🚚 Reduza até 30% no custo logístico"
                    ),
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Olá {{1}}, a Averta ajuda empresas como a {{2}} a otimizar a "
                            "logística: cotação, contratação, tracking e auditoria de fretes "
                            "em uma plataforma. Temos cases no segmento de {{3}} com redução "
                            "de 25% no custo logístico. Quer ver os números?"
                        ),
                        example={
                            "body_text": [
                                ["João", "Empresa ABC", "distribuição de alimentos"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Gestão Inteligente de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Ver cases"},
                            {"type": "QUICK_REPLY", "text": "Agendar demo"},
                            {"type": "QUICK_REPLY", "text": "Não agora"},
                        ]
                    )
                ]
            ),
            WhatsAppTemplate(
                name="case_study",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.MARKETING,
                components=[
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Oi {{1}}, seguindo nosso papo sobre logística. Tenho um case "
                            "similar à {{2}} que reduziu 30% no custo de frete com nossa "
                            "plataforma. Quer ver os detalhes?"
                        ),
                        example={
                            "body_text": [
                                ["João", "Empresa ABC"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Gestão Inteligente de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Sim, mostrar case"},
                            {"type": "QUICK_REPLY", "text": "Enviar por e-mail"},
                            {"type": "QUICK_REPLY", "text": "Não precisa"},
                        ]
                    )
                ]
            ),
            WhatsAppTemplate(
                name="demo_invite",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.MARKETING,
                components=[
                    TemplateComponent(
                        type="HEADER",
                        format="TEXT",
                        text="🎯 Demo: Gestão de Fretes em 15 min"
                    ),
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Olá {{1}}, gostaria de convidar você para uma demo rápida "
                            "(15 min) da nossa plataforma de gestão de fretes. A {{2}} veria "
                            "na prática como reduzir custos e ganhar visibilidade total das "
                            "cargas. Qual melhor horário?"
                        ),
                        example={
                            "body_text": [
                                ["João", "Empresa ABC"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Gestão Inteligente de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Manhã"},
                            {"type": "QUICK_REPLY", "text": "Tarde"},
                            {"type": "QUICK_REPLY", "text": "Melhor por e-mail"},
                        ]
                    )
                ]
            ),
            WhatsAppTemplate(
                name="re_engagement",
                language=TemplateLanguage.PT_BR,
                category=TemplateCategory.UTILITY,
                components=[
                    TemplateComponent(
                        type="BODY",
                        text=(
                            "Oi {{1}}, faz um tempo que não conversamos. A Averta lançou "
                            "novas funcionalidades: roteirização automática, auditoria de "
                            "fretes em lote e integração nativa com {{2}}. Vale a pena "
                            "conversar de novo?"
                        ),
                        example={
                            "body_text": [
                                ["João", "seu ERP"]
                            ]
                        }
                    ),
                    TemplateComponent(
                        type="FOOTER",
                        text="Averta - Novidades em Gestão de Fretes"
                    ),
                    TemplateComponent(
                        type="BUTTONS",
                        buttons=[
                            {"type": "QUICK_REPLY", "text": "Me mostre as novidades"},
                            {"type": "QUICK_REPLY", "text": "Agendar call"},
                            {"type": "QUICK_REPLY", "text": "Não, obrigado"},
                        ]
                    )
                ]
            ),
        ]

        for tmpl in default_templates:
            self.templates[tmpl.name] = tmpl

    def get_template(self, name: str) -> Optional[WhatsAppTemplate]:
        """Get template by name."""
        return self.templates.get(name)

    def get_all_templates(self) -> List[WhatsAppTemplate]:
        """Get all templates."""
        return list(self.templates.values())

    def get_approved_templates(self) -> List[WhatsAppTemplate]:
        """Get only approved templates."""
        return [t for t in self.templates.values() if t.status == "APPROVED"]

    def add_template(self, template: WhatsAppTemplate) -> bool:
        """Add or update template."""
        self.templates[template.name] = template
        return True

    def remove_template(self, name: str) -> bool:
        """Remove template."""
        if name in self.templates:
            del self.templates[name]
            return True
        return False

    def export_templates(self, filepath: str) -> bool:
        """Export templates to JSON file."""
        try:
            data = {
                name: {
                    'name': tmpl.name,
                    'language': tmpl.language.value,
                    'category': tmpl.category.value,
                    'components': [
                        {
                            'type': c.type,
                            'text': c.text,
                            'format': c.format,
                            'example': c.example,
                            'buttons': c.buttons,
                        }
                        for c in tmpl.components
                    ],
                    'status': tmpl.status,
                    'id': tmpl.id,
                    'created_at': tmpl.created_at,
                    'updated_at': tmpl.updated_at,
                    'rejection_reason': tmpl.rejection_reason,
                }
                for name, tmpl in self.templates.items()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Exported {len(data)} templates to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting templates: {e}")
            return False

    def import_templates(self, filepath: str) -> int:
        """Import templates from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            count = 0
            for name, tmpl_data in data.items():
                tmpl = WhatsAppTemplate(
                    name=tmpl_data['name'],
                    language=TemplateLanguage(tmpl_data['language']),
                    category=TemplateCategory(tmpl_data['category']),
                    components=[
                        TemplateComponent(
                            type=c['type'],
                            text=c.get('text'),
                            format=c.get('format'),
                            example=c.get('example'),
                            buttons=c.get('buttons'),
                        )
                        for c in tmpl_data['components']
                    ],
                    status=tmpl_data.get('status', 'PENDING'),
                    id=tmpl_data.get('id'),
                    created_at=tmpl_data.get('created_at'),
                    updated_at=tmpl_data.get('updated_at'),
                    rejection_reason=tmpl_data.get('rejection_reason'),
                )
                self.templates[name] = tmpl
                count += 1

            logger.info(f"Imported {count} templates from {filepath}")
            return count
        except Exception as e:
            logger.error(f"Error importing templates: {e}")
            return 0

    def validate_template(self, template: WhatsAppTemplate) -> List[str]:
        """Validate template against WhatsApp Business API rules."""
        errors = []

        # Name validation
        if not template.name:
            errors.append("Template name is required")
        elif not template.name.islower() or ' ' in template.name:
            errors.append("Template name must be lowercase with underscores only")

        # Component validation
        has_body = False
        for comp in template.components:
            if comp.type == "BODY":
                has_body = True
                if comp.text and len(comp.text) > 1024:
                    errors.append("BODY text exceeds 1024 characters")
                # Check variable format {{1}}, {{2}}, etc.
                import re
                variables = re.findall(r'\{\{(\d+)\}\}', comp.text or '')
                if variables:
                    var_nums = [int(v) for v in variables]
                    if max(var_nums) > 10:
                        errors.append("Maximum 10 variables allowed ({{1}} to {{10}})")

            elif comp.type == "HEADER":
                if comp.format == "TEXT" and comp.text and len(comp.text) > 60:
                    errors.append("HEADER text exceeds 60 characters")

            elif comp.type == "FOOTER":
                if comp.text and len(comp.text) > 60:
                    errors.append("FOOTER text exceeds 60 characters")

            elif comp.type == "BUTTONS":
                if comp.buttons and len(comp.buttons) > 3:
                    errors.append("Maximum 3 buttons allowed")
                for btn in comp.buttons or []:
                    if btn.get('text', '') and len(btn['text']) > 20:
                        errors.append("Button text exceeds 20 characters")

        if not has_body:
            errors.append("At least one BODY component is required")

        return errors


def create_template_manager() -> TemplateManager:
    """Create template manager instance."""
    return TemplateManager()