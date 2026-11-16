/**
 * AvertaSaaS - Storage Account Module
 *
 * Creates Azure Storage Account with Blob containers for document storage.
 * Uses Azure Blob Storage as replacement for MinIO/S3.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('SKU name: Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS, Premium_LRS, Premium_ZRS')
param skuName string = 'Standard_ZRS'

@description('Access tier: Hot, Cool, Cold')
param accessTier string = 'Hot'

@description('Allow blob public access')
param allowBlobPublicAccess bool = false

@description('Minimum TLS version')
param minimumTlsVersion string = 'TLS1_2'

@description('Allow shared key access (disable for managed identity only)')
param allowSharedKeyAccess bool = false

@description('Network ACLs')
param networkAcls object = {
  defaultAction: 'Deny'
  bypass: 'AzureServices'
  virtualNetworkRules: []
  ipRules: []
}

@description('Tags')
param tags object

var storageAccountName = '${uniqueString(resourceGroup().id, appName, environment)}${replace(environment, "staging", "stg")}stg'
var containerName = 'averta-documents'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  kind: 'StorageV2'
  properties: {
    accessTier: accessTier
    allowBlobPublicAccess: allowBlobPublicAccess
    minimumTlsVersion: minimumTlsVersion
    allowSharedKeyAccess: allowSharedKeyAccess
    networkAcls: networkAcls
    supportsHttpsTrafficOnly: true
    largeFileSharesState: 'Enabled'
    isHnsEnabled: false // Set to true if using Data Lake Gen2
    encryption: {
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
      }
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: false
    }
    blobRestoreStatus: environment == 'production' ? 'Enabled' : 'Disabled'
    versioning: {
      enabled: true
    }
    changeFeed: {
      enabled: environment == 'production'
    }
  }
}

// Blob container for documents
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccount
  name: 'default/${containerName}'
  properties: {
    publicAccess: 'None'
    metadata: {
      environment: environment
      application: 'averta'
    }
  }
}

// Blob container for backups
resource backupContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccount
  name: 'default/averta-backups'
  properties: {
    publicAccess: 'None'
    metadata: {
      environment: environment
      application: 'averta'
      purpose: 'backups'
    }
  }
}

// Blob container for logs
resource logsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccount
  name: 'default/averta-logs'
  properties: {
    publicAccess: 'None'
    metadata: {
      environment: environment
      application: 'averta'
      purpose: 'logs'
    }
  }
}

// Lifecycle management for cost optimization
resource lifecycleManagement 'Microsoft.Storage/storageAccounts/managementPolicies@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          name: 'MoveToCoolAfter30Days'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 30
                }
                tierToCold: {
                  daysAfterModificationGreaterThan: 90
                }
                delete: {
                  daysAfterModificationGreaterThan: 365
                }
              }
              snapshot: {
                delete: {
                  daysAfterCreationGreaterThan: 90
                }
              }
            }
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                '${containerName}/'
              ]
            }
          }
        }
        {
          name: 'BackupRetention'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              baseBlob: {
                delete: {
                  daysAfterModificationGreaterThan: environment == 'production' ? 365 : 30
                }
              }
              snapshot: {
                delete: {
                  daysAfterCreationGreaterThan: environment == 'production' ? 365 : 30
                }
              }
            }
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                'averta-backups/'
              ]
            }
          }
        }
        {
          name: 'LogRetention'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              baseBlob: {
                delete: {
                  daysAfterModificationGreaterThan: 90
                }
              }
            }
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                'averta-logs/'
              ]
            }
          }
        }
      ]
    }
  }
}

// Diagnostic settings
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${storageAccountName}-diagnostics'
  scope: storageAccount
  properties: {
    workspaceId: '' // Set from Log Analytics module
    logs: [
      {
        category: 'StorageRead'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
      {
        category: 'StorageWrite'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
      {
        category: 'StorageDelete'
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
  name: '${storageAccountName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '' // Set from VNet module
    }
    privateLinkServiceConnections: [
      {
        name: '${storageAccountName}-pls-blob'
        properties: {
          privateLinkServiceId: storageAccount.id
          groupIds: [
            'blob'
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
        name: 'blob-config'
        properties: {
          privateDnsZoneId: '' // Set from VNet module
        }
      }
    ]
  }
}

// Access keys
resource listKeys 'Microsoft.Storage/storageAccounts/listKeys@2023-01-01' = {
  parent: storageAccount
  name: 'listKeys'
}

// Storage connection string
var connectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${listKeys.properties.keys[0].value};EndpointSuffix=core.windows.net'

output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
output primaryKey string = listKeys.properties.keys[0].value
output secondaryKey string = listKeys.properties.keys[1].value
output connectionString string = connectionString
output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob
output containerName string = containerName