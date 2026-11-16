# AvertaSaaS - Azure Infrastructure

This directory contains the Azure infrastructure as code (Bicep) for deploying AvertaSaaS to Azure.

## Architecture Overview

```
                                    ┌─────────────────┐
                                    │   Azure DNS     │
                                    │  (Custom Domain)│
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Application    │
                                    │    Gateway      │
                                    │  (WAF + TLS)    │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
            ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
            │ Container   │          │ Container   │          │ Container   │
            │   App       │          │   App       │          │   App       │
            │  (Backend)  │          │ (Celery     │          │ (Celery     │
            │             │          │  Workers)   │          │   Beat)     │
            └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
                   │                        │                        │
                   └────────────────────────┼────────────────────────┘
                                            │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
            ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
            │ PostgreSQL  │          │   Azure     │          │  Azure Blob │
            │  Flexible   │          │   Cache     │          │  Storage    │
            │   Server    │          │   for Redis │          │             │
            │  (Multi-AZ) │          │ (Cluster)   │          │             │
            └─────────────┘          └─────────────┘          └─────────────┘
```

## Azure Services Used

| Service | Purpose | SKU (Staging) | SKU (Production) |
|---------|---------|---------------|------------------|
| **Container Apps** | Serverless containers | General Purpose | General Purpose + Memory/Compute Optimized |
| **PostgreSQL Flexible Server** | Primary database | Standard_D2s_v3, 128GB | Standard_D8s_v3, 512GB, Zone Redundant |
| **Azure Cache for Redis** | Caching & Celery broker | Standard C1 | Premium P2, Clustered |
| **Storage Account** | Blob storage for documents | Standard_LRS | Standard_ZRS |
| **Container Registry** | Docker images | Standard | Premium |
| **Application Gateway** | L7 Load Balancer + WAF | Standard_v2 | WAF_v2, Autoscaling |
| **Key Vault** | Secrets management | Standard | Standard, Purge Protection |
| **Application Insights** | APM & Monitoring | Basic | Standard |
| **Log Analytics** | Centralized logging | PerGB2018 | PerGB2018 |
| **Azure DNS** | Custom domain management | - | - |

## Directory Structure

```
infra/azure/
├── bicep/
│   ├── main.bicep                    # Main entry point
│   ├── modules/
│   │   ├── vnet.bicep                # Virtual Network & subnets
│   │   ├── log-analytics.bicep       # Log Analytics workspace
│   │   ├── app-insights.bicep        # Application Insights
│   │   ├── key-vault.bicep           # Key Vault
│   │   ├── key-vault-secrets.bicep   # Key Vault secrets
│   │   ├── postgresql.bicep          # PostgreSQL Flexible Server
│   │   ├── redis.bicep               # Azure Cache for Redis
│   │   ├── storage.bicep             # Storage Account (Blob)
│   │   ├── container-registry.bicep  # Container Registry
│   │   ├── container-apps-env.bicep  # Container Apps Environment
│   │   ├── container-apps.bicep      # Container Apps (Backend, Workers, Beat)
│   │   ├── application-gateway.bicep # Application Gateway + WAF
│   │   ├── dns-zone.bicep            # DNS Zone & records
│   │   └── monitoring.bicep          # Alerts, dashboards, diagnostics
│   └── environments/
│       ├── staging/
│       │   ├── main.bicep            # Staging deployment
│       │   └── main.parameters.json  # Staging parameters (with Key Vault refs)
│       └── production/
│           ├── main.bicep            # Production deployment
│           └── main.parameters.json  # Production parameters (with Key Vault refs)
└── scripts/
    ├── setup-keyvault.ps1            # Initialize Key Vault & secrets
    ├── deploy-staging.ps1            # Deploy to staging
    └── deploy-production.ps1         # Deploy to production (with approvals)
```

## Prerequisites

1. **Azure CLI** (v2.55+)
2. **Bicep CLI** (installed via `az bicep install`)
3. **Azure Subscription** with Owner/Contributor access
4. **Resource Group** (created by deployment scripts)
5. **Key Vault** with secrets (created by setup script)

## Quick Start

### 1. Login to Azure

```bash
az login --use-device-code
az account set --subscription <SUBSCRIPTION_ID>
```

### 2. Set up Key Vault and Secrets

```powershell
# Staging
.\infra\azure\scripts\setup-keyvault.ps1 -SubscriptionId <SUB_ID> -Environment staging

# Production (requires manual secret input)
.\infra\azure\scripts\setup-keyvault.ps1 -SubscriptionId <SUB_ID> -Environment production
```

### 3. Deploy Infrastructure

```powershell
# Staging
.\infra\azure\scripts\deploy-staging.ps1 -SubscriptionId <SUB_ID>

# Production (requires approver email)
.\infra\azure\scripts\deploy-production.ps1 -SubscriptionId <SUB_ID> -ApproverEmail "admin@averta.com.br"
```

## Manual Deployment

```bash
# Staging
az deployment sub create \
  --location eastus \
  --template-file infra/azure/bicep/main.bicep \
  --parameters environment=staging \
  --parameters @infra/azure/bicep/environments/staging/main.parameters.json

# Production
az deployment sub create \
  --location eastus \
  --template-file infra/azure/bicep/main.bicep \
  --parameters environment=production \
  --parameters @infra/azure/bicep/environments/production/main.parameters.json
```

## What-If Analysis (Preview Changes)

```bash
az deployment group what-if \
  --resource-group rg-averta-staging \
  --template-file infra/azure/bicep/main.bicep \
  --parameters @infra/azure/bicep/environments/staging/main.parameters.json
```

