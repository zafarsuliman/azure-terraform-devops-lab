locals {
  name = "taskapi-${var.environment}"
  tags = { application = "task-api", environment = var.environment, owner = var.owner, managed_by = "terraform" }
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-${local.name}"
  address_space       = ["10.20.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_subnet" "apps" {
  name                 = "snet-apps"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.20.0.0/23"]
  delegation {
    name = "container-apps"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_network_security_group" "apps" {
  name                = "nsg-${local.name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_subnet_network_security_group_association" "apps" {
  subnet_id                 = azurerm_subnet.apps.id
  network_security_group_id = azurerm_network_security_group.apps.id
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${local.name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

resource "azurerm_storage_account" "main" {
  name                             = "sttask${var.environment}${random_string.suffix.result}"
  resource_group_name              = azurerm_resource_group.main.name
  location                         = azurerm_resource_group.main.location
  account_tier                     = "Standard"
  account_replication_type         = "GRS"
  min_tls_version                  = "TLS1_2"
  public_network_access_enabled    = false
  shared_access_key_enabled        = true
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  tags                             = local.tags

  sas_policy {
    expiration_period = "01.00:00:00"
  }

  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }

}

resource "azurerm_storage_account_queue_properties" "main" {
  storage_account_id = azurerm_storage_account.main.id

  logging {
    delete                = true
    read                  = true
    write                 = true
    version               = "1.0"
    retention_policy_days = 7
  }
}

resource "azurerm_storage_share" "data" {
  name               = "task-data"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 1
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.name}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id   = azurerm_subnet.apps.id
  tags                       = local.tags
}

resource "azurerm_container_app_environment_storage" "data" {
  name                         = "task-data"
  container_app_environment_id = azurerm_container_app_environment.main.id
  account_name                 = azurerm_storage_account.main.name
  share_name                   = azurerm_storage_share.data.name
  access_key                   = azurerm_storage_account.main.primary_access_key
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app" "api" {
  name                         = "ca-${local.name}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.tags
  identity { type = "SystemAssigned" }
  template {
    min_replicas = 1
    max_replicas = 2
    container {
      name   = "api"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"
      env {
        name  = "APP_ENV"
        value = var.environment
      }
      env {
        name  = "DATABASE_PATH"
        value = "/data/tasks.db"
      }
      volume_mounts {
        name = "data"
        path = "/data"
      }
      liveness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"
      }
      readiness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/ready"
      }
    }
    volume {
      name         = "data"
      storage_name = azurerm_container_app_environment_storage.data.name
      storage_type = "AzureFile"
    }
  }
  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
