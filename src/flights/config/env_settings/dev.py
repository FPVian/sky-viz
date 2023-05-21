from flights.config.env_settings import default, secrets


class Settings(secrets.Dev, default.Settings):

    class Logs(default.Settings.Logs):
        LEVEL = 'DEBUG'
        LOG_TO_CONSOLE = True
