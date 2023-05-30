from flights.utils import logger
from flights.config.settings import s
from flights.data import extract

import asyncio

log = logger.create(__name__)


async def main():
    log.info('starting flights app')
    while True:
        try:
            extract.get_current_flights()
            await asyncio.sleep(5)
        except Exception as e:
            log.error(e)
            await asyncio.sleep(3600)
            log.info('restarting flights app')

if __name__ == '__main__':
    asyncio.run(main())
