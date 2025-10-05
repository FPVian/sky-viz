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
            {'flights': 'flights_dev'},
            {'transform': 'transform_dev'},
            {'skyviz': 'skyviz_dev'},
            {'db': 'sqlite_dev'},
            {'api': 'api_dev'},
            {'api/adsb_exchange': 'adsb_exchange_dev'},
            {'logs': 'logs_default'},
            {'deploy': 'deploy_default'},
        ],

        'dev': [
            '_self_',
            {'flights': 'flights_dev'},
            {'transform': 'transform_dev'},
            {'skyviz': 'skyviz_dev'},
            {'db': 'postgres_docker'},
            {'api': 'api_dev'},
            {'api/adsb_exchange': 'adsb_exchange_dev'},
            {'logs': 'logs_prod'},
            {'deploy': 'deploy_default'},
        ],

        'prod': [
            '_self_',
            {'flights': 'flights_prod'},
            {'transform': 'transform_prod'},
            {'skyviz': 'skyviz_prod'},
            {'db': 'postgres_prod'},
            {'api': 'api_prod'},
            {'api/adsb_exchange': 'adsb_exchange_prod'},
            {'logs': 'logs_prod'},
            {'deploy': 'deploy_prod'},
        ],

        'staging': [
            '_self_',
            {'flights': 'flights_staging'},
            {'transform': 'transform_staging'},
            {'skyviz': 'skyviz_staging'},
            {'db': 'postgres_staging'},
            {'api': 'api_prod'},
            {'api/adsb_exchange': 'adsb_exchange_staging'},
            {'logs': 'logs_prod'},
            {'deploy': 'deploy_staging'},
        ],

        'test': [
            '_self_',
            {'flights': 'flights_dev'},
            {'transform': 'transform_dev'},
            {'skyviz': 'skyviz_dev'},
            {'db': 'sqlite_test'},
            {'api': 'api_dev'},
            {'api/adsb_exchange': 'adsb_exchange_test'},
            {'logs': 'logs_default'},
            {'deploy': 'deploy_default'},
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
