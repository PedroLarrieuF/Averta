#!/usr/bin/env python
"""Demo Script - Gera emails preenchidos com valores reais calculados pelas rules"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.services.rules_engine_v2 import RuleContext, create_engine_v2


async def run_demo_audit():
    """Executa auditoria simulada com dados realistas"""

    # Dados de um CT-e realista: SP -> RJ, 15 ton, cerveja (ST), frete subfaturado
    document = {
        # Identificação
        "chave_acesso": "35240112345678901234550010000000011234567890",
        "numero": "12345",
        "serie": "1",
        "modelo": "57",
        "data_emissao": "2024-01-15T10:30:00",
        # Partes
        "uf_inicio": "SP",
        "uf_fim": "RJ",
        "cep_origem": "04547000",  # SP Capital
        "cep_destino": "20040000",  # RJ Centro
        # Valores
        "valor_total": 150000.00,  # Valor da mercadoria
        "freight_value": 8500.00,  # Frete cobrado (subfaturado)
        "v_frete": 8500.00,
        # ICMS
        "icms": {
            "v_bc": 150000.00,
            "v_icms": 5250.00,  # ICMS cobrado (errado - deveria ser DIFAL)
            "cst": "10",
            "v_bc_st": 150000.00,
            "v_icms_st": 25000.00,  # ST cobrado (errado)
        },
        # Produto
        "ncm": "22030000",  # Cerveja
        "cfop": "6102",
        # Peso/Volume
        "peso_bruto": 15000.00,  # 15 ton (XML)
        "peso_liquido": 14500.00,
        "weight": 18000.00,  # Peso faturado (20% a mais!)
        "volume": 12.5,  # 12.5 m³
        # Componentes do frete
        "components": {
            "v_advalorem": 600.00,  # Ad Valorem cobrado
            "v_gris": 180.00,  # GRIS cobrado
        },
        # Modal rodoviário
        "modal_rodoviario": {
            "veiculo_eixos": 6,
            "veiculo_placa": "ABC1D23",
            "veiculo_uf": "SP",
            "pedagio": [
                {"praca": "Pedágio SP-070", "eixos": 6, "valor": 45.50},
                {"praca": "Pedágio BR-101", "eixos": 6, "valor": 38.20},
            ],
        },
        # Distância
        "distancia_km": 430.0,
        # Redespacho
        "has_redespacho": True,
        "redespacho_details": [
            {"cte": "35240198765432109876550010000000019876543210", "valor": 2500.00},
        ],
        # Tipo carga
        "tipo_carga": "G",  # Geral
        "modalidade": "R",  # Rodoviário
    }

    # Contrato simulado
    contract = {
        "id": "contract-demo-001",
        "number": "CTR-2024-001",
        "success_fee_pct": 20.0,
        "freightTableId": "table-demo-001",
    }

    # Tabela de frete simulada (valores contratuais)
    freight_table = {
        "id": "table-demo-001",
        "name": "Tabela SP-RJ Cerveja 2024",
        "version": "1.0",
        "rules": {
            # DIFAL SP->RJ
            "difal": [
                {
                    "uf_origem": "SP",
                    "uf_destino": "RJ",
                    "aliquota_difal": 5.0,
                    "aliquota_fcp": 2.0,
                    "base_calculo": "valor_operacao",
                }
            ],
            # ICMS ST Cerveja RJ
            "icms_st": [
                {
                    "ncm": "22030000",
                    "uf_origem": "*",
                    "uf_destino": "RJ",
                    "aliquota_st": 20.0,
                    "mva_ajustado": 45.0,
                    "descricao": "Cerveja - ST RJ",
                }
            ],
            # Faixas peso
            "faixas_peso": [
                {
                    "peso_inicial": 0,
                    "peso_final": 5000,
                    "valor_kg": 0.65,
                    "valor_minimo": 800.00,
                    "descricao": "Até 5 ton",
                },
                {
                    "peso_inicial": 5001,
                    "peso_final": 15000,
                    "valor_kg": 0.55,
                    "valor_minimo": 3500.00,
                    "descricao": "5-15 ton",
                },
                {
                    "peso_inicial": 15001,
                    "peso_final": 30000,
                    "valor_kg": 0.48,
                    "valor_minimo": 7000.00,
                    "descricao": "15-30 ton",
                },
            ],
            # Faixas cubagem
            "faixas_cubagem": [
                {
                    "cubagem_inicial": 0,
                    "cubagem_final": 5,
                    "valor_m3": 400.00,
                    "valor_minimo": 1000.00,
                    "descricao": "Até 5 m³",
                },
                {
                    "cubagem_inicial": 5.01,
                    "cubagem_final": 15,
                    "valor_m3": 350.00,
                    "valor_minimo": 2000.00,
                    "descricao": "5-15 m³",
                },
                {
                    "cubagem_inicial": 15.01,
                    "cubagem_final": 30,
                    "valor_m3": 300.00,
                    "valor_minimo": 4000.00,
                    "descricao": "15-30 m³",
                },
            ],
            # Pedágios tabela
            "pedagios": [
                {"praca": "Pedágio SP-070", "eixos": 6, "valor": 42.30},
                {"praca": "Pedágio BR-101", "eixos": 6, "valor": 35.80},
            ],
            # Ad Valorem
            "advalorem": {"aliquota": 0.40, "teto": 500.00},
            # GRIS
            "gris": {"aliquota": 0.12, "teto": 200.00},
            # Sicoban (será usado do JSON)
            "sicoban": [],
        },
    }

    # Carrier
    carrier = {
        "id": "carrier-demo-001",
        "name": "Transportes Rápidos Ltda",
        "trade_name": "TransRápido",
        "cnpj": "12.345.678/0001-90",
    }

    # Contexto para o engine
    context = RuleContext(
        document=document,
        contract=contract,
        freight_table=freight_table["rules"],
        carrier=carrier,
        metadata={
            "company_id": "company-demo-001",
            "document_id": "doc-demo-001",
        },
    )

    # Criar engine e executar
    engine = await create_engine_v2()
    results = await engine.evaluate_all(context)

    return results, document, contract, carrier, freight_table


def render_email_templates(results, document, contract, carrier, freight_table):
    """Renderiza todos os templates de email com dados reais"""

    template_dir = Path(__file__).parent.parent / "app" / "templates" / "emails"
    output_dir = Path(__file__).parent.parent / "demo_emails"
    output_dir.mkdir(exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Preparar dados comuns
    discrepancies_data = []
    total_recoverable = 0

    for r in results:
        disc = {
            "rule_code": r.rule_code,
            "rule_name": r.rule_name,
            "discrepancy_type": r.discrepancy_type.value,
            "expected_value": r.expected_value,
            "actual_value": r.actual_value,
            "difference": r.difference,
            "difference_pct": r.difference_pct,
            "severity": r.severity,
            "details": r.details,
        }
        discrepancies_data.append(disc)
        if r.difference and r.difference > 0:
            total_recoverable += r.difference

    # Agrupar por transportador
    top_carriers = [
        {
            "name": carrier["name"],
            "count": len(results),
            "value": total_recoverable,
        }
    ]

    # Agrupar por tipo
    type_map = {}
    for r in results:
        t = r.discrepancy_type.value
        if t not in type_map:
            type_map[t] = {"type": t, "count": 0, "value": 0}
        type_map[t]["count"] += 1
        if r.difference and r.difference > 0:
            type_map[t]["value"] += r.difference
    top_discrepancy_types = list(type_map.values())

    base_context = {
        "client_name": "Empresa Demo Ltda",
        "to_name": "João Silva",
        "dashboard_url": "https://demo.averta.com.br/dashboard",
        "logo_url": "https://averta.com.br/logo.png",
        "unsubscribe_url": "https://demo.averta.com.br/unsubscribe",
        "support_email": "suporte@averta.com",
        "carrier_name": carrier["name"],
        "document_number": document["numero"],
        "contract_number": contract["number"],
        "total_value": total_recoverable,
        "discrepancies": discrepancies_data,
        "total_discrepancies": len(results),
        "top_carriers": top_carriers,
        "top_discrepancy_types": top_discrepancy_types,
        "period": "15/01/2024 a 21/01/2024",
        "documents_audited": 47,
        "discrepancies_found": len(results),
        "total_recoverable": total_recoverable,
        "success_rate": 78,
        "fee_percentage": contract["success_fee_pct"],
    }

    # Templates para renderizar
    templates_to_render = [
        (
            "discrepancy_alert",
            {
                **base_context,
                "document_number": document["numero"],
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
        (
            "weekly_report",
            {
                **base_context,
            },
        ),
        (
            "contract_expiring",
            {
                **base_context,
                "contract_number": contract["number"],
                "carrier_name": carrier["name"],
                "days_until_expiry": 15,
                "contract_url": "https://demo.averta.com.br/contracts/CTR-2024-001",
            },
        ),
        (
            "payment_received",
            {
                **base_context,
                "contest_number": "CTS-2024-000142",
                "amount": total_recoverable,
                "success_fee": round(total_recoverable * contract["success_fee_pct"] / 100, 2),
                "net_amount": round(total_recoverable * (1 - contract["success_fee_pct"] / 100), 2),
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

    rendered_files = []

    for template_name, context in templates_to_render:
        try:
            html_template = env.get_template(f"{template_name}.html")
            html_content = html_template.render(**context)

            output_file = output_dir / f"{template_name}_demo.html"
            output_file.write_text(html_content, encoding="utf-8")
            rendered_files.append(str(output_file))
            print(f"✅ Gerado: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao renderizar {template_name}: {e}")

    # Também gerar um relatório resumo em JSON
    import json

    summary = {
        "audit_summary": {
            "document": {
                "number": document["numero"],
                "serie": document["serie"],
                "chave_acesso": document["chave_acesso"],
                "uf_origem": document["uf_inicio"],
                "uf_destino": document["uf_fim"],
                "valor_mercadoria": document["valor_total"],
                "frete_cobrado": document["freight_value"],
                "peso_xml": document["peso_bruto"],
                "peso_faturado": document["weight"],
                "volume": document["volume"],
                "ncm": document["ncm"],
            },
            "contract": contract,
            "carrier": carrier,
            "total_discrepancies": len(results),
            "total_recoverable": round(total_recoverable, 2),
            "success_fee_pct": contract["success_fee_pct"],
            "success_fee_value": round(total_recoverable * contract["success_fee_pct"] / 100, 2),
            "net_recovery": round(total_recoverable * (1 - contract["success_fee_pct"] / 100), 2),
        },
        "discrepancies": discrepancies_data,
    }

    summary_file = output_dir / "audit_summary_demo.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Resumo JSON: {summary_file}")

    return rendered_files, output_dir


async def main():
    print("=" * 60)
    print("AVERTA SAAS - DEMO EMAIL GENERATOR")
    print("=" * 60)
    print()

    print("🔍 Executando auditoria simulada...")
    results, document, contract, carrier, freight_table = await run_demo_audit()

    print(f"\n📊 Resultados: {len(results)} divergências encontradas")
    for r in results:
        print(f"  - {r.rule_code}: R$ {r.difference:,.2f} ({r.severity})")

    total = sum(r.difference for r in results if r.difference and r.difference > 0)
    print(f"\n💰 Total a recuperar: R$ {total:,.2f}")
    print(f"💰 Success Fee (20%): R$ {total * 0.20:,.2f}")
    print(f"💰 Líquido para cliente: R$ {total * 0.80:,.2f}")

    print("\n📧 Renderizando templates de email...")
    rendered_files, output_dir = render_email_templates(
        results, document, contract, carrier, freight_table
    )

    print(f"\n✅ Demo concluído! Arquivos em: {output_dir}")
    print("\nArquivos gerados:")
    for f in rendered_files:
        print(f"  - {f}")
    print(f"  - {output_dir / 'audit_summary_demo.json'}")
    print("\n💡 Abra os .html no navegador para apresentar ao cliente")


if __name__ == "__main__":
    asyncio.run(main())
