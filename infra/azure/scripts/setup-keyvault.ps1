<#
.SYNOPSIS
    Sets up Azure Key Vault and populates secrets for AvertaSaaS.

.DESCRIPTION
    This script creates the Key Vault (if not exists) and populates it with
    all required secrets for the application. Run this before deploying infrastructure.

.PARAMETER SubscriptionId
    Azure subscription ID.

.PARAMETER Environment
    Environment to set up: 'staging' or 'production'.

.PARAMETER ResourceGroupName
    Resource group name (default: rg-averta-{environment}).

.PARAMETER KeyVaultName
    Key Vault name (default: averta-kv-{environment}).

.PARAMETER Location
    Azure region (default: eastus).

.PARAMETER PgAdminPassword
    PostgreSQL admin password (will prompt if not provided).

.PARAMETER RedisAccessKey
    Redis access key (will prompt if not provided).

.PARAMETER JwtSecretKey
    JWT secret key (will generate if not provided).

.PARAMETER JwtRefreshSecretKey
    JWT refresh secret key (will generate if not provided).

.PARAMETER SendgridApiKey
    SendGrid API key (optional).

.PARAMETER SmtpPassword
    SMTP password (optional).

.EXAMPLE
    .\setup-keyvault.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Environment staging

.EXAMPLE
    .\setup-keyvault.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Environment production -PgAdminPassword "secure-password"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory=$true)]
    [ValidateSet('staging', 'production')]
    [string]$Environment,

    [string]$ResourceGroupName = "rg-averta-$Environment",

    [string]$KeyVaultName = "averta-kv-$Environment",

    [string]$Location = "eastus",

    [string]$PgAdminPassword,

    [string]$RedisAccessKey,

    [string]$JwtSecretKey,

    [string]$JwtRefreshSecretKey,

    [string]$SendgridApiKey,

    [string]$SmtpPassword
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI not found. Please install Azure CLI first."
    exit 1
}

# Set subscription
Write-Info "Setting subscription to $SubscriptionId..."
az account set --subscription $SubscriptionId

# Create resource group if not exists
$rgExists = az group exists --name $ResourceGroupName -o tsv
if ($rgExists -eq "false") {
    Write-Info "Creating resource group $ResourceGroupName..."
    az group create --name $ResourceGroupName --location $Location --tags Project=AvertaSaaS Environment=$Environment ManagedBy=Script
    Write-Success "Resource group created"
}

