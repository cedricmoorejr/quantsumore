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
EquityAPI — Unified Stock/Equity Data Interface
═══════════════════════════════════════════════

Purpose
───────
    The `EquityAPI.py` module exposes a high-level, user-focused interface for retrieving,
    validating, and transforming equity (stock/ETF) data within the Quantsumore platform.
    Designed for both programmatic analysis and live trading applications, this module abstracts
    away the complexity and variability of upstream data providers, ensuring reliable,
    normalized, and legally compliant access to historical and real-time market data.

Key Capabilities
────────────────
- **Historical Equity Prices:** Retrieve daily, weekly, or monthly time-series price data
  (OHLCV) for any supported ticker, with built-in validation, auto-formatting, and
  provider-agnostic normalization.
- **Live Quotes:** Fetch the latest price, volume, change, and trading statistics for any
  stock, ETF, or supported instrument, returned as a ready-to-use pandas DataFrame.
- **Fundamental Data:** Access current and historical company fundamentals, ratios,
  earnings data, and related key financial metrics.
- **Batch and Single-Asset Workflows:** All methods accept single tickers or lists for
  efficient batch retrieval and analysis.
- **Robust Input Validation:** Tickers, date ranges, and other parameters are strictly
  validated and normalized, with explicit error handling and unambiguous failure modes.
- **Provider Abstraction:** All external data source details are obfuscated and routed
  via encoded, abstract labels to ensure vendor neutrality and licensing compliance.

Design Overview
───────────────
- **Single Point of Access:** End users interact solely with the `APIClient`, which
  wraps the equity adapter registry and routes all queries through a central normalization
  and URL construction system.
- **Centralized Routing:** All endpoint, batching, and provider logic is mediated by
  `equity_adapter.make(...)`, ensuring future-proofing and ease of extension.
- **Strict API Key & Session Management:** All calls support secure, per-session or
  per-request API key injection, with global default fallback.
- **Comprehensive Exception Handling:** Custom exception types surface all relevant
  error conditions, from missing/invalid tickers to upstream rate-limiting and
  empty/invalid responses.
- **Result Normalization:** All outputs are rigorously cleaned, shaped, and returned
  as pandas DataFrames or Python dicts, with consistent column ordering and metadata.

Typical Workflow
────────────────
1. **Install and Import:**
       from quantsumore.api import equity
2. **Initialize Client:**
       engine = equity.APIClient(equity.equity_adapter)
3. **Set API Key (if required):**
       from quantsumore.api import APIKey
       APIKey("your-api-key-here")
4. **Fetch Historical Prices:**
       df = engine.Historical(ticker="AAPL", start="2023-01-01", end="2023-12-31")
5. **Get Latest Quotes:**
       quote = engine.Latest(ticker=["MSFT", "TSLA"])
6. **Batch Workflow:**
       df = engine.Historical(ticker=["AAPL", "GOOG", "MSFT"], start="2024-01-01", end="2024-06-30")

Supported Methods and Workflows
───────────────────────────────
- **Single & Multi-Ticker Queries:** Pass a string or list of tickers to any method.
- **Flexible Date Parsing:** Accepts string, datetime, or pandas.Timestamp; all dates normalized.
- **Live Data & Fundamentals:** Quickly retrieve the latest price or a full current snapshot.
- **Batch Analysis:** All methods handle batch requests and return combined, multi-index DataFrames.

Core Classes and Methods
────────────────────────
- **APIClient(adapter)**
    - `.Historical(ticker, start, end, frequency="1d", api_key=None)`
        - Returns: `pandas.DataFrame` (columns: Date, Ticker, Open, High, Low, Close, Volume, etc.)
    - `.Latest(ticker, api_key=None)`
        - Returns: `pandas.DataFrame` (columns: Ticker, LastPrice, Change, Volume, Time, etc.)

API Key Handling
────────────────
- **Automatic Storage:** Set your API key once with `APIKey("key")`; persists in singleton connection.
- **Per-Request Override:** Optionally pass `api_key` for a specific call.
- **Error Handling:** Raises `APIKeyRequiredError` if a key is required but not found.

Return Types and Data Schema
────────────────────────────
- **Historical Prices:** pandas DataFrame (multi-ticker/multi-date friendly)
- **Latest Quotes:** pandas DataFrame (with all key metrics per adapter)

