/**
 * AvertaSaaS - Application Insights Module
 *
 * Creates Application Insights resource for application performance monitoring.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

@description('Tags')
param tags object

@description('Application type')
param applicationType string = 'web'

@description('Sampling percentage')
param samplingPercentage int = environment == 'production' ? 10 : 100

var appInsightsName = '${appName}-appinsights-${environment}'

resource appInsights 'Microsoft.Insights/components@2023-09-01' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: applicationType
  properties: {
    Application_Type: applicationType
    Flow_Type: 'Redfield'
    Request_Source: 'rest'
    RetentionInDays: environment == 'production' ? 90 : 30
    SamplingPercentage: samplingPercentage
    WorkspaceResourceId: logAnalyticsWorkspaceId
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    ingestionMode: 'LogAnalytics'
    features: [
      {
        FeatureName: 'EnableApplicationInsightsInstrumentationEngine'
        Value: 'true'
      }
    ]
  }
}

// Availability tests (synthetic monitoring)
resource availabilityTest 'Microsoft.Insights/webtests@2023-09-01' = {
  name: '${appName}-availability-test-${environment}'
  location: location
  tags: tags
  kind: 'ping'
  properties: {
    SyntheticMonitorId: '${appName}-availability-test-${environment}'
    Name: '${appName}-availability-test-${environment}'
    Enabled: true
    Frequency: 300
    Timeout: 120
    Kind: 'ping'
    RetryEnabled: true
    Locations: [
      {
        Id: 'emea-nl-amsterdam-azr'
      }
      {
        Id: 'emea-gb-london-azr'
      }
      {
        Id: 'us-tx-sanantonio-azr'
      }
    ]
    Configuration: {
      WebTest: '[WebTest]'
      WebTestType: 'Standard'
    }
    Description: 'Availability test for AvertaSaaS API health endpoint'
  }
}

// Alert rules
resource alertHighLatency 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-high-latency-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when API latency exceeds threshold'
    severity: 2
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighLatency'
          metricName: 'duration'
          operator: 'GreaterThan'
          threshold: environment == 'production' ? 2000 : 5000
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: []
  }
}

resource alertHighErrorRate 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-high-error-rate-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when API error rate exceeds threshold'
    severity: 1
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          name: 'HighErrorRate'
          metricName: 'requests/failed'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: []
  }
}

resource alertLowAvailability 'Microsoft.Insights/metricAlerts@2023-09-01' = {
  name: '${appName}-alert-low-availability-${environment}'
  location: 'global'
  tags: tags
  properties: {
    description: 'Alert when availability drops below threshold'
    severity: 0
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      allOf: [
        {
          name: 'LowAvailability'
          metricName: 'availabilityResults/availabilityPercentage'
          operator: 'LessThan'
          threshold: 99.5
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: []
  }
}

// Workbook (Dashboard)
resource workbook 'Microsoft.Insights/workbooks@2023-09-01' = {
  name: '${appName}-workbook-${environment}'
  location: location
  tags: tags
  properties: {
    displayName: 'AvertaSaaS - ${environment} Dashboard'
    description: 'Operational dashboard for AvertaSaaS ${environment} environment'
    serializedData: json('{
      "version": "Notebook/1.0",
      "items": [
        {
          "type": 1,
          "content": {
            "json": "# AvertaSaaS - ${environment} Dashboard\\n\\nOperational overview for the ${environment} environment.",
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
                "query": "requests | summarize Requests=count(), AvgDuration=avg(duration), Errors=countif(success==false) by bin(timestamp, 5m) | render timechart",
                "resourceIds": [${json(appInsights.id)}]
              }
            ],
            "visualization": "timechart",
            "title": "Request Volume & Latency"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "requests | where success == false | summarize Errors=count() by resultCode, bin(timestamp, 5m) | render timechart",
                "resourceIds": [${json(appInsights.id)}]
              }
            ],
            "visualization": "timechart",
            "title": "Errors by Status Code"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "dependencies | summarize Calls=count(), AvgDuration=avg(duration), Failures=countif(success==false) by name, bin(timestamp, 5m) | render timechart",
                "resourceIds": [${json(appInsights.id)}]
              }
            ],
            "visualization": "timechart",
            "title": "Dependency Calls"
          }
        },
        {
          "type": 3,
          "content": {
            "queries": [
              {
                "query": "traces | where severityLevel >= 3 | summarize count() by message, bin(timestamp, 5m) | render timechart",
                "resourceIds": [${json(appInsights.id)}]
              }
            ],
            "visualization": "timechart",
            "title": "Exceptions & Logs"
          }
        }
      ]
    }')
    version: '1.0'
    category: 'workbook'
    tags: tags
  }
}

output name string = appInsights.name
output connectionString string = appInsights.properties.ConnectionString
output instrumentationKey string = appInsights.properties.InstrumentationKey
output resourceId string = appInsights.id