# Create Key Vault if not exists
$kvExists = az keyvault show --name $KeyVaultName --query "name" -o tsv 2>$null
if (-not $kvExists) {
    Write-Info "Creating Key Vault $KeyVaultName..."
    az keyvault create `
        --name $KeyVaultName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku standard `
        --enable-rbac-authorization true `
        --enable-soft-delete true `
        --soft-delete-retention-days 90 `
        --enable-purge-protection true `
        --public-network-access Enabled `
        --tags Project=AvertaSaaS Environment=$Environment ManagedBy=Script
    Write-Success "Key Vault created"

    # Wait for Key Vault to be ready
    Write-Info "Waiting for Key Vault to be ready..."
    Start-Sleep -Seconds 30
} else {
    Write-Info "Key Vault $KeyVaultName already exists"
}

# Enable RBAC authorization
Write-Info "Ensuring RBAC authorization is enabled..."
az keyvault update --name $KeyVaultName --enable-rbac-authorization true

# Get current user object ID for role assignment
$currentUserId = az ad signed-in-user show --query "id" -o tsv
Write-Info "Current user: $currentUserId"

# Assign Key Vault Secrets Officer role to current user
Write-Info "Assigning Key Vault Secrets Officer role..."
az role assignment create `
    --role "Key Vault Secrets Officer" `
    --assignee $currentUserId `
    --scope "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.KeyVault/vaults/$KeyVaultName" `
    --output none 2>$null || Write-Warning "Role assignment may already exist"

# Wait for role assignment to propagate
Write-Info "Waiting for role assignment to propagate..."
Start-Sleep -Seconds 60

# Prompt for secrets if not provided
function Get-SecretInput {
    param(
        [string]$Name,
        [string]$Description,
        [bool]$GenerateIfEmpty = $false,
        [int]$Length = 32
    )

    $value = (Get-Variable -Name $Name -ValueOnly -ErrorAction SilentlyContinue)
    if (-not $value) {
        if ($GenerateIfEmpty) {
            $value = [System.Convert]::ToBase64String((1..$Length | ForEach-Object { Get-Random -Maximum 256 }))
            Write-Info "Generated $Name: $value"
        } else {
            $value = Read-Host "Enter $Name ($Description)"
            if (-not $value) {
                Write-Error "$Name is required"
                exit 1
            }
        }
    }
    Set-Variable -Name $Name -Value $value -Scope Script
}

# Get all required secrets
Get-SecretInput -Name "PgAdminPassword" -Description "PostgreSQL admin password" -GenerateIfEmpty $true -Length 32
Get-SecretInput -Name "RedisAccessKey" -Description "Redis access key" -GenerateIfEmpty $true -Length 32
Get-SecretInput -Name "JwtSecretKey" -Description "JWT secret key (min 32 chars)" -GenerateIfEmpty $true -Length 64
Get-SecretInput -Name "JwtRefreshSecretKey" -Description "JWT refresh secret key (min 32 chars)" -GenerateIfEmpty $true -Length 64

# Optional secrets
if (-not $SendgridApiKey) {
    $SendgridApiKey = Read-Host "Enter SendGrid API Key (optional, press Enter to skip)"
}
if (-not $SmtpPassword) {
    $SmtpPassword = Read-Host "Enter SMTP Password (optional, press Enter to skip)"
}

# Store secrets in Key Vault
Write-Info "Storing secrets in Key Vault..."

$secrets = @{
    "pg-admin-password" = $PgAdminPassword
    "redis-access-key" = $RedisAccessKey
    "jwt-secret-key" = $JwtSecretKey
    "jwt-refresh-secret-key" = $JwtRefreshSecretKey
}

if ($SendgridApiKey) {
    $secrets["sendgrid-api-key"] = $SendgridApiKey
}
if ($SmtpPassword) {
    $secrets["smtp-password"] = $SmtpPassword
}

foreach ($secret in $secrets.GetEnumerator()) {
    Write-Info "Setting secret: $($secret.Key)"
    az keyvault secret set `
        --vault-name $KeyVaultName `
        --name $secret.Key `
        --value $secret.Value `
        --output none
    Write-Success "Secret '$($secret.Key)' stored"
}

# Store complex secrets (JSON)
Write-Info "Storing complex secrets..."

# Database secret
$dbSecret = @{
    username = "avertaadmin"
    password = $PgAdminPassword
    host = "averta-postgres-$Environment.postgres.database.azure.com"
    port = 5432
    dbname = "averta"
} | ConvertTo-Json -Compress

az keyvault secret set --vault-name $KeyVaultName --name "database" --value $dbSecret --output none
Write-Success "Database secret stored"

# Redis secret
$redisSecret = @{
    host = "averta-redis-$Environment.redis.cache.windows.net"
    port = 6380
    password = $RedisAccessKey
    ssl = $true
} | ConvertTo-Json -Compress

az keyvault secret set --vault-name $KeyVaultName --name "redis" --value $redisSecret --output none
Write-Success "Redis secret stored"

# Storage secret (will be updated after storage account creation)
$storageSecret = @{
    account_name = "avertastorage$Environment"
    account_key = "" # Will be updated after storage account creation
    endpoint = "https://avertastorage$Environment.blob.core.windows.net"
    container = "averta-documents"
    region = $Location
} | ConvertTo-Json -Compress

az keyvault secret set --vault-name $KeyVaultName --name "storage" --value $storageSecret --output none
Write-Success "Storage secret stored (placeholder)"

# JWT secret
$jwtSecret = @{
    secret_key = $JwtSecretKey
    refresh_secret_key = $JwtRefreshSecretKey
    algorithm = "HS256"
    access_token_expire_minutes = 15
    refresh_token_expire_days = 7
} | ConvertTo-Json -Compress

az keyvault secret set --vault-name $KeyVaultName --name "jwt" --value $jwtSecret --output none
Write-Success "JWT secret stored"

# App secret
$appSecret = @{
    environment = $Environment
    log_level = if ($Environment -eq "production") { "INFO" } else { "DEBUG" }
    cors_origins = @("https://$Environment.averta.com.br")
    frontend_url = "https://$Environment.averta.com.br"
    success_fee_percentage = 20.0
} | ConvertTo-Json -Compress

az keyvault secret set --vault-name $KeyVaultName --name "app" --value $appSecret --output none
Write-Success "App secret stored"

# SendGrid secret
if ($SendgridApiKey) {
    $sgSecret = @{
        api_key = $SendgridApiKey
        from_email = "noreply@averta.com.br"
        from_name = "Averta Auditoria"
    } | ConvertTo-Json -Compress

    az keyvault secret set --vault-name $KeyVaultName --name "sendgrid" --value $sgSecret --output none
    Write-Success "SendGrid secret stored"
}

# SMTP secret
if ($SmtpPassword) {
    $smtpSecret = @{
        host = "smtp.sendgrid.net"
        port = 587
        user = "apikey"
        password = $SmtpPassword
        from = "noreply@averta.com.br"
        tls = $true
    } | ConvertTo-Json -Compress

    az keyvault secret set --vault-name $KeyVaultName --name "smtp" --value $smtpSecret --output none
    Write-Success "SMTP secret stored"
}

# Output Key Vault info
Write-Success ""
Write-Success "Key Vault setup completed!"
Write-Success "Key Vault Name: $KeyVaultName"
Write-Success "Key Vault URI: https://$KeyVaultName.vault.azure.net"
Write-Success ""
Write-Info "Secrets stored:"
foreach ($secret in $secrets.GetEnumerator()) {
    Write-Info "  - $($secret.Key)"
}
Write-Info "  - database (JSON)"
Write-Info "  - redis (JSON)"
Write-Info "  - storage (JSON, placeholder)"
Write-Info "  - jwt (JSON)"
Write-Info "  - app (JSON)"
if ($SendgridApiKey) { Write-Info "  - sendgrid (JSON)" }
if ($SmtpPassword) { Write-Info "  - smtp (JSON)" }

Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Update storage secret with actual storage account key after infrastructure deployment"
Write-Info "2. Assign Key Vault Secrets User role to Container Apps managed identity"
Write-Info "3. Configure GitHub Actions OIDC for Key Vault access"