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
from copy import deepcopy

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
# from ...market_utils import fxutil, forex_hours
from ...market_utils import fxutil
from ...shape_tools import is_valid_dataframe
from ...parse_tools import convert_to_float
from ...date_parser import dtparse
from ...strata_utils import IterDict
from ...proxy import Proxy
from ...exceptions import (
    # FXPipelineError,
    # FXInterbankError,
    FXNoDataError,
    FXDataUnavailableError,
    # FXInterbankNoDataError,
    FXInterbankDataUnavailableError,
    LiveBidAskNoDataError,
    LiveBidAskUnavailableError,
    # LiveQuoteValidationError,
    # LiveQuoteUnavailableError,
    # ConversionValidationError,
    ConversionUnavailableError,
    ConversionNoDataError,
    InvalidCurrencyPairError,
    CurrencyPairNotFoundError,
    ConversionError,
)
from ...markup import idextract  


__all__ = [
    'fx_historical', 
    'conversion', 
    'live_quote',
    'fx_interbank_rates',
    'live_bid_ask'
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
class fx_historical:
    """
    Expected Input: Historical FX Rates API Response

    This class expects as input the parsed JSON response for historical foreign exchange rates.
    The input structure includes a list of daily exchange rates for a specified currency pair, 
    each with its value and the date of the quote, as returned by the API.

    Example structure:
    [
      {
        "<string-key>": {
          "response": {
            "d": [
              {
                "RatePair": str,         # Currency pair, e.g. "EURUSD"
                "RatePairValue": float,  # Exchange rate value
                "LastUpdate": str,       # Date/time, e.g. "Sun, 01 Jan 2023 00:00:00"
                "CallCount": int         # API usage tracker (typically 0)
              }
              # ...more daily rate objects...
            ]
          }
        }
      }
    ]
    """
    def __init__(self, json_content=None):
        self.cleaned_data=None; self.data=None; self.error=True
        if json_content: self.json_content = IterDict.isNested(json_content)
        if getattr(self, 'json_content', None):
            self.check_data(); self.display_error_messages()
            if not self.error:
                self.parse()
                if self.cleaned_data: self._create_dataframe()
    def display_error_messages(self):
        if getattr(self, 'error_messages', None):
            for message in self.error_messages: print(message)
    def check_data(self):
        json_content = self.json_content
        def validate_api_responses(api_responses):
            validation_list = []
            for index, response in enumerate(api_responses):
                for url, content in response.items():
                    quotes = content.get('response', {}).get('d', {})
                    if quotes == [] or quotes is None: validation_list.append((url, False))
                    else: validation_list.append((url, True))
            return validation_list
        validate_fx_content = validate_api_responses(json_content)
        error_messages_list = []
        for url, check in validate_fx_content:
            if not check:
                currency_pair = idextract.extract(url, idextract.CURRENCY_PAIR)
                data = IterDict.find(json_content, target_key=url)
                check_quote_values = IterDict.search_keys_in(data, "d")
                message = "No data exists for the specified time periods."
        self.error_messages = error_messages_list
        valid_urls = [url for url, is_valid in validate_fx_content if is_valid]
        self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]
        if valid_urls: self.error = False
    def _create_dataframe(self):
        df = pd.DataFrame(self.cleaned_data)
        df['InverseRate'] = round((1/df['RatePairValue']),6)
        df['LastUpdate'] = df['LastUpdate'].apply(dtparse.parse, to_format='%Y-%m-%d')
        df['BaseCurrency'] = df['RatePair'].str.slice(0,3)
        df['QuoteCurrency'] = df['RatePair'].str.slice(3,6)
        df.rename(columns={'LastUpdate':'Timestamp','RatePair':'CurrencyPair','RatePairValue':'Rate'},inplace=True)
        column_order=['Timestamp','CurrencyPair','BaseCurrency','QuoteCurrency','Rate','InverseRate']
        filtered_columns = [col for col in column_order if col in df.columns]
        self.data = df[filtered_columns]
    def parse(self):
        cleaned_content = IterDict.find(self.json_content, first_only=False, target_key="response", wrap=False)
        flattened_data = []
        for response in cleaned_content:
            for item in response['d']:
                new_item = {key:value for key,value in item.items() if key != 'CallCount'}
                flattened_data.append(new_item)
        if flattened_data: self.cleaned_data = flattened_data
    def DATA(self):
        if not is_valid_dataframe(self.data):
            if getattr(self, 'error_messages', None): raise FXNoDataError(self.error_messages)
            raise FXDataUnavailableError()
        return self.data
    def __dir__(self): return ['DATA']



