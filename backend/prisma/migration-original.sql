-- Add Rules table and rule_version to Discrepancy
-- Migration: 20261101_add_rules_table

-- Create Rule table
CREATE TABLE "Rule" (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    code          TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    type          "DiscrepancyType" NOT NULL,
    severity      TEXT NOT NULL,
    "configJson"  JSONB NOT NULL DEFAULT '{}',
    version       INTEGER NOT NULL DEFAULT 1,
    "isActive"    BOOLEAN NOT NULL DEFAULT true,
    description   TEXT,
    "createdAt"   TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt"   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add rule_version to Discrepancy
ALTER TABLE "Discrepancy" ADD COLUMN "ruleVersion" INTEGER NOT NULL DEFAULT 1;

-- Indexes for Rule
CREATE INDEX "Rule_code_idx" ON "Rule" (code);
CREATE INDEX "Rule_type_idx" ON "Rule" (type);
CREATE INDEX "Rule_isActive_idx" ON "Rule" ("isActive");

-- Insert current 17 rules
INSERT INTO "Rule" (code, name, type, severity, "configJson", version, "isActive", description) VALUES
-- ICMS Rules
('ICMS_DIFAL', 'ICMS Diferencial de Alíquota (DIFAL)', 'ICMS_DIFFERENTIAL', 'HIGH', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida ICMS DIFAL em operações interestaduais'),
('ICMS_FCP', 'FCP - Fundo de Combate à Pobreza', 'ICMS_FCP', 'HIGH', '{"enabled": true}', 1, true, 'Valida FCP em UFs aplicáveis'),
('ICMS_ST', 'ICMS Substituição Tributária (ST)', 'ICMS_ST', 'HIGH', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida ICMS ST por NCM e UF'),

-- Freight Rules
('FRETE_PESO_VALOR', 'Frete Peso vs Valor (Faixas)', 'FREIGHT_WEIGHT_VALUE', 'HIGH', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida frete por faixas de peso'),
('FRETE_CUBAGE', 'Frete Cubagem (m³) vs Tabela', 'FREIGHT_CUBAGE', 'HIGH', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida frete por faixas de cubagem'),
('PESO_REAL_VS_FATURADO', 'Peso Real (XML) vs. Peso Faturado', 'PESO_REAL_VS_FATURADO', 'HIGH', '{"enabled": true, "tolerance_pct": 5.0}', 1, true, 'Detecta divergência de peso > 5%'),
('VALOR_MINIMO_FRETE', 'Valor Mínimo de Frete (ANTT 5.839/2021)', 'VALOR_MINIMO_FRETE', 'CRITICAL', '{"enabled": true}', 1, true, 'Valida piso mínimo ANTT por eixos e distância'),

-- Other Rules
('REDESPACHO_VALIDACAO', 'Validação de Redespacho (CT-e Complementar)', 'REDESPACHO', 'HIGH', '{"enabled": true, "max_ratio": 1.1}', 1, true, 'Valida redespacho não excede 110% do frete principal'),
('PEDAGIO_CONFERENCIA', 'Conferência de Pedágio', 'TOLL_PLAZA', 'MEDIUM', '{"enabled": true, "tolerance": 0.50}', 1, true, 'Confere valores de pedágio com tabela'),
('AD_VALOREM', 'Ad Valorem (Seguro sobre Valor)', 'AD_VALOREM', 'MEDIUM', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida % sobre valor da mercadoria'),
('GRIS', 'GRIS - Gerenciamento de Risco', 'GRIS', 'MEDIUM', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Valida % GRIS sobre valor da mercadoria'),
('SICOBAN_TABLE_REAL', 'Tabela Sicoban/ANTT - Lookup por CEP', 'SICOBAN_TABLE', 'HIGH', '{"enabled": true, "min_difference": 0.01}', 1, true, 'Lookup frete por CEP origem/destino + tipo carga'),

-- CT-e Complementar (3 rules)
('CTE_ANULACAO', 'CT-e Complementar - Anulação', 'COMPLEMENTARY_CTE', 'HIGH', '{"enabled": true}', 1, true, 'Valida CT-e anulação (tpEmis=3) referencia original'),
('CTE_SUBSTITUICAO', 'CT-e Complementar - Substituição', 'COMPLEMENTARY_CTE', 'HIGH', '{"enabled": true}', 1, true, 'Valida CT-e substituição (tpEmis=2) valores diferentes'),
('CTE_COMPLEMENTO_VALOR', 'CT-e Complementar - Complemento de Valor', 'COMPLEMENTARY_CTE', 'MEDIUM', '{"enabled": true}', 1, true, 'Valida CT-e complemento (tpEmis=4) apenas aumenta valores');