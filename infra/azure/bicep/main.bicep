/**
 * AvertaSaaS - Azure Infrastructure Main Entry Point
 *
 * Deploys complete Azure infrastructure for AvertaSaaS production deployment.
 * Target architecture: Container Apps, PostgreSQL Flexible Server, Azure Cache for Redis,
 * Azure Blob Storage, Application Gateway, Azure DNS, Key Vault, Application Insights.
 *
 * Usage:
 *   az deployment sub create --location eastus --template-file main.bicep --parameters environment=production
 *   az deployment sub create --location eastus --template-file main.bicep --parameters environment=staging
 */

@description('Environment name: staging or production')
@allowed(['staging', 'production'])
param environment string = 'staging'

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Application name prefix')
param appName string = 'averta'

@description('Custom domain name (optional)')
param customDomain string = ''

@description('Enable Application Gateway WAF')
param enableWaf bool = true

@description('PostgreSQL administrator login')
@secure()
param pgAdminLogin string = 'avertaadmin'

@description('PostgreSQL administrator password')
@secure()
param pgAdminPassword string

@description('Redis access key (if not using managed identity)')
@secure()
param redisAccessKey string = ''

@description('JWT secret key')
@secure()
param jwtSecretKey string

@description('JWT refresh secret key')
@secure()
param jwtRefreshSecretKey string

@description('SendGrid API key (optional)')
@secure()
param sendgridApiKey string = ''

@description('SMTP password (optional)')
@secure()
param smtpPassword string = ''

@description('Frontend URL for CORS')
param frontendUrl string = ''

@description('Tags to apply to all resources')
param tags object = {
  Project: 'AvertaSaaS'
  Environment: environment
  ManagedBy: 'Bicep'
  Owner: 'Platform Team'
}

// =============================================================================
// MODULE DEPLOYMENTS
// =============================================================================

// 1. Networking - Virtual Network and Subnets
module vnet 'modules/vnet.bicep' = {
  name: '${appName}-vnet-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    tags: tags
  }
}

// 2. Log Analytics Workspace (for monitoring)
module logAnalytics 'modules/log-analytics.bicep' = {
  name: '${appName}-log-analytics-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    tags: tags
  }
}

// 3. Application Insights
module appInsights 'modules/app-insights.bicep' = {
  name: '${appName}-app-insights-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
    tags: tags
  }
}

// 4. Key Vault
module keyVault 'modules/key-vault.bicep' = {
  name: '${appName}-key-vault-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    tags: tags
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: true
    enableRbacAuthorization: true
    softDeleteRetentionDays: 90
    purgeProtectionEnabled: true
  }
}

// 5. Key Vault Secrets
module keyVaultSecrets 'modules/key-vault-secrets.bicep' = {
  name: '${appName}-key-vault-secrets-${environment}'
  params: {
    environment: environment
    appName: appName
    keyVaultName: keyVault.outputs.keyVaultName
    pgAdminLogin: pgAdminLogin
    pgAdminPassword: pgAdminPassword
    redisAccessKey: redisAccessKey
    jwtSecretKey: jwtSecretKey
    jwtRefreshSecretKey: jwtRefreshSecretKey
    sendgridApiKey: sendgridApiKey
    smtpPassword: smtpPassword
    frontendUrl: frontendUrl
  }
  dependsOn: [
    keyVault
  ]
}

// 6. PostgreSQL Flexible Server
module postgres 'modules/postgresql.bicep' = {
  name: '${appName}-postgresql-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    vnetResourceId: vnet.outputs.vnetId
    subnetId: vnet.outputs.databaseSubnetId
    adminLogin: pgAdminLogin
    adminPassword: pgAdminPassword
    skuName: environment == 'production' ? 'Standard_D8s_v3' : 'Standard_D2s_v3'
    storageSizeGB: environment == 'production' ? 512 : 128
    highAvailability: environment == 'production' ? 'ZoneRedundant' : 'Disabled'
    backupRetentionDays: environment == 'production' ? 30 : 7
    geoRedundantBackup: environment == 'production'
    tags: tags
  }
  dependsOn: [
    vnet
  ]
}

// 7. Azure Cache for Redis
module redis 'modules/redis.bicep' = {
  name: '${appName}-redis-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    vnetResourceId: vnet.outputs.vnetId
    subnetId: vnet.outputs.redisSubnetId
    sku: environment == 'production' ? 'Premium' : 'Standard'
    capacity: environment == 'production' ? 2 : 1
    family: 'C'
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
      'maxmemory-reserved': '100'
    }
    tags: tags
  }
  dependsOn: [
    vnet
  ]
}

