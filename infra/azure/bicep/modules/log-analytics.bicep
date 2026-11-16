/**
 * AvertaSaaS - Log Analytics Workspace Module
 *
 * Creates Log Analytics workspace for centralized logging and monitoring.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Tags')
param tags object

@description('Retention in days')
param retentionInDays int = environment == 'production' ? 90 : 30

@description('SKU')
param sku string = 'PerGB2018'

var workspaceName = '${appName}-logs-${environment}'

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: sku
    }
    retentionInDays: retentionInDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Shared keys for workspace (needed for Container Apps)
resource sharedKeys 'Microsoft.OperationalInsights/workspaces/sharedKeys@2023-09-01' = {
  parent: workspace
  name: 'sharedKeys'
}

// Solution for Container Insights
resource containerInsightsSolution 'Microsoft.OperationsManagement/solutions@2023-09-01' = {
  name: 'ContainerInsights(${workspaceName})'
  location: location
  tags: tags
  properties: {
    workspaceResourceId: workspace.id
    containedResources: []
    plan: {
      name: 'ContainerInsights'
      publisher: 'Microsoft'
      product: 'OMSGallery/ContainerInsights'
      promotionCode: ''
    }
  }
}

// Solution for VM Insights (if needed)
resource vmInsightsSolution 'Microsoft.OperationsManagement/solutions@2023-09-01' = {
  name: 'VMInsights(${workspaceName})'
  location: location
  tags: tags
  properties: {
    workspaceResourceId: workspace.id
    containedResources: []
    plan: {
      name: 'VMInsights'
      publisher: 'Microsoft'
      product: 'OMSGallery/VMInsights'
      promotionCode: ''
    }
  }
}

// Data Collection Rule for Container Apps logs
resource dcrContainerApps 'Microsoft.Insights/dataCollectionRules@2023-09-01' = {
  name: '${appName}-dcr-container-apps-${environment}'
  location: location
  tags: tags
  properties: {
    dataSources: {
      performanceCounters: []
      windowsEventLogs: []
      syslog: []
      logFiles: [
        {
          filePatterns: [
            '/var/log/containers/*.log'
          ]
          format: 'json'
          settings: {
            text: {
              recordStartTimestampFormat: 'yyyy-MM-ddTHH:mm:ss.fffK'
            }
          }
        }
      ]
    }
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: workspace.id
          name: 'workspace'
        }
      ]
    }
    dataFlows: [
      {
        streams: [
          'Microsoft-ContainerLogs'
        ]
        destinations: [
          'workspace'
        ]
      }
    ]
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspaceKey string = listKeys(workspace.id, workspace.apiVersion).primarySharedKey