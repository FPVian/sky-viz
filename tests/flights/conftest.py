# from flights.config.settings import build_config

# from hydra.core.global_hydra import GlobalHydra

# import pytest
# import os
# from unittest.mock import patch


# @pytest.fixture
# @patch('flights.config.settings.s')
# def cfg(s):
#     '''
#     Builds config with test environment selected.
#     '''
#     GlobalHydra.instance().clear()
#     os.environ['SKYVIZ_ENV'] = 'test'
#     cfg = build_config()
#     s.return_value = cfg
#     return cfg
