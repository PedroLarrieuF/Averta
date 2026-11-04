#!/usr/bin/env python
"""Demo Script - Gera emails preenchidos com valores reais (standalone, sem deps)"""

import json
from pathlib import Path

# Configurar paths
ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "app" / "templates" / "emails"
OUTPUT_DIR = ROOT / "demo_emails"
OUTPUT_DIR.mkdir(exist_ok=True)

# Simular resultados da auditoria (pré-calculados pelas rules)
DEMO_RESULTS = [
    {
        "rule_code": "ICMS_DIFAL",
        "rule_name": "ICMS Diferencial de Alíquota (DIFAL)",
        "discrepancy_type": "ICMS_DIFFERENTIAL",
        "expected_value": 10500.00,
        "actual_value": 5250.00,
        "difference": 5250.00,
        "difference_pct": 100.0,
        "severity": "HIGH",
        "details": {
            "uf_origem": "SP",
            "uf_destino": "RJ",
            "base_calculo": 150000.00,
            "aliquota_difal": 5.0,
            "aliquota_fcp": 2.0,
        },
    },
    {
        "rule_code": "ICMS_FCP",
        "rule_name": "FCP - Fundo de Combate à Pobreza",
        "discrepancy_type": "ICMS_FCP",
        "expected_value": 3000.00,
        "actual_value": 0.00,
        "difference": 3000.00,
        "difference_pct": 100.0,
        "severity": "HIGH",
        "details": {"uf_destino": "RJ", "aliquota_fcp": 2.0, "base_calculo": 150000.00},
    },
    {
        "rule_code": "ICMS_ST",
        "rule_name": "ICMS Substituição Tributária (ST)",
        "discrepancy_type": "ICMS_ST",
        "expected_value": 30000.00,
        "actual_value": 25000.00,
        "difference": 5000.00,
        "difference_pct": 20.0,
        "severity": "HIGH",
        "details": {
            "cst": "10",
            "ncm": "22030000",
            "uf_origem": "SP",
            "uf_destino": "RJ",
            "base_calculo_st": 150000.00,
            "aliquota_st": 20.0,
        },
    },
    {
        "rule_code": "FRETE_PESO_VALOR",
        "rule_name": "Frete Peso vs Valor (Faixas)",
        "discrepancy_type": "FREIGHT_WEIGHT_VALUE",
        "expected_value": 8640.00,
        "actual_value": 8500.00,
        "difference": 140.00,
        "difference_pct": 1.6,
        "severity": "HIGH",
        "details": {
            "peso": 18000.0,
            "faixa": "15-30 ton",
            "valor_kg": 0.48,
            "valor_minimo": 7000.00,
        },
    },
    {
        "rule_code": "FRETE_CUBAGE",
        "rule_name": "Frete Cubagem (m³) vs Tabela",
        "discrepancy_type": "FREIGHT_CUBAGE",
        "expected_value": 4375.00,
        "actual_value": 8500.00,
        "difference": -4125.00,
        "difference_pct": 48.5,
        "severity": "MEDIUM",
        "details": {
            "volume": 12.5,
            "faixa": "5-15 m³",
            "valor_m3": 350.00,
            "valor_minimo": 2000.00,
        },
    },
    {
        "rule_code": "PESO_REAL_VS_FATURADO",
        "rule_name": "Peso Real (XML) vs. Peso Faturado",
        "discrepancy_type": "PESO_REAL_VS_FATURADO",
        "expected_value": 15000.00,
        "actual_value": 18000.00,
        "difference": 3000.00,
        "difference_pct": 20.0,
        "severity": "HIGH",
        "details": {
            "peso_xml": 15000.0,
            "peso_faturado": 18000.0,
            "tolerancia_pct": 5.0,
        },
    },
    {
        "rule_code": "VALOR_MINIMO_FRETE",
        "rule_name": "Valor Mínimo de Frete (ANTT 5.839/2021)",
        "discrepancy_type": "VALOR_MINIMO_FRETE",
        "expected_value": 15792.00,
        "actual_value": 8500.00,
        "difference": 7292.00,
        "difference_pct": 85.8,
        "severity": "CRITICAL",
        "details": {
            "eixos": 6,
            "distancia_km": 430.0,
            "piso_por_eixo_km": 4.25,
            "peso": 18000.0,
        },
    },
    {
        "rule_code": "REDESPACHO_VALIDACAO",
        "rule_name": "Validação de Redespacho",
        "discrepancy_type": "REDESPACHO",
        "expected_value": 8500.00,
        "actual_value": 11000.00,
        "difference": 2500.00,
        "difference_pct": 29.4,
        "severity": "HIGH",
        "details": {
            "total_redespacho": 2500.0,
            "frete_principal": 8500.0,
            "quantidade_ctes": 1,
        },
    },
    {
        "rule_code": "PEDAGIO_CONFERENCIA",
        "rule_name": "Conferência de Pedágio",
        "discrepancy_type": "TOLL_PLAZA",
        "expected_value": 78.10,
        "actual_value": 83.70,
        "difference": 5.60,
        "difference_pct": 7.2,
        "severity": "MEDIUM",
        "details": {
            "pedagios_documento": [
                {"praca": "Pedágio SP-070", "eixos": 6, "valor": 45.50},
                {"praca": "Pedágio BR-101", "eixos": 6, "valor": 38.20},
            ],
            "pedagios_tabela": [
                {"praca": "Pedágio SP-070", "eixos": 6, "valor": 42.30},
                {"praca": "Pedágio BR-101", "eixos": 6, "valor": 35.80},
            ],
        },
    },
    {
        "rule_code": "AD_VALOREM",
        "rule_name": "Ad Valorem (Seguro sobre Valor)",
        "discrepancy_type": "AD_VALOREM",
        "expected_value": 500.00,
        "actual_value": 600.00,
        "difference": 100.00,
        "difference_pct": 20.0,
        "severity": "MEDIUM",
        "details": {"valor_mercadoria": 150000.0, "aliquota": 0.40, "teto": 500.0},
    },
    {
        "rule_code": "GRIS",
        "rule_name": "GRIS - Gerenciamento de Risco",
        "discrepancy_type": "GRIS",
        "expected_value": 180.00,
        "actual_value": 180.00,
        "difference": 0.00,
        "difference_pct": 0.0,
        "severity": "MEDIUM",
        "details": {"valor_mercadoria": 150000.0, "aliquota": 0.12, "teto": 200.0},
    },
]

