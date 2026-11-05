// Demo API Service - Provides mock data for all endpoints in demo mode
// This simulates the backend API responses without needing a real backend
// Uses frontend types directly for compatibility with all UI components

import type { User as AuthUser } from '../store/auth-storage'
import type {
  Document,
  DocumentStatus,
  DocumentType,
  DocumentFilters,
  Discrepancy,
  DiscrepancyStatus,
  DiscrepancySeverity,
  DiscrepancyType,
  DiscrepancySummary,
  Contest,
  ContestStatus,
  Client,
  Carrier,
  Contract,
  ContractStatus,
  FreightTable,
  FreightTableStatus,
  DashboardKPIs,
  RecoveryReport,
  CarrierPerformanceReport,
} from '../types'

// Local types for internal use (not exported from types index)
interface ContestPayment {
  id: string
  contestId: string
  amount: number
  paymentDate: string
  paymentMethod: string
  reference: string
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED'
  createdAt: string
}

interface ParsedDocumentData {
  chave_acesso?: string
  numero?: string
  serie?: string
  data_emissao?: string
  valor_total?: number
  cnpj_emitente?: string
  nome_emitente?: string
  cnpj_destinatario?: string
  nome_destinatario?: string
  cfop?: string
  natureza_operacao?: string
  peso_bruto?: number
  peso_liquido?: number
  volumes?: number
  valor_frete?: number
  valor_icms?: number
  valor_ipi?: number
  valor_pis?: number
  valor_cofins?: number
  [key: string]: unknown
}

interface ScheduledReport {
  id: string
  companyId: string
  name: string
  description?: string
  format: 'PDF' | 'EXCEL'
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY'
  dayOfWeek?: number
  dayOfMonth?: number
  hour: number
  minute: number
  filters: Record<string, unknown>
  recipients: string[]
  isActive: boolean
  lastRunAt?: string
  nextRunAt?: string
  createdAt: string
  updatedAt: string
}

interface ReportsDashboardResponse {
  kpis: {
    total_documents: number
    total_discrepancies: number
    total_recovered: number
    pending_contests: number
    success_rate: number
  }
  top_carriers: Array<{ carrier_name: string; count: number; value: number }>
  top_rules: Array<{ rule_code: string; count: number; total_difference: number }>
  time_series: Array<{ date: string; discrepancies: number; recovered: number }>
}

interface ScheduledReportListResponse {
  items: ScheduledReport[]
  total: number
  page: number
  size: number
  pages: number
}

// ===== UTILITY FUNCTIONS =====

function generateId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

function randomDate(daysBack = 30): string {
  const date = new Date()
  date.setDate(date.getDate() - Math.floor(Math.random() * daysBack))
  return date.toISOString()
}

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

function randomRange(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function randomFloat(min: number, max: number, decimals = 2): number {
  const value = Math.random() * (max - min) + min
  return Number(value.toFixed(decimals))
}

// ===== MOCK DATA GENERATORS =====

const COMPANY_NAMES = [
  'Averta Logística Ltda',
  'Transportes União S.A.',
  'Cargas Brasil Express',
  'Logística Total Ltda',
  'Frete Rápido Comércio',
]

const CARRIER_NAMES = [
  'Transportes Rápidos Ltda',
  'Logística Express S.A.',
  'Cargas Brasil Transportes',
  'Transporte Sul Norte Ltda',
  'Expresso Nacional S.A.',
  'Caminhões do Brasil Ltda',
  'RodoCarga Transportes',
  'Via Expressa Logística',
]

const CLIENT_NAMES = [
  'Indústria Alfa S.A.',
  'Comércio Beta Ltda',
  'Distribuidora Gama',
  'Atacado Delta S.A.',
  'Varejo Épsilon Ltda',
  'Importadora Zeta',
  'Exportadora Eta S.A.',
  'Fabricante Teta Ltda',
]

const USER_NAMES = [
  'Administrador Demo',
  'João Silva',
  'Maria Santos',
  'Pedro Oliveira',
  'Ana Costa',
  'Carlos Ferreira',
  'Luciana Almeida',
  'Roberto Lima',
  'Fernanda Rocha',
  'Gabriel Martins',
]

const DOCUMENT_TYPES: DocumentType[] = ['CTE', 'NFE', 'CTE_COMPLEMENTAR', 'NFE_COMPLEMENTAR', 'OTHER']
const DOCUMENT_STATUSES: DocumentStatus[] = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'ARCHIVED']
const DISCREPANCY_STATUSES: DiscrepancyStatus[] = ['OPEN', 'IN_REVIEW', 'CONTESTED', 'APPROVED', 'REJECTED', 'PAID', 'CLOSED']
const DISCREPANCY_SEVERITIES: DiscrepancySeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
const DISCREPANCY_TYPES: DiscrepancyType[] = [
  'FREIGHT_VALUE', 'ICMS', 'TOLLS', 'WEIGHT', 'VOLUME', 'DIMENSIONS',
  'DUPLICATE', 'MISSING_DOCUMENT', 'INVALID_CNPJ', 'ROUTE_MISMATCH', 'OTHER'
]
const CONTEST_STATUSES: ContestStatus[] = ['DRAFT', 'SENT', 'ACKNOWLEDGED', 'NEGOTIATING', 'ACCEPTED', 'PARTIAL', 'REJECTED', 'EXPIRED']
const CONTRACT_STATUSES: ContractStatus[] = ['DRAFT', 'ACTIVE', 'EXPIRED', 'CANCELLED']

// ===== DEMO DATA STORE =====
class DemoStore {
  private users: AuthUser[] = []
  private companies: Array<{ id: string; name: string; cnpj: string; email: string; phone: string; address: string; city: string; state: string; zipCode: string; createdAt: string; updatedAt: string }> = []
  private carriers: Carrier[] = []
  private clients: Client[] = []
  private contracts: Contract[] = []
  private documents: Document[] = []
  private discrepancies: Discrepancy[] = []
  private contests: Contest[] = []
  private payments: ContestPayment[] = []
  private scheduledReports: ScheduledReport[] = []
  private freightTables: FreightTable[] = []

  constructor() {
    this.initializeData()
  }

