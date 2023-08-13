from flights.config.settings import s
from flights.config.env import Environs

from pulumi import ResourceOptions
from pulumi_azure_native.resources.v20220901 import ResourceGroup
import pulumi_azure_native.dbforpostgresql.v20230301preview as dbforpostgresql
import pulumi_azure_native.app.v20230501 as app

import os

# import pulumi_azure_native.keyvault.v20230201 as keyvault

'''
Pulumi Azure Native API docs: https://www.pulumi.com/registry/packages/azure-native/api-docs/
Azure API Reference: https://learn.microsoft.com/en-us/azure/templates/
'''


resource_group = ResourceGroup("sky-viz", location='eastus')


postgres_server = dbforpostgresql.Server(
    s.db.server_name,
    opts=ResourceOptions(protect=True),
    server_name=s.db.server_name,
    resource_group_name=resource_group.name,
    administrator_login=s.db.admin_username,
    administrator_login_password=s.db.admin_password,
    sku=dbforpostgresql.SkuArgs(
        name="Standard_B1ms",
        tier=dbforpostgresql.SkuTier.BURSTABLE,
    ),
    storage=dbforpostgresql.StorageArgs(
        auto_grow=dbforpostgresql.StorageAutoGrow.ENABLED,
        storage_size_gb=32,
    ),
    version=dbforpostgresql.ServerVersion.SERVER_VERSION_15,
)

postgres_firewall_rule = dbforpostgresql.FirewallRule(
    "postgres-firewall-rule",
    resource_group_name=resource_group.name,
    server_name=postgres_server.name,
    start_ip_address="0.0.0.0",  # azure resources only
    end_ip_address="0.0.0.0",
)


flights_container_app = app.ContainerApp(  # missing Log Analytics Workspace
    "flights-container-app",
    resource_group_name=resource_group.name,
    opts=ResourceOptions(depends_on=[postgres_server]),  # replace_on_changes?
    configuration=app.ConfigurationArgs(
        secrets=[
            app.SecretArgs(name=s.db.username_env_var, value=s.db.username),
            app.SecretArgs(name=s.db.password_env_var, value=s.db.password),
            app.SecretArgs(name=s.api.adsb_exchange.api_key_env_var, value=s.api.adsb_exchange.api_key),
        ],
    ),
    template=app.TemplateArgs(
        containers=[
            app.ContainerArgs(
                env=[
                    app.EnvironmentVarArgs(
                        Environs.environment_variable, value=os.environ[Environs.environment_variable]),
                    app.EnvironmentVarArgs(
                        s.db.username_env_var, secret_ref=s.db.username_env_var),
                    app.EnvironmentVarArgs(
                        s.db.password_env_var, secret_ref=s.db.password_env_var),
                    app.EnvironmentVarArgs(
                        s.api.adsb_exchange.api_key_env_var,
                        secret_ref=s.api.adsb_exchange.api_key_env_var,
                    ),
                ],
                image="fpvian/sky-viz-flights:latest",
                resources=app.ContainerResourcesArgs(
                    cpu=0.25,
                    memory="0.5Gi",
                ),
            ),
        ],
    ),
)

# skyviz = delete_before_replace
# name = s.general.webapp_name

# delete old skyviz app