"""
Email template management for Averta outreach campaigns.

Templates are designed to be:
- Professional and personalized
- Explain Averta's value proposition clearly
- Include social proof (cases, numbers)
- Clear call-to-action
- Compliant with LGPD (opt-out link)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class EmailType(str, Enum):
    """Types of email campaigns."""
    INITIAL_OUTREACH = "initial_outreach"      # Primeiro contato
    FOLLOW_UP_1 = "follow_up_1"                # Follow-up 1 (3 dias)
    FOLLOW_UP_2 = "follow_up_2"                # Follow-up 2 (7 dias)
    VALUE_PROPOSITION = "value_proposition"    # Proposta de valor detalhada
    CASE_STUDY = "case_study"                  # Case de sucesso
    MEETING_REQUEST = "meeting_request"        # Solicitação de reunião
    BREAKUP = "breakup"                        # Último email (opt-out respeitoso)
    NEWSLETTER = "newsletter"                  # Conteúdo educativo


@dataclass
class EmailTemplate:
    """Email template with HTML and text versions."""
    name: str
    email_type: EmailType
    subject: str
    subject_variables: List[str] = field(default_factory=list)
    html_template: str = ""
    text_template: str = ""
    preview_text: str = ""  # Pre-header text

    # Tracking
    track_opens: bool = True
    track_clicks: bool = True

    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def render_subject(self, variables: Dict[str, str]) -> str:
        """Render subject with variables."""
        subject = self.subject
        for key, value in variables.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
            subject = subject.replace(f"{{{key}}}", str(value))
        return subject

    def render_html(self, variables: Dict[str, str]) -> str:
        """Render HTML template with variables."""
        html = self.html_template
        for key, value in variables.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))
            html = html.replace(f"{{{key}}}", str(value))
        return html

    def render_text(self, variables: Dict[str, str]) -> str:
        """Render text template with variables."""
        text = self.text_template
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email_type": self.email_type.value,
            "subject": self.subject,
            "subject_variables": self.subject_variables,
            "html_template": self.html_template,
            "text_template": self.text_template,
            "preview_text": self.preview_text,
            "track_opens": self.track_opens,
            "track_clicks": self.track_clicks,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailTemplate':
        return cls(
            name=data["name"],
            email_type=EmailType(data["email_type"]),
            subject=data["subject"],
            subject_variables=data.get("subject_variables", []),
            html_template=data.get("html_template", ""),
            text_template=data.get("text_template", ""),
            preview_text=data.get("preview_text", ""),
            track_opens=data.get("track_opens", True),
            track_clicks=data.get("track_clicks", True),
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


class EmailTemplateManager:
    """Manages email templates for outreach campaigns."""

    def __init__(self, templates_dir: str = "config/email_templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, EmailTemplate] = {}
        self._load_builtin_templates()
        self._load_custom_templates()

    def _load_builtin_templates(self):
        """Load built-in Averta templates."""

        # ============================================================
        # TEMPLATE 1: INITIAL OUTREACH - Primeiro Contato
        # ============================================================
        self.templates["initial_outreach"] = EmailTemplate(
            name="initial_outreach",
            email_type=EmailType.INITIAL_OUTREACH,
            subject="Olá {{contact_name}}, oportunidade de recuperação financeira para {{company_name}}",
            subject_variables=["contact_name", "company_name"],
            preview_text="Averta audita CT-es/NF-es e identifica cobranças indevidas - valores que podem ser recuperados...",
            description="Primeiro contato frio - oportunidade de recuperação financeira via auditoria CT-e/NF-e",
            tags=["outbound", "cold_email", "initial", "auditoria_fretes"],
            html_template=self._get_initial_outreach_html(),
            text_template=self._get_initial_outreach_text(),
        )

        # ============================================================
        # TEMPLATE 2: FOLLOW-UP 1 - 3 dias após
        # ============================================================
        self.templates["follow_up_1"] = EmailTemplate(
            name="follow_up_1",
            email_type=EmailType.FOLLOW_UP_1,
            subject="Re: {{contact_name}} - divergências em faturas de frete {{company_name}}",
            subject_variables=["contact_name", "company_name"],
            preview_text="Case similar: {{competitor_reference}} recuperou valores com auditoria automatizada...",
            description="Follow-up 1 - reforça oportunidade de auditoria, menciona case semelhante",
            tags=["outbound", "follow_up", "nurture", "auditoria_fretes"],
            html_template=self._get_follow_up_1_html(),
            text_template=self._get_follow_up_1_text(),
        )

        # ============================================================
        # TEMPLATE 3: FOLLOW-UP 2 - 7 dias após
        # ============================================================
        self.templates["follow_up_2"] = EmailTemplate(
            name="follow_up_2",
            email_type=EmailType.FOLLOW_UP_2,
            subject="Case {{segment}}: {{competitor_reference}} recuperou {{value_prop_1}} com auditoria",
            subject_variables=["segment", "competitor_reference", "value_prop_1"],
            preview_text="Case completo: implementação 30 dias, ROI 1º mês, auditoria CT-e/NF-e automatizada...",
            description="Follow-up 2 - case study detalhado com métricas de recuperação financeira",
            tags=["outbound", "follow_up", "case_study", "auditoria_fretes"],
            html_template=self._get_follow_up_2_html(),
            text_template=self._get_follow_up_2_text(),
        )

        # ============================================================
        # TEMPLATE 4: VALUE PROPOSITION - Proposta detalhada
        # ============================================================
        self.templates["value_proposition"] = EmailTemplate(
            name="value_proposition",
            email_type=EmailType.VALUE_PROPOSITION,
            subject="{{contact_name}}, 5 benefícios da auditoria automatizada de fretes para {{segment}}",
            subject_variables=["contact_name", "segment"],
            preview_text="Identifica cobranças > contratado, divergências fiscais, auditoria CT-e/NF-e, contestações organizadas, valores recuperados...",
            description="Proposta de valor completa - 5 benefícios da auditoria inteligente de fretes",
            tags=["outbound", "value_prop", "education", "auditoria_fretes"],
            html_template=self._get_value_proposition_html(),
            text_template=self._get_value_proposition_text(),
        )

        # ============================================================
        # TEMPLATE 5: CASE STUDY - Case de sucesso
        # ============================================================
        self.templates["case_study"] = EmailTemplate(
            name="case_study",
            email_type=EmailType.CASE_STUDY,
            subject="Case {{segment}}: {{case_study}} - recuperação financeira comprovada",
            subject_variables=["segment", "case_study"],
            preview_text="Resultados reais: implementação 30 dias, ROI 1º mês, auditoria 100% automatizada CT-e/NF-e...",
            description="Case study detalhado com métricas de recuperação de valores pagos a mais",
            tags=["outbound", "case_study", "social_proof", "auditoria_fretes"],
            html_template=self._get_case_study_html(),
            text_template=self._get_case_study_text(),
        )

        # ============================================================
        # TEMPLATE 6: MEETING REQUEST - Solicitação reunião
        # ============================================================
        self.templates["meeting_request"] = EmailTemplate(
            name="meeting_request",
            email_type=EmailType.MEETING_REQUEST,
            subject="{{contact_name}}, 15 min: como a {{company_name}} recupera valores em fretes?",
            subject_variables=["contact_name", "company_name"],
            preview_text="Demo técnica: auditoria CT-e/NF-e, detecção de cobranças indevidas, recuperação financeira...",
            description="Call-to-action direto para agendar demonstração de 15 min",
            tags=["outbound", "meeting", "cta", "auditoria_fretes"],
            html_template=self._get_meeting_request_html(),
            text_template=self._get_meeting_request_text(),
        )

        # ============================================================
        # TEMPLATE 7: BREAKUP - Último email (respeitoso)
        # ============================================================
        self.templates["breakup"] = EmailTemplate(
            name="breakup",
            email_type=EmailType.BREAKUP,
            subject="Fechando contato - {{company_name}} (auditoria de fretes)",
            subject_variables=["company_name"],
            preview_text="Respeito sua decisão. Se no futuro precisar auditar faturas de frete, a Averta estará aqui...",
            description="Breakup email - opt-out respeitoso LGPD, mantém porta aberta para auditoria futura",
            tags=["outbound", "breakup", "opt_out", "auditoria_fretes"],
            html_template=self._get_breakup_html(),
            text_template=self._get_breakup_text(),
        )

    def _load_custom_templates(self):
        """Load custom templates from JSON files."""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                template = EmailTemplate.from_dict(data)
                self.templates[template.name] = template
            except Exception as e:
                print(f"Erro ao carregar template {template_file}: {e}")

    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get template by name."""
        return self.templates.get(name)

    def get_templates_by_type(self, email_type: EmailType) -> List[EmailTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.email_type == email_type]

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates with metadata."""
        return [
            {
                "name": t.name,
                "type": t.email_type.value,
                "subject": t.subject,
                "description": t.description,
                "tags": t.tags,
            }
            for t in self.templates.values()
        ]

    def save_template(self, template: EmailTemplate):
        """Save template to file."""
        file_path = self.templates_dir / f"{template.name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
        self.templates[template.name] = template

    # ============================================================
    # HTML TEMPLATES
    # ============================================================

    def _get_initial_outreach_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">Olá, {{contact_name}}, tudo bem?</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Estava pesquisando empresas do segmento de <strong>{{segment}}</strong> em <strong>{{city}}</strong> e encontrei a <strong>{{company_name}}</strong>.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Pelo perfil da operação de vocês, acredito que exista uma oportunidade interessante de recuperação financeira que merece ser investigada.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">A <strong>Averta</strong> utiliza inteligência automatizada para auditar <strong>CT-es e NF-es</strong>, identificar cobranças indevidas, divergências de valores e possíveis pagamentos realizados acima do contratado.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0; font-weight: 600;">Na prática, podemos ajudar a encontrar valores que já saíram do caixa da <strong>{{company_name}}</strong> e que podem ser recuperados.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0; color: #334155;">{{personalizacao_especifica_da_empresa}}</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Dependendo do volume da operação, estamos falando de oportunidades que podem representar milhares ou até milhões de reais.</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Gostaria de apresentar como funciona nossa análise e avaliar o potencial de recuperação financeira da <strong>{{company_name}}</strong>.</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Podemos conversar por 15 minutos?</p>

        <!-- CTA -->
        <div style="text-align: center; margin: 32px 0;">
            <a href="{{meeting_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3);">
                📅 Conversar por 15 minutos?
            </a>
        </div>

        <p style="font-size: 14px; color: #64748b; text-align: center; margin: 0;">Ou se preferir, responda este email que retornamos no melhor horário.</p>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_initial_outreach_text(self) -> str:
        return """
