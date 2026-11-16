/**
 * AvertaSaaS - Container Apps Environment Module
 *
 * Creates Azure Container Apps Environment for running containerized applications.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('VNet Resource ID')
param vnetResourceId string

@description('Container Apps Subnet ID')
param subnetId string

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

@description('Log Analytics Workspace Key')
param logAnalyticsWorkspaceKey string

@description('Tags')
param tags object

@description('Internal load balancer (for private environments)')
param internalLoadBalancer bool = false

@description('Custom domain configuration')
param customDomainConfiguration object = {}

var envName = '${appName}-cae-${environment}'

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: envName
  location: location
  tags: tags
  properties: {
    daprAIConnectionString: ''
    vnetConfiguration: {
      infrastructureSubnetId: subnetId
      internal: internalLoadBalancer
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspaceId
        sharedKey: logAnalyticsWorkspaceKey
      }
    }
    customDomainConfiguration: customDomainConfiguration
    workloadProfiles: [
      {
        name: 'general-purpose'
        workloadProfileType: 'GeneralPurpose'
        minimumNodes: environment == 'production' ? 2 : 0
        maximumNodes: environment == 'production' ? 10 : 5
      }
      {
        name: 'memory-optimized'
        workloadProfileType: 'MemoryOptimized'
        minimumNodes: 0
        maximumNodes: environment == 'production' ? 5 : 2
      }
      {
        name: 'compute-optimized'
        workloadProfileType: 'ComputeOptimized'
        minimumNodes: 0
        maximumNodes: environment == 'production' ? 3 : 1
      }
    ]
    zoneRedundant: environment == 'production'
    dapr: {
      enabled: false
    }
    peerAuthentication: {
      mtls: {
        enabled: true
      }
    }
  }
}

// User-assigned managed identity for Container Apps
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-ca-mi-${environment}'
  location: location
  tags: tags
}

// Role assignment for Key Vault access
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(managedIdentity.id, 'KeyVaultSecretsUser')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role assignment for Storage access
resource storageBlobDataContributorRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(managedIdentity.id, 'StorageBlobDataContributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role assignment for Container Registry access
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(managedIdentity.id, 'AcrPull')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role assignment for Log Analytics
resource logAnalyticsContributorRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(managedIdentity.id, 'LogAnalyticsContributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '92aaf0da-9dab-42b6-94a3-d43ce8d16293')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Custom domain certificate (if provided)
resource customDomainCertificate 'Microsoft.App/managedEnvironments/customDomainCertificates@2023-05-01' = if (!empty(customDomainConfiguration)) {
  parent: containerAppsEnv
  name: 'custom-domain-cert'
  properties: {
    certificatePassword: '' // Set from Key Vault
    certificateValue: '' // Set from Key Vault
  }
}

output containerAppsEnvId string = containerAppsEnv.id
output containerAppsEnvName string = containerAppsEnv.name
output containerAppsEnvResourceId string = containerAppsEnv.id
output managedIdentityId string = managedIdentity.id
output managedIdentityClientId string = managedIdentity.properties.clientId
output managedIdentityPrincipalId string = managedIdentity.properties.principalId