## GitHub Actions CI/CD

The workflow `.github/workflows/azure-deploy.yml` provides:

- **PR Validation**: Bicep linting and what-if analysis
- **Staging Deploy**: Manual trigger for staging deployment
- **Production Deploy**: Manual trigger with required approver email
- **Drift Detection**: Weekly scheduled check for configuration drift

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

### OIDC Setup for GitHub Actions

```bash
# Create service principal
az ad sp create-for-rbac --name "github-actions-averta" \
  --role Contributor \
  --scopes /subscriptions/<SUB_ID> \
  --sdk-auth

# Configure OIDC federation (one-time setup)
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{"name":"github-actions","issuer":"https://token.actions.githubusercontent.com","subject":"repo:PedroLarrieuF/Averta:ref:refs/heads/main","audiences":["api://AzureADTokenExchange"]}'
```

## Local Development with Azure Services

Use the Azure development docker-compose:

```bash
# Start all services with Azure emulators
docker compose -f docker-compose.azure.yml --env-file .env.azure up -d

# View logs
docker compose -f docker-compose.azure.yml logs -f backend

# Stop and cleanup
docker compose -f docker-compose.azure.yml down -v
```

### Local Services

| Service | Local Endpoint | Emulator |
|---------|---------------|----------|
| PostgreSQL | localhost:5432 | Native |
| Redis | localhost:6379 | Native |
| Blob Storage | localhost:10000 | Azurite |
| PgBouncer | localhost:6432 | Native |
| Mailhog | localhost:8025 | Native |

## Key Vault Secrets Structure

| Secret Name | Content | Format |
|-------------|---------|--------|
| `averta-{env}-database` | PostgreSQL connection | JSON |
| `averta-{env}-redis` | Redis connection | JSON |
| `averta-{env}-storage` | Storage account config | JSON |
| `averta-{env}-jwt` | JWT signing keys | JSON |
| `averta-{env}-sendgrid` | SendGrid API key | JSON |
| `averta-{env}-smtp` | SMTP credentials | JSON |
| `averta-{env}-app` | App configuration | JSON |

## Monitoring & Alerts

The infrastructure includes comprehensive monitoring:

- **Application Insights**: APM, distributed tracing, availability tests
- **Log Analytics**: Centralized logs from all services
- **Metric Alerts**: CPU, Memory, Latency, Errors, Queue depth
- **Log Alerts**: Database errors, Application exceptions
- **Workbooks**: Operational dashboards

### Key Alert Rules

| Alert | Severity | Threshold |
|-------|----------|-----------|
| High API Latency | Warning (2) | > 2s (prod) / > 5s (staging) |
| High Error Rate | Critical (1) | > 5% |
| Low Availability | Critical (0) | < 99.5% |
| PostgreSQL CPU | Warning (2) | > 80% |
| Redis Memory | Warning (2) | > 85% |
| Container Apps Replicas | Warning (2) | At max capacity |

## Security Features

- **Private Endpoints**: All PaaS services accessed via private links
- **Network Segmentation**: Dedicated subnets per service tier
- **NSGs**: Restrictive network security groups
- **WAF**: Application Gateway WAF with OWASP rules
- **RBAC**: Key Vault uses RBAC (no access policies)
- **Managed Identities**: Container Apps use system-assigned identities
- **TLS 1.2+**: Enforced on all services
- **Encryption**: At-rest and in-transit encryption enabled

## Cost Optimization

- **Staging**: ~$400/month (smaller SKUs, no HA)
- **Production**: ~$2,500/month (HA, larger SKUs, WAF)
- **Autoscaling**: Container Apps scale to zero when idle
- **Lifecycle Policies**: Blob storage tiering and deletion
- **Reserved Instances**: Consider for production databases

## Troubleshooting

### Common Issues

1. **Key Vault Access Denied**
   - Ensure RBAC role assignments are propagated (wait 60+ seconds)
   - Check managed identity has "Key Vault Secrets User" role

2. **Container Apps Image Pull Failed**
   - Verify ACR admin user disabled, use managed identity
   - Check ACR network rules allow Container Apps subnet

3. **PostgreSQL Connection Failed**
   - Verify VNet delegation to Microsoft.DBforPostgreSQL/flexibleServers
   - Check NSG rules allow port 5432 from Container Apps subnet

4. **Redis Connection Failed**
   - Verify VNet delegation to Microsoft.Cache/redis
   - Check TLS 1.2 required, use rediss:// scheme

### Useful Commands

```bash
# Check deployment status
az deployment group show -g rg-averta-staging -n staging-deploy-<ID>

# View Container Apps logs
az containerapp logs show -n averta-backend-staging -g rg-averta-staging --tail 100

# Check Key Vault secrets
az keyvault secret list --vault-name averta-kv-staging

# Test private endpoint connectivity
az network private-endpoint show -n averta-postgres-staging-pe -g rg-averta-staging
```

## Migration from AWS

This infrastructure replaces the AWS Terraform configuration:

| AWS Service | Azure Service |
|-------------|---------------|
| ECS Fargate | Container Apps |
| RDS PostgreSQL | PostgreSQL Flexible Server |
| ElastiCache Redis | Azure Cache for Redis |
| S3 | Azure Blob Storage |
| ALB | Application Gateway |
| Route53 | Azure DNS |
| Secrets Manager | Key Vault |
| CloudWatch | Application Insights + Log Analytics |
| IAM | Azure RBAC |
| ECR | Container Registry |

## Support

For issues or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review Azure portal for resource health
- Contact Platform Team: platform@averta.com.br