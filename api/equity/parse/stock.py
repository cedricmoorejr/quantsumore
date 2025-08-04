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


# import re
from copy import deepcopy

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ...date_parser import dtparse
from ...proxy import Proxy
from ...exceptions import (
    # EquityPipelineError,
    # IPOError,
    IPONoDataError,
    IPODataUnavailableError,
    # LatestError,
    LatestNoDataError,
    LatestDataUnavailableError,
    # HistoricalError,
    HistoricalNoDataError,
    HistoricalDataUnavailableError,
    # LastTradeError,
    LastTradeNoDataError,
    LastTradeDataUnavailableError,
    QuoteStatisticsError,
    # QuoteStatisticsValidationError,
    QuoteStatisticsNoDataError,
    # QuoteStatisticsUnavailableError,
    CompanyProfileError,
    CompanyProfileValidationError,
    CompanyProfileNoDataError,
    # CompanyProfileUnavailableError,
)
# from ...markup import idextract


__all__ = [
        'historical',
        'latest',
        'profile',
        'quote_statistics',
    ]




# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire module; actual import occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  



######################################################################
# DATA TYPE 1
######################################################################
class profile:

    """
    Expected Input: Company Profile Data API Response (Index/Node-Mapped Format)

    This class expects as input the parsed JSON response for a company profile endpoint
    where structured company, executive, and filing information is packed into arrays and
    referenced via positional indices mapped by metadata keys. The format is optimized for compactness
    rather than human readability.

    Example Input Structure:
    [
      {
        "<string-key>": {   # Usually a URL-encoded request/endpoint signature
          "response": {
            "type": "data",
            "nodes": [
              { "type": "skip" },
              { "type": "skip" },
              {
                "type": "data",
                "data": [
                  # 0: Profile fields (mapping field names to array indices)
                  {
                    "profile": int,      # Index to company info
                    "logo": int,         # Index to company logo id
                    "logoURL": int,      # Index to company logo url
                    "description": int,  # Index to business description
                    "contact": int,      # Index to contact info
                    "details": int,      # Index to security details
                    "executives": int,   # Index to executives section
                    "filings": int       # Index to SEC filings section
                  },
                  # 1: Company info fields (name, industry, ceo, etc; mapped by index)
                  {
                    "name": int,
                    "country": int,
                    "founded": int,
                    "ipoDate": int,
                    "industry": int,
                    "sector": int,
                    "employees": int,
                    "ceo": int
                  },
                  # 2+: Data fields, in positional order, e.g.:
                  <company_name: str>,               # e.g., "NVIDIA Corporation"
                  <country: str>,                    # e.g., "United States"
                  <founded: int>,                    # e.g., 1993
                  <ipoDate: str>,                    # e.g., "1999-01-22"
                  {
                    "value": str, "url": str         # Industry value & link
                  },
                  <industry: str>,                   # e.g., "Semiconductors"
                  <industry_url: str>,               # e.g., "stocks/industry/semiconductors"
                  {
                    "value": str, "url": str         # Sector value & link
                  },
                  <sector: str>,                     # e.g., "Technology"
                  <sector_url: str>,                 # e.g., "stocks/sector/technology"
                  {
                    "value": str, "url": str         # Employees value & link
                  },
                  <employees: int>,                  # e.g., 36000
                  <employees_url: str>,              # e.g., "stocks/nvda/employees"
                  <ceo: str>,                        # e.g., "Jen-Hsun Huang"
                  # ...other basic info fields ...
                  <logo: bool>,                      # True/False if logo available
                  <logo_url: str>,                   # e.g., https://img.stockanalysis.com/...
                  <description: str>,                # HTML/escaped description
                  {
                    "address": int,                  # Index to address
                    "phone": int,                    # Index to phone
                    "website": int,                  # Index to website
                    "domain": int                    # Index to domain
                  },
                  <address: str>,
                  <phone: str>,
                  <website: str>,
                  <domain: str>,
                  {
                    "symbol": int,
                    "exchange": int,
                    "fiscalYear": int,
                    "currency": int,
                    "cik": int,
                    "cusip": int,
                    "isin": int,
                    "eid": int,
                    "sic": int,
                    "stockType": int,
                    "shareClass": int,
                    "securityName": int
                  },
                  <symbol: str>,
                  <exchange: str>,
                  <fiscalYear: str>,
                  <currency: str>,
                  <cik: str>,
                  <cusip: str>,
                  <isin: str>,
                  <eid: str>,
                  <sic: str>,
                  <stockType: str>,
                  <shareClass: str or None>,
                  # ...more details, as indexed...
                  [<executive_index_list: int>],
                  # Executives: repeated pattern of { "Name": int, "Title": int }, <name: str>, <title: str>
                  {
                    "Name": int,
                    "Title": int
                  },
                  <exec_name: str>,
                  <exec_title: str>,
                  # ...repeat for each executive...
                  [<filing_index_list: int>],
                  # Filings: repeated pattern of { "date": int, "path": int, "type": int, "title": int }, <date: str>, <path: str>, <type: str>, <title: str>
                  {
                    "date": int,
                    "path": int,
                    "type": int,
                    "title": int
                  },
                  <filing_date: str>,
                  <filing_path: str>,
                  <filing_type: str>,
                  <filing_title: str>,
                  # ...repeat for each filing...
                ],
                "uses": {
                  "search_params": [str],  # E.g., ["cache-bust"]
                  "params": [str]          # E.g., ["symbol"]
                }
              }
            ]
          }
        }
      }
      # ...more results if batch queries...
    ]

    Notes:
    - All content is index-mapped for compactness; use the first two "data" dicts as field-to-index guides.
    - Executives and filings are represented as a list of index blocks, each followed by the corresponding field values.
    - Company info, contact, and security details may have nested dicts with their own index mapping.
    - All string values may be HTML-escaped (e.g., `\u003Cbr\u003E` or `\u003Cp\u003E`).
    - Always check index existence and type before dereferencing—structure may vary by company or API version.

    This structure is highly compact but non-intuitive—**always use the provided index mapping** for extraction.
    """
    __slots__ = ("_raw","_payload","company_description","basic_info","industry_sector","employee_count","contact_details","executives","security_details","_data")
    def __init__(self, json_content=None):
        self._raw=None;self._payload=None;self._data=None;self.company_description=None;self.basic_info=None;self.industry_sector=None;self.employee_count=None;self.contact_details=None;self.executives=None;self.security_details=None
        if json_content is None: raise CompanyProfileNoDataError("No JSON content provided")
        self._raw = deepcopy(json_content); self._payload = self._response_status(json_content); self._populate_from_json(self._payload)
    @staticmethod
    def _replace_none_with_na(obj, na_type="N/A"):
        na_type = na_type if isinstance(na_type, str) and na_type.lower() in ("n/a","na") else None
        if isinstance(obj, dict): return {k:profile._replace_none_with_na(v) for k,v in obj.items()}
        elif isinstance(obj, list): return [profile._replace_none_with_na(item) for item in obj]
        elif obj is None: return na_type
        else: return obj
    @staticmethod
    def _to_dataframe(data):
        if isinstance(data, dict): return pd.DataFrame([data])
        elif isinstance(data, list) and all(isinstance(row, dict) for row in data): return pd.DataFrame(data)
        else: raise ValueError(f"Unsupported data type: {type(data)}")
    def _populate_from_json(self, payload):
        self.basic_info = self._extract_basic_info(payload)
        self.industry_sector = self._extract_industry_sector(payload)
        self.employee_count = self._extract_employee_count(payload)
        self.contact_details = self._extract_contact_details(payload)
        self.executives = self._extract_executives(payload)
        self.security_details = self._extract_security_details(payload)
        desc_dict = self._extract_description(payload)
        self.company_description = desc_dict.get("description")
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content)
        if isinstance(payload, list):
            if not payload: raise CompanyProfileError("Response not a non‐empty list")
            node = payload[0]
        elif isinstance(payload, dict): node = payload
        else: raise CompanyProfileError(f"Unsupported response type: {type(payload)}")
        if isinstance(node, dict) and len(node) == 1:
            key = next(iter(node))
            if isinstance(key, str) and '+' in key: node = node[key]
        if isinstance(node, dict) and "response" in node: node = node["response"]
        if not isinstance(node, dict): raise CompanyProfileError("Unexpected structure after unwrapping URL/response")
        if node.get("type") == "data" and isinstance(node.get("nodes"), list): return node
        raise CompanyProfileNoDataError("No valid data")
    @staticmethod
    def _core(payload): return payload["nodes"][2]["data"]
    @classmethod
    def _extract_basic_info(cls, payload):
        core, field_map = cls._core(payload), cls._core(payload)[1]
        info = {}
        for field, idx in field_map.items():
            val = core[idx]
            info[field] = core[val["value"]] if isinstance(val, dict) and "value" in val else val
        return info
    @classmethod
    def _extract_industry_sector(cls, payload):
        core, fm = cls._core(payload), cls._core(payload)[1]
        def unpack(idx):
            entry = core[idx]
            if isinstance(entry, dict) and "value" in entry and "url" in entry: return core[entry["value"]], core[entry["url"]]
            return entry, None
        industry, ind_url = unpack(fm["industry"]); sector, sec_url = unpack(fm["sector"])
        return {"industry":industry,"industry_url":ind_url,"sector":sector,"sector_url":sec_url}
    @classmethod
    def _extract_employee_count(cls, payload):
        core, fm = cls._core(payload), cls._core(payload)[1]
        emp_entry = core[fm["employees"]]
        employees = core[emp_entry["value"]] if isinstance(emp_entry, dict) else emp_entry
        return {"employees": employees}
    @classmethod
    def _extract_description(cls, payload):
        import re; core = cls._core(payload)
        raw_html = core[core[0]["description"]]
        return {"description": re.sub(r"<[^>]+>", "", raw_html).strip()}
    @classmethod
    def _extract_contact_details(cls, payload):
        core = cls._core(payload); contact_map = core[core[0]["contact"]]
        return {field: core[idx] for field, idx in contact_map.items()}
    @classmethod
    def _extract_executives(cls, payload):
        core = cls._core(payload); exec_section = core[0]["executives"]; execs = []
        for mi in core[exec_section]:
            mapping = core[mi]
            execs.append({"name":core[mapping["Name"]],"title":core[mapping["Title"]]})
        return execs
    @classmethod
    def _extract_security_details(cls, payload):
        core = cls._core(payload); details_map = core[core[0]["details"]]
        return {field: core[idx] for field, idx in details_map.items()}
    def as_dict(self):
        if self._data is None:
            if self._payload is None: raise CompanyProfileValidationError("No profile data loaded")
            basic_info = dict(self.basic_info) if self.basic_info else {}
            if self.employee_count and "employees" in self.employee_count: basic_info["employees"] = self.employee_count["employees"]
            self._data = {"basic_info":basic_info,"industry_sector":self.industry_sector,"contact_details":self.contact_details,"executives":self.executives,"security_details":self.security_details,"company_description":self.company_description}
        return self._data
    def DATA(self): return self._replace_none_with_na(self.as_dict())
    def __dir__(self): return ["DATA"]




