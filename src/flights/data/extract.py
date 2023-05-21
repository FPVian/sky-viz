from flights.utils import logger

log = logger.create(__name__)


def get_current_flights():
    log.info('starting get_current_flights')
    # do something
    log.info('get_current_flights complete!')


if __name__ == '__main__':
    get_current_flights()
