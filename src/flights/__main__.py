from config.settings import s
from config.logger import Logger
from flights.api.adsb_exchange import AdsbExchangeClient
from flights.data.flight_samples_map import FlightSamplesMapper
from flights.db.repository import DbRepo

from sqlalchemy.orm import Session

import asyncio


log = Logger.create(__name__)


def app_routine(db: DbRepo):
    scatter_api_sample = AdsbExchangeClient().collect_usa_scatter_sample()
    flights_rows = FlightSamplesMapper().map_scatter_data(scatter_api_sample)
    with Session(db.engine) as session, session.begin():
        db.insert_rows(session, flights_rows)


async def main():
    log.info('starting flights app')
    db = DbRepo()
    db.upgrade_db()
    while True:
        try:
            app_routine(db)
        except Exception as e:
            log.error(e)
            if s.flights.suppress_errors is False:
                raise e
            log.info('restarting flights app')
        log.info(f'sleeping for {s.flights.wait_between_runs // 60} minutes')
        await asyncio.sleep(s.flights.wait_between_runs)


if __name__ == '__main__':
    asyncio.run(main())
