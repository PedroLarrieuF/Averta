"""XML Parser for CT-e and NF-e - Extracts freight audit relevant data using lxml.etree"""

from datetime import datetime
from typing import Any

import structlog
from lxml import etree

logger = structlog.get_logger()

# Namespace constants
NS_NFE = "http://www.portalfiscal.inf.br/nfe"
NS_CTE = "http://www.portalfiscal.inf.br/cte"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"

# Namespace map for XPath queries
NS_MAP = {
    "nfe": NS_NFE,
    "cte": NS_CTE,
    "ds": NS_DS,
}

# Register namespaces for output serialization
etree.register_namespace("nfe", NS_NFE)
etree.register_namespace("cte", NS_CTE)
etree.register_namespace("ds", NS_DS)


def parse_cte_xml(xml_content: str | bytes) -> dict[str, Any]:
    """Parse CT-e XML and extract structured data for audit using lxml.etree"""
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8")

    try:
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        root = etree.fromstring(xml_content.encode("utf-8"), parser)

        # Handle both cteProc and direct CTe
        cte_elem = root.find(".//cte:CTe", namespaces=NS_MAP)
        if cte_elem is None:
            cte_elem = root

        inf_cte = cte_elem.find("cte:infCte", namespaces=NS_MAP)
        if inf_cte is None:
            raise ValueError("infCte not found in CT-e XML")

        return _extract_cte_data_lxml(inf_cte, cte_elem)
    except etree.XMLSyntaxError as e:
        logger.exception("cte_parse_xml_syntax_error", error=str(e))
        raise ValueError(f"Invalid CT-e XML syntax: {e}") from e
    except Exception as e:
        logger.exception("cte_parse_error", error=str(e))
        raise ValueError(f"Failed to parse CT-e XML: {e}") from e


def parse_nfe_xml(xml_content: str | bytes) -> dict[str, Any]:
    """Parse NF-e XML and extract structured data for audit using lxml.etree"""
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8")

    try:
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        root = etree.fromstring(xml_content.encode("utf-8"), parser)

        # Handle both nfeProc and direct NFe
        nfe_elem = root.find(".//nfe:NFe", namespaces=NS_MAP)
        if nfe_elem is None:
            nfe_elem = root

        inf_nfe = nfe_elem.find("nfe:infNFe", namespaces=NS_MAP)
        if inf_nfe is None:
            raise ValueError("infNFe not found in NF-e XML")

        return _extract_nfe_data_lxml(inf_nfe, nfe_elem)
    except etree.XMLSyntaxError as e:
        logger.exception("nfe_parse_xml_syntax_error", error=str(e))
        raise ValueError(f"Invalid NF-e XML syntax: {e}") from e
    except Exception as e:
        logger.exception("nfe_parse_error", error=str(e))
        raise ValueError(f"Failed to parse NF-e XML: {e}") from e