class quote_statistics:
    """
    Expected Input: Quote Statistics API Response (Screener/Market Fundamentals Endpoint)

    This class expects, as input, the parsed JSON response from a quote statistics or market screener API.
    The data structure summarizes real-time and fundamental statistics for a given equity (by symbol).

    Example Input Structure:
    [
      {
        "<string-key>": {   # Usually a URL-encoded query string or endpoint signature
          "response": {
            "status": int,             # HTTP-like status code (e.g., 200 for success)
            "data": {
              "data": [
                {
                  "s": str,            # Symbol (e.g., "$NVDA")
                  "n": str,            # Company name (e.g., "NVIDIA Corporation")
                  "marketCap": float,  # Market capitalization
                  "price": float,      # Last trade price
                  "volume": float,     # Trading volume
                  "peRatio": float,    # Price/Earnings ratio
                  "open": float,       # Opening price
                  "close": float,      # Previous close
                  "low": float,        # Session low
                  "high": float,       # Session high
                  "dividendYield": float,    # Dividend yield (%)
                  "low52": float,            # 52-week low
                  "high52": float,           # 52-week high
                  "priceTarget": float,      # Analyst price target
                  "exDivDate": str,          # Ex-dividend date (YYYY-MM-DD)
                  "nextEarningsDate": str,   # Next earnings report date (YYYY-MM-DD)
                  "averageVolume": float,    # Average volume (period depends on API)
                  "eps": float,              # Earnings per share
                  "beta": float              # Beta (volatility measure)
                }
                # ...more securities if requested in batch (usually length 1)
              ],
              "resultsCount": int           # Number of records in "data" array
            }
          }
        }
      }
      # ...more entries if batched...
    ]

    Notes:
    - The top-level list supports batch queries.
    - "<string-key>" is typically the request signature or endpoint+params.
    - The "data" array contains one dict per equity/security (typically just one per request).
    - All fields may be missing/null if data is unavailable for the requested symbol.
    - Date fields are ISO date strings (YYYY-MM-DD).
    """
    __slots__ = ("_raw","_payload","symbol","name","market_cap","price","volume","pe_ratio","open","close","low","high","dividend_yield","low52","high52","price_target","ex_div_date","next_earnings_date","average_volume","eps","beta")
    METRIC_KEY_MAP = {
        's':'Ticker','n':'Company Name','close':'Previous Close','open':'Open','low':'Day\'s Low','high':'Day\'s High','low52':'52W Low',
        'high52':'52W High','bid':'Bid','ask':'Ask','volume':'Volume','averageVolume':'Avg. Volume','marketCap':'Market Cap','beta':'Beta (5Y Monthly)','peRatio':'PE Ratio',
        'eps':'EPS','dividendYield':'Dividend Yield','exDivDate':'Ex-Dividend Date','nextEarningsDate':'Earnings Date','priceTarget':'Price Target',
    }
    def __init__(self, json_content=None):
        self._raw=None; self._payload=None
        self.symbol=None; self.name=None; self.market_cap=None; self.price=None; self.volume=None; self.pe_ratio=None; self.open=None; self.close=None; self.low=None; self.high=None; self.dividend_yield=None; self.low52=None; self.high52=None; self.price_target=None; self.ex_div_date=None; self.next_earnings_date=None; self.average_volume=None; self.eps=None; self.beta=None
        if json_content is None: raise QuoteStatisticsNoDataError("No JSON content provided")
        self._raw = deepcopy(json_content); self._payload = self._response_status(json_content); self._populate_from_json(self._payload)
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content)
        if isinstance(payload, list):
            if not payload: raise QuoteStatisticsError("Response not a non‐empty list")
            node = payload[0]
        elif isinstance(payload, dict): node = payload
        else: raise QuoteStatisticsError(f"Unsupported response type: {type(payload)}")
        if isinstance(node, dict) and len(node) == 1:
            key = next(iter(node))
            if isinstance(key, str) and '+' in key: node = node[key]
        if isinstance(node, dict) and "response" in node: node = node["response"]
        if not isinstance(node, dict) or "data" not in node or "status" not in node: raise QuoteStatisticsError("Unexpected structure after unwrapping URL/response")
        data_section = node.get("data")
        if (not isinstance(data_section, dict) or "data" not in data_section or not isinstance(data_section["data"], list) or len(data_section["data"]) == 0):
            raise QuoteStatisticsNoDataError("No valid data found in response")
        return node
    def _populate_from_json(self, payload):
        record = payload["data"]["data"][0]
        field_map = {
            "s":"symbol","n":"name","marketCap":"market_cap","price":"price","volume":"volume","peRatio":"pe_ratio","open":"open",
            "close":"close","low":"low","high":"high","dividendYield":"dividend_yield","low52":"low52","high52":"high52","priceTarget":"price_target",
            "exDivDate":"ex_div_date","nextEarningsDate":"next_earnings_date","averageVolume":"average_volume","eps":"eps","beta":"beta",
        }
        for json_key, attr in field_map.items(): setattr(self, attr, record.get(json_key))
    @staticmethod
    def _replace_none_with_na(obj, na_value="N/A"):
        if isinstance(obj, dict): return {k: quote_statistics._replace_none_with_na(v, na_value) for k,v in obj.items()}
        elif isinstance(obj, list): return [quote_statistics._replace_none_with_na(v, na_value) for v in obj]
        elif obj is None: return na_value
        else: return obj
    def _metrics(self):
        record = self._payload["data"]["data"][0]; out = {}
        for api_key, human in self.METRIC_KEY_MAP.items():
            value = record.get(api_key)
            if human=="Ticker" and isinstance(value, str): value = value.lstrip('$').strip()
            out[human] = value
        low, high = record.get('low'), record.get('high')
        out["Day's Range"] = f"{low} - {high}" if low is not None and high is not None else None
        low52, high52 = record.get('low52'), record.get('high52')
        out["52 Week Range"] = f"{low52} - {high52}" if low52 is not None and high52 is not None else None
        out.setdefault('Bid', None); out.setdefault('Ask', None)
        return out
    def DATA(self):
        raw_metrics = self._metrics()
        return self._replace_none_with_na(raw_metrics)
    def __dir__(self): return ["DATA"]





