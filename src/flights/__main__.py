from flights.utils import logger
from flights.data import transform

import asyncio

log = logger.create(__name__)


async def main():
    log.info('starting flights app')
    while True:
        try:
            transform.get_current_flights()
            await asyncio.sleep(5)
        except Exception as e:
            log.error(e)
            await asyncio.sleep(60)
            log.info('restarting flights app')

if __name__ == '__main__':
    asyncio.run(main())