def _extract_cte_data_lxml(inf_cte: etree._Element, cte_elem: etree._Element) -> dict[str, Any]:  # noqa: PLR0912, PLR0915
    """Extract relevant fields from CT-e infCte using lxml XPath"""

    # Helper functions
    def get_text(elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP) -> str | None:
        result = elem.find(xpath, namespaces=ns)
        return result.text if result is not None else None

    def get_attr(elem: etree._Element, attr: str) -> str | None:
        return elem.get(attr)  # type: ignore[no-any-return]

    def get_float(elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP) -> float | None:
        val = get_text(elem, xpath, ns)
        if val is None:
            return None
        try:
            return float(val)
        except ValueError:
            return None

    def get_int(elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP) -> int | None:
        val = get_text(elem, xpath, ns)
        if val is None:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def find_all(
        elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP
    ) -> list[etree._Element]:
        return elem.findall(xpath, ns)  # type: ignore[no-any-return]

    ide = inf_cte.find("cte:ide", namespaces=NS_MAP)
    emit = inf_cte.find("cte:emit", namespaces=NS_MAP)
    rem = inf_cte.find("cte:rem", namespaces=NS_MAP)
    dest = inf_cte.find("cte:dest", namespaces=NS_MAP)
    v_prest = inf_cte.find("cte:vPrest", namespaces=NS_MAP)
    imp = inf_cte.find("cte:imp", namespaces=NS_MAP)
    inf_cte_norm = inf_cte.find("cte:infCteNorm", namespaces=NS_MAP)

    inf_modal = (
        inf_cte_norm.find("cte:infModal", namespaces=NS_MAP) if inf_cte_norm is not None else None
    )
    rodo = inf_modal.find("cte:rodo", namespaces=NS_MAP) if inf_modal is not None else None
    veic_list = rodo.findall("cte:veic", namespaces=NS_MAP) if rodo is not None else []
    veic = veic_list[0] if veic_list else None
    moto = rodo.find("cte:moto", namespaces=NS_MAP) if rodo is not None else None

    # Extract values from vPrest/Comp
    comp_list = find_all(v_prest, "cte:Comp", NS_MAP) if v_prest is not None else []

    def get_comp_value(name: str) -> float | None:
        for comp in comp_list:
            xnome = comp.find("cte:xNome", namespaces=NS_MAP)
            if xnome is not None and xnome.text == name:
                vcomp = comp.find("cte:vComp", namespaces=NS_MAP)
                if vcomp is not None:
                    try:
                        return float(vcomp.text)
                    except ValueError:
                        pass
        return None

    v_tot = get_comp_value("vTPrest")
    v_frete = get_comp_value("vFrete")
    v_peso = get_comp_value("vPeso")
    v_cubagem = get_comp_value("vCubagem")
    v_pedagio = get_comp_value("vPedagio")
    v_advalorem = get_comp_value("vAdValorem")
    v_gris = get_comp_value("vGRIS")
    v_icms_comp = get_comp_value("vICMS")
    v_outros = get_comp_value("vOutros")

    # ICMS details
    icms_valor = None
    icms_bc = None
    icms_p = None
    icms_cst = None

    if imp is not None:
        icms_elem = imp.find("cte:ICMS", namespaces=NS_MAP)
        if icms_elem is not None:
            for key in ["ICMS00", "ICMS20", "ICMS45", "ICMS60", "ICMS90", "ICMSOutraUF"]:
                icms_type = icms_elem.find(f"cte:{key}", namespaces=NS_MAP)
                if icms_type is not None:
                    v_icms_elem = icms_type.find("cte:vICMS", namespaces=NS_MAP)
                    if v_icms_elem is not None:
                        try:
                            icms_valor = float(v_icms_elem.text)
                        except ValueError:
                            pass
                    v_bc_elem = icms_type.find("cte:vBC", namespaces=NS_MAP)
                    if v_bc_elem is not None:
                        try:
                            icms_bc = float(v_bc_elem.text)
                        except ValueError:
                            pass
                    p_icms_elem = icms_type.find("cte:pICMS", namespaces=NS_MAP)
                    if p_icms_elem is not None:
                        try:
                            icms_p = float(p_icms_elem.text)
                        except ValueError:
                            pass
                    cst_elem = icms_type.find("cte:CST", namespaces=NS_MAP)
                    if cst_elem is None:
                        cst_elem = icms_type.find("cte:CSOSN", namespaces=NS_MAP)
                    if cst_elem is not None:
                        icms_cst = cst_elem.text
                    break

    # Redespacho
    redespacho_list = []
    has_redespacho = False
    if inf_cte_norm is not None:
        inf_doc = inf_cte_norm.find("cte:infDoc", namespaces=NS_MAP)
        if inf_doc is not None:
            redespacho_elems = inf_doc.findall("cte:infCTeRedesp", namespaces=NS_MAP)
            has_redespacho = len(redespacho_elems) > 0
            for r in redespacho_elems:
                redespacho_list.append(
                    {
                        "chave_cte": get_text(r, "cte:chCTe"),
                        "cnpj_transportadora": get_text(r, "cte:CNPJ"),
                        "valor": get_float(r, "cte:vCTe"),
                    }
                )

    # Pedágio
    pedagio_list = []
    if rodo is not None:
        pedagio_elems = rodo.findall("cte:pedagio", namespaces=NS_MAP)
        for p in pedagio_elems:
            pedagio_list.append(
                {
                    "praça": get_text(p, "cte:xPraca"),
                    "valor": get_float(p, "cte:vPedagio"),
                    "eixos": get_text(p, "cte:eixos"),
                }
            )

    # Access key from infCte/@Id
    access_key = get_attr(inf_cte, "Id")
    if access_key and access_key.startswith("CTe"):
        access_key = access_key[3:]

    return {
        "access_key": access_key or "",
        "chave_acesso": access_key or "",
        "numero": get_text(ide, "cte:nCT"),
        "serie": get_text(ide, "cte:serie"),
        "modelo": get_text(ide, "cte:mod"),
        "natureza_operacao": get_text(ide, "cte:natOp"),
        "data_emissao": _parse_date(get_text(ide, "cte:dhEmi")),
        "data_saida": _parse_date(get_text(ide, "cte:dhSaiEnt")),
        "uf_inicio": get_text(ide, "cte:UFIni"),
        "uf_fim": get_text(ide, "cte:UFFim"),
        "municipio_inicio": get_text(ide, "cte:xMunIni"),
        "municipio_fim": get_text(ide, "cte:xMunFim"),
        "tipo_transporte": get_text(ide, "cte:tpTransp"),
        "modalidade": get_text(ide, "cte:modFrete"),
        "emit_cnpj": get_text(emit, "cte:CNPJ"),
        "emit_ie": get_text(emit, "cte:IE"),
        "emit_nome": get_text(emit, "cte:xNome"),
        "emit_fantasia": get_text(emit, "cte:xFant"),
        "emit_endereco": _format_address_lxml(emit, "cte:enderEmit"),
        "rem_cnpj": get_text(rem, "cte:CNPJ") or get_text(rem, "cte:CPF"),
        "rem_ie": get_text(rem, "cte:IE"),
        "rem_nome": get_text(rem, "cte:xNome"),
        "rem_endereco": _format_address_lxml(rem, "cte:enderReme"),
        "dest_cnpj": get_text(dest, "cte:CNPJ") or get_text(dest, "cte:CPF"),
        "dest_ie": get_text(dest, "cte:IE"),
        "dest_nome": get_text(dest, "cte:xNome"),
        "dest_endereco": _format_address_lxml(dest, "cte:enderDest"),
        "total_value": v_tot,
        "freight_value": v_frete,
        "icms_value": icms_valor,
        "weight": v_peso,
        "volume": v_cubagem,
        "components": {
            "v_frete": v_frete,
            "v_peso": v_peso,
            "v_cubagem": v_cubagem,
            "v_pedagio": v_pedagio,
            "v_advalorem": v_advalorem,
            "v_gris": v_gris,
            "v_icms": v_icms_comp,
            "v_outros": v_outros,
        },
        "icms": {
            "v_icms": icms_valor,
            "v_bc": icms_bc,
            "p_icms": icms_p,
            "cst": icms_cst,
        },
        "modal_rodoviario": {
            "rntrc": get_text(moto, "cte:RNTRC") if moto is not None else None,
            "veiculo_placa": get_text(veic, "cte:placa") if veic is not None else None,
            "veiculo_uf": get_text(veic, "cte:UF") if veic is not None else None,
            "veiculo_rntc": get_text(veic, "cte:RNTC") if veic is not None else None,
            "veiculo_tara": get_float(veic, "cte:tara") if veic is not None else None,
            "veiculo_cap_kg": get_float(veic, "cte:capKG") if veic is not None else None,
            "veiculo_cap_m3": get_float(veic, "cte:capM3") if veic is not None else None,
            "tipo_veiculo": get_text(veic, "cte:tpVeic") if veic is not None else None,
            "tipo_rodado": get_text(veic, "cte:tpRod") if veic is not None else None,
            "tipo_carroceria": get_text(veic, "cte:tpCar") if veic is not None else None,
            "pedagio": pedagio_list,
        },
        "has_redespacho": has_redespacho,
        "redespacho_details": redespacho_list,
        "raw_ide": _elem_to_dict(ide) if ide is not None else {},
        "raw_vprest": [
            {
                "xNome": c.find("cte:xNome", namespaces=NS_MAP).text
                if c.find("cte:xNome", namespaces=NS_MAP) is not None
                else None,
                "vComp": c.find("cte:vComp", namespaces=NS_MAP).text
                if c.find("cte:vComp", namespaces=NS_MAP) is not None
                else None,
            }
            for c in comp_list
        ],
    }