######################################################################
# DATA TYPE 2
######################################################################
class latest:
    """
    Expected Input: Intraday "Latest" Price and Minute-Bar API Response ("spark" endpoint)

    This class expects as input the parsed JSON response for the latest price and intraday minute-bar data
    for a single financial instrument (e.g., stock, ETF, crypto). The input is a list containing one or more
    objects, each keyed by a unique request string (often the full endpoint and parameters).

    Example Input Structure:
    [
      {
        "<string-key>": {   # Typically a URL-encoded string or endpoint signature
          "response": {
            "spark": {
              "result": [
                {
                  "symbol": str,         # e.g., "NVDA"
                  "response": [
                    {
                      "meta": {
                        "currency": str,                # e.g., "USD"
                        "symbol": str,                  # e.g., "NVDA"
                        "exchangeName": str,            # e.g., "NMS"
                        "fullExchangeName": str,        # e.g., "NasdaqGS"
                        "instrumentType": str,          # e.g., "EQUITY"
                        "firstTradeDate": int,          # Unix timestamp
                        "regularMarketTime": int,       # Unix timestamp for latest tick
                        "hasPrePostMarketData": bool,
                        "gmtoffset": int,               # GMT offset in seconds
                        "timezone": str,                # e.g., "EDT"
                        "exchangeTimezoneName": str,    # e.g., "America/New_York"
                        "regularMarketPrice": float,    # Latest trade price
                        "fiftyTwoWeekHigh": float,
                        "fiftyTwoWeekLow": float,
                        "regularMarketDayHigh": float,
                        "regularMarketDayLow": float,
                        "regularMarketVolume": int,
                        "longName": str,                # e.g., "NVIDIA Corporation"
                        "shortName": str,               # e.g., "NVIDIA Corporation"
                        "chartPreviousClose": float,
                        "previousClose": float,
                        "scale": int,                   # Number of decimals for price display
                        "priceHint": int,
                        "currentTradingPeriod": {
                          "pre": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          },
                          "regular": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          },
                          "post": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          }
                        },
                        "tradingPeriods": [
                          [
                            {
                              "timezone": str,
                              "end": int,
                              "start": int,
                              "gmtoffset": int
                            }
                            # ... possibly more trading period dicts ...
                          ]
                        ],
                        "dataGranularity": str,         # e.g., "1m"
                        "range": str,                   # e.g., "1d"
                        "validRanges": [str],           # Allowed ranges, e.g., ["1d", "5d", ...]
                      },
                      "timestamp": [int],               # List of UNIX timestamps for each minute bar
                      "indicators": {
                        "quote": [
                          {
                            "close": [float],           # List of close prices (aligned to timestamp)
                            # Optionally: "open", "high", "low", "volume"
                          }
                        ]
                      }
                      # ...possible additional keys, e.g., "adjclose"
                    }
                    # ...possibly more response objects
                  ]
                }
                # ...more symbols if batch request
              ],
              "error": None or {}  # Error object on failure, else None
            }
          }
        }
      }
      # ...more result objects for batch queries...
    ]

    Notes:
    - The top-level list supports batching (multiple symbols/queries).
    - The "<string-key>" is typically the unique request string or endpoint signature.
    - The "result" array contains a dict per symbol; each symbol has a "response" list (usually length 1).
    - Timestamps and indicator arrays (such as "close") are strictly aligned by index.
    - Not all indicator arrays ("open", "high", "low", "volume") may be present, depending on API permissions or symbol.
    - "error" is only populated on request failure.
    - Defensive parsing is attempted; field presence may vary by instrument, trading session, or API changes.
    """
    __slots__ = ('_raw', '_record', 'symbol', 'meta', 'timestamps', 'close_prices', 'longName', 'shortName')
    def __init__(self, json_content=None):
        self._raw = None; self._record = None; self.symbol = None; self.longName = None; self.shortName = None; self.meta = {}; self.timestamps = []; self.close_prices = []
        if json_content is None: raise LatestDataUnavailableError("No JSON content provided")
        self._raw = deepcopy(json_content); self._record = self._response_status(self._raw); self._populate()
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content)
        if isinstance(payload, list):
            if not payload: raise LatestDataUnavailableError("Empty list at top level")
            node = payload[0]
        elif isinstance(payload, dict): node = payload
        else: raise LatestDataUnavailableError(f"Unsupported JSON type: {type(payload)}")
        if isinstance(node, dict) and len(node) == 1:
            key = next(iter(node))
            if isinstance(key, str) and '+' in key: node = node[key]
        if isinstance(node, dict) and "response" in node: node = node["response"]
        else: raise LatestDataUnavailableError("Missing 'response' field")
        if isinstance(node, dict) and "spark" in node: node = node["spark"]
        else: raise LatestDataUnavailableError("Missing 'spark' field")
        result = node.get("result")
        if not isinstance(result, list) or not result: raise LatestNoDataError("No 'result' data present")
        return result[0]
    def _populate(self):
        rec = self._record
        self.symbol = rec.get("symbol")
        responses = rec.get("response")
        if not isinstance(responses, list) or not responses: raise LatestNoDataError("No 'response' sub‑array found")
        resp0 = responses[0]
        self.meta = resp0.get("meta", {})
        self.longName = "".join(self.meta.get("longName", None).split()) if self.meta.get("longName", None) else None
        self.shortName = "".join(self.meta.get("shortName", None).split()) if self.meta.get("shortName", None) else None
        ts = resp0.get("timestamp")
        if not isinstance(ts, list): raise LatestNoDataError("Missing or invalid 'timestamp'")
        self.timestamps = ts
        indicators = resp0.get("indicators", {}); quote_list = indicators.get("quote", [])
        self.close_prices = quote_list[0].get("close", []) if quote_list and isinstance(quote_list, list) else []
        if len(self.timestamps) != len(self.close_prices): raise LatestDataUnavailableError(f"Timestamp ({len(self.timestamps)}) vs close ({len(self.close_prices)}) length mismatch")
    @property
    def latest_price(self):
        if not self.close_prices: raise LatestDataUnavailableError("No price series available")
        return self.close_prices[-1]
    @property
    def latest_timestamp(self):
        if not self.timestamps: raise LatestDataUnavailableError("No timestamp series available")
        return self.timestamps[-1]
    def DATA(self):
        ts = self.latest_timestamp; price = self.latest_price; rm_tm = self.meta.get("regularMarketTime")
        result = {
            "Ticker": self.symbol, "Price": price,
            "lastPriceTime": dtparse.unix_timestamp(ts, format='%Y-%m-%d %I:%M %p', to_unix=False),
            "regularMarketTime": dtparse.unix_timestamp(rm_tm, format='%Y-%m-%d %I:%M %p', to_unix=False),
        }
        if self.longName and self.longName == self.shortName: result["Name"] = self.longName
        else:
            if self.longName: result["longName"] = self.longName
            if self.shortName: result["shortName"] = self.shortName
        if "Name" in result: order = ['Ticker', 'Name', 'Price', 'lastPriceTime', 'regularMarketTime']
        else: order = ['Ticker', 'longName', 'shortName', 'Price', 'lastPriceTime', 'regularMarketTime']
        return {k: result[k] for k in order if k in result}
    def __repr__(self):
        count = len(self.timestamps) if self.timestamps else 0
        return f"<latest symbol={self.symbol!r}, points={count}>"
    def __dir__(self): return ["DATA"]



