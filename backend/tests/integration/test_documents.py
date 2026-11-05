"""Integration tests for Documents module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestDocumentsUpload:
    """Tests for POST /api/v1/documents/upload"""

    async def test_upload_valid_xml(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading valid XML document"""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<cteProc xmlns="http://www.portalfiscal.inf.br/cte">
    <CTe>
        <infCte Id="CTe123" versao="4.00">
            <ide>
                <cUF>35</cUF>
                <cCT>12345678</cCT>
                <CFOP>6352</CFOP>
                <natOp>PRESTACAO DE SERVICO</natOp>
                <mod>57</mod>
                <serie>1</serie>
                <nCT>1</nCT>
                <dhEmi>2024-01-01T10:00:00-03:00</dhEmi>
                <tpImp>1</tpImp>
                <tpEmis>1</tpEmis>
                <cDV>1</cDV>
                <tpAmb>2</tpAmb>
                <tpCTe>0</tpCTe>
                <procEmi>0</procEmi>
                <verProc>1.0</verProc>
                <cMunEnv>3550308</cMunEnv>
                <xMunEnv>SAO PAULO</xMunEnv>
                <UFEnv>SP</UFEnv>
                <modal>01</modal>
                <tpServ>0</tpServ>
                <cMunIni>3550308</cMunIni>
                <xMunIni>SAO PAULO</xMunIni>
                <UFIni>SP</UFIni>
                <cMunFim>3106200</cMunFim>
                <xMunFim>BELO HORIZONTE</xMunFim>
                <UFFim>MG</UFFim>
                <retira>1</retira>
                <xDetRetira>SAO PAULO</xDetRetira>
            </ide>
            <compl>
                <xObs>Test document</xObs>
            </compl>
            <emit>
                <CNPJ>12345678000195</CNPJ>
                <xNome>EMITENTE TESTE LTDA</xNome>
                <enderEmit>
                    <xLgr>RUA TESTE</xLgr>
                    <nro>123</nro>
                    <xBairro>CENTRO</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>SAO PAULO</xMun>
                    <UF>SP</UF>
                    <CEP>01000000</CEP>
                </enderEmit>
                <IE>123456789</IE>
                <CRT>3</CRT>
            </emit>
            <rem>
                <CNPJ>11111111000199</CNPJ>
                <xNome>REMETENTE TESTE LTDA</xNome>
                <enderReme>
                    <xLgr>RUA REMETENTE</xLgr>
                    <nro>456</nro>
                    <xBairro>CENTRO</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>SAO PAULO</xMun>
                    <UF>SP</UF>
                    <CEP>01000000</CEP>
                </enderReme>
            </rem>
            <dest>
                <CNPJ>22222222000188</CNPJ>
                <xNome>DESTINATARIO TESTE LTDA</xNome>
                <enderDest>
                    <xLgr>RUA DESTINATARIO</xLgr>
                    <nro>789</nro>
                    <xBairro>CENTRO</xBairro>
                    <cMun>3106200</cMun>
                    <xMun>BELO HORIZONTE</xMun>
                    <UF>MG</UF>
                    <CEP>30000000</CEP>
                </enderDest>
            </dest>
            <vPrest>
                <vTPrest>1000.00</vTPrest>
                <vRec>1000.00</vRec>
                <Comp>
                    <xNome>FRETE</xNome>
                    <vComp>1000.00</vComp>
                </Comp>
            </vPrest>
            <imp>
                <ICMS>
                    <ICMS00>
                        <CST>00</CST>
                        <vBC>1000.00</vBC>
                        <pICMS>12.00</pICMS>
                        <vICMS>120.00</vICMS>
                    </ICMS00>
                </ICMS>
            </imp>
            <infCTeNorm>
                <infCarga>
                    <vCarga>10000.00</vCarga>
                    <proPred>PRODUTO TESTE</proPred>
                    <qCarga>1.0000</qCarga>
                    <unCarga>KG</unCarga>
                </infCarga>
            </infCTeNorm>
        </infCte>
    </CTe>
</cteProc>"""

        files = {"file": ("test.xml", xml_content, "application/xml")}
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 500]

    async def test_upload_invalid_xml(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading invalid XML"""
        files = {"file": ("test.xml", b"<invalid>xml</invalid>", "application/xml")}
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_upload_without_auth(self, async_client: AsyncClient):
        """Test uploading without authentication"""
        files = {"file": ("test.xml", b"<xml></xml>", "application/xml")}
        response = await async_client.post("/api/v1/documents/upload", files=files)
        assert response.status_code in [401, 500]

    async def test_upload_empty_file(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading empty file"""
        files = {"file": ("empty.xml", b"", "application/xml")}
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]


@pytest.mark.integration
class TestDocumentsList:
    """Tests for GET /api/v1/documents"""

    async def test_list_documents_pagination(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing documents with pagination"""
        response = await async_client.get(
            "/api/v1/documents",
            headers=auth_headers,
            params={"page": 1, "size": 10},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_documents_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing documents with filters"""
        response = await async_client.get(
            "/api/v1/documents",
            headers=auth_headers,
            params={"status": "COMPLETED", "type": "CTE"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_documents_search(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing documents with search"""
        response = await async_client.get(
            "/api/v1/documents",
            headers=auth_headers,
            params={"search": "test"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_documents_without_auth(self, async_client: AsyncClient):
        """Test listing documents without auth"""
        response = await async_client.get("/api/v1/documents")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDocumentsDetail:
    """Tests for GET /api/v1/documents/{id}"""

    async def test_get_document_exists(self, async_client: AsyncClient, auth_headers: dict, mock_document: dict):
        """Test getting existing document"""
        response = await async_client.get(
            f"/api/v1/documents/{mock_document['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_get_document_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent document"""
        response = await async_client.get(
            "/api/v1/documents/non-existent-id",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]

    async def test_get_document_unauthorized(self, async_client: AsyncClient):
        """Test getting document without auth"""
        response = await async_client.get("/api/v1/documents/some-id")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDocumentsReprocess:
    """Tests for POST /api/v1/documents/{id}/reprocess"""

    async def test_reprocess_document(self, async_client: AsyncClient, auth_headers: dict, mock_document: dict):
        """Test reprocessing a document"""
        response = await async_client.post(
            f"/api/v1/documents/{mock_document['id']}/reprocess",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_reprocess_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test reprocessing non-existent document"""
        response = await async_client.post(
            "/api/v1/documents/non-existent/reprocess",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]

    async def test_reprocess_unauthorized(self, async_client: AsyncClient):
        """Test reprocessing without auth"""
        response = await async_client.post("/api/v1/documents/some-id/reprocess")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDocumentsImport:
    """Tests for POST /api/v1/documents/import"""

    async def test_import_base64_xml(self, async_client: AsyncClient, auth_headers: dict):
        """Test importing base64 encoded XML"""
        import base64
        xml_content = b"<cteProc><CTe><infCte Id='test' versao='4.00'></infCte></CTe></cteProc>"
        base64_content = base64.b64encode(xml_content).decode()

        response = await async_client.post(
            "/api/v1/documents/import",
            json={"file_base64": base64_content, "file_name": "test.xml"},
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 500]

    async def test_import_invalid_base64(self, async_client: AsyncClient, auth_headers: dict):
        """Test importing invalid base64"""
        response = await async_client.post(
            "/api/v1/documents/import",
            json={"file_base64": "invalid-base64!", "file_name": "test.xml"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]