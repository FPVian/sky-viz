from dotenv import load_dotenv

from dataclasses import dataclass
import os

load_dotenv()


@dataclass
class Environs:
    '''
    Use this class to create different combinations of settings for different environments.
    New environments can be created by adding a new entry in the environments dict.
    
    New groups and grouped dataclasses should be added to the defaults list in the environments dict.
    Don't forget to add new groups and dataclasses in settings.py.

    The '__self__' string is a placeholder for the Config class.
    '_self_' at the top of a list indicates that the settings in the Config class can be overwritten.
    Matching dictionaries will always be merged.
    '''
    environment_variable: str = 'SKYVIZ_ENV'

    environments = {
        'default': [
            '_self_',
            {'general': 'general_dev'},
            {'db': 'sqlite_dev'},
            {'logs': 'logs_default'},
        ],

        'dev': [
            '_self_',
            {'general': 'general_dev'},
            {'db': 'postgres_docker'},
            {'logs': 'logs_prod'},
        ],

        'prod': [
            '_self_',
            {'general': 'general_prod'},
            {'db': 'postgres_docker'},
            {'logs': 'logs_prod'},
        ],

        'test': [
            '_self_',
            {'general': 'general_dev'},
            {'db': 'sqlite_test'},
            {'logs': 'logs_default'},
        ]
    }

    def defaults_list(self) -> list:
        defaults = self.environments['default']
        env = os.environ.get(self.environment_variable)
        if env:
            defaults = self.environments[env]
        hydra_overrides = [
            {'override hydra/hydra_logging': 'none'},
            {'override hydra/job_logging': 'none'},
        ]
        defaults.extend(hydra_overrides)
        return defaults
