from copy import deepcopy

# Custom
from ..._http.connection import http_client
from ..prep import crypto_asset
from .parse import crypto


class APIClient:
    def __init__(self, asset):
        self.asset = asset

    def _make_request(self, url, headers_to_update=None):
        """ Note: http_client is a Singleton class instance."""
        http_client.update_base_url(url)
        original_headers = {}
        if headers_to_update:
            for header, value in headers_to_update.items():
                original_headers[header] = http_client.get_headers(header)
                http_client.update_header(header, value)
        response = http_client.make_request(params={})
        for header, original_value in original_headers.items():
            http_client.update_header(header, original_value)
        content = response["response"]
        return content if content else None

    def cLatest(self, slug, baseCurrencySymbol=None, quoteCurrencySymbol=None, cryptoExchange=None, limit=100, exchangeType="all"):
        """
        Fetches and returns the latest live cryptocurrency market data for a specified asset.

        This method retrieves the most recent live trading data for the specified cryptocurrency asset 
        identified by its slug (e.g., "bitcoin"). It allows filtering based on base and quote currency 
        symbols, the specific cryptocurrency exchange, the maximum number of results, and the type of exchange.
        The data is structured as a DataFrame containing various metrics related to live trading activity.

        Parameters:
        ----------
        slug : str
            The identifier for the cryptocurrency asset (e.g., "bitcoin").
        baseCurrencySymbol : str, optional
            The symbol of the base currency (e.g., "USD"). Defaults to None.
        quoteCurrencySymbol : str, optional
            The symbol of the quote currency (e.g., "JPY"). Defaults to None.
        cryptoExchange : str, optional
            The name of the cryptocurrency exchange to filter results (e.g., "binance"). Defaults to None.
        limit : int, optional
            The maximum number of results to return. Defaults to 100.
        exchangeType : str, optional
            The type of exchange to filter by (e.g., "all", "cex", "dex"). Defaults to "all".

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing the latest market data for the specified asset. The DataFrame includes 
            the following columns:
            - 'coinName': The full name of the cryptocurrency (e.g., "Bitcoin").
            - 'coinSymbol': The symbol of the cryptocurrency (e.g., "BTC").
            - 'exchangeName': The name of the exchange where the trading occurred.
            - 'marketPair': The market pair (e.g., "BTC/USD").
            - 'category': The category of the market pair.
            - 'baseSymbol': The base currency symbol (e.g., "USD").
            - 'quoteSymbol': The quote currency symbol (e.g., "JPY").
            - 'price': The current price of the asset in the specified quote currency.
            - 'volumeUsd': The trading volume in USD.
            - 'effectiveLiquidity': The liquidity of the market.
            - 'lastUpdated': The last updated time of the price data.
            - 'quote': The quote currency information.
            - 'volumeBase': The trading volume in the base currency.
            - 'volumeQuote': The trading volume in the quote currency.
            - 'feeType': The type of trading fee (e.g., "maker", "taker").
            - 'depthUsdNegativeTwo': Depth of the order book at -2% price deviation.
            - 'depthUsdPositiveTwo': Depth of the order book at +2% price deviation.
            - 'volumePercent': The percentage of total volume.
            - 'exchangeType': The type of exchange (e.g., "cex", "dex").
            - 'timeQueried': The time when the data was queried.

        Example:
        -------
        >>> engine = APIClient(asset=some_asset_instance)
        >>> latest_data = engine.cLatest(slug="bitcoin", baseCurrencySymbol="USD", quoteCurrencySymbol="JPY", cryptoExchange="binance", limit=100, exchangeType="all")
        >>> print(latest_data)
          coinName coinSymbol  ... exchangeType                      timeQueried
        0  Bitcoin        BTC  ...          cex 2024-08-27 14:57:32.938000+00:00

        [1 rows x 20 columns]
        """    	
        make_method = getattr(self.asset, 'make')
        url = make_method('live', slug, baseCurrencySymbol, quoteCurrencySymbol, limit, exchangeType)
        headers_to_update = {"Accept": "application/json"}
        content = self._make_request(url, headers_to_update=headers_to_update)
        if content:
            obj = crypto.live_quote(content, cryptoExchange=cryptoExchange)
            data = obj.DATA()
            return data

    def cHistorical(self, slug, start, end):
        """
        Fetches and returns historical cryptocurrency data for a specified asset within a given date range.

        This method retrieves historical price and trading data for the specified cryptocurrency asset 
        identified by its slug (e.g., "bitcoin"). The data is fetched for a date range defined by the 
        `start` and `end` parameters. The result is structured as a DataFrame containing various metrics 
        such as open, high, low, close prices, volume, market capitalization, and timestamps.

        Parameters:
        ----------
        slug : str
            The identifier for the cryptocurrency asset (e.g., "bitcoin").
        start : str
            The start date for the historical data retrieval in the format "YYYY-MM-DD".
        end : str
            The end date for the historical data retrieval in the format "YYYY-MM-DD".

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing the historical data for the specified asset. The DataFrame includes 
            the following columns:
            - 'symbol': The symbol of the cryptocurrency (e.g., "BTC").
            - 'name': The full name of the cryptocurrency.
            - 'timeOpen': The time the market opened for the given date range.
            - 'timeClose': The time the market closed for the given date range.
            - 'timeHigh': The time the highest price was recorded.
            - 'timeLow': The time the lowest price was recorded.
            - 'open': The opening price of the asset.
            - 'high': The highest price of the asset.
            - 'low': The lowest price of the asset.
            - 'close': The closing price of the asset.
            - 'volume': The trading volume during the specified period.
            - 'marketCap': The market capitalization during the specified period.
            - 'timestamp': The timestamp of the recorded data.
            - 'time_queried': The time when the data was queried.

        Example:
        -------
        >>> engine = APIClient(asset=some_asset_instance)
        >>> historical_data = engine.cHistorical(slug="bitcoin", start="2024-01-01", end="2024-01-10")
        >>> print(historical_data)
          symbol  ...                     time_queried
        0    BTC  ... 2024-08-27 14:52:44.320000+00:00
        1    BTC  ... 2024-08-27 14:52:44.320000+00:00
        2    BTC  ... 2024-08-27 14:52:44.320000+00:00
        3    BTC  ... 2024-08-27 14:52:44.320000+00:00
        4    BTC  ... 2024-08-27 14:52:44.320000+00:00
        5    BTC  ... 2024-08-27 14:52:44.320000+00:00
        6    BTC  ... 2024-08-27 14:52:44.320000+00:00
        7    BTC  ... 2024-08-27 14:52:44.320000+00:00
        8    BTC  ... 2024-08-27 14:52:44.320000+00:00

        [9 rows x 14 columns]
        """    	
        make_method = getattr(self.asset, 'make')
        url = make_method(query_type='historical', slug=slug, start=start, end=end)
        headers_to_update = {"Accept": "application/json"}
        content = self._make_request(url, headers_to_update=headers_to_update)
        if content:
            obj = crypto.crypto_historical(content)
            data = obj.DATA()
            return data
           
    def __dir__(self):
        return ['cHistorical','cLatest'] 



engine = APIClient(crypto_asset)

def __dir__():
    return ['engine']

__all__ = ['engine']


