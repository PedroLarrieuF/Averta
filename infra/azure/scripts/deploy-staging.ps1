<#
.SYNOPSIS
    Deploys AvertaSaaS staging infrastructure to Azure using Bicep.

.DESCRIPTION
    This script deploys the complete staging infrastructure including:
    - Virtual Network with subnets
    - Log Analytics Workspace
    - Application Insights
    - Key Vault with secrets
    - PostgreSQL Flexible Server
    - Azure Cache for Redis
    - Storage Account (Blob)
    - Container Registry
    - Container Apps Environment
    - Container Apps (Backend, Celery Worker, Celery Beat, Flower)
    - Application Gateway
    - DNS Zone (if custom domain provided)
    - Monitoring and Alerts

.PARAMETER SubscriptionId
    Azure subscription ID to deploy to.

.PARAMETER ResourceGroupName
    Name of the resource group (default: rg-averta-staging).

.PARAMETER Location
    Azure region for deployment (default: eastus).

.PARAMETER ParametersFile
    Path to the parameters file (default: ../bicep/environments/staging/main.parameters.json).

.PARAMETER WhatIf
    Run in what-if mode to preview changes without deploying.

.PARAMETER Confirm
    Prompt for confirmation before deployment.

.EXAMPLE
    .\deploy-staging.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    .\deploy-staging.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -WhatIf

.EXAMPLE
    .\deploy-staging.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Confirm:$false
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,

    [string]$ResourceGroupName = "rg-averta-staging",

    [string]$Location = "eastus",

    [string]$ParametersFile = "$PSScriptRoot/../bicep/environments/staging/main.parameters.json",

    [switch]$WhatIf,

    [switch]$Confirm = $true
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

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
    az group create --name $ResourceGroupName --location $Location --tags Project=AvertaSaaS Environment=staging ManagedBy=Bicep Owner="Platform Team" CostCenter=Engineering
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

# Read parameters to check for Key Vault references
$parameters = Get-Content $ParametersFile | ConvertFrom-Json
$hasKeyVaultRefs = $false
foreach ($param in $parameters.parameters.PSObject.Properties) {
    if ($param.Value.reference -and $param.Value.reference.keyVault) {
        $hasKeyVaultRefs = $true
        $kvId = $param.Value.reference.keyVault.id
        Write-Info "Found Key Vault reference: $kvId"
    }
}

if ($hasKeyVaultRefs) {
    Write-Warning "Parameters file contains Key Vault references. Ensure Key Vault exists and secrets are populated."
    Write-Warning "Run the Key Vault setup script first if this is a new deployment."
}

# Confirm deployment
if ($Confirm -and -not $WhatIf) {
    $confirmation = Read-Host "Deploy to staging environment? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Warning "Deployment cancelled by user"
        exit 0
    }
}

# Build deployment command
$deploymentName = "staging-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
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

} catch {
    Write-Error "Deployment failed: $_"
    Write-Info "Checking deployment status..."
    az deployment group show --resource-group $ResourceGroupName --name $deploymentName --query "properties.error" -o json
    exit 1
}

# Post-deployment info
Write-Success "Staging deployment completed successfully!"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Build and push Docker images to Container Registry"
Write-Info "2. Configure GitHub Actions OIDC for CI/CD"
Write-Info "3. Set up custom domain and SSL certificates"
Write-Info "4. Configure Application Gateway WAF rules"
Write-Info "5. Test all services and monitoring"