param resourceGroup string = 'rg-avoulia-fr-dev'
param region string = 'francecentral'
param environment string = 'dev'
param appInsightsName string = 'ai-avoulia-${environment}'
param appInsightsSku string = 'standard'
param appInsightsRetention int = 30
param logAnalyticsName string = 'law-avoulia-${environment}'
param logAnalyticsSku string = 'PerGB2018'
param logAnalyticsRetention int = 30
param storageAccountName string = 'stavoulia${uniqueString(resourceGroup)}${environment}'
param storageSku string = 'Standard_LRS'
param storageKind string = 'StorageV2'
param tags object = {}

targetScope = 'resourceGroup'

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: logAnalyticsName
  location: region
  properties: {
    sku: {
      name: logAnalyticsSku
    }
    retentionInDays: logAnalyticsRetention
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: tags
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: region
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: appInsightsRetention
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
  tags: tags
}

// Storage Account (for mapping CSV + blob artifacts)
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: region
  kind: storageKind
  sku: {
    name: storageSku
  }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
  tags: tags
}

// Blob Service (container for mapping CSV)
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2021-06-01' = {
  parent: storageAccount
  name: 'default'
}

// Container for mapping_uc_hash.csv
resource mappingContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  parent: blobService
  name: 'parcours-mappings'
  properties: {
    publicAccess: 'None'
  }
}

// Outputs
output appInsightsKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output logAnalyticsId string = logAnalyticsWorkspace.id
output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
output storageAccountKey string = listKeys(storageAccount.id, '2021-06-01').keys[0].value
output containerName string = mappingContainer.name
