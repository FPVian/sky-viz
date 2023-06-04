from flights.config.settings import s
from flights.utils import logger
from flights.data import transform

import asyncio

log = logger.create(__name__)


def app_routine():
    transform.get_current_flights()


async def main():
    log.info('starting flights app')
    while True:
        if s.general.suppress_errors:
            try:
                app_routine()
                await asyncio.sleep(1)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(60)
                log.info('restarting flights app')
        else:
            app_routine()
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