Olá, {{contact_name}}, tudo bem?

Estava pesquisando empresas do segmento de {{segment}} em {{city}} e encontrei a {{company_name}}.

Pelo perfil da operação de vocês, acredito que exista uma oportunidade interessante de recuperação financeira que merece ser investigada.

A Averta utiliza inteligência automatizada para auditar CT-es e NF-es, identificar cobranças indevidas, divergências de valores e possíveis pagamentos realizados acima do contratado.

Na prática, podemos ajudar a encontrar valores que já saíram do caixa da {{company_name}} e que podem ser recuperados.

{{personalizacao_especifica_da_empresa}}

Dependendo do volume da operação, estamos falando de oportunidades que podem representar milhares ou até milhões de reais.

Gostaria de apresentar como funciona nossa análise e avaliar o potencial de recuperação financeira da {{company_name}}.

Podemos conversar por 15 minutos?

📅 Conversar por 15 minutos? {{meeting_link}}

Ou se preferir, responda este email que retornamos no melhor horário.

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_follow_up_1_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">Oi {{contact_name}},</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Passando para dar seguimento ao meu email anterior. Entendo que o dia a dia é corrido e emails podem se perder.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Queria reforçar que a Averta já ajudou <strong>{{competitor_reference}}</strong> a <strong>{{value_prop_2}}</strong>. Foi implementado em 30 dias e o ROI apareceu no primeiro mês.</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Se agora não for o momento, sem problemas! Me avisa quando fizer sentido conversarmos, ou posso te mandar o material por email para você avaliar com calma.</p>

        <!-- CTA -->
        <div style="text-align: center; margin: 32px 0;">
            <a href="{{meeting_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3); margin-right: 12px;">
                📅 Agendar para depois
            </a>
            <a href="{{material_link}}" style="background: #fff; color: #0066cc; border: 2px solid #0066cc; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                📄 Enviar material
            </a>
        </div>

        <p style="font-size: 14px; color: #64748b; text-align: center; margin: 0;">Qualquer coisa, é só responder.</p>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_follow_up_1_text(self) -> str:
        return """
Oi {{contact_name}},

Passando para dar seguimento ao meu email anterior. Entendo que o dia a dia é corrido e emails podem se perder.

Queria reforçar que a Averta já ajudou {{competitor_reference}} a {{value_prop_2}}. Foi implementado em 30 dias e o ROI apareceu no primeiro mês.

Se agora não for o momento, sem problemas! Me avisa quando fizer sentido conversarmos, ou posso te mandar o material por email para você avaliar com calma.

📅 Agendar para depois: {{meeting_link}}
📄 Enviar material: {{material_link}}

Qualquer coisa, é só responder.

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_follow_up_2_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">{{contact_name}},</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Compartilhando um case rápido que faz total sentido para {{segment}}:</p>

        <div style="background: #f0f9ff; border-left: 4px solid #0066cc; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; font-style: italic; color: #1e3a5f;">{{case_study}}</p>
        </div>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Foi implementado em <strong>30 dias</strong> e o <strong>ROI apareceu no primeiro mês</strong>.</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Se quiser, te envio o case completo (PDF) por aqui mesmo ou marcamos 15 min para eu explicar os detalhes e como aplicar na {{company_name}}.</p>

        <!-- CTA -->
        <div style="text-align: center; margin: 32px 0;">
            <a href="{{case_study_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3); margin-right: 12px;">
                📄 Receber case completo
            </a>
            <a href="{{meeting_link}}" style="background: #fff; color: #0066cc; border: 2px solid #0066cc; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                📅 Marcar 15 min
            </a>
        </div>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_follow_up_2_text(self) -> str:
        return """
{{contact_name}},

