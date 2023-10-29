from transform.config.settings import s
from transform.utils.logger import Logger
from transform.data.aggregation import FlightsProcessor
from transform.db.base_repo import BaseRepository

from hydra.utils import instantiate
from sqlalchemy.orm import Session

import asyncio


log = Logger.create(__name__)


def app_routine(db: BaseRepository):
    with Session(db.engine) as session, session.begin():
        FlightsProcessor().summarize_flight_samples(session, db)


async def main():
    log.info('starting transform app')
    db: BaseRepository = instantiate(s.db)
    while True:
        try:
            app_routine(db)
        except Exception as e:
            log.error(e)
            if s.general.suppress_errors is False:
                raise e
            log.info('restarting transform app')
        log.info(f'sleeping for {s.general.wait_between_runs // 60} minutes')
        await asyncio.sleep(s.general.wait_between_runs)


if __name__ == '__main__':
    asyncio.run(main())
