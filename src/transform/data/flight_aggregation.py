from config.logger import Logger
from database.models import FlightSamples, FlightAggregates
from transform.db.repository import DbRepo
from transform.data.base_calcs import BaseCalcs

from sqlalchemy.orm import Session, Mapped
import polars as pl

from typing import Iterator
from datetime import datetime
from enum import Enum

log = Logger.create(__name__)


class FlightAggregator(BaseCalcs):
    '''
    Populates flight_aggregates table for efficiently querying flight data.
    '''
    def __init__(self) -> None:
        self.db = DbRepo()

    def aggregate_flight_samples(self) -> None:
        '''
        Gets new flight samples, summarizes them, and inserts them into the flight_aggregates table.
        '''
        log.info('summarizing flight samples')
        with Session(self.db.engine) as session:
            unmatched_flight_samples: Iterator[FlightSamples] = self.db.get_new_flight_samples(session)
        for flight_sample_date in unmatched_flight_samples:  # delete any dependent daily, weekly, monthly totals
            sample_date: datetime = flight_sample_date.sample_entry_date_utc
            flight_sample: pl.LazyFrame = self.db.filter_table_by_dates(
                FlightSamples, FlightSamples.sample_entry_date_utc, sample_date
                ).lazy()
            aggregate_row = self.summarize_flight_sample(flight_sample)
            with Session(self.db.engine) as session, session.begin():
                session.add(aggregate_row)
        log.info('summarized flight samples')

    def summarize_flight_sample(self, flight_sample: pl.LazyFrame) -> FlightAggregates:
        '''
        Summarizes a sample of flights into a single row of the flight_aggregates table.
        '''
        sample_date = flight_sample.select(
            pl.col(FlightSamples.sample_entry_date_utc.name)).first().collect().item()
        log.info(f'summarizing flight sample from: {sample_date}')
        agg_row = FlightAggregates()
        agg_row.sample_entry_date_utc = sample_date
        agg_row.number_of_flights = flight_sample.select(pl.count()).collect().item()
        agg_row.avg_altitude_ft = flight_sample.select(
            pl.col(FlightSamples.altitude_ft.name)).mean().collect().item()
        agg_row = self._calculate_max_min_columns(  # max altitude
            flight_sample, agg_row, FlightSamples.altitude_ft, FlightAggregates.max_altitude_ft,
            FlightAggregates.max_alt_aircraft_type, FlightAggregates.max_alt_aircraft_registration,
            FlightAggregates.max_alt_flight, self.AggregationType.MAX)
        agg_row = self._calculate_max_climb_rate(flight_sample, agg_row)
        agg_row = self._calculate_max_descent_rate(flight_sample, agg_row)
        agg_row.avg_ground_speed_knots = flight_sample.select(
            pl.col(FlightSamples.ground_speed_knots.name)).mean().collect().item()
        agg_row = self._calculate_max_min_columns(  # max ground speed
            flight_sample, agg_row, FlightSamples.ground_speed_knots,
            FlightAggregates.max_ground_speed_knots, FlightAggregates.max_speed_aircraft_type,
            FlightAggregates.max_speed_aircraft_registration, FlightAggregates.max_speed_flight,
            self.AggregationType.MAX)
        log.info(f'returning summarized sample as flight_aggregates row for: {sample_date}')
        return agg_row
    
    def _calculate_max_climb_rate(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        log.info('inserting flight with max climb rate')
        climb_rows = flight_sample.filter(pl.col(FlightSamples.alt_change_ft_per_min.name) > 0)
        agg_row = self._calculate_max_min_columns(
            climb_rows, agg_row, FlightSamples.alt_change_ft_per_min,
            FlightAggregates.max_climb_rate_ft_per_min, FlightAggregates.max_climb_aircraft_type,
            FlightAggregates.max_climb_aircraft_registration, FlightAggregates.max_climb_flight,
            self.AggregationType.MAX)
        log.info('inserting flight with max climb rate')
        return agg_row
    
    def _calculate_max_descent_rate(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        log.info('inserting flight with max descent rate')
        descent_rows = flight_sample.filter(pl.col(FlightSamples.alt_change_ft_per_min.name) < 0)
        agg_row = self._calculate_max_min_columns(
            descent_rows, agg_row, FlightSamples.alt_change_ft_per_min,
            FlightAggregates.max_descent_rate_ft_per_min, FlightAggregates.max_descent_aircraft_type,
            FlightAggregates.max_descent_aircraft_registration, FlightAggregates.max_descent_flight,
            self.AggregationType.MIN)
        if agg_row.max_descent_rate_ft_per_min:
            agg_row.max_descent_rate_ft_per_min *= -1
        log.info('inserted flight with max descent rate')
        return agg_row

    class AggregationType(Enum):
        MAX = 'max'
        MIN = 'min'

    def _calculate_max_min_columns(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates, search_column: Mapped,
            max_column: Mapped, aircraft_type_column: Mapped, registration_column: Mapped,
            flight_column: Mapped, aggregation_type: AggregationType
        ) -> FlightAggregates:
        '''
        Calculates the max value in a search column and records the 
        associated aircraft type, registration, and flight for a sample of flights.
        '''
        log.info(f'calculating {max_column.name} flight for sample')
        if aggregation_type == self.AggregationType.MAX:
            filtered_row = self._filter_to_max_row(flight_sample, search_column)
        elif aggregation_type == self.AggregationType.MIN:
            filtered_row = self._filter_to_min_row(flight_sample, search_column)
        if filtered_row.height == 1:
            setattr(agg_row, max_column.name, filtered_row.select(pl.col(search_column.name)).item())
            setattr(agg_row, aircraft_type_column.name,
                    filtered_row.select(pl.col(FlightSamples.aircraft_type.name)).item())
            setattr(agg_row, registration_column.name,
                    filtered_row.select(pl.col(FlightSamples.aircraft_registration.name)).item())
            setattr(agg_row, flight_column.name,
                    filtered_row.select(pl.col(FlightSamples.flight.name)).item())
        else:
            log.warning(f'no {max_column.name} value for sample; all values are null or filtered out')
        log.info(f'calculated {max_column.name} flight for sample')
        return agg_row
