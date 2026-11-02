"""Documents module router"""
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAuditor,
    CompanyIdDep,
    ClientIdDep,
    PaginationDep,
)
from app.core.rate_limit import upload_limiter
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentImport,
    DocumentImportResponse,
    DocumentType,
    DocumentStatus,
)
from app.modules.documents.service import DocumentsService

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_documents_service(db: Prisma = Depends(get_database)) -> DocumentsService:
    return DocumentsService(db)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create document",
)
async def create_document(
    data: DocumentCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Create a new document manually"""
    return await documents_service.create_document(data, company_id)


@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List documents",
)
async def list_documents(
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    client_id: ClientIdDep,
    pagination: PaginationDep,
    carrier_id: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    type: Optional[DocumentType] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """List documents with filters"""
    if current_user.role == "CLIENT" and current_user.client_id:
        client_id = current_user.client_id

    return await documents_service.list_documents(
        company_id, pagination, client_id, carrier_id, status, type, date_from, date_to
    )


@router.post(
    "/import",
    response_model=DocumentImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Import XML files",
)
async def import_documents(
    import_data: DocumentImport,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Import multiple XML files (CT-e/NF-e)"""
    import_data.client_id = current_user.client_id or import_data.client_id
    return await documents_service.import_batch(import_data, company_id)


@router.post(
    "/upload",
    response_model=DocumentImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload XML files",
)
@upload_limiter
async def upload_documents(
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    client_id: ClientIdDep,
    files: List[UploadFile] = File(...),
    carrier_id: Optional[str] = Form(None),
    contract_id: Optional[str] = Form(None),
    auto_match_contract: bool = Form(True),
    auto_run_rules: bool = Form(True),
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Upload XML files directly"""
    if current_user.role == "CLIENT" and current_user.client_id:
        client_id = current_user.client_id

    file_contents = []
    for file in files:
        content = await file.read()
        file_contents.append(content.decode("utf-8"))

    import_data = DocumentImport(
        client_id=client_id,
        carrier_id=carrier_id,
        contract_id=contract_id,
        files=file_contents,
        auto_match_contract=auto_match_contract,
        auto_run_rules=auto_run_rules,
    )

    return await documents_service.import_batch(import_data, company_id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document by ID",
)
async def get_document(
    document_id: str,
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Get document details"""
    return await documents_service.get_by_id(document_id, company_id)


@router.get(
    "/access-key/{access_key}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document by access key",
)
async def get_document_by_access_key(
    access_key: str,
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Get document by access key (chave de acesso)"""
    document = await documents_service.get_by_access_key(access_key, company_id)
    if not document:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document", access_key)
    return document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document",
)
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Update document"""
    return await documents_service.update_document(document_id, company_id, data)


@router.post(
    "/{document_id}/reprocess",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Reprocess document",
)
async def reprocess_document(
    document_id: str,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Reprocess document (re-run rules engine)"""
    return await documents_service.reprocess_document(document_id, company_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
)
async def delete_document(
    document_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Delete document"""
    await documents_service.delete_document(document_id, company_id)