class fx_interbank_rates:
    """
    Expected Input: Interbank FX Rates API Response

    This class expects as input the parsed JSON response from the interbank foreign exchange (FX) rates service.
    The input should provide real-time and historical market data for various currency pairs, supported currencies, 
    high/low stats, and percentage changes over multiple time frames.

    Example structure:
    [
      {
        "<string-key>": {
          "response": {
            "formatted": [
              {
                "rate": float,            # Current exchange rate (e.g. 1.1582)
                "ratepair": str,          # E.g. "USDEUR"
                "m_change_pct": float,    # % change over the month
                "w_change_pct": float,    # % change over the week
                "d_change_pct": float,    # % change over the day
                "high": float,            # High for the day
                "low": float              # Low for the day
              }
              # ...more rate dicts...
            ],
            "currencyList": [
              {
                "id": int,
                "currency_code": str,     # "USD", "EUR", etc.
                "currency_name": str,     # "US Dollar"
                "is_supported": bool | None,
                "inverse": bool | None,   # Inverse conversion support
                "two_letter_code": str,
                "createdAt": str,         # ISO timestamp
                "updatedAt": str,
                "publishedAt": str,
                "country_name": str | None,
                "slug": str | None,
                "flag": (
                  {
                    "id": int,
                    "name": str,
                    "alternativeText": str | None,
                    "caption": str | None,
                    "width": int,
                    "height": int,
                    "formats": None,
                    "hash": str,
                    "ext": str,
                    "mime": str,
                    "size": float,
                    "url": str,
                    "previewUrl": None,
                    "provider": str,
                    "provider_metadata": None,
                    "createdAt": str,
                    "updatedAt": str
                  }
                  # or {"data": None}
                )
              }
              # ...more currencies...
            ],
            "HighLow": [
              {
                "ticker": str,            # E.g. "EUR/USD"
                "bid": float,
                "ask": float,
                "open": float,
                "low": float,
                "high": float,
                "changes": float,         # Total change for period
                "date": str               # "YYYY-MM-DD HH:mm:ss"
              }
              # ...more HighLow dicts...
            ],
            "DailyChange": {
              "success": bool,
              "terms": str,              # Terms of service URL
              "privacy": str,            # Privacy policy URL
              "change": bool,
              "start_date": str,         # "YYYY-MM-DD"
              "end_date": str,           # "YYYY-MM-DD"
              "source": str,             # e.g. "USD"
              "quotes": {
                "USDEUR": {
                  "start_rate": float,
                  "end_rate": float,
                  "change": float,       # Absolute change
                  "change_pct": float    # Percent change
                }
                # ...other pairs...
              }
            }
          }
        }
      }
    ]
    """	
    def __init__(self, json_content=None):
        self.cleaned_data=None; self.timestamp=dtparse.now(format="%Y-%m-%d %H:%M:%S"); self.data=None; self.error=False
        if json_content:
            self.json_content = IterDict.isNested(json_content)
            self.timestamp = self.extract_highlow_timestamp(self.json_content) or dtparse.now(format="%Y-%m-%d %H:%M:%S")
        else: self.timestamp = dtparse.now(format="%Y-%m-%d %H:%M:%S")
        if hasattr(self,"json_content") and self.json_content:
            if not self.error:
                self.parse()
                if self.cleaned_data: self._create_dataframe()
    def extract_highlow_timestamp(self, json_content):
        responses = IterDict.find(json_content, first_only=False, target_key="response", wrap=False)
        for response in responses:
            highlow = response.get("HighLow")
            if highlow and isinstance(highlow, list) and "date" in highlow[0]: return highlow[0]["date"]
        return None
    def smart_normalize(self, rows):
        _CHANGE_RE = re.compile(r'^(?P<period>[dDwWmM])_change_pct$')
        if not rows: return pd.DataFrame()
        sample = rows[0]; col_map = {}
        for key, val in sample.items():
            low = key.lower()
            if isinstance(val, str) and re.fullmatch(r'[A-Z]{6}', val): col_map[key] = 'CurrencyPair'
            elif isinstance(val, (int, float)) and 'rate' in low and 'change' not in low: col_map[key] = 'Rate'
        for key in sample:
            m = _CHANGE_RE.match(key)
            if m:
                period = m.group('period').lower()
                if period=='d': col_map[key]='DailyChange'
                elif period=='w': col_map[key]='WeeklyChange'
                elif period=='m': col_map[key]='MonthlyChange'
        df = pd.DataFrame(rows).rename(columns=col_map)
        return df
    def _create_dataframe(self):
        df = self.smart_normalize(self.cleaned_data)
        df['Timestamp'] = self.timestamp
        df['QuoteCurrency'] = df['CurrencyPair'].str[:3]
        key_cols = ['CurrencyPair', 'Rate', 'DailyChange', 'WeeklyChange', 'MonthlyChange']
        df = df.dropna(subset=key_cols, how='all')
        desired = ['Timestamp','CurrencyPair','QuoteCurrency','Rate','DailyChange','WeeklyChange','MonthlyChange']
        self.data = df[[c for c in desired if c in df.columns]]
    def parse(self):
        cleaned_content = IterDict.find(self.json_content, first_only=False, target_key="response", wrap=False)
        flattened_data = []
        for response in cleaned_content:
            for value in response.values():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            new_item = {k:v for k,v in item.items() if k!="ChartData"}
                            flattened_data.append(new_item)
        if flattened_data: self.cleaned_data = flattened_data
    def DATA(self):
        if not is_valid_dataframe(self.data): raise FXInterbankDataUnavailableError()
        return self.data
    def __dir__(self): return ['DATA']



