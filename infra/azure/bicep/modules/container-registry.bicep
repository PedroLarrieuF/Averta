/**
 * AvertaSaaS - Container Registry Module
 *
 * Creates Azure Container Registry for Docker images.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('SKU: Basic, Standard, Premium')
param sku string = 'Standard'

@description('Enable admin user')
param adminUserEnabled bool = false

@description('Public network access: Enabled, Disabled')
param publicNetworkAccess string = 'Disabled'

@description('VNet Resource ID')
param vnetResourceId string

@description('ACR Subnet ID')
param subnetId string

@description('Tags')
param tags object

var registryName = '${uniqueString(resourceGroup().id, appName, environment)}acr'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    publicNetworkAccess: publicNetworkAccess
    networkRuleSet: publicNetworkAccess == 'Disabled' ? {
      defaultAction: 'Deny'
      virtualNetworkRules: [
        {
          action: 'Allow'
          id: subnetId
        }
      ]
      ipRules: []
    } : {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    policies: {
      quarantinePolicy: {
        status: 'enabled'
      }
      trustPolicy: {
        type: 'Notary',
        status: environment == 'production' ? 'enabled' : 'disabled'
      }
      retentionPolicy: {
        days: environment == 'production' ? 90 : 30
        status: 'enabled'
      }
      softDeletePolicy: {
        days: 90
        status: 'enabled'
      }
    }
    encryption: {
      status: 'Enabled'
      keyType: 'System'
    }
    dataEndpointEnabled: true
    zoneRedundancy: environment == 'production' ? 'Enabled' : 'Disabled'
  }
}

// Diagnostic settings
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${registryName}-diagnostics'
  scope: containerRegistry
  properties: {
    workspaceId: '' // Set from Log Analytics module
    logs: [
      {
        category: 'ContainerRegistryLoginEvents'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
      {
        category: 'ContainerRegistryRepositoryEvents'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
    ]
  }
}

// Private Endpoint
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = if (environment == 'production') {
  name: '${registryName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${registryName}-pls'
        properties: {
          privateLinkServiceId: containerRegistry.id
          groupIds: [
            'registry'
          ]
          requestMessage: 'Auto-approved'
        }
      }
    ]
  }
}

// Private DNS Zone Group
resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-09-01' = if (environment == 'production') {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'acr-config'
        properties: {
          privateDnsZoneId: '' // Set from VNet module
        }
      }
    ]
  }
}

// Webhook for CI/CD integration
resource webhook 'Microsoft.ContainerRegistry/registries/webhooks@2023-07-01' = {
  parent: containerRegistry
  name: '${registryName}-github-webhook'
  properties: {
    actions: [
      'push'
      'delete'
    ]
    status: 'enabled'
    scope: '${registryName}/averta-backend'
    serviceUri: '' // Set from GitHub Actions configuration
  }
}

// Scope map for fine-grained access
resource scopeMap 'Microsoft.ContainerRegistry/registries/scopeMaps@2023-07-01' = {
  parent: containerRegistry
  name: 'averta-scope-map'
  properties: {
    description: 'Scope map for AvertaSaaS applications'
    actions: [
      'repositories/averta-backend/content/read',
      'repositories/averta-backend/content/write',
      'repositories/averta-backend/content/delete',
      'repositories/averta-frontend/content/read',
      'repositories/averta-frontend/content/write',
      'repositories/averta-frontend/content/delete'
    ]
  }
}

// Token for GitHub Actions
resource token 'Microsoft.ContainerRegistry/registries/tokens@2023-07-01' = {
  parent: containerRegistry
  name: 'github-actions-token'
  properties: {
    scopeMapId: scopeMap.id
    status: 'enabled'
    credentials: {
      passwords: [
        {
          name: 'password1'
          expiry: timeAdd('P1Y')
        }
        {
          name: 'password2'
          expiry: timeAdd('P2Y')
        }
      ]
    }
  }
}

output loginServer string = containerRegistry.properties.loginServer
output registryName string = containerRegistry.name
output registryId string = containerRegistry.id
output resourceGroup string = resourceGroup().name