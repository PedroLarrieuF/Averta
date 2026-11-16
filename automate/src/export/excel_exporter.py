"""Excel export functionality for leads."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dataclasses import asdict

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import format_date, serialize_json_field
from storage.models import QualifiedLead, LeadClassification, DailyReport

logger = get_logger(__name__)


class ExcelExporter:
    """Exports leads and reports to Excel format."""

    def __init__(self):
        self.settings = get_settings()
        self.output_dir = Path(self.settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Style definitions
        self.header_font = Font(bold=True, color="FFFFFF", size=11)
        self.header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
        self.header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        self.classification_fills = {
            'A': PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),  # Green
            'B': PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"),  # Yellow
            'C': PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),  # Red
            'D': PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"),  # Gray
        }

        self.thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    def export_leads_ab(self, leads: List[QualifiedLead], filename: str = None) -> str:
        """Export leads A and B to consolidated Excel."""
        if filename is None:
            filename = self.settings.export_files_leads_ab.format(
                date=format_date(datetime.now())
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Filter A and B leads
        ab_leads = [l for l in leads if l.classification in [LeadClassification.A, LeadClassification.B]]

        if not ab_leads:
            logger.warning("No A or B leads to export")
            # Create empty file with headers
            self._create_empty_export(filepath, self._get_leads_ab_columns())
            return str(filepath)

        # Convert to DataFrame
        data = []
        for lead in ab_leads:
            row = self._lead_to_row_ab(lead)
            data.append(row)

        df = pd.DataFrame(data)

        # Write to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads A_B', index=False)
            self._format_worksheet(writer.sheets['Leads A_B'], df, 'classification')

        logger.info(f"Exported {len(ab_leads)} leads A/B to {filepath}")
        return str(filepath)

    def export_leads_c(self, leads: List[QualifiedLead], filename: str = None) -> str:
        """Export leads C for enrichment to Excel."""
        if filename is None:
            filename = self.settings.export_files_leads_c.format(
                date=format_date(datetime.now())
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Filter C leads
        c_leads = [l for l in leads if l.classification == LeadClassification.C]

        if not c_leads:
            logger.warning("No C leads to export")
            self._create_empty_export(filepath, self._get_leads_c_columns())
            return str(filepath)

        # Convert to DataFrame
        data = []
        for lead in c_leads:
            row = self._lead_to_row_c(lead)
            data.append(row)

        df = pd.DataFrame(data)

        # Write to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads C - Enriquecimento', index=False)
            self._format_worksheet(writer.sheets['Leads C - Enriquecimento'], df)

        logger.info(f"Exported {len(c_leads)} leads C to {filepath}")
        return str(filepath)

    def export_whatsapp_ready(self, leads: List[QualifiedLead], filename: str = None) -> str:
        """Export WhatsApp-ready leads to Excel."""
        if filename is None:
            filename = self.settings.export_files_whatsapp_ready.format(
                date=format_date(datetime.now())
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Filter WhatsApp-ready leads
        wa_leads = [l for l in leads if l.whatsapp_ready]

        if not wa_leads:
            logger.warning("No WhatsApp-ready leads to export")
            self._create_empty_export(filepath, self._get_whatsapp_columns())
            return str(filepath)

        # Convert to DataFrame
        data = []
        for lead in wa_leads:
            row = self._lead_to_row_whatsapp(lead)
            data.append(row)

        df = pd.DataFrame(data)

        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='WhatsApp Ready', index=False)
            self._format_worksheet(writer.sheets['WhatsApp Ready'], df)

        logger.info(f"Exported {len(wa_leads)} WhatsApp-ready leads to {filepath}")
        return str(filepath)

    def export_daily_report(self, report: DailyReport, filename: str = None) -> str:
        """Export daily report to Excel."""
        if filename is None:
            filename = self.settings.export_files_daily_report.format(
                date=format_date(report.date)
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Create workbook with multiple sheets
        wb = Workbook()

        # Sheet 1: Summary
        ws1 = wb.active
        ws1.title = "Resumo Diário"
        self._write_summary_sheet(ws1, report)

        # Sheet 2: Coverage by State
        ws2 = wb.create_sheet("Cobertura por Estado")
        self._write_coverage_sheet(ws2, report)

        # Sheet 3: Classification Breakdown
        ws3 = wb.create_sheet("Classificação")
        self._write_classification_sheet(ws3, report)

        # Sheet 4: Contacts
        ws4 = wb.create_sheet("Contatos")
        self._write_contacts_sheet(ws4, report)

        wb.save(filepath)
        logger.info(f"Exported daily report to {filepath}")
        return str(filepath)

    def export_coverage_report(self, stats: Dict[str, Any], filename: str = None) -> str:
        """Export coverage report to Excel."""
        if filename is None:
            filename = self.settings.export_files_coverage_report.format(
                date=format_date(datetime.now())
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        wb = Workbook()

        # Sheet 1: By State
        ws1 = wb.active
        ws1.title = "Por Estado"
        self._write_state_coverage(ws1, stats.get('by_state', {}))

        # Sheet 2: By Segment
        ws2 = wb.create_sheet("Por Segmento")
        self._write_segment_coverage(ws2, stats.get('by_segment', {}))

        # Sheet 3: By Classification
        ws3 = wb.create_sheet("Por Classificação")
        self._write_classification_coverage(ws3, stats.get('by_classification', {}))

        # Sheet 4: Contacts Summary
        ws4 = wb.create_sheet("Resumo Contatos")
        self._write_contacts_summary(ws4, stats)

        wb.save(filepath)
        logger.info(f"Exported coverage report to {filepath}")
        return str(filepath)

    def export_decision_makers_report(self, leads: List[QualifiedLead], filename: str = None) -> str:
        """Export decision makers report to Excel."""
        if filename is None:
            filename = self.settings.export_files_decision_makers_report.format(
                date=format_date(datetime.now())
            )

        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Collect all decision makers
        data = []
        for lead in leads:
            for dm in lead.decision_makers:
                data.append({
                    'lead_id': lead.id,
                    'company_name': lead.name,
                    'company_segment': lead.segment,
                    'company_city': lead.city,
                    'company_state': lead.state,
                    'lead_score': lead.score,
                    'lead_classification': lead.classification.value,
                    'dm_id': dm.id,
                    'dm_name': dm.name,
                    'dm_role': dm.role,
                    'dm_department': dm.department,
                    'dm_email': dm.email,
                    'dm_email_verified': dm.email_verified,
                    'dm_phone': dm.phone,
                    'dm_phone_verified': dm.phone_verified,
                    'dm_whatsapp': dm.whatsapp,
                    'dm_whatsapp_verified': dm.whatsapp_verified,
                    'dm_linkedin': dm.linkedin,
                    'dm_linkedin_verified': dm.linkedin_verified,
                    'dm_source': dm.source,
                    'dm_confidence': dm.confidence,
                    'dm_identified_at': dm.identified_at.isoformat() if dm.identified_at else None,
                })

        if not data:
            logger.warning("No decision makers to export")
            self._create_empty_export(filepath, [
                'lead_id', 'company_name', 'company_segment', 'company_city', 'company_state',
                'lead_score', 'lead_classification', 'dm_id', 'dm_name', 'dm_role',
                'dm_department', 'dm_email', 'dm_email_verified', 'dm_phone',
                'dm_phone_verified', 'dm_whatsapp', 'dm_whatsapp_verified',
                'dm_linkedin', 'dm_linkedin_verified', 'dm_source', 'dm_confidence',
                'dm_identified_at'
            ])
            return str(filepath)

        df = pd.DataFrame(data)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Decisores', index=False)
            self._format_worksheet(writer.sheets['Decisores'], df)

        logger.info(f"Exported {len(data)} decision makers to {filepath}")
        return str(filepath)

    def _get_leads_ab_columns(self) -> List[str]:
        """Get columns for leads A/B export."""
        return self.settings.export_leads_ab_columns

    def _get_leads_c_columns(self) -> List[str]:
        """Get columns for leads C export."""
        return self.settings.export_leads_c_columns

    def _get_whatsapp_columns(self) -> List[str]:
        """Get columns for WhatsApp export."""
        return self.settings.export_whatsapp_columns

    def _lead_to_row_ab(self, lead: QualifiedLead) -> Dict:
        """Convert lead to row for A/B export."""
        return {
            'id': lead.id,
            'classification': lead.classification.value,
            'score': lead.score,
            'company_name': lead.name,
            'trade_name': lead.trade_name,
            'segment': lead.segment,
            'address': lead.address,
            'city': lead.city,
            'state': lead.state,
            'postal_code': lead.postal_code,
            'phone': lead.phone,
            'phone_verified': 'Sim' if lead.phone_verified else 'Não',
            'whatsapp': lead.whatsapp,
            'whatsapp_verified': 'Sim' if lead.whatsapp_verified else 'Não',
            'email': lead.email,
            'email_verified': 'Sim' if lead.email_verified else 'Não',
            'website': lead.website,
            'website_verified': 'Sim' if lead.website_verified else 'Não',
            'linkedin': lead.linkedin,
            'linkedin_verified': 'Sim' if lead.linkedin_verified else 'Não',
            'rating': lead.rating,
            'reviews_count': lead.reviews_count,
            'latitude': lead.latitude,
            'longitude': lead.longitude,
            'operational_fit_score': lead.operational_fit_score,
            'commercial_fit_score': lead.commercial_fit_score,
            'data_confidence_score': lead.data_confidence_score,
            'decision_makers': serialize_json_field([dm.to_dict() for dm in lead.decision_makers]),
            'institutional_contacts': serialize_json_field([ic.to_dict() for ic in lead.institutional_contacts]),
            'source_query': lead.source_query,
            'scraped_at': lead.scraped_at.isoformat() if lead.scraped_at else None,
            'qualified_at': lead.qualified_at.isoformat() if lead.qualified_at else None,
            'notes': lead.notes,
        }

    def _lead_to_row_c(self, lead: QualifiedLead) -> Dict:
        """Convert lead to row for C export."""
        missing = lead.get_missing_fields()
        return {
            'id': lead.id,
            'score': lead.score,
            'company_name': lead.name,
            'trade_name': lead.trade_name,
            'segment': lead.segment,
            'address': lead.address,
            'city': lead.city,
            'state': lead.state,
            'phone': lead.phone,
            'email': lead.email,
            'website': lead.website,
            'linkedin': lead.linkedin,
            'missing_fields': serialize_json_field(missing),
            'source_query': lead.source_query,
            'scraped_at': lead.scraped_at.isoformat() if lead.scraped_at else None,
            'enrichment_priority': lead.enrichment_priority,
            'notes': lead.notes,
        }

    def _lead_to_row_whatsapp(self, lead: QualifiedLead) -> Dict:
        """Convert lead to row for WhatsApp export."""
        # Get best contact name
        contact_name = ""
        contact_role = ""
        if lead.decision_makers:
            dm = lead.decision_makers[0]
            contact_name = dm.name or ""
            contact_role = dm.role or ""

        # Determine best phone
        phone = lead.whatsapp or lead.phone or ""

        return {
            'id': lead.id,
            'company_name': lead.name or lead.trade_name,
            'contact_name': contact_name,
            'contact_role': contact_role,
            'phone': phone,
            'whatsapp': lead.whatsapp or "",
            'email': lead.email or "",
            'segment': lead.segment,
            'city': lead.city or "",
            'state': lead.state or "",
            'score': lead.score,
            'template_suggested': lead.whatsapp_template_suggested or "",
            'opt_in_status': lead.whatsapp_opt_in_status,
            'last_contact_at': lead.whatsapp_last_contact_at.isoformat() if lead.whatsapp_last_contact_at else "",
            'notes': lead.notes or "",
        }

    def _create_empty_export(self, filepath: Path, columns: List[str]):
        """Create empty export file with headers."""
        df = pd.DataFrame(columns=columns)
        df.to_excel(filepath, index=False)

    def _format_worksheet(self, ws, df: pd.DataFrame, classification_col: str = None):
        """Apply formatting to worksheet."""
        # Format headers
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.header_alignment
            cell.border = self.thin_border

        # Format data rows
        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = self.thin_border
                cell.alignment = Alignment(vertical="center", wrap_text=True)

                # Color by classification
                if classification_col and classification_col in df.columns:
                    class_col_idx = df.columns.get_loc(classification_col) + 1
                    if col_idx == class_col_idx:
                        class_value = cell.value
                        if class_value in self.classification_fills:
                            cell.fill = self.classification_fills[class_value]

        # Auto-adjust column widths
        for col_idx in range(1, ws.max_column + 1):
            max_length = 0
            column_letter = get_column_letter(col_idx)

            for row_idx in range(1, min(ws.max_row + 1, 100)):  # Sample first 100 rows
                cell = ws.cell(row=row_idx, column=col_idx)
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            # Set width with limits
            adjusted_width = min(max(max_length + 2, 10), 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Freeze header row
        ws.freeze_panes = 'A2'

        # Auto-filter
        if ws.max_row > 1:
            ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

    def _write_summary_sheet(self, ws, report: DailyReport):
        """Write daily report summary sheet."""
        ws.cell(row=1, column=1, value="Relatório Diário de Prospecção").font = Font(bold=True, size=14)
        ws.cell(row=2, column=1, value=f"Data: {format_date(report.date)}").font = Font(size=11)

        summary_data = [
            ("Métrica", "Valor"),
            ("Queries Executadas", report.queries_executed),
            ("Empresas Encontradas", report.companies_found),
            ("Empresas Únicas", report.unique_companies),
            ("Leads Classificação A", report.leads_classified_a),
            ("Leads Classificação B", report.leads_classified_b),
            ("Leads Classificação C", report.leads_classified_c),
            ("Leads Classificação D", report.leads_classified_d),
            ("Leads Descartados", report.leads_discarded),
            ("Decisores Identificados", report.decision_makers_identified),
            ("Contatos Institucionais Válidos", report.institutional_contacts_valid),
            ("Telefones Comerciais Válidos", report.business_phones_valid),
            ("E-mails Corporativos Encontrados", report.corporate_emails_found),
            ("LinkedIn Verificáveis", report.linkedin_verified),
            ("Estados Cobertos", report.states_covered),
            ("Segmentos Cobertos", report.segments_covered),
            ("Custo por Lead Qualificado", f"R$ {report.cost_per_qualified_lead:.2f}"),
            ("Taxa de Qualificação", f"{report.qualification_rate:.1f}%"),
            ("Duração (segundos)", report.duration_seconds),
        ]

        for row_idx, (metric, value) in enumerate(summary_data, 4):
            ws.cell(row=row_idx, column=1, value=metric).font = Font(bold=True)
            ws.cell(row=row_idx, column=2, value=value)

        # Errors and warnings
        if report.errors:
            row = len(summary_data) + 5
            ws.cell(row=row, column=1, value="Erros:").font = Font(bold=True, color="FF0000")
            for err in report.errors:
                row += 1
                ws.cell(row=row, column=1, value=f"  • {err}")

        if report.warnings:
            row += 2
            ws.cell(row=row, column=1, value="Avisos:").font = Font(bold=True, color="FFA500")
            for warn in report.warnings:
                row += 1
                ws.cell(row=row, column=1, value=f"  • {warn}")

    def _write_coverage_sheet(self, ws, report: DailyReport):
        """Write coverage by state sheet."""
        # This would need state breakdown data from report
        # For now, create placeholder
        ws.cell(row=1, column=1, value="Estado").font = self.header_font
        ws.cell(row=1, column=2, value="Leads A").font = self.header_font
        ws.cell(row=1, column=3, value="Leads B").font = self.header_font
        ws.cell(row=1, column=4, value="Leads C").font = self.header_font
        ws.cell(row=1, column=5, value="Total").font = self.header_font

        for col in range(1, 6):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

    def _write_classification_sheet(self, ws, report: DailyReport):
        """Write classification breakdown sheet."""
        ws.cell(row=1, column=1, value="Classificação").font = self.header_font
        ws.cell(row=1, column=2, value="Quantidade").font = self.header_font
        ws.cell(row=1, column=3, value="Percentual").font = self.header_font

        for col in range(1, 4):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        total = (report.leads_classified_a + report.leads_classified_b +
                report.leads_classified_c + report.leads_classified_d)

        classifications = [
            ('A', report.leads_classified_a),
            ('B', report.leads_classified_b),
            ('C', report.leads_classified_c),
            ('D', report.leads_classified_d),
        ]

        for row_idx, (cls, count) in enumerate(classifications, 2):
            ws.cell(row=row_idx, column=1, value=cls).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=count).border = self.thin_border
            pct = (count / total * 100) if total > 0 else 0
            ws.cell(row=row_idx, column=3, value=f"{pct:.1f}%").border = self.thin_border

            if cls in self.classification_fills:
                ws.cell(row=row_idx, column=1).fill = self.classification_fills[cls]

    def _write_contacts_sheet(self, ws, report: DailyReport):
        """Write contacts summary sheet."""
        ws.cell(row=1, column=1, value="Tipo de Contato").font = self.header_font
        ws.cell(row=1, column=2, value="Quantidade Válida").font = self.header_font

        for col in range(1, 3):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        contacts = [
            ("Decisores Identificados", report.decision_makers_identified),
            ("Contatos Institucionais", report.institutional_contacts_valid),
            ("Telefones Comerciais", report.business_phones_valid),
            ("E-mails Corporativos", report.corporate_emails_found),
            ("LinkedIn Verificáveis", report.linkedin_verified),
        ]

        for row_idx, (contact_type, count) in enumerate(contacts, 2):
            ws.cell(row=row_idx, column=1, value=contact_type).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=count).border = self.thin_border

    def _write_state_coverage(self, ws, by_state: Dict[str, int]):
        """Write state coverage sheet."""
        ws.cell(row=1, column=1, value="Estado").font = self.header_font
        ws.cell(row=1, column=2, value="Total Leads").font = self.header_font

        for col in range(1, 3):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        for row_idx, (state, count) in enumerate(sorted(by_state.items()), 2):
            ws.cell(row=row_idx, column=1, value=state).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=count).border = self.thin_border

    def _write_segment_coverage(self, ws, by_segment: Dict[str, int]):
        """Write segment coverage sheet."""
        ws.cell(row=1, column=1, value="Segmento").font = self.header_font
        ws.cell(row=1, column=2, value="Total Leads").font = self.header_font

        for col in range(1, 3):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        for row_idx, (segment, count) in enumerate(sorted(by_segment.items(), key=lambda x: -x[1]), 2):
            ws.cell(row=row_idx, column=1, value=segment).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=count).border = self.thin_border

    def _write_classification_coverage(self, ws, by_classification: Dict[str, int]):
        """Write classification coverage sheet."""
        ws.cell(row=1, column=1, value="Classificação").font = self.header_font
        ws.cell(row=1, column=2, value="Total Leads").font = self.header_font

        for col in range(1, 3):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        for row_idx, (cls, count) in enumerate(sorted(by_classification.items()), 2):
            ws.cell(row=row_idx, column=1, value=cls).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=count).border = self.thin_border

            if cls in self.classification_fills:
                ws.cell(row=row_idx, column=1).fill = self.classification_fills[cls]

    def _write_contacts_summary(self, ws, stats: Dict[str, Any]):
        """Write contacts summary sheet."""
        ws.cell(row=1, column=1, value="Métrica").font = self.header_font
        ws.cell(row=1, column=2, value="Valor").font = self.header_font

        for col in range(1, 3):
            ws.cell(row=1, column=col).fill = self.header_fill
            ws.cell(row=1, column=col).alignment = self.header_alignment
            ws.cell(row=1, column=col).border = self.thin_border

        metrics = [
            ("Total Leads Qualificados", stats.get('total_qualified', 0)),
            ("Com E-mail", stats.get('with_email', 0)),
            ("Com Telefone", stats.get('with_phone', 0)),
            ("Com WhatsApp", stats.get('with_whatsapp', 0)),
            ("Com LinkedIn", stats.get('with_linkedin', 0)),
            ("Prontos para WhatsApp", stats.get('whatsapp_ready', 0)),
        ]

        for row_idx, (metric, value) in enumerate(metrics, 2):
            ws.cell(row=row_idx, column=1, value=metric).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=value).border = self.thin_border