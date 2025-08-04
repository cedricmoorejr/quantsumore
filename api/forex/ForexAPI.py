# -*- coding: utf-8 -*-
#
## ╭────────────────────────────────────────────────────────────────────────────────────────────╮
## │  Library         : doydl's Finance API Client — quantsumore                                 │
## │                                                                                             │
## │                                                                                             │
## │  Description     : `quantsumore` is a comprehensive Python library designed to streamline   │
## │                    the process of accessing and analyzing real-time financial data across   │
## │                    various markets. It provides specialized API clients to fetch data       │
## │                    from multiple financial instruments, including:                          │
## │                      - Cryptocurrencies                                                     │
## │                      - Equities and Stock Markets                                           │
## │                      - Foreign Exchange (Forex)                                             │
## │                      - Treasury Instruments                                                 │
## │                      - Consumer Price Index (CPI) Metrics                                   │
## │                                                                                             │
## │                    The library offers a unified interface for retrieving diverse financial  │
## │                    data, enabling users to perform in-depth financial and technical         │
## │                    analysis. Whether you're developing trading algorithms, conducting       │
## │                    market research, or building financial dashboards, `quantsumore` serves  │
## │                    as a reliable and efficient tool in your data pipeline.                  │
## │                                                                                             │
## │                                                                                             │
## │  Key Features    : - Real-time data retrieval from multiple financial markets               │
## │                    - Support for various financial instruments and metrics                  │
## │                    - Simplified API clients for ease of integration                         │
## │                    - Designed for both personal and non-commercial use                      │
## │                                                                                             │
## │                                                                                             │
## │  Legal Disclaimer: `quantsumore` is an independent Python library and is not affiliated     │
## │                    with any financial institutions or data providers. Likewise, doydl       │
## │                    technologies is not affiliated with, endorsed by, or sponsored by any    │
## │                    government, corporate, or financial institutions. Users should verify    │
## │                    the accuracy of the data obtained and consult professional advice        │
## │                    before making investment decisions.                                      │
## │                                                                                             │
## │                                                                                             │
## │  Copyright       : © 2023–2025 by doydl technologies. All rights reserved.                  │
## │                                                                                             │
## │                                                                                             │
## │  License         : Licensed under the Apache License, Version 2.0 (the "License");          │
## │                    you may not use this file except in compliance with the License.         │
## │                    You may obtain a copy of the License at:                                 │
## │                                                                                             │
## │                        http://www.apache.org/licenses/LICENSE-2.0                           │
## │                                                                                             │
## │                    Unless required by applicable law or agreed to in writing, software      │
## │                    distributed under the License is distributed on an "AS IS" BASIS,        │
## │                    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or          │
## │                    implied. See the License for the specific language governing             │
## │                    permissions and limitations under the License.                           │
## ╰────────────────────────────────────────────────────────────────────────────────────────────╯
#

