"""ML Inference Service - FastAPI endpoint for anomaly scoring."""

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Feature columns in exact order used during training
FEATURE_ORDER = [
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

# UF encoding (must match training)
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


class AnomalyRequest(BaseModel):
    """Request model for anomaly scoring."""

    features: dict[str, float] = Field(..., description="Feature dictionary")


class AnomalyResponse(BaseModel):
    """Response model for anomaly scoring."""

    anomaly_score: float = Field(
        ..., description="Isolation Forest decision function score (negative = anomaly)"
    )
    is_anomaly: bool = Field(..., description="Whether the score indicates an anomaly")
    threshold: float = Field(..., description="Threshold used for anomaly classification")
    model_version: str = Field(..., description="Model version")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_version: str | None = None


# Default threshold (Isolation Forest: negative = anomaly)
DEFAULT_MODEL_THRESHOLD: float = -0.5


class ModelManager:
    """Singleton manager for ML model and scaler."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._scaler: Any | None = None
        self._model_version: str | None = None
        self._model_threshold: float = DEFAULT_MODEL_THRESHOLD

    @property
    def model(self) -> Any | None:
        return self._model

    @property
    def scaler(self) -> Any | None:
        return self._scaler

    @property
    def model_version(self) -> str | None:
        return self._model_version

    @property
    def model_threshold(self) -> float:
        return self._model_threshold

    def load_model(self) -> tuple[Any, Any]:
        """Load the latest trained model and scaler."""
        models_dir = Path("models")
        model_path = models_dir / "isolation_forest_latest.joblib"
        scaler_path = models_dir / "scaler_latest.joblib"
        metadata_path = models_dir / "metadata_latest.json"

        if not model_path.exists():
            raise RuntimeError(f"Model not found at {model_path}. Run train_anomaly_model.py first.")

        self._model = joblib.load(model_path)
        self._scaler = joblib.load(scaler_path)

        if metadata_path.exists():
            with metadata_path.open() as f:
                metadata = json.load(f)
            self._model_version = metadata.get("version", "unknown")
            # Use contamination-based threshold
            contamination = metadata.get("model_params", {}).get("contamination", 0.05)
            self._model_threshold = -contamination * 10  # Approximate heuristic

        return self._model, self._scaler


# Global model manager instance
model_manager = ModelManager()


app = FastAPI(
    title="AvertaSaaS ML Inference Service",
    description="Isolation Forest anomaly detection for freight audit discrepancies",
    version="1.0.0",
)


app = FastAPI(
    title="AvertaSaaS ML Inference Service",
    description="Isolation Forest anomaly detection for freight audit discrepancies",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Load model on startup."""
    try:
        model_manager.load_model()
    except Exception:
        pass


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model_manager.model is not None else "degraded",
        model_loaded=model_manager.model is not None,
        model_version=model_manager.model_version,
    )


@app.post("/ml/anomaly-score", response_model=AnomalyResponse)
async def anomaly_score(request: AnomalyRequest) -> AnomalyResponse:
    """Score anomaly for given features.

    Expected features (in order):
    - rule_type_hash: hashed rule code
    - carrier_id_hash: hashed carrier ID
    - client_id_hash: hashed client ID
    - value: total document value
    - weight: document weight
    - volume: document volume
    - uf_origem_encoded: encoded origin UF
    - uf_destino_encoded: encoded destination UF
    - diff_pct: percentage difference
    - severity_encoded: encoded severity (0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL)
    - document_type_encoded: encoded document type
    - distance_km: distance in km
    - eixos: number of axles
    - has_icms: 1 if ICMS data present, 0 otherwise
    - has_freight_value: 1 if freight value present, 0 otherwise
    """
    if model_manager.model is None or model_manager.scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check /health endpoint.")

    # Convert features dict to array in correct order
    try:
        X = np.array([[request.features.get(f, 0.0) for f in FEATURE_ORDER]])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid features: {str(e)}") from e

    # Scale features
    X_scaled = model_manager.scaler.transform(X)

    # Get anomaly score (decision_function: negative = anomaly)
    score = float(model_manager.model.decision_function(X_scaled)[0])

    # Classify
    is_anomaly = score < model_manager.model_threshold

    return AnomalyResponse(
        anomaly_score=score,
        is_anomaly=is_anomaly,
        threshold=model_manager.model_threshold,
        model_version=model_manager.model_version or "unknown",
    )


@app.post("/ml/anomaly-score/batch")
async def anomaly_score_batch(requests: list[AnomalyRequest]) -> list[AnomalyResponse | dict[str, str]]:
    """Batch anomaly scoring for multiple records."""
    if model_manager.model is None or model_manager.scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    results: list[AnomalyResponse | dict[str, str]] = []
    for req in requests:
        try:
            X = np.array([[req.features.get(f, 0.0) for f in FEATURE_ORDER]])
            X_scaled = model_manager.scaler.transform(X)
            score = float(model_manager.model.decision_function(X_scaled)[0])
            is_anomaly = score < model_manager.model_threshold
            results.append(
                AnomalyResponse(
                    anomaly_score=score,
                    is_anomaly=is_anomaly,
                    threshold=model_manager.model_threshold,
                    model_version=model_manager.model_version or "unknown",
                )
            )
        except Exception as e:
            results.append({"error": str(e)})

    return results


def extract_features_from_context(context: dict[str, Any]) -> dict[str, float]:
    """Extract ML features from rule evaluation context (for Rules Engine integration)."""
    doc = context.get("document", {})
    metadata = context.get("metadata", {})

    # Hash categorical fields
    rule_code = metadata.get("rule_code", "")
    carrier_id = doc.get("carrier_id", "") or doc.get("carrierId", "")
    client_id = doc.get("client_id", "") or doc.get("clientId", "")

    rule_type_hash = hash(rule_code) % 10000
    carrier_id_hash = hash(carrier_id) % 10000
    client_id_hash = hash(client_id) % 10000

    # UF encoding
    uf_origem = doc.get("uf_inicio", "") or doc.get("ufOrigem", "") or doc.get("uf_origem", "")
    uf_destino = doc.get("uf_fim", "") or doc.get("ufDestino", "") or doc.get("uf_destino", "")
    uf_origem_encoded = UF_ENCODING.get(uf_origem.upper() if uf_origem else "", 0)
    uf_destino_encoded = UF_ENCODING.get(uf_destino.upper() if uf_destino else "", 0)

    # Document type
    doc_type = doc.get("type", "OTHER")
    if hasattr(doc_type, "value"):
        doc_type = doc_type.value
    document_type_encoded = DOCUMENT_TYPE_ENCODING.get(str(doc_type).upper(), 8)

    # Severity
    severity = metadata.get("severity", "MEDIUM")
    severity_encoded = SEVERITY_ENCODING.get(
        severity.upper() if isinstance(severity, str) else "MEDIUM", 1
    )

    # Numeric features
    value = doc.get("total_value", 0) or doc.get("totalValue", 0) or 0
    weight = doc.get("weight", 0) or 0
    volume = doc.get("volume", 0) or 0
    diff_pct = metadata.get("difference_pct", 0) or metadata.get("differencePct", 0) or 0
    distance_km = doc.get("distancia_km", 0) or doc.get("distanceKm", 0) or 0
    eixos = (
        doc.get("modal_rodoviario_veiculo_eixos", 0)
        or doc.get("modalRodoviarioVeiculoEixos", 0)
        or 0
    )

    has_icms = 1 if (doc.get("icms_value", None) or doc.get("icmsValue", None)) else 0
    has_freight_value = (
        1 if (doc.get("freight_value", None) or doc.get("freightValue", None)) else 0
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
