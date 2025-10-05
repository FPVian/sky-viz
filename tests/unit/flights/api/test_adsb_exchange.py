from flights.api.adsb_exchange import AdsbExchangeClient
from config.settings import s

from unittest.mock import patch


class TestGetAircraftScatter:

    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_scatter_with_data(self, mock_base_api):
        '''
        Test that the get_aircraft_scatter() method returns the value of the 'ac' key.
        '''
        mock_base_api.return_value = {'ac': [{'alt_baro': 33975}]}
        aircraft = AdsbExchangeClient().get_aircraft_scatter(0, 0)
        assert aircraft == [{'alt_baro': 33975}]

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_scatter_no_data(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_scatter() method returns an empty list and
        logs a warning when the 'ac' key is None.
        '''
        mock_base_api.return_value = {'ac': None}
        aircraft = AdsbExchangeClient().get_aircraft_scatter(90, 45)
        assert aircraft == []
        mock_log.warning.assert_called_once

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_scatter_unsuccessful(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_scatter() method returns an empty list and
        logs a warning when there is no response.
        '''
        mock_base_api.return_value = None
        aircraft = AdsbExchangeClient().get_aircraft_scatter(0, 0)
        assert aircraft == []
        mock_log.warning.assert_called_once

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_scatter_unexpected_format(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_scatter() method returns an empty list and
        logs a warning when there is no 'ac' key.
        '''
        mock_base_api.return_value = {'foo': 'bar'}
        aircraft = AdsbExchangeClient().get_aircraft_scatter(0, 0)
        assert aircraft == []
        mock_log.warning.assert_called_once


class TestGetAircraftTraffic:

    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_traffic_with_data(self, mock_base_api):
        '''
        Test that the get_aircraft_traffic() method returns the value of the 'ac' key.
        '''
        mock_base_api.return_value = {'ac': [{'lat': '51.152251'}]}
        aircraft = AdsbExchangeClient().get_aircraft_traffic(0, 0)
        assert aircraft == [{'lat': '51.152251'}]

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_traffic_no_data(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_traffic() method returns an empty list and
        logs a warning when the 'ac' key is None.
        '''
        mock_base_api.return_value = {'ac': None}
        aircraft = AdsbExchangeClient().get_aircraft_traffic(90, 45)
        assert aircraft == []
        mock_log.warning.assert_called_once

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_traffic_unsuccessful(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_traffic() method returns an empty list and
        logs a warning when there is no response.
        '''
        mock_base_api.return_value = None
        aircraft = AdsbExchangeClient().get_aircraft_traffic(0, 0)
        assert aircraft == []
        mock_log.warning.assert_called_once

    @patch('flights.api.adsb_exchange.log')
    @patch('flights.api.adsb_exchange.RestApi.get')
    def test_get_aircraft_traffic_unexpected_format(self, mock_base_api, mock_log):
        '''
        Test that the get_aircraft_traffic() method returns an empty list and
        logs a warning when there is no 'ac' key.
        '''
        mock_base_api.return_value = {'foo': 'bar'}
        aircraft = AdsbExchangeClient().get_aircraft_traffic(0, 0)
        assert aircraft == []
        mock_log.warning.assert_called_once


class TestCollectUSAScatterSample:

    @patch('flights.api.adsb_exchange.AdsbExchangeClient.get_aircraft_scatter')
    def test_collect_usa_scatter_sample(self, mock_scatter):
        '''
        Test that the collect_usa_scatter_sample() method returns a list of aircraft scatter data.
        The mock return value is repeated for every coordinate pair in the usa_sample_coordinates list.
        '''
        mock_scatter.return_value = [{'foo': 'bar'}]
        aircraft = AdsbExchangeClient().collect_usa_scatter_sample()
        assert aircraft == [{'foo': 'bar'}] * len(s.api.adsb_exchange.usa_sample_coordinates)

    @patch('flights.api.adsb_exchange.AdsbExchangeClient.get_aircraft_scatter')
    def test_collect_usa_scatter_sample_no_data(self, mock_scatter):
        '''
        Test that the collect_usa_scatter_sample() method returns an empty list if there is no data.
        '''
        mock_scatter.return_value = []
        aircraft = AdsbExchangeClient().collect_usa_scatter_sample()
        assert aircraft == []
