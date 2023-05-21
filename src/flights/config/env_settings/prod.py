from flights.config.env_settings import default, secrets


class Settings(secrets.Prod, default.Settings):

    class Logs(default.Settings.Logs):
        LOG_TO_CONSOLE = False
        BYTES_PER_FILE = 100000000  # must be nonzero to rotate
        NUMBER_OF_BACKUPS = 1  # must be nonzero to rotate

    class Database(default.Settings.Database):
        DRIVER = 'postgres'