Compartilhando um case rápido que faz total sentido para {{segment}}:

"{{case_study}}"

Foi implementado em 30 dias e o ROI apareceu no primeiro mês.

Se quiser, te envio o case completo (PDF) ou marcamos 15 min para eu explicar os detalhes e como aplicar na {{company_name}}.

📄 Case completo: {{case_study_link}}
📅 Marcar 15 min: {{meeting_link}}

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_value_proposition_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">{{contact_name}},</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Resumindo o que a <strong>Averta</strong> entrega para empresas de <strong>{{segment}}</strong> como a <strong>{{company_name}}</strong>:</p>

        <!-- Value Props focused on Audit -->
        <p style="font-size: 16px; margin: 0 0 12px 0; font-weight: 600;">Na prática, ajudamos sua empresa a:</p>
        <ul style="margin: 0 0 24px 0; padding-left: 20px; font-size: 16px;">
            <li style="margin: 8px 0;">Identificar cobranças de frete acima dos valores contratados;</li>
            <li style="margin: 8px 0;">Detectar divergências fiscais e tributárias;</li>
            <li style="margin: 8px 0;">Auditar documentos automaticamente (CT-e/NF-e);</li>
            <li style="margin: 8px 0;">Organizar contestações e evidências;</li>
            <li style="margin: 8px 0;">Acompanhar valores questionados e efetivamente recuperados.</li>
        </ul>

        <p style="font-size: 16px; margin: 0 0 24px 0; color: #334155; font-style: italic;">A proposta é simples: transformar a auditoria de fretes em um processo inteligente, rastreável e orientado à recuperação financeira.</p>

        <!-- Features Detail -->
        <div style="background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #e2e8f0;">
            <p style="margin: 0 0 15px 0; font-weight: 600; color: #0066cc;">Funcionalidades de Auditoria Inteligente:</p>
            <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 0; color: #64748b;">✅ Análise automática de CT-e e NF-e</td>
                    <td style="padding: 8px 0; color: #64748b;">✅ Detecção de divergências de valor</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 0; color: #64748b;">✅ Validação tributária (ICMS, ST, etc.)</td>
                    <td style="padding: 8px 0; color: #64748b;">✅ Gestão de contestações e evidências</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 0; color: #64748b;">✅ Dashboard de valores recuperados</td>
                    <td style="padding: 8px 0; color: #64748b;">✅ Integração ERP/TMS (API/SFTP)</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">✅ Alertas de cobranças indevidas</td>
                    <td style="padding: 8px 0; color: #64748b;">✅ Relatórios gerenciais automáticos</td>
                </tr>
            </table>
        </div>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Quer ver uma demo rápida (15 min) e entender como isso se aplica na <strong>{{company_name}}</strong>?</p>

        <!-- CTA -->
        <div style="text-align: center; margin: 32px 0;">
            <a href="{{meeting_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3);">
                📅 Ver demo de 15 min
            </a>
        </div>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_value_proposition_text(self) -> str:
        return """
{{contact_name}},

Resumindo o que a Averta entrega para empresas de {{segment}} como a {{company_name}}:

Na prática, ajudamos sua empresa a:
• Identificar cobranças de frete acima dos valores contratados
• Detectar divergências fiscais e tributárias
• Auditar documentos automaticamente (CT-e/NF-e)
• Organizar contestações e evidências
• Acompanhar valores questionados e efetivamente recuperados

A proposta é simples: transformar a auditoria de fretes em um processo inteligente, rastreável e orientado à recuperação financeira.

Funcionalidades de Auditoria Inteligente:
✅ Análise automática de CT-e e NF-e
✅ Detecção de divergências de valor
✅ Validação tributária (ICMS, ST, etc.)
✅ Gestão de contestações e evidências
✅ Dashboard de valores recuperados
✅ Integração ERP/TMS (API/SFTP)
✅ Alertas de cobranças indevidas
✅ Relatórios gerenciais automáticos

Quer ver uma demo rápida (15 min)?
📅 {{meeting_link}}

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_case_study_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">{{contact_name}},</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Como prometido, o case completo de auditoria de fretes:</p>

        <div style="background: #fff; border: 1px solid #eaeaea; border-radius: 8px; padding: 25px; margin: 20px 0;">
            <h3 style="margin: 0 0 15px 0; color: #0066cc;">{{case_study}}</h3>

            <p style="margin: 10px 0;"><strong>Segmento:</strong> {{segment}}</p>
            <p style="margin: 10px 0;"><strong>Desafio:</strong> Cobranças indevidas em fretes, divergências fiscais, auditoria manual e sem controle</p>

            <p style="margin: 15px 0 10px 0;"><strong>Resultados em 90 dias:</strong></p>
            <ul style="margin: 0; padding-left: 20px;">
                <li style="margin: 8px 0;">✅ Recuperação de {{value_prop_1}}</li>
                <li style="margin: 8px 0;">✅ Implementação em 30 dias</li>
                <li style="margin: 8px 0;">✅ ROI no primeiro mês</li>
                <li style="margin: 8px 0;">✅ Auditoria 100% automatizada (CT-e/NF-e)</li>
            </ul>
        </div>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Quer agendar para ver como aplicar na <strong>{{company_name}}</strong>?</p>

        <!-- CTA -->
        <div style="text-align: center; margin: 32px 0;">
            <a href="{{meeting_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3);">
                📅 Ver como aplicar
            </a>
        </div>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_case_study_text(self) -> str:
        return """
{{contact_name}},