Exception Hierarchy
───────────────────
- `APIKeyRequiredError`: Missing or invalid API key.
- `TickerNotFoundError`: Ticker does not exist or not supported.
- `EmptyResponseError`, `InvalidResponseError`: Upstream provider issues.
- `ValueError`: Invalid argument or parameter.

Internal Modules and Compliance Policy
──────────────────────────────────────
- **prep.py:** Centralizes all ticker validation, provider abstraction, and
  endpoint normalization.
- **parse/equity.py:** Parses responses and shapes output DataFrames.
- **_http/connection.py:** Manages HTTP(S) session, authentication, and retries.
- **Provider Obfuscation:** All external provider branding/details are abstracted.
  See `prep.py` for encoded label registry and compliance notes.

Reference Table: Method Inputs/Outputs
──────────────────────────────────────
| Method       | Input(s)                                                        | Output                       | Notes                                                                          |
| ------------ | --------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------ |
| Historical   | `ticker`, `start`, `end`, `frequency` (default="1d"), `api_key` | `pandas.DataFrame`           | OHLCV price data. Accepts string or list for ticker(s), flexible date parsing. |
| Latest       | `ticker`, `api_key`                                             | `pandas.DataFrame`           | Live quote for 1+ assets. Returns key stats: Last, Change, Volume, Time, etc.  |

Example
───────
    >>> from quantsumore.api import equity
    >>> engine = equity.APIClient(equity.equity_adapter)
    >>> df = engine.Historical(ticker="AAPL", start="2024-01-01", end="2024-06-30")
    >>> print(df.head())

    >>> quote = engine.Latest(ticker="MSFT")
    >>> print(quote)
