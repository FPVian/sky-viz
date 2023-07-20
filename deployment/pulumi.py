from flights.config.settings import s
from resources.vm import build_vm

import pulumi
from pulumi_azure_native import resources, network, compute, app

'''
Pulumi Azure Native API docs: https://www.pulumi.com/registry/packages/azure-native/api-docs/
'''

## Key Vault

resource_group = resources.ResourceGroup("sky-viz", location='eastus')  # done

net = network.VirtualNetwork(
    "skyviz-network",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    subnets=[
        network.SubnetArgs(
            name="public",
            address_prefix="10.0.1.0/24",
        ),
        network.SubnetArgs(
            name="private",
            address_prefix="10.0.1.0/24",
        )])

vm = build_vm(resource_group)


# Azure Database for PostgreSQL
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
#   authentication_method="PostgreSQL and Azure Active Directory authentication",
#   administrator_login=os.environ.get('POSTGRES_PROD_ADMIN_USERNAME'),
#   administrator_login_password=os.environ.get('POSTGRES_PROD_ADMIN_PASSWORD'),
#   azure_admin="email@address",
# ),
# network_connectivity=private_access,
# vnet = net,
# subnet_name = private,
# private_dns_zone = network.PrivateDnsZone("flights-db-server.private.postgres.database.azure.com"),



## Azure Container Registry?

## Static IP
public_ip = network.PublicIPAddress(
    "skyviz.app-ip",
    resource_group_name=resource_group.name,
    public_ip_allocation_method=network.IPAllocationMethod.STATIC)


## Container App - certificate
container_app = app.ContainerApp("app",
    resource_group_name=resource_group.name,
    managed_environment_id=managed_env.id,
    configuration=app.ConfigurationArgs(
        ingress=app.IngressArgs(
            external=True,
            target_port=80
        ),
        registries=[
            app.RegistryCredentialsArgs(
                server=registry.login_server,
                username=admin_username,
                password_secret_ref="pwd")
        ],
        secrets=[
            app.SecretArgs(
                name="pwd",
                value=admin_password)
        ],
    ),
    template=app.TemplateArgs(
        containers = [
            app.ContainerArgs(
                name="myapp",
                image=my_image.image_name)
        ]))