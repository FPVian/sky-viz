from dataclasses import dataclass


@dataclass
class Logs():
    level: str = 'INFO'
    log_to_console: bool = True
    log_to_file: bool = True
    path: str = '${project_root}/logs'
    name: str = 'skyviz.log'
    file_path: str = '${.path}/${.name}'
    stream_format: str = '[%(levelname)s] %(module)-12s - %(message)s'
    file_format: str = (
        '[%(levelname)s] %(asctime)s %(name)-40s: %(funcName)-15s - %(message)-50s (pid:%(process)s)')
    bytes_per_file: int = 1000000  # must be nonzero to rotate
    number_of_backups: int = 1  # must be nonzero to rotate


@dataclass
class LogsDefault(Logs):
    pass


@dataclass
class LogsProd(Logs):
    level: str = 'INFO'
    log_to_file: bool = False


@dataclass
class LogsDebug(Logs):
    level: str = 'DEBUG'
    log_to_console: bool = False
    bytes_per_file: int = 100000000
