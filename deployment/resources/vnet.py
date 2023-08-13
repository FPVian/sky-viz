import pulumi_azure_native.network.v20230401 as network


def create_vnet(resource_group):
    vnet = network.VirtualNetwork(
        "skyviz-vnet",
        resource_group_name=resource_group.name,
        address_space=network.AddressSpaceArgs(
            address_prefixes=["10.0.0.0/16"],
        ),
        subnets=[
            network.SubnetArgs(
                name="default",
                address_prefix="10.0.0.0/24",
                service_endpoints=[
                    network.ServiceEndpointPropertiesFormatArgs(service="Microsoft.KeyVault"),
                ],
            ),
        ]
    )
    return vnet