CONTRACT = {
    "id": "contract-demo-001",
    "number": "CTR-2024-001",
    "success_fee_pct": 20.0,
}

CARRIER = {
    "id": "carrier-demo-001",
    "name": "Transportes Rápidos Ltda",
    "trade_name": "TransRápido",
}

DOCUMENT = {
    "numero": "12345",
    "serie": "1",
    "chave_acesso": "35240112345678901234550010000000011234567890",
    "uf_inicio": "SP",
    "uf_fim": "RJ",
    "valor_total": 150000.00,
    "freight_value": 8500.00,
    "peso_bruto": 15000.00,
    "weight": 18000.00,
    "volume": 12.5,
    "ncm": "22030000",
}

# Filtrar apenas divergências positivas (a recuperar)
positive_discs = [d for d in DEMO_RESULTS if d["difference"] > 0]
TOTAL_RECOVERABLE = sum(d["difference"] for d in positive_discs)
SUCCESS_FEE = round(TOTAL_RECOVERABLE * CONTRACT["success_fee_pct"] / 100, 2)
NET_RECOVERY = round(TOTAL_RECOVERABLE - SUCCESS_FEE, 2)

# Agrupar para relatórios
type_map = {}
for d in DEMO_RESULTS:
    t = d["discrepancy_type"]
    if t not in type_map:
        type_map[t] = {"type": t, "count": 0, "value": 0}
    type_map[t]["count"] += 1
    if d["difference"] > 0:
        type_map[t]["value"] += d["difference"]

TOP_CARRIERS = [
    {
        "name": CARRIER["name"],
        "count": len(DEMO_RESULTS),
        "value": TOTAL_RECOVERABLE,
    }
]

TOP_DISCREPANCY_TYPES = list(type_map.values())


def render_template(template_name, context):
    """Renderiza template Jinja2 simples (sem autoescape complexo)"""
    template_path = TEMPLATES_DIR / f"{template_name}.html"
    if not template_path.exists():
        return None

    content = template_path.read_text(encoding="utf-8")

    # Substituição simples de variáveis {{ var }}
    import re

    def replace_var(match):
        var_path = match.group(1).strip()
        try:
            # Navegar no context: obj.attr ou obj['key']
            value = context
            for part in var_path.split("."):
                if "[" in part and "]" in part:
                    key = part[part.index("[") + 1 : part.index("]")]
                    key = key.strip("'\"")
                    value = value.get(key, "")
                elif "|" in part:
                    # filtro - ignorar por simplicidade
                    var_name = part.split("|")[0].strip()
                    value = value.get(var_name, "")
                else:
                    value = value.get(part, "")
            if isinstance(value, float):
                return f"{value:,.2f}"
            return str(value)
        except:
            return f"{{{{{var_path}}}}}"

    content = re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace_var, content)

    # Remover blocos {% if %}...{% endif %} simples (manter conteúdo)
    content = re.sub(
        r"\{%\s*if\s+[^%]+\s*%\}(.*?)\{%\s*endif\s*%\}", r"\1", content, flags=re.DOTALL
    )
    content = re.sub(
        r"\{%\s*for\s+[^%]+\s*%\}(.*?)\{%\s*endfor\s*%\}", r"\1", content, flags=re.DOTALL
    )

    return content


