/**
 * AvertaSaaS - Monitoring Module
 *
 * Creates alert rules, action groups, and diagnostic settings for all resources.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

@description('Application Insights name')
param appInsightsName string

@description('PostgreSQL Resource ID')
param postgresResourceId string

@description('Redis Resource ID')
param redisResourceId string

@description('Storage Resource ID')
param storageResourceId string

@description('Container Apps Environment Resource ID')
param containerAppsEnvResourceId string

@description('Application Gateway Resource ID')
param appGatewayResourceId string

@description('Tags')
param tags object

@description('Alert email receivers')
param alertEmails array = []

@description('Alert webhook URL (optional)')
param alertWebhookUrl string = ''

var actionGroupName = '${appName}-alerts-${environment}'

// Action Group for alerts
resource actionGroup 'Microsoft.Insights/actionGroups@2023-09-01' = {
  name: actionGroupName
  location: 'Global'
  tags: tags
  properties: {
    groupShortName: 'averta-${environment}'
    enabled: true
    emailReceivers: [for email in alertEmails: {
      name: 'email-${split(email, '@')[0]}'
      emailAddress: email
      useCommonAlertSchema: true
    }]
    webhookReceivers: alertWebhookUrl != '' ? [
      {
        name: 'webhook'
        serviceUri: alertWebhookUrl
        useCommonAlertSchema: true
      }
    ] : []
    smsReceivers: []
    voiceReceivers: []
    azureAppPushReceivers: []
    itsmReceivers: []
    automationRunbookReceivers: []
    logicAppReceivers: []
    azureFunctionReceivers: []
  }
}

// =============================================================================
// POSTGRESQL ALERTS
// =============================================================================

resource alertPgCpuHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-pg-cpu-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'PostgreSQL CPU usage above 80%'
    severity: 2
    enabled: true
    scopes: [postgresResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighCpu'
          metricName: 'cpu_percent'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertPgMemoryHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-pg-memory-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'PostgreSQL memory usage above 85%'
    severity: 2
    enabled: true
    scopes: [postgresResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighMemory'
          metricName: 'memory_percent'
          operator: 'GreaterThan'
          threshold: 85
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertPgStorageHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-pg-storage-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'PostgreSQL storage usage above 80%'
    severity: 1
    enabled: true
    scopes: [postgresResourceId]
    evaluationFrequency: 'PT1H'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          name: 'HighStorage'
          metricName: 'storage_percent'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertPgConnectionsHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-pg-connections-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'PostgreSQL connections above 80% of max'
    severity: 2
    enabled: true
    scopes: [postgresResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighConnections'
          metricName: 'active_connections'
          operator: 'GreaterThan'
          threshold: 320 // 80% of 400
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertPgReplicationLag 'Microsoft.Insights/metricAlerts@2023-09-01' = if (environment == 'production') {
  name: '${appName}-alert-pg-replication-lag-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'PostgreSQL replication lag above 30 seconds'
    severity: 1
    enabled: true
    scopes: [postgresResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'ReplicationLag'
          metricName: 'replication_lag'
          operator: 'GreaterThan'
          threshold: 30
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// REDIS ALERTS
// =============================================================================

resource alertRedisCpuHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-redis-cpu-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Redis CPU usage above 80%'
    severity: 2
    enabled: true
    scopes: [redisResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighCpu'
          metricName: 'cpu'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertRedisMemoryHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-redis-memory-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Redis memory usage above 85%'
    severity: 2
    enabled: true
    scopes: [redisResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighMemory'
          metricName: 'used_memory_percentage'
          operator: 'GreaterThan'
          threshold: 85
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertRedisConnectedClients 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-redis-clients-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Redis connected clients above threshold'
    severity: 2
    enabled: true
    scopes: [redisResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighClients'
          metricName: 'connected_clients'
          operator: 'GreaterThan'
          threshold: 1000
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertRedisCacheMissRate 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-redis-cache-miss-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Redis cache miss rate above 20%'
    severity: 2
    enabled: true
    scopes: [redisResourceId]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      allOf: [
        {
          name: 'HighCacheMiss'
          metricName: 'cache_miss_rate'
          operator: 'GreaterThan'
          threshold: 20
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// STORAGE ALERTS
// =============================================================================

resource alertStorageCapacity 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-storage-capacity-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Storage account capacity above 80%'
    severity: 1
    enabled: true
    scopes: [storageResourceId]
    evaluationFrequency: 'PT1H'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          name: 'HighCapacity'
          metricName: 'UsedCapacity'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertStorageAvailability 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-storage-availability-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Storage availability below 99.9%'
    severity: 0
    enabled: true
    scopes: [storageResourceId]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      allOf: [
        {
          name: 'LowAvailability'
          metricName: 'Availability'
          operator: 'LessThan'
          threshold: 99.9
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertStorageLatency 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-storage-latency-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Storage latency above 500ms'
    severity: 2
    enabled: true
    scopes: [storageResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighLatency'
          metricName: 'SuccessE2ELatency'
          operator: 'GreaterThan'
          threshold: 500
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// CONTAINER APPS ALERTS
// =============================================================================

resource alertCaCpuHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-ca-cpu-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Container Apps CPU usage above 80%'
    severity: 2
    enabled: true
    scopes: [containerAppsEnvResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighCpu'
          metricName: 'CpuUsage'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertCaMemoryHigh 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-ca-memory-high-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Container Apps memory usage above 85%'
    severity: 2
    enabled: true
    scopes: [containerAppsEnvResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighMemory'
          metricName: 'MemoryUsage'
          operator: 'GreaterThan'
          threshold: 85
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertCaRequestLatency 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-ca-latency-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Container Apps request latency above 2s'
    severity: 2
    enabled: true
    scopes: [containerAppsEnvResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighLatency'
          metricName: 'HttpRequestLatency'
          operator: 'GreaterThan'
          threshold: 2000
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertCaHttpErrors 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-ca-http-errors-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Container Apps HTTP 5xx error rate above 1%'
    severity: 1
    enabled: true
    scopes: [containerAppsEnvResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighErrorRate'
          metricName: 'HttpServerErrors'
          operator: 'GreaterThan'
          threshold: 1
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertCaReplicaCount 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-ca-replicas-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Container Apps replica count at maximum'
    severity: 2
    enabled: true
    scopes: [containerAppsEnvResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'MaxReplicas'
          metricName: 'ReplicaCount'
          operator: 'GreaterThanOrEqual'
          threshold: environment == 'production' ? 10 : 5
          timeAggregation: 'Maximum'
          criterionType: 'StaticThresholdCriterion'
          dimensions: []
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// APPLICATION GATEWAY ALERTS
// =============================================================================

resource alertAppGwLatency 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appgw-latency-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Gateway latency above 2s'
    severity: 2
    enabled: true
    scopes: [appGatewayResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighLatency'
          metricName: 'Latency'
          operator: 'GreaterThan'
          threshold: 2000
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertAppGwFailedRequests 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appgw-failed-requests-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Gateway failed requests above 1%'
    severity: 1
    enabled: true
    scopes: [appGatewayResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighFailedRequests'
          metricName: 'FailedRequests'
          operator: 'GreaterThan'
          threshold: 1
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertAppGwWafBlocked 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appgw-waf-blocked-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Gateway WAF blocked requests spike'
    severity: 2
    enabled: true
    scopes: [appGatewayResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'WafBlockedSpike'
          metricName: 'WebApplicationFirewallBlockedRequestCount'
          operator: 'GreaterThan'
          threshold: 100
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertAppGwUnhealthyBackend 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appgw-unhealthy-backend-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Gateway unhealthy backend count > 0'
    severity: 0
    enabled: true
    scopes: [appGatewayResourceId]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'UnhealthyBackend'
          metricName: 'UnhealthyHostCount'
          operator: 'GreaterThan'
          threshold: 0
          timeAggregation: 'Maximum'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// APPLICATION INSIGHTS ALERTS (Additional)
// =============================================================================

resource alertAppInsightsFailedRequests 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appinsights-failed-requests-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Insights failed requests above 5%'
    severity: 1
    enabled: true
    scopes: [resourceId('Microsoft.Insights/components', appInsightsName)]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighFailureRate'
          metricName: 'requests/failed'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertAppInsightsDependencyFailures 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appinsights-dep-failures-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Insights dependency failures above 5%'
    severity: 2
    enabled: true
    scopes: [resourceId('Microsoft.Insights/components', appInsightsName)]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighDepFailureRate'
          metricName: 'dependencies/failed'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource alertAppInsightsExceptions 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-appinsights-exceptions-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Application Insights exception rate spike'
    severity: 2
    enabled: true
    scopes: [resourceId('Microsoft.Insights/components', appInsightsName)]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighExceptionRate'
          metricName: 'exceptions/count'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// LOG ALERTS (for specific error patterns)
// =============================================================================

resource logAlertDatabaseErrors 'Microsoft.Insights/scheduledQueryRules@2023-09-01' = {
  name: '${appName}-log-alert-db-errors-${environment}'
  location: location
  tags: tags
  kind: 'LogAlert'
  properties: {
    description: 'Alert on database errors in logs'
    severity: 1
    enabled: true
    schedule: {
      frequencyInMinutes: 5
      timeWindowInMinutes: 10
    }
    query: '''
      AzureDiagnostics
      | where ResourceType == "DATABASEFORPOSTGRESQL/FLEXIBLESERVERS"
      | where LogicalServerName_s == "${appName}-postgres-${environment}"
      | where Message has "ERROR" or Message has "FATAL" or Message has "PANIC"
      | summarize count() by bin(TimeGenerated, 5m)
      | where count_ > 0
    '''
    trigger: {
      thresholdOperator: 'GreaterThan'
      threshold: 0
      triggerConditionType: 'Consecutive'
      triggerCondition: 1
    }
    actionGroups: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

resource logAlertAppErrors 'Microsoft.Insights/scheduledQueryRules@2023-09-01' = {
  name: '${appName}-log-alert-app-errors-${environment}'
  location: location
  tags: tags
  kind: 'LogAlert'
  properties: {
    description: 'Alert on application errors in Container Apps logs'
    severity: 1
    enabled: true
    schedule: {
      frequencyInMinutes: 5
      timeWindowInMinutes: 10
    }
    query: '''
      ContainerAppConsoleLogs_CL
      | where ContainerAppName_s startswith "${appName}-"
      | where Log_s has "ERROR" or Log_s has "EXCEPTION" or Log_s has "CRITICAL"
      | summarize count() by bin(TimeGenerated, 5m), ContainerAppName_s
      | where count_ > 10
    '''
    trigger: {
      thresholdOperator: 'GreaterThan'
      threshold: 0
      triggerConditionType: 'Consecutive'
      triggerCondition: 1
    }
    actionGroups: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// =============================================================================
// WORKBOOK (Dashboard)
// =============================================================================

resource workbook 'Microsoft.Insights/workbooks@2023-09-01' = {
  name: '${appName}-workbook-${environment}'
  location: location
  tags: tags
  properties: {
    displayName: 'AvertaSaaS - ${environment} Infrastructure'
    description: 'Infrastructure monitoring dashboard for ${environment} environment'
    serializedData: json('{
      "version": "Notebook/1.0",
      "items": [
        {
          "type": 1,
          "content": {
            "json": "# AvertaSaaS Infrastructure - ${environment}\\n\\nReal-time infrastructure health and performance metrics.",
            "settings": {
              "markdown": {
                "header": 1
              }
            }
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "AzureMetrics | where ResourceProvider == \"MICROSOFT.DBFORPOSTGRESQL\" | summarize AvgCpu=avg(Val) by Resource, bin(TimeGenerated, 5m) | render timechart",
                "resourceIds": [${json(postgresResourceId)}]
              }
            ],
            "visualization": "timechart",
            "title": "PostgreSQL CPU Usage"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "AzureMetrics | where ResourceProvider == \"MICROSOFT.CACHE\" | summarize AvgMem=avg(Val) by Resource, bin(TimeGenerated, 5m) | render timechart",
                "resourceIds": [${json(redisResourceId)}]
              }
            ],
            "visualization": "timechart",
            "title": "Redis Memory Usage"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "AzureMetrics | where ResourceProvider == \"MICROSOFT.STORAGE\" | summarize AvgLatency=avg(Val) by Resource, bin(TimeGenerated, 5m) | render timechart",
                "resourceIds": [${json(storageResourceId)}]
              }
            ],
            "visualization": "timechart",
            "title": "Storage Latency"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "ContainerAppConsoleLogs_CL | where ContainerAppName_s startswith \"${appName}-\" | summarize count() by ContainerAppName_s, bin(TimeGenerated, 5m) | render timechart",
                "resourceIds": [${json(containerAppsEnvResourceId)}]
              }
            ],
            "visualization": "timechart",
            "title": "Container Apps Log Volume"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "AzureMetrics | where ResourceProvider == \"MICROSOFT.NETWORK/APPLICATIONGATEWAYS\" | summarize AvgLatency=avg(Val) by Resource, bin(TimeGenerated, 5m) | render timechart",
                "resourceIds": [${json(appGatewayResourceId)}]
              }
            ],
            "visualization": "timechart",
            "title": "Application Gateway Latency"
          }
        }
      ]
    }')
    version: '1.0'
    category: 'workbook'
    tags: tags
  }
}

// =============================================================================
// DIAGNOSTIC SETTINGS FOR ALL RESOURCES
// =============================================================================

// These would be added to each resource module, but can be centralized here
// Example for PostgreSQL:
resource pgDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${appName}-pg-diagnostics-${environment}'
  scope: postgresResourceId
  properties: {
    workspaceId: logAnalyticsWorkspaceId
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

resource redisDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${appName}-redis-diagnostics-${environment}'
  scope: redisResourceId
  properties: {
    workspaceId: logAnalyticsWorkspaceId
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

resource storageDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${appName}-storage-diagnostics-${environment}'
  scope: storageResourceId
  properties: {
    workspaceId: logAnalyticsWorkspaceId
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

resource appGwDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${appName}-appgw-diagnostics-${environment}'
  scope: appGatewayResourceId
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'ApplicationGatewayAccessLog'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
      {
        category: 'ApplicationGatewayPerformanceLog'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
      {
        category: 'ApplicationGatewayFirewallLog'
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

output actionGroupId string = actionGroup.id
output workbookId string = workbook.id