"""
# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..prep import equity_adapter
from .parse._info import profile
from .parse._metric import quote_statistics
from .parse._intra import latest
from .parse._trailing import last
from .parse._periods import historical
from .parse._listing import ipo
from .parse._shareholders import dividend
from .parse._financials import statements
from ..._http.connection import Connection
from ...strata_utils import IterDict
# from ...date_parser import dtparse


__all__ = ['engine']


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

class ProfileClient:
    def __init__(self, adapter):
        self._adapter = adapter

    def _fetch(self, ticker, api_key=None):
        make = getattr(self._adapter, 'make')
        url = make(query='profile', ticker=ticker)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        ) 
        if content:
            obj = profile(content)
            return obj.DATA()

    def bio(self, ticker, api_key=None):
        """
        Provides an overview or summary of a company's information based on its ticker symbol.

        This method retrieves and displays information about a company identified by its ticker symbol.
        It returns the company's description.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose information is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        str or None
            Returns the company description as a string.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('company_description')

    def executives(self, ticker, api_key=None):
        """
        Provides information about a company's executives based on its ticker symbol.

        This method retrieves and displays information about the executives of a company identified
        by its ticker symbol.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose executive information is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.


        Returns:
        -------
        list or dict or None
            Returns the list or dictionary of company executives.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('executives')

    def info(self, ticker, api_key=None):
        """
        Retrieves the basic information of a company based on its ticker symbol.

        This method returns a dictionary containing the company's basic profile information,
        such as its name, location, website, and other key identifying details.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose basic information is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            A dictionary containing the company's basic information, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('basic_info')

    def industry(self, ticker, api_key=None):
        """
        Retrieves the industry and sector classification for a company based on its ticker symbol.

        This method returns a dictionary containing the company's industry and sector information,
        which can be useful for categorization and analysis.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose industry and sector information is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            A dictionary with 'industry' and 'sector' keys, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('industry_sector')

    def contact(self, ticker, api_key=None):
        """
        Retrieves contact information for a company based on its ticker symbol.

        This method returns a dictionary containing details such as address, phone number,
        email, and website, providing users with official company contact information.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose contact details are to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            A dictionary containing contact details, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('contact_details')

    def security(self, ticker, api_key=None):
        """
        Retrieves security-related information for a company based on its ticker symbol.

        This method returns a dictionary with details such as the security symbol,
        exchange, and other relevant security identifiers.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose security details are to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            A dictionary containing security details, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('security_details')

    def filings(self, ticker, api_key=None):
        """
        Retrieves a company's regulatory filings based on its ticker symbol.

        This method returns a list or dictionary of company filings, such as SEC filings,
        quarterly/annual reports, and other important regulatory documents.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose filings are to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        list or dict or None
            Returns the list or dictionary of company filings, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        data = self._fetch(ticker, api_key)
        return data and data.get('company_filings')

    def full(self, ticker, api_key=None):
        """
        Retrieves the complete company profile as a processed dictionary.

        This method returns the entire set of processed company profile data,
        which may include description, executives, industry, contact details,
        security information, and more.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose full profile is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            A dictionary containing the full company profile, or None if not available.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        return self._fetch(ticker, api_key)

    def __dir__(self):
        return [
            'bio',
            'executives',
            'info',
            'industry',
            'contact',
            'security',
            'filings',            
            'full',
        ]
        



class APIClient:
    def __init__(self, adapter):
        self.adapter = adapter
        # Attach profile namespace:
        self.Profile = ProfileClient(adapter)

    def Stats(self, ticker, api_key=None):
        """
        Provides various statistical information and financial metrics about a company based on its ticker symbol.

        This method retrieves and displays statistical and financial data for a company identified by its
        ticker symbol. The data includes metrics such as the previous close price, open price, bid and ask prices,
        daily and 52-week price ranges, volume, market capitalization, beta, PE ratio, earnings per share (EPS),
        earnings date, dividend yield, ex-dividend date, and 1-year target estimate.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose executive information is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.

        Returns:
        -------
        dict or None
            Returns a dictionary containing statistical data.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='stats', ticker=ticker)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )            
        if content:
            obj = quote_statistics(content)
            return obj.DATA()        

    def Historical(self, ticker, start, end, api_key=None):
        """
        Retrieves historical stock price data for a company based on its ticker symbol and a specified date range.

        This method fetches historical price data for a company identified by its ticker symbol over a given
        date range. The data includes the date, opening price, highest price, lowest price, closing price,
        adjusted closing price, and trading volume for each trading day within the specified range.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        ticker : str
            The ticker symbol (or list of symbols) of the company (or companies) for which historical data is to be retrieved.
        start : str
            The start date for the historical data in the format 'YYYY-MM-DD'. This date is inclusive.
        end : str
            The end date for the historical data in the format 'YYYY-MM-DD'. This date is inclusive.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        pandas.DataFrame or None
            Returns a DataFrame containing historical price data for each trading day in the specified date range.
            Each row represents a trading day, with columns for the date, open, high, low, close,
            adjusted close, and volume. Returns None if no data is found for the given ticker or if the data request fails.

        Raises:
        ------
        ValueError
            If the start and end date is not provided, a ValueError is raised.
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.            
        """
        if all(x is None for x in [start, end]):
            raise ValueError("Start and end dates must be provided for historical data requests.")
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='price', ticker=ticker, start=start, end=end)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )            
        if content:
            obj = historical(content)
            return obj.DATA()

    # Notes:
    # -----
    # This method is useful for obtaining real-time or near-real-time price information for a stock.
    # It handles the distinction between active trading hours and after-hours or closed market scenarios,
    # ensuring that the most relevant price is returned.
    #    
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.
    def Latest(self, ticker, api_key=None):
        """
        Retrieves the latest stock price for a company based on its ticker symbol.

        This method fetches the most recent price of a stock identified by its ticker symbol.
        During trading hours, it provides the current price. If trading is closed, it returns
        the last available price from the most recent trading session.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose latest stock price is to be retrieved.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        float or None
            Returns a float representing the latest stock price. Returns None if no data
            is found for the given ticker symbol or if the data request fails.
            
        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.            
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='latest', ticker=ticker)        
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )       
        if content:
            obj = latest(content)
            return obj.DATA()

    # Notes:
    # -----
    # - The method constructs a request URL using the adapter's `make` method, tailored to query dividend information,
    #   and sends the request to retrieve the data in JSON format.
    # - The `dividend` function is used to process the JSON response and create a structured dividend
    #   data object from the returned content.
    def Dividends(self, ticker, api_key=None):
        """
        Retrieves dividend data for the specified ticker symbol.

        This method fetches dividend-related information such as ex-dividend dates, dividend yields, and payment dates
        for a given company based on the `ticker`. It is designed to provide an overview of a company's dividend history
        and current dividend policies.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        ticker : str
            The ticker symbol for which to retrieve dividend data. Example: 'AAPL' for Apple Inc.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        object
            A dividend data object that contains historical and current dividend information for the specified `ticker`.
            The object includes the dividend data parsed from the response in JSON format.
            
        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.            
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='dividend_history', ticker=ticker)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )         
        if content:
            obj = dividend(content)
            return (obj.DividendReport, obj.DividendData)

    # Notes:
    # ------
    # The returned data includes detailed metrics such as currency, exchange information, 
    # timestamps, and price points across specified trading periods. This allows for precise 
    # tracking of stock price movements within the last trading session.
    #
    # >>>>>>>>>>>>>>>>>>>>> REAL-TIME DATA - LIVE FEED <<<<<<<<<<<<<<<<<<<<<<
    # Returned results reflect the most current trading data available at the time of the request.
    def Lastn(self, ticker,  range="1d", interval="1m", api_key=None):
        """
        Retrieve the latest stock price data for a given ticker symbol, with flexible time range and granularity.

        This method constructs a request url for a ticker symbol, specifying
        both the historical range (e.g., '1d', '1mo', '1y') and the interval (e.g., '1m', '1h', '1d') between data points.
        It handles API constraints by validating range/interval combinations and automatically adjusting the interval
        to avoid excessively large responses.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.

        Parameters
        ----------
        ticker : str
            The ticker symbol to retrieve stock data for.
            Example: 'AAPL' for Apple Inc.,.
        interval : str, optional
            The granularity of data points, defaulting to '1m' (1 minute).
            Supported intervals (may vary by range): [
                '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h',
                '1d', '5d', '1wk', '1mo', '3mo'
            ].
        range : str, optional
            The historical window to retrieve, defaulting to '1d' (1 day).
            Valid values include: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y',
            '5y', '10y', 'ytd', 'max'.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            already been set using `APIKey()`.

        Returns
        -------
        object
            An object containing the requested stock data, including prices, volumes, timestamps,
            and session metadata.

        Raises
        ------
        ValueError
            If the specified interval or range is not supported, or if the combination is invalid
            under API constraints (e.g., 1m interval cannot be used with 1y range).
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`. 

        Notes
        -----
        - Invalid range/interval combinations are automatically detected and rejected before the request is made.
        - If the requested range/interval combination would result in a response exceeding 100,000 data points,
          the interval is automatically increased (coarsened) to reduce the data size, and a warning may be emitted.


        Understanding `range` and `interval` (API Client)
        -------------------------------------------------
        The `range` and `interval` arguments control **how much historical data you receive** and **how detailed each data point is**.
        Here’s how to use them and what to keep in mind:

        range
            - What it does:
                Specifies how far back in time you want to fetch data.
                Example values: `1d` (1 day), `1mo` (1 month), `1y` (1 year), etc.
            - Valid values:
                `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`
            - Note:
                Use these exact strings—custom ranges like `30d` are not supported.

        interval
            - What it does:
                Sets how granular each data point is.
                Example values: `1m` (1 minute), `1d` (1 day), `1wk` (1 week).
            - Valid values (depend on range):
                `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`
            - Note:
                Not every interval is available for every range. Fine intervals (like `1m`) can only be used with short ranges (like `1d` or `5d`). For longer ranges, use coarser intervals (`1d`, `1wk`, `1mo`).

        Allowed Combinations

            | range   | Allowed intervals                      | Example Use               |
            | ------- | -------------------------------------- | ------------------------- |
            | 1d      | 1m, 2m, 5m, 15m, 30m, 60m              | Intraday, high detail     |
            | 5d      | 5m, 15m, 30m, 60m, 90m                 | Intraday, medium detail   |
            | 1mo or longer | 1d                               | Daily closes only         |
            | 3mo or longer | 1d, 1wk, 1mo                     | Coarser, for long history |

            Note: If you use a fine interval (like `1m`) with a long range (like `1y`), you will get an error.
            - For minute-level data, use short ranges: `1d` or `5d`.
            - For long time spans, use daily or weekly intervals.

        Examples

            | range | interval | What you get                          |
            | ----- | -------- | ------------------------------------- |
            | 1d    | 1m       | 1-minute data for today (high detail) |
            | 5d    | 15m      | 5 days, one point every 15 minutes    |
            | 1mo   | 1d       | 1 month of daily closing prices       |
            | 6mo   | 1wk      | 6 months, weekly prices               |

            If you want all available historical data (`range='max'`), use only coarser intervals like `1d`, `1wk`, or `1mo`.

        General Guidelines

            - range: “How much time do you want?”
            - interval: “How detailed should each data point be?”
            - If you request too much data or an invalid combination, you’ll get an error.

        Example Call
        -----------
            output = equity.Lastn(ticker="AAPL", range="1d", interval="60m")

            Returns prices for the past day, one data point per hour block (e.g., 10:30, 11:30, etc).

        Developer Tips
        --------------
            - Always validate your range and interval combination before sending a request.
            - Minute-level intervals are only supported for very recent data (about 1–7 days).
            - Medium intervals (5m, 15m, etc.) are available for up to about 60 days.
            - For months/years of data, use intervals like `1d`, `1wk`, or `1mo`.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='last', ticker=ticker, range=range, interval=interval)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )         
        if content:
            obj = last(content)
            return obj.DATA()

    # Notes:
    # -----
    # - The method uses an internal class method `key_from_mapping` to map user-friendly terms to actual statement types
    #   and periods. This allows for case-insensitive input and use of common synonyms (e.g., 'IS' for 'Income Statement').
    # - The method constructs a request URL using the adapter's `make` method and sends the request to retrieve the
    #   financial data in JSON format.
    # - This method requires that the `statements` object is available to parse the returned content
    #   into a structured financial statement object.
    def Financials(self, ticker, period="Quarterly", api_key=None):
        """
        Retrieves financial statement data for the specified ticker symbol.

        This method fetches financial statement information such as the income statement, balance sheet, or cash flow
        for a given company based on the `ticker`. The user can specify the type of statement (e.g., Income Statement,
        Balance Sheet, Cash Flow Statement) and the reporting period (e.g., Quarterly or Annually). If no valid
        statement type or period is provided, it raises an error.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        ticker : str
            The stock ticker symbol representing the company for which financial statements are requested.
        period : str, optional, default="Quarterly"
            The reporting period for the financial statement. It can be either:
            - 'Quarterly' (synonyms include 'Q', 'Quarter', 'Qtr')
            - 'Annually' (synonyms include 'A', 'Annual')
            If an invalid period is provided, a ValueError is raised.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        object
            A financial statement object that contains the requested data for the specified `ticker`, `statementType`,
            and `period`. The object includes the financial data parsed from the response in JSON format.

        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.
        """
        valid_periods = {'Quarterly': ['Q', 'Quarter', 'Qtr'], 'Annually': ['A', 'Annual']}
        period = IterDict.key_from_mapping(period, valid_periods, invert=False)
        if not period:
            raise ValueError("Invalid period.")
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='financials', ticker=ticker, period=period)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )      
        if content:
            obj = statements(json_content=content)
            return (obj.IncomeStatement, obj.BalanceSheet, obj.CashFlowStatement)

    # Notes:
    # -----
    # - The method constructs a request URL using the adapter's `make` method, tailored to query IPO information for a specific period,
    #   and sends the request to retrieve the data.
    # - The `ipo` function is used to process the JSON response and create a structured IPO data object from the returned content.
    def IPO(self, date=None, api_key=None):
        """
        Retrieves IPO data for the specified date or date range.

        This method fetches information related to initial public offerings (IPOs) such as the ticker symbols, company names,
        proposed exchanges, share prices, and the number of shares offered. It is designed to provide details about companies going public
        within a specified period.

        API Key Usage:
        -------------
        If `api_key` is not provided, the method expects that an API key has already been set using:

            from quantsumore.api import APIKey
            APIKey("your-api-key-string")

        This securely stores your API key for all subsequent requests via a singleton connection manager.
        Passing `api_key` directly will override any stored key for this request.
        
        Parameters:
        ----------
        date : str, optional
            The date or date range for which to retrieve IPO data. The date should be in a format recognized by the API endpoint.
            Example: '2024-01' for January 2024.
        api_key : str, optional
            The API key for authenticated requests. If not provided, an API key must have
            been previously set using `APIKey()`.            

        Returns:
        -------
        object
            An object that contains IPO data parsed from the response in JSON format. This object includes structured information
            about each IPO listing retrieved for the given period.
            
        Raises:
        ------
        APIKeyRequiredError
            If no API key is provided and none has been set using `APIKey()`.            
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='ipo', period=date)
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )     
        if content:
            obj = ipo(content)
            return obj.DATA()

    def __dir__(self):
        return [
            'Profile',        
            'Stats',               
            'Financials',
            'Dividends',
            'Historical',
            'Lastn',
            'Latest',
            'IPO'
        ]

engine = APIClient(equity_adapter)

def __dir__():
    return __all__