def main():


    base_context = {
        "client_name": "Empresa Demo Ltda",
        "to_name": "João Silva",
        "dashboard_url": "https://demo.averta.com.br/dashboard",
        "logo_url": "https://averta.com.br/logo.png",
        "unsubscribe_url": "https://demo.averta.com.br/unsubscribe",
        "support_email": "suporte@averta.com",
        "carrier_name": CARRIER["name"],
        "document_number": DOCUMENT["numero"],
        "contract_number": CONTRACT["number"],
        "total_value": TOTAL_RECOVERABLE,
        "discrepancies": DEMO_RESULTS,
        "total_discrepancies": len(DEMO_RESULTS),
        "top_carriers": TOP_CARRIERS,
        "top_discrepancy_types": TOP_DISCREPANCY_TYPES,
        "period": "15/01/2024 a 21/01/2024",
        "documents_audited": 47,
        "discrepancies_found": len(DEMO_RESULTS),
        "total_recoverable": TOTAL_RECOVERABLE,
        "success_rate": 78,
        "fee_percentage": CONTRACT["success_fee_pct"],
    }

    templates_to_render = [
        (
            "discrepancy_alert",
            {
                **base_context,
                "document_number": DOCUMENT["numero"],
            },
        ),
        (
            "contest_created",
            {
                **base_context,
                "contest_number": "CTS-2024-000142",
                "contest_url": "https://demo.averta.com.br/contests/CTS-2024-000142",
            },
        ),
        ("weekly_report", base_context),
        (
            "contract_expiring",
            {
                **base_context,
                "contract_number": CONTRACT["number"],
                "carrier_name": CARRIER["name"],
                "days_until_expiry": 15,
                "contract_url": "https://demo.averta.com.br/contracts/CTR-2024-001",
            },
        ),
        (
            "payment_received",
            {
                **base_context,
                "contest_number": "CTS-2024-000142",
                "amount": TOTAL_RECOVERABLE,
                "success_fee": SUCCESS_FEE,
                "net_amount": NET_RECOVERY,
            },
        ),
        (
            "welcome",
            {
                **base_context,
                "login_url": "https://demo.averta.com.br/login",
                "temp_password": "TempPass2024!",
            },
        ),
        (
            "password_reset",
            {
                **base_context,
                "reset_url": "https://demo.averta.com.br/reset-password?token=demo123",
                "expires_hours": 24,
            },
        ),
    ]

    rendered = []
    for template_name, context in templates_to_render:
        html = render_template(template_name, context)
        if html:
            output_file = OUTPUT_DIR / f"{template_name}_demo.html"
            output_file.write_text(html, encoding="utf-8")
            rendered.append(str(output_file))
        else:
            pass

    # Salvar resumo JSON
    summary = {
        "audit_summary": {
            "document": {
                "number": DOCUMENT["numero"],
                "serie": DOCUMENT["serie"],
                "chave_acesso": DOCUMENT["chave_acesso"],
                "uf_origem": DOCUMENT["uf_inicio"],
                "uf_destino": DOCUMENT["uf_fim"],
                "valor_mercadoria": DOCUMENT["valor_total"],
                "frete_cobrado": DOCUMENT["freight_value"],
                "peso_xml": DOCUMENT["peso_bruto"],
                "peso_faturado": DOCUMENT["weight"],
                "volume": DOCUMENT["volume"],
                "ncm": DOCUMENT["ncm"],
            },
            "contract": CONTRACT,
            "carrier": CARRIER,
            "total_discrepancies": len(DEMO_RESULTS),
            "total_recoverable": TOTAL_RECOVERABLE,
            "success_fee_pct": CONTRACT["success_fee_pct"],
            "success_fee_value": SUCCESS_FEE,
            "net_recovery": NET_RECOVERY,
        },
        "discrepancies": DEMO_RESULTS,
    }

    summary_file = OUTPUT_DIR / "audit_summary_demo.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")



if __name__ == "__main__":
    main()
