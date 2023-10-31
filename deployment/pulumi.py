from config.settings import s
from config.env import Environs

import pulumi
from pulumi import ResourceOptions
import pulumi_docker as docker
from pulumi_azure_native.resources.v20220901 import ResourceGroup
import pulumi_azure_native.dbforpostgresql.v20230301preview as dbforpostgresql
import pulumi_azure_native.operationalinsights.v20221001 as operationalinsights
from pulumi_azure_native.operationalinsights.v20200801 import get_shared_keys_output
import pulumi_azure_native.app.v20230501 as app
import pulumi_azure_native.web.v20220901 as web
import pulumi_azure_native.insights.v20230101 as insights
from pulumi_azure_native.insights.v20210501preview import DiagnosticSetting, LogSettingsArgs
from pulumi_azure_native.insights.v20230315preview import (
    ScheduledQueryRule, ScheduledQueryRuleCriteriaArgs, ConditionArgs, ConditionOperator,
    TimeAggregation, ActionsArgs)

import os
from datetime import datetime

'''
Pulumi Azure Native API docs: https://www.pulumi.com/registry/packages/azure-native/api-docs/
Azure API Reference: https://learn.microsoft.com/en-us/azure/templates/
'''


env_var = Environs.environment_variable
environment = os.environ[env_var]
pulumi.export("Environment", environment)
docker_user = os.environ['DOCKER_USER']
docker_token = os.environ['DOCKER_TOKEN']


resource_group = ResourceGroup(
    f"{s.deploy.webapp_name}-resource-group",
    location=s.deploy.azure_region,
)


class DockerContainers:
    '''
    Manual builds:
    docker build -t fpvian/sky-viz-flights:latest -f ./deployment/flights.Dockerfile .
    docker build -t fpvian/sky-viz-transform:latest -f ./deployment/transform.Dockerfile .
    docker build -t fpvian/sky-viz-skyviz:latest -f ./deployment/skyviz.Dockerfile .
    docker push fpvian/sky-viz-flights:latest
    docker push fpvian/sky-viz-transform:latest
    docker push fpvian/sky-viz-skyviz:latest
    '''
    now = datetime.utcnow().strftime("%m.%d.%y-%H.%M.%S")
    flights_image_name = f"{docker_user}/sky-viz-flights:{environment}-{now}"
    transform_image_name = f"{docker_user}/sky-viz-transform:{environment}-{now}"
    skyviz_image_name = f"{docker_user}/sky-viz-skyviz:{environment}-{now}"

    flights_image = docker.Image(
        "flights-image",
        build=docker.DockerBuildArgs(
            context="..",
            dockerfile="flights.Dockerfile",
            platform='linux/amd64',
        ),
        image_name=flights_image_name,
        registry=docker.RegistryArgs(
            server=f'https://hub.docker.com/repositories/{docker_user}',
            username=docker_user,
            password=docker_token,
        ),
    )

    transform_image = docker.Image(
        "transform-image",
        build=docker.DockerBuildArgs(
            context="..",
            dockerfile="transform.Dockerfile",
            platform='linux/amd64',
        ),
        image_name=transform_image_name,
        registry=docker.RegistryArgs(
            server=f'https://hub.docker.com/repositories/{docker_user}',
            username=docker_user,
            password=docker_token,
        ),
    )

    skyviz_image = docker.Image(
        "skyviz-image",
        build=docker.DockerBuildArgs(
            context="..",
            dockerfile="skyviz.Dockerfile",
            platform='linux/amd64',
        ),
        image_name=skyviz_image_name,
        registry=docker.RegistryArgs(
            server=f'https://hub.docker.com/repositories/{docker_user}',
            username=docker_user,
            password=docker_token,
        ),
    )

    pulumi.export(
        "Docker images",
        [flights_image.image_name, transform_image.image_name, skyviz_image.image_name],
    )


