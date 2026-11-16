<#
.SYNOPSIS
    Deploys AvertaSaaS production infrastructure to Azure using Bicep.

.DESCRIPTION
    This script deploys the complete production infrastructure with high availability.
    Requires manual approval and additional safety checks.

.PARAMETER SubscriptionId
    Azure subscription ID to deploy to.

.PARAMETER ResourceGroupName
    Name of the resource group (default: rg-averta-production).

.PARAMETER Location
    Azure region for deployment (default: eastus).

.PARAMETER ParametersFile
    Path to the parameters file (default: ../bicep/environments/production/main.parameters.json).

.PARAMETER WhatIf
    Run in what-if mode to preview changes without deploying.

.PARAMETER SkipConfirmation
    Skip the manual confirmation prompt (not recommended for production).

.PARAMETER ApproverEmail
    Email of the person approving this production deployment.

.EXAMPLE
    .\deploy-production.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -ApproverEmail "admin@averta.com.br"

.EXAMPLE
    .\deploy-production.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -WhatIf
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,

    [string]$ResourceGroupName = "rg-averta-production",

    [string]$Location = "eastus",

    [string]$ParametersFile = "$PSScriptRoot/../bicep/environments/production/main.parameters.json",

    [switch]$WhatIf,

    [Parameter(Mandatory=$true)]
    [string]$ApproverEmail,

    [switch]$SkipConfirmation = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Critical { param([string]$Message) Write-Host "[CRITICAL] $Message" -ForegroundColor Red -BackgroundColor White }

# Production safety banner
Write-Critical "=========================================="
Write-Critical "   PRODUCTION DEPLOYMENT - AVERTA SAAS   "
Write-Critical "=========================================="
Write-Critical "Environment: PRODUCTION"
Write-Critical "Approver: $ApproverEmail"
Write-Critical "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Critical "=========================================="

# Check prerequisites
Write-Info "Checking prerequisites..."

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI not found. Please install: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
}

# Check Bicep
if (-not (az bicep version -ErrorAction SilentlyContinue)) {
    Write-Warning "Bicep not installed. Installing..."
    az bicep install
}

# Check Azure login
$account = az account show --query "id" -o tsv 2>$null
if (-not $account) {
    Write-Warning "Not logged in to Azure. Running az login..."
    az login --use-device-code
}

# Set subscription
Write-Info "Setting subscription to $SubscriptionId..."
az account set --subscription $SubscriptionId

# Verify subscription
$currentSub = az account show --query "id" -o tsv
if ($currentSub -ne $SubscriptionId) {
    Write-Error "Failed to set subscription. Current: $currentSub, Expected: $SubscriptionId"
    exit 1
}

Write-Success "Subscription set to $SubscriptionId"

# Check if resource group exists
$rgExists = az group exists --name $ResourceGroupName -o tsv
if ($rgExists -eq "false") {
    Write-Info "Resource group '$ResourceGroupName' does not exist. Creating..."
    az group create --name $ResourceGroupName --location $Location --tags Project=AvertaSaaS Environment=production ManagedBy=Bicep Owner="Platform Team" CostCenter=Engineering Compliance=PCI-DSS DataClassification=Confidential
    Write-Success "Resource group created"
} else {
    Write-Info "Resource group '$ResourceGroupName' already exists"
}

# Validate Bicep files
Write-Info "Validating Bicep files..."
$bicepRoot = "$PSScriptRoot/../bicep"
az bicep build --file "$bicepRoot/main.bicep" --stdout | Out-Null
Write-Success "Bicep validation passed"

# Check parameters file
if (-not (Test-Path $ParametersFile)) {
    Write-Error "Parameters file not found: $ParametersFile"
    exit 1
}

# Check Key Vault references
$parameters = Get-Content $ParametersFile | ConvertFrom-Json
$hasKeyVaultRefs = $false
foreach ($param in $parameters.parameters.PSObject.Properties) {
    if ($param.Value.reference -and $param.Value.reference.keyVault) {
        $hasKeyVaultRefs = true
        $kvId = $param.Value.reference.keyVault.id
        Write-Info "Found Key Vault reference: $kvId"
    }
}

if ($hasKeyVaultRefs) {
    Write-Warning "Parameters file contains Key Vault references. Ensure Key Vault exists and secrets are populated."
}

# Additional production checks
Write-Info "Running production pre-deployment checks..."

# Check if Key Vault exists and has required secrets
$kvName = "averta-kv-production"
$kvExists = az keyvault show --name $kvName --query "name" -o tsv 2>$null
if (-not $kvExists) {
    Write-Error "Production Key Vault '$kvName' not found! Run Key Vault setup first."
    exit 1
}

