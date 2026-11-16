/**
 * AvertaSaaS - Production Environment Deployment
 *
 * Deploys production infrastructure with high availability and security.
 *
 * Usage:
 *   az deployment sub create --location eastus --template-file ../main.bicep --parameters @production/main.parameters.json
 */

targetScope = 'subscription'

@description('Resource group name')
param resourceGroupName string = 'rg-averta-production'

@description('Resource group location')
param resourceGroupLocation string = 'eastus'

@description('Tags')
param tags object = {
  Project: 'AvertaSaaS'
  Environment: 'production'
  ManagedBy: 'Bicep'
  Owner: 'Platform Team'
  CostCenter: 'Engineering'
  Compliance: 'PCI-DSS'
  DataClassification: 'Confidential'
}

// Create resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-09-01' = {
  name: resourceGroupName
  location: resourceGroupLocation
  tags: tags
}

// Deploy main infrastructure into the resource group
module mainInfra '../main.bicep' = {
  name: 'production-infra-deployment'
  scope: resourceGroup
  params: {
    environment: 'production'
    appName: 'averta'
    location: resourceGroupLocation
    tags: tags
    // Production-specific parameters
    customDomain: 'averta.com.br'
    enableWaf: true
    pgAdminLogin: 'avertaadmin'
    pgAdminPassword: '' // Will be provided via parameter file or key vault
    redisAccessKey: '' // Will be provided via parameter file
    jwtSecretKey: '' // Will be provided via parameter file
    jwtRefreshSecretKey: '' // Will be provided via parameter file
    sendgridApiKey: '' // Will be provided via parameter file
    smtpPassword: '' // Will be provided via parameter file
    frontendUrl: 'https://app.averta.com.br'
  }
}