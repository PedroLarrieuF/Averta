/**
 * AvertaSaaS - Staging Environment Deployment
 *
 * Deploys staging infrastructure with cost-optimized settings.
 *
 * Usage:
 *   az deployment sub create --location eastus --template-file ../main.bicep --parameters @staging/main.parameters.json
 */

targetScope = 'subscription'

@description('Resource group name')
param resourceGroupName string = 'rg-averta-staging'

@description('Resource group location')
param resourceGroupLocation string = 'eastus'

@description('Tags')
param tags object = {
  Project: 'AvertaSaaS'
  Environment: 'staging'
  ManagedBy: 'Bicep'
  Owner: 'Platform Team'
  CostCenter: 'Engineering'
}

// Create resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-09-01' = {
  name: resourceGroupName
  location: resourceGroupLocation
  tags: tags
}

// Deploy main infrastructure into the resource group
module mainInfra '../main.bicep' = {
  name: 'staging-infra-deployment'
  scope: resourceGroup
  params: {
    environment: 'staging'
    appName: 'averta'
    location: resourceGroupLocation
    tags: tags
    // Staging-specific parameters
    customDomain: ''
    enableWaf: false
    pgAdminLogin: 'avertaadmin'
    pgAdminPassword: '' // Will be provided via parameter file or key vault
    redisAccessKey: '' // Will be provided via parameter file
    jwtSecretKey: '' // Will be provided via parameter file
    jwtRefreshSecretKey: '' // Will be provided via parameter file
    sendgridApiKey: ''
    smtpPassword: ''
    frontendUrl: 'https://staging.averta.com.br'
  }
}