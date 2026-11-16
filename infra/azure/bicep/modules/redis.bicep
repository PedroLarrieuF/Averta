/**
 * AvertaSaaS - Azure Cache for Redis Module
 *
 * Creates Azure Cache for Redis with clustering and high availability.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('VNet Resource ID')
param vnetResourceId string

@description('Redis Subnet ID')
param subnetId string

@description('SKU: Basic, Standard, Premium, Enterprise, EnterpriseFlash')
param sku string = 'Standard'

@description('Capacity (depends on SKU)')
param capacity int = 1

@description('Family: C (Basic/Standard), P (Premium), E (Enterprise)')
param family string = 'C'

@description('Enable non-SSL port (6379)')
param enableNonSslPort bool = false

@description('Minimum TLS version')
param minimumTlsVersion string = '1.2'

@description('Redis configuration')
param redisConfiguration object = {
  'maxmemory-policy': 'allkeys-lru'
  'maxmemory-reserved': '100'
}

@description('Tags')
param tags object

@description('Enable clustering (Premium only)')
param enableClustering bool = false

@description('Cluster shard count (Premium only)')
param shardCount int = 1

var redisName = '${appName}-redis-${environment}'

resource redisCache 'Microsoft.Cache/redis@2023-07-01' = {
  name: redisName
  location: location
  tags: tags
  sku: {
    name: sku
    family: family
    capacity: capacity
  }
  properties: {
    enableNonSslPort: enableNonSslPort
    minimumTlsVersion: minimumTlsVersion
    redisConfiguration: redisConfiguration
    shardCount: enableClustering ? shardCount : 1
    redisVersion: '7'
    sku: {
      name: sku
      family: family
      capacity: capacity
    }
    subnetId: subnetId
    staticIP: ''
    zones: environment == 'production' ? ['1', '2', '3'] : []
    publicNetworkAccess: 'Disabled'
    enableAuth: true
    auth: {
      enableAuth: true
    }
  }
}

// Diagnostic settings
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${redisName}-diagnostics'
  scope: redisCache
  properties: {
    workspaceId: '' // Set from Log Analytics module
    logs: [
      {
        category: 'AllLogs'
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
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: '${redisName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${redisName}-pls'
        properties: {
          privateLinkServiceId: redisCache.id
          groupIds: [
            'redisCache'
          ]
          requestMessage: 'Auto-approved'
        }
      }
    ]
  }
}

// Access keys (output)
resource listKeys 'Microsoft.Cache/redis/listKeys@2023-07-01' = {
  parent: redisCache
  name: 'listKeys'
}

output resourceId string = redisCache.id
output hostName string = redisCache.properties.hostName
output port int = redisCache.properties.port
output sslPort int = redisCache.properties.sslPort
output primaryKey string = listKeys.properties.primaryKey
output secondaryKey string = listKeys.properties.secondaryKey
output connectionString string = 'rediss://:${listKeys.properties.primaryKey}@${redisCache.properties.hostName}:${redisCache.properties.sslPort}/0'