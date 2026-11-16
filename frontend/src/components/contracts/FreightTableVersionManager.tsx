// Freight Table Version Manager Component
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { useState, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Loader2, Eye, Edit2, Copy, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { Button, Card, CardHeader, CardBody, CardFooter, Badge, Modal, Table, Tooltip } from '../index';
import { useFreightTables } from '../../hooks/useContracts';
import { formatDate } from '../../utils/helpers';

interface FreightTableVersionManagerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  contractId: string;
  currentTableId?: string;
}

interface FreightTableVersion {
  id: string;
  version: number;
  status: 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
  effectiveFrom: string;
  effectiveTo: string | null;
  ratesCount: number;
  createdAt: string;
  updatedAt: string;
}

const STATUS_LABELS: Record<string, string> = {
  DRAFT: 'Rascunho',
  ACTIVE: 'Ativo',
  ARCHIVED: 'Arquivado',
};

const STATUS_BADGE_VARIANTS: Record<string, 'success' | 'warning' | 'secondary'> = {
  ACTIVE: 'success',
  DRAFT: 'warning',
  ARCHIVED: 'secondary',
};

export function FreightTableVersionManager({
  open,
  onOpenChange,
  contractId,
  currentTableId,
}: FreightTableVersionManagerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const { data: freightTables, isLoading, refetch } = useFreightTables(contractId);

  useEffect(() => {
    if (open) {
      refetch();
    }
  }, [open, refetch]);

  const versions: FreightTableVersion[] = useMemo(() => {
    if (!freightTables) return [];
    return freightTables
      .map((ft) => ({
        id: ft.id,
        version: ft.version,
        status: ft.status,
        effectiveFrom: ft.effectiveFrom,
        effectiveTo: ft.effectiveTo,
        ratesCount: ft.rates.length,
        createdAt: ft.createdAt,
        updatedAt: ft.updatedAt,
      }))
      .sort((a, b) => b.version - a.version);
  }, [freightTables]);

  const totalPages = Math.ceil(versions.length / pageSize);
  const paginatedVersions = versions.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const versionColumns = [
    {
      key: 'version',
      header: 'Versão',
      render: (v: FreightTableVersion) => (
        <span className="font-mono font-medium text-secondary-900">v{v.version}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (v: FreightTableVersion) => (
        <Badge variant={STATUS_BADGE_VARIANTS[v.status] || 'secondary'}>
          {STATUS_LABELS[v.status]}
        </Badge>
      ),
    },
    {
      key: 'effectiveFrom',
      header: 'Início Vigência',
      render: (v: FreightTableVersion) => (
        <span className="text-sm text-secondary-900">{formatDate(v.effectiveFrom)}</span>
      ),
    },
    {
      key: 'effectiveTo',
      header: 'Fim Vigência',
      render: (v: FreightTableVersion) => (
        <span className="text-sm text-secondary-500">
          {v.effectiveTo ? formatDate(v.effectiveTo) : 'Indeterminado'}
        </span>
      ),
    },
    {
      key: 'ratesCount',
      header: 'Taxas',
      render: (v: FreightTableVersion) => (
        <span className="text-sm text-secondary-900">{v.ratesCount}</span>
      ),
    },
    {
      key: 'createdAt',
      header: 'Criado em',
      render: (v: FreightTableVersion) => (
        <span className="text-sm text-secondary-500">{formatDate(v.createdAt)}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (v: FreightTableVersion) => (
        <div className="flex items-center justify-center gap-1">
          <Tooltip content="Visualizar">
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <Eye className="h-4 w-4" />
            </Button>
          </Tooltip>
          {v.status === 'DRAFT' && (
            <Tooltip content="Editar">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <Edit2 className="h-4 w-4" />
              </Button>
            </Tooltip>
          )}
          <Tooltip content="Duplicar">
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <Copy className="h-4 w-4" />
            </Button>
          </Tooltip>
        </div>
      ),
    },
  ];

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Gerenciar Versões"
      size="xl"
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-secondary-400" />
        </div>
      ) : versions.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-secondary-400">
          <Clock className="h-12 w-12 mb-4" />
          <p className="text-secondary-500">Nenhuma versão encontrada</p>
          <p className="text-sm text-secondary-400">Crie a primeira tabela de frete para começar</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current version indicator */}
          {currentTableId && (
            <div className="p-3 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary-600" />
                <span className="text-sm text-primary-900">
                  Versão atual: <strong className="font-mono">v{versions.find((v) => v.id === currentTableId)?.version}</strong>
                </span>
              </div>
            </div>
          )}

          {/* Version History Table */}
          <Card>
            <CardHeader className="pb-2">
              <h3 className="text-lg font-semibold text-secondary-900">Histórico de Versões</h3>
            </CardHeader>
            <CardBody className="p-0">
              <Table
                columns={versionColumns}
                data={paginatedVersions}
                keyField="id"
                isLoading={false}
                emptyMessage="Nenhuma versão encontrada"
              />
            </CardBody>
            <CardFooter className="flex items-center justify-between">
              <span className="text-sm text-secondary-500">
                Mostrando {(currentPage - 1) * pageSize + 1} a {Math.min(currentPage * pageSize, versions.length)} de {versions.length}
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage <= 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-secondary-500 px-2">
                  Página {currentPage} de {totalPages}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardFooter>
          </Card>

          {/* Version comparison note */}
          <div className="p-3 bg-secondary-50 border border-secondary-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-secondary-500 mt-0.5" />
              <div className="text-sm text-secondary-700">
                <p className="font-medium">Comparação de Versões</p>
                <p className="mt-1">
                  Selecione duas versões acima para comparar as diferenças nas taxas de frete.
                  Esta funcionalidade estará disponível em uma próxima atualização.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}