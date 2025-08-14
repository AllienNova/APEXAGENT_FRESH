@description('Environment name')
param environment string = 'production'

@description('Domain name for the CDN endpoint')
param domainName string

@description('Name of the storage account for static assets')
param storageAccountName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('SKU name for the CDN profile')
@allowed([
  'Standard_Microsoft'
  'Standard_Verizon'
  'Premium_Verizon'
  'Standard_Akamai'
  'Standard_ChinaCdn'
])
param cdnSku string = 'Standard_Microsoft'

@description('Origin path')
param originPath string = ''

var cdnProfileName = 'apexagent-cdn-${environment}'
var cdnEndpointName = replace(domainName, '.', '-')
var apiAppName = 'apexagent-api-${environment}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: true
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2021-08-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: [
        {
          allowedOrigins: [
            'https://${domainName}'
          ]
          allowedMethods: [
            'GET'
            'HEAD'
            'OPTIONS'
          ]
          allowedHeaders: [
            '*'
          ]
          exposedHeaders: [
            '*'
          ]
          maxAgeInSeconds: 3600
        }
      ]
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource staticWebsite 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-08-01' = {
  parent: blobService
  name: '$web'
  properties: {
    publicAccess: 'Blob'
  }
}

resource cdnProfile 'Microsoft.Cdn/profiles@2020-09-01' = {
  name: cdnProfileName
  location: location
  sku: {
    name: cdnSku
  }
  properties: {}
}

resource cdnEndpoint 'Microsoft.Cdn/profiles/endpoints@2020-09-01' = {
  parent: cdnProfile
  name: cdnEndpointName
  location: location
  properties: {
    originHostHeader: '${storageAccountName}.blob.core.windows.net'
    isHttpAllowed: false
    isHttpsAllowed: true
    queryStringCachingBehavior: 'IgnoreQueryString'
    contentTypesToCompress: [
      'application/javascript'
      'application/json'
      'application/xml'
      'text/css'
      'text/html'
      'text/javascript'
      'text/plain'
      'text/xml'
      'image/svg+xml'
    ]
    isCompressionEnabled: true
    optimizationType: 'GeneralWebDelivery'
    origins: [
      {
        name: 'storage-origin'
        properties: {
          hostName: '${storageAccountName}.blob.core.windows.net'
          originHostHeader: '${storageAccountName}.blob.core.windows.net'
          originPath: originPath
          httpPort: 80
          httpsPort: 443
          enabled: true
        }
      }
      {
        name: 'api-origin'
        properties: {
          hostName: '${apiAppName}.azurewebsites.net'
          originHostHeader: '${apiAppName}.azurewebsites.net'
          httpPort: 80
          httpsPort: 443
          enabled: true
        }
      }
    ]
    deliveryPolicy: {
      rules: [
        {
          name: 'EnforceHTTPS'
          order: 1
          conditions: [
            {
              name: 'RequestScheme'
              parameters: {
                matchValues: [
                  'HTTP'
                ]
                operator: 'Equal'
                negateCondition: false
                typeName: 'DeliveryRuleRequestSchemeConditionParameters'
              }
            }
          ]
          actions: [
            {
              name: 'UrlRedirect'
              parameters: {
                redirectType: 'Found'
                destinationProtocol: 'Https'
                typeName: 'DeliveryRuleUrlRedirectActionParameters'
              }
            }
          ]
        }
        {
          name: 'CacheStaticFiles'
          order: 2
          conditions: [
            {
              name: 'UrlPath'
              parameters: {
                operator: 'BeginsWith'
                matchValues: [
                  '/static/'
                  '/assets/'
                  '/images/'
                ]
                transforms: [
                  'Lowercase'
                ]
                typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
              }
            }
          ]
          actions: [
            {
              name: 'CacheExpiration'
              parameters: {
                cacheBehavior: 'Override'
                cacheType: 'All'
                cacheDuration: '7.00:00:00'
                typeName: 'DeliveryRuleCacheExpirationActionParameters'
              }
            }
          ]
        }
        {
          name: 'RouteAPIRequests'
          order: 3
          conditions: [
            {
              name: 'UrlPath'
              parameters: {
                operator: 'BeginsWith'
                matchValues: [
                  '/api/'
                ]
                transforms: [
                  'Lowercase'
                ]
                typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
              }
            }
          ]
          actions: [
            {
              name: 'RouteConfigurationOverride'
              parameters: {
                originGroupOverride: {
                  forwardingProtocol: 'HttpsOnly'
                  originGroupId: resourceId('Microsoft.Cdn/profiles/endpoints/originGroups', cdnProfileName, cdnEndpointName, 'api-origin-group')
                }
                typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
              }
            }
            {
              name: 'CacheExpiration'
              parameters: {
                cacheBehavior: 'BypassCache'
                typeName: 'DeliveryRuleCacheExpirationActionParameters'
              }
            }
          ]
        }
        {
          name: 'AddSecurityHeaders'
          order: 4
          conditions: []
          actions: [
            {
              name: 'ModifyResponseHeader'
              parameters: {
                headerAction: 'Append'
                headerName: 'Strict-Transport-Security'
                value: 'max-age=31536000; includeSubDomains; preload'
                typeName: 'DeliveryRuleHeaderActionParameters'
              }
            }
            {
              name: 'ModifyResponseHeader'
              parameters: {
                headerAction: 'Append'
                headerName: 'X-Content-Type-Options'
                value: 'nosniff'
                typeName: 'DeliveryRuleHeaderActionParameters'
              }
            }
            {
              name: 'ModifyResponseHeader'
              parameters: {
                headerAction: 'Append'
                headerName: 'X-Frame-Options'
                value: 'DENY'
                typeName: 'DeliveryRuleHeaderActionParameters'
              }
            }
            {
              name: 'ModifyResponseHeader'
              parameters: {
                headerAction: 'Append'
                headerName: 'X-XSS-Protection'
                value: '1; mode=block'
                typeName: 'DeliveryRuleHeaderActionParameters'
              }
            }
            {
              name: 'ModifyResponseHeader'
              parameters: {
                headerAction: 'Append'
                headerName: 'Referrer-Policy'
                value: 'strict-origin-when-cross-origin'
                typeName: 'DeliveryRuleHeaderActionParameters'
              }
            }
          ]
        }
      ]
    }
    defaultOriginGroup: {
      id: resourceId('Microsoft.Cdn/profiles/endpoints/originGroups', cdnProfileName, cdnEndpointName, 'storage-origin-group')
    }
  }
}

