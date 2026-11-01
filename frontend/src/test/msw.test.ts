import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './setupTests'

describe('MSW Setup', () => {
  it('intercepts API calls with default handlers', async () => {
    // Test login endpoint
    const loginResponse = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'admin@averta.com', password: 'admin123' }),
    })
    const loginData = await loginResponse.json()
    expect(loginResponse.status).toBe(200)
    expect(loginData.access_token).toBe('mock-access-token-admin')
    expect(loginData.user.role).toBe('ADMIN')
  })

  it('returns 401 for invalid credentials', async () => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'wrong@test.com', password: 'wrong' }),
    })
    const data = await response.json()
    expect(response.status).toBe(401)
    expect(data.detail).toBe('Credenciais inválidas')
  })

  it('intercepts documents list', async () => {
    const response = await fetch('/api/v1/documents')
    const data = await response.json()
    expect(response.status).toBe(200)
    expect(data.items).toBeInstanceOf(Array)
    expect(data.items.length).toBeGreaterThan(0)
    expect(data.total).toBeGreaterThan(0)
  })

  it('intercepts discrepancies list', async () => {
    const response = await fetch('/api/v1/discrepancies')
    const data = await response.json()
    expect(response.status).toBe(200)
    expect(data.items).toBeInstanceOf(Array)
  })

  it('intercepts contests list', async () => {
    const response = await fetch('/api/v1/contests')
    const data = await response.json()
    expect(response.status).toBe(200)
    expect(data.items).toBeInstanceOf(Array)
  })

  it('intercepts reports dashboard', async () => {
    const response = await fetch('/api/v1/reports/dashboard')
    const data = await response.json()
    expect(response.status).toBe(200)
    expect(data.total_documents).toBeDefined()
    expect(data.total_recovered).toBeDefined()
  })

  it('allows overriding handlers per test', async () => {
    // Override handler for this test only
    server.use(
      http.get('/api/v1/documents', () => {
        return HttpResponse.json({
          items: [{ id: 'custom-1', original_filename: 'custom.xml' }],
          total: 1,
          page: 1,
          size: 20,
          pages: 1,
        })
      })
    )

    const response = await fetch('/api/v1/documents')
    const data = await response.json()
    expect(data.items[0].id).toBe('custom-1')
    expect(data.total).toBe(1)
  })

  it('allows adding new handlers per test', async () => {
    server.use(
      http.get('/api/v1/test-endpoint', () => {
        return HttpResponse.json({ message: 'custom response' })
      })
    )

    const response = await fetch('/api/v1/test-endpoint')
    const data = await response.json()
    expect(data.message).toBe('custom response')
  })
})