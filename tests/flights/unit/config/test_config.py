from flights.config.settings import build_config
from flights.config.env import Environs

from hydra.core.global_hydra import GlobalHydra

import pytest
import os


@pytest.mark.parametrize('environment', Environs.environments.keys())
def test_config_compilation(environment):
    '''
    Builds config with all available config options.
    If no error is raised, then all config groups and all base class attributes are implemented in each environment.
    If all tests fail, there is likely an issue with the current environment.
    Disable building s in settings.py and run tests again to narrow down the issue.
    '''
    
    GlobalHydra.instance().clear()
    os.environ[Environs.environment_variable] = environment
    build_config()
