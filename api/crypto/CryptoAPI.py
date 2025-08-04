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
CryptoAPI — Unified Cryptocurrency Data Interface
═════════════════════════════════════════════════

Purpose
───────
    The `CryptoAPI.py` module provides the primary, user-facing interface for cryptocurrency data
    retrieval and analysis in the Quantsumore library. It abstracts away all provider-specific logic,
    endpoint quirks, and slug normalization — allowing end-users to seamlessly access both real-time
    and historical market data for any supported digital asset via a consistent, well-documented API.

Key Capabilities
───────────────
- **Live Crypto Market Data:** Instantly fetches the most recent trade, liquidity, and price data for any
  coin or token, with full support for exchange, base/quote filtering, and live order book metrics.
- **Historical OHLCV and Time Series:** Retrieves daily (or other interval) price, volume, and market cap
  history for all tracked assets, with robust date normalization and error handling.
- **Automatic Input Validation:** Slug, symbol, and ID validation handled centrally (see `prep.py`),
  with full support for canonicalization, error messaging, and defensive normalization.
- **Provider Obfuscation and Routing:** All upstream provider logic is abstracted; users interact only with
  stable, neutral interfaces (see “Data Attribution Policy” in `prep.py` for details).

Design Overview
───────────────
- **Single Entry Point:** Users interact exclusively through `APIClient`, constructed with a validated
  asset registry (typically `crypto_adapter` from `prep.py`).
- **Centralized URL Construction:** All endpoints, query params, and date conversions are built via
  `crypto_adapter.make(...)`, with strict input checking and multi-provider support.
- **Response Parsing and Shaping:** Raw API responses are parsed and normalized into pandas DataFrames by
  `crypto.live_quote` and `crypto.crypto_historical` (from `parse.crypto`), with consistent schema and
  timestamp formatting.
- **Unified Exception Hierarchy:** All downstream errors are mapped to clear, Quantsumore-defined exceptions.

Typical Workflow
────────────────
1. **Install and Import:**
       from quantsumore.api import crypto
2. **Initialize Client:**
       engine = crypto.APIClient(crypto.crypto_adapter)
3. **Set API Key (if required):**
       from quantsumore.api import APIKey
       APIKey("my-secret-key")
4. **Fetch Live Data:**
       df = engine.Latest(slug="bitcoin", cryptoExchange="binance")
5. **Fetch Historical Data:**
       df = engine.Historical(slug="bitcoin", start="2023-01-01", end="2023-06-30")

Supported Workflows
───────────────────
- **Batch Queries:** Both methods support single coin or list-of-coins for batch data retrieval.
- **Fine-Grained Filtering:** Live queries support filtering by base currency, quote currency, exchange, type, etc.
- **Time Series Customization:** Historical queries support arbitrary date ranges (UTC), with ISO or Unix input.
- **Extensible Endpoint Logic:** Adding new query types or intervals only requires changes to internal routing logic.

Core Classes and Methods
────────────────────────
- **APIClient(adapter)**
    - `.Latest(slug, baseCurrencySymbol=None, quoteCurrencySymbol=None, limit=100, exchangeType="all", cryptoExchange=None, api_key=None)`
      - Returns: `pandas.DataFrame` (live market pairs with columns: coin, symbol, exchange, price, volume, liquidity, etc.)
    - `.Historical(slug, start, end, api_key=None)`
      - Returns: `pandas.DataFrame` (daily OHLCV, market cap, volume, timestamp, etc.)

API Key Handling
────────────────
- **Automatic Storage:** Set your API key once with `APIKey("key")`; persists in singleton connection.
- **Per-Request Override:** Optionally pass `api_key` for a specific call.
- **Error Handling:** Raises `APIKeyRequiredError` if a key is required but not found.

Return Types and Data Structure
───────────────────────────────
All data is returned as pandas DataFrames with a standardized column set. Examples include:

Live Market Data:
    - 'coinName', 'coinSymbol', 'exchangeName', 'marketPair', 'category', 'baseSymbol', 'quoteSymbol',
      'price', 'volumeUsd', 'effectiveLiquidity', 'lastUpdated', 'quote', 'volumeBase', 'volumeQuote',
      'feeType', 'depthUsdNegativeTwo', 'depthUsdPositiveTwo', 'volumePercent', 'exchangeType', 'timeQueried'
Historical Time Series:
    - 'symbol', 'name', 'date', 'open', 'high', 'low', 'close', 'volume', 'marketCap', 'time_queried'

Exception Handling
──────────────────
- `APIKeyRequiredError`: API key missing or invalid.
- `ValueError`: Malformed or missing input arguments.
- `CryptoLiveQuoteNoDataError`, `CryptoHistoricalNoDataError`: No valid data returned.
- `CryptoLiveQuoteUnavailableError`, `CryptoHistoricalUnavailableError`: Provider down or unresponsive.