"""
ForexAPI — Unified Foreign Exchange Data Interface
══════════════════════════════════════════════════

Purpose
───────
    The `ForexAPI.py` module exposes a user-friendly, provider-agnostic interface for retrieving,
    analyzing, and converting foreign exchange (FX) data within the Quantsumore ecosystem.
    This module streamlines access to both historical and real-time FX market data, providing
    strict input validation, compliance with external provider requirements, and rich
    post-processing to standardized dataframes and dictionaries.

Key Capabilities
────────────────
- **Historical FX Rates:** Retrieve daily, time-series exchange rate data for all major currency pairs,
  with robust normalization of input pairs and date ranges, and provider-specific formatting handled internally.
- **Real-Time Interbank Rates:** Fetch live interbank market rates for any supported currency or basket of currencies,
  with fine-grained filtering (include/exclude by currency or region).
- **Bid/Ask and Market Spreads:** Instantly obtain current bid and ask prices and spreads for a curated set of major currency pairs,
  with rigorous pair validation.
- **Conversion and Quote:** Calculate the value of converting any amount from one currency to another,
  using the latest available market rates and returning a detailed breakdown.
- **Comprehensive Input Validation:** Currency codes, pairs, and dates are canonicalized and checked for
  support before any request is sent, guaranteeing API safety and clear error reporting.
- **Provider Obfuscation:** All upstream provider logic is abstracted away and referenced only via encoded,
  abstract labels for legal and vendor-neutrality reasons (see `prep.py` for full attribution policy).

Design Overview
───────────────
- **Single Entry Point:** Users only interact with the `APIClient`, which wraps an `forex_adapter` registry (from `prep.py`)
  that handles normalization and routing for all FX queries.
- **Centralized URL Construction:** All endpoint logic, batching, date formatting, and provider-specific quirks
  are routed through `forex_adapter.make(...)`, guaranteeing consistency and future extensibility.
- **Response Parsing and Data Normalization:** All responses are parsed, validated, and shaped into
  pandas DataFrames or Python dictionaries by the `fx` submodule, using strict, documented schema.
- **API Key and Session Management:** Fully supports secure API key management (set once globally, override per-call if needed).
- **Explicit Exception Hierarchy:** All failure cases—missing keys, invalid pairs, upstream errors—raise
  custom exceptions, with detailed context for diagnostics and robust fallback handling.

Typical Workflow
────────────────
1. **Install and Import:**
       from quantsumore.api import forex
2. **Initialize Client:**
       engine = forex.APIClient(forex.forex_adapter)
3. **Set API Key (if needed):**
       from quantsumore.api import APIKey
       APIKey("my-forex-api-key")
4. **Fetch Historical Rates:**
       df = engine.Historical(currency_pair="EURUSD", start="2023-01-01", end="2023-12-31")
5. **Get Real-Time Interbank Rates:**
       rates = engine.Interbank(currency_code="USD", include=["EUR", "JPY"])
6. **Bid/Ask Prices:**
       data = engine.BidAsk(currency_pair=["EURUSD", "USDJPY"])
# 7. **Live Quote Overview:**
#        data = engine.QuoteOverview(currency_pair="EURUSD")
8. **Currency Conversion:**
       conversion = engine.CurrencyConversion(currency_pair="EURUSD", conversion_amount=1000)

Supported Workflows
──────────────────
- **Batch and Single Queries:** Most methods accept single codes/pairs or lists for efficient batch retrieval.
- **Date Normalization:** Start/end dates are strictly parsed, normalized, and converted to provider-specific formats automatically.
- **Pair Validation:** Only valid, supported pairs/codes are accepted (detailed error messages if invalid).
- **Real-Time and Historical Data:** Live and historical endpoints are unified under a single interface, with branching handled internally.

Core Classes and Methods
────────────────────────
- **APIClient(adapter)**
    - `.Historical(currency_pair, start, end, api_key=None)`
        - Returns: `pandas.DataFrame` (with columns: Date, CurrencyPair, BaseCurrency, QuoteCurrency, Rate, InverseRate, QueriedAt)
    - `.Interbank(currency_code, include=None, exclude=None, api_key=None)`
        - Returns: `pandas.DataFrame` (live interbank rates, percent change, timestamp, etc.)
    - `.BidAsk(currency_pair, api_key=None)`
        - Returns: `pandas.DataFrame` (bid, ask, spread, last update, etc.)
    # - `.QuoteOverview(currency_pair, api_key=None)`
    #     - Returns: `dict` (key forex price points, e.g., bid, ask, open, close, high, low, change, etc.)
    - `.CurrencyConversion(currency_pair, conversion_amount=1, api_key=None)`
        - Returns: `dict` (all fields for conversion: base/quote code, names, both conversion directions, last update)

API Key Handling
────────────────
- **Automatic Storage:** Set your API key once with `APIKey("key")`; persists in singleton connection.
- **Per-Request Override:** Optionally pass `api_key` for a specific call.
- **Error Handling:** Raises `APIKeyRequiredError` if a key is required but not found.

Return Types and Data Structure
───────────────────────────────
- **Historical Rates:** pandas DataFrame (see `.Historical` doc for columns)
- **Interbank Rates:** pandas DataFrame (see `.Interbank` doc for columns)
- **Bid/Ask:** pandas DataFrame (see `.BidAsk` doc for columns)
# - **Quote Overview:** Python dict, keys depend on provider/market
# - **Conversion:** Python dict (see `.CurrencyConversion` doc)

Exception Handling
──────────────────
- `APIKeyRequiredError`: API key missing or invalid.
- `ValueError`: Malformed or missing input arguments (dates, codes, pairs).
- `FXNoDataError`, `FXDataUnavailableError`, `FXInterbankNoDataError`, `FXInterbankDataUnavailableError`:
    Various no-data/empty-response conditions.
- `LiveBidAskNoDataError`, `LiveBidAskUnavailableError`: Failed to fetch bid/ask spreads.
- `LiveQuoteValidationError`, `LiveQuoteUnavailableError`: HTML/response validation failed.
- `ConversionValidationError`, `ConversionUnavailableError`: Conversion logic failed or no data.

Internal Structure & Related Modules
────────────────────────────────────
- **prep.py:** Handles adapter/pair validation, provider obfuscation, and all normalization.
- **parse/fx.py:** Parses responses and shapes them for downstream consumption.
- **_http/connection.py:** Handles HTTP(S) connections, API key/session injection.

Data Attribution & Licensing Policy
───────────────────────────────────
- All provider-specific logic is routed through abstract, encoded labels only (see `prep.py`).
- No branding, domains, or direct attribution of upstream data providers is exposed at the API layer.
- Vendor neutrality and legal compliance are prioritized at every interface point.

Reference Table: Method Inputs/Outputs
──────────────────────────────────────
| Method            | Input(s)                                | Output            | Supports Multi? |
|-------------------|-----------------------------------------|-------------------|-----------------|
| Historical        | currency_pair(s), start, end            | DataFrame         | Yes             |
| Interbank         | currency_code(s), include/exclude       | DataFrame         | Yes             |
| BidAsk            | currency_pair(s)                        | DataFrame         | Yes             |
# | QuoteOverview   | currency_pair                           | dict              | No              |
| CurrencyConversion| currency_pair, conversion_amount        | dict              | No              |

Example
───────
    >>> from quantsumore.api import forex
    >>> engine = forex.APIClient(forex.forex_adapter)
    >>> df = engine.Historical(currency_pair="USDJPY", start="2024-01-01", end="2024-01-31")
    >>> print(df.head())

    >>> rates = engine.Interbank(currency_code="EUR", include=["USD", "JPY"])
    >>> print(rates)

    >>> data = engine.BidAsk(currency_pair=["EURUSD", "GBPUSD"])
    >>> print(data)

    # >>> overview = engine.QuoteOverview(currency_pair="EURUSD")
    # >>> print(overview)
    # 
    >>> conversion = engine.CurrencyConversion(currency_pair="EURUSD", conversion_amount=500)
    >>> print(conversion)
"""
# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..prep import forex_adapter
from .parse import fx
from ..._http.connection import Connection


