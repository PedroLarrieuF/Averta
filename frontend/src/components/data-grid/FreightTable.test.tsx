import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FreightTable } from './FreightTable'
import type { FreightTableColumn, FreightTableRow } from './types'

const mockColumns: FreightTableColumn[] = [
  { id: 'originCity', header: 'Cidade Origem', type: 'text', required: true },
  { id: 'originState', header: 'UF Origem', type: 'text', required: true, width: 80 },
  { id: 'destinationCity', header: 'Cidade Destino', type: 'text', required: true },
  { id: 'destinationState', header: 'UF Destino', type: 'text', required: true, width: 80 },
  { id: 'freightType', header: 'Tipo Frete', type: 'select', required: true, options: [
    { value: 'NORMAL', label: 'Normal' },
    { value: 'EXPRESS', label: 'Expresso' },
    { value: 'FRACIONADO', label: 'Fracionado' },
  ]},
  { id: 'weightMin', header: 'Peso Mín (kg)', type: 'number', required: true, width: 120 },
  { id: 'weightMax', header: 'Peso Máx (kg)', type: 'number', required: true, width: 120 },
  { id: 'value', header: 'Valor', type: 'currency', required: true, width: 140 },
  { id: 'valueType', header: 'Tipo Valor', type: 'select', required: true, options: [
    { value: 'FIXED', label: 'Fixo' },
    { value: 'PER_KG', label: 'Por kg' },
  ]},
]

const mockRows: FreightTableRow[] = [
  { id: '1', data: { originCity: 'São Paulo', originState: 'SP', destinationCity: 'Rio de Janeiro', destinationState: 'RJ', freightType: 'NORMAL', weightMin: 0, weightMax: 1000, value: 500, valueType: 'FIXED' }, isNew: false, isDirty: false, errors: {} },
  { id: '2', data: { originCity: 'Belo Horizonte', originState: 'MG', destinationCity: 'São Paulo', destinationState: 'SP', freightType: 'EXPRESS', weightMin: 0, weightMax: 500, value: 800, valueType: 'FIXED' }, isNew: false, isDirty: false, errors: {} },
]

describe('FreightTable', () => {
  it('renders table with headers', () => {
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} />)

    expect(screen.getByText('Cidade Origem')).toBeInTheDocument()
    expect(screen.getByText('UF Origem')).toBeInTheDocument()
    expect(screen.getByText('Cidade Destino')).toBeInTheDocument()
    expect(screen.getByText('Tipo Frete')).toBeInTheDocument()
    expect(screen.getByText('Valor')).toBeInTheDocument()
  })

  it('renders data rows', () => {
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} />)

    expect(screen.getByText('São Paulo')).toBeInTheDocument()
    expect(screen.getByText('Rio de Janeiro')).toBeInTheDocument()
    expect(screen.getByText('Belo Horizonte')).toBeInTheDocument()
  })

  it('shows row numbers', () => {
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} />)

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('calls onSave when adding a row', () => {
    const onSave = vi.fn()
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={onSave} />)

    fireEvent.click(screen.getByText('Adicionar Linha'))

    // Click save button
    fireEvent.click(screen.getByText('Salvar'))

    expect(onSave).toHaveBeenCalled()
    const savedRows = onSave.mock.calls[0][0]
    expect(savedRows.length).toBe(3)
    expect(savedRows[2]).toHaveProperty('id')
  })

  it('formats currency values', () => {
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} />)

    expect(screen.getByText('R$ 500,00')).toBeInTheDocument()
    expect(screen.getByText('R$ 800,00')).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    render(<FreightTable columns={mockColumns} initialRows={[]} onSave={vi.fn()} />)

    expect(screen.getByText('Nenhum dado')).toBeInTheDocument()
  })

  it('shows delete button when onDeleteRow provided', () => {
    const onDeleteRow = vi.fn()
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} onDeleteRow={onDeleteRow} />)

    const deleteButtons = screen.getAllByTitle('Excluir')
    expect(deleteButtons).toHaveLength(2)
  })

  it('shows duplicate button when onDuplicateRow provided', () => {
    const onDuplicateRow = vi.fn()
    render(<FreightTable columns={mockColumns} initialRows={mockRows} onSave={vi.fn()} onDuplicateRow={onDuplicateRow} />)

    const duplicateButtons = screen.getAllByTitle('Duplicar')
    expect(duplicateButtons).toHaveLength(2)
  })

  it('respects maxRows prop', () => {
    const manyRows = Array.from({ length: 100 }, (_, i) => ({
      id: String(i + 1),
      data: { originCity: 'Cidade', originState: 'SP', destinationCity: 'Destino', destinationState: 'RJ', freightType: 'NORMAL', weightMin: 0, weightMax: 1000, value: 500, valueType: 'FIXED' },
      isNew: false,
      isDirty: false,
      errors: {},
    }))

    render(<FreightTable columns={mockColumns} initialRows={manyRows} onSave={vi.fn()} maxRows={100} />)

    const addButton = screen.getByText('Adicionar')
    expect(addButton).toBeDisabled()
  })
})