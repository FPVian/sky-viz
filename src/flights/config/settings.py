from flights.config.env import Environs
from flights.config.groups.general import General, GeneralDev, GeneralProd
from flights.config.groups.db import Db, PostgresProd, PostgresDocker, SqliteDev, SqliteTest
from flights.config.groups.api import Api, ApiDev, ApiProd
from flights.config.groups.api_subgroup.adsb_exchange import (
    AdsbExchangeDev, AdsbExchangeProd, AdsbExchangeTest)
from flights.config.groups.logs import Logs, LogsDefault, LogsProd, LogsDebug

import hydra
from hydra import compose, initialize
from hydra.core.config_store import ConfigStore
from hydra.core.global_hydra import GlobalHydra
from omegaconf import MISSING, OmegaConf
from omegaconf.dictconfig import DictConfig

from typing import Optional, Any
from dataclasses import dataclass, field

'''
Add new groups and static configs to the Config class.
Add new dataclasses which belong to groups to the ConfigStore in register_config_options().
Don't forget to add groups and grouped classes to the appropriate defaults list(s) in env.py.

Structured configs in Hydra: https://hydra.cc/docs/tutorials/structured_config/intro/
'''


@dataclass
class Config:
    '''
    Top-level settings and setting groups to be set at runtime
    '''
    defaults: list[Any] = field(default_factory=Environs().defaults_list)
    hydra: Any = field(default_factory=lambda: {  # routes hydra output to .hydra folder
        'run': {'dir': '.hydra/outputs'},
        'sweep': {'dir': '.hydra/multirun'},
    })

    general: General = MISSING
    db: Db = MISSING
    api: Api = MISSING
    logs: Logs = MISSING


class Settings:
    '''
    Configures Hydra and then builds a new, independent/persistent, read-only OmegaConf object
    '''
    def register_config_options(self):
        GlobalHydra.instance().clear()  # must clear the current Hydra config, if any, before creation
        cs = ConfigStore.instance()
        cs.store(name='config', node=Config)
        cs.store(group='override hydra/hydra_logging', name='none', node='none')
        cs.store(group='override hydra/job_logging', name='none', node='none')
        cs.store(group='general', name='general_dev', node=GeneralDev)
        cs.store(group='general', name='general_prod', node=GeneralProd)
        cs.store(group='db', name='sqlite_dev', node=SqliteDev)
        cs.store(group='db', name='sqlite_test', node=SqliteTest)
        cs.store(group='db', name='postgres_prod', node=PostgresProd)
        cs.store(group='db', name='postgres_docker', node=PostgresDocker)
        cs.store(group='api', name='api_dev', node=ApiDev)
        cs.store(group='api', name='api_prod', node=ApiProd)
        cs.store(group='api/adsb_exchange', name='adsb_exchange_dev', node=AdsbExchangeDev)
        cs.store(group='api/adsb_exchange', name='adsb_exchange_prod', node=AdsbExchangeProd)
        cs.store(group='api/adsb_exchange', name='adsb_exchange_test', node=AdsbExchangeTest)
        cs.store(group='logs', name='logs_default', node=LogsDefault)
        cs.store(group='logs', name='logs_prod', node=LogsProd)
        cs.store(group='logs', name='logs_debug', node=LogsDebug)

    def build_config(self, overrides: Optional[list[str]] = None) -> DictConfig:
        self.register_config_options()
        initialize(version_base=None)
        cfg = compose(config_name='config', overrides=overrides)
        OmegaConf.set_readonly(cfg, True)  # prevents cfg from being modified at runtime
        OmegaConf.to_object(cfg)  # converts cfg to a dataclass, which forces MISSING values to be set
        return cfg


s = Settings().build_config()  # Global config object. Set the first time this file is imported.


@hydra.main(version_base=None, config_name='config')
def save_config_to_file(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))


if __name__ == '__main__':  # Prints and exports the current configuration to .hydra folder
    Settings().register_config_options()
    save_config_to_file()