__all__ = ['engine']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

class APIClient:
    def __init__(self, adapter):
        self.adapter = adapter  

    def Historical(self, currency_pair, start, end, api_key=None):
        """
        Retrieves historical exchange rates for one currency pair over a specified date range.

        This method fetches historical exchange rate data for currency pair identified by their ISO 4217 codes,
        within a given date range. The results include exchange rate information for each requested day.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        currency_pair : str
            The currency pair for which historical exchange rate data is requested. 
            The currency pair should be formatted as 'XXXYYY', where 'XXX' and 'YYY' are ISO 4217 currency codes 
            (e.g., 'EURUSD').
        start : str or datetime
            The start date for the historical data query. Accepts a string in 'YYYY-MM-DD' format or a datetime object.
        end : str or datetime
            The end date for the historical data query. Accepts a string in 'YYYY-MM-DD' format or a datetime object.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        dict or None
            A dictionary containing historical exchange rate data for the requested currency pair over the specified range,
            or None if no data could be retrieved.

        Raises:
        ------
        ValueError
            If either `start` or `end` date is not provided.
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """  	
        if all(x is None for x in [start, end]): 
            raise ValueError("Start and end dates must be provided for historical data requests.")  
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='historical', currency_pair=currency_pair, start=start, end=end)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )     
        if content:
            obj = fx.fx_historical(content)
            historical_data = obj.DATA()
            return historical_data
           
    # Notes:
    # -----
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.            
    def Interbank(self, base_currency, filter_currencies=None, ignore_currencies=None, api_key=None):
        """
        Retrieves live interbank exchange rates for specified currencies.

        Interbank rates represent market-average values derived from the midpoint between 'buy' and 'sell'
        rates across global currency markets.
        Optionally, you can specify which currencies to include in the results using
        `filter_currencies`, or ignore/exclude specific currencies using `ignore_currencies`.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        base_currency : str or list of str
            ISO 4217 code for the base/source currency (e.g., 'USD').
            If a list is provided, only the first item is used.
        filter_currencies : list of str, optional
            List of ISO 4217 currency codes to filter in the results.
            Defaults to all major currencies if not specified.
        ignore_currencies : list of str, optional
            List of ISO 4217 currency codes to ignore from the results.
            Defaults to none.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            Dictionary containing interbank rates and related metadata, or None if no data is returned.

        Raises:
        ------
        ConnectionError
            If the request to the external data source fails.
        ValueError
            If any provided currency codes are invalid or unsupported.
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='interbank', base_currency=base_currency, filter_currencies=filter_currencies, ignore_currencies=ignore_currencies)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )        
        if content:
            obj = fx.fx_interbank_rates(content)
            interbank_data = obj.DATA()
            return interbank_data
       
    # Notes:
    # -----
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.        
    def BidAsk(self, currency_pair, api_key=None):
        """
        Retrieves current bid and ask prices, along with the spread, for a specified currency pair.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        currency_pair : str
            The currency pair to retrieve, formatted as 'XXXYYY' (e.g., 'EURUSD').
            Only allowed pairs: 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'USDMXN',
            'USDINR', 'USDRUB', 'USDBRL'.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            Dictionary with bid price, ask price, bid-ask spread, and last update timestamp,
            or None if the data cannot be retrieved.

        Raises:
        ------
        InvalidCurrencyPairError
            If any provided currency pairs are invalid.
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """   	
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='bid_ask', currency_pair=currency_pair)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )     
        if content:
            obj = fx.live_bid_ask(content)
            bid_ask_data = obj.DATA()
            return bid_ask_data   

    # # Notes:
    # # -----
    # # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # # Returned results reflect the most current trading data available at the time of the request.  
    # def QuoteOverview(self, currency_pair, api_key=None):
    #     """
    #     Retrieves a live overview of forex trading data for a specified currency pair.
    # 
    #     API Key Usage:
    #     -------------
    #     If `api_key` is not provided, the method expects that an API key has already been set using:
    # 
    #         from quantsumore.api import APIKey
    #         APIKey("your-api-key-string")
    # 
    #     This securely stores your API key for all subsequent requests via a singleton connection manager.
    #     Passing `api_key` directly will override any stored key for this request.
    # 
    #     Parameters:
    #     ----------
    #     currency_pair : str
    #         The currency pair for which data is requested, formatted as 'XXXYYY' (e.g., 'EURUSD').
    #     api_key : str, optional
    #         The API key for authenticated requests. If not provided, an API key must have
    #         been previously set using `APIKey()`.
    # 
    #     Returns:
    #     -------
    #     dict or None
    #         Dictionary with key forex data points (e.g., 'currencyPair', 'openPrice', 'bidPrice'),
    #         or None if data is unavailable.
    # 
    #     Raises:
    #     ------
    #     APIKeyRequiredError
    #         If no API key is provided and none has been set using `APIKey()`.
    #     """  	
    #     make_method = getattr(self.adapter, 'make')
    #     url = make_method(query='current', currency_pair=currency_pair)
    #     html_content = Connection.Request(url=url, api_key=api_key, params=None, return_url=True)        
    #     if html_content:
    #         obj = fx.live_quote(html_content)
    #         quote_data = obj.DATA()
    #         return quote_data
    # 

    # Notes:
    # -----
    # - This method uses an internal API to fetch live data when needed. It also includes data manipulation functions
    #   to format the data appropriately for display or return.
    #
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.
    def CurrencyConversion(self, currency_pair, conversion_amount=1, api_key=None):
        """
        Converts a specified amount from one currency to another using the latest available conversion rates.

        This method retrieves current conversion rates and calculates the converted value for the requested amount.
        Data caching may be used to optimize performance.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        currency_pair : str
            The currency pair for conversion, formatted as 'XXXYYY' (e.g., 'EURUSD'), where 'XXX' is the base and 'YYY' is the target.
        conversion_amount : float, optional
            The amount of the base currency to convert. Defaults to 1.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            Dictionary with detailed conversion data (rates, original and converted amounts, last update timestamp),
            or None if no data is available.

        Examples:
        --------
        >>> engine.CurrencyConversion(currency_pair="EURUSD", conversion_amount=4)
        {'from_currency': 'Euro', 'from_currency_code': 'EUR', 'to_currency': 'U.S. Dollar', 'to_currency_code': 'USD',
         'conversion_rate_EUR_to_USD': 1.1126, 'conversion_rate_USD_to_EUR': 0.898796,
         'amount_converted_from_EUR': {'original_amount_EUR': 4, 'converted_amount_to_USD': 4.4504},
         'amount_converted_from_USD': {'original_amount_USD': 4, 'converted_amount_to_EUR': 3.595184},
         'last_updated': '2024-08-23 11:27:02'}

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='convert', currency_pair=currency_pair)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        ) 
        if content:
            obj = fx.conversion(content, conversion_amount=conversion_amount)
            conversion_data = obj.DATA()
            return conversion_data
       
    def __dir__(self):
        return [
            'Historical',
            'Interbank',
            'BidAsk',
            # 'QuoteOverview',            
            'CurrencyConversion',
        ]

          
engine = APIClient(forex_adapter)


def __dir__():
    return __all__
