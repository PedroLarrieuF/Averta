import { faker } from '@faker-js/faker'

// ===== TYPE DEFINITIONS =====

export interface User {
  id: string
  email: string
  full_name: string
  role: 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT' | 'CARRIER'
  company_id: string
  company_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Company {
  id: string
  name: string
  cnpj: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  zip_code: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Carrier {
  id: string
  company_id: string
  name: string
  cnpj: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  zip_code: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Contract {
  id: string
  company_id: string
  carrier_id: string
  name: string
  description: string
  success_fee_pct: number
  min_recovery_value: number
  effective_date: string
  expiry_date: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Document {
  id: string
  company_id: string
  carrier_id: string
  contract_id: string
  original_filename: string
  file_size: number
  mime_type: string
  storage_path: string
  status: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'ERROR' | 'REPROCESSING'
  document_type: 'NFE' | 'CTE' | 'MDFE'
  document_number: string
  document_series: string
  emission_date: string
  total_value: number
  company_name: string
  carrier_name: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface Discrepancy {
  id: string
  document_id: string
  rule_id: string
  rule_name: string
  rule_description: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  status: 'PENDING' | 'UNDER_REVIEW' | 'ACCEPTED' | 'REJECTED' | 'CONTESTED'
  expected_value: number
  actual_value: number
  difference_value: number
  difference_pct: number
  description: string
  evidence: Record<string, unknown>
  reviewed_by: string | null
  reviewed_at: string | null
  review_notes: string | null
  created_at: string
  updated_at: string
}

export interface Contest {
  id: string
  discrepancy_id: string
  company_id: string
  carrier_id: string
  title: string
  description: string
  status: 'DRAFT' | 'SENT' | 'NEGOTIATING' | 'SETTLED' | 'REJECTED' | 'EXPIRED'
  requested_amount: number
  offered_amount: number | null
  settled_amount: number | null
  sent_at: string | null
  responded_at: string | null
  settled_at: string | null
  expires_at: string
  created_at: string
  updated_at: string
}

export interface Payment {
  id: string
  contest_id: string
  amount: number
  payment_date: string
  payment_method: 'PIX' | 'TED' | 'BOLETO' | 'DEPOSIT'
  transaction_id: string
  status: 'PENDING' | 'CONFIRMED' | 'FAILED' | 'REFUNDED'
  notes: string | null
  created_at: string
  updated_at: string
}

// ===== FACTORY HELPERS =====

const ROLES = ['ADMIN', 'MANAGER', 'AUDITOR', 'CLIENT', 'CARRIER'] as const
const DOCUMENT_STATUSES = ['UPLOADED', 'PROCESSING', 'PROCESSED', 'ERROR', 'REPROCESSING'] as const
const DOCUMENT_TYPES = ['NFE', 'CTE', 'MDFE'] as const
const DISCREPANCY_SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const
const DISCREPANCY_STATUSES = ['PENDING', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'CONTESTED'] as const
const CONTEST_STATUSES = ['DRAFT', 'SENT', 'NEGOTIATING', 'SETTLED', 'REJECTED', 'EXPIRED'] as const
const PAYMENT_METHODS = ['PIX', 'TED', 'BOLETO', 'DEPOSIT'] as const
const PAYMENT_STATUSES = ['PENDING', 'CONFIRMED', 'FAILED', 'REFUNDED'] as const
const STATES = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE'] as const

function randomEnum<T extends readonly string[]>(arr: T): T[number] {
  return arr[Math.floor(Math.random() * arr.length)]
}

function randomDate(daysBack = 365): string {
  const date = faker.date.recent({ days: daysBack })
  return date.toISOString()
}

function randomPastDate(): string {
  return faker.date.past({ years: 2 }).toISOString()
}

function randomFutureDate(): string {
  return faker.date.future({ years: 1 }).toISOString()
}

function generateId(): string {
  return faker.string.uuid()
}

function generateCNPJ(): string {
  const numbers = Array.from({ length: 14 }, () => faker.number.int({ min: 0, max: 9 }))
  return `${numbers.slice(0, 2).join('')}.${numbers.slice(2, 5).join('')}.${numbers.slice(5, 8).join('')}/${numbers.slice(8, 12).join('')}-${numbers.slice(12).join('')}`
}

// ===== FACTORY FUNCTIONS =====

export const factory = {
  user(overrides: Partial<User> = {}): User {
    const role = overrides.role || randomEnum(ROLES)
    const companyId = overrides.company_id || generateId()
    return {
      id: generateId(),
      email: overrides.email || faker.internet.email(),
      full_name: overrides.full_name || faker.person.fullName(),
      role,
      company_id: companyId,
      company_name: overrides.company_name || faker.company.name(),
      is_active: overrides.is_active ?? true,
      created_at: overrides.created_at || randomPastDate(),
      updated_at: overrides.updated_at || randomPastDate(),
    }
  },

  company(overrides: Partial<Company> = {}): Company {
    return {
      id: generateId(),
      name: overrides.name || faker.company.name(),
      cnpj: overrides.cnpj || generateCNPJ(),
      email: overrides.email || faker.internet.email(),
      phone: overrides.phone || faker.phone.number(),
      address: overrides.address || faker.location.streetAddress(),
      city: overrides.city || faker.location.city(),
      state: overrides.state || randomEnum(STATES),
      zip_code: overrides.zip_code || faker.location.zipCode('#####-###'),
      is_active: overrides.is_active ?? true,
      created_at: overrides.created_at || randomPastDate(),
      updated_at: overrides.updated_at || randomPastDate(),
    }
  },

  carrier(overrides: Partial<Carrier> = {}): Carrier {
    const companyId = overrides.company_id || generateId()
    return {
      id: generateId(),
      company_id: companyId,
      name: overrides.name || faker.company.name() + ' Transportes',
      cnpj: overrides.cnpj || generateCNPJ(),
      email: overrides.email || faker.internet.email(),
      phone: overrides.phone || faker.phone.number(),
      address: overrides.address || faker.location.streetAddress(),
      city: overrides.city || faker.location.city(),
      state: overrides.state || randomEnum(STATES),
      zip_code: overrides.zip_code || faker.location.zipCode('#####-###'),
      is_active: overrides.is_active ?? true,
      created_at: overrides.created_at || randomPastDate(),
      updated_at: overrides.updated_at || randomPastDate(),
    }
  },

  contract(overrides: Partial<Contract> = {}): Contract {
    const companyId = overrides.company_id || generateId()
    const carrierId = overrides.carrier_id || generateId()
    return {
      id: generateId(),
      company_id: companyId,
      carrier_id: carrierId,
      name: overrides.name || `Contrato ${faker.company.name()} - ${faker.company.name()}`,
      description: overrides.description || faker.lorem.paragraph(),
      success_fee_pct: overrides.success_fee_pct ?? faker.number.float({ min: 5, max: 20, fractionDigits: 2 }),
      min_recovery_value: overrides.min_recovery_value ?? faker.number.float({ min: 100, max: 10000, fractionDigits: 2 }),
      effective_date: overrides.effective_date || randomDate(30),
      expiry_date: overrides.expiry_date || randomFutureDate(),
      is_active: overrides.is_active ?? true,
      created_at: overrides.created_at || randomPastDate(),
      updated_at: overrides.updated_at || randomPastDate(),
    }
  },

  document(overrides: Partial<Document> = {}): Document {
    const companyId = overrides.company_id || generateId()
    const carrierId = overrides.carrier_id || generateId()
    const contractId = overrides.contract_id || generateId()
    const status = overrides.status || randomEnum(DOCUMENT_STATUSES)
    const docType = overrides.document_type || randomEnum(DOCUMENT_TYPES)
    const emissionDate = overrides.emission_date || randomDate(90)
    const totalValue = overrides.total_value ?? faker.number.float({ min: 500, max: 50000, fractionDigits: 2 })

    return {
      id: generateId(),
      company_id: companyId,
      carrier_id: carrierId,
      contract_id: contractId,
      original_filename: overrides.original_filename || `${docType}_${faker.string.alphanumeric(10)}.xml`,
      file_size: overrides.file_size ?? faker.number.int({ min: 1000, max: 500000 }),
      mime_type: overrides.mime_type || 'application/xml',
      storage_path: overrides.storage_path || `documents/${companyId}/${faker.string.uuid()}.xml`,
      status,
      document_type: docType,
      document_number: overrides.document_number || faker.string.numeric(9),
      document_series: overrides.document_series || faker.string.numeric(3),
      emission_date: emissionDate,
      total_value: totalValue,
      company_name: overrides.company_name || faker.company.name(),
      carrier_name: overrides.carrier_name || faker.company.name() + ' Transportes',
      error_message: status === 'ERROR' ? (overrides.error_message || 'Erro ao processar XML: namespace inválido') : null,
      created_at: overrides.created_at || randomDate(60),
      updated_at: overrides.updated_at || randomDate(10),
    }
  },

  discrepancy(overrides: Partial<Discrepancy> = {}): Discrepancy {
    const documentId = overrides.document_id || generateId()
    const severity = overrides.severity || randomEnum(DISCREPANCY_SEVERITIES)
    const status = overrides.status || randomEnum(DISCREPANCY_STATUSES)
    const expectedValue = overrides.expected_value ?? faker.number.float({ min: 100, max: 10000, fractionDigits: 2 })
    const actualValue = overrides.actual_value ?? faker.number.float({ min: 100, max: 10000, fractionDigits: 2 })
    const differenceValue = Math.abs(expectedValue - actualValue)
    const differencePct = expectedValue > 0 ? (differenceValue / expectedValue) * 100 : 0

    const ruleNames = [
      'Valor do Frete divergente',
      'ICMS calculado incorretamente',
      'Peso da mercadoria divergente',
      'Volume da carga não confere',
      'CFOP inválido para operação',
      'Base de cálculo ICMS errada',
      'Alíquota interestadual incorreta',
      'Frete não informado na nota',
      'Dados do destinatário incompletos',
      'NCM não confere com produto',
    ]

    return {
      id: generateId(),
      document_id: documentId,
      rule_id: overrides.rule_id || `RULE-${faker.number.int({ min: 1, max: 17 }).toString().padStart(3, '0')}`,
      rule_name: overrides.rule_name || randomEnum(ruleNames),
      rule_description: overrides.rule_description || faker.lorem.sentence(),
      severity,
      status,
      expected_value: expectedValue,
      actual_value: actualValue,
      difference_value: differenceValue,
      difference_pct: Number(differencePct.toFixed(2)),
      description: overrides.description || faker.lorem.paragraph(),
      evidence: overrides.evidence || {
        xml_path: '/invoice/total/ICMS',
        expected: expectedValue,
        found: actualValue,
      },
      reviewed_by: status !== 'PENDING' ? (overrides.reviewed_by || generateId()) : null,
      reviewed_at: status !== 'PENDING' ? (overrides.reviewed_at || randomDate(30)) : null,
      review_notes: status !== 'PENDING' ? (overrides.review_notes || faker.lorem.sentence()) : null,
      created_at: overrides.created_at || randomDate(60),
      updated_at: overrides.updated_at || randomDate(10),
    }
  },

  contest(overrides: Partial<Contest> = {}): Contest {
    const discrepancyId = overrides.discrepancy_id || generateId()
    const companyId = overrides.company_id || generateId()
    const carrierId = overrides.carrier_id || generateId()
    const status = overrides.status || randomEnum(CONTEST_STATUSES)
    const requestedAmount = overrides.requested_amount ?? faker.number.float({ min: 50, max: 5000, fractionDigits: 2 })

    return {
      id: generateId(),
      discrepancy_id: discrepancyId,
      company_id: companyId,
      carrier_id: carrierId,
      title: overrides.title || `Contestação - ${faker.lorem.words(4)}`,
      description: overrides.description || faker.lorem.paragraphs(2),
      status,
      requested_amount: requestedAmount,
      offered_amount: status === 'NEGOTIATING' || status === 'SETTLED' ? (overrides.offered_amount ?? faker.number.float({ min: requestedAmount * 0.5, max: requestedAmount, fractionDigits: 2 })) : null,
      settled_amount: status === 'SETTLED' ? (overrides.settled_amount ?? faker.number.float({ min: requestedAmount * 0.5, max: requestedAmount, fractionDigits: 2 })) : null,
      sent_at: status !== 'DRAFT' ? (overrides.sent_at || randomDate(30)) : null,
      responded_at: status === 'NEGOTIATING' || status === 'SETTLED' || status === 'REJECTED' ? (overrides.responded_at || randomDate(15)) : null,
      settled_at: status === 'SETTLED' ? (overrides.settled_at || randomDate(5)) : null,
      expires_at: overrides.expires_at || randomFutureDate(),
      created_at: overrides.created_at || randomDate(60),
      updated_at: overrides.updated_at || randomDate(10),
    }
  },

  payment(overrides: Partial<Payment> = {}): Payment {
    const contestId = overrides.contest_id || generateId()
    const amount = overrides.amount ?? faker.number.float({ min: 100, max: 10000, fractionDigits: 2 })
    const status = overrides.status || randomEnum(PAYMENT_STATUSES)

    return {
      id: generateId(),
      contest_id: contestId,
      amount,
      payment_date: overrides.payment_date || randomDate(30),
      payment_method: overrides.payment_method || randomEnum(PAYMENT_METHODS),
      transaction_id: overrides.transaction_id || faker.string.alphanumeric(20),
      status,
      notes: overrides.notes || (status === 'FAILED' ? 'Pagamento rejeitado pelo banco' : faker.lorem.sentence()),
      created_at: overrides.created_at || randomDate(30),
      updated_at: overrides.updated_at || randomDate(5),
    }
  },
}

// ===== FACTORY HELPERS =====

export function manyOf<T>(factoryFn: (overrides?: Partial<T>) => T, count: number, overrides?: Partial<T>): T[] {
  return Array.from({ length: count }, (_, i) => factoryFn({ ...overrides, id: `${overrides?.id || 'auto'}-${i}` } as Partial<T>))
}

export function oneOf<T>(factoryFn: (overrides?: Partial<T>) => T, overrides?: Partial<T>): T {
  return factoryFn(overrides)
}

// Seed for reproducible tests
export function seedFactories(seed: number): void {
  faker.seed(seed)
}