class PostgresDB:
    postgres_server = dbforpostgresql.Server(
        s.db.server_name,
        opts=ResourceOptions(protect=s.deploy.protect_db),
        server_name=s.db.server_name,
        resource_group_name=resource_group.name,
        administrator_login=s.db.username,
        administrator_login_password=s.db.password,
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


class ContainerApps:
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

    flights_container_app = app.ContainerApp(
        "flights-container-app",
        environment_id=flights_container_app_environment.id,
        resource_group_name=resource_group.name,
        opts=ResourceOptions(
            depends_on=[
                PostgresDB.postgres_server,
                DockerContainers.flights_image,
            ],
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
                            name=env_var,
                            value=environment
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
                    image=DockerContainers.flights_image_name,
                    resources=app.ContainerResourcesArgs(
                        cpu=0.25,
                        memory="0.5Gi",
                    ),
                ),
            ],
            scale=app.ScaleArgs(min_replicas=1, max_replicas=1),
        ),
    )

    transform_container_app = app.ContainerApp(
        "transform-container-app",
        environment_id=flights_container_app_environment.id,
        resource_group_name=resource_group.name,
        opts=ResourceOptions(
            depends_on=[
                PostgresDB.postgres_server,
                DockerContainers.transform_image,
                flights_container_app,
            ],
            delete_before_replace=True,
        ),
        configuration=app.ConfigurationArgs(
            secrets=[db_username_secret, db_password_secret],
        ),
        template=app.TemplateArgs(
            containers=[
                app.ContainerArgs(
                    name="transform",
                    env=[
                        app.EnvironmentVarArgs(
                            name=env_var,
                            value=environment
                        ),
                        app.EnvironmentVarArgs(
                            name=s.db.username_env_var, secret_ref=db_username_secret.name),
                        app.EnvironmentVarArgs(
                            name=s.db.password_env_var, secret_ref=db_password_secret.name),
                    ],
                    image=DockerContainers.transform_image_name,
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
        s.deploy.webapp_name,
        name=s.deploy.webapp_name,
        opts=ResourceOptions(depends_on=[
            ContainerApps.flights_container_app,
            DockerContainers.skyviz_image,
        ]),
        resource_group_name=resource_group.name,
        site_config=web.SiteConfigArgs(
            linux_fx_version=f"DOCKER|{DockerContainers.skyviz_image_name}",
            always_on=True,
            health_check_path="/healthz",
            app_settings=[
                web.NameValuePairArgs(
                    name=env_var,
                    value=environment
                ),
                web.NameValuePairArgs(name=s.db.username_env_var, value=s.db.username),
                web.NameValuePairArgs(name=s.db.password_env_var, value=s.db.password),
            ],
        ),
        client_affinity_enabled=True,
        https_only=True,
        server_farm_id=skyviz_app_service_plan.id,
    )

    '''
    Commenting the certificate due to an issue between pulumi and the Azure API.
    The bind must be made in the first pulumi run.
    Then the certificate is created and the ssl state/thumbprint added to the bind in a subsequent run.
    This makes adding certificates a multi-step process and runs counter to the ethos of pulumi/IAC.
    After the stack is deployed, manually add the ip address to DNS records and issue certificates.
    More info: https://github.com/pulumi/pulumi-azure-native/issues/578

    skyviz_certificate = web.Certificate(
        "skyviz-certificate",
        canonical_name="www.skyviz.app",
        host_names=[skyviz_web_app.default_host_name, "www.skyviz.app", "skyviz.app"],
        opts=ResourceOptions(delete_before_replace=True),
        resource_group_name=resource_group.name,
        server_farm_id=skyviz_app_service_plan.id,
    )

    hostname bind args:
    # ssl_state=web.SslState.SNI_ENABLED,
    # thumbprint=skyviz_certificate.thumbprint,
    '''

    skyviz_hostname_bind = web.WebAppHostNameBinding(
        "skyviz-hostname-bind",
        host_name="www.skyviz.app",
        resource_group_name=resource_group.name,
        name=skyviz_web_app.name,
    )

    skyviz_root_hostname_bind = web.WebAppHostNameBinding(
        "skyviz-root-hostname-bind",
        opts=ResourceOptions(depends_on=skyviz_hostname_bind),
        host_name="skyviz.app",
        resource_group_name=resource_group.name,
        name=skyviz_web_app.name,
    )

    skyviz_diagnostic_setting = DiagnosticSetting(
        "skyviz-diagnostic-setting",
        resource_uri=skyviz_web_app.id,
        workspace_id=LogAnalytics.log_analytics_workspace.id,
        logs=[
            LogSettingsArgs(
                category="AppServiceConsoleLogs",
                enabled=True,
            ),
            LogSettingsArgs(
                category="AppServicePlatformLogs",
                enabled=True,
            ),
            LogSettingsArgs(
                category="AppServiceHTTPLogs",
                enabled=True,
            ),
        ],
    )

    pulumi.export("URL", skyviz_web_app.default_host_name.apply(lambda name: "https://" + name))


class Alerts:
    email_alerts = insights.ActionGroup(
        "email-alerts",
        group_short_name="skyviz-alert",
        resource_group_name=resource_group.name,
        location="global",
        email_receivers=[insights.EmailReceiverArgs(
            name="skyviz-domain-email",
            email_address="azure.alerts@skyviz.app",
        )]
    )

    if environment == "prod":
        '''
        Stack must be deployed before adding these alerts.
        Azure throws an error if there are no logs in the queried table.
        '''
        container_app_warnings = ScheduledQueryRule(
            "container-app-warnings",
            opts=ResourceOptions(depends_on=[ContainerApps.flights_container_app]),
            resource_group_name=resource_group.name,
            criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
                time_aggregation=TimeAggregation.COUNT,
                operator=ConditionOperator.GREATER_THAN,
                threshold=0,
                query='''ContainerAppConsoleLogs_CL
                        | where TimeGenerated >= ago(48h)
                        | where Log_s contains "[WARNING]" or Log_s contains "[ERROR]"
                        or Log_s contains "[CRITICAL]"''',
            ),]),
            evaluation_frequency="P1D",  # ISO 8601 duration format
            actions=ActionsArgs(action_groups=[email_alerts.id]),
            window_size="P2D",
            scopes=[LogAnalytics.log_analytics_workspace.id],
            enabled=True,
            severity=2,
        )

        container_app_health = ScheduledQueryRule(
            "container-app-health",
            opts=ResourceOptions(depends_on=[ContainerApps.flights_container_app]),
            resource_group_name=resource_group.name,
            criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
                time_aggregation=TimeAggregation.COUNT,
                operator=ConditionOperator.GREATER_THAN,
                threshold=0,
                query='''ContainerAppSystemLogs_CL
                        | where TimeGenerated >= ago(48h)
                        | where Type_s == "Error" or Type_s == "Critical"''',
            ),]),
            evaluation_frequency="P1D",  # ISO 8601 duration format
            actions=ActionsArgs(action_groups=[email_alerts.id]),
            window_size="P2D",
            scopes=[LogAnalytics.log_analytics_workspace.id],
            enabled=True,
            severity=1,
        )

    web_app_warnings = ScheduledQueryRule(
        "web-app-warnings",
        resource_group_name=resource_group.name,
        criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
            time_aggregation=TimeAggregation.COUNT,
            operator=ConditionOperator.GREATER_THAN,
            threshold=0,
            query='''AppServiceConsoleLogs
                    | where TimeGenerated >= ago(48h)
                    | where ResultDescription has "[WARNING]" or ResultDescription has "[ERROR]"
                    or ResultDescription has "[CRITICAL]"''',
        ),]),
        evaluation_frequency="P1D",  # ISO 8601 duration format
        actions=ActionsArgs(action_groups=[email_alerts.id]),
        window_size="P2D",
        scopes=[SkyVizApp.skyviz_web_app.id],
        enabled=True,
        severity=2,
    )

    web_app_health = ScheduledQueryRule(
        "web-app-health",
        resource_group_name=resource_group.name,
        criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
            time_aggregation=TimeAggregation.COUNT,
            operator=ConditionOperator.GREATER_THAN,
            threshold=0,
            query='''AppServiceHTTPLogs
                    | where TimeGenerated >= ago(48h)
                    | where ScStatus >= 500''',
        ),]),
        evaluation_frequency="P1D",  # ISO 8601 duration format
        actions=ActionsArgs(action_groups=[email_alerts.id]),
        window_size="P2D",
        scopes=[SkyVizApp.skyviz_web_app.id],
        enabled=True,
        severity=1,
    )

    web_app_activity = ScheduledQueryRule(
        "web-app-activity",
        resource_group_name=resource_group.name,
        criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
            time_aggregation=TimeAggregation.COUNT,
            operator=ConditionOperator.GREATER_THAN,
            threshold=0,
            query='''AppServiceHTTPLogs
                    | where TimeGenerated >= ago(24h)
                    | where UserAgent != "AlwaysOn"''',
        ),]),
        evaluation_frequency="P1D",  # ISO 8601 duration format
        actions=ActionsArgs(action_groups=[email_alerts.id]),
        window_size="P1D",
        scopes=[SkyVizApp.skyviz_web_app.id],
        enabled=True,
        severity=4,
    )

    log_analytics_limits = ScheduledQueryRule(
        "log-analytics-limits",
        resource_group_name=resource_group.name,
        criteria=ScheduledQueryRuleCriteriaArgs(all_of=[ConditionArgs(
            time_aggregation=TimeAggregation.COUNT,
            operator=ConditionOperator.GREATER_THAN,
            threshold=0,
            query='''_LogOperation
                    | where TimeGenerated >= ago(48h)
                    | where Category == "Ingestion"
                    | where Operation == "Data Collection" or Operation == "Ingestion rate"
                    | where Level == "Warning" or Level == "Error"''',
        ),]),
        evaluation_frequency="P1D",  # ISO 8601 duration format
        actions=ActionsArgs(action_groups=[email_alerts.id]),
        window_size="P2D",
        scopes=[LogAnalytics.log_analytics_workspace.id],
        enabled=True,
        severity=1,
    )