class conversion:
    """
    Expected Input Structure for Conversion

    This class expects as input the parsed JSON response from the rates API.
    The response should provide exchange rate time series sampled at daily, weekly,
    monthly, and custom intervals. Each entry is a [timestamp, value] pair.

    Example structure:
    [
      {
        "<string-key>": {
          "response": {
            "DailyData": [
              # List of [timestamp, value] pairs for the day
              [timestamp_ms, float],  # e.g. [1754280000000, 196.14]
              # ...more entries...
            ],

            "WeeklyData": [
              # List of [timestamp, value] pairs for the week
              [timestamp_ms, float],  # e.g. [1753675200000, 198.514]
              # ...more entries...
            ],

            "MonthlyData": [
              # List of [timestamp, value] pairs for the month
              [timestamp_ms, float],  # e.g. [1751601600000, 197.236]
              # ...more entries...
            ],

            "Custom": [
              # List of [timestamp, value] pairs for a custom period
              [timestamp_ms, float],  # e.g. [1753329600000, 198.3]
              # ...more entries...
            ]
          }
        }
      }
    ]
    
    ## Notes:
    - `timestamp_ms` is the Unix timestamp in milliseconds (UTC).
    - Each list contains [timestamp_ms, value] pairs for the requested interval.    
    """
    __slots__ = ("_json","_amount","_timestamp","_rate_from","_rate_to","from_code","to_code","from_name","to_name","data")
    def __init__(self, json_content=None, conversion_amount=1.0):
        self.data=None; self._json=None; self._amount=conversion_amount or 1.0; self._timestamp=None; self._rate_from=None; self._rate_to=None
        self.from_code=None; self.to_code=None; self.from_name=None; self.to_name=None
        if json_content: self._json = conversion._response_status(json_content)
        if self._json:
            self.from_code, self.to_code = self._extract_currencies(self._json)
            if self.from_code and self.to_code:
                self.from_name = fxutil.query(self.from_code, ret_type="name")
                self.to_name = fxutil.query(self.to_code, ret_type="name")
            self._parse()
    @staticmethod
    def _response_status(json_content):
        expected = ["DailyData","WeeklyData","MonthlyData","Custom"]
        dataset = deepcopy(json_content)
        if isinstance(json_content, list):
            if not json_content: raise ConversionError("Response not a non-empty list")
            node = json_content[0]
        elif isinstance(json_content, dict): node = json_content
        else: raise ConversionError(f"Unsupported response type: {type(json_content)}")
        if (isinstance(node, dict) and len(node)==1 and not any(k in node for k in expected+["error","response"])):
            node = next(iter(node.values()))
        if isinstance(node, dict) and "error" in node: raise ConversionError(node["error"])
        data = node["response"] if isinstance(node, dict) and "response" in node else node
        if not isinstance(data, dict): raise ConversionError("Unexpected structure for data payload")
        if all(not data.get(k) for k in expected): raise ConversionNoDataError("All data arrays are empty or missing")
        custom = data.get("Custom")
        if not isinstance(custom, list): raise ConversionNoDataError("No 'Custom' list in response")
        for pair in custom:
            if (isinstance(pair, (list, tuple)) and len(pair)==2 and isinstance(pair[0], (int, float)) and isinstance(pair[1], (int, float))):
                return dataset
        raise ConversionNoDataError("No valid [timestamp, value] pairs in 'Custom'")
    def _extract_currencies(self, url_or_response):
        if isinstance(url_or_response, list):
            if not url_or_response: raise InvalidCurrencyPairError("No data found in response.")
            item = url_or_response[0]
            if not isinstance(item, dict) or len(item)!=1: raise InvalidCurrencyPairError("Malformed response structure.")
            url = next(iter(item))
        elif isinstance(url_or_response, str): url = url_or_response
        else: raise InvalidCurrencyPairError("Invalid input: expected a URL string or list.")
        rp = idextract.extract(url, idextract.CURRENCY_PAIR)
        if not rp: raise InvalidCurrencyPairError("Could not find a valid currency pair in URL.")
        if len(rp)!=6 or not rp.isalpha(): raise InvalidCurrencyPairError(f"Invalid rate pair '{rp}'. Expected a 6‑letter alphabetic pair like 'EURUSD'.")
        base, quote = rp[:3].upper(), rp[3:].upper()
        for code in (base, quote):
            try: result = fxutil.query(code)
            except Exception as e: raise InvalidCurrencyPairError(f"Error validating currency '{code}': {e}")
            if not result or result[0]!=code: raise CurrencyPairNotFoundError(f"Unknown or unsupported currency code: '{code}' in pair '{rp}'")
        return base, quote
    def _parse(self):
        cleaned = IterDict.find(self._json, first_only=False, target_key="response", wrap=False)
        if not cleaned or not isinstance(cleaned, list): raise ValueError("No 'response' list found in JSON")
        entry = cleaned[0]; raw = entry.get("Custom")
        if not isinstance(raw, list): raise ValueError("Expected 'Custom' key with a list value")
        valid = [(t,v) for t,v in raw if isinstance(t,(int,float)) and isinstance(v,(int,float))]
        if not valid: raise ValueError("No valid [timestamp, value] in 'Custom'")
        ts, rate = max(valid, key=lambda x:x[0]); self._timestamp = int(ts)
        self._rate_from = convert_to_float(rate, roundn=6)
        self._rate_to = round(1/self._rate_from, 6)
    @property
    def amount_to(self):
        if self._rate_from is None: raise ValueError("Rate not parsed yet")
        return round(self._amount * self._rate_from, 6)
    def to_dict(self):
        if self._rate_from is None or self.from_code is None: raise ValueError("Conversion data is unavailable")
        return {
            "from_currency":self.from_name,"from_currency_code":self.from_code,
            "to_currency":self.to_name,"to_currency_code":self.to_code,
            f"conversion_rate_{self.from_code}_to_{self.to_code}":self._rate_from,
            f"conversion_rate_{self.to_code}_to_{self.from_code}":self._rate_to,
            f"amount_converted_from_{self.from_code}":{"original_amount_"+self.from_code:self._amount,"converted_amount_to_"+self.to_code:self.amount_to},
            f"amount_converted_from_{self.to_code}":{"original_amount_"+self.to_code:self._amount,"converted_amount_to_"+self.from_code:round(self._amount*self._rate_to,6)},
            "last_updated":self._timestamp,
        }
    def DATA(self):
        self.data = self.to_dict()
        if not self.data: raise ConversionUnavailableError()
        return self.data
    def __dir__(self): return ["DATA"]
    
    