resource storageOriginGroup 'Microsoft.Cdn/profiles/endpoints/originGroups@2020-09-01' = {
  parent: cdnEndpoint
  name: 'storage-origin-group'
  properties: {
    origins: [
      {
        id: resourceId('Microsoft.Cdn/profiles/endpoints/origins', cdnProfileName, cdnEndpointName, 'storage-origin')
      }
    ]
    healthProbeSettings: {
      probePath: '/'
      probeRequestType: 'HEAD'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 100
    }
  }
}

resource apiOriginGroup 'Microsoft.Cdn/profiles/endpoints/originGroups@2020-09-01' = {
  parent: cdnEndpoint
  name: 'api-origin-group'
  properties: {
    origins: [
      {
        id: resourceId('Microsoft.Cdn/profiles/endpoints/origins', cdnProfileName, cdnEndpointName, 'api-origin')
      }
    ]
    healthProbeSettings: {
      probePath: '/health'
      probeRequestType: 'HEAD'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 100
    }
  }
}

resource cdnCustomDomain 'Microsoft.Cdn/profiles/endpoints/customDomains@2020-09-01' = {
  parent: cdnEndpoint
  name: replace(domainName, '.', '-')
  properties: {
    hostName: domainName
  }
}

resource frontDoorWAFPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2020-11-01' = if (cdnSku == 'Premium_Verizon') {
  name: 'apexagent-waf-policy-${environment}'
  location: 'global'
  properties: {
    policySettings: {
      enabledState: 'Enabled'
      mode: 'Prevention'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'DefaultRuleSet'
          ruleSetVersion: '1.0'
        }
        {
          ruleSetType: 'BotProtection'
          ruleSetVersion: '1.0'
        }
      ]
    }
  }
}

output cdnEndpointHostName string = cdnEndpoint.properties.hostName
output cdnEndpointUrl string = 'https://${cdnEndpoint.properties.hostName}'
output storageAccountName string = storageAccount.name
