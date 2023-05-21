from flights.config.env_settings import default, prod, dev

import os

s = default.Settings

env = None
try:  # set environment using ENV_VAR_NAME
    env = os.environ[s.ENV_VAR_NAME]
except KeyError:
    try:  # use .env file in src folder
        env = open(f'{s.PROJECT_ROOT}/.env').read().strip()
    except FileNotFoundError:
        with open(f'{s.Logs.PATH}/ERROR.log', 'w') as log:
            log.write("no environment variable '{}' found! using default settings".format(s.ENV_VAR_NAME))

if env == 'dev':
    s = dev.Settings
if env == 'prod':
    s = prod.Settings