Internal Structure & Related Modules
────────────────────────────────────
- **prep.py:** Handles asset and slug validation, data provider obfuscation, and all input normalization.
- **parse/crypto.py:** Parses API responses and shapes them into DataFrames.
- **_http/connection.py:** Underlying HTTP(S) connection manager, with API key and session support.

Data Attribution & Licensing Policy
───────────────────────────────────
- All external provider logic is routed through abstract labels (e.g., “CryptoProviderA”);
  no explicit provider branding or endpoint URLs are exposed to end-users.
- For compliance, see the “Provider Label Registry” in `prep.py`.

Reference Table: Method Inputs/Outputs
──────────────────────────────────────
| Method     | Input(s)                                 | Output                        | Supports Multi? |
|------------|------------------------------------------|-------------------------------|-----------------|
| Latest     | slug(s), base/quote, limit, exchange     | DataFrame: market pairs       | Yes             |
| Historical | slug(s), start, end                      | DataFrame: daily OHLCV        | Yes             |

Example
───────
    >>> from quantsumore.api import crypto
    >>> engine = crypto.APIClient(crypto.crypto_adapter)
    >>> df = engine.Latest(slug=["bitcoin", "ethereum"], baseCurrencySymbol="USD", exchangeType="cex")
    >>> print(df.head())

    >>> df = engine.Historical(slug="bitcoin", start="2024-01-01", end="2024-01-31")
    >>> print(df.head())
"""
# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..prep import crypto_adapter
from .parse import crypto
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

    # Notes:
    # -----
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.  
    def Latest(self, slug, baseCurrencySymbol=None, quoteCurrencySymbol=None, limit=100, exchangeType="all", cryptoExchange=None, api_key=None):
        """
        Fetches and returns the latest live cryptocurrency market data for a specified asset.

        This method retrieves the most recent live trading data for the specified cryptocurrency asset 
        identified by its slug (e.g., "bitcoin"). It allows filtering based on base and quote currency 
        symbols, the specific cryptocurrency exchange, the maximum number of results, and the type of exchange.
        The data is structured as a DataFrame containing various metrics related to live trading activity.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        slug : str
            The identifier(s) for the cryptocurrency asset(s). Accepts a single identifier (e.g., "bitcoin").
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
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

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
        >>> engine = APIClient(adapter=some_asset_instance)
        >>> latest_data = engine.Latest(slug="bitcoin", baseCurrencySymbol="USD", quoteCurrencySymbol="JPY", cryptoExchange="binance", limit=100, exchangeType="all")
        >>> print(latest_data)
          coinName coinSymbol  ... exchangeType                      timeQueried
        0  Bitcoin        BTC  ...          cex 2024-08-27 14:57:32.938000+00:00

        [1 rows x 20 columns]
        
        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.        
        """    	
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='live', slug=slug, baseCurrencySymbol=baseCurrencySymbol, quoteCurrencySymbol=quoteCurrencySymbol, limit=limit, exchangeType=exchangeType)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )         
        if content:
            obj = crypto.live_quote(content, cryptoExchange=cryptoExchange)
            data = obj.DATA()
            return data

    def Historical(self, slug, start, end, api_key=None):
        """
        Fetches and returns historical cryptocurrency data for a specified asset within a given date range.

        This method retrieves historical price and trading data for the specified cryptocurrency asset 
        identified by its slug (e.g., "bitcoin"). The data is fetched for a date range defined by the 
        `start` and `end` parameters. The result is structured as a DataFrame containing various metrics 
        such as open, high, low, close prices, volume, market capitalization, and timestamps.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        slug : str
            The identifier(s) for the cryptocurrency asset(s). Accepts a single identifier (e.g., "bitcoin").
        start : str
            The start date for the historical data retrieval in the format "YYYY-MM-DD".
        end : str
            The end date for the historical data retrieval in the format "YYYY-MM-DD".
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

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
        >>> engine = APIClient(adapter=some_asset_instance)
        >>> historical_data = engine.Historical(slug="bitcoin", start="2024-01-01", end="2024-01-10")
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

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.        
        """    	
        if all(x is None for x in [start, end]):
            raise ValueError("Start and end dates must be provided for historical data requests.")
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='historical', slug=slug, start=start, end=end)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )          
        if content:
            obj = crypto.crypto_historical(content)
            data = obj.DATA()
            return data
           
    def __dir__(self):
        return ['Historical','Latest'] 



engine = APIClient(crypto_adapter)

def __dir__():
    return __all__




