from config.settings import s
from config.logger import Logger
from transform.data.flight_aggregation import FlightAggregator
from transform.db.repository import DbRepo

import asyncio

log = Logger.create(__name__)


def app_routine():
    FlightAggregator().aggregate_flight_samples()


async def main():
    log.info('starting transform app')
    db = DbRepo()
    db.upgrade_db()
    while True:
        try:
            app_routine(db)
        except Exception as e:
            log.error(e)
            if s.transform.suppress_errors is False:
                raise e
            log.info('restarting transform app')
        log.info(f'sleeping for {s.transform.wait_between_runs // 60} minutes')
        await asyncio.sleep(s.transform.wait_between_runs)


if __name__ == '__main__':
    asyncio.run(main())


'''
Control flow:

find sample dates with no matching daily aggregates
    if missing daily aggregates:
        summarize_daily_top_flights()

find sample dates with no matching weekly aggregates
    if missing weekly aggregates:
        summarize_weekly_monthly_top_flights()

find sample dates with no matching monthly aggregates
    if missing monthly aggregates:
        summarize_weekly_monthly_top_flights()
        count_flights_per_month()
'''