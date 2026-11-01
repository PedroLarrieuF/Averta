"""PDF Generator for contest letters and reports"""
from typing import Optional
from datetime import datetime
from jinja2 import Environment, BaseLoader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
import io
import structlog

logger = structlog.get_logger()


# Colors
DARK_BLUE = HexColor("#1e3a5f")
MEDIUM_BLUE = HexColor("#2c5f8a")
LIGHT_BLUE = HexColor("#e8f0f8")
GRAY = HexColor("#666666")
DARK_GRAY = HexColor("#333333")
LIGHT_GRAY = HexColor("#f5f5f5")
RED = HexColor("#dc3545")
GREEN = HexColor("#28a745")


def generate_contest_letter(
    contest: dict,
    client: dict,
    carrier: dict,
    company: dict,
    template: str = "default",
) -> bytes:
    """Generate contest letter PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        leading=22,
        textColor=DARK_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=MEDIUM_BLUE,
        spaceAfter=12,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=DARK_BLUE,
        spaceBefore=12,
        spaceAfter=6,
        borderWidth=0,
        borderPadding=0,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=DARK_GRAY,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    )

    bold_style = ParagraphStyle(
        'CustomBold',
        parent=body_style,
        fontName='Helvetica-Bold',
    )

    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=GRAY,
        alignment=TA_CENTER,
    )

    # ===== HEADER =====
    story.append(Paragraph(company.get("name", "AVERTA S.A."), title_style))
    story.append(Paragraph("Auditoria de Frete com Cobrança por Êxito", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE, spaceAfter=12))

    # ===== CONTEST INFO =====
    contest_data = [
        ["Número da Contestação:", contest.get("number", "")],
        ["Data:", datetime.utcnow().strftime("%d/%m/%Y")],
        ["Status:", contest.get("status", "DRAFT")],
        ["Cliente:", client.get("name", "")],
        ["CNPJ Cliente:", _format_cnpj(client.get("cnpj", ""))],
        ["Transportadora:", carrier.get("name", "")],
        ["CNPJ Transportadora:", _format_cnpj(carrier.get("cnpj", ""))],
    ]

    if contest.get("contract_id"):
        contest_data.append(["Contrato:", contest.get("contract_id", "")])

    info_table = Table(contest_data, colWidths=[5*cm, 13*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), DARK_BLUE),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_BLUE),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ===== INTRODUCTION =====
    story.append(Paragraph("1. INTRODUÇÃO", heading_style))
    story.append(Paragraph(
        f"Prezados,<br/><br/>"
        f"A {company.get('name', 'AVERTA S.A.')}, em nome de seu cliente "
        f"<b>{client.get('name', '')}</b> (CNPJ: {_format_cnpj(client.get('cnpj', ''))}), "
        f"apresenta a presente contestação referente a divergências identificadas "
        f"nas faturas de frete emitidas por <b>{carrier.get('name', '')}</b> "
        f"(CNPJ: {_format_cnpj(carrier.get('cnpj', ''))}).",
        body_style
    ))

    # ===== DISCREPANCIES TABLE =====
    story.append(Paragraph("2. DIVERGÊNCIAS IDENTIFICADAS", heading_style))
    story.append(Paragraph(
        "Abaixo seguem o detalhamento das divergências encontradas após auditoria "
        "das faturas de frete (CT-e/NF-e) conforme contrato vigente:",
        body_style
    ))

    # Table header
    disc_data = [
        ["Item", "Tipo", "Regra", "Valor Esperado", "Valor Faturado", "Diferença", "%"]
    ]

    items = contest.get("items", [])
    for idx, item in enumerate(items, 1):
        # Get discrepancy details from item metadata or fetch
        disc_type = item.get("discrepancy", {}).get("type", "N/A")
        rule_code = item.get("discrepancy", {}).get("ruleCode", "N/A")

        disc_data.append([
            str(idx),
            _format_disc_type(disc_type),
            rule_code,
            f"R$ {item.get('expected_value', 0):,.2f}",
            f"R$ {item.get('actual_value', item.get('contested_value', 0)):,.2f}",
            f"R$ {item.get('difference', 0):,.2f}",
            f"{item.get('difference_pct', 0):.1f}%",
        ])

    # Total row
    total_expected = sum(i.get('expected_value', 0) for i in items)
    total_contested = sum(i.get('contested_value', 0) for i in items)
    total_diff = sum(i.get('difference', 0) for i in items)

    disc_data.append([
        "", "", "<b>TOTAL</b>",
        f"<b>R$ {total_expected:,.2f}</b>",
        f"<b>R$ {total_contested:,.2f}</b>",
        f"<b>R$ {total_diff:,.2f}</b>",
        "",
    ])

    disc_table = Table(disc_data, colWidths=[1*cm, 2.5*cm, 3*cm, 3*cm, 3*cm, 3*cm, 2*cm])
    disc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [HexColor("#ffffff"), LIGHT_GRAY]),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BLUE),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(disc_table)
    story.append(Spacer(1, 12))

    # ===== FINANCIAL SUMMARY =====
    story.append(Paragraph("3. RESUMO FINANCEIRO", heading_style))

    success_fee_pct = contest.get("success_fee_pct", 25)
    success_fee_value = contest.get("success_fee_value", 0)
    net_recovery = contest.get("net_recovery", 0)

    fin_data = [
        ["Descrição", "Valor"],
        ["Total Contestável", f"R$ {total_contested:,.2f}"],
        ["Success Fee ({:.0f}%)".format(success_fee_pct), f"R$ {success_fee_value:,.2f}"],
        ["<b>Valor Líquido a Recuperar</b>", f"<b>R$ {net_recovery:,.2f}</b>"],
    ]

    fin_table = Table(fin_data, colWidths=[10*cm, 6*cm])
    fin_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [HexColor("#ffffff"), LIGHT_GRAY]),
        ('BACKGROUND', (0, -1), (-1, -1), GREEN),
        ('TEXTCOLOR', (0, -1), (-1, -1), HexColor("#ffffff")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 16))

    # ===== LEGAL BASIS =====
    story.append(Paragraph("4. FUNDAMENTAÇÃO LEGAL E CONTRATUAL", heading_style))
    story.append(Paragraph(
        "A presente contestação fundamenta-se nas seguintes bases:",
        body_style
    ))

    legal_items = [
        "Contrato de prestação de serviços de transporte vigente entre as partes;",
        "Tabela de frete acordada (anexa ao contrato) com vigência na data dos CT-es;",
        "Legislação tributária aplicável (ICMS, DIFAL, FCP, ST) conforme UF origem/destino;",
        "Resolução ANTT nº 5.839/2020 (tabela de frete mínimo);",
        "Código de Defesa do Consumidor (Lei nº 8.078/90) - art. 6º, VIII;",
        "Código Civil (Lei nº 10.406/02) - arts. 186, 927 e 944;",
    ]

    for item in legal_items:
        story.append(Paragraph(f"• {item}", body_style))

    story.append(Spacer(1, 12))

    # ===== REQUEST =====
    story.append(Paragraph("5. PEDIDO", heading_style))
    story.append(Paragraph(
        "Diante do exposto, requer-se:",
        body_style
    ))

    requests = [
        "O reconhecimento das divergências apontadas e a correção dos valores faturados;",
        "O pagamento da diferença apurada no valor total de <b>R$ {:,.2f}</b> "
        "em favor de <b>{}</b> (CNPJ: {}), "
        "no prazo de 30 (trinta) dias corridos a contar do recebimento desta;".format(
            total_contested, client.get('name', ''), _format_cnpj(client.get('cnpj', ''))
        ),
        "A apresentação de justificativa fundamentada, no prazo de 15 (quinze) dias, "
        "caso discorde dos valores apresentados;",
        "A aplicação da cláusula de success fee contratual ({:.0f}%) "
        "sobre o valor efetivamente recuperado.".format(success_fee_pct),
    ]

    for req in requests:
        story.append(Paragraph(f"• {req}", body_style))

    story.append(Spacer(1, 20))

    # ===== CLOSING =====
    story.append(Paragraph(
        "Certos de contar com a compreensão e colaboração de V.Sas., "
        "colocamo-nos à disposição para quaisquer esclarecimentos adicionais.",
        body_style
    ))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE, spaceAfter=12))

    story.append(Paragraph(
        f"<b>{company.get('name', 'AVERTA S.A.')}</b><br/>"
        f"Auditoria de Frete com Cobrança por Êxito<br/>"
        f"E-mail: {company.get('email', 'contato@averta.com')}<br/>"
        f"Site: {company.get('website', 'www.averta.com')}",
        ParagraphStyle('Closing', parent=body_style, alignment=TA_LEFT, fontSize=9, textColor=GRAY)
    ))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info("pdf_generated", contest_number=contest.get("number"), size=len(pdf_bytes))
    return pdf_bytes


def _format_cnpj(cnpj: str) -> str:
    """Format CNPJ: 00.000.000/0000-00"""
    digits = "".join(filter(str.isdigit, cnpj))
    if len(digits) == 14:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    return cnpj


def _format_disc_type(disc_type: str) -> str:
    """Format discrepancy type for display"""
    mapping = {
        "ICMS_DIFFERENTIAL": "ICMS DIFAL",
        "ICMS_FCP": "ICMS FCP",
        "ICMS_ST": "ICMS ST",
        "FREIGHT_WEIGHT_VALUE": "Frete Peso/Valor",
        "FREIGHT_CUBAGE": "Frete Cubagem",
        "REDESPACHO": "Redespacho",
        "TOLL_PLAZA": "Pedágio",
        "AD_VALOREM": "Ad Valorem",
        "GRIS": "GRIS",
        "SICOBAN_TABLE": "Tabela Sicoban",
        "COMPLEMENTARY_CTE": "CT-e Complementar",
    }
    return mapping.get(disc_type, disc_type)