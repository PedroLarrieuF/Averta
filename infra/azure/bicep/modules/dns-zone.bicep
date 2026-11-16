/**
 * AvertaSaaS - DNS Zone Module
 *
 * Creates Azure DNS Zone and records for custom domains.
 * Points to Application Gateway for API and Container Apps for frontend.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Custom domain name (e.g., averta.com.br)')
param customDomain string

@description('Application Gateway Public IP')
param appGatewayPublicIp string

@description('Frontend App FQDN (Container Apps or Static Web Apps)')
param frontendAppFqdn string = ''

@description('Tags')
param tags object

@description('TTL for DNS records (seconds)')
param ttl int = 300

// Only create DNS resources if custom domain is provided
resource dnsZone 'Microsoft.Network/dnszones@2023-09-01' = if (customDomain != '') {
  name: customDomain
  location: 'global'
  tags: tags
}

// A record for API (api.averta.com.br -> App Gateway)
resource aRecordApi 'Microsoft.Network/dnszones/A@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: 'api'
  properties: {
    TTL: ttl
    aRecords: [
      {
        ipv4Address: appGatewayPublicIp
      }
    ]
  }
}

// A record for App (app.averta.com.br -> Frontend)
resource aRecordApp 'Microsoft.Network/dnszones/A@2023-09-01' = if (customDomain != '' && frontendAppFqdn != '') {
  parent: dnsZone
  name: 'app'
  properties: {
    TTL: ttl
    aRecords: [
      {
        ipv4Address: appGatewayPublicIp // Or frontend IP if separate
      }
    ]
  }
}

// CNAME record for API (alternative to A record)
resource cnameRecordApi 'Microsoft.Network/dnszones/CNAME@2023-09-01' = if (customDomain != '' && appGatewayPublicIp == '') {
  parent: dnsZone
  name: 'api'
  properties: {
    TTL: ttl
    cnameRecord: {
      cname: '${appName}-appgw-${environment}.${resourceGroup().location}.cloudapp.azure.com'
    }
  }
}

// CNAME record for www
resource cnameRecordWww 'Microsoft.Network/dnszones/CNAME@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: 'www'
  properties: {
    TTL: ttl
    cnameRecord: {
      cname: 'app.${customDomain}'
    }
  }
}

// TXT record for domain verification (SPF, DKIM, etc.)
resource txtRecordVerification 'Microsoft.Network/dnszones/TXT@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: '_dmarc'
  properties: {
    TTL: ttl
    txtRecords: [
      {
        value: [
          'v=DMARC1; p=quarantine; rua=mailto:dmarc@${customDomain}'
        ]
      }
    ]
  }
}

// SPF record
resource txtRecordSpf 'Microsoft.Network/dnszones/TXT@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: '@'
  properties: {
    TTL: ttl
    txtRecords: [
      {
        value: [
          'v=spf1 include:sendgrid.net ~all'
        ]
      }
    ]
  }
}

// DKIM records (would be provided by SendGrid)
resource cnameRecordDkim1 'Microsoft.Network/dnszones/CNAME@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: 's1._domainkey'
  properties: {
    TTL: ttl
    cnameRecord: {
      cname: 's1.domainkey.uXXXXXX.wlXXX.sendgrid.net'
    }
  }
}

resource cnameRecordDkim2 'Microsoft.Network/dnszones/CNAME@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: 's2._domainkey'
  properties: {
    TTL: ttl
    cnameRecord: {
      cname: 's2.domainkey.uXXXXXX.wlXXX.sendgrid.net'
    }
  }
}

// CAA record for certificate authority authorization
resource caaRecord 'Microsoft.Network/dnszones/CAA@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: '@'
  properties: {
    TTL: ttl
    caaRecords: [
      {
        flags: 0
        tag: 'issue'
        value: 'letsencrypt.org'
      }
      {
        flags: 0
        tag: 'issue'
        value: 'digicert.com'
      }
      {
        flags: 0
        tag: 'issuewild'
        value: 'letsencrypt.org'
      }
      {
        flags: 128
        tag: 'iodef'
        value: 'mailto:security@${customDomain}'
      }
    ]
  }
}

// Health check for DNS
resource healthCheck 'Microsoft.Network/dnszones/healthCheck@2023-09-01' = if (customDomain != '') {
  parent: dnsZone
  name: 'health-check'
  properties: {
    protocol: 'Https'
    port: 443
    path: '/health'
    intervalInSeconds: 30
    timeoutInSeconds: 10
    unhealthyThreshold: 3
    healthyThreshold: 2
    enabled: true
  }
}

output dnsZoneName string = customDomain != '' ? dnsZone.name : ''
output dnsZoneId string = customDomain != '' ? dnsZone.id : ''
output nameServers array = customDomain != '' ? dnsZone.properties.nameServers : []