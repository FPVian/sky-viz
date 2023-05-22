from flights.config.env_settings import default, secrets


class Settings(secrets.Prod, default.Settings):

    class Logs(default.Settings.Logs):
        LOG_TO_CONSOLE: bool = False
        BYTES_PER_FILE: int = 100000000  # must be nonzero to rotate
        NUMBER_OF_BACKUPS: int = 1  # must be nonzero to rotate

    class Database(default.Settings.Database):
        DRIVER: str = 'postgres'
