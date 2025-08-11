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
APIClient: Unified Fetcher for Equity Financial Statements and Dividend Data
────────────────────────────────────────────────────────────────────────────

Module Purpose
────────────────────────────────────────────────────
`APIClient` provides a **high-level, silent interface** for retrieving, categorizing,
and preprocessing financial statement and dividend data for equities. This module acts
as a central point for assembling API queries, dispatching outbound requests, and constructing
ready-to-analyze DataFrames for income statements, balance sheets, cash flows, and dividend history.

**Note:** APIClient does not print, warn, or log on missing or invalid data. All feedback or error
reporting is handled by downstream consumers (such as `fAnalyze`). The client returns only structured
data objects or None/empty on failure, leaving messaging responsibilities to analysis layers.

Key Use Cases
────────────────────────────────────────────────────
- Loading all available statement and dividend data for a single stock ticker
- Handling both annual and quarterly reporting periods
- Integrating with asset-agnostic adapters (i.e., for stocks, funds, etc.)
- Serving as the backend for fundamental analysis workflows

System Architecture
────────────────────────────────────────────────────
1. **Asset Adapter Integration**  
   The client takes an `asset` object (such as `equity_adapter`) with a standardized
   `.make()` method for URL construction. This abstracts away provider details and
   keeps endpoint logic modular and updatable.

2. **URL Generation and Request Dispatch**  
   For any ticker and period, the client assembles all relevant URLs for
   financials and dividends. Requests are routed through the `Connection.Request`
   proxy, which manages authentication, rate limits, and vendor-neutrality.

3. **Categorization of Responses**  
   Returned payloads are grouped into "financial_statements" and "dividend"
   buckets, using URL pattern matching. This ensures correct parsing even as
   provider endpoints evolve.

4. **Parsing and Structuring**  
   The categorized raw JSON is passed to dedicated parser classes:
   - `statements`: converts statement JSON into Pandas DataFrames
     for Income, Balance, and Cash Flow Statements
   - `dividend`: structures dividend history and summary reports

5. **Unified Results Dictionary**  
   Results are always returned as a dictionary with clear keys:
   - `'financial_statements'`: tuple of (Income, Balance, Cash Flow) DataFrames
   - `'dividend'`: tuple of (dividend summary, dividend history) DataFrames

Design Features
────────────────────────────────────────────────────
- **Backend-agnostic, silent operation**: All errors and missing data are indicated via return values only;
  no user-facing prints, warnings, or logs are emitted from this module.
- **Extensible**: Add new asset types, queries, or providers by plugging in new asset adapters or adjusting URL assembly logic.
- **Type Consistency**: All parsed objects are guaranteed to be DataFrames or None,
  enabling smooth downstream analysis and error handling.
- **Request Flexibility**: Handles both list and singleton endpoint generation;
  manages batch requests and merging of results.

Data Guarantees
────────────────────────────────────────────────────
- All successfully loaded data is returned as DataFrame objects; missing data
  results in None or empty DataFrames.
- Every fetch operation returns both statement and dividend data if available,
  or an explicit indication of unavailability.
- Ticker validity and provider response codes are checked before parsing.

Available Output Structure
────────────────────────────────────────────────────
• result["financial_statements"][0] → (income_statement, balance_sheet, cash_flow_statement) DataFrames
• result["dividend"][0] → (dividend_summary, dividend_data) DataFrames

