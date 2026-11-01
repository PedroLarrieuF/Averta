---
id: 17
title: "ML Anomaly Detection (Isolation Forest on difference_pct)"
priority: medium
type: feature
agent: backend
sprint: 5
estimate: L
status: backlog
created: 2026-11-01
reviewed_by: techlead
---

# Card 17: ML Anomaly Detection

## Contexto
Roadmap médio prazo. Detectar anomalias históricas em `difference_pct` usando Isolation Forest.

## Definition of Ready
- [ ] Dataset histórico suficiente (>10k discrepâncias)
- [ ] Pipeline ML definido (treino, inferência, monitoramento)
- [ ] Integração com Rules Engine (nova regra ML_ANOMALY)

## Tasks
- [ ] Coletar/preparar dataset: features (rule_type, carrier, client, value, weight, uf, diff_pct)
- [ ] Treinar Isolation Forest (scikit-learn)
- [ ] Serializar modelo (joblib/ONNX)
- [ ] Servir inferência: endpoint interno ou sidecar
- [ ] Nova rule `MLAnomalyRule` no engine v2
- [ ] Feedback loop: auditor marca FP/FN → retreino
- [ ] Monitoring: drift detection, performance metrics
- [ ] A/B test vs rules atuais

## Acceptance Criteria
- [ ] Detecta anomalias não cobertas por rules determinísticas
- [ ] Precision > 70% (baixo false positive)
- [ ] Latência inferência < 50ms
- [ ] Retreino automático mensal
- [ ] Dashboard ML metrics

## Referências
- `TECHLEAD_REVIEW.md` - Roadmap médio prazo
- scikit-learn IsolationForest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html