  private initializeData() {
    // Create demo company
    const demoCompany = {
      id: 'demo-company-1',
      name: 'Averta Logística Ltda',
      cnpj: '12.345.678/0001-90',
      email: 'contato@averta.com.br',
      phone: '(11) 3456-7890',
      address: 'Av. Paulista, 1000',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01310-100',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    }
    this.companies = [demoCompany, ...COMPANY_NAMES.slice(1).map((name, i) => ({
      id: `demo-company-${i + 2}`,
      name,
      cnpj: `${Math.floor(10000000 + Math.random() * 90000000)}.${Math.floor(100 + Math.random() * 900)}/${Math.floor(1000 + Math.random() * 9000)}-${Math.floor(10 + Math.random() * 90)}`,
      email: `contato@${name.toLowerCase().replace(/\s+/g, '').replace('ltda', '').replace('s.a.', '')}.com.br`,
      phone: `(${11 + i}) ${3000 + i * 111}-${7000 + i * 111}`,
      address: `Rua ${i + 1}, ${100 + i * 100}`,
      city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba'][i],
      state: ['SP', 'RJ', 'MG', 'PR'][i],
      zipCode: `${10000 + i * 1111}-${100 + i * 11}`,
      createdAt: randomDate(365),
      updatedAt: randomDate(30),
    }))]

    // Create demo user (admin)
    const demoUser: AuthUser = {
      id: 'demo-user-1',
      email: 'admin@averta.com',
      fullName: 'Administrador Demo',
      role: 'ADMIN',
      status: 'ACTIVE',
      companyId: demoCompany.id,
      clientId: undefined,
      avatarUrl: undefined,
      lastLoginAt: new Date().toISOString(),
      createdAt: '2024-01-01T00:00:00Z',
    }
    this.users = [demoUser, ...USER_NAMES.slice(1).map((name, i) => ({
      id: `demo-user-${i + 2}`,
      email: `${name.toLowerCase().replace(' ', '.')}@averta.com`,
      fullName: name,
      role: randomItem(['ADMIN', 'MANAGER', 'AUDITOR', 'CLIENT', 'CARRIER'] as const),
      status: randomItem(['ACTIVE', 'ACTIVE', 'ACTIVE', 'INACTIVE', 'PENDING'] as const),
      companyId: demoCompany.id,
      clientId: undefined,
      avatarUrl: undefined,
      lastLoginAt: randomDate(30),
      createdAt: randomDate(365),
    }))]

    // Create demo carriers
    this.carriers = CARRIER_NAMES.map((name, i) => {
      const carrierId = `demo-carrier-${i + 1}`
      return {
        id: carrierId,
        companyId: demoCompany.id,
        name,
        cnpj: `${Math.floor(10000000 + Math.random() * 90000000)}.${Math.floor(100 + Math.random() * 900)}/${Math.floor(1000 + Math.random() * 9000)}-${Math.floor(10 + Math.random() * 90)}`,
        email: `contato@${name.toLowerCase().replace(/\s+/g, '').replace('ltda', '').replace('s.a.', '')}.com.br`,
        phone: `(${11 + i}) ${4000 + i * 111}-${8000 + i * 111}`,
        anttRegistry: `${Math.floor(100000 + Math.random() * 900000)}`,
        address: `Av. das Transportadoras, ${100 + i * 100}`,
        city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza', 'Brasília'][i],
        state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'DF'][i],
        zipCode: `${20000 + i * 1111}-${200 + i * 11}`,
        contacts: [
          {
            id: `contact-${carrierId}-1`,
            name: `Contato ${name}`,
            email: `contato@${name.toLowerCase().replace(/\s+/g, '')}.com.br`,
            phone: `(${11 + i}) 9${8000 + i * 111}-${1000 + i * 111}`,
            role: 'Gerente Comercial',
          },
          {
            id: `contact-${carrierId}-2`,
            name: `Operações ${name}`,
            email: `operacoes@${name.toLowerCase().replace(/\s+/g, '')}.com.br`,
            phone: `(${11 + i}) 9${9000 + i * 111}-${2000 + i * 111}`,
            role: 'Gerente de Operações',
          },
        ],
        branches: [
          {
            id: `branch-${carrierId}-1`,
            carrierId,
            name: `${name} - Matriz`,
            code: 'MATRIZ',
            address: `Av. das Transportadoras, ${100 + i * 100}`,
            city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza', 'Brasília'][i],
            state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'DF'][i],
            zipCode: `${20000 + i * 1111}-${200 + i * 11}`,
            isMain: true,
            anttCode: `${Math.floor(10000 + Math.random() * 90000)}`,
          },
          {
            id: `branch-${carrierId}-2`,
            carrierId,
            name: `${name} - Filial`,
            code: 'FILIAL',
            address: `Rua das Filiais, ${200 + i * 100}`,
            city: ['Campinas', 'Niterói', 'Contagem', 'Londrina', 'Caxias do Sul', 'Feira de Santana', 'Maracanaú', 'Goiânia'][i],
            state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'GO'][i],
            zipCode: `${30000 + i * 1111}-${300 + i * 11}`,
            isMain: false,
            anttCode: `${Math.floor(10000 + Math.random() * 90000)}`,
          },
        ],
        status: randomItem(['ACTIVE', 'ACTIVE', 'INACTIVE'] as const),
        createdAt: randomDate(365),
        updatedAt: randomDate(30),
      }
    })

    // Create demo clients
    this.clients = CLIENT_NAMES.map((name, i) => {
      const clientId = `demo-client-${i + 1}`
      return {
        id: clientId,
        companyId: demoCompany.id,
        name,
        cnpj: `${Math.floor(10000000 + Math.random() * 90000000)}.${Math.floor(100 + Math.random() * 900)}/${Math.floor(1000 + Math.random() * 9000)}-${Math.floor(10 + Math.random() * 90)}`,
        email: `compras@${name.toLowerCase().replace(/\s+/g, '').replace('ltda', '').replace('s.a.', '')}.com.br`,
        phone: `(${11 + i}) ${5000 + i * 111}-${9000 + i * 111}`,
        address: `Rua dos Clientes, ${300 + i * 100}`,
        city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza', 'Brasília'][i],
        state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'DF'][i],
        zipCode: `${40000 + i * 1111}-${400 + i * 11}`,
        contacts: [
          {
            id: `client-contact-${clientId}-1`,
            name: `Comprador ${name}`,
            email: `compras@${name.toLowerCase().replace(/\s+/g, '')}.com.br`,
            phone: `(${11 + i}) 9${7000 + i * 111}-${3000 + i * 111}`,
            role: 'Gerente de Compras',
            isPrimary: true,
          },
          {
            id: `client-contact-${clientId}-2`,
            name: `Financeiro ${name}`,
            email: `financeiro@${name.toLowerCase().replace(/\s+/g, '')}.com.br`,
            phone: `(${11 + i}) 9${8000 + i * 111}-${4000 + i * 111}`,
            role: 'Analista Financeiro',
            isPrimary: false,
          },
        ],
        branches: [
          {
            id: `client-branch-${clientId}-1`,
            clientId,
            name: `${name} - Matriz`,
            code: 'MATRIZ',
            address: `Rua dos Clientes, ${300 + i * 100}`,
            city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza', 'Brasília'][i],
            state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'DF'][i],
            zipCode: `${40000 + i * 1111}-${400 + i * 11}`,
            isMain: true,
          },
          {
            id: `client-branch-${clientId}-2`,
            clientId,
            name: `${name} - Filial`,
            code: 'FILIAL',
            address: `Av. das Filiais, ${400 + i * 100}`,
            city: ['Campinas', 'Niterói', 'Contagem', 'Londrina', 'Caxias do Sul', 'Feira de Santana', 'Maracanaú', 'Goiânia'][i],
            state: ['SP', 'RJ', 'MG', 'PR', 'RS', 'BA', 'CE', 'GO'][i],
            zipCode: `${50000 + i * 1111}-${500 + i * 11}`,
            isMain: false,
          },
        ],
        status: randomItem(['ACTIVE', 'ACTIVE', 'INACTIVE'] as const),
        createdAt: randomDate(365),
        updatedAt: randomDate(30),
      }
    })

    // Create demo contracts
    this.contracts = [
      {
        id: 'demo-contract-1',
        companyId: demoCompany.id,
        clientId: 'demo-client-1',
        carrierId: 'demo-carrier-1',
        name: 'Contrato Transportes Rápidos - SP/RJ',
        number: 'CTR-2024-001',
        version: 1,
        status: 'ACTIVE',
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        successFeePct: 15.0,
        description: 'Contrato de frete entre São Paulo e Rio de Janeiro',
        client: this.clients.find(c => c.id === 'demo-client-1'),
        carrier: this.carriers.find(c => c.id === 'demo-carrier-1'),
        freightTables: [],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'demo-contract-2',
        companyId: demoCompany.id,
        clientId: 'demo-client-2',
        carrierId: 'demo-carrier-2',
        name: 'Contrato Logística Express - Nacional',
        number: 'CTR-2024-002',
        version: 1,
        status: 'ACTIVE',
        startDate: '2024-02-01',
        endDate: '2025-01-31',
        successFeePct: 12.5,
        description: 'Contrato de frete nacional',
        client: this.clients.find(c => c.id === 'demo-client-2'),
        carrier: this.carriers.find(c => c.id === 'demo-carrier-2'),
        freightTables: [],
        createdAt: '2024-02-01T00:00:00Z',
        updatedAt: '2024-02-01T00:00:00Z',
      },
      {
        id: 'demo-contract-3',
        companyId: demoCompany.id,
        clientId: 'demo-client-3',
        carrierId: 'demo-carrier-3',
        name: 'Contrato Cargas Brasil - Sul/Sudeste',
        number: 'CTR-2024-003',
        version: 2,
        status: 'EXPIRED',
        startDate: '2023-01-01',
        endDate: '2023-12-31',
        successFeePct: 18.0,
        description: 'Contrato de frete Sul/Sudeste (expirado)',
        client: this.clients.find(c => c.id === 'demo-client-3'),
        carrier: this.carriers.find(c => c.id === 'demo-carrier-3'),
        freightTables: [],
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-12-31T00:00:00Z',
      },
      ...Array.from({ length: 5 }, (_, i) => {
        const client = randomItem(this.clients)
        const carrier = randomItem(this.carriers)
        return {
          id: `demo-contract-${i + 4}`,
          companyId: demoCompany.id,
          clientId: client.id,
          carrierId: carrier.id,
          name: `Contrato ${client.name} - ${carrier.name} #${i + 4}`,
          number: `CTR-2024-${String(i + 4).padStart(3, '0')}`,
          version: 1,
          status: randomItem(CONTRACT_STATUSES),
          startDate: '2024-01-01',
          endDate: '2024-12-31',
          successFeePct: randomFloat(10, 20),
          description: `Contrato de frete ${client.name} - ${carrier.name}`,
          client,
          carrier,
          freightTables: [],
          createdAt: randomDate(365),
          updatedAt: randomDate(30),
        }
      }),
    ]

    // Create demo freight tables
    this.freightTables = this.contracts.slice(0, 3).map((contract, i) => ({
      id: `demo-freight-table-${i + 1}`,
      contractId: contract.id,
      version: 1,
      status: 'ACTIVE' as FreightTableStatus,
      effectiveFrom: '2024-01-01',
      effectiveTo: '2024-12-31',
      rates: [
        {
          id: `rate-${i + 1}-1`,
          weightMin: 0,
          weightMax: 1000,
          cubageMin: 0,
          cubageMax: 10,
          distanceMin: 0,
          distanceMax: 500,
          modal: 'RODOVIARIO',
          ufOrigin: 'SP',
          ufDest: 'RJ',
          ratePerKg: randomFloat(1.5, 3.0),
          ratePerM3: randomFloat(100, 200),
          ratePerKm: randomFloat(2.0, 4.0),
          minimumValue: randomFloat(50, 150),
        },
        {
          id: `rate-${i + 1}-2`,
          weightMin: 1000,
          weightMax: 5000,
          cubageMin: 10,
          cubageMax: 50,
          distanceMin: 500,
          distanceMax: 1000,
          modal: 'RODOVIARIO',
          ufOrigin: 'SP',
          ufDest: 'MG',
          ratePerKg: randomFloat(1.2, 2.5),
          ratePerM3: randomFloat(80, 180),
          ratePerKm: randomFloat(1.8, 3.5),
          minimumValue: randomFloat(100, 300),
        },
      ],
      entries: [
        {
          id: `entry-${i + 1}-1`,
          originCity: 'São Paulo',
          originState: 'SP',
          destinationCity: 'Rio de Janeiro',
          destinationState: 'RJ',
          freightType: 'NORMAL',
          weightMin: 0,
          weightMax: 1000,
          volumeMin: 0,
          volumeMax: 10,
          value: randomFloat(200, 500),
          valueType: 'FIXED',
          icms: 12,
          tolls: 50,
        },
        {
          id: `entry-${i + 1}-2`,
          originCity: 'São Paulo',
          originState: 'SP',
          destinationCity: 'Belo Horizonte',
          destinationState: 'MG',
          freightType: 'EXPRESS',
          weightMin: 1000,
          weightMax: 5000,
          volumeMin: 10,
          volumeMax: 50,
          value: randomFloat(800, 2000),
          valueType: 'PER_KG',
          icms: 12,
          tolls: 80,
        },
      ],
      createdAt: randomDate(365),
      updatedAt: randomDate(30),
    }))

    // Assign freight tables to contracts
    this.contracts.forEach((contract, i) => {
      if (this.freightTables[i]) {
        contract.freightTables = [this.freightTables[i]]
      }
    })

    // Create demo documents
    this.documents = Array.from({ length: 25 }, (_, i) => {
      const carrier = randomItem(this.carriers)
      const client = randomItem(this.clients)
      const status = randomItem(DOCUMENT_STATUSES)
      const type = randomItem(DOCUMENT_TYPES)
      const fileSize = randomRange(50000, 5000000)
      const createdAt = randomDate(60)
      return {
        id: `demo-doc-${i + 1}`,
        companyId: demoCompany.id,
        clientId: client.id,
        carrierId: carrier.id,
        type,
        status,
        fileName: `${type}_${String(i + 1).padStart(5, '0')}_${randomDate(60).split('T')[0]}.xml`,
        fileSize,
        fileUrl: `https://demo-storage.averta.com/documents/demo-doc-${i + 1}.xml`,
        parsedData: status === 'COMPLETED' ? this.generateParsedData(type, carrier, client) : undefined,
        errorMessage: status === 'FAILED' ? 'Erro ao processar XML: tag obrigatória ausente' : undefined,
        processedAt: status === 'COMPLETED' ? new Date(new Date(createdAt).getTime() + randomRange(1, 3600) * 1000).toISOString() : undefined,
        createdAt,
        updatedAt: status === 'COMPLETED' ? new Date(new Date(createdAt).getTime() + randomRange(1, 3600) * 1000).toISOString() : createdAt,
      }
    })

    // Create demo discrepancies
    this.discrepancies = Array.from({ length: 50 }, (_, i) => {
      const document = randomItem(this.documents)
      const contract = randomItem(this.contracts)
      const carrier = this.carriers.find(c => c.id === document.carrierId)
      const client = this.clients.find(c => c.id === document.clientId)
      const status = randomItem(DISCREPANCY_STATUSES)
      const severity = randomItem(DISCREPANCY_SEVERITIES)
      const type = randomItem(DISCREPANCY_TYPES)
      const expectedValue = randomFloat(100, 10000)
      const differencePercent = randomFloat(1, 50)
      const actualValue = expectedValue * (1 + (Math.random() > 0.5 ? 1 : -1) * differencePercent / 100)
      const difference = Math.abs(expectedValue - actualValue)
      const createdAt = randomDate(60)
      return {
        id: `demo-disc-${i + 1}`,
        companyId: demoCompany.id,
        documentId: document.id,
        contractId: contract.id,
        clientId: client?.id,
        carrierId: carrier?.id,
        type,
        severity,
        status,
        description: `Discrepância de ${type.toLowerCase().replace('_', ' ')} detectada no documento ${document.fileName}`,
        expectedValue,
        actualValue,
        difference,
        differencePercent,
        fieldName: type.toLowerCase().replace('_', '_'),
        suggestedAction: this.getSuggestedAction(type, severity),
        reviewedBy: status !== 'OPEN' && status !== 'IN_REVIEW' ? 'demo-user-1' : undefined,
        reviewedAt: status !== 'OPEN' && status !== 'IN_REVIEW' ? new Date(new Date(createdAt).getTime() + randomRange(3600, 86400) * 1000).toISOString() : undefined,
        createdAt,
        updatedAt: status !== 'OPEN' && status !== 'IN_REVIEW' ? new Date(new Date(createdAt).getTime() + randomRange(3600, 86400) * 1000).toISOString() : createdAt,
      }
    })

    // Create demo contests
    this.contests = Array.from({ length: 30 }, (_, i) => {
      const discrepancy = randomItem(this.discrepancies.filter(d => d.status === 'CONTESTED' || d.status === 'OPEN' || d.status === 'IN_REVIEW'))
      const carrier = this.carriers.find(c => c.id === discrepancy.carrierId)
      const document = this.documents.find(d => d.id === discrepancy.documentId)
      const status = randomItem(CONTEST_STATUSES)
      const requestedAmount = discrepancy.difference * randomFloat(1.0, 1.5)
      const createdAt = new Date(new Date(discrepancy.createdAt).getTime() + randomRange(86400, 604800) * 1000).toISOString()

      return {
        id: `demo-contest-${i + 1}`,
        companyId: demoCompany.id,
        discrepancyId: discrepancy.id,
        discrepancyIds: [discrepancy.id],
        documentId: discrepancy.documentId,
        carrierId: discrepancy.carrierId || carrier?.id || 'demo-carrier-1',
        status,
        title: `Contestação: ${discrepancy.type} - ${document?.fileName || 'Doc'}`,
        description: `Contestação referente à discrepância de ${discrepancy.type.toLowerCase().replace('_', ' ')} no valor de R$ ${discrepancy.difference.toFixed(2)}`,
        requestedAmount,
        offeredAmount: status === 'NEGOTIATING' || status === 'ACCEPTED' || status === 'PARTIAL' ? requestedAmount * randomFloat(0.5, 0.9) : undefined,
        agreedAmount: status === 'ACCEPTED' || status === 'PARTIAL' ? requestedAmount * randomFloat(0.6, 1.0) : undefined,
        evidenceFiles: Array.from({ length: randomRange(0, 3) }, (_, j) => ({
          id: `evidence-${i + 1}-${j + 1}`,
          fileName: `comprovante_${j + 1}.pdf`,
          fileUrl: `https://demo-storage.averta.com/evidence/evidence-${i + 1}-${j + 1}.pdf`,
          fileSize: randomRange(100000, 1000000),
          type: 'application/pdf',
          uploadedAt: new Date(new Date(createdAt).getTime() + randomRange(0, 86400) * 1000).toISOString(),
        })),
        items: [discrepancy],
        sentAt: status !== 'DRAFT' ? new Date(new Date(createdAt).getTime() + randomRange(86400, 604800) * 1000).toISOString() : undefined,
        acknowledgedAt: ['ACKNOWLEDGED', 'NEGOTIATING', 'ACCEPTED', 'PARTIAL', 'REJECTED'].includes(status) ? new Date(new Date(createdAt).getTime() + randomRange(172800, 1209600) * 1000).toISOString() : undefined,
        resolvedAt: ['ACCEPTED', 'PARTIAL', 'REJECTED'].includes(status) ? new Date(new Date(createdAt).getTime() + randomRange(604800, 2592000) * 1000).toISOString() : undefined,
        expiresAt: new Date(new Date(createdAt).getTime() + 2592000 * 1000).toISOString(), // 30 days
        createdAt,
        updatedAt: status !== 'DRAFT' ? new Date(new Date(createdAt).getTime() + randomRange(86400, 2592000) * 1000).toISOString() : createdAt,
      }
    })

    // Create demo payments
    this.payments = this.contests
      .filter(c => c.status === 'ACCEPTED' || c.status === 'PARTIAL')
      .slice(0, 10)
      .map((contest, i) => ({
        id: `demo-payment-${i + 1}`,
        contestId: contest.id,
        amount: contest.agreedAmount || contest.requestedAmount * 0.8,
        paymentDate: new Date(new Date(contest.resolvedAt || contest.createdAt).getTime() + randomRange(86400, 604800) * 1000).toISOString(),
        paymentMethod: randomItem(['PIX', 'TED', 'BOLETO', 'DEPOSITO'] as const),
        reference: `PAG-${contest.id}-${i + 1}`,
        status: 'COMPLETED' as const,
        createdAt: new Date(new Date(contest.resolvedAt || contest.createdAt).getTime() + randomRange(86400, 604800) * 1000).toISOString(),
      }))

    // Create demo scheduled reports
    this.scheduledReports = [
      {
        id: 'demo-schedule-1',
        companyId: demoCompany.id,
        name: 'Relatório Diário de Discrepâncias',
        description: 'Envio diário por e-mail com resumo de discrepâncias',
        format: 'PDF',
        frequency: 'DAILY',
        hour: 8,
        minute: 0,
        filters: { period: '1d' },
        recipients: ['admin@averta.com', 'gerente@averta.com'],
        isActive: true,
        lastRunAt: new Date(Date.now() - 86400000).toISOString(),
        nextRunAt: new Date(Date.now() + 86400000).toISOString(),
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'demo-schedule-2',
        companyId: demoCompany.id,
        name: 'Relatório Semanal de Recuperação',
        description: 'Relatório semanal de valores recuperados por transportadora',
        format: 'EXCEL',
        frequency: 'WEEKLY',
        dayOfWeek: 1, // Monday
        hour: 9,
        minute: 0,
        filters: { period: '7d' },
        recipients: ['admin@averta.com', 'financeiro@averta.com'],
        isActive: true,
        lastRunAt: new Date(Date.now() - 604800000).toISOString(),
        nextRunAt: new Date(Date.now() + 604800000).toISOString(),
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'demo-schedule-3',
        companyId: demoCompany.id,
        name: 'Relatório Mensal de Performance',
        description: 'Performance mensal por transportadora e regra',
        format: 'PDF',
        frequency: 'MONTHLY',
        dayOfMonth: 1,
        hour: 10,
        minute: 0,
        filters: { period: '30d' },
        recipients: ['diretoria@averta.com'],
        isActive: false,
        lastRunAt: new Date(Date.now() - 2592000000).toISOString(),
        nextRunAt: new Date(Date.now() + 2592000000).toISOString(),
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: new Date().toISOString(),
      },
    ]
  }

  private generateParsedData(_type: DocumentType, carrier: Carrier, client: Client): ParsedDocumentData {
    const baseValue = randomFloat(1000, 50000)
    return {
      chave_acesso: `${Math.floor(10000000000000000000)}${Math.random().toString().substr(2, 24)}`,
      numero: `${Math.floor(1000 + Math.random() * 9000)}`,
      serie: `${Math.floor(1 + Math.random() * 999)}`,
      data_emissao: new Date().toISOString().split('T')[0],
      valor_total: baseValue,
      cnpj_emitente: carrier.cnpj,
      nome_emitente: carrier.name,
      cnpj_destinatario: client.cnpj,
      nome_destinatario: client.name,
      cfop: '5353',
      natureza_operacao: 'Prestação de Serviço de Transporte',
      peso_bruto: randomFloat(100, 50000),
      peso_liquido: randomFloat(100, 45000),
      volumes: randomRange(1, 50),
      valor_frete: randomFloat(100, 5000),
      valor_icms: baseValue * 0.12,
      valor_ipi: 0,
      valor_pis: baseValue * 0.0165,
      valor_cofins: baseValue * 0.076,
    }
  }

  private getSuggestedAction(type: DiscrepancyType, severity: DiscrepancySeverity): string {
    const actions: Record<DiscrepancyType, string> = {
      FREIGHT_VALUE: 'Verificar tabela de frete aplicada e recalcular',
      ICMS: 'Confirmar alíquota de ICMS interestadual',
      TOLLS: 'Solicitar comprovantes de pedágio da transportadora',
      WEIGHT: 'Conferir pesagem na origem e destino',
      VOLUME: 'Verificar cubagem declarada vs. real',
      DIMENSIONS: 'Conferir dimensões da carga com a transportadora',
      DUPLICATE: 'Identificar e cancelar documento duplicado',
      MISSING_DOCUMENT: 'Solicitar documento faltante à transportadora',
      INVALID_CNPJ: 'Validar CNPJ na Receita Federal',
      ROUTE_MISMATCH: 'Verificar rota percorrida vs. contratada',
      OTHER: 'Analisar caso a caso com a equipe operacional',
    }
    const baseAction = actions[type] || 'Analisar discrepância'
    return severity === 'CRITICAL' ? `[URGENTE] ${baseAction}` : baseAction
  }

  // ===== AUTH =====
  getDemoUser(): AuthUser {
    return this.users[0]
  }

  getDemoTokens() {
    return {
      accessToken: 'demo-access-token',
      refreshToken: 'demo-refresh-token',
      expiresIn: 3600,
      tokenType: 'bearer',
    }
  }

  // ===== COMPANIES =====
  getCompanies(page = 1, size = 20) {
    const start = (page - 1) * size
    return {
      items: this.companies.slice(start, start + size),
      total: this.companies.length,
      page,
      size,
      pages: Math.ceil(this.companies.length / size),
    }
  }

  getCompany(id: string) {
    return this.companies.find((c) => c.id === id) || this.companies[0]
  }

  createCompany(data: Partial<typeof this.companies[0]>) {
    const company = {
      id: generateId('demo-company'),
      name: data.name || 'Nova Empresa',
      cnpj: data.cnpj || '',
      email: data.email || '',
      phone: data.phone || '',
      address: data.address || '',
      city: data.city || '',
      state: data.state || '',
      zipCode: data.zipCode || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.companies.push(company)
    return company
  }

  updateCompany(id: string, data: Partial<typeof this.companies[0]>) {
    const idx = this.companies.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.companies[idx] = { ...this.companies[idx], ...data, updatedAt: new Date().toISOString() }
      return this.companies[idx]
    }
    return this.companies[0]
  }

  deleteCompany(id: string) {
    this.companies = this.companies.filter((c) => c.id !== id)
    return { message: 'Empresa removida' }
  }

  // ===== USERS =====
  getUsers(page = 1, size = 20) {
    const start = (page - 1) * size
    return {
      items: this.users.slice(start, start + size),
      total: this.users.length,
      page,
      size,
      pages: Math.ceil(this.users.length / size),
    }
  }

  getUser(id: string) {
    return this.users.find((u) => u.id === id) || this.users[0]
  }

  createUser(data: Partial<AuthUser>) {
    const user: AuthUser = {
      id: generateId('demo-user'),
      email: data.email || '',
      fullName: data.fullName || '',
      role: data.role || 'CLIENT',
      status: data.status || 'ACTIVE',
      companyId: data.companyId || this.companies[0].id,
      clientId: data.clientId,
      avatarUrl: data.avatarUrl,
      lastLoginAt: new Date().toISOString(),
      createdAt: new Date().toISOString(),
    }
    this.users.push(user)
    return user
  }

  updateUser(id: string, data: Partial<AuthUser>) {
    const idx = this.users.findIndex((u) => u.id === id)
    if (idx >= 0) {
      this.users[idx] = { ...this.users[idx], ...data, lastLoginAt: new Date().toISOString() }
      return this.users[idx]
    }
    return this.users[0]
  }

  deleteUser(id: string) {
    this.users = this.users.filter((u) => u.id !== id)
    return { message: 'Usuário removido' }
  }

  // ===== CARRIERS =====
  getCarriers(page = 1, size = 20) {
    const start = (page - 1) * size
    return {
      items: this.carriers.slice(start, start + size),
      total: this.carriers.length,
      page,
      size,
      pages: Math.ceil(this.carriers.length / size),
    }
  }

  getCarrier(id: string) {
    return this.carriers.find((c) => c.id === id) || this.carriers[0]
  }

  createCarrier(data: Partial<Carrier>) {
    const carrier: Carrier = {
      id: generateId('demo-carrier'),
      companyId: data.companyId || this.companies[0].id,
      name: data.name || '',
      cnpj: data.cnpj || '',
      email: data.email,
      phone: data.phone,
      anttRegistry: data.anttRegistry,
      address: data.address,
      city: data.city,
      state: data.state,
      zipCode: data.zipCode,
      contacts: data.contacts || [],
      branches: data.branches || [],
      status: data.status || 'ACTIVE',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.carriers.push(carrier)
    return carrier
  }

  updateCarrier(id: string, data: Partial<Carrier>) {
    const idx = this.carriers.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.carriers[idx] = { ...this.carriers[idx], ...data, updatedAt: new Date().toISOString() }
      return this.carriers[idx]
    }
    return this.carriers[0]
  }

  deleteCarrier(id: string) {
    this.carriers = this.carriers.filter((c) => c.id !== id)
    return { message: 'Transportadora removida' }
  }

  // ===== CLIENTS =====
  getClients(page = 1, size = 20) {
    const start = (page - 1) * size
    return {
      items: this.clients.slice(start, start + size),
      total: this.clients.length,
      page,
      size,
      pages: Math.ceil(this.clients.length / size),
    }
  }

  getClient(id: string) {
    return this.clients.find((c) => c.id === id) || this.clients[0]
  }

  createClient(data: Partial<Client>) {
    const client: Client = {
      id: generateId('demo-client'),
      companyId: data.companyId || this.companies[0].id,
      name: data.name || '',
      cnpj: data.cnpj || '',
      email: data.email,
      phone: data.phone,
      address: data.address,
      city: data.city,
      state: data.state,
      zipCode: data.zipCode,
      contacts: data.contacts || [],
      branches: data.branches || [],
      status: data.status || 'ACTIVE',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.clients.push(client)
    return client
  }

  updateClient(id: string, data: Partial<Client>) {
    const idx = this.clients.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.clients[idx] = { ...this.clients[idx], ...data, updatedAt: new Date().toISOString() }
      return this.clients[idx]
    }
    return this.clients[0]
  }

  deleteClient(id: string) {
    this.clients = this.clients.filter((c) => c.id !== id)
    return { message: 'Cliente removido' }
  }

  // ===== CONTRACTS =====
  getContracts(page = 1, size = 20) {
    const start = (page - 1) * size
    return {
      items: this.contracts.slice(start, start + size),
      total: this.contracts.length,
      page,
      size,
      pages: Math.ceil(this.contracts.length / size),
    }
  }

  getContract(id: string) {
    return this.contracts.find((c) => c.id === id) || this.contracts[0]
  }

  createContract(data: Partial<Contract>) {
    const contract: Contract = {
      id: generateId('demo-contract'),
      companyId: data.companyId || this.companies[0].id,
      clientId: data.clientId || this.clients[0].id,
      carrierId: data.carrierId || this.carriers[0].id,
      name: data.name || '',
      number: data.number || `CTR-${Date.now()}`,
      version: data.version || 1,
      status: data.status || 'DRAFT',
      startDate: data.startDate || new Date().toISOString().split('T')[0],
      endDate: data.endDate,
      successFeePct: data.successFeePct || 15,
      description: data.description,
      client: this.clients.find(c => c.id === data.clientId),
      carrier: this.carriers.find(c => c.id === data.carrierId),
      freightTables: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.contracts.push(contract)
    return contract
  }

  updateContract(id: string, data: Partial<Contract>) {
    const idx = this.contracts.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.contracts[idx] = {
        ...this.contracts[idx],
        ...data,
        client: data.clientId ? this.clients.find(c => c.id === data.clientId) : this.contracts[idx].client,
        carrier: data.carrierId ? this.carriers.find(c => c.id === data.carrierId) : this.contracts[idx].carrier,
        updatedAt: new Date().toISOString()
      }
      return this.contracts[idx]
    }
    return this.contracts[0]
  }

  deleteContract(id: string) {
    this.contracts = this.contracts.filter((c) => c.id !== id)
    return { message: 'Contrato removido' }
  }

  // ===== DOCUMENTS =====
  getDocuments(page = 1, size = 20, filters?: DocumentFilters) {
    let docs = [...this.documents]

    if (filters?.status?.length) {
      docs = docs.filter((d) => filters.status!.includes(d.status))
    }
    if (filters?.documentType?.length) {
      docs = docs.filter((d) => filters.documentType!.includes(d.type))
    }
    if (filters?.clientId) {
      docs = docs.filter((d) => d.clientId === filters.clientId)
    }
    if (filters?.carrierId) {
      docs = docs.filter((d) => d.carrierId === filters.carrierId)
    }
    if (filters?.dateFrom) {
      docs = docs.filter((d) => d.createdAt >= filters.dateFrom!)
    }
    if (filters?.dateTo) {
      docs = docs.filter((d) => d.createdAt <= filters.dateTo!)
    }
    if (filters?.search) {
      const search = filters.search.toLowerCase()
      docs = docs.filter(
        (d) =>
          d.fileName.toLowerCase().includes(search) ||
          (d.parsedData?.nome_emitente?.toLowerCase().includes(search) ?? false) ||
          (d.parsedData?.nome_destinatario?.toLowerCase().includes(search) ?? false)
      )
    }

    // Sort by createdAt desc
    docs.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    const start = (page - 1) * size
    return {
      items: docs.slice(start, start + size),
      total: docs.length,
      page,
      size,
      pages: Math.ceil(docs.length / size),
    }
  }

  getDocument(id: string) {
    return this.documents.find((d) => d.id === id) || this.documents[0]
  }

  uploadDocument(file: File) {
    const carrier = randomItem(this.carriers)
    const client = randomItem(this.clients)
    const type = randomItem(DOCUMENT_TYPES)

    const doc: Document = {
      id: generateId('demo-doc'),
      companyId: this.companies[0].id,
      clientId: client.id,
      carrierId: carrier.id,
      type,
      status: 'PENDING',
      fileName: file.name,
      fileSize: file.size,
      fileUrl: `https://demo-storage.averta.com/documents/${generateId('doc')}.xml`,
      parsedData: undefined,
      errorMessage: undefined,
      processedAt: undefined,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.documents.unshift(doc)

    // Simulate async processing
    setTimeout(() => {
      const idx = this.documents.findIndex(d => d.id === doc.id)
      if (idx >= 0) {
        this.documents[idx] = {
          ...this.documents[idx],
          status: 'PROCESSING',
          updatedAt: new Date().toISOString(),
        }
        setTimeout(() => {
          const idx2 = this.documents.findIndex(d => d.id === doc.id)
          if (idx2 >= 0) {
            const success = Math.random() > 0.1 // 90% success rate
            this.documents[idx2] = {
              ...this.documents[idx2],
              status: success ? 'COMPLETED' : 'FAILED',
              parsedData: success ? this.generateParsedData(type, carrier, client) : undefined,
              errorMessage: success ? undefined : 'Erro ao processar XML: tag obrigatória ausente',
              processedAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            }

            // If completed, create some discrepancies
            if (success && Math.random() > 0.3) {
              const numDisc = randomRange(1, 5)
              for (let i = 0; i < numDisc; i++) {
                this.createDiscrepancyFromDocument(this.documents[idx2])
              }
            }
          }
        }, 1000)
      }
    }, 500)

    return doc
  }

  private createDiscrepancyFromDocument(doc: Document) {
    const contract = randomItem(this.contracts)
    const carrier = this.carriers.find(c => c.id === doc.carrierId)
    const client = this.clients.find(c => c.id === doc.clientId)
    const type = randomItem(DISCREPANCY_TYPES)
    const severity = randomItem(DISCREPANCY_SEVERITIES)
    const expectedValue = randomFloat(100, 10000)
    const differencePercent = randomFloat(1, 50)
    const actualValue = expectedValue * (1 + (Math.random() > 0.5 ? 1 : -1) * differencePercent / 100)
    const difference = Math.abs(expectedValue - actualValue)

    const discrepancy: Discrepancy = {
      id: generateId('demo-disc'),
      companyId: this.companies[0].id,
      documentId: doc.id,
      contractId: contract.id,
      clientId: client?.id,
      carrierId: carrier?.id,
      type,
      severity,
      status: 'OPEN',
      description: `Discrepância de ${type.toLowerCase().replace('_', ' ')} detectada no documento ${doc.fileName}`,
      expectedValue,
      actualValue,
      difference,
      differencePercent,
      fieldName: type.toLowerCase().replace('_', '_'),
      suggestedAction: this.getSuggestedAction(type, severity),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.discrepancies.unshift(discrepancy)
    return discrepancy
  }

  reprocessDocument(id: string) {
    const idx = this.documents.findIndex((d) => d.id === id)
    if (idx >= 0) {
      this.documents[idx] = {
        ...this.documents[idx],
        status: 'PROCESSING',
        errorMessage: undefined,
        updatedAt: new Date().toISOString()
      }

      setTimeout(() => {
        const idx2 = this.documents.findIndex(d => d.id === id)
        if (idx2 >= 0) {
          const carrier = this.carriers.find(c => c.id === this.documents[idx2].carrierId)
          const client = this.clients.find(c => c.id === this.documents[idx2].clientId)
          const type = this.documents[idx2].type
          const success = Math.random() > 0.1
          this.documents[idx2] = {
            ...this.documents[idx2],
            status: success ? 'COMPLETED' : 'FAILED',
            parsedData: success ? this.generateParsedData(type, carrier!, client!) : undefined,
            errorMessage: success ? undefined : 'Erro ao reprocessar XML',
            processedAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
        }
      }, 1000)

      return this.documents[idx]
    }
    return this.documents[0]
  }

  // ===== DISCREPANCIES =====
  getDiscrepancies(page = 1, size = 20, filters?: {
    status?: DiscrepancyStatus[]
    severity?: DiscrepancySeverity[]
    type?: DiscrepancyType[]
    clientId?: string
    carrierId?: string
    contractId?: string
    documentId?: string
    dateFrom?: string
    dateTo?: string
    search?: string
  }) {
    let disc = [...this.discrepancies]

    if (filters?.status?.length) {
      disc = disc.filter((d) => filters.status!.includes(d.status))
    }
    if (filters?.severity?.length) {
      disc = disc.filter((d) => filters.severity!.includes(d.severity))
    }
    if (filters?.type?.length) {
      disc = disc.filter((d) => filters.type!.includes(d.type))
    }
    if (filters?.clientId) {
      disc = disc.filter((d) => d.clientId === filters.clientId)
    }
    if (filters?.carrierId) {
      disc = disc.filter((d) => d.carrierId === filters.carrierId)
    }
    if (filters?.contractId) {
      disc = disc.filter((d) => d.contractId === filters.contractId)
    }
    if (filters?.documentId) {
      disc = disc.filter((d) => d.documentId === filters.documentId)
    }
    if (filters?.dateFrom) {
      disc = disc.filter((d) => d.createdAt >= filters.dateFrom!)
    }
    if (filters?.dateTo) {
      disc = disc.filter((d) => d.createdAt <= filters.dateTo!)
    }
    if (filters?.search) {
      const search = filters.search.toLowerCase()
      disc = disc.filter(
        (d) =>
          d.description.toLowerCase().includes(search) ||
          d.fieldName.toLowerCase().includes(search) ||
          d.type.toLowerCase().includes(search)
      )
    }

    // Sort by createdAt desc
    disc.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    const start = (page - 1) * size
    return {
      items: disc.slice(start, start + size),
      total: disc.length,
      page,
      size,
      pages: Math.ceil(disc.length / size),
    }
  }

  getDiscrepancySummary(): DiscrepancySummary {
    const byStatus = this.discrepancies.reduce(
      (acc, d) => {
        acc[d.status] = (acc[d.status] || 0) + 1
        return acc
      },
      {} as Record<DiscrepancyStatus, number>
    )

    const bySeverity = this.discrepancies.reduce(
      (acc, d) => {
        acc[d.severity] = (acc[d.severity] || 0) + 1
        return acc
      },
      {} as Record<DiscrepancySeverity, number>
    )

    const byRule = this.discrepancies.reduce(
      (acc, d) => {
        acc[d.type] = (acc[d.type] || 0) + 1
        return acc
      },
      {} as Record<DiscrepancyType, number>
    )

    const totalRecovered = this.discrepancies
      .filter((d) => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED')
      .reduce((sum, d) => sum + d.difference, 0)

    const totalContested = this.discrepancies
      .filter((d) => d.status === 'CONTESTED')
      .reduce((sum, d) => sum + d.difference, 0)

    return {
      total: this.discrepancies.length,
      by_status: {
        OPEN: byStatus.OPEN || 0,
        IN_REVIEW: byStatus.IN_REVIEW || 0,
        CONTESTED: byStatus.CONTESTED || 0,
        APPROVED: byStatus.APPROVED || 0,
        REJECTED: byStatus.REJECTED || 0,
        PAID: byStatus.PAID || 0,
        CLOSED: byStatus.CLOSED || 0,
      },
      by_severity: {
        LOW: bySeverity.LOW || 0,
        MEDIUM: bySeverity.MEDIUM || 0,
        HIGH: bySeverity.HIGH || 0,
        CRITICAL: bySeverity.CRITICAL || 0,
      },
      by_rule: DISCREPANCY_TYPES.reduce(
        (acc, t) => {
          acc[t] = byRule[t] || 0
          return acc
        },
        {} as Record<DiscrepancyType, number>
      ),
      total_recovered: Number(totalRecovered.toFixed(2)),
      total_contested: Number(totalContested.toFixed(2)),
    }
  }

  getDiscrepancy(id: string) {
    return this.discrepancies.find((d) => d.id === id) || this.discrepancies[0]
  }

  bulkUpdateStatus(ids: string[], status: DiscrepancyStatus) {
    ids.forEach((id) => {
      const idx = this.discrepancies.findIndex((d) => d.id === id)
      if (idx >= 0) {
        this.discrepancies[idx] = {
          ...this.discrepancies[idx],
          status,
          reviewedBy: 'demo-user-1',
          reviewedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      }
    })
    return { updated: ids.length, message: `${ids.length} discrepâncias atualizadas para ${status}` }
  }

  reviewDiscrepancy(id: string, status: DiscrepancyStatus, _reviewNotes?: string) {
    const idx = this.discrepancies.findIndex((d) => d.id === id)
    if (idx >= 0) {
      this.discrepancies[idx] = {
        ...this.discrepancies[idx],
        status,
        reviewedBy: 'demo-user-1',
        reviewedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      return this.discrepancies[idx]
    }
    return this.discrepancies[0]
  }

  bulkReviewDiscrepancies(ids: string[], status: DiscrepancyStatus, _notes?: string) {
    ids.forEach((id) => {
      const idx = this.discrepancies.findIndex((d) => d.id === id)
      if (idx >= 0) {
        this.discrepancies[idx] = {
          ...this.discrepancies[idx],
          status,
          reviewedBy: 'demo-user-1',
          reviewedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      }
    })
    return { updated: ids.length, message: `${ids.length} discrepâncias revisadas para ${status}` }
  }

  createContestFromDiscrepancies(data: { discrepancyIds: string[]; title: string; description: string }) {
    const firstDiscrepancy = this.discrepancies.find(d => d.id === data.discrepancyIds[0])
    const carrier = firstDiscrepancy ? this.carriers.find(c => c.id === firstDiscrepancy.carrierId) : this.carriers[0]

    const contest: Contest = {
      id: generateId('demo-contest'),
      companyId: this.companies[0].id,
      discrepancyId: data.discrepancyIds[0],
      discrepancyIds: data.discrepancyIds,
      documentId: firstDiscrepancy?.documentId || '',
      carrierId: carrier?.id || this.carriers[0].id,
      status: 'DRAFT',
      title: data.title,
      description: data.description,
      requestedAmount: firstDiscrepancy ? data.discrepancyIds.reduce((sum, id) => {
        const d = this.discrepancies.find(disc => disc.id === id)
        return sum + (d?.difference || 0)
      }, 0) : 0,
      offeredAmount: undefined,
      agreedAmount: undefined,
      evidenceFiles: [],
      items: data.discrepancyIds.map(id => this.discrepancies.find(d => d.id === id)).filter(Boolean) as Discrepancy[],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.contests.unshift(contest)

    // Update discrepancies status to CONTESTED
    data.discrepancyIds.forEach(id => {
      const idx = this.discrepancies.findIndex(d => d.id === id)
      if (idx >= 0) {
        this.discrepancies[idx] = {
          ...this.discrepancies[idx],
          status: 'CONTESTED',
          updatedAt: new Date().toISOString(),
        }
      }
    })

    return { contestId: contest.id }
  }

  // ===== CONTESTS =====
  getContests(page = 1, size = 20, filters?: {
    status?: ContestStatus[]
    carrierId?: string
    dateFrom?: string
    dateTo?: string
    search?: string
  }) {
    let contests = [...this.contests]

    if (filters?.status?.length) {
      contests = contests.filter((c) => filters.status!.includes(c.status))
    }
    if (filters?.carrierId) {
      contests = contests.filter((c) => c.carrierId === filters.carrierId)
    }
    if (filters?.dateFrom) {
      contests = contests.filter((c) => c.createdAt >= filters.dateFrom!)
    }
    if (filters?.dateTo) {
      contests = contests.filter((c) => c.createdAt <= filters.dateTo!)
    }
    if (filters?.search) {
      const search = filters.search.toLowerCase()
      contests = contests.filter(
        (c) =>
          c.title.toLowerCase().includes(search) ||
          c.description.toLowerCase().includes(search)
      )
    }

    // Sort by createdAt desc
    contests.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    const start = (page - 1) * size
    return {
      items: contests.slice(start, start + size),
      total: contests.length,
      page,
      size,
      pages: Math.ceil(contests.length / size),
    }
  }

  getContest(id: string) {
    return this.contests.find((c) => c.id === id) || this.contests[0]
  }

  createContest(data: {
    discrepancyIds: string[]
    carrierId: string
    title: string
    description: string
    requestedAmount: number
    evidenceFiles?: File[]
  }) {
    const discrepancy = this.discrepancies.find(d => d.id === data.discrepancyIds[0])
    // const _carrier = this.carriers.find(c => c.id === data.carrierId) // Used for validation if needed
    // const _document = discrepancy ? this.documents.find(d => d.id === discrepancy.documentId) : undefined

    const contest: Contest = {
      id: generateId('demo-contest'),
      companyId: this.companies[0].id,
      discrepancyId: data.discrepancyIds[0],
      discrepancyIds: data.discrepancyIds,
      documentId: discrepancy?.documentId || '',
      carrierId: data.carrierId,
      status: 'DRAFT',
      title: data.title,
      description: data.description,
      requestedAmount: data.requestedAmount,
      offeredAmount: undefined,
      agreedAmount: undefined,
      evidenceFiles: data.evidenceFiles?.map((file, _i) => ({
        id: `evidence-${generateId('ev')}`,
        fileName: file.name,
        fileUrl: `https://demo-storage.averta.com/evidence/${file.name}`,
        fileSize: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
      })) || [],
      items: discrepancy ? [discrepancy] : [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.contests.unshift(contest)

    // Update discrepancy status to CONTESTED
    if (discrepancy) {
      const discIdx = this.discrepancies.findIndex(d => d.id === discrepancy.id)
      if (discIdx >= 0) {
        this.discrepancies[discIdx] = {
          ...this.discrepancies[discIdx],
          status: 'CONTESTED',
          updatedAt: new Date().toISOString(),
        }
      }
    }

    return contest
  }

  sendContest(id: string) {
    const idx = this.contests.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.contests[idx] = {
        ...this.contests[idx],
        status: 'SENT',
        sentAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      return this.contests[idx]
    }
    return this.contests[0]
  }

  negotiateContest(id: string, data: { offeredAmount: number; message: string }) {
    const idx = this.contests.findIndex((c) => c.id === id)
    if (idx >= 0) {
      this.contests[idx] = {
        ...this.contests[idx],
        offeredAmount: data.offeredAmount,
        status: 'NEGOTIATING',
        acknowledgedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      return this.contests[idx]
    }
    return this.contests[0]
  }

  // ===== PAYMENTS =====
  createPayment(contestId: string, data: { amount: number; paymentMethod: string; reference: string }) {
    const contest = this.contests.find(c => c.id === contestId)

    const payment: ContestPayment = {
      id: generateId('demo-payment'),
      contestId,
      amount: data.amount,
      paymentDate: new Date().toISOString(),
      paymentMethod: data.paymentMethod,
      reference: data.reference,
      status: 'COMPLETED',
      createdAt: new Date().toISOString(),
    }
    this.payments.push(payment)

    // Update contest status
    if (contest) {
      const idx = this.contests.findIndex(c => c.id === contestId)
      if (idx >= 0) {
        this.contests[idx] = {
          ...this.contests[idx],
          status: 'ACCEPTED',
          agreedAmount: data.amount,
          resolvedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
      }
    }

    return payment
  }

  // ===== REPORTS =====
  getDashboardReport(): DashboardKPIs {
    const totalDiscrepancies = this.discrepancies.length
    const openDiscrepancies = this.discrepancies.filter(d => d.status === 'OPEN' || d.status === 'IN_REVIEW').length
    const contestedAmount = this.discrepancies.filter(d => d.status === 'CONTESTED').reduce((sum, d) => sum + d.difference, 0)
    const recoveredAmount = this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').reduce((sum, d) => sum + d.difference, 0)
    const documentsProcessed = this.documents.filter(d => d.status === 'COMPLETED').length
    const documentsPending = this.documents.filter(d => d.status === 'PENDING' || d.status === 'PROCESSING').length

    return {
      totalDiscrepancies,
      openDiscrepancies,
      contestedAmount: Number(contestedAmount.toFixed(2)),
      recoveredAmount: Number(recoveredAmount.toFixed(2)),
      recoveryRate: totalDiscrepancies > 0 ? Number((this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').length / totalDiscrepancies * 100).toFixed(1)) : 0,
      documentsProcessed,
      documentsPending,
      avgResolutionTime: 12,
      trends: {
        discrepancies: [
          { date: '2024-01', count: 45 },
          { date: '2024-02', count: 52 },
          { date: '2024-03', count: 38 },
          { date: '2024-04', count: 61 },
          { date: '2024-05', count: 68 },
          { date: '2024-06', count: 76 },
        ],
        recovered: [
          { date: '2024-01', amount: 120000 },
          { date: '2024-02', amount: 135000 },
          { date: '2024-03', amount: 110000 },
          { date: '2024-04', amount: 145000 },
          { date: '2024-05', amount: 160000 },
          { date: '2024-06', amount: 180000 },
        ],
      },
    }
  }

  getReportsDashboard(): ReportsDashboardResponse {
    const totalRecovered = this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').reduce((sum, d) => sum + d.difference, 0)
    const pendingContests = this.contests.filter(c => c.status === 'SENT' || c.status === 'ACKNOWLEDGED' || c.status === 'NEGOTIATING').length

    return {
      kpis: {
        total_documents: this.documents.length,
        total_discrepancies: this.discrepancies.length,
        total_recovered: Number(totalRecovered.toFixed(2)),
        pending_contests: pendingContests,
        success_rate: this.discrepancies.length > 0 ? Number((this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').length / this.discrepancies.length * 100).toFixed(1)) : 0,
      },
      top_carriers: this.carriers.slice(0, 5).map(c => ({
        carrier_name: c.name,
        count: this.discrepancies.filter(d => d.carrierId === c.id).length,
        value: this.discrepancies.filter(d => d.carrierId === c.id).reduce((sum, d) => sum + d.difference, 0),
      })),
      top_rules: DISCREPANCY_TYPES.slice(0, 5).map(t => ({
        rule_code: t,
        count: this.discrepancies.filter(d => d.type === t).length,
        total_difference: this.discrepancies.filter(d => d.type === t).reduce((sum, d) => sum + d.difference, 0),
      })),
      time_series: [
        { date: '2024-01', discrepancies: 45, recovered: 120000 },
        { date: '2024-02', discrepancies: 52, recovered: 135000 },
        { date: '2024-03', discrepancies: 38, recovered: 110000 },
        { date: '2024-04', discrepancies: 61, recovered: 145000 },
        { date: '2024-05', discrepancies: 68, recovered: 160000 },
        { date: '2024-06', discrepancies: 76, recovered: 180000 },
      ],
    }
  }

  generatePDF(_type: string) {
    return new Blob([`%PDF-1.4 mock pdf content`], { type: 'application/pdf' })
  }

  generateExcel(_type: string) {
    return new Blob([`mock excel content`], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  }

  getRecoveryReport(filters?: { period?: string; dateFrom?: string; dateTo?: string }): RecoveryReport {
    return {
      id: generateId('demo-recovery'),
      period: filters?.period || '30d',
      totalDiscrepancies: this.discrepancies.length,
      totalContested: this.discrepancies.filter(d => d.status === 'CONTESTED').length,
      totalRecovered: this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').reduce((sum, d) => sum + d.difference, 0),
      recoveryRate: this.discrepancies.length > 0 ? this.discrepancies.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').length / this.discrepancies.length * 100 : 0,
      byCarrier: this.carriers.map(c => ({
        carrierId: c.id,
        carrierName: c.name,
        count: this.discrepancies.filter(d => d.carrierId === c.id).length,
        recovered: this.discrepancies.filter(d => d.carrierId === c.id && (d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED')).reduce((sum, d) => sum + d.difference, 0),
      })),
      byRule: DISCREPANCY_TYPES.map(t => ({
        ruleCode: t,
        count: this.discrepancies.filter(d => d.type === t).length,
        recovered: this.discrepancies.filter(d => d.type === t && (d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED')).reduce((sum, d) => sum + d.difference, 0),
      })),
      createdAt: new Date().toISOString(),
    }
  }

  getCarrierPerformanceReport(filters?: { carrierIds?: string[]; dateFrom?: string; dateTo?: string }): CarrierPerformanceReport[] {
    const carriers = filters?.carrierIds
      ? this.carriers.filter(c => filters.carrierIds!.includes(c.id))
      : this.carriers

    return carriers.map(c => {
      const carrierDiscs = this.discrepancies.filter(d => d.carrierId === c.id)
      return {
        carrierId: c.id,
        carrierName: c.name,
        totalDiscrepancies: carrierDiscs.length,
        totalContested: carrierDiscs.filter(d => d.status === 'CONTESTED').length,
        totalRecovered: carrierDiscs.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').reduce((sum, d) => sum + d.difference, 0),
        recoveryRate: carrierDiscs.length > 0 ? carrierDiscs.filter(d => d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED').length / carrierDiscs.length * 100 : 0,
        avgResolutionTime: 12,
        topRules: DISCREPANCY_TYPES.slice(0, 3).map(t => ({
          ruleCode: t,
          count: carrierDiscs.filter(d => d.type === t).length,
          recovered: carrierDiscs.filter(d => d.type === t && (d.status === 'APPROVED' || d.status === 'PAID' || d.status === 'CLOSED')).reduce((sum, d) => sum + d.difference, 0),
        })),
      }
    })
  }

  // ===== SCHEDULED REPORTS =====
  getScheduledReports(page = 1, size = 20): ScheduledReportListResponse {
    const start = (page - 1) * size
    return {
      items: this.scheduledReports.slice(start, start + size),
      total: this.scheduledReports.length,
      page,
      size,
      pages: Math.ceil(this.scheduledReports.length / size),
    }
  }

  getScheduledReport(id: string) {
    return this.scheduledReports.find(r => r.id === id) || this.scheduledReports[0]
  }

  createSchedule(data: Partial<ScheduledReport>) {
    const schedule: ScheduledReport = {
      id: generateId('demo-schedule'),
      companyId: this.companies[0].id,
      name: data.name || 'Novo Relatório Agendado',
      description: data.description,
      format: data.format || 'PDF',
      frequency: data.frequency || 'DAILY',
      dayOfWeek: data.dayOfWeek,
      dayOfMonth: data.dayOfMonth,
      hour: data.hour || 8,
      minute: data.minute || 0,
      filters: data.filters || {},
      recipients: data.recipients || [],
      isActive: data.isActive ?? true,
      lastRunAt: undefined,
      nextRunAt: new Date(Date.now() + 86400000).toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    this.scheduledReports.push(schedule)
    return schedule
  }

  updateSchedule(id: string, data: Partial<ScheduledReport>) {
    const idx = this.scheduledReports.findIndex(r => r.id === id)
    if (idx >= 0) {
      this.scheduledReports[idx] = { ...this.scheduledReports[idx], ...data, updatedAt: new Date().toISOString() }
      return this.scheduledReports[idx]
    }
    return this.scheduledReports[0]
  }

  deleteSchedule(id: string) {
    this.scheduledReports = this.scheduledReports.filter(r => r.id !== id)
    return { message: 'Agendamento removido' }
  }

  // ===== NOTIFICATIONS =====
  getNotifications() {
    return {
      email_enabled: true,
      slack_enabled: false,
      webhook_url: '',
      events: ['document_uploaded', 'discrepancy_found', 'contest_created', 'payment_received'],
    }
  }

  updateNotifications(data: any) {
    return { ...this.getNotifications(), ...data }
  }
}

// Singleton instance
export const demoStore = new DemoStore()

// ===== DEMO API FUNCTIONS =====
// These simulate the API calls with artificial delays

const DEMO_DELAY = 300 // ms

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const demoApi = {
  // Auth
  async login(_email: string, _password: string) {
    await delay(DEMO_DELAY)
    // In demo mode, accept any credentials but use demo user
    return {
      access_token: 'demo-access-token',
      refresh_token: 'demo-refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
      user: demoStore.getDemoUser(),
    }
  },

  async register(data: any) {
    await delay(DEMO_DELAY)
    return {
      access_token: 'demo-access-token',
      refresh_token: 'demo-refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
      user: demoStore.createUser({ ...data, role: 'CLIENT' }),
    }
  },

  async refresh() {
    await delay(100)
    return {
      access_token: 'demo-new-access-token',
      token_type: 'bearer',
      expires_in: 3600,
    }
  },

  async logout() {
    await delay(100)
    return { message: 'Logout realizado com sucesso' }
  },

  async me() {
    await delay(100)
    return demoStore.getDemoUser()
  },

  // Companies
  async getCompanies(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getCompanies(params.page, params.size)
  },

  async getCompany(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getCompany(id)
  },

  async createCompany(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createCompany(data)
  },

  async updateCompany(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateCompany(id, data)
  },

  async deleteCompany(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteCompany(id)
  },

  // Users
  async getUsers(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getUsers(params.page, params.size)
  },

  async getUser(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getUser(id)
  },

  async createUser(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createUser(data)
  },

  async updateUser(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateUser(id, data)
  },

  async deleteUser(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteUser(id)
  },

  // Carriers
  async getCarriers(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getCarriers(params.page, params.size)
  },

  async getCarrier(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getCarrier(id)
  },

  async createCarrier(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createCarrier(data)
  },

  async updateCarrier(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateCarrier(id, data)
  },

  async deleteCarrier(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteCarrier(id)
  },

  // Clients
  async getClients(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getClients(params.page, params.size)
  },

  async getClient(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getClient(id)
  },

  async createClient(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createClient(data)
  },

  async updateClient(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateClient(id, data)
  },

  async deleteClient(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteClient(id)
  },

  // Contracts
  async getContracts(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getContracts(params.page, params.size)
  },

  async getContract(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getContract(id)
  },

  async createContract(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createContract(data)
  },

  async updateContract(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateContract(id, data)
  },

  async deleteContract(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteContract(id)
  },

  // Documents
  async getDocuments(params: { page?: number; size?: number; status?: DocumentStatus[]; documentType?: DocumentType[]; clientId?: string; carrierId?: string; dateFrom?: string; dateTo?: string; search?: string } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getDocuments(params.page, params.size, params)
  },

  async getDocument(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getDocument(id)
  },

  async uploadDocument(file: File) {
    await delay(500)
    return demoStore.uploadDocument(file)
  },

  async reprocessDocument(id: string) {
    await delay(300)
    return demoStore.reprocessDocument(id)
  },

  // Discrepancies
  async getDiscrepancies(params: { page?: number; size?: number; status?: DiscrepancyStatus[]; severity?: DiscrepancySeverity[]; type?: DiscrepancyType[]; clientId?: string; carrierId?: string; contractId?: string; documentId?: string; dateFrom?: string; dateTo?: string; search?: string } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getDiscrepancies(params.page, params.size, params)
  },

  async getDiscrepancySummary() {
    await delay(DEMO_DELAY)
    return demoStore.getDiscrepancySummary()
  },

  async getDiscrepancy(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getDiscrepancy(id)
  },

  async bulkUpdateStatus(ids: string[], status: DiscrepancyStatus) {
    await delay(DEMO_DELAY)
    return demoStore.bulkUpdateStatus(ids, status)
  },

  async reviewDiscrepancy(id: string, status: DiscrepancyStatus, _reviewNotes?: string) {
    await delay(DEMO_DELAY)
    return demoStore.reviewDiscrepancy(id, status, _reviewNotes)
  },

  async bulkReviewDiscrepancies(ids: string[], status: DiscrepancyStatus, _notes?: string) {
    await delay(DEMO_DELAY)
    return demoStore.bulkReviewDiscrepancies(ids, status, _notes)
  },

  async createContestFromDiscrepancies(data: { discrepancyIds: string[]; title: string; description: string }) {
    await delay(DEMO_DELAY)
    return demoStore.createContestFromDiscrepancies(data)
  },

  // Contests
  async getContests(params: { page?: number; size?: number; status?: ContestStatus[]; carrierId?: string; dateFrom?: string; dateTo?: string; search?: string } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getContests(params.page, params.size, params)
  },

  async getContest(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getContest(id)
  },

  async createContest(data: { discrepancyIds: string[]; carrierId: string; title: string; description: string; requestedAmount: number; evidenceFiles?: File[] }) {
    await delay(DEMO_DELAY)
    return demoStore.createContest(data)
  },

  async sendContest(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.sendContest(id)
  },

  async negotiateContest(id: string, data: { offeredAmount: number; message: string }) {
    await delay(DEMO_DELAY)
    return demoStore.negotiateContest(id, data)
  },

  // Payments
  async createPayment(contestId: string, data: { amount: number; paymentMethod: string; reference: string }) {
    await delay(DEMO_DELAY)
    return demoStore.createPayment(contestId, data)
  },

  // Reports
  async getDashboardReport() {
    await delay(DEMO_DELAY)
    return demoStore.getDashboardReport()
  },

  async getReportsDashboard() {
    await delay(DEMO_DELAY)
    return demoStore.getReportsDashboard()
  },

  async getPDFReport(type: string) {
    await delay(500)
    return demoStore.generatePDF(type)
  },

  async getExcelReport(type: string) {
    await delay(500)
    return demoStore.generateExcel(type)
  },

  async getRecoveryReport(filters?: any) {
    await delay(DEMO_DELAY)
    return demoStore.getRecoveryReport(filters)
  },

  async getCarrierPerformanceReport(filters?: any) {
    await delay(DEMO_DELAY)
    return demoStore.getCarrierPerformanceReport(filters)
  },

  async createSchedule(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.createSchedule(data)
  },

  async getScheduledReports(params: { page?: number; size?: number } = {}) {
    await delay(DEMO_DELAY)
    return demoStore.getScheduledReports(params.page, params.size)
  },

  async getScheduledReport(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.getScheduledReport(id)
  },

  async updateSchedule(id: string, data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateSchedule(id, data)
  },

  async deleteSchedule(id: string) {
    await delay(DEMO_DELAY)
    return demoStore.deleteSchedule(id)
  },

  // Notifications
  async getNotifications() {
    await delay(DEMO_DELAY)
    return demoStore.getNotifications()
  },

  async updateNotifications(data: any) {
    await delay(DEMO_DELAY)
    return demoStore.updateNotifications(data)
  },
}