Implementation Notes
────────────────────────────────────────────────────
• All request routing, authentication, and proxy logic is encapsulated in Connection.Request
• Asset adapters (like equity_adapter) are responsible for URL construction only — not for transport
• Statement and dividend parsers enforce strict shape validation for DataFrames
• No provider names, endpoints, or internal keys are exposed in public APIs or docstrings
"""
import re

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..api.equity.parse._financials import statements
from ..api.equity.parse._shareholders import dividend
from ..api.prep import equity_adapter
from ..._http.connection import Connection
from ..strata_utils import IterDict
from ..exceptions import (
    DividendHistoryNoDataError,
    DividendHistoryUnavailableError,
    FinancialStatementUnavailableError,
    FinancialDataNotLoadedError,
    APIQuotaError,    
    APIKeyRequiredError,
    APIRequestError,    
)
from ..__relaytable__ import __API_BASE__

__all__ = [
    # 'process',
    'get_process'
    ]    


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.
def _normalize_base_url(u):
    if isinstance(u, (list, tuple)) and u:
        u = u[0]
    if isinstance(u, (bytes, bytearray)):
        u = u.decode()
    return str(u).rstrip('/')
   
def fetch_financials_dividends_pair(pairs, api_key=None, base_url=None, timeout=20):
    """
    Special case: hit /relay/pair with two (base, endpoint) tuples, but
    borrow API key handling & error semantics from Connection (_httpClient).
    """
    import requests    
    if len(pairs) != 2:
        raise ValueError("Provide exactly two (base, endpoint) tuples")
    if api_key is None:
        api_key = getattr(Connection, "api_key", None)
        if not api_key:
            raise APIKeyRequiredError(
                "API key is required. Use APIKey() first or pass api_key."
            )
    if base_url is None:
        try:
            base_url = getattr(Connection, "base_url", None) or __API_BASE__
        except AttributeError:
            base_url = __API_BASE__

    payload = {"items": [{"base": b, "endpoint": e} for (b, e) in pairs]}
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "User-Agent": "APIClient/1.0"
    }
    url = f"{base_url.rstrip('/')}/relay/pair"
    try:
        session = getattr(Connection, "_get_session")()
        r = session.post(url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        raise APIRequestError(e)
    except requests.RequestException as e:
        raise APIRequestError(requests.exceptions.HTTPError(str(e)))  
       
class APIClient:
    """
    Unified Fetcher for Equity Financial Statements and Dividend Data

    Overview
    --------
    APIClient is a high-level, backend-agnostic interface for retrieving, categorizing,
    and preprocessing both financial statement and dividend data for equities. It
    abstracts away the complexities of endpoint management, request dispatch,
    response parsing, and data validation, serving as the central fetch layer for
    downstream analysis engines.

    Core Responsibilities
    ---------------------
    - Assemble and dispatch API requests for both financial statements and dividend history
      using an asset adapter.
    - Route all requests through a centralized connection proxy (handles authentication,
      rate limiting, and provider neutrality).
    - Categorize and parse responses, converting raw JSON payloads into structured
      Pandas DataFrames for income statements, balance sheets, cash flows, and dividends.
    - Return all data (or explicit None/empty objects) via a standardized result dictionary.

    Design Philosophy
    -----------------
    - **Silent Operation:** APIClient performs no user-facing messaging—no prints,
      warnings, or logs. All error and warning communication is delegated to downstream
      consumers such as analysis or reporting layers.
    - **Backend-Agnostic:** The client is provider-neutral, relying on asset adapters
      and connection proxies to interface with various data sources.
    - **Extensible:** Easily accommodates new asset types, providers, or data endpoints
      with minimal internal modification.

    Output Contract
    ---------------
    The `Process()` method always returns a dictionary with:
        • 'financial_statements': [(income_statement, balance_sheet, cash_flow_statement)]
        • 'dividend': [(dividend_summary, dividend_data)]
    Any missing or invalid data is represented as None or empty DataFrames.
    All messaging regarding missing data is handled externally.
    """	
    def __init__(self, adapter):
        """
        Initialize the APIClient with a specified asset adapter.

        Parameters:
        ----------
        adapter : object
            Asset adapter responsible for constructing API endpoint URLs via its `make()` method.
            Typically, this is an object such as `equity_adapter` that abstracts provider logic.

        Notes
        -----
        The asset adapter must support the interface expected by APIClient, particularly
        a `make()` method for endpoint assembly.
        """    	
        self.adapter = adapter

    def _make_request(self, url, api_key=None):
        """
        Dispatch outbound API requests for the specified URL(s).

        Parameters:
        ----------
        url : str or list of str
            One or more API endpoint URLs to be fetched.
        api_key : str, optional
            API key or authentication token, if required by the connection proxy.

        Returns
        -------
        content : list of dict
            Raw response payload(s) as returned by the `Connection.Request` proxy.
        """    	
        base = url[0].decode() if isinstance(url[0], bytes) else url[0]
        endpoint = url[1]
        content = Connection.Request(
            url=(base, endpoint),
            api_key=api_key,
            params=None,
            return_url=True
        )      
        return content
    
    def _make_pair(self, pairs, api_key=None):
        return fetch_financials_dividends_pair(pairs, api_key)
       
    def _urls(self, ticker, period):
        """
        Construct all required endpoint URLs for both financials and dividends.

        Parameters:
        ----------
        ticker : str
            The stock ticker symbol to query.
        period : str
            Reporting period (e.g., "Q", "Quarterly", "A", "Annual").

        Returns
        -------
        urls : list of str
            List of endpoint URLs needed to fetch all relevant data.

        Raises
        ------
        ValueError
            If an unsupported reporting period is provided.
        """    	
        valid_periods = {'Quarterly': ['Q', 'Quarter', 'Qtr'], 'Annually': ['A', 'Annual']} 
        period = IterDict.key_from_mapping(period, valid_periods, invert=False)
        if not period: raise ValueError("Invalid period.")
        urls = []; make = getattr(self.adapter, 'make')
        f = make(query='financials', ticker=ticker, period=period)
        f_base = f[0].decode() if isinstance(f[0], bytes) else f[0]
        f_ep = f[1]
        d = make(query='dividend_history', ticker=ticker)
        d_base = d[0].decode() if isinstance(d[0], bytes) else d[0]
        d_ep = d[1]
        urls.append((f_base, f_ep)); urls.append((d_base, d_ep))
        return urls

    def _categorize_content(self, content):     
        """
        Group fetched response content into financial statement and dividend categories.

        Parameters:
        ----------
        content : list of dict
            Raw response payload(s) returned from API requests.

        Returns
        -------
        categorized_content : dict
            Dictionary with two keys:
                - 'financial_statements': list of statement payloads
                - 'dividend': list of dividend payloads

        Notes
        -----
        Categorization is based on URL patterns; endpoints containing 'dividend' are
        grouped separately from those containing 'financials'.
        """    	
        categorized = {'dividend': [], 'financial_statements': []}
        url_pattern = re.compile(
            r"""
            ^[\w+/=.-]+/[\w.-]+(?:\?[\w=&%.-]*)?$
            """,
            re.VERBOSE
        )  
                    
        # Flatten: accept list[dict] or list[list[dict]]
        flat = []
        for entry in content:
            if isinstance(entry, dict):
                flat.append(entry)
            elif isinstance(entry, list):
                flat.extend(d for d in entry if isinstance(d, dict))

        for entry in flat:
            for url, data in entry.items():
                if url_pattern.fullmatch(url):           
                    u = url.lower()
                    if "dividend" in u:                   
                        categorized['dividend'].append({url: data})
                    elif "financials" in u:
                        categorized['financial_statements'].append({url: data})
        return categorized     

    def Process(self, ticker, period="Q", api_key=None):
        """
        Fetch and parse all available financial statement and dividend data for a specified ticker and period.

        Parameters:
        ----------
        ticker : str
            Stock ticker symbol to fetch data for.
        period : str, optional
            Reporting period (e.g., "Q", "Quarterly", "A", "Annual"). Default is "Q".
        api_key : str, optional
            API key or authentication token for request dispatch.

        Returns
        -------
        results : dict
            Dictionary with two keys:
                - 'financial_statements': list containing (income, balance, cash flow) DataFrames
                - 'dividend': list containing (dividend summary, dividend history) DataFrames

        Notes
        -----
        All results are returned as DataFrames or None. No exceptions are raised for missing data;
        downstream consumers are responsible for error handling and messaging.
        """    	
        urls = self._urls(ticker=ticker, period=period)
        try:
            Connection._anyquota(needed=1, api_key=api_key, force=True)
        except QuotaError as e:
            return {
                "error": "INSUFFICIENT_QUOTA",
                "detail": str(e),
                "needed": 2,
                "available": e.available,
            }        
        
        try:
            responses = fetch_financials_dividends_pair(urls, api_key=api_key)
        except APIRequestError as e:
            return {"error": "REQUEST_FAILED", "detail": str(e)}        
        categorized = self._categorize_content(responses)
        
        results = {'financial_statements': [], 'dividend': []}
        fin_content = categorized.get('financial_statements', [])
        if fin_content:
            try:
                fs_obj = statements(json_content=fin_content)
                results['financial_statements'] = [(fs_obj.IncomeStatement, fs_obj.BalanceSheet, fs_obj.CashFlowStatement)]
            except (FinancialDataNotLoadedError, FinancialStatementUnavailableError): pass
        div_content = categorized.get('dividend', [])
        if div_content:
            try:
                dv_obj = dividend(json_content=div_content)
                results['dividend'] = [(dv_obj.DividendReport, dv_obj.DividendData)]
            except (DividendHistoryNoDataError, DividendHistoryUnavailableError): pass
        return results


# process = APIClient(equity_adapter)
def get_process():
    from quantsumore.api.prep import equity_adapter
    return APIClient(equity_adapter)

def __dir__():
    return __all__
