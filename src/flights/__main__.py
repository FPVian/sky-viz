from flights.config.settings import s
from flights.utils import logger
from flights.api.clients.adsb_exchange import AdsbExchangeClient
from flights.data.mappers.flight_samples_map import FlightSamplesMapper
from flights.data.transforms.flight_samples_transform import FlightSamplesTransform
from flights.data.cleaners.flight_samples_clean import FlightSamplesCleaner
from flights.db.base_repo import BaseRepository

from hydra.utils import instantiate

import asyncio


log = logger.create(__name__)


def app_routine(db: BaseRepository):
    scatter_api_sample = AdsbExchangeClient().collect_usa_scatter_sample()
    clean_scatter_sample = FlightSamplesCleaner().clean_flight_sample(scatter_api_sample)
    flights_rows = FlightSamplesMapper().map_scatter_data(clean_scatter_sample)
    flights_transformed = FlightSamplesTransform().transform_flight_sample(flights_rows)
    db.insert_rows(flights_transformed)


async def main():
    log.info('starting flights app')
    db: BaseRepository = instantiate(s.db)
    db.upgrade_db()
    while True:
        if s.general.suppress_errors:
            try:
                app_routine(db)
                await asyncio.sleep(s.general.wait_between_runs)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(s.general.wait_between_runs)
                log.info('restarting flights app')
        else:
            app_routine(db)
            await asyncio.sleep(s.general.wait_between_runs)


if __name__ == '__main__':
    asyncio.run(main())
