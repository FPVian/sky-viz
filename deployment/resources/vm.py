from pulumi_azure_native import compute


def build_vm(resource_group):
    vm = compute.VirtualMachine(
        "flights-vm",
        resource_group_name=resource_group.name,

        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(id=network_iface.id),
            ],
        ),

        hardware_profile=compute.HardwareProfileArgs(
            vm_size=compute.VirtualMachineSizeTypes.STANDARD_B1S,
        ),
        
        os_profile=compute.OSProfileArgs(
            computer_name="hostname",
            admin_username=username,
            admin_password=password,
            custom_data=base64.b64encode(init_script.encode("ascii")).decode("ascii"),
            linux_configuration=compute.LinuxConfigurationArgs(
                disable_password_authentication=False,
            ),
        ),
        storage_profile=compute.StorageProfileArgs(
            os_disk=compute.OSDiskArgs(
                create_option=compute.DiskCreateOptionTypes.FROM_IMAGE,
                name="myosdisk1",
            ),
            image_reference=compute.ImageReferenceArgs(
                publisher="canonical",
                offer="UbuntuServer",
                sku="22.04-LTS",
                version="latest",
            ),
        ))
    return vm
