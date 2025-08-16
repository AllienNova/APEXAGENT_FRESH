resource "azurerm_resource_group" "apexagent" {
  name     = "apexagent-${var.environment}"
  location = var.location
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_container_registry" "acr" {
  name                = "apexagent${var.environment}acr"
  resource_group_name = azurerm_resource_group.apexagent.name
  location            = azurerm_resource_group.apexagent.location
  sku                 = "Standard"
  admin_enabled       = true
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "apexagent-${var.environment}-aks"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  dns_prefix          = "apexagent-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "default"
    node_count          = var.node_count
    vm_size             = var.vm_size
    os_disk_size_gb     = 30
    enable_auto_scaling = true
    min_count           = var.min_node_count
    max_count           = var.max_node_count
    vnet_subnet_id      = azurerm_subnet.aks_subnet.id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    network_policy    = "calico"
  }

  role_based_access_control_enabled = true

  addon_profile {
    oms_agent {
      enabled                    = true
      log_analytics_workspace_id = azurerm_log_analytics_workspace.workspace.id
    }
    
    azure_policy {
      enabled = true
    }
  }

  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_virtual_network" "vnet" {
  name                = "apexagent-${var.environment}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.apexagent.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "db_subnet" {
  name                 = "db-subnet"
  resource_group_name  = azurerm_resource_group.apexagent.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Sql"]
}

resource "azurerm_network_security_group" "nsg" {
  name                = "apexagent-${var.environment}-nsg"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  
  security_rule {
    name                       = "HTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_subnet_network_security_group_association" "aks_nsg_association" {
  subnet_id                 = azurerm_subnet.aks_subnet.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_log_analytics_workspace" "workspace" {
  name                = "apexagent-${var.environment}-workspace"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_postgresql_server" "postgres" {
  name                = "apexagent-${var.environment}-postgres"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name

  sku_name = "GP_Gen5_2"

  storage_mb                   = 5120
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = var.db_admin_username
  administrator_login_password = var.db_admin_password
  version                      = "11"
  ssl_enforcement_enabled      = true

  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_postgresql_database" "database" {
  name                = "apexagent"
  resource_group_name = azurerm_resource_group.apexagent.name
  server_name         = azurerm_postgresql_server.postgres.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}

resource "azurerm_postgresql_virtual_network_rule" "postgres_vnet_rule" {
  name                = "postgres-vnet-rule"
  resource_group_name = azurerm_resource_group.apexagent.name
  server_name         = azurerm_postgresql_server.postgres.name
  subnet_id           = azurerm_subnet.db_subnet.id
}

resource "azurerm_redis_cache" "redis" {
  name                = "apexagent-${var.environment}-redis"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  capacity            = 1
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {
    maxmemory_reserved = 50
    maxmemory_delta    = 50
    maxmemory_policy   = "allkeys-lru"
  }
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_key_vault" "keyvault" {
  name                        = "apexagent-${var.environment}-kv"
  location                    = azurerm_resource_group.apexagent.location
  resource_group_name         = azurerm_resource_group.apexagent.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get", "List", "Create", "Delete", "Update",
    ]

    secret_permissions = [
      "Get", "List", "Set", "Delete",
    ]

    certificate_permissions = [
      "Get", "List", "Create", "Delete",
    ]
  }
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

resource "azurerm_key_vault_secret" "db_connection" {
  name         = "database-url"
  value        = "postgresql://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_server.postgres.fqdn}:5432/apexagent"
  key_vault_id = azurerm_key_vault.keyvault.id
}

resource "azurerm_key_vault_secret" "redis_connection" {
  name         = "redis-url"
  value        = "redis://${azurerm_redis_cache.redis.hostname}:${azurerm_redis_cache.redis.ssl_port}"
  key_vault_id = azurerm_key_vault.keyvault.id
}

resource "azurerm_application_insights" "insights" {
  name                = "apexagent-${var.environment}-insights"
  location            = azurerm_resource_group.apexagent.location
  resource_group_name = azurerm_resource_group.apexagent.name
  application_type    = "web"
  
  tags = {
    Environment = var.environment
    Application = "ApexAgent"
  }
}

data "azurerm_client_config" "current" {}

output "kubernetes_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "host" {
  value     = azurerm_kubernetes_cluster.aks.kube_config.0.host
  sensitive = true
}

output "client_certificate" {
  value     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
  sensitive = true
}

output "client_key" {
  value     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
  sensitive = true
}

output "cluster_ca_certificate" {
  value     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
  sensitive = true
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "postgres_fqdn" {
  value = azurerm_postgresql_server.postgres.fqdn
}

output "redis_hostname" {
  value = azurerm_redis_cache.redis.hostname
}

output "application_insights_instrumentation_key" {
  value     = azurerm_application_insights.insights.instrumentation_key
  sensitive = true
}
