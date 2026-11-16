/**
 * AvertaSaaS - PostgreSQL Flexible Server Module
 *
 * Creates Azure Database for PostgreSQL Flexible Server with high availability options.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('VNet Resource ID')
param vnetResourceId string

@description('Database Subnet ID')
param subnetId string

@description('PostgreSQL administrator login')
@secure()
param adminLogin string

@description('PostgreSQL administrator password')
@secure()
param adminPassword string

@description('SKU name (e.g., Standard_D2s_v3, Standard_D8s_v3)')
param skuName string = 'Standard_D2s_v3'

@description('Storage size in GB')
param storageSizeGB int = 128

@description('High availability mode: Disabled, ZoneRedundant, SameZone')
param highAvailability string = 'Disabled'

@description('Backup retention days (7-35)')
param backupRetentionDays int = 7

@description('Enable geo-redundant backup')
param geoRedundantBackup bool = false

@description('PostgreSQL version')
param pgVersion string = '16'

@description('Tags')
param tags object

var serverName = '${appName}-postgres-${environment}'
var firewallRuleName = 'AllowAzureServices'

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: 'GeneralPurpose'
  }
  properties: {
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    version: pgVersion
    storage: {
      storageSizeGB: storageSizeGB
      storageAutoGrow: 'Enabled'
      storageIoTb: '1000'
      storageAutogrowLimit: storageSizeGB * 4
    }
    highAvailability: {
      mode: highAvailability
      standbyAvailabilityZone: highAvailability == 'ZoneRedundant' ? '1' : ''
    }
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: geoRedundantBackup ? 'Enabled' : 'Disabled'
      backupIntervalHours: 24
    }
    network: {
      delegatedSubnetResourceId: subnetId
      privateDnsZoneArmResourceId: '${vnetResourceId}/providers/Microsoft.Network/privateDnsZones/privatelink.postgres.database.azure.com'
      publicNetworkAccess: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 2
      startMinute: 0
    }
    createMode: 'Default'
    availabilityZone: highAvailability == 'ZoneRedundant' ? '1' : ''
  }
}

// Database
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: postgresServer
  name: 'averta'
  properties: {
    charset: 'utf8'
    collation: 'en_US.utf8'
  }
}

// Firewall rule for Azure services
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01-preview' = {
  parent: postgresServer
  name: firewallRuleName
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Server configuration (parameter group equivalent)
resource configLogMinDurationStatement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'log_min_duration_statement'
  properties: {
    value: '1000' // Log queries taking longer than 1 second
    source: 'user-override'
  }
}

resource configLogStatement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'log_statement'
  properties: {
    value: 'ddl'
    source: 'user-override'
  }
}

resource configSharedPreloadLibraries 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'shared_preload_libraries'
  properties: {
    value: 'pg_stat_statements,auto_explain'
    source: 'user-override'
  }
}

resource configWorkMem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'work_mem'
  properties: {
    value: '64MB'
    source: 'user-override'
  }
}

resource configMaintenanceWorkMem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'maintenance_work_mem'
  properties: {
    value: '512MB'
    source: 'user-override'
  }
}

resource configEffectiveCacheSize 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'effective_cache_size'
  properties: {
    value: '4GB'
    source: 'user-override'
  }
}

resource configRandomPageCost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'random_page_cost'
  properties: {
    value: '1.1'
    source: 'user-override'
  }
}

resource configMaxConnections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'max_connections'
  properties: {
    value: environment == 'production' ? '400' : '200'
    source: 'user-override'
  }
}

// PgBouncer is not natively supported in Azure Database for PostgreSQL Flexible Server
// You would typically deploy it as a separate Container App or use RDS Proxy equivalent
// For now, we'll document this in the outputs

// Diagnostic settings
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${serverName}-diagnostics'
  scope: postgresServer
  properties: {
    workspaceId: '' // Set from Log Analytics module
    logs: [
      {
        category: 'PostgreSQLLogs'
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
  name: '${serverName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${serverName}-pls'
        properties: {
          privateLinkServiceId: postgresServer.id
          groupIds: [
            'postgresqlServer'
          ]
          requestMessage: 'Auto-approved'
        }
      }
    ]
  }
}

output resourceId string = postgresServer.id
output fullyQualifiedDomainName string = postgresServer.properties.fullyQualifiedDomainName
output administratorLogin string = adminLogin
output databaseName string = 'averta'
output port int = 5432
output connectionString string = 'postgresql://${adminLogin}:${adminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/averta?sslmode=require'