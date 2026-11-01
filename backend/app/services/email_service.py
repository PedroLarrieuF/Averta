"""Email Service - SendGrid integration with templates"""
from typing import Optional, List, Dict, Any
from pathlib import Path
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64

from app.core.config import settings

logger = structlog.get_logger()


class EmailService:
    """SendGrid-based email service with Jinja2 templates"""

    def __init__(self):
        self.client = None
        self.templates_env = None
        self._init_client()
        self._init_templates()

    def _init_client(self):
        """Initialize SendGrid client"""
        if settings.SENDGRID_API_KEY:
            self.client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            logger.info("sendgrid_client_initialized")
        else:
            logger.warning("sendgrid_api_key_not_set", environment=settings.ENVIRONMENT)

    def _init_templates(self):
        """Initialize Jinja2 template environment"""
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.templates_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        logger.info("email_templates_loaded", template_dir=str(template_dir))

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """Render both HTML and text versions of a template"""
        try:
            html_template = self.templates_env.get_template(f"{template_name}.html")
            text_template = self.templates_env.get_template(f"{template_name}.txt")

            html_content = html_template.render(**context)
            text_content = text_template.render(**context)

            return html_content, text_content
        except Exception as e:
            logger.exception("template_render_error", template=template_name, error=str(e))
            # Fallback simple content
            return (
                f"<p>{context.get('message', 'Notification')}</p>",
                context.get('message', 'Notification')
            )

    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        attachments: Optional[List[Dict[str, Any]]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """Send email using SendGrid"""
        if not self.client:
            logger.warning("sendgrid_not_configured", to_email=to_email)
            return False

        from_email = from_email or settings.SENDGRID_FROM_EMAIL
        from_name = from_name or settings.SENDGRID_FROM_NAME

        html_content, text_content = self._render_template(template_name, context)

        message = Mail(
            from_email=Email(from_email, from_name),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", html_content),
            plain_text_content=Content("text/plain", text_content),
        )

        # Add attachments if any
        if attachments:
            for att in attachments:
                attachment = Attachment()
                attachment.file_content = FileContent(att["content"])
                attachment.file_name = FileName(att["filename"])
                attachment.file_type = FileType(att.get("type", "application/pdf"))
                attachment.disposition = Disposition(att.get("disposition", "attachment"))
                message.attachment = attachment

        try:
            response = self.client.send(message)
            logger.info(
                "email_sent",
                to_email=to_email,
                subject=subject,
                status_code=response.status_code,
            )
            return response.status_code in (200, 201, 202)
        except Exception as e:
            logger.exception("email_send_failed", to_email=to_email, error=str(e))
            return False

    # ============================================
    # High-level notification methods
    # ============================================

    async def send_discrepancy_alert(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        discrepancies: List[Dict[str, Any]],
        document_number: str,
        carrier_name: str,
    ) -> bool:
        """Send discrepancy alert to client"""
        context = {
            "client_name": client_name,
            "document_number": document_number,
            "carrier_name": carrier_name,
            "discrepancies": discrepancies,
            "total_discrepancies": len(discrepancies),
            "total_value": sum(d.get("difference", 0) for d in discrepancies if d.get("difference")),
            "dashboard_url": f"{settings.FRONTEND_URL}/documents",
        }

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=f"[Averta] {len(discrepancies)} divergências encontradas no CT-e {document_number}",
            template_name="discrepancy_alert",
            context=context,
        )

    async def send_contest_created(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        contest_number: str,
        carrier_name: str,
        total_value: float,
        pdf_path: Optional[str] = None,
    ) -> bool:
        """Send contest notification with PDF attachment"""
        context = {
            "client_name": client_name,
            "contest_number": contest_number,
            "carrier_name": carrier_name,
            "total_value": total_value,
            "contest_url": f"{settings.FRONTEND_URL}/contests/{contest_number}",
        }

        attachments = None
        if pdf_path:
            import os
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_content = base64.b64encode(f.read()).decode()
                attachments = [{
                    "content": pdf_content,
                    "filename": f"Contestacao_{contest_number}.pdf",
                    "type": "application/pdf",
                }]

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=f"[Averta] Contestação {contest_number} criada - R$ {total_value:,.2f}",
            template_name="contest_created",
            context=context,
            attachments=attachments,
        )

    async def send_weekly_report(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        report_data: Dict[str, Any],
        pdf_path: Optional[str] = None,
        excel_path: Optional[str] = None,
    ) -> bool:
        """Send weekly audit report"""
        context = {
            "client_name": client_name,
            "period": report_data.get("period", "Esta semana"),
            "documents_audited": report_data.get("documents_audited", 0),
            "discrepancies_found": report_data.get("discrepancies_found", 0),
            "total_recoverable": report_data.get("total_recoverable", 0),
            "success_rate": report_data.get("success_rate", 0),
            "top_carriers": report_data.get("top_carriers", []),
            "top_discrepancy_types": report_data.get("top_discrepancy_types", []),
            "dashboard_url": f"{settings.FRONTEND_URL}/reports",
        }

        attachments = []
        if pdf_path:
            import os
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_content = base64.b64encode(f.read()).decode()
                attachments.append({
                    "content": pdf_content,
                    "filename": f"Relatorio_Semanal_{client_name}.pdf",
                    "type": "application/pdf",
                })
        if excel_path:
            import os
            if os.path.exists(excel_path):
                with open(excel_path, "rb") as f:
                    excel_content = base64.b64encode(f.read()).decode()
                attachments.append({
                    "content": excel_content,
                    "filename": f"Relatorio_Semanal_{client_name}.xlsx",
                    "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                })

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=f"[Averta] Relatório Semanal de Auditoria - {client_name}",
            template_name="weekly_report",
            context=context,
            attachments=attachments if attachments else None,
        )

    async def send_contract_expiring(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        contract_number: str,
        carrier_name: str,
        days_until_expiry: int,
    ) -> bool:
        """Send contract expiration warning"""
        context = {
            "client_name": client_name,
            "contract_number": contract_number,
            "carrier_name": carrier_name,
            "days_until_expiry": days_until_expiry,
            "contract_url": f"{settings.FRONTEND_URL}/contracts/{contract_number}",
        }

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=f"[Averta] Contrato {contract_number} vence em {days_until_expiry} dias",
            template_name="contract_expiring",
            context=context,
        )

    async def send_payment_received(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        contest_number: str,
        amount: float,
        success_fee: float,
        net_amount: float,
    ) -> bool:
        """Send payment received notification (success-fee billing)"""
        context = {
            "client_name": client_name,
            "contest_number": contest_number,
            "amount": amount,
            "success_fee": success_fee,
            "net_amount": net_amount,
            "fee_percentage": settings.SUCCESS_FEE_PERCENTAGE,
        }

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=f"[Averta] Pagamento recebido - Contestação {contest_number}",
            template_name="payment_received",
            context=context,
        )

    async def send_welcome(
        self,
        to_email: str,
        to_name: str,
        client_name: str,
        login_url: str,
        temp_password: Optional[str] = None,
    ) -> bool:
        """Send welcome email to new client"""
        context = {
            "client_name": client_name,
            "login_url": login_url,
            "temp_password": temp_password,
            "support_email": settings.SUPPORT_EMAIL,
        }

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject="Bem-vindo à Averta - Auditoria de Frete",
            template_name="welcome",
            context=context,
        )

    async def send_password_reset(
        self,
        to_email: str,
        to_name: str,
        reset_url: str,
        expires_hours: int = 24,
    ) -> bool:
        """Send password reset email"""
        context = {
            "to_name": to_name,
            "reset_url": reset_url,
            "expires_hours": expires_hours,
        }

        return await self.send_email(
            to_email=to_email,
            to_name=to_name,
            subject="Redefinição de senha - Averta",
            template_name="password_reset",
            context=context,
        )


# Singleton instance
email_service = EmailService()