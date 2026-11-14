output "api_url" { value = "https://${azurerm_container_app.api.latest_revision_fqdn}" }
output "resource_group" { value = azurerm_resource_group.main.name }
