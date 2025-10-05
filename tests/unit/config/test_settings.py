from config.settings import Settings
from config import settings
from config.env import Environs

import pytest
from hydra.utils import instantiate

import os
import subprocess


@pytest.mark.parametrize('environment', Environs.environments.keys())
def test_config_compilation(environment):
    '''
    Builds config with all available config options.
    If no error is raised, then all config groups and
    all base class attributes are implemented in each environment.
    If all tests fail, there is likely an issue with the current environment.
    Disable building s in settings.py and run tests again to narrow down the issue.
    '''
    os.environ[Environs.environment_variable] = environment
    conf = Settings().build_config()
    instantiate(conf.db)
    subprocess.run(['python', settings.__file__])
    del os.environ[Environs.environment_variable]
