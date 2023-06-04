from dataclasses import dataclass


'''
Rename this to secrets.py to store passwords and keys for different environments
'''


@dataclass(frozen=True)
class PostgresSecrets:
    password: str = 'secret'
