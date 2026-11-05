// Contracts & Freight Tables Types
// Card #24: Contracts Page - CRUD + FreightTable Editor

export type ContractStatus = 'ACTIVE' | 'EXPIRED' | 'PENDING';
export type FreightTableStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
export type FreightModal = 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';

export interface Contract {
  id: string;
  number: string;
  client_id: string;
  client_name?: string;
  carrier_id: string;
  carrier_name?: string;
  status: ContractStatus;
  start_date: string;
  end_date: string | null;
  success_fee_pct: number;
  description: string | null;
  freight_tables_count: number;
  documents_count: number;
  discrepancies_count: number;
  contests_count: number;
  created_at: string;
  updated_at: string;
}

export interface ContractListParams {
  page?: number;
  size?: number;
  search?: string;
  status?: ContractStatus;
  client_id?: string;
  carrier_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface PaginatedContracts {
  data: Contract[];
  meta: {
    page: number;
    size: number;
    total: number;
    total_pages: number;
  };
}

export interface CreateContractData {
  number: string;
  client_id: string;
  carrier_id: string;
  status: ContractStatus;
  start_date: string;
  end_date: string | null;
  success_fee_pct: number;
  description: string;
}

export interface UpdateContractData extends Partial<CreateContractData> {}

// Freight Table Types
export interface FreightTable {
  id: string;
  contract_id: string;
  version: number;
  status: FreightTableStatus;
  effective_from: string;
  effective_to: string | null;
  rates: FreightRate[];
  created_at: string;
  updated_at: string;
}

export interface FreightRate {
  id: string;
  freight_table_id: string;
  weight_min: number | null;
  weight_max: number | null;
  cubage_min: number | null;
  cubage_max: number | null;
  distance_min: number | null;
  distance_max: number | null;
  modal: FreightModal;
  uf_origin: string | null;
  uf_dest: string | null;
  rate_per_kg: number | null;
  rate_per_m3: number | null;
  rate_per_km: number | null;
  minimum_value: number | null;
}

export interface FreightRateInput extends Omit<FreightRate, 'id' | 'freight_table_id'> {}

export interface CreateFreightTableData {
  contract_id: string;
  version?: number;
  status: FreightTableStatus;
  effective_from: string;
  effective_to: string | null;
  rates: FreightRateInput[];
}

export interface UpdateFreightTableData {
  status?: FreightTableStatus;
  effective_from?: string;
  effective_to?: string | null;
  rates?: FreightRateInput[];
}

export interface FreightTableListParams {
  contract_id: string;
}

export interface SimpleSelectOption {
  id: string;
  name: string;
}

export const FREIGHT_MODALS: { value: FreightModal; label: string }[] = [
  { value: 'RODOVIARIO', label: 'Rodoviário' },
  { value: 'AEREO', label: 'Aéreo' },
  { value: 'MARITIMO', label: 'Marítimo' },
  { value: 'FERROVIARIO', label: 'Ferroviário' },
];

export const CONTRACT_STATUSES: { value: ContractStatus; label: string }[] = [
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'EXPIRED', label: 'Expirado' },
  { value: 'PENDING', label: 'Pendente' },
];

export const FREIGHT_TABLE_STATUSES: { value: FreightTableStatus; label: string }[] = [
  { value: 'DRAFT', label: 'Rascunho' },
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'ARCHIVED', label: 'Arquivado' },
];

export const BRAZILIAN_STATES = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
];