import type { DocumentStatus, DocumentType } from './enums';
import type { PaginatedResponse } from './common';

// Re-export enums for convenience
export type { DocumentType, DocumentStatus } from './enums';

// Document Types
export interface ParsedDocumentData {
  // CTe/NFE parsed fields - 40+ fields from xml_parser
  chave_acesso?: string;
  numero?: string;
  serie?: string;
  data_emissao?: string;
  valor_total?: number;
  cnpj_emitente?: string;
  nome_emitente?: string;
  cnpj_destinatario?: string;
  nome_destinatario?: string;
  cfop?: string;
  natureza_operacao?: string;
  peso_bruto?: number;
  peso_liquido?: number;
  volumes?: number;
  valor_frete?: number;
  valor_icms?: number;
  valor_ipi?: number;
  valor_pis?: number;
  valor_cofins?: number;
  [key: string]: unknown;
}

export interface Document {
  id: string;
  companyId: string;
  clientId?: string;
  carrierId?: string;
  type: DocumentType;
  status: DocumentStatus;
  fileName: string;
  fileSize: number;
  fileUrl?: string;
  parsedData?: ParsedDocumentData;
  errorMessage?: string;
  processedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentUploadResponse {
  document: Document;
  uploadUrl?: string;
}

export type DocumentListResponse = PaginatedResponse<Document>;

export interface DocumentFilters {
  status?: DocumentStatus[];
  documentType?: DocumentType[];
  clientId?: string;
  carrierId?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

export interface ReprocessDocumentRequest {
  documentId: string;
}

export interface DocumentCreateRequest {
  clientId?: string;
  carrierId?: string;
  type: DocumentType;
  fileName: string;
  fileSize: number;
}

export interface DocumentUpdateRequest {
  status?: DocumentStatus;
  parsedData?: ParsedDocumentData;
  errorMessage?: string;
}