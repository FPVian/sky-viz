from flights.api.clients.adsb_exchange import AdsbExchangeClient
import pandas as pd


def main():
    latitude = 39.8564  # Denver International Airport
    longitude = -104.6764  # Denver International Airport
    client = AdsbExchangeClient()
    response = client.get_aircraft_scatter(latitude, longitude)
    df = pd.json_normalize(response)
    df.to_excel('./scripts/flights.xlsx', index=False)


if __name__ == '__main__':
    main()