######################################################################
# DATA TYPE 2
######################################################################
class live_bid_ask:
    """
    Expected Input: Live Bid/Ask API Response

    This class expects as input the parsed JSON response from a live currency bid/ask API call.
    The structure includes summary statistics and metadata for a given forex symbol, as returned by the external service.

    Example structure:
    [
      {
        "<string-key>": {
          "response": {
            "data": {
              "symbol": str,           # e.g. "EURUSD"
              "summaryData": {
                "Bid": {
                  "label": str,        # "Bid"
                  "value": str         # e.g. "1.1572"
                },
                "Ask": {
                  "label": str,        # "Ask"
                  "value": str         # e.g. "1.1573"
                },
                "TodaysHigh": {
                  "label": str,        # "Today's High"
                  "value": str         # e.g. "1.1597"
                },
                "TodaysLow": {
                  "label": str,        # "Today's Low"
                  "value": str         # e.g. "1.1551"
                },
                "Open": {
                  "label": str,        # "Open"
                  "value": str         # e.g. "1.1586"
                },
                "NetChangePercent": {
                  "label": str,        # "Net Change %"
                  "value": str         # e.g. "-0.12%"
                },
                "pc": {
                  "label": str,        # "Net Change"
                  "value": str         # e.g. "-0.0014"
                },
                "Price": {
                  "label": str,        # "Last Value"
                  "value": str         # e.g. "1.1572"
                },
                "Time": {
                  "label": str,        # "Time of Last Value"
                  "value": str         # e.g. "08/04/2025 01:39:01"
                },
                "OneDayRange": {
                  "label": str,        # "1 Day Range"
                  "value": str         # e.g. "1.1551-1.1597"
                }
                # ...more fields possible...
              },
              "assetClass": str,        # e.g. "CURRENCIES"
              "additionalData": None,   # could also be more data
              "bidAsk": None            # could also be more data
            },
            "message": None,            # could also be a string message
            "status": {
              "rCode": int,             # HTTP-style code, e.g. 200
              "bCodeMessage": None,     # backend code message or None
              "developerMessage": None  # extra dev info or None
            }
          }
        }
      }
    ]
    """ 	
    def __init__(self, json_content=None):
        self.cleaned_data = None; self.data = None; self.json_content = None
        if json_content: self.json_content = live_bid_ask._response_status(json_content)
        if self.json_content:
            self.parse()
            if self.cleaned_data: self._create_dataframe()
    @staticmethod
    def _response_status(json_content):
        dataset = deepcopy(json_content)
        if isinstance(json_content, list):
            if not json_content: raise LiveBidAskError("Response is not a non-empty list")
            node = json_content[0]
        elif isinstance(json_content, dict): node = json_content
        else: raise LiveBidAskError(f"Unsupported response type: {type(json_content)}")
        if (isinstance(node, dict) and len(node)==1 and not any(k in node for k in ["response","error","data"])):
            node = next(iter(node.values()))
        if isinstance(node, dict) and "error" in node: raise LiveBidAskError(node["error"])
        data = node["response"] if isinstance(node, dict) and "response" in node else node
        if not isinstance(data, dict): raise LiveBidAskError("Unexpected structure for data payload")
        if "data" not in data: raise LiveBidAskNoDataError("No 'data' key found in response")
        data_dict = data["data"]
        summary = data_dict.get("summaryData")
        if not isinstance(summary, dict) or not summary: raise LiveBidAskNoDataError("No summary data available in response")
        return data_dict
    def _create_dataframe(self):
        df = pd.DataFrame(self.cleaned_data); self.data = df
    def parse(self):
        rows = []; content = deepcopy(self.json_content)
        entries = [content] if isinstance(content, dict) else content if isinstance(content, list) else []
        for entry in entries:
            row = {}; row['Symbol'] = entry.get('symbol'); row['Asset Class'] = entry.get('assetClass')
            summary_data = entry.get('summaryData', {})
            for val in summary_data.values():
                label = val.get('label'); value = val.get('value')
                if label is not None: row[label] = value
            rows.append(row)
        if rows: self.cleaned_data = rows
    def DATA(self):
        if not is_valid_dataframe(self.data): raise LiveBidAskUnavailableError()
        return self.data
    def __dir__(self): return ['DATA']

    
def __dir__():
    return __all__
