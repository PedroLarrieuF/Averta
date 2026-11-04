---
name: averta-backend-ml-agent
description: Specialized agent for Machine Learning - Anomaly Detection, Isolation Forest, Model Training/Serving, Feature Engineering
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend ML Agent

> **Specialization:** ML anomaly detection, model training/serving, feature engineering, drift monitoring
> **Location:** `backend/`
> **Cards:** #17 (ML Anomaly Detection - Sprint 5, L) - Joint with Rules Engine agent
> **Related Agents:** `rules-engine`, `core`

## Project Context

**Goal:** Detect anomalies in historical `difference_pct` using Isolation Forest
**Integration:** New rule `MLAnomalyRule` in Rules Engine v2
**Tech:** scikit-learn, joblib/ONNX, FastAPI endpoint or sidecar

## Card #17: ML Anomaly Detection

### Definition of Ready
- [ ] Dataset histórico suficiente (>10k discrepâncias)
- [ ] Pipeline ML definido (treino, inferência, monitoramento)
- [ ] Integração com Rules Engine (nova regra ML_ANOMALY)

### Tasks
1. **Dataset Preparation**
   - Features: rule_type, carrier, client, value, weight, uf_origem, uf_destino, diff_pct, severity, document_type
   - Target: anomaly label (from auditor feedback FP/FN)
   - Train/test split temporal

2. **Model Training**
   - Isolation Forest (scikit-learn)
   - Hyperparameter tuning (contamination, n_estimators, max_samples)
   - Cross-validation temporal

3. **Model Serialization**
   - joblib for Python serving
   - ONNX for polyglot serving (optional)
   - Versioning: model_v1, model_v2, ...

4. **Inference Serving**
   - Option A: FastAPI endpoint `/ml/anomaly-score`
   - Option B: Sidecar service (mlflow, bentoml, or custom)
   - Latency target: < 50ms

5. **Rules Engine Integration**
   - New rule `MLAnomalyRule` in `rules_critical.py`
   - Calls inference endpoint
   - Triggers on high anomaly score (> threshold)
   - Adds to discrepancy with type `ML_ANOMALY`

6. **Feedback Loop**
   - Auditor marks FP/FN in UI
   - Collect labels for retraining
   - Monthly automated retrain

7. **Monitoring**
   - Drift detection (feature distribution shift)
   - Performance metrics (precision, recall on labeled)
   - A/B test vs deterministic rules

## Implementation Sketch

### MLAnomalyRule (in rules_critical.py)
```python
class MLAnomalyRule(BaseRule):
    rule_code = "ML_ANOMALY"
    rule_name = "ML Anomaly Detection (Isolation Forest)"
    discrepancy_type = DiscrepancyType.OTHER  # or new ML_ANOMALY type
    severity = "MEDIUM"
    relevance_tags = ["ml", "anomaly"]
    
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.threshold = config.get("anomaly_threshold", -0.5)  # Isolation Forest score
        self.endpoint = config.get("ml_endpoint", "http://localhost:8001/ml/anomaly-score")
    
    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Extract features from context
        features = self._extract_features(context)
        
        # Call ML inference
        async with httpx.AsyncClient() as client:
            response = await client.post(self.endpoint, json=features)
            score = response.json()["anomaly_score"]
        
        triggered = score < self.threshold  # Negative = anomaly in Isolation Forest
        
        return self._create_result(
            triggered=triggered,
            expected=0,  # No expected value for ML
            actual=score,
            details={
                "anomaly_score": score,
                "threshold": self.threshold,
                "features": features,
            },
            severity="HIGH" if score < -0.7 else "MEDIUM",
        )
    
    def _extract_features(self, context: RuleContext) -> dict:
        doc = context.document
        return {
            "rule_type_hash": hash(context.metadata.get("rule_code", "")),
            "carrier_id_hash": hash(doc.get("carrier_id", "")),
            "value": doc.get("total_value", 0),
            "weight": doc.get("weight", 0),
            "uf_origem": doc.get("uf_inicio", ""),
            "uf_destino": doc.get("uf_fim", ""),
            "diff_pct": context.metadata.get("difference_pct", 0),
            "severity_encoded": {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(
                context.metadata.get("severity", "MEDIUM"), 1
            ),
        }
```

### ML Inference Service (separate or in backend)
```python
# app/services/ml_inference.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()
model = joblib.load("models/isolation_forest_v1.joblib")

class AnomalyRequest(BaseModel):
    features: dict

@app.post("/ml/anomaly-score")
async def anomaly_score(request: AnomalyRequest):
    # Convert features to array in correct order
    X = np.array([[request.features[f] for f in FEATURE_ORDER]])
    score = model.decision_function(X)[0]  # Negative = anomaly
    return {"anomaly_score": float(score)}
```

## Model Training Pipeline
```python
# scripts/train_anomaly_model.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import TimeSeriesSplit
import joblib

# Load historical discrepancies
df = pd.read_parquet("data/discrepancies_history.parquet")

# Feature engineering
X = df[FEATURE_COLUMNS]

# Train
model = IsolationForest(
    contamination=0.05,
    n_estimators=200,
    max_samples=256,
    random_state=42
)
model.fit(X)

# Save
joblib.dump(model, "models/isolation_forest_v1.joblib")
```

## Acceptance Criteria
- [ ] Detecta anomalias não cobertas por rules determinísticas
- [ ] Precision > 70% (baixo false positive)
- [ ] Latência inferência < 50ms
- [ ] Retreino automático mensal
- [ ] Dashboard ML metrics

## Monitoring Dashboard Metrics
- Anomaly detection rate (daily/weekly)
- Precision/Recall on labeled feedback
- Feature drift (KS test per feature)
- Inference latency (p50, p95, p99)
- Model version in production

## Quality Gates
```bash
cd backend
poetry run lint
poetry run typecheck
poetry run pytest tests/test_ml_anomaly.py -v
```

---

*Specialized for ML. Joint work with rules-engine agent for Card #17.*