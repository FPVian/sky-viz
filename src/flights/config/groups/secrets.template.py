from dataclasses import dataclass


'''
Rename this to secrets.py to store passwords and keys for different environments
'''


@dataclass(frozen=True)
class AdsbExchangeSecrets:
    api_key_dev: str = 'secret'
    api_key_prod: str = 'secret'


@dataclass(frozen=True)
class PostgresSecrets:
    password: str = 'secret'
