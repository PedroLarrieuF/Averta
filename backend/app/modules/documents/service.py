"""Documents module service"""

from datetime import datetime
from typing import Any

import structlog

from app.core.dependencies import PaginationParams
from app.core.exceptions import NotFoundError, ValidationError_
from app.modules.discrepancies.schemas import DiscrepancyCreate, DiscrepancyResponse
from app.modules.discrepancies.service import DiscrepanciesService
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentImport,
    DocumentImportResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatus,
    DocumentType,
    DocumentUpdate,
)
from app.modules.notifications.service import NotificationsService
from app.services.rules_engine_v2 import RuleContext, create_engine_v2
from app.services.storage import upload_file
from app.services.xml_parser import parse_cte_xml, parse_nfe_xml
from prisma import Prisma
from prisma.models import Document as DocumentModel

logger = structlog.get_logger()


class DocumentsService:
    def __init__(self, db: Prisma):
        self.db = db
        self._rules_engine: Any = None

    async def _get_rules_engine(self) -> Any:
        if self._rules_engine is None:
            self._rules_engine = await create_engine_v2()
        return self._rules_engine

    def _to_response(self, document: DocumentModel) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            company_id=document.companyId,
            client_id=document.clientId,
            carrier_id=document.carrierId,
            contract_id=document.contractId,
            type=document.type,
            access_key=document.accessKey,
            number=document.number,
            series=document.series,
            issue_date=document.issueDate,
            total_value=document.totalValue,
            freight_value=document.freightValue,
            weight=document.weight,
            volume=document.volume,
            status=document.status,
            parsed_data=document.parsedData,
            error_message=document.errorMessage,
            file_path=document.filePath,
            file_size=document.fileSize,
            created_at=document.createdAt,
            updated_at=document.updatedAt,
        )

    async def create_document(self, data: DocumentCreate, company_id: str) -> DocumentResponse:
        """Create new document"""
        # Check if access key already exists
        existing = await self.db.document.find_unique(
            where={"accessKey_companyId": {"accessKey": data.access_key, "companyId": company_id}}
        )
        if existing:
            raise ValidationError_(f"Document with access key {data.access_key} already exists")

        document = await self.db.document.create(
            data={
                "companyId": company_id,
                "clientId": data.client_id,
                "carrierId": data.carrier_id,
                "contractId": data.contract_id,
                "type": data.type.value,
                "accessKey": data.access_key,
                "number": data.number,
                "series": data.series,
                "issueDate": data.issue_date,
                "totalValue": data.total_value,
                "freightValue": data.freight_value,
                "weight": data.weight,
                "volume": data.volume,
                "status": DocumentStatus.PENDING.value,
                "parsedData": data.parsed_data,
                "filePath": data.file_path,
                "fileSize": data.file_size,
            }
        )

        logger.info("document_created", id=document.id, access_key=data.access_key)
        return self._to_response(document)

    async def get_by_id(self, document_id: str, company_id: str) -> DocumentResponse:
        """Get document by ID"""
        document = await self.db.document.find_unique(
            where={"id": document_id, "companyId": company_id}
        )
        if not document:
            raise NotFoundError("Document", document_id)
        return self._to_response(document)

    async def get_by_access_key(self, access_key: str, company_id: str) -> DocumentResponse | None:
        """Get document by access key"""
        document = await self.db.document.find_unique(
            where={"accessKey_companyId": {"accessKey": access_key, "companyId": company_id}}
        )
        if not document:
            return None
        return self._to_response(document)

    async def list_documents(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        client_id: str | None = None,
        carrier_id: str | None = None,
        status: DocumentStatus | None = None,
        type: DocumentType | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> DocumentListResponse:
        """List documents with filters"""
        where: dict[str, Any] = {"companyId": company_id}
        if client_id:
            where["clientId"] = client_id
        if carrier_id:
            where["carrierId"] = carrier_id
        if status:
            where["status"] = status.value
        if type:
            where["type"] = type.value
        if date_from or date_to:
            where["issueDate"] = {}
            if date_from:
                where["issueDate"]["gte"] = date_from
            if date_to:
                where["issueDate"]["lte"] = date_to

        total = await self.db.document.count(where=where)
        documents = await self.db.document.find_many(
            where=where,
            skip=pagination.offset,
            take=pagination.limit,
            order={"createdAt": "desc"},
        )

        return DocumentListResponse(
            items=[self._to_response(d) for d in documents],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def update_document(
        self, document_id: str, company_id: str, data: DocumentUpdate
    ) -> DocumentResponse:
        """Update document"""
        document = await self.db.document.update(
            where={"id": document_id, "companyId": company_id},
            data=data.model_dump(exclude_unset=True),
        )
        if not document:
            raise NotFoundError("Document", document_id)
        return self._to_response(document)

    async def delete_document(self, document_id: str, company_id: str) -> None:
        """Delete document"""
        await self.db.document.delete(where={"id": document_id, "companyId": company_id})

    async def import_xml(
        self,
        file_content: str,
        company_id: str,
        client_id: str,
        carrier_id: str | None = None,
        contract_id: str | None = None,
    ) -> DocumentResponse:
        """Parse XML and create document"""
        # Parse XML - try CT-e first, then NF-e
        try:
            parsed = parse_cte_xml(file_content)
        except ValueError:
            try:
                parsed = parse_nfe_xml(file_content)
            except ValueError as e:
                raise ValidationError_(f"Could not parse XML: {e}") from e

        # Determine document type
        doc_type = DocumentType.CTE
        if parsed.get("modelo") == "55":
            doc_type = DocumentType.NFE
        elif parsed.get("modelo") in ["57", "67"]:
            doc_type = DocumentType.CTE_COMPLEMENTAR

        # Extract key fields
        access_key = parsed.get("chave_acesso") or parsed.get("access_key")
        if not access_key:
            raise ValidationError_("Could not extract access key from XML")

        # Check for duplicate
        existing = await self.get_by_access_key(access_key, company_id)
        if existing:
            raise ValidationError_(f"Document with access key {access_key} already exists")

        # Store XML file
        file_path = await upload_file(
            file_data=file_content.encode(),
            object_name=f"documents/{company_id}/{client_id}/{access_key}.xml",
            content_type="application/xml",
        )

        # Create document
        doc_data = DocumentCreate(
            client_id=client_id,
            carrier_id=carrier_id,
            contract_id=contract_id,
            type=doc_type,
            access_key=access_key,
            number=parsed.get("numero"),
            series=parsed.get("serie"),
            issue_date=parsed.get("data_emissao"),
            total_value=parsed.get("valor_total"),
            freight_value=parsed.get("valor_frete"),
            weight=parsed.get("peso_bruto"),
            volume=parsed.get("volume"),
            xml_content=file_content,
            parsed_data=parsed,
            file_path=file_path,
            file_size=len(file_content.encode()),
        )

        document = await self.create_document(doc_data, company_id)

        # Auto-match contract if not provided
        if not contract_id and document.carrier_id:
            contract = await self._match_contract(document, company_id)
            if contract:
                document = await self.update_document(
                    document.id, company_id, DocumentUpdate(contract_id=contract.id)
                )

        # Run rules engine
        discrepancies = await self._run_audit(document, company_id)

        # Notify if discrepancies found
        if discrepancies:
            notifications = NotificationsService(self.db)
            for disc in discrepancies:
                await notifications.notify_discrepancy_found(
                    client_id=client_id,
                    discrepancy_id=disc.id,
                    discrepancy_type=disc.discrepancy_type,
                    value=disc.difference or 0,
                )

        return document

    async def _match_contract(self, document: DocumentResponse, company_id: str) -> Any | None:
        """Match document to contract based on carrier and client"""
        return await self.db.contract.find_first(
            where={
                "companyId": company_id,
                "clientId": document.client_id,
                "carrierId": document.carrier_id,
                "status": "ACTIVE",
                "validFrom": {"lte": document.issue_date or datetime.utcnow()},
                "validTo": {"gte": document.issue_date or datetime.utcnow()},
            },
            order={"validFrom": "desc"},
        )

    async def _run_audit(
        self, document: DocumentResponse, company_id: str
    ) -> list[DiscrepancyResponse]:
        """Run rules engine on document"""
        engine = await self._get_rules_engine()

        # Get contract and freight table
        contract = None
        freight_table = None
        if document.contract_id:
            contract = await self.db.contract.find_unique(where={"id": document.contract_id})
            if contract and contract.freightTableId:
                freight_table = await self.db.freightTable.find_unique(
                    where={"id": contract.freightTableId}
                )

        carrier = None
        if document.carrier_id:
            carrier = await self.db.carrier.find_unique(where={"id": document.carrier_id})

        # Build context
        context = RuleContext(
            document=document.parsed_data or {},
            contract=contract.model_dump() if contract else None,
            freight_table=freight_table.rules if freight_table else None,
            carrier=carrier.model_dump() if carrier else None,
            metadata={"company_id": company_id, "document_id": document.id},
        )

        # Run rules
        results = await engine.evaluate_all(context)

        # Create discrepancies
        discrepancies = []
        discrepancies_service = DiscrepanciesService(self.db)

        for result in results:
            disc_data = DiscrepancyCreate(
                document_id=document.id,
                company_id=company_id,
                rule_code=result.rule_code,
                rule_name=result.rule_name,
                discrepancy_type=result.discrepancy_type.value,
                expected_value=result.expected_value,
                actual_value=result.actual_value,
                difference=result.difference,
                difference_pct=result.difference_pct,
                details=result.details,
                evidence=result.evidence,
                severity=result.severity,
            )
            disc = await discrepancies_service.create_discrepancy(disc_data)
            discrepancies.append(disc)

        # Update document status
        await self.update_document(
            document.id,
            company_id,
            DocumentUpdate(
                status=DocumentStatus.COMPLETED if not discrepancies else DocumentStatus.COMPLETED,
            ),
        )

        logger.info("document_audited", document_id=document.id, discrepancies=len(discrepancies))
        return discrepancies

    async def import_batch(
        self, import_data: DocumentImport, company_id: str
    ) -> DocumentImportResponse:
        """Import multiple XML files"""
        imported = 0
        failed = 0
        documents = []
        errors = []

        for file_content in import_data.files:
            try:
                doc = await self.import_xml(
                    file_content=file_content,
                    company_id=company_id,
                    client_id=import_data.client_id,
                    carrier_id=import_data.carrier_id,
                    contract_id=import_data.contract_id,
                )
                documents.append(doc)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({"file": file_content[:100], "error": str(e)})
                logger.exception("import_failed", error=str(e))

        return DocumentImportResponse(
            imported=imported,
            failed=failed,
            documents=documents,
            errors=errors,
        )

    async def reprocess_document(self, document_id: str, company_id: str) -> DocumentResponse:
        """Reprocess document (re-run rules)"""
        document = await self.get_by_id(document_id, company_id)

        # Delete existing discrepancies
        await self.db.discrepancy.delete_many(where={"documentId": document_id})

        # Re-run audit
        await self._run_audit(document, company_id)

        return await self.get_by_id(document_id, company_id)