class last:
    """
    Expected Input: Latest Price & Historical Time-Series API Response ("spark" endpoint)

    This class expects, as input, the parsed JSON response for the latest price and historical timeseries data
    for a single financial instrument (e.g., stock, ETF, crypto). The input is a list containing one or more
    objects, each keyed by a unique request string (often the full endpoint with params).

    Example Input Structure:
    [
      {
        "<string-key>": {   # Usually a URL-encoded string or endpoint signature (e.g. "...+NVDA&range=1y...")
          "response": {
            "spark": {
              "result": [
                {
                  "symbol": str,     # e.g. "NVDA"
                  "response": [
                    {
                      "meta": {
                        "currency": str,                # e.g. "USD"
                        "symbol": str,                  # e.g. "NVDA"
                        "exchangeName": str,            # e.g. "NMS"
                        "fullExchangeName": str,        # e.g. "NasdaqGS"
                        "instrumentType": str,          # e.g. "EQUITY"
                        "firstTradeDate": int,          # Unix timestamp
                        "regularMarketTime": int,       # Unix timestamp
                        "hasPrePostMarketData": bool,
                        "gmtoffset": int,               # Offset from GMT (in seconds)
                        "timezone": str,                # e.g. "EDT"
                        "exchangeTimezoneName": str,    # e.g. "America/New_York"
                        "regularMarketPrice": float,    # Latest available price
                        "fiftyTwoWeekHigh": float,
                        "fiftyTwoWeekLow": float,
                        "regularMarketDayHigh": float,
                        "regularMarketDayLow": float,
                        "regularMarketVolume": int,
                        "longName": str,                # e.g. "NVIDIA Corporation"
                        "shortName": str,               # e.g. "NVIDIA Corporation"
                        "chartPreviousClose": float,
                        "priceHint": int,
                        "currentTradingPeriod": {
                          "pre": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          },
                          "regular": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          },
                          "post": {
                            "timezone": str,
                            "end": int,
                            "start": int,
                            "gmtoffset": int
                          }
                        },
                        "dataGranularity": str,         # e.g. "1d"
                        "range": str,                   # e.g. "1y"
                        "validRanges": [str],           # e.g. ["1d", "5d", ...]
                      },
                      "timestamp": [int],               # List of UNIX timestamps, one per bar
                      "indicators": {
                        "quote": [
                          {
                            "close": [float],           # Closing prices, aligned by index to "timestamp"
                            # Optionally: "open", "high", "low", "volume" arrays
                          }
                        ]
                      }
                      # ...possibly other time-series data, e.g. "adjclose", "volume"
                    }
                    # ...possibly more response objects
                  ]
                  # ...possibly other fields (e.g. "error" for failure cases)
                }
                # ...more symbol results if batched
              ],
              "error": None or {}  # Error info if present, else None
            }
          }
        }
      }
      # ...more entries if batched
    ]

    Notes:
    - The outer list allows for batch queries (multiple instruments in one request).
    - "<string-key>" is typically the request signature (endpoint + params).
    - The `"result"` list contains a dict per symbol/instrument. Each symbol may have one or more `"response"` entries (usually one).
    - Timestamps and indicator arrays (like `"close"`, `"open"`, etc.) are aligned by index (i.e., `close[i]` is the close for `timestamp[i]`).
    - Some fields (e.g., `"open"`, `"high"`, `"low"`, `"volume"`) may be omitted depending on request granularity or permissions.
    - `"error"` is present if the request fails for a symbol; otherwise it's `None`.

    Always check for missing or `None` fields defensively.
    """
    __slots__ = ("_raw", "_record", "symbol", "longName", "shortName", "meta", "timestamps", "close_prices", "data")
    def __init__(self, json_content=None):
        self._raw = None; self._record = None; self.symbol = None; self.longName = None; self.shortName = None; self.meta = {}; self.timestamps = []; self.close_prices = []; self.data = None
        if json_content is None: raise LastTradeDataUnavailableError("No JSON content provided")
        self._raw = deepcopy(json_content)
        self._record = self._response_status(self._raw)
        self._populate()
        self._create_dataframe()
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content)
        if isinstance(payload, list):
            if not payload: raise LastTradeDataUnavailableError("Empty list at top level")
            node = payload[0]
        elif isinstance(payload, dict): node = payload
        else: raise LastTradeDataUnavailableError(f"Unsupported JSON type: {type(payload)}")
        if isinstance(node, dict) and len(node) == 1:
            key = next(iter(node))
            if isinstance(key, str) and "+" in key: node = node[key]
        try: node = node["response"]["spark"]["result"]
        except Exception: raise LastTradeDataUnavailableError("Missing one of: 'response', 'spark', or 'result'")
        if not isinstance(node, list) or not node: raise LastTradeNoDataError("No 'result' data present")
        return node[0]
    def _populate(self):
        rec = self._record
        self.symbol = rec.get("symbol")
        responses = rec.get("response")
        if not isinstance(responses, list) or not responses: raise LastTradeNoDataError("No 'response' sub-array found")
        resp0 = responses[0]
        self.meta = resp0.get("meta", {})
        self.longName = self.meta.get("longName")
        self.shortName = self.meta.get("shortName")
        ts = resp0.get("timestamp")
        if not isinstance(ts, list): raise LastTradeNoDataError("Missing or invalid 'timestamp'")
        self.timestamps = ts
        quote_list = resp0.get("indicators", {}).get("quote", [])
        self.close_prices = quote_list[0].get("close", []) if quote_list and isinstance(quote_list, list) else []
        if len(self.timestamps) != len(self.close_prices):
            raise LastTradeDataUnavailableError(f"Timestamp ({len(self.timestamps)}) vs close ({len(self.close_prices)}) length mismatch")
    def _create_dataframe(self):
        company = self.longName or self.shortName or self.meta.get("shortName") or ""
        df = pd.DataFrame({
            "Symbol": [self.symbol]*len(self.timestamps), "Timestamp": self.timestamps, "Close Price": self.close_prices,
            "Market Price": [self.meta.get("regularMarketPrice")]*len(self.timestamps),
            "Day High": [self.meta.get("regularMarketDayHigh")]*len(self.timestamps),
            "Day Low": [self.meta.get("regularMarketDayLow")]*len(self.timestamps),
            "Volume": [self.meta.get("regularMarketVolume")]*len(self.timestamps),
            "Company Name": [company]*len(self.timestamps),
        })
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
        df = df[["Timestamp", "Symbol", "Company Name", "Close Price", "Market Price", "Day High", "Day Low", "Volume"]]
        self.data = df
    def DATA(self):
        if self.data is None or self.data.empty: raise LastTradeDataUnavailableError("No data available to return")
        return self.data
    def __repr__(self):
        cnt = len(self.timestamps) if self.timestamps else 0
        return f"<latest(symbol={self.symbol!r}, points={cnt})>"
    def __dir__(self): return ["DATA"]

       


