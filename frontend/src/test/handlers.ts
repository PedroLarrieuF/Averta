import { http, HttpResponse, delay } from 'msw'
import { factory, manyOf } from './factories'

const API_BASE = '/api/v1'

// ===== AUTH HANDLERS =====
const authHandlers = [
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    await delay(100)
    const body = await request.json()
    const { email, password } = body

    if (email === 'admin@averta.com' && password === 'admin123') {
      return HttpResponse.json({
        access_token: 'mock-access-token-admin',
        refresh_token: 'mock-refresh-token-admin',
        token_type: 'bearer',
        expires_in: 900,
        user: factory.user({ email, role: 'ADMIN' }),
      })
    }

    if (email === 'manager@averta.com' && password === 'manager123') {
      return HttpResponse.json({
        access_token: 'mock-access-token-manager',
        refresh_token: 'mock-refresh-token-manager',
        token_type: 'bearer',
        expires_in: 900,
        user: factory.user({ email, role: 'MANAGER' }),
      })
    }

    return HttpResponse.json(
      { detail: 'Credenciais inválidas' },
      { status: 401 }
    )
  }),

  http.post(`${API_BASE}/auth/register`, async ({ request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json({
      access_token: 'mock-access-token-new',
      refresh_token: 'mock-refresh-token-new',
      token_type: 'bearer',
      expires_in: 900,
      user: factory.user({ email: body.email, role: 'CLIENT' }),
    })
  }),

  http.post(`${API_BASE}/auth/refresh`, async ({ cookies }) => {
    await delay(50)
    const refreshToken = cookies.refresh_token
    if (!refreshToken) {
      return HttpResponse.json({ detail: 'Refresh token não fornecido' }, { status: 401 })
    }
    return HttpResponse.json({
      access_token: 'mock-new-access-token',
      token_type: 'bearer',
      expires_in: 900,
    })
  }),

  http.post(`${API_BASE}/auth/logout`, async () => {
    await delay(50)
    return HttpResponse.json({ message: 'Logout realizado com sucesso' })
  }),

  http.get(`${API_BASE}/auth/me`, async ({ cookies }) => {
    await delay(50)
    const accessToken = cookies.access_token
    if (!accessToken) {
      return HttpResponse.json({ detail: 'Não autenticado' }, { status: 401 })
    }
    return HttpResponse.json(factory.user({ role: 'ADMIN' }))
  }),
]

// ===== DOCUMENTS HANDLERS =====
const documentsHandlers = [
  http.get(`${API_BASE}/documents`, async ({ request }) => {
    await delay(150)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const status = url.searchParams.get('status')
    const search = url.searchParams.get('search')

    let documents = manyOf(factory.document, 25)

    if (status) {
      documents = documents.filter((d) => d.status === status)
    }
    if (search) {
      documents = documents.filter(
        (d) =>
          d.original_filename.toLowerCase().includes(search.toLowerCase()) ||
          d.company_name.toLowerCase().includes(search.toLowerCase())
      )
    }

    const total = documents.length
    const start = (page - 1) * size
    const paginated = documents.slice(start, start + size)

    return HttpResponse.json({
      items: paginated,
      total,
      page,
      size,
      pages: Math.ceil(total / size),
    })
  }),

  http.post(`${API_BASE}/documents/upload`, async ({ request }) => {
    await delay(300)
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return HttpResponse.json({ detail: 'Arquivo não fornecido' }, { status: 400 })
    }

    if (!file.name.endsWith('.xml')) {
      return HttpResponse.json({ detail: 'Apenas arquivos XML são permitidos' }, { status: 400 })
    }

    return HttpResponse.json(factory.document({ original_filename: file.name, status: 'UPLOADED' }), { status: 201 })
  }),

  http.get(`${API_BASE}/documents/:id`, async ({ params }) => {
    await delay(100)
    const { id } = params
    return HttpResponse.json(factory.document({ id: id as string }))
  }),

  http.post(`${API_BASE}/documents/:id/reprocess`, async ({ params }) => {
    await delay(200)
    const { id } = params
    return HttpResponse.json(factory.document({ id: id as string, status: 'PROCESSING' }))
  }),
]

