/**
 * AvertaSaaS - Key Vault Secrets Module
 *
 * Creates secrets in Key Vault for application configuration.
 * Secrets are populated from deployment parameters.
 */

@description('Environment name')
param environment string

@description('Application name prefix')
param appName string

@description('Key Vault name')
param keyVaultName string

@description('PostgreSQL admin login')
@secure()
param pgAdminLogin string

@description('PostgreSQL admin password')
@secure()
param pgAdminPassword string

@description('Redis access key')
@secure()
param redisAccessKey string

@description('JWT secret key')
@secure()
param jwtSecretKey string

@description('JWT refresh secret key')
@secure()
param jwtRefreshSecretKey string

@description('SendGrid API key')
@secure()
param sendgridApiKey string

@description('SMTP password')
@secure()
param smtpPassword string

@description('Frontend URL')
param frontendUrl string

var keyVaultId = resourceId('Microsoft.KeyVault/vaults', keyVaultName)

// Database secret
resource secretDatabase 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVaultName
  name: 'database'
  properties: {
    value: json('{
      "username": "${pgAdminLogin}",
      "password": "${pgAdminPassword}",
      "host": "${appName}-postgres-${environment}.postgres.database.azure.com",
      "port": 5432,
      "dbname": "averta"
    }')
    contentType: 'application/json'
  }
}

// Redis secret
resource secretRedis 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVaultName
  name: 'redis'
  properties: {
    value: json('{
      "host": "${appName}-redis-${environment}.redis.cache.windows.net",
      "port": 6380,
      "password": "${redisAccessKey}",
      "ssl": true
    }')
    contentType: 'application/json'
  }
}

// MinIO/Storage secret
resource secretStorage 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVaultName
  name: 'storage'
  properties: {
    value: json('{
      "account_name": "${appName}storage${environment}",
      "account_key": "",
      "endpoint": "https://${appName}storage${environment}.blob.core.windows.net",
      "container": "averta-documents",
      "region": "${resourceGroup().location}"
    }')
    contentType: 'application/json'
  }
}

// JWT secrets
resource secretJwt 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVaultName
  name: 'jwt'
  properties: {
    value: json('{
      "secret_key": "${jwtSecretKey}",
      "refresh_secret_key": "${jwtRefreshSecretKey}",
      "algorithm": "HS256",
      "access_token_expire_minutes": 15,
      "refresh_token_expire_days": 7
    }')
    contentType: 'application/json'
  }
}

// SendGrid secret
resource secretSendgrid 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (sendgridApiKey != '') {
  parent: keyVaultName
  name: 'sendgrid'
  properties: {
    value: json('{
      "api_key": "${sendgridApiKey}",
      "from_email": "noreply@averta.com.br",
      "from_name": "Averta Auditoria"
    }')
    contentType: 'application/json'
  }
}

// SMTP secret
resource secretSmtp 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (smtpPassword != '') {
  parent: keyVaultName
  name: 'smtp'
  properties: {
    value: json('{
      "host": "smtp.sendgrid.net",
      "port": 587,
      "user": "apikey",
      "password": "${smtpPassword}",
      "from": "noreply@averta.com.br",
      "tls": true
    }')
    contentType: 'application/json'
  }
}

// App configuration secret
resource secretApp 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVaultName
  name: 'app'
  properties: {
    value: json('{
      "environment": "${environment}",
      "log_level": "${environment == "production" ? "INFO" : "DEBUG"}",
      "cors_origins": ["${frontendUrl}"],
      "frontend_url": "${frontendUrl}",
      "success_fee_percentage": 20.0
    }')
    contentType: 'application/json'
  }
}

// Certificate for TLS (if custom domain)
resource secretTlsCert 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (environment == 'production') {
  parent: keyVaultName
  name: 'tls-certificate'
  properties: {
    value: '' // Will be populated by ACM/Let's Encrypt integration
    contentType: 'application/x-pem-file'
  }
}

// Output secret URIs for reference
output databaseSecretUri string = 'https://${keyVaultName}.vault.azure.net/secrets/database'
output redisSecretUri string = 'https://${keyVaultName}.vault.azure.net/secrets/redis'
output storageSecretUri string = 'https://${keyVaultName}.vault.azure.net/secrets/storage'
output jwtSecretUri string = 'https://${keyVaultName}.vault.azure.net/secrets/jwt'
output sendgridSecretUri string = sendgridApiKey != '' ? 'https://${keyVaultName}.vault.azure.net/secrets/sendgrid' : ''
output smtpSecretUri string = smtpPassword != '' ? 'https://${keyVaultName}.vault.azure.net/secrets/smtp' : ''
output appSecretUri string = 'https://${keyVaultName}.vault.azure.net/secrets/app'