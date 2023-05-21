from flights.utils import logger
from flights.data import extract

log = logger.create(__name__)


def main():
    log.info('starting flights app')
    extract.get_current_flights()


if __name__ == '__main__':
    main()