// 8. Storage Account (Blob Storage)
module storage 'modules/storage.bicep' = {
  name: '${appName}-storage-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    skuName: environment == 'production' ? 'Standard_ZRS' : 'Standard_LRS'
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    allowSharedKeyAccess: false
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
      virtualNetworkRules: [
        {
          id: vnet.outputs.storageSubnetId
          action: 'Allow'
        }
      ]
    }
    tags: tags
  }
  dependsOn: [
    vnet
  ]
}

// 9. Container Registry
module containerRegistry 'modules/container-registry.bicep' = {
  name: '${appName}-acr-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    sku: environment == 'production' ? 'Premium' : 'Standard'
    adminUserEnabled: false
    publicNetworkAccess: 'Disabled'
    vnetResourceId: vnet.outputs.vnetId
    subnetId: vnet.outputs.acrSubnetId
    tags: tags
  }
  dependsOn: [
    vnet
  ]
}

// 10. Container Apps Environment
module containerAppsEnv 'modules/container-apps-env.bicep' = {
  name: '${appName}-cae-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    vnetResourceId: vnet.outputs.vnetId
    subnetId: vnet.outputs.containerAppsSubnetId
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
    logAnalyticsWorkspaceKey: logAnalytics.outputs.workspaceKey
    tags: tags
  }
  dependsOn: [
    vnet
    logAnalytics
  ]
}

// 11. Container Apps (Backend, Celery Worker, Celery Beat)
module containerApps 'modules/container-apps.bicep' = {
  name: '${appName}-container-apps-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    containerAppsEnvId: containerAppsEnv.outputs.containerAppsEnvId
    containerRegistry: containerRegistry.outputs
    postgresFqdn: postgres.outputs.fullyQualifiedDomainName
    postgresAdminLogin: pgAdminLogin
    postgresAdminPassword: pgAdminPassword
    redisHost: redis.outputs.hostName
    redisPort: redis.outputs.port
    redisAccessKey: redis.outputs.primaryKey
    storageAccountName: storage.outputs.storageAccountName
    storageAccountKey: storage.outputs.primaryKey
    appInsightsConnectionString: appInsights.outputs.connectionString
    keyVaultName: keyVault.outputs.keyVaultName
    frontendUrl: frontendUrl
    customDomain: customDomain
    tags: tags
  }
  dependsOn: [
    containerAppsEnv
    containerRegistry
    postgres
    redis
    storage
    appInsights
    keyVault
    keyVaultSecrets
  ]
}

// 12. Application Gateway
module appGateway 'modules/application-gateway.bicep' = {
  name: '${appName}-app-gateway-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    vnetResourceId: vnet.outputs.vnetId
    subnetId: vnet.outputs.appGatewaySubnetId
    containerAppsEnvId: containerAppsEnv.outputs.containerAppsEnvId
    backendAppFqdn: containerApps.outputs.backendFqdn
    enableWaf: enableWaf
    customDomain: customDomain
    tags: tags
  }
  dependsOn: [
    vnet
    containerAppsEnv
    containerApps
  ]
}

// 13. DNS Zone and Records
module dnsZone 'modules/dns-zone.bicep' = {
  name: '${appName}-dns-zone-${environment}'
  params: {
    environment: environment
    appName: appName
    customDomain: customDomain
    appGatewayPublicIp: appGateway.outputs.publicIpAddress
    tags: tags
  }
  dependsOn: [
    appGateway
  ]
}

// 14. Monitoring (Alerts, Dashboards)
module monitoring 'modules/monitoring.bicep' = {
  name: '${appName}-monitoring-${environment}'
  params: {
    environment: environment
    appName: appName
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
    appInsightsName: appInsights.outputs.name
    postgresResourceId: postgres.outputs.resourceId
    redisResourceId: redis.outputs.resourceId
    storageResourceId: storage.outputs.resourceId
    containerAppsEnvResourceId: containerAppsEnv.outputs.containerAppsEnvResourceId
    appGatewayResourceId: appGateway.outputs.resourceId
    tags: tags
  }
  dependsOn: [
    logAnalytics
    appInsights
    postgres
    redis
    storage
    containerAppsEnv
    appGateway
  ]
}

// =============================================================================
// OUTPUTS
// =============================================================================

output resourceGroupName string = resourceGroup().name
output location string = location
output environment string = environment

output vnetId string = vnet.outputs.vnetId
output logAnalyticsWorkspaceId string = logAnalytics.outputs.workspaceId
output appInsightsConnectionString string = appInsights.outputs.connectionString
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultUri string = keyVault.outputs.keyVaultUri
output postgresFqdn string = postgres.outputs.fullyQualifiedDomainName
output redisHost string = redis.outputs.hostName
output storageAccountName string = storage.outputs.storageAccountName
output containerAppsEnvId string = containerAppsEnv.outputs.containerAppsEnvId
output containerRegistryLoginServer string = containerRegistry.outputs.loginServer
output appGatewayPublicIp string = appGateway.outputs.publicIpAddress
output backendAppUrl string = containerApps.outputs.backendAppUrl