// ===== DISCREPANCIES HANDLERS =====
const discrepanciesHandlers = [
  http.get(`${API_BASE}/discrepancies`, async ({ request }) => {
    await delay(150)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const status = url.searchParams.get('status')
    const severity = url.searchParams.get('severity')
    const document_id = url.searchParams.get('document_id')

    let discrepancies = manyOf(factory.discrepancy, 50)

    if (status) {
      discrepancies = discrepancies.filter((d) => d.status === status)
    }
    if (severity) {
      discrepancies = discrepancies.filter((d) => d.severity === severity)
    }
    if (document_id) {
      discrepancies = discrepancies.filter((d) => d.document_id === document_id)
    }

    const total = discrepancies.length
    const start = (page - 1) * size
    const paginated = discrepancies.slice(start, start + size)

    return HttpResponse.json({
      items: paginated,
      total,
      page,
      size,
      pages: Math.ceil(total / size),
    })
  }),

  http.get(`${API_BASE}/discrepancies/summary`, async () => {
    await delay(100)
    return HttpResponse.json({
      total: 150,
      by_status: {
        PENDING: 45,
        UNDER_REVIEW: 20,
        ACCEPTED: 50,
        REJECTED: 25,
        CONTESTED: 10,
      },
      by_severity: {
        LOW: 60,
        MEDIUM: 55,
        HIGH: 25,
        CRITICAL: 10,
      },
      total_recovered: 125000.00,
      total_contested: 45000.00,
    })
  }),

  http.get(`${API_BASE}/discrepancies/:id`, async ({ params }) => {
    await delay(100)
    const { id } = params
    return HttpResponse.json(factory.discrepancy({ id: id as string }))
  }),

  http.patch(`${API_BASE}/discrepancies/bulk-status`, async ({ request }) => {
    await delay(150)
    const body = await request.json()
    const { ids, status } = body
    return HttpResponse.json({
      updated: ids.length,
      message: `${ids.length} discrepâncias atualizadas para ${status}`,
    })
  }),

  http.post(`${API_BASE}/discrepancies/:id/review`, async ({ params, request }) => {
    await delay(150)
    const { id } = params
    const body = await request.json()
    return HttpResponse.json(factory.discrepancy({ id: id as string, status: body.status || 'UNDER_REVIEW' }))
  }),
]

// ===== CONTESTS HANDLERS =====
const contestsHandlers = [
  http.get(`${API_BASE}/contests`, async ({ request }) => {
    await delay(150)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const status = url.searchParams.get('status')

    let contests = manyOf(factory.contest, 30)

    if (status) {
      contests = contests.filter((c) => c.status === status)
    }

    const total = contests.length
    const start = (page - 1) * size
    const paginated = contests.slice(start, start + size)

    return HttpResponse.json({
      items: paginated,
      total,
      page,
      size,
      pages: Math.ceil(total / size),
    })
  }),

  http.post(`${API_BASE}/contests`, async ({ request }) => {
    await delay(200)
    const body = await request.json()
    return HttpResponse.json(factory.contest({ ...body, status: 'DRAFT' }), { status: 201 })
  }),

  http.get(`${API_BASE}/contests/:id`, async ({ params }) => {
    await delay(100)
    const { id } = params
    return HttpResponse.json(factory.contest({ id: id as string }))
  }),

  http.post(`${API_BASE}/contests/:id/send`, async ({ params }) => {
    await delay(200)
    const { id } = params
    return HttpResponse.json(factory.contest({ id: id as string, status: 'SENT' }))
  }),

  http.patch(`${API_BASE}/contests/:id/negotiate`, async ({ params, request }) => {
    await delay(200)
    const { id } = params
    const body = await request.json()
    return HttpResponse.json(factory.contest({ id: id as string, ...body, status: 'NEGOTIATING' }))
  }),

  http.post(`${API_BASE}/contests/:id/payments`, async ({ params, request }) => {
    await delay(200)
    const { id } = params
    const body = await request.json()
    return HttpResponse.json(factory.payment({ contest_id: id as string, ...body }), { status: 201 })
  }),
]

// ===== REPORTS HANDLERS =====
const reportsHandlers = [
  http.get(`${API_BASE}/reports/dashboard`, async () => {
    await delay(150)
    return HttpResponse.json({
      total_documents: 1250,
      total_discrepancies: 340,
      total_contests: 85,
      total_recovered: 1250000.00,
      total_pending: 340000.00,
      success_rate: 0.78,
      avg_processing_days: 12,
      monthly_trend: [
        { month: '2024-01', recovered: 120000, discrepancies: 45 },
        { month: '2024-02', recovered: 135000, discrepancies: 52 },
        { month: '2024-03', recovered: 110000, discrepancies: 38 },
        { month: '2024-04', recovered: 145000, discrepancies: 61 },
        { month: '2024-05', recovered: 160000, discrepancies: 68 },
        { month: '2024-06', recovered: 180000, discrepancies: 76 },
      ],
      top_carriers: [
        { carrier: 'Transportes ABC', recovered: 250000, count: 45 },
        { carrier: 'Logística XYZ', recovered: 180000, count: 32 },
        { carrier: 'Cargas Rápidas', recovered: 150000, count: 28 },
      ],
    })
  }),

  http.get(`${API_BASE}/reports/pdf`, async ({ request }) => {
    await delay(500)
    const url = new URL(request.url)
    const type = url.searchParams.get('type') || 'dashboard'
    return new HttpResponse(
      new Blob(['%PDF-1.4 mock pdf content'], { type: 'application/pdf' }),
      {
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': `attachment; filename="${type}-report.pdf"`,
        },
      }
    )
  }),

  http.get(`${API_BASE}/reports/excel`, async ({ request }) => {
    await delay(500)
    const url = new URL(request.url)
    const type = url.searchParams.get('type') || 'discrepancies'
    return new HttpResponse(
      new Blob(['mock excel content'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }),
      {
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': `attachment; filename="${type}-report.xlsx"`,
        },
      }
    )
  }),

  http.post(`${API_BASE}/reports/schedule`, async ({ request }) => {
    await delay(200)
    const body = await request.json()
    return HttpResponse.json({
      id: crypto.randomUUID(),
      ...body,
      status: 'SCHEDULED',
      next_run: new Date(Date.now() + 86400000).toISOString(),
    }, { status: 201 })
  }),
]

