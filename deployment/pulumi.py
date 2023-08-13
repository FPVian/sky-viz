from flights.config.settings import s
from flights.config.env import Environs

from pulumi import ResourceOptions
from pulumi_azure_native.resources.v20220901 import ResourceGroup
import pulumi_azure_native.dbforpostgresql.v20230301preview as dbforpostgresql
import pulumi_azure_native.operationalinsights.v20221001 as operationalinsights
from pulumi_azure_native.operationalinsights.v20200801 import get_shared_keys
import pulumi_azure_native.app.v20230501 as app

import os

# import pulumi_azure_native.keyvault.v20230201 as keyvault

'''
Pulumi Azure Native API docs: https://www.pulumi.com/registry/packages/azure-native/api-docs/
Azure API Reference: https://learn.microsoft.com/en-us/azure/templates/
'''


resource_group = ResourceGroup(s.general.webapp_name, location='eastus')


class PostgresDB:
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


class LogAnalytics:
    log_analytics_workspace = operationalinsights.Workspace(
        "skyviz-log-analytics",
        resource_group_name=resource_group.name,
        workspace_capping=operationalinsights.WorkspaceCappingArgs(daily_quota_gb=0.2),
    )

    workspace_shared_keys = get_shared_keys(
        resource_group_name=resource_group.name,
        workspace_name=log_analytics_workspace.name,
    )

    # flights_warnings_query = operationalinsights.


class FlightsContainer:
    flights_container_app_environment = app.ManagedEnvironment(
        "flights-container-app-environment",
        resource_group_name=resource_group.name,
        app_logs_configuration=app.AppLogsConfigurationArgs(
            destination="log-analytics",
            log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
                customer_id=LogAnalytics.log_analytics_workspace.customer_id,
                shared_key=LogAnalytics.workspace_shared_keys.primary_shared_key
            ),
        ),
    )

    db_username_secret = app.SecretArgs(name="db-username", value=s.db.username)
    db_password_secret = app.SecretArgs(name="db-password", value=s.db.password)
    adsb_exchange_api_key_secret = app.SecretArgs(
        name="adsb-exchange-api-key", value=s.api.adsb_exchange.api_key)

    flights_container_app = app.ContainerApp(  # replace_on_changes?
        "flights-container-app",
        environment_id=flights_container_app_environment.id,
        resource_group_name=resource_group.name,
        opts=ResourceOptions(
            depends_on=[PostgresDB.postgres_server],
            delete_before_replace=True,
        ),
        configuration=app.ConfigurationArgs(
            secrets=[db_username_secret, db_password_secret, adsb_exchange_api_key_secret],
        ),
        template=app.TemplateArgs(
            containers=[
                app.ContainerArgs(
                    name="flights",
                    env=[
                        app.EnvironmentVarArgs(
                            name=Environs.environment_variable,
                            value=os.environ[Environs.environment_variable]
                        ),
                        app.EnvironmentVarArgs(
                            name=s.db.username_env_var, secret_ref=db_username_secret.name),
                        app.EnvironmentVarArgs(
                            name=s.db.password_env_var, secret_ref=db_password_secret.name),
                        app.EnvironmentVarArgs(
                            name=s.api.adsb_exchange.api_key_env_var,
                            secret_ref=adsb_exchange_api_key_secret.name,
                        ),
                    ],
                    image="fpvian/sky-viz-flights:latest",
                    resources=app.ContainerResourcesArgs(
                        cpu=0.25,
                        memory="0.5Gi",
                    ),
                ),
            ],
            scale=app.ScaleArgs(min_replicas=1, max_replicas=1),
        ),
    )


class SkyVizApp:
    pass
# skyviz = depends on flights
# name = s.general.webapp_name
# delete old skyviz app
