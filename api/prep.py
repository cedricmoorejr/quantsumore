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

import re

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from .market_utils import fxutil, CurrencyQuery
from ..date_parser import dtparse
from ..markup import url_encode_decode
from ..exceptions import InvalidCurrencyPairError
from ._prep_utils import (
    _normalize_dates,
    _INTERVAL_TO_MINUTES,
    _RANGE_TO_DAYS,
    _enforce_valid_combo,
    _auto_adjust_interval,
    _days_from_range,
    _MAX_POINTS,
    _validate,
    _aliasmap,
)


__all__ = [
    'equity_adapter',
    'forex_adapter',
    'crypto_adapter',
    'cpi_adapter',
    'treasury_adapter',
]


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.




######################################################################
# EQUITY DATA ROUTING AND URL CONSTRUCTION INTERFACE
######################################################################
class _Equity:
    """
    Core interface for stock data URL construction and routing.

    This class centralizes the logic for generating endpoint URLs for a wide variety of
    equity data queries (e.g., company profiles, statistics, prices, dividends, IPO calendar)
    across multiple data providers. It supports argument normalization, ticker validation,
    batching for multi-ticker operations, and flexible query routing.

    Class Workflow and Features:
      1. **Initialization:**
         - Stores encrypted base URLs for different providers/versions.
         - Flags for enabling batch processing of dividends or prices.

      2. **Ticker Normalization (`_normalize_tickers`):**
         - Accepts a single ticker or list; deduplicates, uppercases, and validates each symbol.
         - Uses the `instrument_validation` class to ensure all tickers are recognized by the system.
         - Prevents malformed, unknown, or duplicate tickers from reaching the URL builder.

      3. **URL Construction (`_construct_url`):**
         - Assembles endpoint URLs for each supported query type, adapting parameters for
           each provider’s requirements (e.g., EquityProviderA, EquityProviderD).
         - Handles multi-ticker URLs where supported, plus different endpoints for stats,
           dividends, financials, IPO calendars, and historical prices.
         - Always returns the ready-to-use URL or (base, endpoint) tuple.

      4. **Main Routing (`make`):**
         - Acts as a centralized API for building stock data URLs.
         - Dispatches to the correct URL builder based on the `query` type and parameters.
         - Handles ticker(s), dates, periods, and batching as required for the endpoint.
         - Validates and normalizes all inputs before constructing URLs.
         - Returns either a single URL or a list of URLs, depending on batching and query type.

      5. **Batching and Multi-Ticker Support:**
         - Supports batch queries for dividends and prices (if enabled).
         - Processes each ticker separately for endpoints that do not support batching.

      6. **Strict Separation of Concerns:**
         - This class is responsible only for URL assembly—**not** for fetching or parsing data.
         - Ensures all downstream network or data-fetching logic receives validated, provider-ready URLs.

    Usage Example:
        eq = _Equity()
        url = eq.make("profile", ticker="AAPL")
        urls = eq.make("dividend_history", ticker="AAPL")
        url = eq.make("price", ticker="GOOG", start="2023-01-01", end="2023-06-01")

    Notes:
        - Only intended for internal use by higher-level data clients or query routers.
        - All argument validation, normalization, and batching handled here before URL generation.
        - Designed for extensibility if new endpoints or providers are added.
    """	
    def __init__(self):
        self.base_url_v1 = b'gAAAAABohzVhSfnBi7DAMY0knQyX9YcI2OyPUFr2usvYjlO05oH17Dt6aNl5n1AsbT9qCtZ6YDe5-S5dYGON_15b_k45n_pPkDJ5njJqXq9csaSBUR9zAqg='
        self.base_url_v2 = b'gAAAAABohzVhVDs2iMD_UICL-STxw1vVvq5dcNgU8xZbDSFKYV75GszKH-xefbnyxnakr52kK1mVBluwKCCgkP49528py0CaF4e3cfRbAopV3LtorA7QPaADL26aCnI3fzlitNNGmjJ0gYLJcHicJ70Q4TITuqZayQ=='
        self.base_url_v3 = b'gAAAAABohzVhI9NPcDcLtukAnro6tfJ93xVRQVI3Src77aPcdt4It99ZKA5gdPLfIEGOW7ZLZZ9PwuCAAO0JgVG6Wft5IcJ0EOjkM5LRDkUrr3SxxuPS7O-5bA2EogufTKzIUv3f_MgIFLV93imZTmYcR2I_FWVdHA=='
        self.base_url_v4 = b'gAAAAABohzVhLcmj99RtSYzELuF9P5OlldUvpxOnQE_UZ5tRkaRjSYpWJOMoHLbcw6Mnb5mmOt8_7Jyjj2Oswjl36rUv0POhqDt2xJpok9vhMEW1Dvek4HmTI0F_tcuZRLQtv_mx0fCf'
        self.base_url_v5 = b'gAAAAABohzVh6URZ0EvhHo6mWBoPZWRdRn8ccZ_rH4ie3WkR3am2pNbTvw9At5dyNe3EvrTqJscVgqGr3hv_j5JsEql_24FJhtbIfcwl_j0cX2TV0GNfiOVk9pwuQuZBuPONT70Alw9d'
        self.base_url_v6 = b'gAAAAABohzVhFsRpWFzfPZ1o0duc3lsBGNLpazdLEHQtcL7hcu_6DoqqG0aeU_dbOiK6aSKgehXzA09WZwUjIUDuV1Em52rymLfnH-V3D9iZvdCsu2ZwOjZXKOMBqJB1XUNVNyweFuRa'

    def _normalize_tickers(self, tickers):
        if isinstance(tickers, str): tickers = [tickers]; [_validate.stock_ticker(t) for t in tickers]
        elif isinstance(tickers, list):
            if not all(isinstance(t, str) for t in tickers): raise ValueError("All elements in the ticker list must be strings.")
        else: raise ValueError("Input must be either a string or a list of strings.")
        norm = list(dict.fromkeys(t.upper() for t in tickers))
        [_validate.stock_ticker(t) for t in norm]
        return norm

    def _construct_url(self, id, period1=None, period2=None, f_rng=None, f_period=None, f_interval=None, Type=None):
        if period1 is None and period2 is None:
            if Type == "y_spark":
                t = url_encode_decode.encode_str(i=id, chars_to_encode=",", join_char=",")
                return (self.base_url_v3, f"{t}&range={f_rng}&interval={f_interval}&indicators=close&includeTimestamps=true&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance") # Used by: "latest" and "last" queries in make()
            if Type == "exchange_company":
                sel = 'Quarterly' if f_period == 'Quarterly' or f_period is None else 'Annually' # Used by: "financials" query in make()
                period = "2" if sel == 'Quarterly' else "1"
                return (self.base_url_v4, f"{id}/financials?frequency={period}")
            if Type == "div_payout":
                return (self.base_url_v5, f"{id}/dividends?assetclass=stocks") # Used by: "dividend_history" query in make()
            if Type == "stats":
                return (self.base_url_v1, f"api/screener/m/f?m=s&s=symbol&c=s,n,marketCap,price,volume,peRatio,open,close,low,high,dividendYield,low52,high52,priceTarget,exDivDate,nextEarningsDate,averageVolume,eps,beta&cn=100&f=s-is-%2524{id}") # Used by: "stats" query in make()
            return (self.base_url_v1, f"stocks/{id}/company/__data.json?x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001") # Used by: "profile" query in make()
        elif Type == "ipo" and period1:
            return (self.base_url_v6, f"{period1}") # Used by: "ipo" query in make()
        return (self.base_url_v2, f"{id}?formatted=true&includeAdjustedClose=true&interval=1d&userYfid=false&lang=en-US&region=US&period1={period1}&period2={period2}") # Used by: "price" query in make() (when start/end are provided)

    def make(self, query, *args, **kwargs):
        """
        Supported queries:
            - profile:    Company overview/profile (base_url_v1)
            - stats:      Statistics snapshot (base_url_v1)
            - last:       Recent/intraday/minute-by-minute price data (base_url_v3, "spark" endpoint)
            - financials: Financial statements (base_url_v4)
            - dividend_history: Dividends (base_url_v5)
            - price:      Historical price or "latest" price if range is today (base_url_v2)
            - ipo:        IPO calendar/listings (base_url_v6)
        """        
        if query.lower() == "ipo":
            period = kwargs.get('period')
            period = _normalize_dates.norm(period, future_date_check=True, date_format="%Y-%m", clip="end") if period else dtparse.now(format="%Y-%m")
            return self._construct_url(id=None, period1=period, Type="ipo")  
        ticker = args[0] if args else kwargs.get('ticker')
        start, end = kwargs.get('start'), kwargs.get('end')
        ticker = self._normalize_tickers(ticker)
        if query.lower() == "profile":
            return self._construct_url(id=ticker[0] if isinstance(ticker, list) else ticker)
        if query.lower() == "stats":
            return self._construct_url(id=ticker[0] if isinstance(ticker, list) else ticker, Type="stats")
           
        if query.lower() == "last":
            rng = kwargs.get("range", "1d")          
            interval = kwargs.get('interval', '1m')
            
            # Make sure if alias its given correctly
            rng = _aliasmap.lookup(rng, mapping="ranges")
            interval = _aliasmap.lookup(interval, mapping="intervals")            
            
            # Normalize and explicitly validate inputs
            interval = interval.lower()
            rng = rng.lower()
            if interval not in _INTERVAL_TO_MINUTES:
                raise ValueError(f"Unsupported interval '{interval}'. Valid intervals: {list(_INTERVAL_TO_MINUTES.keys())}")
            if rng not in _RANGE_TO_DAYS and rng not in ("ytd", "max"):
                raise ValueError(f"Unsupported range '{rng}'. Valid ranges: {list(_RANGE_TO_DAYS.keys()) + ['ytd', 'max']}")
            
            # Strictly forbid invalid combos
            _enforce_valid_combo(rng, interval)
            
            # Auto-coarsen if you'd fetch >100k points            
            new_iv = _auto_adjust_interval(rng, interval)
            if new_iv != interval:
                print(f"interval '{interval}' bumped to '{new_iv}' to limit payload")
                interval = new_iv

            # Guard for multi-ticker
            days = _days_from_range(rng)
            pts  = float("inf") if days == float("inf") else days * 1440 / _INTERVAL_TO_MINUTES[interval]
            max_tks = int(_MAX_POINTS // pts) if pts != float("inf") else 0

            if max_tks < 1:
                raise ValueError(f"Even one ticker at range='{rng}' & interval='{interval}' exceeds {MAX_POINTS:,} points.")
            if len(ticker) > max_tks:
                raise ValueError(
                    f"Too many tickers: for range='{rng}', interval='{interval}', "
                    f"max {max_tks} tickers allowed (≈{int(pts):,} points each)."
                )
            
            return self._construct_url(id=ticker, f_rng=rng, f_interval=interval, Type="y_spark")
           
        if query.lower() == "financials":
            period = kwargs.get('period')
            return self._construct_url(id=ticker[0] if isinstance(ticker, list) else ticker, f_period=period, Type="exchange_company")
        if query.lower() == "dividend_history":
            return self._construct_url(id=ticker[0] if isinstance(ticker, list) else ticker, Type="div_payout")
        if query.lower() == "price":
            t = ticker[0] if isinstance(ticker, list) else ticker
            if start and end:
                start, end = _normalize_dates.norm(start, end)
                return self._construct_url(id=t, period1=start, period2=end)
            raise ValueError("Start and end dates are required for historical price queries.")    
           
        if query.lower() == "latest":
            return self._construct_url(id=ticker[0] if isinstance(ticker, list) else ticker, f_rng="1d", f_interval="1m", Type="y_spark")
    def __dir__(self): return ['make']    


######################################################################
# FOREX DATA ROUTING AND URL CONSTRUCTION INTERFACE
######################################################################
class _Forex:
    """
    Central interface for constructing and routing Forex (foreign exchange) data URLs.

    The _Forex class manages all logic related to the assembly of endpoint URLs for fetching 
    forex rates, historical data, interbank/spot prices, bid/ask spreads, and currency conversion, 
    adapting inputs to match multiple provider requirements and supporting flexible batching.

    Workflow and Features:
      1. **Initialization:**
         - Stores encrypted base URLs for live/interbank, historical, bid/ask, and conversion endpoints.
         - Loads the system's list of supported major currencies at startup.
         - Sets flags for enabling batch operations (historical, bid/ask).

      2. **Currency Normalization (`_normalize_currencies`):**
         - Accepts a single currency code/pair or a list.
         - Deduplicates and uppercases all entries, preserving order.
         - Validates each code/pair against the FX registry using `instrument_validation`.
         - Ensures only recognized, supported currencies/pairs are used for downstream queries.

      3. **URL Construction (`_construct_url`):**
         - Builds the correct provider-specific endpoint for each supported Forex query:
             - Interbank rates: supports single code or batch, with optional inclusion/exclusion filters.
             - Historical rates: formats date ranges and encodes currency pairs as needed.
             - Bid/ask: assembles the summary endpoint for one or multiple currency pairs.
         - Returns a ready-to-use (base, endpoint) tuple or full URL string for direct API requests.

      4. **Main Routing (`make`):**
         - Centralizes dispatch for all supported Forex query types.
         - Accepts a flexible set of parameters (query type, codes/pairs, dates, filters).
         - Handles input normalization, batching logic, and query-specific argument routing.
         - Returns either a single URL or a list of URLs, depending on input and endpoint support.

      5. **Batching & Multi-Currency Support:**
         - Supports batch requests for historical, interbank, and bid/ask endpoints (when enabled).
         - Ensures all returned URLs are for validated, canonicalized codes/pairs.

      6. **Design Principles:**
         - Purely responsible for string construction; never fetches or mutates data.
         - Provider-specific logic is contained for easy extension or update.
         - Strict argument and type validation prevents malformed URLs or unsupported queries.
         - All network requests must use URLs produced by this class for system consistency.

    Example Usage:
        fx = _Forex()
        url = fx.make("historical", currency_pair="EURUSD", start="2023-01-01", end="2023-06-30")
        urls = fx.make("bid_ask", currency_pair=["USDJPY", "EURUSD"])
        url = fx.make("interbank", base_currency="USD", filter_currencies=["EUR", "GBP"])

    Notes:
        - Intended for internal use by data-fetching clients and query routers.
        - Endpoints and logic are tightly coupled to current provider requirements; may need
          updates if APIs change.
        - All inputs are normalized and validated before URL generation for robustness.
    """	
    def __init__(self):
        self.historical_batching_enabled = False
        self.bid_ask_batching_enabled = False
        self.major_forex_currencies = fxutil.which.major()
        self.ccy = None            
        self.conversion_url = b'gAAAAABohzVh-avNIuz6bACRJK2ph5nDJy2QsGAvDH7QtrpmNDC33A54bXY18MPCI4Gx7j1pTX1MajKVMkWoX_rUStZbDGixJPaGHJDOYKEqQ4K6q8WFdQKiHW5BuXpW8oNVgXWOzkno8CtFhzwvBexqjfsZlpwBt2TgQPCUnoVN9Zk6ZtPuKOE='
        self.interbank_base_url = b'gAAAAABohzVh3O5XnN6gOyel6cviuEGZZ5DpxG-3nEnx9z6apDAz0v69o9FrhlowkYLZD_vroGvZIMhTAkQ330G2mF66noWtWh2sRoeqya62SwziPDEshDw2feCF7nP32vayhrfWxjcOo3HuiVX2QxKBLZp_dtNChojB4tNBmOknmlTzTY-zIhc='
        self.historical_base_url = b'gAAAAABohzVhIS7LERF6a7PnkJ1OTQEtOv2WAV8BXxI6aCr7W3hqyl1SKDoUOcj7JL9_Z_G36ReGbjHu9jSA2k5GzHPrmt8hOmc0Hz6ZJXfx-txR3kcZsufur4SX0fahcYlDDGwyF4yDP5FU_j3MOKBiUGpCtag8uw=='
        self.bid_ask_url = b'gAAAAABohzVhR3M8hqk1Zwl9-598dyDDQ8KiBzZEeKgYE79bqP1vw3mjGLhpAekroc-ZCCF3VhdzciOqle7k1cLdXXpedmHG0-kKRTtqxLXcuB3ze5SMMFx2HW1Q4-VuuScljvwfPr2v'
    
    def _normalize_currencies(self, currencies, currency_dict_type="major"):
        lst = []
        if isinstance(currencies, str): currencies = [currencies]
        if isinstance(currencies, list):
            if not all(isinstance(c, str) for c in currencies): raise ValueError("All elements in the currency list must be strings.")
            for c in currencies:
                result = _validate.fx_currency(c, currency_dict_type=currency_dict_type)
                if result is None: lst.append(_validate.validated_instrument)
        else: raise ValueError("Input must be either a string or a list of strings.")
        norm = list(dict.fromkeys(c.upper() for c in lst))
        return norm[0] if len(norm) == 1 else norm

    def _construct_url(self, id, filter_currencies=None, ignore_currencies=None, p1=None, p2=None):
        if all(x is None for x in [p1, p2]):
            ccy = self.major_forex_currencies.copy()
            id = re.sub(r'\s+', chr(32), id).strip()
            if len(id) == 3:
                filter_currencies = [filter_currencies] if isinstance(filter_currencies, str) else filter_currencies
                ignore_currencies = [ignore_currencies] if isinstance(ignore_currencies, str) else ignore_currencies
                if filter_currencies: ccy = [curr for curr in filter_currencies if curr in ccy]
                elif ignore_currencies: ccy = [curr for curr in ccy if curr not in ignore_currencies]
                else: 
                    if id in ccy: ccy.remove(id)
                s = '%2C'.join(ccy)
                return (self.interbank_base_url, f"{s}&source={id}")
        start = p1.replace('/', '%2F') if p1 else ""
        end = p2.replace('/', '%2F') if p2 else ""
        return (self.historical_base_url, f"?ratepair={id}&start_date={start}&end_date={end}")

    def make(self, query, *args, **kwargs):
        if query.lower() == "historical":
            pair = args[0] if args else kwargs.get('currency_pair')
            start = kwargs.get('start')
            end = kwargs.get('end')
            pair = self._normalize_currencies(pair)
            if start and end: sdate, edate = _normalize_dates.norm(start, end, future_date_check=True, date_format='%d/%m/%Y')
            elif start: sdate, edate = _normalize_dates.norm(start, start, future_date_check=True, date_format='%d/%m/%Y')
            else: raise ValueError("Both start and end dates are required for historical data.")
            if self.historical_batching_enabled and isinstance(pair, list) and len(pair) > 1:
                urls = [self._construct_url(id=c, p1=sdate, p2=edate) for c in pair]
                return urls if len(urls) > 1 else urls[0]
            if isinstance(pair, list): pair = pair[0]
            return self._construct_url(id=pair, p1=sdate, p2=edate)
        elif query.lower() == "interbank":
            bc = args[0] if args else kwargs.get('base_currency')
            if bc is None: raise ValueError("Base currency must be provided for 'interbank' queries.")
            fltr = args[1] if len(args) > 1 else kwargs.get('filter_currencies', [])
            ign = args[2] if len(args) > 2 else kwargs.get('ignore_currencies', [])
            fltr = fxutil.tokenize(fltr) if fltr else None
            ign = fxutil.tokenize(ign) if ign else None
            bc = self._normalize_currencies(bc)
            return self._construct_url(id=bc, filter_currencies=fltr, ignore_currencies=ign)
        elif query.lower() == "bid_ask":
            pair = args[0] if args else kwargs.get('currency_pair')
            pair = self._normalize_currencies(pair, currency_dict_type="all_currency_names")
            pair = pair[0] if isinstance(pair, list) else pair
            try:
                if not fxutil.query(pair, query_type="major_pairs", ret_type="bool"):
                    raise InvalidCurrencyPairError(f"Currency pair '{pair}' is invalid or not supported.")
            except Exception:
                raise InvalidCurrencyPairError(f"Currency pair '{pair}' is invalid or not supported.")
            return (self.bid_ask_url, f"{pair}/summary?assetclass=currencies")
        elif query.lower() == "convert":
            pair = args[0] if args else kwargs.get('currency_pair')
            _validate.fx_currency(pair)
            self.ccy = _validate.validated_instrument
            return (self.conversion_url, self.ccy)
        # Disabled "current" query (which use self.quote_base_url) 
        elif query.lower() == "current":
            raise Exception("The 'current' endpoint is currently disabled due to bandwidth constraints.")

    def __dir__(self): return ['make'] 


######################################################################
# CRYPTOCURRENCY DATA ROUTING AND URL CONSTRUCTION INTERFACE
######################################################################
class _Crypto:
    """
    Central interface for constructing and routing cryptocurrency data URLs.

    The _Crypto class manages all logic related to the construction of endpoint URLs
    for cryptocurrency queries (e.g., live order book, historical OHLCV), adapting
    parameters for provider requirements and supporting robust input normalization,
    validation, and batching.

    Workflow and Features:
      1. **Initialization:**
         - Stores encrypted base URLs for live and historical endpoints.
         - Flags control whether batch operations are enabled for historical and live queries.

      2. **Slug and ID Normalization:**
         - `_normalize_slugs`: Accepts one or many slugs, validates each against the coin registry,
           deduplicates, and normalizes to lowercase, ensuring only known coins are queried.
         - `_normalize_ids`: Accepts one or many slugs, resolves each to its numeric coin ID
           via validation, deduplicates, and returns as a list or single ID.

      3. **URL Construction (`_construct_url`):**
         - Assembles the correct provider-specific endpoint for either live or historical data,
           adapting to supplied slugs/IDs, currency filters, limits, and exchange type.
         - Converts currency symbols to IDs for correct filtering and applies canonicalization.

      4. **Main Routing (`make`):**
         - Central entry point for query routing: dispatches either "historical" or "live"
           requests to the correct URL builder, normalizing and validating all inputs first.
         - Handles batching of requests where enabled, outputting a list of URLs as needed.

      5. **Design Principles:**
         - Purely responsible for string construction; never fetches or mutates data.
         - Strict validation for slugs and IDs using the internal registry to ensure only
           supported coins are queried.
         - Batch and single-asset queries handled consistently for all endpoints.

    Example Usage:
        c = _Crypto()
        url = c.make("historical", slug="bitcoin", start="2023-01-01", end="2023-07-01")
        urls = c.make("live", slug=["bitcoin", "ethereum"], baseCurrencySymbol="usd", limit=20, exchangeType="cex")

    Notes:
        - Intended for internal use by data retrieval and routing systems.
        - All input normalization and error handling are performed here, guaranteeing
          that URLs passed to request logic are valid and canonical.
        - Provider-specific logic is easily extensible for future endpoint changes.
    """	
    def __init__(self):
        self.historical_batching_enabled = False
        self.live_batching_enabled = False
        self.historical_base_url = b'gAAAAABoiGILgRUXTfZG7scsJV0867Wxxljrlud-EzlgB2DL4ooXSsl_PR-5KLD8hWHJwePSR4OsOCiB6iv0lZ0DODvTj2Id_obWlM4Ebc2-4DnV6loTc_h-4N7msVlMJCtmXPLEA2vNkWPj_mEfMFNhGZak_SPkywNnJKRVQv_a0BZ3QprX_OE='
        self.live_base_url = b'gAAAAABoiGIw2048TggtV7iVKJnchnB73P1P1Al56x6UKQetUrxZn2K3G-O6kUSnHOHGBHQHOTRP9tqdBIlS_UczTNjOylpDmOQOb0_hyYoZu_qXdXCwF_9qJ7AJPYptH6LE5swuhSsZOQd8Ft1lML-kdELF1WDOTfNiK-mXjV-kvKgrQ1M6-Js='

    def _normalize_slugs(self, slugs):
        if isinstance(slugs, str): slugs = [slugs]; [_validate.crypto_slug_name(s) for s in slugs]
        elif isinstance(slugs, list):
            if not all(isinstance(s, str) for s in slugs): raise ValueError("All elements in the slug list must be strings.")
        else: raise ValueError("Input must be either a string or a list of strings.")
        norm = list(dict.fromkeys(s.lower() for s in slugs))
        return norm[0] if len(norm) == 1 else norm

    def _normalize_ids(self, ids):
        ID_list = []
        if isinstance(ids, str): ids = [ids]
        if isinstance(ids, list):
            if not all(isinstance(ID, str) for ID in ids): raise ValueError("All elements in the ID list must be strings.")
            for i in ids:
                result = _validate.crypto_slug_name(i)
                if result is None: ID_list.append(_validate.validated_instrument[1])
        else: raise ValueError("Input must be either a string or a list of strings.")
        norm = list(dict.fromkeys(ID for ID in ID_list))
        return norm[0] if len(norm) == 1 else norm

    def _construct_url(self, id, baseCurrency=None, quoteCurrency=None, limit=100, exchange_type='all', period1=None, period2=None):
        if all(x is None for x in [period1, period2]):
            endpoint = f"slug={id}&start=1&limit={limit}&category=spot&centerType=all&sort=cmc_rank_advanced&direction=desc&spotUntracked=true"
            if baseCurrency: endpoint += f'&baseCurrencyId={CurrencyQuery.SymbolreturnID(baseCurrency)}'
            if quoteCurrency: endpoint += f'&quoteCurrencyId={CurrencyQuery.SymbolreturnID(quoteCurrency)}'
            if exchange_type and exchange_type.lower() not in ['all', 'dex', 'cex']: exchange_type = 'all'
            endpoint = endpoint.replace("centerType=all", f'centerType={exchange_type.lower()}')
            return (self.live_base_url, endpoint)
        else:
            endpoint = f"id={id}&convertId=2781&timeStart={period1}&timeEnd={period2}&interval=1d"
            return (self.historical_base_url, endpoint)

    def make(self, query, *args, **kwargs):
        if query.lower() == "historical":
            slug = args[0] if args else kwargs.get('slug')
            if slug is None: raise ValueError("Slug name must be provided for 'historical' queries.")
            slug = [slug] if isinstance(slug, str) else slug
            start = args[1] if len(args) > 1 else kwargs.get('start')
            end = args[2] if len(args) > 2 else kwargs.get('end')
            ID = self._normalize_ids(slug)
            ID = [str(ID)] if not isinstance(ID, list) else [str(i) for i in ID]
            if not start: raise ValueError("Both start and end dates are required for historical data.")
            start, end = _normalize_dates.norm(start, end, future_date_check=True, date_format="utc_unix")
            if self.historical_batching_enabled:
                urls = [self._construct_url(id=i, period1=start, period2=end) for i in ID]
                return urls if len(urls) > 1 else urls[0]
            else:
                return self._construct_url(id=ID[0], period1=start, period2=end)
        elif query.lower() == "live":
            slug = args[0] if args else kwargs.get('slug')
            if slug is None: raise ValueError("Slug name must be provided for 'live' queries.")
            slug = [slug] if isinstance(slug, str) else slug
            base = args[1] if len(args) > 1 else kwargs.get('baseCurrencySymbol')
            quote = args[2] if len(args) > 2 else kwargs.get('quoteCurrencySymbol')
            limit = args[3] if len(args) > 3 else kwargs.get('limit', 100)
            exch = args[4] if len(args) > 4 else kwargs.get('exchangeType', 'all')
            slug = self._normalize_slugs(slug)
            if self.live_batching_enabled and isinstance(slug, list) and len(slug) > 1:
                urls = [self._construct_url(id=s, baseCurrency=base, quoteCurrency=quote, limit=limit, exchange_type=exch) for s in slug]
                return urls if len(urls) > 1 else urls[0]
            else:
                if isinstance(slug, list): slug = slug[0]
                return self._construct_url(id=slug, baseCurrency=base, quoteCurrency=quote, limit=limit, exchange_type=exch)
    def __dir__(self): return ['make']
    

######################################################################
# CONSUMER PRICE INDEX DATA ROUTING AND URL CONSTRUCTION INTERFACE
######################################################################
class _CPI:
    """
    URL interface for generating FRED (Federal Reserve Economic Data) series URLs.

    The CPI class centralizes the construction of endpoint URLs for Consumer Price Index
    (CPI) and other economic indicators, using the FRED series identifier. It enforces
    input validation, provides a simple public interface, and ensures all URLs are
    properly formatted for downstream use.

    Workflow and Features:
      1. **Initialization:**
         - Stores the base URL for all FRED economic series.
         - Designed to work for CPI and any other FRED-supported series.

      2. **URL Construction:**
         - `_construct_url`: Internal helper that concatenates the supplied FRED
           series ID to the base URL, returning the canonical page for the indicator.

      3. **Main Routing (`make`):**
         - Public method that validates the presence of a `series_id`.
         - Delegates URL assembly to `_construct_url`, returning the ready-to-use URL.

      4. **Design Principles:**
         - Pure string assembly; never fetches, mutates, or validates series content.
         - Extensible for any FRED series; not just CPI.
         - Enforces required input and clean, canonical URL output.

    Example Usage:
        cpi = CPI()
        url = cpi.make("CPIAUCSL")
        url = cpi.make("UNRATE")

    Notes:
        - Always use the `make()` method for generating URLs (not `_construct_url`).
        - Will raise ValueError if a series_id is missing or empty.
        - Suitable for programmatic or end-user use as part of a data client.
    """	
    def __init__(self): self.base_url_cpi = 'https://fred.stlouisfed.org/series/'
    def _construct_url(self, series_id): return f"{self.base_url_cpi}{series_id}"
    def make(self, series_id, *args, **kwargs):
        if not series_id: raise ValueError("Series ID is required")
        return self._construct_url(series_id)
    def __dir__(self): return ['make']
    

######################################################################
# TREASURY DATA ROUTING AND URL CONSTRUCTION INTERFACE
######################################################################
class _TreasuryGov:
    """
    Routing and URL builder for U.S. Treasury.gov daily bill and yield curve data.

    The _TreasuryGov class centralizes construction of URLs for downloading daily treasury
    bill rates and daily treasury yield curve CSVs from the official U.S. Treasury site.
    It accepts flexible period specifications (year, year+month, current year), enforces
    correct input, and always returns canonical download URLs for use by client code.

    Workflow and Features:
      1. **Initialization:** Sets the base URL for all treasury rate downloads.

      2. **URL Construction (_construct_url):**
         - Accepts an identifier ("tbill" or "tyield") and optional period argument.
         - Dynamically resolves the year (from YYYY, YYYYMM, or "cy"/None for current year).
         - Selects the correct CSV resource type for bills or yields.
         - Always uses the year in both the path and query string.
         - Returns a fully-assembled, ready-to-download CSV URL.

      3. **Public Routing (make):**
         - Validates the requested query ("tbill" or "tyield").
         - Accepts flexible period via positional or keyword arg.
         - Delegates to `_construct_url`, returning the canonical download URL.
         - Raises ValueError for any unsupported identifier or malformed period.

    Example Usage:
        treasury = _TreasuryGov()
        url1 = treasury.make("tbill")
        url2 = treasury.make("tyield", period=2022)
        url3 = treasury.make("tbill", period=202203)

    Notes:
        - Always use the `make()` method for client code.
        - Only "tbill" and "tyield" are supported; periods must be None/"cy", a 4-digit year,
          or a 6-digit yyyymm (in which case, filter by month after download).
        - Designed for internal routing; no actual data is fetched or mutated.
        - Covers Treasury data from 1990 to present.
    """	
    def __init__(self):
        self.base_url = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/'
    def _construct_url(self, identifier, period=None):
        today = dtparse.nowCT(); current_year = today.year
        if identifier == 'tbill': csv_type = 'daily_treasury_bill_rates'
        elif identifier == 'tyield': csv_type = 'daily_treasury_yield_curve'
        else: raise ValueError(f"Unknown identifier: {identifier}")
        if period is None or str(period).lower() == 'cy': year = current_year
        else:
            p = str(period)
            if len(p) == 6 and p.isdigit(): year = int(p[:4])
            elif len(p) == 4 and p.isdigit(): year = int(p)
            else: raise ValueError("Period must be None, 'cy', a 4-digit year, or 6-digit yyyymm.")
        return f"{self.base_url}{year}/all?type={csv_type}&field_tdr_date_value={year}&page&_format=csv"
    def make(self, query, *args, **kwargs):
        period = args[0] if args else kwargs.get('period', None)
        if query.lower() == "tbill": return self._construct_url('tbill', period)
        elif query.lower() == "tyield": return self._construct_url('tyield', period)
        else: raise ValueError(f"Invalid query: {query}")
    def __dir__(self): return ['make']


# Instantiate data access classes for each adapter type:
crypto_adapter   = _Crypto()         # Access to cryptocurrency data (live and historical)
forex_adapter    = _Forex()          # Access to foreign exchange (FX) data and rates
equity_adapter   = _Equity()         # Access to equity/stock market data (prices, dividends, stats, etc.)
cpi_adapter      = _CPI()            # Access to Consumer Price Index (CPI) data series
treasury_adapter = _TreasuryGov()    # Access to US Treasury bill and yield data

def __dir__():
    return __all__


