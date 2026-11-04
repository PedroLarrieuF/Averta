---
id: 42
title: "API Public: JWT Authorizer Lambda"
priority: critical
type: feature
agent: backend
sprint: 1
estimate: M
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 42: API Public - JWT Authorizer Lambda

## Contexto
Lambda Authorizer para AWS API Gateway que valida API Key, gera JWT RS256 com claims (sub, scopes, tier, company_id) e injeta no request para o backend.

## Arquitetura
```
API Gateway Request
       │
       ▼
┌──────────────────┐
│  Lambda Authorizer│
│  (Token Validation)│
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Valid?  │
    └────┬────┘
   No  │  Yes
    ▼    ▼
  401  Generate JWT
         │
         ▼
    Policy Document
    + Context (claims)
         │
         ▼
    Backend recebe
    Authorization: Bearer <JWT>
    X-API-Key: <original>
    X-API-Key-ID: <uuid>
```

## Tasks

### 1. Lambda Authorizer (`lambdas/authorizer/handler.py`)
```python
import json
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import boto3
import os

# Cache de chaves públicas (carregado do Parameter Store/Secrets Manager)
JWKS_CACHE = {}

def handler(event, context):
    """
    API Gateway Lambda Authorizer (TOKEN type)
    event: {
        "type": "TOKEN",
        "authorizationToken": "avsk_xxxxxxxx...",
        "methodArn": "arn:aws:execute-api:region:account:api-id/stage/GET/resource"
    }
    """
    try:
        # 1. Extract API Key
        api_key = event["authorizationToken"].replace("Bearer ", "").strip()
        if not api_key.startswith("avsk_"):
            return deny_all(event["methodArn"], "Invalid API Key format")

        # 2. Validate API Key (call internal service or DB)
        key_data = validate_api_key(api_key)
        if not key_data:
            return deny_all(event["methodArn"], "Invalid or revoked API Key")

        # 3. Check tier access (sandbox vs prod)
        stage = extract_stage(event["methodArn"])
        if key_data["tier"] == "free" and stage == "prod":
            return deny_all(event["methodArn"], "Free tier only allows sandbox")

        # 4. Generate JWT RS256
        jwt_token = generate_jwt(key_data)

        # 5. Return policy + context
        return {
            "principalId": key_data["id"],
            "policyDocument": generate_policy(event["methodArn"], "Allow"),
            "context": {
                "api_key_id": key_data["id"],
                "company_id": key_data["company_id"],
                "tier": key_data["tier"],
                "scopes": ",".join(key_data["scopes"]),
                "jwt": jwt_token  # Backend validates this
            },
            "usageIdentifierKey": key_data["id"]  # For API Gateway usage plans
        }

    except Exception as e:
        print(f"Authorizer error: {e}")
        return deny_all(event["methodArn"], "Authorization failed")

def validate_api_key(api_key: str) -> Optional[dict]:
    """Call internal validation endpoint or query DB directly"""
    # Option A: HTTP call to backend /internal/api-keys/validate
    # Option B: Direct DB query (preferred for latency)
    # Returns: {id, company_id, scopes, tier, is_active, expires_at}
    pass

def generate_jwt(key_data: dict) -> str:
    """Generate RS256 JWT with 5min expiry"""
    private_key = get_private_key()  # From Secrets Manager
    now = datetime.now(timezone.utc)
    payload = {
        "sub": key_data["id"],
        "company_id": key_data["company_id"],
        "tier": key_data["tier"],
        "scopes": key_data["scopes"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "iss": "averta-api-gateway",
        "aud": "averta-backend"
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def generate_policy(method_arn: str, effect: str) -> dict:
    """Generate IAM policy for API Gateway"""
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": method_arn
        }]
    }

def deny_all(method_arn: str, message: str = "Unauthorized") -> dict:
    return {
        "principalId": "unauthorized",
        "policyDocument": generate_policy(method_arn, "Deny"),
        "context": {"error": message}
    }
```

### 2. Private/Public Key Management
- **Private Key**: AWS Secrets Manager (`averta/api/gateway/jwt-private-key`)
- **Public Key (JWKS)**: AWS Parameter Store (`/averta/api/gateway/jwks`) ou endpoint `/.well-known/jwks.json`
- **Rotation**: Anual, com overlap de 30 dias (duas chaves válidas)

### 3. Backend JWT Validation Middleware (`middleware/auth.py`)
```python
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWKS
import httpx

JWKS_URL = os.getenv("JWKS_URL", "https://api.averta.com/.well-known/jwks.json")
jwks_client = JWKS(JWKS_URL)

async def validate_api_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing JWT")

    token = auth.split(" ")[1]
    try:
        # Validate signature, expiry, issuer, audience
        payload = jwt.decode(
            token,
            jwks_client.get_signing_key,
            algorithms=["RS256"],
            issuer="averta-api-gateway",
            audience="averta-backend"
        )
        # Inject into request.state
        request.state.api_key_id = payload["sub"]
        request.state.company_id = payload["company_id"]
        request.state.tier = payload["tier"]
        request.state.scopes = payload["scopes"]
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "JWT expired")
    except jwt.JWTError as e:
        raise HTTPException(401, f"Invalid JWT: {e}")

# Dependency for scope checking
def require_scope(scope: str):
    def checker(request: Request = Depends(validate_api_jwt)):
        if scope not in request.state.scopes and "admin:all" not in request.state.scopes:
            raise HTTPException(403, f"Scope required: {scope}")
    return checker
```

### 4. Usage Plan Integration
- Authorizer retorna `usageIdentifierKey` = `api_key_id`
- API Gateway associa ao Usage Plan correspondente ao tier
- Usage Plans criados via CDK (Card 43)

### 5. Caching
- API Gateway cache TTL: 300 segundos (padrão)
- Cache key: API Key
- Invalidar cache na rotação/revogação (chamar `apigateway:UpdateAuthorizer`)

### 6. Monitoring & Alerts
- CloudWatch Metrics: `AuthorizerLatency`, `AuthorizerErrors`, `UnauthorizedRequests`
- Alarms: Latency > 500ms, Error rate > 1%, 401 spike

## Acceptance Criteria
- [ ] Authorizer valida API Key em < 100ms (p95)
- [ ] JWT RS256 gerado corretamente
- [ ] Claims corretos injetados no backend
- [ ] Tier enforcement (free só sandbox)
- [ ] Scope enforcement no backend
- [ ] Cache funciona (latency < 50ms cached)
- [ ] Rotação de chaves sem downtime
- [ ] Logs estruturados para debugging

## Referências
- Card 41 (API Key Model) - Fonte dos dados
- Card 43 (API Gateway Setup) - Onde authorizer é anexado
- AWS Lambda Authorizer docs
- `lambdas/authorizer/` - Diretório do código