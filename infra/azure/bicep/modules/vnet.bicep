/**
 * AvertaSaaS - Virtual Network Module
 *
 * Creates VNet with subnets for:
 * - Application Gateway (public)
 * - Container Apps (private)
 * - PostgreSQL Flexible Server (private)
 * - Azure Cache for Redis (private)
 * - Storage Account (private)
 * - Container Registry (private)
 * - Bastion (optional, for management)
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Tags')
param tags object

@description('VNet address space')
param vnetAddressSpace string = '10.0.0.0/16'

@description('Application Gateway subnet prefix')
param appGatewaySubnetPrefix string = '10.0.0.0/24'

@description('Container Apps subnet prefix')
param containerAppsSubnetPrefix string = '10.0.1.0/24'

@description('Database subnet prefix (PostgreSQL)')
param databaseSubnetPrefix string = '10.0.2.0/24'

@description('Redis subnet prefix')
param redisSubnetPrefix string = '10.0.3.0/24'

@description('Storage subnet prefix')
param storageSubnetPrefix string = '10.0.4.0/24'

@description('Container Registry subnet prefix')
param acrSubnetPrefix string = '10.0.5.0/24'

@description('Bastion subnet prefix (optional)')
param bastionSubnetPrefix string = '10.0.254.0/24'

var vnetName = '${appName}-vnet-${environment}'
var appGatewaySubnetName = 'app-gateway-subnet'
var containerAppsSubnetName = 'container-apps-subnet'
var databaseSubnetName = 'database-subnet'
var redisSubnetName = 'redis-subnet'
var storageSubnetName = 'storage-subnet'
var acrSubnetName = 'acr-subnet'
var bastionSubnetName = 'bastion-subnet'

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressSpace
      ]
    }
    subnets: [
      {
        name: appGatewaySubnetName
        properties: {
          addressPrefix: appGatewaySubnetPrefix
          serviceEndpoints: []
          delegations: [
            {
              name: 'app-gateway-delegation'
              properties: {
                serviceName: 'Microsoft.Network/applicationGateways'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: containerAppsSubnetName
        properties: {
          addressPrefix: containerAppsSubnetPrefix
          serviceEndpoints: [
            {
              service: 'Microsoft.Storage'
            }
            {
              service: 'Microsoft.Sql'
            }
            {
              service: 'Microsoft.KeyVault'
            }
          ]
          delegations: [
            {
              name: 'container-apps-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: databaseSubnetName
        properties: {
          addressPrefix: databaseSubnetPrefix
          serviceEndpoints: [
            {
              service: 'Microsoft.Sql'
            }
            {
              service: 'Microsoft.Storage'
            }
          ]
          delegations: [
            {
              name: 'postgresql-delegation'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: redisSubnetName
        properties: {
          addressPrefix: redisSubnetPrefix
          serviceEndpoints: [
            {
              service: 'Microsoft.Cache'
            }
          ]
          delegations: [
            {
              name: 'redis-delegation'
              properties: {
                serviceName: 'Microsoft.Cache/redis'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: storageSubnetName
        properties: {
          addressPrefix: storageSubnetPrefix
          serviceEndpoints: [
            {
              service: 'Microsoft.Storage'
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: acrSubnetName
        properties: {
          addressPrefix: acrSubnetPrefix
          serviceEndpoints: [
            {
              service: 'Microsoft.ContainerRegistry'
            }
          ]
          delegations: [
            {
              name: 'acr-delegation'
              properties: {
                serviceName: 'Microsoft.ContainerRegistry/registries'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: bastionSubnetName
        properties: {
          addressPrefix: bastionSubnetPrefix
          serviceEndpoints: []
          delegations: []
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
    enableDdosProtection: environment == 'production'
    ddosProtectionPlan: environment == 'production' ? {
      id: '${vnetName}-ddos-plan'
    } : null
  }
}

// DDoS Protection Plan (Production only)
resource ddosPlan 'Microsoft.Network/ddosProtectionPlans@2023-09-01' = if (environment == 'production') {
  name: '${vnetName}-ddos-plan'
  location: location
  tags: tags
  properties: {}
  sku: 'Standard'
}

// Network Security Groups
resource appGatewayNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-app-gateway-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHTTP'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '80'
        }
      }
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 110
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowAppGatewayHealthProbe'
        properties: {
          priority: 120
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'GatewayManager'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '65503-65534'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource containerAppsNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-container-apps-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowAppGateway'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: appGatewaySubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '8000'
        }
      }
      {
        name: 'AllowVnetInternal'
        properties: {
          priority: 110
          protocol: '*'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'VirtualNetwork'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      {
        name: 'AllowAzureLoadBalancer'
        properties: {
          priority: 120
          protocol: '*'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'AzureLoadBalancer'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource databaseNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-database-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowPostgresFromContainerApps'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: containerAppsSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '5432'
        }
      }
      {
        name: 'AllowPostgresFromBastion'
        properties: {
          priority: 110
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: bastionSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '5432'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource redisNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-redis-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowRedisFromContainerApps'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: containerAppsSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '6380'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource storageNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-storage-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowStorageFromContainerApps'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: containerAppsSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource acrNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${appName}-acr-nsg-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowACRFromContainerApps'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: containerAppsSubnetPrefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          protocol: '*'
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// Subnet NSG Associations
resource appGatewaySubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${appGatewaySubnetName}/default'
  properties: {
    id: appGatewayNsg.id
  }
}

resource containerAppsSubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${containerAppsSubnetName}/default'
  properties: {
    id: containerAppsNsg.id
  }
}

resource databaseSubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${databaseSubnetName}/default'
  properties: {
    id: databaseNsg.id
  }
}

resource redisSubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${redisSubnetName}/default'
  properties: {
    id: redisNsg.id
  }
}

resource storageSubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${storageSubnetName}/default'
  properties: {
    id: storageNsg.id
  }
}

resource acrSubnetNsgAssociation 'Microsoft.Network/virtualNetworks/subnets/networkSecurityGroups@2023-09-01' = {
  parent: vnet
  name: '${acrSubnetName}/default'
  properties: {
    id: acrNsg.id
  }
}

// Private DNS Zones for Private Endpoints
resource privateDnsZonePostgres 'Microsoft.Network/privateDnsZones@2023-09-01' = {
  name: 'privatelink.postgres.database.azure.com'
  location: 'global'
  tags: tags
}

resource privateDnsZoneRedis 'Microsoft.Network/privateDnsZones@2023-09-01' = {
  name: 'privatelink.redis.cache.windows.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneStorage 'Microsoft.Network/privateDnsZones@2023-09-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneKeyVault 'Microsoft.Network/privateDnsZones@2023-09-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneContainerRegistry 'Microsoft.Network/privateDnsZones@2023-09-01' = {
  name: 'privatelink.azurecr.io'
  location: 'global'
  tags: tags
}

// VNet Links for Private DNS Zones
resource vnetLinkPostgres 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2023-09-01' = {
  parent: privateDnsZonePostgres
  name: '${vnetName}-link'
  properties: {
    virtualNetworkId: vnet.id
    registrationEnabled: false
  }
}

resource vnetLinkRedis 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2023-09-01' = {
  parent: privateDnsZoneRedis
  name: '${vnetName}-link'
  properties: {
    virtualNetworkId: vnet.id
    registrationEnabled: false
  }
}

resource vnetLinkStorage 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2023-09-01' = {
  parent: privateDnsZoneStorage
  name: '${vnetName}-link'
  properties: {
    virtualNetworkId: vnet.id
    registrationEnabled: false
  }
}

resource vnetLinkKeyVault 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2023-09-01' = {
  parent: privateDnsZoneKeyVault
  name: '${vnetName}-link'
  properties: {
    virtualNetworkId: vnet.id
    registrationEnabled: false
  }
}

resource vnetLinkContainerRegistry 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2023-09-01' = {
  parent: privateDnsZoneContainerRegistry
  name: '${vnetName}-link'
  properties: {
    virtualNetworkId: vnet.id
    registrationEnabled: false
  }
}

// Outputs
output vnetId string = vnet.id
output vnetName string = vnet.name
output appGatewaySubnetId string = vnet::subnets(appGatewaySubnetName).id
output containerAppsSubnetId string = vnet::subnets(containerAppsSubnetName).id
output databaseSubnetId string = vnet::subnets(databaseSubnetName).id
output redisSubnetId string = vnet::subnets(redisSubnetName).id
output storageSubnetId string = vnet::subnets(storageSubnetName).id
output acrSubnetId string = vnet::subnets(acrSubnetName).id
output bastionSubnetId string = vnet::subnets(bastionSubnetName).id