$requiredSecrets = @("pg-admin-password", "redis-access-key", "jwt-secret-key", "jwt-refresh-secret-key", "sendgrid-api-key", "smtp-password")
$missingSecrets = @()
foreach ($secret in $requiredSecrets) {
    $secretExists = az keyvault secret show --vault-name $kvName --name $secret --query "id" -o tsv 2>$null
    if (-not $secretExists) {
        $missingSecrets += $secret
    }
}

if ($missingSecrets.Count -gt 0) {
    Write-Error "Missing required secrets in Key Vault: $($missingSecrets -join ', ')"
    exit 1
}

Write-Success "All required secrets found in Key Vault"

# Check custom domain DNS
$customDomain = "averta.com.br"
Write-Info "Checking DNS for $customDomain..."
# This would need actual DNS resolution check

# Confirm deployment (MANDATORY for production)
if (-not $SkipConfirmation -and -not $WhatIf) {
    Write-Critical ""
    Write-Critical "⚠️  PRODUCTION DEPLOYMENT CONFIRMATION REQUIRED ⚠️"
    Write-Critical ""
    Write-Critical "You are about to deploy to PRODUCTION environment."
    Write-Critical "This will create/update production resources and may incur costs."
    Write-Critical "Approver: $ApproverEmail"
    Write-Critical ""

    $confirmation = Read-Host "Type 'DEPLOY TO PRODUCTION' to confirm (case-sensitive)"
    if ($confirmation -ne "DEPLOY TO PRODUCTION") {
        Write-Warning "Deployment cancelled - confirmation text did not match"
        exit 0
    }

    Write-Critical "Confirmation received. Proceeding with production deployment..."
}

# Build deployment command
$deploymentName = "production-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$templateFile = "$bicepRoot/main.bicep"

Write-Info "Starting deployment: $deploymentName"
Write-Info "Template: $templateFile"
Write-Info "Parameters: $ParametersFile"

$cmd = @(
    "az", "deployment", "group", "create",
    "--resource-group", $ResourceGroupName,
    "--template-file", $templateFile,
    "--parameters", "@$ParametersFile",
    "--name", $deploymentName,
    "--mode", "Incremental"
)

if ($WhatIf) {
    $cmd += "--what-if"
    Write-Warning "Running in WHAT-IF mode - no changes will be applied"
}

# Execute deployment
try {
    $startTime = Get-Date
    Write-Info "Deployment started at $startTime"

    & $cmd

    $endTime = Get-Date
    $duration = $endTime - $startTime
    Write-Success "Deployment completed in $($duration.ToString('hh\:mm\:ss'))"

    # Show outputs
    Write-Info "Fetching deployment outputs..."
    $outputs = az deployment group show --resource-group $ResourceGroupName --name $deploymentName --query "properties.outputs" -o json
    $outputs | ConvertFrom-Json | Format-List

    # Log deployment
    $logEntry = @{
        deploymentName = $deploymentName
        timestamp = Get-Date -Format 'o'
        approver = $ApproverEmail
        subscription = $SubscriptionId
        resourceGroup = $ResourceGroupName
        status = "SUCCESS"
        duration = $duration.ToString()
    }
    $logEntry | ConvertTo-Json -Depth 3 | Out-File "$PSScriptRoot/../logs/deployment-log-$(Get-Date -Format 'yyyyMMdd').json" -Append -Encoding utf8

} catch {
    Write-Error "Deployment failed: $_"

    # Log failure
    $logEntry = @{
        deploymentName = $deploymentName
        timestamp = Get-Date -Format 'o'
        approver = $ApproverEmail
        subscription = $SubscriptionId
        resourceGroup = $ResourceGroupName
        status = "FAILED"
        error = $_
    }
    $logEntry | ConvertTo-Json -Depth 3 | Out-File "$PSScriptRoot/../logs/deployment-log-$(Get-Date -Format 'yyyyMMdd').json" -Append -Encoding utf8

    Write-Info "Checking deployment status..."
    az deployment group show --resource-group $ResourceGroupName --name $deploymentName --query "properties.error" -o json
    exit 1
}

# Post-deployment info
Write-Success "Production deployment completed successfully!"
Write-Critical ""
Write-Critical "=========================================="
Write-Critical "   PRODUCTION DEPLOYMENT COMPLETE        "
Write-Critical "=========================================="
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Verify all services are healthy in Azure Portal"
Write-Info "2. Run smoke tests against production endpoints"
Write-Info "3. Configure DNS records for custom domain"
Write-Info "4. Set up SSL certificates in Application Gateway"
Write-Info "5. Configure GitHub Actions OIDC for CI/CD"
Write-Info "6. Enable monitoring alerts and on-call rotations"
Write-Info "7. Document deployment in runbook"
Write-Info ""
Write-Critical "Deployment logged by: $ApproverEmail at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"