from copy import deepcopy
import time
import hashlib

# Custom
from ..._http.connection import http_client
from ..prep import fx_asset
from .parse import fx
from ...render.d import Table, Grid




def sci_notation(value):
    def is_scientific_notation(value):
        if isinstance(value, float):
            return 'e' in f"{value:.5e}".lower() 
        try:
            float(value) 
            return 'e' in str(value).lower() 
        except (ValueError, TypeError):
            return False
        
    # Find the order of magnitude (number of decimal places needed)
    if is_scientific_notation(value):
        if value != 0:
            magnitude = abs(int(f"{value:e}".split("e")[1]))
            return f"{value:.{magnitude}f}"
        else:
            return "0.0"
    else:
        return float(value)


class APIClient:
    def __init__(self, asset, cache_duration=60):
        self.asset = asset  
        self.data_cache = {}
        self.historical_cache = {}
        self.interbank_cache = {}        
        self.live_data_cache = {}
        self.cache_duration = cache_duration  # Duration in seconds for live data cache
        
    def _rename_keys(self, data, old_keys, new_keys):
        """ Renames specified keys in a dictionary."""
        if len(old_keys) != len(new_keys):
            raise ValueError("The list of old keys and new keys must have the same length.")
        new_data = deepcopy(data)
        for old_key, new_key in zip(old_keys, new_keys):
            if old_key in new_data:
                new_data[new_key] = new_data.pop(old_key)
            else:
                raise KeyError(f"The key '{old_key}' does not exist in the dictionary.")
        return new_data
       
    def _split_dataframe(self, df):
        data = [list(df[column]) for column in df.columns]
        return data

    def _flatten_currency_data(self, data):
        flattened_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                flattened_data.update(value)
            else:
                flattened_data[key] = value
        return flattened_data
       
    def _is_cache_valid(self, cache_key):
        if cache_key in self.live_data_cache:
            cache_entry = self.live_data_cache[cache_key]
            cached_time = cache_entry['timestamp']
            current_time = time.time()
            if (current_time - cached_time) < self.cache_duration:
                return True
        return False       
       
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

    def clear_cache(self, currency=None):
        if currency:
            self.data_cache.pop(currency, None)
            self.historical_cache = {key: val for key, val in self.historical_cache.items() if key[0] != currency}
            self.interbank_cache = {key: val for key, val in self.interbank_cache.items() if key[0] != currency}            
            self.live_data_cache = {key: val for key, val in self.live_data_cache.items() if not key.startswith(f"QuoteOverview:{currency}") and not key.startswith(f"CurrencyConversion:{currency}") and not key.startswith(f"BidAsk:{currency}")}
        else:
            self.data_cache.clear()
            self.historical_cache.clear()
            self.interbank_cache.clear()            
            self.live_data_cache.clear() 

    def fHistorical(self, currency_pair, start, end):
        """
        Retrieves historical exchange rates for a specified currency pair over a given date range.

        Parameters:
        - currency_pair (str): The currency pair for which historical data is requested, formatted as 'XXXYYY',
                               where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD').
        - start (str or datetime): The start date for the historical data query. Can be a string in 'YYYY-MM-DD' format
                                   or a datetime object.
        - end (str or datetime): The end date for the historical data query. Similar format to `start`.

        Returns:
        - dict or None: Returns a dictionary containing historical rates if successful. If verbose is True, the method
                        displays the data in a table format and returns None. Returns None if the data fetch fails or
                        if the date parameters are not provided correctly.

        Raises:
        - ValueError: If either `start` or `end` dates are not provided, indicating that valid dates are required for
                      the request.

        This method checks a local cache for the requested data using a specific key based on the currency pair and date
        range. If the cache hit occurs and the data is valid, it retrieves this data. If the cache is missed or outdated,
        it fetches fresh data using an API request, processes the data, and updates the cache accordingly.
        """    	
        if start is None or end is None:
            raise ValueError("Dates must be provided for historical data requests.")
            
        cache_key = (currency_pair, start, end)
        if cache_key in self.historical_cache:
            historical_data = self.historical_cache[cache_key]
            if verbose:
                rows = self._split_dataframe(historical_data)
                cols = list(historical_data.columns)
                db = Table(rows, custom_columns=cols)
                db.display()
                return
            return historical_data

        make_method = getattr(self.asset, 'make')
        url = make_method(query='historical', currency_pair=currency_pair, start=start, end=end)
        headers_to_update = {"Accept": "application/json"}
        content = self._make_request(url, headers_to_update=headers_to_update)
        if content:
            obj = fx.fx_historical(content)
            historical_data = obj.DATA()
            self.historical_cache[cache_key] = historical_data
            return historical_data
        return None       
       
    def Interbank(self, currency_code, include=None, exclude=None, verbose=True):
        """
        Retrieves interbank exchange rates for a specified currency and optionally filters the data based on included
        or excluded countries or regions. Interbank rates are derived from the midpoint between 'buy' and 'sell' rates
        from global currency markets and represent market averages, not transactional rates.

        Parameters:
        - currency_code (str): ISO 4217 currency code (e.g., 'USD', 'EUR') for which interbank rates are to be retrieved.
        - include (list, optional): List of country codes to specifically include in the results.
        - exclude (list, optional): List of country codes to exclude from the results.
        - verbose (bool): If True, displays the rates in a table format. If False, returns the rates as a dictionary.

        Returns:
        - dict or None: Returns a dictionary containing interbank rates if successful. If verbose is True, the method
                        displays the data in a table format and returns None. Returns None if the data fetch fails.

        Raises:
        - ConnectionError: If the request to the external data source fails.
        - ValueError: If the provided currency code is not supported.

        This method first checks a local cache for the requested data. If the cache is hit and is still valid, it uses this
        cached data. If the cache is missed or invalid, it makes a new API request, processes the received data, and updates
        the cache.
        """
        cache_key = (currency_code, include)
        if cache_key in self.interbank_cache:
            interbank_data = self.interbank_cache[cache_key]
            if verbose:
                rows = self._split_dataframe(interbank_data)
                cols = list(interbank_data.columns)
                db = Table(rows, custom_columns=cols)
                db.display()
                return
            return interbank_data

        make_method = getattr(self.asset, 'make')
        url = make_method(query='interbank', currency_code=currency_code, include=include, exclude=exclude)
        headers_to_update = {"Accept": "application/json"}
        content = self._make_request(url, headers_to_update=headers_to_update)
        if content:
            obj = fx.fx_interbank_rates(content)
            interbank_data = obj.DATA()
            self.interbank_cache[cache_key] = interbank_data

            if verbose:
                rows = self._split_dataframe(interbank_data)
                cols = list(interbank_data.columns)
                db = Table(rows, custom_columns=cols)
                db.display()
                return
            return interbank_data
        return None       
       
    def QuoteOverview(self, currency_pair, verbose=True):
        """
        Retrieves and displays an overview of forex trading data for a specified currency pair.

        This method first checks if the requested data is available in the cache. If the cache is valid,
        it retrieves the data from there. If not, it fetches fresh data using an API request, parses
        the response, and updates the cache.

        Parameters:
        - currency_pair (str): The currency pair for which data is requested, formatted as 'XXXYYY',
                               where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD').
        - verbose (bool): If True, displays the data in a detailed format using a data grid and modifies
                          the key names for readability. If False, returns the raw data dictionary.

        Returns:
        - dict: If verbose is False, returns a dictionary containing key forex data points such as
                'currencyPair', 'openPrice', 'bidPrice', etc. The dictionary keys will remain as received
                from the data source unless modified for display.
        - None: If verbose is True, displays the forex data in a grid format and does not return any value.
        """    	
        cache_key = f"QuoteOverview:{currency_pair}"
        if self._is_cache_valid(cache_key):
            quote_data = self.live_data_cache[cache_key]['data']
            chart_title = self.live_data_cache[cache_key]['title']
        else:
            make_method = getattr(self.asset, 'make')
            url = make_method(query='current', currency_pair=currency_pair)
            html_content = self._make_request(url)
            if html_content:
                obj = fx.live_quote(html_content)
                chart_title, quote_data = obj.DATA()
                self.live_data_cache[cache_key] = {
                    'data': quote_data,
                    'title': chart_title,
                    'timestamp': time.time()
                }
        if verbose:
            quote_data = self._rename_keys(
                quote_data,
                ['currencyPair', 'bidPrice', 'askPrice', 'bid-askSpread', 'dailyLow', 'openPrice', 'dailyHigh', 'lastTradedPrice', 'lastChangeInRate', 'previousClose', 'ytdHigh', 'ytdLow', 'stochastic%K', 'weightedAlpha', '5dayChange', '52weekRange', 'lastUpdated'],
                ['Currency Pair', 'Bid Price', 'Ask Price', 'Bid-Ask Spread', 'Low', 'Open', 'High', 'Last', 'Change in Rate', 'Previous Close', 'YTD High', 'YTD Low', 'Stochastic %K', 'Weighted Alpha', '5-Day Change', '52-Week Range', 'Last Updated']
            )
            dg = Grid(statistics=quote_data, Title=chart_title)
            dg.display()
            return
        return quote_data

    def BidAsk(self, currency_pair, verbose=True):
        """
        Retrieves and displays the current bid and ask prices along with the spread for a specified currency pair.

        This method checks the cache for the required data using a specific cache key. If the cached data is still
        valid, it retrieves the data from the cache. If the data is not in the cache or the cache is invalid, it fetches
        new data using an API request, processes the data, and updates the cache.

        Parameters:
        - currency_pair (str): The currency pair to retrieve the bid and ask data for, formatted as 'XXXYYY',
                               where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD').
        - verbose (bool): If True, displays the bid and ask data in a visually appealing grid format and modifies
                          the key names for better readability. If False, returns the data in a dictionary format.

        Returns:
        - dict: If verbose is False, returns a dictionary containing the currency pair, bid price, ask price,
                bid-ask spread, and the timestamp of the last update.
        - None: If verbose is True, the method displays the data in a grid format and does not return any value.
        """    	
        cache_key = f"BidAsk:{currency_pair}"
        if self._is_cache_valid(cache_key):
            bid_ask_data = self.live_data_cache[cache_key]['data']
            chart_title = self.live_data_cache[cache_key]['title']
        else:
            make_method = getattr(self.asset, 'make')
            url = make_method(query='current', currency_pair=currency_pair)
            html_content = self._make_request(url)
            if html_content:
                obj = fx.live_bid_ask(html_content)
                chart_title, bid_ask_data = obj.DATA()
                bid_ask_data['bid-askSpread'] = sci_notation(bid_ask_data['bid-askSpread'])
                
                self.live_data_cache[cache_key] = {
                    'data': bid_ask_data,
                    'title': chart_title,
                    'timestamp': time.time()
                }
        if verbose:
            bid_ask_data = self._rename_keys(
                bid_ask_data,
                ['currencyPair', 'bidPrice', 'askPrice', 'bid-askSpread', 'lastUpdated'],
                ['Currency Pair', 'Bid Price', 'Ask Price', 'Bid-Ask Spread', 'Last Updated']
            )
            dg = Grid(statistics=bid_ask_data, Title=chart_title)
            dg.display()
            return
        return bid_ask_data

    def CurrencyConversion(self, currency_pair, conversion_amount=1, verbose=True):
        """
        Converts a specified amount from one currency to another based on the latest conversion rates for the given
        currency pair.

        This method retrieves and displays conversion data between two currencies, handling data caching to optimize
        performance. If the data is not in cache or is outdated, it fetches new data, processes it, and updates the cache.

        Parameters:
        - currency_pair (str): The currency pair for conversion, formatted as 'XXXYYY' (e.g., 'EURUSD'),
                               where 'XXX' is the base currency and 'YYY' is the target currency.
        - conversion_amount (float, optional): The amount of the base currency to be converted. Defaults to 1.
        - verbose (bool): If True, displays detailed conversion information in a table format. If False, returns the
                          conversion data as a dictionary.

        Returns:
        - dict: A dictionary containing detailed conversion data, including rates and converted amounts. If verbose
                is True, displays the data in a table format and returns None.

        Examples:
        >>> engine.CurrencyConversion(currency_pair="EURUSD", conversion_amount=4, verbose=False)
        {'from_currency': 'Euro', 'from_currency_code': 'EUR', 'to_currency': 'U.S. Dollar', 'to_currency_code': 'USD',
         'conversion_rate_EUR_to_USD': 1.1126, 'conversion_rate_USD_to_EUR': 0.898796,
         'amount_converted_from_EUR': {'original_amount_EUR': 4, 'converted_amount_to_USD': 4.4504},
         'amount_converted_from_USD': {'original_amount_USD': 4, 'converted_amount_to_EUR': 3.595184},
         'last_updated': '2024-08-23 11:27:02'}

        Notes:
        - The data is cached to prevent excessive API requests and improve response times. The cache is checked at
          the beginning of the function, and if the requested data is available and valid, it is used directly.
        - This method uses an internal API to fetch live data when needed. It also includes data manipulation functions
          to format the data appropriately for display or return.
        """    	
        cache_key = f"CurrencyConversion:{currency_pair}:{conversion_amount}"
        if self._is_cache_valid(cache_key):
            conversion_data = self.live_data_cache[cache_key]['data']
        else:
            make_method = getattr(self.asset, 'make')
            url = make_method(query='convert', currency_pair=currency_pair)
            html_content = self._make_request(url)
            if html_content:
                obj = fx.conversion(html_content, conversion_amount=conversion_amount)
                conversion_data = obj.DATA()
                flat_conversion_data = self._flatten_currency_data(conversion_data)
                self.live_data_cache[cache_key] = {
                    'data': conversion_data,
                    'timestamp': time.time()
                }
        flat_conversion_data = self._flatten_currency_data(conversion_data)
        if verbose:
            db = Table(flat_conversion_data, custom_columns=list(flat_conversion_data.keys()))
            db.display()
            return
        return conversion_data
       
    def __dir__(self):
        return [
            'fHistorical',
            'Interbank',
            'QuoteOverview',
            'BidAsk',
            'CurrencyConversion',
            'clear_cache'
        ]

          

# Set cache duration to 20 seconds
engine = APIClient(fx_asset, cache_duration=0)


def __dir__():
    return ['engine']

__all__ = ['engine']
