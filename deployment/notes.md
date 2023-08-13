# Resource Group
- name: "sky-viz"
- location: eastus


# Virtual Network
- name: "skyviz-vnet"
- add service enpoint for KeyVault in subnet


# Key Vault
resource_group_name=resource_group.name,
name="skyviz-key-vault",
permission model = vault access policy
enable public access = False
Allow access from specific vnets -> skyviz-vnet -> default subnet
create secrets: POSTGRES-PROD-ADMIN-USERNAME, POSTGRES-PROD-ADMIN-PASSWORD, ADSB-EXCHANGE-API-KEY-PROD
create access policy (get secrets) for skyviz and flights managed identities


# Azure Database for PostgreSQL (need to change db server name in settings after deploying via pulumi)
Flexible Server
resource_group_name=resource_group.name,
server_name="flights-db-server",
version = "15",
workload_type = "Development",
compute = database.ComputeStorageArgs(
  tier="Burstable",
  compute_size="Standard_B1ms",
  storage_size_gb=32,
  storage_auto_growth_enabled=True,
),
authentication=database.ServerPropertiesForDefaultCreateArgs(
  authentication_method="PostgreSQL Authentication Only",
  administrator_login=os.environ.get('POSTGRES_PROD_ADMIN_USERNAME'),
  administrator_login_password=os.environ.get('POSTGRES_PROD_ADMIN_PASSWORD'),
),
network_connectivity=public_access,
azure_access_enabled=True,


# App Service Plan - SkyViz
resource_group_name=resource_group.name,
name="skyviz-app-service-plan",
pricing_plan = "Basic B1",

# Web App - SkyViz (delete before deploying via pulumi)
resource_group_name=resource_group.name,
name="skyviz",
publish="Docker Container",
linux_plan = app_service_plan.id,
image_source = app.ImageSourceArgs(
  registry = "Docker Hub",
  image = "fpvian/sky-viz-skyviz:latest",

post-deploy:
Add application settings:
SKYVIZ_ENV=prod
POSTGRES_PROD_ADMIN_USERNAME = @Microsoft.KeyVault(SecretUri=pg_user_secret.identifier)
POSTGRES_PROD_ADMIN_PASSWORD = @Microsoft.KeyVault(SecretUri=pg_pass_secret.identifier)
Always On = True
ARR Affinity = True
system assigned managed identity = enabled
continuous_deployment = on, (copy webhook url to docker repo)
vnet_integration = skyviz-vnet -> default subnet
health check = enabled, path = /healthz
app service logs -> application logging = file system, quota = 100 MB

Add Custom Domains
domain provider = all other domain services
certificate = app service managed certificate
type = SNI SSL
domain = skyviz.app
Repeat for www.skyviz.app

# Log Analytics Workspace - Flights
name="flights-log-analytics-workspace"

# Container Apps Environment - Flights
name="flights-container-app-environment",
Logs Destination = Azure Log Analytics

# Web App - Flights
resource_group_name=resource_group.name,
name="flights",
image_source="Docker Hub or other registries",
image_and_tag = "fpvian/sky-viz-flights:latest",
Environment Variables:
  SKYVIZ_ENV=prod
  POSTGRES_PROD_ADMIN_USERNAME = @Microsoft.KeyVault(SecretUri=pg_user_secret.identifier)
  POSTGRES_PROD_ADMIN_PASSWORD = @Microsoft.KeyVault(SecretUri=pg_pass_secret.identifier)
  ADSB_EXCHANGE_API_KEY_PROD = @Microsoft.KeyVault(SecretUri=adsb_api_key_secret.identifier)

post-deploy:
setup warning/error level log alerts:
-----------------------------------------------
ContainerAppConsoleLogs_CL
| where TimeGenerated >= ago(48h)
| where ContainerName_s == "flights-1"
| where Log_s contains "[WARNING]" or Log_s contains "[ERROR]" or Log_s contains "[CRITICAL]"
-----------------------------------------------

??? system assigned managed identity = enabled
??? continuous_deployment = on, (copy webhook url to docker repo)
??? vnet_integration = skyviz-vnet -> default subnet

# To Do
ci/cd
lock name of database and web app since it is used in connections and github actions
version lock pulumi provider