// ===== SETTINGS HANDLERS =====
const settingsHandlers = [
  // Companies
  http.get(`${API_BASE}/settings/companies`, async ({ request }) => {
    await delay(100)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const companies = manyOf(factory.company, 10)
    return HttpResponse.json({ items: companies, total: companies.length, page, size, pages: 1 })
  }),
  http.post(`${API_BASE}/settings/companies`, async ({ request }) => {
    await delay(150)
    const body = await request.json()
    return HttpResponse.json(factory.company(body), { status: 201 })
  }),
  http.get(`${API_BASE}/settings/companies/:id`, async ({ params }) => {
    await delay(80)
    return HttpResponse.json(factory.company({ id: params.id as string }))
  }),
  http.patch(`${API_BASE}/settings/companies/:id`, async ({ params, request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json(factory.company({ id: params.id as string, ...body }))
  }),
  http.delete(`${API_BASE}/settings/companies/:id`, async () => {
    await delay(80)
    return HttpResponse.json({ message: 'Empresa removida' })
  }),

  // Users
  http.get(`${API_BASE}/settings/users`, async ({ request }) => {
    await delay(100)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const users = manyOf(factory.user, 20)
    return HttpResponse.json({ items: users, total: users.length, page, size, pages: 1 })
  }),
  http.post(`${API_BASE}/settings/users`, async ({ request }) => {
    await delay(150)
    const body = await request.json()
    return HttpResponse.json(factory.user(body), { status: 201 })
  }),
  http.get(`${API_BASE}/settings/users/:id`, async ({ params }) => {
    await delay(80)
    return HttpResponse.json(factory.user({ id: params.id as string }))
  }),
  http.patch(`${API_BASE}/settings/users/:id`, async ({ params, request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json(factory.user({ id: params.id as string, ...body }))
  }),
  http.delete(`${API_BASE}/settings/users/:id`, async () => {
    await delay(80)
    return HttpResponse.json({ message: 'Usuário removido' })
  }),

  // Carriers
  http.get(`${API_BASE}/settings/carriers`, async ({ request }) => {
    await delay(100)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const carriers = manyOf(factory.carrier, 15)
    return HttpResponse.json({ items: carriers, total: carriers.length, page, size, pages: 1 })
  }),
  http.post(`${API_BASE}/settings/carriers`, async ({ request }) => {
    await delay(150)
    const body = await request.json()
    return HttpResponse.json(factory.carrier(body), { status: 201 })
  }),
  http.get(`${API_BASE}/settings/carriers/:id`, async ({ params }) => {
    await delay(80)
    return HttpResponse.json(factory.carrier({ id: params.id as string }))
  }),
  http.patch(`${API_BASE}/settings/carriers/:id`, async ({ params, request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json(factory.carrier({ id: params.id as string, ...body }))
  }),
  http.delete(`${API_BASE}/settings/carriers/:id`, async () => {
    await delay(80)
    return HttpResponse.json({ message: 'Transportadora removida' })
  }),

  // Contracts
  http.get(`${API_BASE}/settings/contracts`, async ({ request }) => {
    await delay(100)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const size = parseInt(url.searchParams.get('size') || '20')
    const contracts = manyOf(factory.contract, 12)
    return HttpResponse.json({ items: contracts, total: contracts.length, page, size, pages: 1 })
  }),
  http.post(`${API_BASE}/settings/contracts`, async ({ request }) => {
    await delay(150)
    const body = await request.json()
    return HttpResponse.json(factory.contract(body), { status: 201 })
  }),
  http.get(`${API_BASE}/settings/contracts/:id`, async ({ params }) => {
    await delay(80)
    return HttpResponse.json(factory.contract({ id: params.id as string }))
  }),
  http.patch(`${API_BASE}/settings/contracts/:id`, async ({ params, request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json(factory.contract({ id: params.id as string, ...body }))
  }),
  http.delete(`${API_BASE}/settings/contracts/:id`, async () => {
    await delay(80)
    return HttpResponse.json({ message: 'Contrato removido' })
  }),

  // Notifications
  http.get(`${API_BASE}/settings/notifications`, async () => {
    await delay(100)
    return HttpResponse.json({
      email_enabled: true,
      slack_enabled: false,
      webhook_url: '',
      events: ['document_uploaded', 'discrepancy_found', 'contest_created', 'payment_received'],
    })
  }),
  http.patch(`${API_BASE}/settings/notifications`, async ({ request }) => {
    await delay(100)
    const body = await request.json()
    return HttpResponse.json(body)
  }),
]

// Export all handlers
export const handlers = [
  ...authHandlers,
  ...documentsHandlers,
  ...discrepanciesHandlers,
  ...contestsHandlers,
  ...reportsHandlers,
  ...settingsHandlers,
]