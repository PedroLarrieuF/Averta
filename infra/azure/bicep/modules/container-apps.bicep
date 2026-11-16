/**
 * AvertaSaaS - Container Apps Module
 *
 * Creates Container Apps for:
 * - Backend API (with ingress)
 * - Celery Worker (no ingress, scaled by queue depth)
 * - Celery Beat (single replica, scheduled tasks)
 *
 * All apps use managed identity for Azure service access.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('Container Apps Environment ID')
param containerAppsEnvId string

@description('Container Registry output object')
param containerRegistry object

@description('PostgreSQL FQDN')
param postgresFqdn string

@description('PostgreSQL admin login')
param postgresAdminLogin string

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('Redis host name')
param redisHost string

@description('Redis port')
param redisPort int

@description('Redis access key')
@secure()
param redisAccessKey string

@description('Storage account name')
param storageAccountName string

@description('Storage account key')
@secure()
param storageAccountKey string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Key Vault name')
param keyVaultName string

@description('Frontend URL for CORS')
param frontendUrl string

@description('Custom domain (optional)')
param customDomain string

@description('Tags')
param tags object

@description('Backend image tag')
param backendImageTag string = 'latest'

@description('Backend CPU cores')
param backendCpu string = environment == 'production' ? '2.0' : '1.0'

@description('Backend memory')
param backendMemory string = environment == 'production' ? '4Gi' : '2Gi'

@description('Backend min replicas')
param backendMinReplicas int = environment == 'production' ? 2 : 1

@description('Backend max replicas')
param backendMaxReplicas int = environment == 'production' ? 10 : 5

@description('Worker CPU cores')
param workerCpu string = environment == 'production' ? '2.0' : '1.0'

@description('Worker memory')
param workerMemory string = environment == 'production' ? '4Gi' : '2Gi'

@description('Worker min replicas')
param workerMinReplicas int = environment == 'production' ? 1 : 0

@description('Worker max replicas')
param workerMaxReplicas int = environment == 'production' ? 20 : 5

@description('Beat CPU cores')
param beatCpu string = '0.5'

@description('Beat memory')
param beatMemory string = '1Gi'

var containerAppsEnvName = last(split(containerAppsEnvId, '/'))
var registryLoginServer = containerRegistry.loginServer
var backendImage = '${registryLoginServer}/averta-backend:${backendImageTag}'
var keyVaultUri = 'https://${keyVaultName}.vault.azure.net'

// =============================================================================
// BACKEND API CONTAINER APP
// =============================================================================

resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-backend-${environment}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
        customDomains: customDomain != '' ? [
          {
            name: customDomain
            bindingType: 'SniEnabled'
          }
        ] : []
        cors: {
          allowedOrigins: [
            frontendUrl
          ]
          allowedMethods: [
            'GET'
            'POST'
            'PUT'
            'DELETE'
            'PATCH'
            'OPTIONS'
          ]
          allowedHeaders: [
            '*'
          ]
          allowCredentials: true
          maxAge: 3600
        }
      }
      registries: [
        {
          server: registryLoginServer
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      secrets: [
        {
          name: 'database-url'
          keyVaultUrl: '${keyVaultUri}/secrets/database'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'redis-url'
          keyVaultUrl: '${keyVaultUri}/secrets/redis'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'storage-config'
          keyVaultUrl: '${keyVaultUri}/secrets/storage'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'jwt-secrets'
          keyVaultUrl: '${keyVaultUri}/secrets/jwt'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'app-config'
          keyVaultUrl: '${keyVaultUri}/secrets/app'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      activeRevisionsMode: 'Multiple'
      dapr: {
        enabled: false
      }
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          resources: {
            cpu: backendCpu
            memory: backendMemory
          }
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'S3_ENDPOINT'
              value: 'https://${storageAccountName}.blob.core.windows.net'
            }
            {
              name: 'S3_ACCESS_KEY'
              value: storageAccountName
            }
            {
              name: 'S3_SECRET_KEY'
              secretRef: 'storage-config'
            }
            {
              name: 'S3_BUCKET'
              value: 'averta-documents'
            }
            {
              name: 'S3_REGION'
              value: location
            }
            {
              name: 'S3_PUBLIC_URL'
              value: 'https://${storageAccountName}.blob.core.windows.net'
            }
            {
              name: 'CELERY_BROKER_URL'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/1'
            }
            {
              name: 'CELERY_RESULT_BACKEND'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/2'
            }
            {
              name: 'JWT_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'JWT_REFRESH_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'JWT_ALGORITHM'
              value: 'HS256'
            }
            {
              name: 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
              value: '15'
            }
            {
              name: 'JWT_REFRESH_TOKEN_EXPIRE_DAYS'
              value: '7'
            }
            {
              name: 'FRONTEND_URL'
              value: frontendUrl
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'DEBUG'
              value: environment == 'production' ? 'false' : 'true'
            }
            {
              name: 'LOG_LEVEL'
              value: environment == 'production' ? 'INFO' : 'DEBUG'
            }
            {
              name: 'LOG_FORMAT'
              value: 'json'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: 'https://${location}.otlp.azuremonitor.com/v1/traces'
            }
            {
              name: 'OTEL_EXPORTER_OTLP_HEADERS'
              value: 'Authorization=Bearer ${appInsightsConnectionString}'
            }
            {
              name: 'PYTHONUNBUFFERED'
              value: '1'
            }
            {
              name: 'UVICORN_WORKERS'
              value: '4'
            }
          ]
          probes: {
            liveness: {
              type: 'http'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
            readiness: {
              type: 'http'
              httpGet: {
                path: '/health/ready'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 5
              timeoutSeconds: 3
              failureThreshold: 3
            }
          }
        }
      ]
      scale: {
        minReplicas: backendMinReplicas
        maxReplicas: backendMaxReplicas
        rules: [
          {
            name: 'http-scaling'
            type: 'http'
            metadata: {
              concurrentRequests: '100'
            }
          }
          {
            name: 'cpu-scaling'
            type: 'cpu'
            metadata: {
              type: 'Utilization'
              value: '70'
            }
          }
          {
            name: 'memory-scaling'
            type: 'memory'
            metadata: {
              type: 'Utilization'
              value: '80'
            }
          }
        ]
      }
    }
  }
}

// =============================================================================
// CELERY WORKER CONTAINER APP
// =============================================================================

resource celeryWorkerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-celery-worker-${environment}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: false
      }
      registries: [
        {
          server: registryLoginServer
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      secrets: [
        {
          name: 'database-url'
          keyVaultUrl: '${keyVaultUri}/secrets/database'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'redis-url'
          keyVaultUrl: '${keyVaultUri}/secrets/redis'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'storage-config'
          keyVaultUrl: '${keyVaultUri}/secrets/storage'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'jwt-secrets'
          keyVaultUrl: '${keyVaultUri}/secrets/jwt'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'app-config'
          keyVaultUrl: '${keyVaultUri}/secrets/app'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      activeRevisionsMode: 'Multiple'
      dapr: {
        enabled: false
      }
    }
    template: {
      containers: [
        {
          name: 'celery-worker'
          image: backendImage
          resources: {
            cpu: workerCpu
            memory: workerMemory
          }
          command: [
            'celery'
            '-A'
            'app.core.celery_app'
            'worker'
            '--loglevel=info'
            '--concurrency=4'
            '--pool=prefork'
            '--max-tasks-per-child=1000'
          ]
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'S3_ENDPOINT'
              value: 'https://${storageAccountName}.blob.core.windows.net'
            }
            {
              name: 'S3_ACCESS_KEY'
              value: storageAccountName
            }
            {
              name: 'S3_SECRET_KEY'
              secretRef: 'storage-config'
            }
            {
              name: 'S3_BUCKET'
              value: 'averta-documents'
            }
            {
              name: 'S3_REGION'
              value: location
            }
            {
              name: 'S3_PUBLIC_URL'
              value: 'https://${storageAccountName}.blob.core.windows.net'
            }
            {
              name: 'CELERY_BROKER_URL'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/1'
            }
            {
              name: 'CELERY_RESULT_BACKEND'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/2'
            }
            {
              name: 'JWT_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'JWT_REFRESH_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'DEBUG'
              value: environment == 'production' ? 'false' : 'true'
            }
            {
              name: 'LOG_LEVEL'
              value: environment == 'production' ? 'INFO' : 'DEBUG'
            }
            {
              name: 'LOG_FORMAT'
              value: 'json'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
            {
              name: 'PYTHONUNBUFFERED'
              value: '1'
            }
          ]
          probes: {
            liveness: {
              type: 'exec'
              exec: {
                command: [
                  'celery'
                  '-A'
                  'app.core.celery_app'
                  'inspect'
                  'ping'
                ]
              }
              initialDelaySeconds: 60
              periodSeconds: 30
              timeoutSeconds: 10
              failureThreshold: 3
            }
          }
        }
      ]
      scale: {
        minReplicas: workerMinReplicas
        maxReplicas: workerMaxReplicas
        rules: [
          {
            name: 'queue-scaling'
            type: 'azure-queue'
            metadata: {
              queueName: 'celery'
              connection: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/1'
              queueLength: '10'
            }
          }
          {
            name: 'cpu-scaling'
            type: 'cpu'
            metadata: {
              type: 'Utilization'
              value: '70'
            }
          }
        ]
      }
    }
  }
}

// =============================================================================
// CELERY BEAT CONTAINER APP
// =============================================================================

resource celeryBeatApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-celery-beat-${environment}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: false
      }
      registries: [
        {
          server: registryLoginServer
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      secrets: [
        {
          name: 'database-url'
          keyVaultUrl: '${keyVaultUri}/secrets/database'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'redis-url'
          keyVaultUrl: '${keyVaultUri}/secrets/redis'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'jwt-secrets'
          keyVaultUrl: '${keyVaultUri}/secrets/jwt'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'app-config'
          keyVaultUrl: '${keyVaultUri}/secrets/app'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      activeRevisionsMode: 'Single'
      dapr: {
        enabled: false
      }
    }
    template: {
      containers: [
        {
          name: 'celery-beat'
          image: backendImage
          resources: {
            cpu: beatCpu
            memory: beatMemory
          }
          command: [
            'celery'
            '-A'
            'app.core.celery_app'
            'beat'
            '--loglevel=info'
            '--scheduler'
            'celery.beat.PersistentScheduler'
          ]
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'CELERY_BROKER_URL'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/1'
            }
            {
              name: 'CELERY_RESULT_BACKEND'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/2'
            }
            {
              name: 'JWT_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'JWT_REFRESH_SECRET_KEY'
              secretRef: 'jwt-secrets'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'DEBUG'
              value: environment == 'production' ? 'false' : 'true'
            }
            {
              name: 'LOG_LEVEL'
              value: environment == 'production' ? 'INFO' : 'DEBUG'
            }
            {
              name: 'LOG_FORMAT'
              value: 'json'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
            {
              name: 'PYTHONUNBUFFERED'
              value: '1'
            }
          ]
          probes: {
            liveness: {
              type: 'exec'
              exec: {
                command: [
                  'celery'
                  '-A'
                  'app.core.celery_app'
                  'inspect'
                  'ping'
                ]
              }
              initialDelaySeconds: 30
              periodSeconds: 60
              timeoutSeconds: 10
              failureThreshold: 3
            }
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
        rules: []
      }
    }
  }
}

// =============================================================================
// FLOWER CONTAINER APP (Monitoring)
// =============================================================================

resource flowerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-flower-${environment}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: true
        targetPort: 5555
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: [
        {
          server: registryLoginServer
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      secrets: [
        {
          name: 'redis-url'
          keyVaultUrl: '${keyVaultUri}/secrets/redis'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
        {
          name: 'app-config'
          keyVaultUrl: '${keyVaultUri}/secrets/app'
          identity: '${containerAppsEnvId}/userAssignedIdentities/${appName}-ca-mi-${environment}'
        }
      ]
      activeRevisionsMode: 'Single'
      dapr: {
        enabled: false
      }
    }
    template: {
      containers: [
        {
          name: 'flower'
          image: backendImage
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
          command: [
            'celery'
            '-A'
            'app.core.celery_app'
            'flower'
            '--port=5555'
            '--basic_auth=admin:admin'
          ]
          env: [
            {
              name: 'CELERY_BROKER_URL'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/1'
            }
            {
              name: 'CELERY_RESULT_BACKEND'
              value: 'rediss://:${redisAccessKey}@${redisHost}:${redisPort}/2'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'LOG_LEVEL'
              value: environment == 'production' ? 'INFO' : 'DEBUG'
            }
            {
              name: 'PYTHONUNBUFFERED'
              value: '1'
            }
          ]
          probes: {
            liveness: {
              type: 'http'
              httpGet: {
                path: '/'
                port: 5555
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 30
              timeoutSeconds: 10
              failureThreshold: 3
            }
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
        rules: []
      }
    }
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

output backendFqdn string = backendApp.properties.configuration.ingress.fqdn
output backendAppUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output backendAppId string = backendApp.id
output celeryWorkerAppId string = celeryWorkerApp.id
output celeryBeatAppId string = celeryBeatApp.id
output flowerAppId string = flowerApp.id
output flowerFqdn string = flowerApp.properties.configuration.ingress.fqdn