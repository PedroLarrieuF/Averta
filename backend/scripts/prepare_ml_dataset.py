#!/usr/bin/env python
"""Prepare ML dataset for anomaly detection from historical discrepancies.

This script extracts features from historical discrepancy data and auditor feedback
to create a training dataset for Isolation Forest anomaly detection.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from generated.prisma import Prisma

# Feature columns in the order expected by the model
FEATURE_COLUMNS = [
    "rule_type_hash",
    "carrier_id_hash",
    "client_id_hash",
    "value",
    "weight",
    "volume",
    "uf_origem_encoded",
    "uf_destino_encoded",
    "diff_pct",
    "severity_encoded",
    "document_type_encoded",
    "distance_km",
    "eixos",
    "has_icms",
    "has_freight_value",
]

# UF encoding
UF_ENCODING = {
    "AC": 1,
    "AL": 2,
    "AP": 3,
    "AM": 4,
    "BA": 5,
    "CE": 6,
    "DF": 7,
    "ES": 8,
    "GO": 9,
    "MA": 10,
    "MT": 11,
    "MS": 12,
    "MG": 13,
    "PA": 14,
    "PB": 15,
    "PR": 16,
    "PE": 17,
    "PI": 18,
    "RJ": 19,
    "RN": 20,
    "RS": 21,
    "RO": 22,
    "RR": 23,
    "SC": 24,
    "SP": 25,
    "SE": 26,
    "TO": 27,
}

SEVERITY_ENCODING = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}

DOCUMENT_TYPE_ENCODING = {
    "CTE": 1,
    "NFE": 2,
    "CTE_COMPLEMENTAR": 3,
    "NFE_COMPLEMENTAR": 4,
    "INVOICE": 5,
    "SPREADSHEET": 6,
    "CONTRACT": 7,
    "OTHER": 8,
}


async def fetch_historical_data(prisma: Prisma, days_back: int = 365) -> list[dict[str, Any]]:
    """Fetch historical discrepancies with auditor feedback."""
    since = datetime.utcnow() - timedelta(days=days_back)

    discrepancies = await prisma.discrepancy.find_many(
        where={
            "createdAt": {"gte": since},
            "status": {"in": ["APPROVED", "REJECTED", "CLOSED"]},  # Has auditor decision
        },
        include={
            "document": True,
            "contract": True,
            "carrier": True,
            "client": True,
        },
        order={"createdAt": "asc"},
    )

    return discrepancies


def extract_features(discrepancy: Any) -> dict[str, float] | None:
    """Extract ML features from a discrepancy record."""
    doc = discrepancy.document
    if not doc:
        return None

    # Get carrier/client IDs for hashing
    carrier_id = discrepancy.carrierId or ""
    client_id = discrepancy.clientId or ""

    # Hash categorical IDs (consistent hashing)
    rule_type_hash = hash(discrepancy.ruleCode) % 10000
    carrier_id_hash = hash(carrier_id) % 10000
    client_id_hash = hash(client_id) % 10000

    # UF encoding
    uf_origem = getattr(doc, "uf_inicio", None) or getattr(doc, "ufOrigem", None) or ""
    uf_destino = getattr(doc, "uf_fim", None) or getattr(doc, "ufDestino", None) or ""
    uf_origem_encoded = UF_ENCODING.get(uf_origem.upper() if uf_origem else "", 0)
    uf_destino_encoded = UF_ENCODING.get(uf_destino.upper() if uf_destino else "", 0)

    # Document type encoding
    doc_type = getattr(doc, "type", None) or "OTHER"
    document_type_encoded = DOCUMENT_TYPE_ENCODING.get(
        doc_type.value if hasattr(doc_type, "value") else str(doc_type), 8
    )

    # Severity encoding
    severity = getattr(discrepancy, "details", {}).get("severity", "MEDIUM")
    if isinstance(severity, str):
        severity_encoded = SEVERITY_ENCODING.get(severity.upper(), 1)
    else:
        severity_encoded = 1

    # Numeric features
    value = getattr(doc, "totalValue", None) or getattr(doc, "total_value", None) or 0
    weight = getattr(doc, "weight", None) or 0
    volume = getattr(doc, "volume", None) or 0
    diff_pct = getattr(discrepancy, "differencePct", None) or 0
    distance_km = getattr(doc, "distancia_km", None) or getattr(doc, "distanceKm", None) or 0
    eixos = (
        getattr(doc, "modal_rodoviario_veiculo_eixos", None)
        or getattr(doc, "modalRodoviarioVeiculoEixos", None)
        or 0
    )

    # Boolean flags as numeric
    has_icms = 1 if (getattr(doc, "icmsValue", None) or getattr(doc, "icms_value", None)) else 0
    has_freight_value = (
        1 if (getattr(doc, "freightValue", None) or getattr(doc, "freight_value", None)) else 0
    )

    return {
        "rule_type_hash": float(rule_type_hash),
        "carrier_id_hash": float(carrier_id_hash),
        "client_id_hash": float(client_id_hash),
        "value": float(value),
        "weight": float(weight),
        "volume": float(volume),
        "uf_origem_encoded": float(uf_origem_encoded),
        "uf_destino_encoded": float(uf_destino_encoded),
        "diff_pct": float(diff_pct),
        "severity_encoded": float(severity_encoded),
        "document_type_encoded": float(document_type_encoded),
        "distance_km": float(distance_km),
        "eixos": float(eixos),
        "has_icms": float(has_icms),
        "has_freight_value": float(has_freight_value),
    }


def create_labels(discrepancy: Any) -> int:
    """Create anomaly label from auditor feedback.

    Returns:
        1 = normal (auditor approved the discrepancy)
        -1 = anomaly (auditor rejected/marked as false positive)
    """
    status = getattr(discrepancy, "status", None)
    if hasattr(status, "value"):
        status = status.value

    # APPROVED = normal discrepancy (not anomaly)
    # REJECTED = false positive (anomaly detected by rules but not real)
    # CLOSED = could be either, check notes
    if status == "APPROVED":
        return 1
    elif status == "REJECTED":
        return -1  # Anomaly (FP)
    elif status == "CLOSED":
        # Check notes for auditor feedback
        notes = getattr(discrepancy, "notes", "") or ""
        if "false positive" in notes.lower() or "fp" in notes.lower():
            return -1
        return 1
    return 1  # Default to normal


async def prepare_dataset(
    output_path: str = "data/discrepancies_history.parquet", days_back: int = 365
):
    """Main function to prepare the ML dataset."""
    prisma = Prisma()
    await prisma.connect()

    try:
        discrepancies = await fetch_historical_data(prisma, days_back)

        if len(discrepancies) < 1000:
            # Generate synthetic data for development
            discrepancies = await generate_synthetic_data(prisma, target_count=10000)

        rows = []
        for d in discrepancies:
            features = extract_features(d)
            if features:
                label = create_labels(d)
                features["label"] = label
                features["discrepancy_id"] = d.id
                features["rule_code"] = d.ruleCode
                rows.append(features)

        df = pd.DataFrame(rows)

        # Ensure all feature columns exist
        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0.0

        # Reorder columns
        df = df[["discrepancy_id", "rule_code", "label"] + FEATURE_COLUMNS]

        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)

        return df

    finally:
        await prisma.disconnect()


async def generate_synthetic_data(prisma: Prisma, target_count: int = 10000) -> list[Any]:
    """Generate synthetic discrepancy data for development/testing."""

    # Get some real carriers/clients for realistic IDs
    carriers = await prisma.carrier.find_many(take=20)
    clients = await prisma.client.find_many(take=20)
    contracts = await prisma.contract.find_many(take=20)

    carrier_ids = [c.id for c in carriers] if carriers else [f"carrier-{i}" for i in range(20)]
    client_ids = [c.id for c in clients] if clients else [f"client-{i}" for i in range(20)]
    contract_ids = [c.id for c in contracts] if contracts else [f"contract-{i}" for i in range(20)]

    rule_codes = [
        "ICMS_DIFAL",
        "ICMS_FCP",
        "ICMS_ST",
        "FRETE_PESO_VALOR",
        "FRETE_CUBAGE",
        "PESO_REAL_VS_FATURADO",
        "VALOR_MINIMO_FRETE",
        "REDESPACHO_VALIDACAO",
        "PEDAGIO_CONFERENCIA",
        "AD_VALOREM",
        "GRIS",
        "SICOBAN_TABLE_REAL",
        "CTE_ANULACAO",
        "CTE_SUBSTITUICAO",
        "CTE_COMPLEMENTO_VALOR",
    ]

    ufs = list(UF_ENCODING.keys())
    doc_types = list(DOCUMENT_TYPE_ENCODING.keys())
    severities = list(SEVERITY_ENCODING.keys())

    # Create mock objects
    class MockDiscrepancy:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MockDoc:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MockContract:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MockCarrier:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MockClient:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    synthetic = []
    for i in range(target_count):
        rule_code = np.random.choice(rule_codes)
        carrier_id = np.random.choice(carrier_ids)
        client_id = np.random.choice(client_ids)
        contract_id = np.random.choice(contract_ids)

        # Generate realistic values based on rule type
        if "ICMS" in rule_code:
            value = np.random.lognormal(10, 1)  # ~20k
            weight = np.random.lognormal(8, 1)
            diff_pct = np.random.exponential(15)  # ICMS diffs can be larger
        elif "FRETE" in rule_code or "PESO" in rule_code or "VALOR_MINIMO" in rule_code:
            value = np.random.lognormal(9, 1)
            weight = np.random.lognormal(7, 1)
            diff_pct = np.random.exponential(10)
        else:
            value = np.random.lognormal(9, 1)
            weight = np.random.lognormal(7, 1)
            diff_pct = np.random.exponential(8)

        # 5% anomaly rate
        is_anomaly = np.random.random() < 0.05
        if is_anomaly:
            diff_pct *= np.random.uniform(3, 10)  # Anomalies have larger diffs
            status = "REJECTED"
        else:
            status = "APPROVED"

        doc = MockDoc(
            id=f"doc-{i}",
            type=np.random.choice(doc_types),
            uf_inicio=np.random.choice(ufs),
            uf_fim=np.random.choice(ufs),
            totalValue=value,
            freightValue=value * 0.1,
            icmsValue=value * 0.18 if "ICMS" in rule_code else None,
            weight=weight,
            volume=weight / 500,
            distancia_km=np.random.uniform(100, 2000),
            modal_rodoviario_veiculo_eixos=np.random.choice([2, 3, 4, 5, 6]),
            peso_bruto=weight * np.random.uniform(0.95, 1.05),
        )

        discrepancy = MockDiscrepancy(
            id=f"disc-{i}",
            ruleCode=rule_code,
            clientId=client_id,
            carrierId=carrier_id,
            contractId=contract_id,
            differencePct=diff_pct,
            status=status,
            notes="False positive" if is_anomaly else "",
            details={"severity": np.random.choice(severities)},
            document=doc,
            carrier=MockCarrier(id=carrier_id),
            client=MockClient(id=client_id),
            contract=MockContract(id=contract_id),
        )
        synthetic.append(discrepancy)

    return synthetic


if __name__ == "__main__":
    asyncio.run(prepare_dataset())