class historical:
    """
    Expected Input: Historical Price Data API Response ("chart" endpoint)

    This class expects as input the parsed JSON response for historical price data for a single security
    (e.g., stock, ETF, or crypto). The structure is tailored to a "chart" API, delivering
    daily or custom-interval time series data, including open, high, low, close, volume, and adjusted close prices.

    Example Input Structure:
    [
      {
        "<string-key>": {   # Typically a URL-encoded query string or endpoint signature
          "response": {
            "chart": {
              "result": [
                {
                  "meta": {
                    "currency": str,                # e.g., "USD"
                    "symbol": str,                  # e.g., "NVDA"
                    "exchangeName": str,            # e.g., "NMS"
                    "fullExchangeName": str,        # e.g., "NasdaqGS"
                    "instrumentType": str,          # e.g., "EQUITY"
                    "firstTradeDate": int,          # Unix timestamp
                    "regularMarketTime": int,       # Unix timestamp (latest tick)
                    "hasPrePostMarketData": bool,
                    "gmtoffset": int,               # GMT offset in seconds
                    "timezone": str,                # e.g., "EDT"
                    "exchangeTimezoneName": str,    # e.g., "America/New_York"
                    "regularMarketPrice": float,    # Latest market price
                    "fiftyTwoWeekHigh": float,
                    "fiftyTwoWeekLow": float,
                    "regularMarketDayHigh": float,
                    "regularMarketDayLow": float,
                    "regularMarketVolume": int,
                    "longName": str,
                    "shortName": str,
                    "chartPreviousClose": float,
                    "priceHint": int,
                    "currentTradingPeriod": {
                      "pre": {
                        "timezone": str,
                        "start": int,
                        "end": int,
                        "gmtoffset": int
                      },
                      "regular": {
                        "timezone": str,
                        "start": int,
                        "end": int,
                        "gmtoffset": int
                      },
                      "post": {
                        "timezone": str,
                        "start": int,
                        "end": int,
                        "gmtoffset": int
                      }
                    },
                    "dataGranularity": str,         # e.g., "1d"
                    "range": str,                   # (can be empty string)
                    "validRanges": [str]            # Allowed ranges
                  },
                  "timestamp": [int],               # List of UNIX timestamps for each bar (aligned with OHLCV)
                  "indicators": {
                    "quote": [
                      {
                        "open": [float],            # Open prices per bar (aligned by index)
                        "high": [float],            # High prices per bar
                        "low": [float],             # Low prices per bar
                        "close": [float],           # Close prices per bar
                        "volume": [int]             # Volume per bar
                      }
                    ],
                    "adjclose": [
                      {
                        "adjclose": [float]         # Adjusted close prices per bar
                      }
                    ]
                  }
                  # ...possibly more fields...
                }
                # ...more results for batch/overlay queries (rare)
              ],
              "error": None or {}                    # Error info if request fails, else None
            }
          }
        }
      }
      # ...more items if batch queries...
    ]

    Notes:
    - The top-level list supports batch queries (multiple symbols/requests).
    - "<string-key>" is typically the request signature.
    - "result" is an array; for most use cases only the first entry is needed.
    - All time series arrays ("open", "high", "low", "close", "volume", "adjclose") are aligned by index to "timestamp".
    - Not all fields may be present for every symbol or interval (e.g., "adjclose" sometimes omitted).
    - Defensive parsing is attempted, as field presence and array lengths may vary.
    - Date/time fields are Unix timestamps (seconds since epoch).
    """
    __slots__ = ("_raw", "_records", "_rows", "data")
    def __init__(self, json_content=None):
        self._raw = None; self._records = []; self._rows = []; self.data = None
        if json_content is None: raise HistoricalDataUnavailableError("No JSON content provided")
        self._raw = deepcopy(json_content)
        self._records = self._response_status(self._raw)
        if not self._records: raise HistoricalNoDataError("No historical result data present")
        self._parse_rows()
        if not self._rows: raise HistoricalNoDataError("No valid data points found after parsing")
        self._create_dataframe()
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content); records = []
        if isinstance(payload, list):
            for entry in payload:
                if not isinstance(entry, dict): continue
                inner = next(iter(entry.values())); resp = inner.get("response", {}); chart = resp.get("chart", {})
                if chart.get("error"): continue
                result = chart.get("result", [])
                if isinstance(result, list): records.extend(result)
        elif isinstance(payload, dict):
            chart = payload.get("chart", {})
            if chart.get("error"): raise HistoricalDataUnavailableError(f"Chart error: {chart['error']}")
            result = chart.get("result", [])
            if isinstance(result, list): records.extend(result)
        else: raise HistoricalDataUnavailableError(f"Unsupported payload type: {type(payload)}")
        return records
    def _parse_rows(self):
        for rec in self._records:
            meta = rec.get("meta", {}); symbol = meta.get("symbol")
            company = meta.get("longName") or meta.get("shortName") or ""
            timestamps = rec.get("timestamp", [])
            quote_list = rec.get("indicators", {}).get("quote", []); adj_list = rec.get("indicators", {}).get("adjclose", [])
            quote = quote_list[0] if quote_list else {}; adj = adj_list[0] if adj_list else {}
            for i, ts in enumerate(timestamps):
                self._rows.append({
                    "Timestamp": ts, "Symbol": symbol, "Company Name": company,
                    "Open": quote.get("open", [None])[i], "High": quote.get("high", [None])[i],
                    "Low": quote.get("low", [None])[i], "Close": quote.get("close", [None])[i],
                    "Adj Close": adj.get("adjclose", [None])[i], "Volume": quote.get("volume", [None])[i],
                    "Currency": meta.get("currency"), "Exchange Name": meta.get("exchangeName"),
                    "Full Exchange Name": meta.get("fullExchangeName"), "Instrument Type": meta.get("instrumentType"),
                    "First Trade Date": meta.get("firstTradeDate"), "Regular Market Price": meta.get("regularMarketPrice"),
                    "52 Week High": meta.get("fiftyTwoWeekHigh"), "52 Week Low": meta.get("fiftyTwoWeekLow"),
                    "Day High": meta.get("regularMarketDayHigh"), "Day Low": meta.get("regularMarketDayLow"),
                    "Regular Market Volume": meta.get("regularMarketVolume"), "Market Time": meta.get("regularMarketTime"),
                })
    def _create_dataframe(self):
        df = pd.DataFrame(self._rows)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
        df["First Trade Date"] = pd.to_datetime(df["First Trade Date"], unit="s", errors="coerce")
        df["Market Time"] = pd.to_datetime(df["Market Time"], unit="s", errors="coerce")
        desired = ["Timestamp", "Symbol", "Company Name", "Open", "High", "Low", "Close", "Adj Close", "Volume",
                   "Currency", "Exchange Name", "Full Exchange Name", "Instrument Type", "First Trade Date",
                   "Regular Market Price", "52 Week High", "52 Week Low", "Day High", "Day Low", "Regular Market Volume", "Market Time"]
        df = df[[c for c in desired if c in df.columns]]
        self.data = df
    def DATA(self):
        if self.data is None or self.data.empty: raise HistoricalNoDataError("No historical data available")
        return self.data
    def __repr__(self):
        count = len(self.data) if self.data is not None else 0
        symbol = self.data["Symbol"].iat[0] if count > 0 else None
        return f"<historical symbol={symbol!r}, points={count}>"
    def __dir__(self): return ['DATA']