def _extract_nfe_data_lxml(inf_nfe: etree._Element, nfe_elem: etree._Element) -> dict[str, Any]:  # noqa: PLR0912, PLR0915
    """Extract relevant fields from NF-e infNFe using lxml XPath"""

    def get_text(elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP) -> str | None:
        result = elem.find(xpath, namespaces=ns)
        return result.text if result is not None else None

    def get_attr(elem: etree._Element, attr: str) -> str | None:
        return elem.get(attr)  # type: ignore[no-any-return]

    def get_float(elem: etree._Element, xpath: str, ns: dict[str, str] = NS_MAP) -> float | None:
        val = get_text(elem, xpath, ns)
        if val is None:
            return None
        try:
            return float(val)
        except ValueError:
            return None

    ide = inf_nfe.find("nfe:ide", namespaces=NS_MAP)
    emit = inf_nfe.find("nfe:emit", namespaces=NS_MAP)
    dest = inf_nfe.find("nfe:dest", namespaces=NS_MAP)
    total = inf_nfe.find("nfe:total/nfe:ICMSTot", namespaces=NS_MAP)
    transp = inf_nfe.find("nfe:transp", namespaces=NS_MAP)

    emit_ender = emit.find("nfe:enderEmit", namespaces=NS_MAP) if emit is not None else None
    dest_ender = dest.find("nfe:enderDest", namespaces=NS_MAP) if dest is not None else None
    transporta = transp.find("nfe:transporta", namespaces=NS_MAP) if transp is not None else None

    access_key = get_attr(inf_nfe, "Id")
    if access_key and access_key.startswith("NFe"):
        access_key = access_key[3:]

    return {
        "access_key": access_key or "",
        "chave_acesso": access_key or "",
        "numero": get_text(ide, "nfe:nNF"),
        "serie": get_text(ide, "nfe:serie"),
        "modelo": get_text(ide, "nfe:mod"),
        "natureza_operacao": get_text(ide, "nfe:natOp"),
        "data_emissao": _parse_date(get_text(ide, "nfe:dhEmi")),
        "data_saida": _parse_date(get_text(ide, "nfe:dhSaiEnt")),
        "uf_emit": get_text(emit_ender, "nfe:UF") if emit_ender is not None else None,
        "uf_dest": get_text(dest_ender, "nfe:UF") if dest_ender is not None else None,
        "municipio_emit": get_text(emit_ender, "nfe:xMun") if emit_ender is not None else None,
        "municipio_dest": get_text(dest_ender, "nfe:xMun") if dest_ender is not None else None,
        "emit_cnpj": get_text(emit, "nfe:CNPJ"),
        "emit_nome": get_text(emit, "nfe:xNome"),
        "dest_cnpj": get_text(dest, "nfe:CNPJ") or get_text(dest, "nfe:CPF"),
        "dest_nome": get_text(dest, "nfe:xNome"),
        "total_value": get_float(total, "nfe:vNF"),
        "produtos_value": get_float(total, "nfe:vProd"),
        "freight_value": get_float(total, "nfe:vFrete"),
        "icms_value": get_float(total, "nfe:vICMS"),
        "ipi_value": get_float(total, "nfe:vIPI"),
        "pis_value": get_float(total, "nfe:vPIS"),
        "cofins_value": get_float(total, "nfe:vCOFINS"),
        "peso_liquido": get_float(total, "nfe:vPesoL"),
        "peso_bruto": get_float(total, "nfe:vPesoB"),
        "transportadora": {
            "cnpj": get_text(transporta, "nfe:CNPJ"),
            "nome": get_text(transporta, "nfe:xNome"),
            "ie": get_text(transporta, "nfe:IE"),
            "uf": get_text(transporta, "nfe:UF"),
            "modalidade_frete": get_text(transp, "nfe:modFrete"),
        },
        "raw_ide": _elem_to_dict(ide) if ide is not None else {},
        "raw_total": _elem_to_dict(total) if total is not None else {},
    }


