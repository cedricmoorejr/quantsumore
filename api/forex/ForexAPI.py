# -*- coding: utf-8 -*-
#
# quantsumore - finance api client
# https://github.com/cedricmoorejr/quantsumore/
#
# Copyright 2023-2024 Cedric Moore Jr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from copy import deepcopy
import time

# Custom
from ..prep import fx_asset
from .parse import fx
from ..._http.response_utils import Request, validateHTMLResponse



class APIClient:
    def __init__(self, asset):
        self.asset = asset  

    def fHistorical(self, currency_pair, start, end):
        """
        Retrieves historical exchange rates for a specified currency pair over a given date range.

        Parameters:
        - currency_pair (str or list of str): The currency pair(s) for which historical data is requested. This can be a single
          currency pair formatted as 'XXXYYY', where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD'), or a list of
          such currency pairs.
          
        - start (str or datetime): The start date for the historical data query. Can be a string in 'YYYY-MM-DD' format
                                   or a datetime object.
        - end (str or datetime): The end date for the historical data query. Similar format to `start`.

        Returns:
        - dict or None: Returns a dictionary containing historical rates if successful. 

        Raises:
        - ValueError: If either `start` or `end` dates are not provided, indicating that valid dates are required for
                      the request.

        This method checks a local cache for the requested data using a specific key based on the currency pair and date
        range. If the cache hit occurs and the data is valid, it retrieves this data. If the cache is missed or outdated,
        it fetches fresh data using an API request, processes the data, and updates the cache accordingly.
        """    	
        if all(x is None for x in [start, end]): 
            raise ValueError("Start and end dates must be provided for historical data requests.")  

        make_method = getattr(self.asset, 'make')
        url = make_method(query='historical', currency_pair=currency_pair, start=start, end=end)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        if content:
            obj = fx.fx_historical(content)
            historical_data = obj.DATA()
            return historical_data
           
    def Interbank(self, currency_code, include=None, exclude=None):
        """
        Retrieves interbank exchange rates for a specified currency or multiple currencies and optionally filters the data based on included
        or excluded countries or regions. Interbank rates are derived from the midpoint between 'buy' and 'sell' rates
        from global currency markets and represent market averages, not transactional rates.

        Parameters:
        - currency_code (str or list of str): ISO 4217 currency code(s) (e.g., 'USD', 'EUR') for which interbank rates are to be retrieved.
          This can be a single currency code or a list of currency codes.
        - include (list, optional): List of country codes to specifically include in the results.
        - exclude (list, optional): List of country codes to exclude from the results.

        Returns:
        - dict or None: Returns a dictionary containing interbank rates if successful. If include and exclude are both None,
                all major currency rates will be returned.

        Raises:
        - ConnectionError: If the request to the external data source fails.
        - ValueError: If any of the provided currency codes are not supported.

        This method first checks a local cache for the requested data. If the cache is hit and is still valid, it uses this
        cached data. If the cache is missed or invalid, it makes a new API request, processes the received data, and updates
        the cache accordingly.
        """
        make_method = getattr(self.asset, 'make')
        url = make_method(query='interbank', currency_code=currency_code, include=include, exclude=exclude)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        if content:
            obj = fx.fx_interbank_rates(content)
            interbank_data = obj.DATA()
            return interbank_data
       
    def BidAsk(self, currency_pair):
        """
        Retrieves and displays the current bid and ask prices along with the spread for a specified currency pair.

        This method checks the cache for the required data using a specific cache key. If the cached data is still
        valid, it retrieves the data from the cache. If the data is not in the cache or the cache is invalid, it fetches
        new data using an API request, processes the data, and updates the cache.

        Parameters:
        - currency_pair (str or list of str): The currency pair to retrieve the bid and ask data for, formatted as 'XXXYYY',
                               where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD').

        Returns:
        - dict: Returns a dictionary containing the currency pair, bid price, ask price,
                bid-ask spread, and the timestamp of the last update.
        """    	
        allowed_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD',
            'AUDUSD', 'USDMXN', 'USDINR', 'USDRUB', 'USDBRL'
        ]
        if isinstance(currency_pair, str):
            currency_pair = [currency_pair]
        invalid_pairs = [pair for pair in currency_pair if pair not in allowed_pairs]
        if invalid_pairs:
            raise ValueError(f"Invalid currency pair(s) '{', '.join(invalid_pairs)}'. Allowed pairs are: {allowed_pairs}")
           
        make_method = getattr(self.asset, 'make')
        url = make_method(query='bid_ask', currency_pair=currency_pair)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        if content:
            obj = fx.live_bid_ask(content)
            bid_ask_data = obj.DATA()
            return bid_ask_data

    def QuoteOverview(self, currency_pair):
        """
        Retrieves and displays an overview of forex trading data for a specified currency pair.

        This method first checks if the requested data is available in the cache. If the cache is valid,
        it retrieves the data from there. If not, it fetches fresh data using an API request, parses
        the response, and updates the cache.

        Parameters:
        - currency_pair (str): The currency pair for which data is requested, formatted as 'XXXYYY',
                               where 'XXX' and 'YYY' are ISO 4217 currency codes (e.g., 'EURUSD').

        Returns:
        - dict: Returns a dictionary containing key forex data points such as
                'currencyPair', 'openPrice', 'bidPrice', etc. The dictionary keys will remain as received
                from the data source unless modified for display..
        """    	
        make_method = getattr(self.asset, 'make')
        url = make_method(query='current', currency_pair=currency_pair)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        html_check = validateHTMLResponse(html_content).currency(currency_pair=currency_pair)
        if html_check:
            obj = fx.live_quote(html_content)
            quote_data = obj.DATA()
            return quote_data

    def CurrencyConversion(self, currency_pair, conversion_amount=1):
        """
        Converts a specified amount from one currency to another based on the latest conversion rates for the given
        currency pair.

        This method retrieves and displays conversion data between two currencies, handling data caching to optimize
        performance. If the data is not in cache or is outdated, it fetches new data, processes it, and updates the cache.

        Parameters:
        - currency_pair (str): The currency pair for conversion, formatted as 'XXXYYY' (e.g., 'EURUSD'),
                               where 'XXX' is the base currency and 'YYY' is the target currency.
        - conversion_amount (float, optional): The amount of the base currency to be converted. Defaults to 1.
        
        Returns:
        - dict: A dictionary containing detailed conversion data, including rates and converted amounts. 

        Examples:
        >>> engine.CurrencyConversion(currency_pair="EURUSD", conversion_amount=4)
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
        make_method = getattr(self.asset, 'make')
        url = make_method(query='convert', currency_pair=currency_pair)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        html_check = validateHTMLResponse(html_content).currency(currency_pair=currency_pair)
        if html_check:
            obj = fx.conversion(html_content, conversion_amount=conversion_amount)
            conversion_data = obj.DATA()
            return conversion_data
       
    def __dir__(self):
        return [
            'fHistorical',
            'Interbank',
            'QuoteOverview',
            'BidAsk',
            'CurrencyConversion',
        ]

          

# Set cache duration to 20 seconds
engine = APIClient(fx_asset)


def __dir__():
    return ['engine']

__all__ = ['engine']