######################################################################
# DATA TYPE 3
######################################################################
class ipo:
    """
    Expected Input: IPO Calendar API Response

    This class expects as input the parsed JSON response for an IPO (Initial Public Offering) calendar
    API, summarizing priced, filed, upcoming, and withdrawn IPO deals for a given time period.

    Example Input Structure:
    [
      {
        "<string-key>": {   # Usually a URL-encoded query string or endpoint signature (e.g., "...+2025-06")
          "response": {
            "data": {
              "priced": {
                "asOf": null or str,
                "headers": {                # Mapping of data keys to column headers
                  "proposedTickerSymbol": str,
                  "companyName": str,
                  "proposedExchange": str,
                  "proposedSharePrice": str,
                  "sharesOffered": str,
                  "pricedDate": str,
                  "dollarValueOfSharesOffered": str,
                  "dealStatus": str
                },
                "rows": [
                  {
                    "dealID": str,
                    "proposedTickerSymbol": str,
                    "companyName": str,
                    "proposedExchange": str,
                    "proposedSharePrice": str,
                    "sharesOffered": str,
                    "pricedDate": str,                # Format: "M/D/YYYY"
                    "dollarValueOfSharesOffered": str,
                    "dealStatus": str                  # e.g., "Priced"
                  },
                  # ...more priced IPOs...
                ]
              },
              "upcoming": {
                "upcomingTable": {
                  "asOf": null or str,
                  "headers": null or dict,
                  "rows": null or list
                },
                "lastUpdatedTime": str                # e.g., "LAST UPDATED: 07/31/2025* - Source: EDGAR® Online"
              },
              "filed": {
                "asOf": null or str,
                "headers": {                          # Mapping for filed IPOs
                  "proposedTickerSymbol": str,
                  "companyName": str,
                  "filedDate": str,
                  "dollarValueOfSharesOffered": str
                },
                "rows": [
                  {
                    "dealID": str,
                    "proposedTickerSymbol": str or null,
                    "companyName": str,
                    "filedDate": str,                 # Format: "M/D/YYYY"
                    "dollarValueOfSharesOffered": str
                  },
                  # ...more filed IPOs...
                ]
              },
              "withdrawn": {
                "asOf": null or str,
                "headers": {                          # Mapping for withdrawn IPOs
                  "proposedTickerSymbol": str,
                  "companyName": str,
                  "proposedExchange": str,
                  "sharesOffered": str,
                  "filedDate": str,
                  "dollarValueOfSharesOffered": str,
                  "withdrawDate": str
                },
                "rows": [
                  {
                    "dealID": str,
                    "proposedTickerSymbol": str or null,
                    "companyName": str,
                    "proposedExchange": str or null,
                    "sharesOffered": str,
                    "filedDate": str,
                    "dollarValueOfSharesOffered": str,
                    "withdrawDate": str
                  },
                  # ...more withdrawn IPOs...
                ]
              },
              "month": int,                           # Numeric month (e.g., 6)
              "year": int,                            # Numeric year (e.g., 2025)
              "totalResults": int                     # Total IPOs in the period (may only count one category)
            },
            "message": str or null,                   # Usually null
            "status": {
              "rCode": int,                           # e.g., 200 (success)
              "bCodeMessage": [
                {
                  "code": int,
                  "errorMessage": str                 # May indicate missing or partial data (e.g., "Upcoming:No record found.")
                },
                # ...more status messages...
              ],
              "developerMessage": str or null
            }
          }
        }
      }
      # ...more entries if batched
    ]

    Notes:
    - The top-level list supports batch queries for multiple date ranges.
    - "<string-key>" is the endpoint+params signature, often includes the query month.
    - “priced”, “filed”, and “withdrawn” each have their own `headers` mapping and `rows` with actual IPO records.
    - Fields are always strings, and may be empty/null if not reported.
    - Defensive parsing is attempted; check for nulls and empty arrays.
    """
    __slots__ = ("_raw", "_payload", "_rows", "data")
    def __init__(self, json_content=None):
        self._raw = None; self._payload = {}; self._rows = []; self.data = None
        if json_content is None: raise IPODataUnavailableError("No JSON content provided")
        self._raw = deepcopy(json_content)
        resp = self._response_status(self._raw)
        data_section = resp.get("data", {})
        if data_section.get("totalResults", 0) < 1: raise IPONoDataError("No IPO records found")
        self._payload = data_section
        self._parse_rows()
        if not self._rows: raise IPONoDataError("No valid IPO rows to parse")
        self._create_dataframe()
    @staticmethod
    def _response_status(json_content):
        payload = deepcopy(json_content)
        if isinstance(payload, list):
            if not payload: raise IPODataUnavailableError("Empty list at top level")
            node = payload[0]
        elif isinstance(payload, dict): node = payload
        else: raise IPODataUnavailableError(f"Unsupported JSON type: {type(payload)}")
        if isinstance(node, dict) and len(node) == 1:
            key = next(iter(node))
            if "+" in key: node = node[key]
        resp = node.get("response")
        if not isinstance(resp, dict): raise IPODataUnavailableError("Missing or invalid 'response' field")
        return resp
    def _parse_rows(self):
        priced = self._payload.get("priced", {})
        for entry in priced.get("rows", []):
            self._rows.append({
                "Ticker_Symbol": entry.get("proposedTickerSymbol"),
                "Company_Name": entry.get("companyName"),
                "Exchange": entry.get("proposedExchange"),
                "IPO_Price": entry.get("proposedSharePrice"),
                "Shares_Offered": entry.get("sharesOffered"),
                "IPO_Date": entry.get("pricedDate"),
                "Total_Offer_Amount": entry.get("dollarValueOfSharesOffered"),
            })
    def _create_dataframe(self):
        df = pd.DataFrame(self._rows)
        df["Total_Offer_Amount"] = df["Total_Offer_Amount"].replace(r"[\$,]", "", regex=True).astype(float)
        df["IPO_Date"] = pd.to_datetime(df["IPO_Date"], format="%m/%d/%Y", errors="coerce")
        df = df[["Ticker_Symbol","Company_Name","Exchange","IPO_Price","Shares_Offered","IPO_Date","Total_Offer_Amount"]]
        self.data = df
    def DATA(self):
        if self.data is None or self.data.empty: raise IPONoDataError("IPO data unavailable or empty")
        return self.data
    def __repr__(self):
        count = len(self.data) if self.data is not None else 0
        return f"<ipo rows={count}>"
    def __dir__(self): return ['DATA']



def __dir__():
    return __all__






