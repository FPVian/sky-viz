from dataclasses import dataclass


@dataclass
class Deploy:
    pass


@dataclass
class DeployProd(Deploy):
    azure_region: str = 'eastus'
    webapp_name: str = 'skyviz'
    protect_db: bool = True
    # db_server_name: str = 'flights-db-server'
    # db_username_env_var: str = 'POSTGRES_USERNAME'
    # db_password_env_var: str = 'POSTGRES_PASSWORD'


@dataclass
class DeployStaging(Deploy):
    azure_region: str = 'eastus2'
    webapp_name: str = 'skyviz-staging'
    protect_db: bool = False
    # db_server_name: str = 'flights-db-server-staging'
    # db_username_env_var: str = 'POSTGRES_USERNAME'
    # db_password_env_var: str = 'POSTGRES_PASSWORD'
