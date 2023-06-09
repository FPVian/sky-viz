from dataclasses import dataclass


@dataclass
class Logs():
    level: str = 'INFO'
    log_to_console: bool = True
    path: str = '${general.project_root}/logs'
    name: str = 'flights.log'
    file_path: str = '${.path}/${.name}'
    stream_format: str = '[%(levelname)s] %(module)-12s - %(message)s'
    file_format: str = '[%(levelname)s] %(asctime)s %(name)-40s: %(funcName)-15s - %(message)-50s (pid:%(process)s)'
    bytes_per_file: int = 1000000  # must be nonzero to rotate
    number_of_backups: int = 1  # must be nonzero to rotate


@dataclass
class LogsDev(Logs):
    pass


@dataclass
class LogsProd(Logs):
    log_to_console: bool = False
    bytes_per_file: int = 100000000


@dataclass
class LogsDebug(Logs):
    level: str = 'DEBUG'
    log_to_console: bool = False
    bytes_per_file: int = 100000000