def _format_address_lxml(parent: etree._Element, xpath: str) -> dict[str, str | None] | None:
    """Format address from lxml element"""
    if parent is None:
        return None
    end = parent.find(xpath, namespaces=NS_MAP)
    if end is None:
        return None

    def get_text(elem: etree._Element, path: str) -> str | None:
        result = elem.find(path, namespaces=NS_MAP)
        return result.text if result is not None else None

    return {
        "logradouro": get_text(end, "cte:xLgr"),
        "numero": get_text(end, "cte:nro"),
        "complemento": get_text(end, "cte:xCpl"),
        "bairro": get_text(end, "cte:xBairro"),
        "municipio": get_text(end, "cte:xMun"),
        "uf": get_text(end, "cte:UF"),
        "cep": get_text(end, "cte:CEP"),
        "pais": get_text(end, "cte:cPais"),
    }


def _elem_to_dict(elem: etree._Element) -> dict[str, Any]:
    """Convert lxml element to dict (simplified)"""
    result: dict[str, Any] = {}
    for child in elem:
        # Remove namespace from tag
        tag = child.tag
        if "}" in tag:
            tag = tag.split("}")[1]
        if child.text and child.text.strip():
            result[tag] = child.text.strip()
        elif len(child) > 0:
            result[tag] = _elem_to_dict(child)
    return result


def _parse_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str[: len(fmt)], fmt).isoformat()
            except ValueError:
                continue
        return date_str
    except Exception:
        return None
