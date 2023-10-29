from flights.config.settings import s
from flights.utils.logger import Logger
from flights.api.clients.adsb_exchange import AdsbExchangeClient
from flights.data.flight_samples_map import FlightSamplesMapper
from flights.data.flight_samples_transform import FlightSamplesTransform
from flights.data.flight_samples_clean import FlightSamplesCleaner
from flights.db.base_repo import BaseRepository

from hydra.utils import instantiate
from sqlalchemy.orm import Session

import asyncio


log = Logger.create(__name__)


def app_routine(db: BaseRepository):
    scatter_api_sample = AdsbExchangeClient().collect_usa_scatter_sample()
    clean_scatter_sample = FlightSamplesCleaner().clean_flight_sample(scatter_api_sample)
    flights_rows = FlightSamplesMapper().map_scatter_data(clean_scatter_sample)
    flights_transformed = FlightSamplesTransform().transform_flight_sample(flights_rows)
    with Session(db.engine) as session, session.begin():
        db.insert_rows(session, flights_transformed)


async def main():
    log.info('starting flights app')
    db: BaseRepository = instantiate(s.db)
    db.upgrade_db()
    while True:
        try:
            app_routine(db)
        except Exception as e:
            log.error(e)
            if s.general.suppress_errors is False:
                raise e
            log.info('restarting flights app')
        log.info(f'sleeping for {s.general.wait_between_runs // 60} minutes')
        await asyncio.sleep(s.general.wait_between_runs)


if __name__ == '__main__':
    asyncio.run(main())
