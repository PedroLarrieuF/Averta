/**
 * AvertaSaaS - Key Vault Module
 *
 * Creates Azure Key Vault for secrets management with RBAC authorization.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Tags')
param tags object

@description('Enable for deployment')
param enabledForDeployment bool = true

@description('Enable for template deployment')
param enabledForTemplateDeployment bool = true

@description('Enable for disk encryption')
param enabledForDiskEncryption bool = true

@description('Enable RBAC authorization (recommended)')
param enableRbacAuthorization bool = true

@description('Soft delete retention days (7-90)')
param softDeleteRetentionDays int = 90

@description('Enable purge protection')
param purgeProtectionEnabled bool = true

@description('SKU name')
param skuName string = 'standard'

@description('Network ACLs')
param networkAcls object = {
  defaultAction: 'Allow'
  bypass: 'AzureServices'
  virtualNetworkRules: []
  ipRules: []
}

var keyVaultName = '${uniqueString(resourceGroup().id, appName, environment)}-kv'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: skuName
    }
    enabledForDeployment: enabledForDeployment
    enabledForTemplateDeployment: enabledForTemplateDeployment
    enabledForDiskEncryption: enabledForDiskEncryption
    enableRbacAuthorization: enableRbacAuthorization
    enableSoftDelete: true
    softDeleteRetentionInDays: softDeleteRetentionDays
    enablePurgeProtection: purgeProtectionEnabled
    networkAcls: networkAcls
    publicNetworkAccess: environment == 'production' ? 'Disabled' : 'Enabled'
  }
}

// Role assignments for Key Vault (RBAC)
// These would typically be assigned to managed identities or service principals
// Example: Key Vault Secrets User role for Container Apps managed identity
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(keyVault.id, 'KeyVaultSecretsUser', 'container-apps-mi')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: '' // Will be set after Container Apps Environment is created
    principalType: 'ServicePrincipal'
  }
}

resource keyVaultSecretsOfficerRole 'Microsoft.Authorization/roleAssignments@2023-04-01' = {
  name: guid(keyVault.id, 'KeyVaultSecretsOfficer', 'github-actions')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7') // Key Vault Secrets Officer
    principalId: '' // Will be set for GitHub Actions OIDC
    principalType: 'ServicePrincipal'
  }
}

// Private Endpoint for Key Vault (if VNet is provided)
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = if (environment == 'production') {
  name: '${keyVaultName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '' // Will be set from VNet module
    }
    privateLinkServiceConnections: [
      {
        name: '${keyVaultName}-pls'
        properties: {
          privateLinkServiceId: keyVault.id
          groupIds: [
            'vault'
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
        name: 'keyvault-config'
        properties: {
          privateDnsZoneId: '' // Will be set from VNet module
        }
      }
    ]
  }
}

// Diagnostic settings for Key Vault
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${keyVaultName}-diagnostics'
  scope: keyVault
  properties: {
    workspaceId: '' // Will be set from Log Analytics module
    logs: [
      {
        category: 'AuditEvent'
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

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultId string = keyVault.id