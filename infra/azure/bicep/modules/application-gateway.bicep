/**
 * AvertaSaaS - Application Gateway Module
 *
 * Creates Azure Application Gateway with WAF for backend API.
 * Provides TLS termination, routing, and protection.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Azure region')
param location string

@description('VNet Resource ID')
param vnetResourceId string

@description('Application Gateway Subnet ID')
param subnetId string

@description('Container Apps Environment ID')
param containerAppsEnvId string

@description('Backend App FQDN')
param backendAppFqdn string

@description('Enable WAF')
param enableWaf bool = true

@description('Custom domain (optional)')
param customDomain string = ''

@description('Tags')
param tags object

@description('SKU name: Standard_v2, WAF_v2')
param skuName string = enableWaf ? 'WAF_v2' : 'Standard_v2'

@description('SKU tier: Standard_v2, WAF_v2')
param skuTier string = enableWaf ? 'WAF_v2' : 'Standard_v2'

@description('Capacity (instances)')
param capacity int = environment == 'production' ? 3 : 1

@description('Enable autoscaling')
param enableAutoscaling bool = environment == 'production'

@description('Min capacity for autoscaling')
param minCapacity int = environment == 'production' ? 2 : 1

@description('Max capacity for autoscaling')
param maxCapacity int = environment == 'production' ? 10 : 3

var appGatewayName = '${appName}-appgw-${environment}'
var publicIpName = '${appName}-appgw-pip-${environment}'
var wafPolicyName = '${appName}-waf-policy-${environment}'

// Public IP Address
resource publicIp 'Microsoft.Network/publicIPAddresses@2023-09-01' = {
  name: publicIpName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: '${uniqueString(resourceGroup().id, appName, environment)}'
    }
    zones: environment == 'production' ? ['1', '2', '3'] : []
  }
}

// WAF Policy
resource wafPolicy 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2023-09-01' = if (enableWaf) {
  name: wafPolicyName
  location: location
  tags: tags
  properties: {
    policySettings: {
      mode: 'Prevention'
      state: 'Enabled'
      requestBodyCheck: true
      maxRequestBodySizeInKb: 128
      fileUploadLimitInMb: 100
    }
    customRules: [
      {
        name: 'RateLimitAPI'
        priority: 1
        ruleType: 'MatchRule'
        action: 'Block'
        matchConditions: [
          {
            matchVariables: [
              {
                variableName: 'RemoteAddr'
              }
            ]
            operator: 'IPMatch'
            matchValues: [] // Add IPs to block
          }
        ]
      }
      {
        name: 'BlockBadBots'
        priority: 2
        ruleType: 'MatchRule'
        action: 'Block'
        matchConditions: [
          {
            matchVariables: [
              {
                variableName: 'RequestHeaders'
                selector: 'User-Agent'
              }
            ]
            operator: 'Contains'
            matchValues: [
              'sqlmap'
              'nikto'
              'nmap'
              'masscan'
              'zap'
            ]
          }
        ]
      }
      {
        name: 'AllowHealthChecks'
        priority: 100
        ruleType: 'MatchRule'
        action: 'Allow'
        matchConditions: [
          {
            matchVariables: [
              {
                variableName: 'RequestUri'
              }
            ]
            operator: 'Contains'
            matchValues: [
              '/health'
            ]
          }
        ]
      }
    ]
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'OWASP'
          ruleSetVersion: '3.2'
          ruleGroupOverrides: [
            {
              ruleGroupName: 'REQUEST-911-METHOD-ENFORCEMENT'
              rules: [
                {
                  ruleId: '911100'
                  action: 'Allow'
                }
              ]
            }
            {
              ruleGroupName: 'REQUEST-942-APPLICATION-ATTACK-SQLI'
              rules: []
            }
          ]
        }
        {
          ruleSetType: 'Microsoft_BotManager'
          ruleSetVersion: '1.0'
        }
      ]
    }
  }
}

// Application Gateway
resource appGateway 'Microsoft.Network/applicationGateways@2023-09-01' = {
  name: appGatewayName
  location: location
  tags: tags
  properties: {
    sku: {
      name: skuName
      tier: skuTier
      capacity: capacity
    }
    gatewayIPConfigurations: [
      {
        name: 'appGatewayIpConfig'
        properties: {
          subnet: {
            id: subnetId
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appGatewayFrontendIP'
        properties: {
          publicIPAddress: {
            id: publicIp.id
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'httpPort'
        properties: {
          port: 80
        }
      }
      {
        name: 'httpsPort'
        properties: {
          port: 443
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'backendPool'
        properties: {
          backendAddresses: [
            {
              fqdn: backendAppFqdn
            }
          ]
        }
      }
    ]
    backendHttpSettings: [
      {
        name: 'backendHttpSettings'
        properties: {
          port: 443
          protocol: 'Https'
          cookieBasedAffinity: 'Disabled'
          requestTimeout: 60
          probe: {
            id: '${appGatewayName}/probes/healthProbe'
          }
          hostName: backendAppFqdn
          pickHostNameFromBackendAddress: true
          affinityCookieName: 'AvertaAffinity'
        }
      }
    ]
    httpListeners: [
      {
        name: 'httpListener'
        properties: {
          frontendIPConfiguration: {
            id: '${appGatewayName}/frontendIPConfigurations/appGatewayFrontendIP'
          }
          frontendPort: {
            id: '${appGatewayName}/frontendPorts/httpPort'
          }
          protocol: 'Http'
          sslProfile: null
          hostName: customDomain != '' ? customDomain : ''
          requireServerNameIndication: customDomain != ''
          firewallPolicy: enableWaf ? {
            id: wafPolicy.id
          } : null
        }
      }
      {
        name: 'httpsListener'
        properties: {
          frontendIPConfiguration: {
            id: '${appGatewayName}/frontendIPConfigurations/appGatewayFrontendIP'
          }
          frontendPort: {
            id: '${appGatewayName}/frontendPorts/httpsPort'
          }
          protocol: 'Https'
          sslProfile: {
            id: '${appGatewayName}/sslProfiles/defaultSslProfile'
          }
          hostName: customDomain != '' ? customDomain : ''
          requireServerNameIndication: true
          firewallPolicy: enableWaf ? {
            id: wafPolicy.id
          } : null
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'httpToHttpsRedirect'
        properties: {
          ruleType: 'Basic'
          priority: 10
          httpListener: {
            id: '${appGatewayName}/httpListeners/httpListener'
          }
          redirectConfiguration: {
            id: '${appGatewayName}/redirectConfigurations/httpToHttps'
          }
        }
      }
      {
        name: 'httpsRoutingRule'
        properties: {
          ruleType: 'Basic'
          priority: 20
          httpListener: {
            id: '${appGatewayName}/httpListeners/httpsListener'
          }
          backendAddressPool: {
            id: '${appGatewayName}/backendAddressPools/backendPool'
          }
          backendHttpSettings: {
            id: '${appGatewayName}/backendHttpSettings/backendHttpSettings'
          }
        }
      }
    ]
    redirectConfigurations: [
      {
        name: 'httpToHttps'
        properties: {
          redirectType: 'Permanent'
          targetListener: {
            id: '${appGatewayName}/httpListeners/httpsListener'
          }
          includePath: true
          includeQueryString: true
        }
      }
    ]
    probes: [
      {
        name: 'healthProbe'
        properties: {
          protocol: 'Https'
          host: backendAppFqdn
          path: '/health'
          interval: 30
          timeout: 30
          unhealthyThreshold: 3
          pickHostNameFromBackendHttpSettings: true
          minServers: 0
          match: {
            statusCodes: [
              '200-399'
            ]
          }
        }
      }
    ]
    sslProfiles: [
      {
        name: 'defaultSslProfile'
        properties: {
          sslPolicy: {
            policyType: 'Predefined'
            policyName: 'AppGwSslPolicy20220101S'
          }
          clientAuthConfiguration: {
            verifyClientCertIssuerDN: false
          }
          trustedClientCertificates: []
        }
      }
    ]
    sslCertificates: customDomain != '' ? [
      {
        name: 'customDomainCert'
        properties: {
          data: '', // Base64 encoded PFX - set from Key Vault
          password: '' // Set from Key Vault
        }
      }
    ] : [
      {
        name: 'defaultCert'
        properties: {
          data: '', // Self-signed for development
          password: ''
        }
      }
    ]
    rewriteRuleSets: [
      {
        name: 'securityHeaders'
        properties: {
          rewriteRules: [
            {
              name: 'addSecurityHeaders'
              ruleSequence: 100
              conditions: []
              actionSet: {
                requestHeaderConfigurations: []
                responseHeaderConfigurations: [
                  {
                    headerName: 'Strict-Transport-Security'
                    headerValue: 'max-age=31536000; includeSubDomains'
                    action: 'Set'
                  }
                  {
                    headerName: 'X-Content-Type-Options'
                    headerValue: 'nosniff'
                    action: 'Set'
                  }
                  {
                    headerName: 'X-Frame-Options'
                    headerValue: 'DENY'
                    action: 'Set'
                  }
                  {
                    headerName: 'Content-Security-Policy'
                    headerValue: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;"
                    action: 'Set'
                  }
                  {
                    headerName: 'Referrer-Policy'
                    headerValue: 'strict-origin-when-cross-origin'
                    action: 'Set'
                  }
                  {
                    headerName: 'Permissions-Policy'
                    headerValue: 'geolocation=(), microphone=(), camera=()'
                    action: 'Set'
                  }
                ]
              }
            }
            {
              name: 'removeServerHeader'
              ruleSequence: 200
              conditions: []
              actionSet: {
                requestHeaderConfigurations: []
                responseHeaderConfigurations: [
                  {
                    headerName: 'Server'
                    headerValue: ''
                    action: 'Delete'
                  }
                  {
                    headerName: 'X-Powered-By'
                    headerValue: ''
                    action: 'Delete'
                  }
                ]
              }
            }
          ]
        }
      }
    ]
    globalConfiguration: {
      enableHttp2: true
      enableFips: false
    }
    autoscaleConfiguration: enableAutoscaling ? {
      minCapacity: minCapacity
      maxCapacity: maxCapacity
    } : null
  }
  dependsOn: enableWaf ? [wafPolicy] : []
}

// Diagnostic settings
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2023-09-01' = {
  name: '${appGatewayName}-diagnostics'
  scope: appGateway
  properties: {
    workspaceId: '' // Set from Log Analytics module
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

// Private Endpoint for App Gateway (if needed)
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = if (environment == 'production') {
  name: '${appGatewayName}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${appGatewayName}-pls'
        properties: {
          privateLinkServiceId: appGateway.id
          groupIds: [
            'frontendIPConfigurations'
          ]
          requestMessage: 'Auto-approved'
        }
      }
    ]
  }
}

output resourceId string = appGateway.id
output publicIpAddress string = publicIp.properties.ipAddress
output publicIpFqdn string = publicIp.properties.dnsSettings.fqdn
output wafPolicyId string = enableWaf ? wafPolicy.id : ''