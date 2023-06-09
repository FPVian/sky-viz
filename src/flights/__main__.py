from flights.config.settings import s
from flights.utils import logger
from flights.data.mappers. flights_model_map import FlightsMapper
from flights.api.clients.adsb_exchange import AdsbExchangeClient
from flights.db.base_repo import BaseRepository

from hydra.utils import instantiate
import asyncio

log = logger.create(__name__)


def app_routine(db: BaseRepository):
    scatter_api_response = AdsbExchangeClient().get_aircraft_scatter()  # take_sample()
    flights_rows = FlightsMapper().map_scatter_data(scatter_api_response)
    # dedupe()
    db.insert_rows(flights_rows)


async def main():
    log.info('starting flights app')
    db: BaseRepository = instantiate(s.db)
    db.upgrade_db()
    while True:
        if s.general.suppress_errors:
            try:
                app_routine(db)
                await asyncio.sleep(1)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(60)
                log.info('restarting flights app')
        else:
            app_routine(db)
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
