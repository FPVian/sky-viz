from flights.config.settings import s
from flights.config.env import Environs

from pulumi import ResourceOptions
from pulumi_azure_native.resources.v20220901 import ResourceGroup
import pulumi_azure_native.dbforpostgresql.v20230301preview as dbforpostgresql
import pulumi_azure_native.operationalinsights.v20221001 as operationalinsights
from pulumi_azure_native.operationalinsights.v20200801 import get_shared_keys_output
from pulumi_azure_native.operationalinsights.v20190901 import Query
import pulumi_azure_native.app.v20230501 as app
import pulumi_azure_native.web.v20220901 as web

import os

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

    workspace_shared_keys = get_shared_keys_output(
        resource_group_name=resource_group.name,
        workspace_name=log_analytics_workspace.name,
    )

    # container_app_warnings_query = Query(
    #     "flights-warnings-query",
    #     query_pack_name="tbd",
    #     resource_group_name=resource_group.name,
    #     body='''
    #     ContainerAppConsoleLogs_CL
    #     | where TimeGenerated >= ago(48h)
    #     | where Log_s contains "[WARNING]" or Log_s contains "[ERROR]" or Log_s contains "[CRITICAL]"
    #     '''
    # )


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
    skyviz_app_service_plan = web.AppServicePlan(
        "skyviz-app-service-plan",
        resource_group_name=resource_group.name,
        kind="Linux",
        reserved=True,
        sku=web.SkuDescriptionArgs(
            name="B1",
            tier="Basic",
        ),
    )

    skyviz_web_app = web.WebApp(
        s.general.webapp_name,
        name=s.general.webapp_name,
        opts=ResourceOptions(depends_on=[FlightsContainer.flights_container_app]),
        resource_group_name=resource_group.name,
        site_config=web.SiteConfigArgs(
            linux_fx_version="DOCKER|fpvian/sky-viz-skyviz:latest",
            always_on=True,
            health_check_path="/healthz",
            app_settings=[
                web.NameValuePairArgs(
                    name=Environs.environment_variable,
                    value=os.environ[Environs.environment_variable]
                ),
                web.NameValuePairArgs(name=s.db.username_env_var, value=s.db.username),
                web.NameValuePairArgs(name=s.db.password_env_var, value=s.db.password),
            ],
        ),
        client_affinity_enabled=True,
        https_only=True,
        server_farm_id=skyviz_app_service_plan.id,
        # host_name_ssl_states=[web.HostNameSslStateArgs(
        #     host_type=web.HostType.REPOSITORY,
        #     name="skyviz.app",
        #     ssl_state=web.SslState.SNI_ENABLED,
        # #     # thumbprint="",
        # ),],
        # custom_domain_verification_id="",
    )


# skyviz_certificate = web.Certificate(
#     "skyviz-certificate",
#     resource_group_name=resource_group.name,
#     host_names=["skyviz.app", "www.skyviz.app",],
# )

# skyviz_certificate = web.WebAppPublicCertificate(
#     "skyviz-certificate",
#     resource_group_name=resource_group.name,
#     name=SkyVizApp.skyviz_web_app.name,
#     public_certificate_name="skyviz.app",
#     public_certificate_location=web.PublicCertificateLocation.CURRENT_USER_MY,
# )

skyviz_domain = web.WebAppHostNameBinding(
    "skyviz-domain",
    resource_group_name=resource_group.name,
    name=SkyVizApp.skyviz_web_app.name,
    host_name="skyviz.app",
    host_name_type=web.HostNameType.VERIFIED,
    ssl_state=web.SslState.SNI_ENABLED,
    thumbprint=skyviz_certificate.thumbprint,
    # ssl_state="Disabled",
)

# To Do
# logging
# certificates
# cicd
# delete old skyviz app
# alerts for postgres
# variable for docker image names

# app service logs -> application logging = file system, quota = 100 MB

# Add Custom Domains
# domain provider = all other domain services
# certificate = app service managed certificate
# type = SNI SSL
# domain = skyviz.app
# Repeat for www.skyviz.app

# continuous_deployment = on, (copy webhook url to docker repo)
