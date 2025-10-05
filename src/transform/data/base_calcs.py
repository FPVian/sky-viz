from config.logger import Logger

from sqlalchemy.orm import Mapped
import polars as pl

log = Logger.create(__name__)


class BaseCalcs:
    '''
    Shared methods for transforming data.
    '''
    def _filter_to_max_row(self, lazyframe: pl.LazyFrame, column: Mapped) -> pl.DataFrame:
        '''
        Filters a lazyframe to a single row based with the the max value in a given column.
        '''
        log.info(f'filtering to row with max value in column: {column.name}')
        max_row = lazyframe.filter(pl.col(column.name) == pl.max(column.name)).first().collect()
        log.info(f'returning row with max value in column: {column.name}')
        return max_row

    def _filter_to_min_row(self, lazyframe: pl.LazyFrame, column: Mapped) -> pl.DataFrame:
        '''
        Filters a lazyframe to a single row based with the the min value in a given column.
        '''
        log.info(f'filtering to row with min value in column: {column.name}')
        min_row = lazyframe.filter(pl.col(column.name) == pl.min(column.name)).first().collect()
        log.info(f'returning row with min value in column: {column.name}')
        return min_row
