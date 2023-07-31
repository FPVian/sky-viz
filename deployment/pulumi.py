from flights.config.settings import s
from resources.vm import build_vm

import pulumi
from pulumi_azure_native import resources, network, compute, app

'''
Pulumi Azure Native API docs: https://www.pulumi.com/registry/packages/azure-native/api-docs/
'''


resource_group = resources.ResourceGroup("sky-viz", location='eastus')  # done


net = network.VirtualNetwork(
    "skyviz-vnet",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    subnets=[
        network.SubnetArgs(
            name="default",
            address_prefix="10.0.0.0/24",
            # service_endpoints=["Microsoft.KeyVault"],
        )])


vm = build_vm(resource_group)  # example


# Key Vault
# resource_group_name=resource_group.name,
# name="skyviz-key-vault",
# permission model = vault access policy
# enable public access = False
# Allow access from specific vnets -> skyviz-vnet -> default subnet
# create secrets: POSTGRES-PROD-ADMIN-USERNAME, POSTGRES-PROD-ADMIN-PASSWORD, ADSB-EXCHANGE-API-KEY-PROD
# create access policy (get secrets) for skyviz and flights managed identities


# Azure Database for PostgreSQL (need to change db server name in settings)
# Flexible Server
# resource_group_name=resource_group.name,
# server_name="flights-db-server",
# version = "15",
# workload_type = "Development",
# compute = database.ComputeStorageArgs(
#   tier="Burstable",
#   compute_size="Standard_B1ms",
#   storage_size_gb=32,
#   storage_auto_growth_enabled=True,
# ),
# authentication=database.ServerPropertiesForDefaultCreateArgs(
#   authentication_method="PostgreSQL Authentication Only",
#   administrator_login=os.environ.get('POSTGRES_PROD_ADMIN_USERNAME'),
#   administrator_login_password=os.environ.get('POSTGRES_PROD_ADMIN_PASSWORD'),
# ),
# network_connectivity=public_access,
# azure_access_enabled=True,


# App Service Plan - SkyViz
# resource_group_name=resource_group.name,
# name="skyviz-app-service-plan",
# pricing_plan = "Basic B1",

# Web App - SkyViz (delete before deploying)
# resource_group_name=resource_group.name,
# name="skyviz",
# publish="Docker Container",
# linux_plan = app_service_plan.id,
# image_source = app.ImageSourceArgs(
#   registry = "Docker Hub",
#   image = "fpvian/sky-viz-skyviz:latest",

# post-deploy:
# Add application settings:
# SKYVIZ_ENV=prod
# POSTGRES_PROD_ADMIN_USERNAME = @Microsoft.KeyVault(SecretUri=pg_user_secret.identifier)
# POSTGRES_PROD_ADMIN_PASSWORD = @Microsoft.KeyVault(SecretUri=pg_pass_secret.identifier)
# Always On = True
# ARR Affinity = True
# system assigned managed identity = enabled
# continuous_deployment = on, (copy webhook url to docker repo)
# vnet_integration = skyviz-vnet -> default subnet
# health check = enabled, path = /healthz
# app service logs -> application logging = file system, quota = 100 MB

# Add Custom Domains
# domain provider = all other domain services
# certificate = app service managed certificate
# type = SNI SSL
# domain = skyviz.app
# Repeat for www.skyviz.app


# App Service Plan - Flights
# resource_group_name=resource_group.name,
# name="flights-app-service-plan",
# pricing_plan = "Free F1",

# Web App - Flights
# resource_group_name=resource_group.name,
# name="flights",
# publish="Docker Container",
# linux_plan = app_service_plan.id,
# image_source = app.ImageSourceArgs(
#   registry = "Docker Hub",
#   image = "fpvian/sky-viz-flights:latest",
# enable_public_access = False,

# post-deploy:
# Add application settings:
# SKYVIZ_ENV=prod
# POSTGRES_PROD_ADMIN_USERNAME = @Microsoft.KeyVault(SecretUri=pg_user_secret.identifier)
# POSTGRES_PROD_ADMIN_PASSWORD = @Microsoft.KeyVault(SecretUri=pg_pass_secret.identifier)
# ADSB_EXCHANGE_API_KEY_PROD = @Microsoft.KeyVault(SecretUri=adsb_api_key_secret.identifier)
# Always On = True???
# system assigned managed identity = enabled
# continuous_deployment = on, (copy webhook url to docker repo)
# vnet_integration = skyviz-vnet -> default subnet
# app service logs -> application logging = file system, quota = 100 MB
