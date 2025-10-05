from dataclasses import dataclass


@dataclass
class Deploy:
    pass


@dataclass
class DeployProd(Deploy):
    azure_region: str = 'eastus'
    webapp_name: str = 'skyviz'
    protect_db: bool = True


@dataclass
class DeployStaging(Deploy):
    azure_region: str = 'eastus2'
    webapp_name: str = 'skyviz-staging'
    protect_db: bool = False
