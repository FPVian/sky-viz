from flights.config.settings import s

import pulumi
from pulumi_azure_native import resources

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("sky-viz", location='eastus')