Como prometido, o case completo de auditoria de fretes:

{{case_study}}
Segmento: {{segment}}

Desafio: Cobranças indevidas em fretes, divergências fiscais, auditoria manual e sem controle

Resultados em 90 dias:
✅ Recuperação de {{value_prop_1}}
✅ Implementação em 30 dias
✅ ROI no primeiro mês
✅ Auditoria 100% automatizada (CT-e/NF-e)

Quer agendar para ver como aplicar na {{company_name}}?
📅 {{meeting_link}}

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_meeting_request_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px; text-align: center;">
        <p style="font-size: 18px; font-weight: 600; margin: 0 0 20px 0;">{{contact_name}},</p>

        <p style="font-size: 16px; max-width: 400px; margin: 0 auto 25px;">15 minutos para eu mostrar exatamente como a <strong>{{company_name}}</strong> pode recuperar valores pagos a mais em fretes.</p>

        <p style="font-size: 14px; color: #64748b; margin: 0 0 30px 0;">Sem compromisso, sem venda agressiva. Só uma demonstração técnica de como auditamos CT-e/NF-e para {{segment}}.</p>

        <a href="{{meeting_link}}" style="background: #0066cc; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 2px 8px rgba(0,102,204,0.3);">
            📅 Escolher horário no calendário
        </a>

        <p style="margin-top: 20px; font-size: 14px; color: #64748b;">O link abre meu Calendly direto - você escolhe o melhor horário.</p>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Não quero receber mais emails</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_meeting_request_text(self) -> str:
        return """
{{contact_name}},

15 minutos para eu mostrar exatamente como a {{company_name}} pode recuperar valores pagos a mais em fretes.

Sem compromisso, sem venda agressiva. Só uma demonstração técnica de como auditamos CT-e/NF-e para {{segment}}.

📅 Escolher horário: {{meeting_link}}

(O link abre meu Calendly direto - você escolhe o melhor horário)

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""

    def _get_breakup_html(self) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">

    <!-- Header with Logo -->
    <div style="text-align: center; padding: 30px 0 20px 0; border-bottom: 1px solid #eaeaea;">
        <img src="https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png" alt="Averta" style="height: 60px; max-width: 100%;" onerror="this.style.display='none'">
    </div>

    <!-- Main Content -->
    <div style="padding: 30px 20px;">
        <p style="font-size: 16px; margin: 0 0 16px 0;">{{contact_name}},</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Não recebi retorno dos meus emails anteriores, então assumo que agora não é o momento certo para a <strong>{{company_name}}</strong>.</p>

        <p style="font-size: 16px; margin: 0 0 16px 0;">Vou fechar meu contato por aqui para não incomodar. Respeito totalmente sua decisão.</p>

        <p style="font-size: 16px; margin: 0 0 24px 0;">Se no futuro a {{company_name}} precisar auditar faturas de frete, identificar cobranças indevidas ou recuperar valores, a Averta estará aqui.</p>

        <div style="text-align: center; margin: 32px 0; padding: 20px; background: #f8fafc; border-radius: 8px;">
            <p style="margin: 0; font-size: 14px; color: #64748b;">Fica à vontade para me chamar quando quiser:<br>
            <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc;">contato@avertabrasil.com.br</a> |
            <a href="{{meeting_link}}" style="color: #0066cc;">Agendar direto no calendário</a></p>
        </div>

        <p style="font-size: 16px; text-align: center; margin: 0;">Obrigado pelo tempo! 🙏</p>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #eaeaea; padding: 24px 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; border-radius: 0 0 8px 8px;">
        <p style="margin: 0 0 8px 0;"><strong>Equipe Averta</strong><br>
        <a href="mailto:contato@avertabrasil.com.br" style="color: #0066cc; text-decoration: none;">contato@avertabrasil.com.br</a> |
        <span style="color: #0066cc;">+55 21 97887-9164</span></p>

        <p style="margin: 16px 0 0 0; font-size: 11px;">
            <a href="{{unsubscribe_link}}" style="color: #94a3b8; text-decoration: none;">Descadastrar permanentemente</a> |
            <a href="{{preferences_link}}" style="color: #94a3b8; text-decoration: none;">Preferências de comunicação</a>
        </p>
    </div>
</body>
</html>
"""

    def _get_breakup_text(self) -> str:
        return """
{{contact_name}},

Não recebi retorno dos meus emails anteriores, então assumo que agora não é o momento certo para a {{company_name}}.

Vou fechar meu contato por aqui para não incomodar. Respeito totalmente sua decisão.

Se no futuro a {{company_name}} precisar auditar faturas de frete, identificar cobranças indevidas ou recuperar valores, a Averta estará aqui.

Fica à vontade para me chamar quando quiser:
contato@avertabrasil.com.br | {{meeting_link}}

Obrigado pelo tempo! 🙏

---
Equipe Averta
contato@avertabrasil.com.br | +55 21 97887-9164

Não quer receber mais emails? {{unsubscribe_link}}
Preferências de comunicação: {{preferences_link}}
"""