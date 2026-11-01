"""XML Parser for CT-e and NF-e - Extracts freight audit relevant data"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
import xmltodict
from lxml import etree
import structlog

logger = structlog.get_logger()


# Namespace mappings
NS_CTE = {"cte": "http://www.portalfiscal.inf.br/cte"}
NS_NFE = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


def parse_cte_xml(xml_content: str | bytes) -> dict:
    """Parse CT-e XML and extract structured data for audit"""
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8")

    try:
        # Parse with xmltodict for easy dict access
        doc = xmltodict.parse(xml_content)
        cte = doc.get("cteProc", {}).get("CTe", {}) or doc.get("CTe", {})
        inf_cte = cte.get("infCte", {})

        return _extract_cte_data(inf_cte, cte)
    except Exception as e:
        logger.exception("cte_parse_error", error=str(e))
        raise ValueError(f"Failed to parse CT-e XML: {e}")


def parse_nfe_xml(xml_content: str | bytes) -> dict:
    """Parse NF-e XML and extract structured data for audit"""
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8")

    try:
        doc = xmltodict.parse(xml_content)
        nfe = doc.get("nfeProc", {}).get("NFe", {}) or doc.get("NFe", {})
        inf_nfe = nfe.get("infNFe", {})

        return _extract_nfe_data(inf_nfe, nfe)
    except Exception as e:
        logger.exception("nfe_parse_error", error=str(e))
        raise ValueError(f"Failed to parse NF-e XML: {e}")


def _extract_cte_data(inf_cte: dict, cte: dict) -> dict:
    """Extract relevant fields from CT-e infCte"""
    ide = inf_cte.get("ide", {})
    emit = inf_cte.get("emit", {})
    rem = inf_cte.get("rem", {})
    dest = inf_cte.get("dest", {})
    v_prest = inf_cte.get("vPrest", {})
    imp = inf_cte.get("imp", {})
    inf_cte_norm = inf_cte.get("infCteNorm", {})
    inf_modal = inf_cte_norm.get("infModal", {}) if inf_cte_norm else {}
    rodo = inf_modal.get("rodo", {}) if inf_modal else {}
    veic = rodo.get("veic", [{}])[0] if rodo.get("veic") else {}
    moto = rodo.get("moto", {}) if rodo else {}

    # Values
    v_prest_comp = v_prest.get("Comp", [])
    v_tot = _get_comp_value(v_prest_comp, "vTPrest")
    v_frete = _get_comp_value(v_prest_comp, "vFrete")
    v_peso = _get_comp_value(v_prest_comp, "vPeso")
    v_cubagem = _get_comp_value(v_prest_comp, "vCubagem")
    v_pedagio = _get_comp_value(v_prest_comp, "vPedagio")
    v_advalorem = _get_comp_value(v_prest_comp, "vAdValorem")
    v_gris = _get_comp_value(v_prest_comp, "vGRIS")
    v_icms = _get_comp_value(v_prest_comp, "vICMS")
    v_outros = _get_comp_value(v_prest_comp, "vOutros")

    # ICMS details
    icms = imp.get("ICMS", {}) if imp else {}
    icms_valor = None
    for key in ["ICMS00", "ICMS20", "ICMS45", "ICMS60", "ICMS90", "ICMSOutraUF"]:
        if key in icms:
            icms_valor = _safe_decimal(icms[key].get("vICMS"))
            break

    # Redespacho
    redespacho = inf_cte_norm.get("infDoc", {}).get("infCTeRedesp", []) if inf_cte_norm else []
    has_redespacho = len(redespacho) > 0

    # Pedágio
    pedagio = rodo.get("pedagio", []) if rodo else {}

    return {
        # Identification
        "access_key": inf_cte.get("@Id", "").replace("CTe", ""),
        "chave_acesso": inf_cte.get("@Id", "").replace("CTe", ""),
        "numero": ide.get("nCT"),
        "serie": ide.get("serie"),
        "modelo": ide.get("mod"),
        "natureza_operacao": ide.get("natOp"),
        "data_emissao": _parse_date(ide.get("dhEmi")),
        "data_saida": _parse_date(ide.get("dhSaiEnt")),
        "uf_inicio": ide.get("UFIni"),
        "uf_fim": ide.get("UFFim"),
        "municipio_inicio": ide.get("xMunIni"),
        "municipio_fim": ide.get("xMunFim"),
        "tipo_transporte": ide.get("tpTransp"),
        "modalidade": ide.get("modFrete"),

        # Emitente (Transportadora)
        "emit_cnpj": emit.get("CNPJ"),
        "emit_ie": emit.get("IE"),
        "emit_nome": emit.get("xNome"),
        "emit_fantasia": emit.get("xFant"),
        "emit_endereco": _format_address(emit.get("enderEmit", {})),

        # Remetente
        "rem_cnpj": rem.get("CNPJ") or rem.get("CPF"),
        "rem_ie": rem.get("IE"),
        "rem_nome": rem.get("xNome"),
        "rem_endereco": _format_address(rem.get("enderReme", {})),

        # Destinatário
        "dest_cnpj": dest.get("CNPJ") or dest.get("CPF"),
        "dest_ie": dest.get("IE"),
        "dest_nome": dest.get("xNome"),
        "dest_endereco": _format_address(dest.get("enderDest", {})),

        # Valores principais
        "total_value": _safe_float(v_tot),
        "freight_value": _safe_float(v_frete),
        "icms_value": _safe_float(icms_valor),
        "weight": _safe_float(v_peso),
        "volume": _safe_float(v_cubagem),

        # Componentes do frete
        "components": {
            "v_frete": _safe_float(v_frete),
            "v_peso": _safe_float(v_peso),
            "v_cubagem": _safe_float(v_cubagem),
            "v_pedagio": _safe_float(v_pedagio),
            "v_advalorem": _safe_float(v_advalorem),
            "v_gris": _safe_float(v_gris),
            "v_icms": _safe_float(v_icms),
            "v_outros": _safe_float(v_outros),
        },

        # ICMS
        "icms": {
            "v_icms": _safe_float(icms_valor),
            "v_bc": _safe_float(_get_icms_bc(icms)),
            "p_icms": _safe_float(_get_icms_p(icms)),
            "cst": _get_icms_cst(icms),
        },

        # Modal rodoviário
        "modal_rodoviario": {
            "rntrc": moto.get("RNTRC"),
            "veiculo_placa": veic.get("placa"),
            "veiculo_uf": veic.get("UF"),
            "veiculo_rntc": veic.get("RNTC"),
            "veiculo_tara": _safe_float(veic.get("tara")),
            "veiculo_cap_kg": _safe_float(veic.get("capKG")),
            "veiculo_cap_m3": _safe_float(veic.get("capM3")),
            "tipo_veiculo": veic.get("tpVeic"),
            "tipo_rodado": veic.get("tpRod"),
            "tipo_carroceria": veic.get("tpCar"),
            "pedagio": _extract_pedagio(pedagio),
        },

        # Redespacho
        "has_redespacho": has_redespacho,
        "redespacho_details": [
            {
                "chave_cte": r.get("chCTe"),
                "cnpj_transportadora": r.get("CNPJ"),
                "valor": _safe_float(r.get("vCTe")),
            }
            for r in redespacho
        ] if has_redespacho else [],

        # Raw data for debugging
        "raw_ide": ide,
        "raw_vprest": v_prest,
    }


def _extract_nfe_data(inf_nfe: dict, nfe: dict) -> dict:
    """Extract relevant fields from NF-e infNFe"""
    ide = inf_nfe.get("ide", {})
    emit = inf_nfe.get("emit", {})
    dest = inf_nfe.get("dest", {})
    total = inf_nfe.get("total", {}).get("ICMSTot", {})
    transp = inf_nfe.get("transp", {})

    return {
        "access_key": inf_nfe.get("@Id", "").replace("NFe", ""),
        "chave_acesso": inf_nfe.get("@Id", "").replace("NFe", ""),
        "numero": ide.get("nNF"),
        "serie": ide.get("serie"),
        "modelo": ide.get("mod"),
        "natureza_operacao": ide.get("natOp"),
        "data_emissao": _parse_date(ide.get("dhEmi")),
        "data_saida": _parse_date(ide.get("dhSaiEnt")),
        "uf_emit": emit.get("enderEmit", {}).get("UF"),
        "uf_dest": dest.get("enderDest", {}).get("UF"),
        "municipio_emit": emit.get("enderEmit", {}).get("xMun"),
        "municipio_dest": dest.get("enderDest", {}).get("xMun"),

        "emit_cnpj": emit.get("CNPJ"),
        "emit_nome": emit.get("xNome"),
        "dest_cnpj": dest.get("CNPJ") or dest.get("CPF"),
        "dest_nome": dest.get("xNome"),

        "total_value": _safe_float(total.get("vNF")),
        "produtos_value": _safe_float(total.get("vProd")),
        "freight_value": _safe_float(total.get("vFrete")),
        "icms_value": _safe_float(total.get("vICMS")),
        "ipi_value": _safe_float(total.get("vIPI")),
        "pis_value": _safe_float(total.get("vPIS")),
        "cofins_value": _safe_float(total.get("vCOFINS")),

        "peso_liquido": _safe_float(total.get("vPesoL")),
        "peso_bruto": _safe_float(total.get("vPesoB")),

        "transportadora": {
            "cnpj": transp.get("transporta", {}).get("CNPJ"),
            "nome": transp.get("transporta", {}).get("xNome"),
            "ie": transp.get("transporta", {}).get("IE"),
            "uf": transp.get("transporta", {}).get("UF"),
            "modalidade_frete": transp.get("modFrete"),
        },

        "raw_ide": ide,
        "raw_total": total,
    }


def _extract_pedagio(pedagio_data) -> list:
    """Extract toll plaza data"""
    if not pedagio_data:
        return []
    if isinstance(pedagio_data, dict):
        pedagio_data = [pedagio_data]
    return [
        {
            "praça": p.get("xPraca"),
            "valor": _safe_float(p.get("vPedagio")),
            "eixos": p.get("eixos"),
        }
        for p in pedagio_data
    ]


def _get_comp_value(comp_list: list, name: str) -> Optional[str]:
    """Get component value by name from vPrest/Comp list"""
    if isinstance(comp_list, dict):
        comp_list = [comp_list]
    for comp in comp_list:
        if comp.get("xNome") == name:
            return comp.get("vComp")
    return None


def _get_icms_bc(icms: dict) -> Optional[str]:
    for key in ["ICMS00", "ICMS20", "ICMS45", "ICMS60", "ICMS90", "ICMSOutraUF"]:
        if key in icms:
            return icms[key].get("vBC")
    return None


def _get_icms_p(icms: dict) -> Optional[str]:
    for key in ["ICMS00", "ICMS20", "ICMS45", "ICMS60", "ICMS90", "ICMSOutraUF"]:
        if key in icms:
            return icms[key].get("pICMS")
    return None


def _get_icms_cst(icms: dict) -> Optional[str]:
    for key in ["ICMS00", "ICMS20", "ICMS45", "ICMS60", "ICMS90", "ICMSOutraUF"]:
        if key in icms:
            return icms[key].get("CST") or icms[key].get("CSOSN")
    return None


def _safe_decimal(val) -> Optional[Decimal]:
    try:
        return Decimal(str(val)) if val is not None else None
    except Exception:
        return None


def _safe_float(val) -> Optional[float]:
    d = _safe_decimal(val)
    return float(d) if d is not None else None


def _parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    try:
        # Handle various formats
        for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str[:len(fmt)], fmt).isoformat()
            except ValueError:
                continue
        return date_str
    except Exception:
        return None


def _format_address(end: dict) -> Optional[dict]:
    if not end:
        return None
    return {
        "logradouro": end.get("xLgr"),
        "numero": end.get("nro"),
        "complemento": end.get("xCpl"),
        "bairro": end.get("xBairro"),
        "municipio": end.get("xMun"),
        "uf": end.get("UF"),
        "cep": end.get("CEP"),
        "pais": end.get("cPais"),
    }