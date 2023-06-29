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
    subnets=[network.SubnetArgs(
        name="public",
        address_prefix="10.0.1.0/24",
    )])

vm = build_vm(resource_group)

## install postgres

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