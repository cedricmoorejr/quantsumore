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
TreasuryAPI — Unified U.S. Treasury Rates Access and Analytics Interface
════════════════════════════════════════════════════════════════════════

Purpose
───────
    The `TreasuryAPI.py` module provides a single, robust, and extensible interface for querying,
    filtering, and analyzing official U.S. Treasury bill rates and yield curve data from the U.S.
    Department of the Treasury. The design standardizes data access, abstracts away CSV source quirks,
    and enables downstream analytics, risk modeling, or visualization in any finance workflow
    using the Quantsumore package.

Key Capabilities
────────────────
- **Direct Treasury Data Access:** Downloads and parses official Treasury bill and par yield curve rates
  (from https://home.treasury.gov/), automatically handling CSV sources and dynamic periods.
- **Flexible Period Filtering:** Users can request data for the current year, a specific year,
  or a given year and month, with strict parsing and validation.
- **DataFrame-First and Dictionary Summaries:** Most methods return filtered pandas DataFrames for
  full table analysis, or summary dictionaries for quick access to latest rates.
- **Unified Bill & Yield Interface:** Exposes parallel workflows for Treasury Bills and the
  full Par Yield Curve, including summary and full-table options.
- **No API Key Needed:** All endpoints work out of the box—no authentication, registration, or keys required.
- **Validation and Error Handling:** Every data request is validated for date/period support and format,
  with descriptive exceptions for malformed inputs or unavailable data.

Design Overview
───────────────
- **Single Entry Point:** All user interaction is through the `APIClient`, which is auto-instantiated as `engine`.
- **Flexible Routing:** The underlying `prep.py` adapter interface (`treasury_adapter`) manages all URL assembly and period normalization.
- **Source-Agnostic, Version-Stable:** Treasury.gov CSV sources are auto-routed and parsed to work with new or legacy formats, ensuring forward compatibility.
- **Explicit Summary vs. Full Table:** Methods provide both quick one-liner rates (e.g., "latest 3-Month T-Bill") and full DataFrame outputs for analysis.
- **Tested for Large-Scale Data:** Robust to periods with missing/partial data, suitable for research, backtesting, or production modeling.

Typical Workflow
────────────────
1. **Install and Import:**
       from quantsumore.api import treasury

2. **Initialize the Client:**
       engine = treasury.APIClient(treasury.treasury_adapter)

3. **Fetch Latest Treasury Bill Rates (as dict):**
       rates = engine.TBill(period='CY')  # Current year, latest daily rates as a dictionary

4. **Fetch Yield Curve (summary):**
       yields = engine.Yield(period=202308)   # August 2023 summary rates as a dictionary

5. **Fetch Full Table for Research:**
       full_df = engine.YieldAll(period=2022)   # Full DataFrame for all maturities in 2022

6. **Workflow Example (rate spread, modeling):**
       tbill = engine.TBill(period=202307)
       yieldcurve = engine.Yield(period=202307)
       # Now compute spread, chart, or use in risk model

Class Structure
───────────────
- **APIClient(adapter)**
    - Core interface for all Treasury queries (auto-initialized as `engine`)
    - Methods:
        - `.TBill(period=None, full_table=False)` — Fetches and summarizes Treasury bill rates.
        - `.Yield(period=None, full_table=False)` — Fetches and summarizes Treasury par yield curve.
        - `.YieldAll(period=None)` — Fetches the *full table* of all available yield maturities.

    - Internal Methods:
        - `._exists(df)` — Utility: checks if DataFrame is not None and not empty.
        - `._request_csv(url, period)` — Core fetch: downloads, parses, and filters CSV data by period.

Return Types and Data Structures
────────────────────────────────
- **Rates Summary:** Dictionary of latest available rates (e.g., `{'3-Month T-Bill': 0.0452, ...}`)
- **Full DataFrame:** Filtered pandas DataFrame with date-indexed columns for all maturities.

Supported Data Series and Periods
─────────────────────────────────
- **Treasury Bills (`TBill`)** — 1, 2, 3, 4, 6, and 12-month maturities.
- **Yield Curve (`Yield`, `YieldAll`)** — 1/2/3/4/6-month and 1/2/3/5/7/10/20/30-year.
- **Period Controls:** Any period from 1990 through current year:
    - None or 'CY': Current year.
    - 4-digit year: Full year.
    - 6-digit YYYYMM: That year and month (must exist in source).

Error Handling
──────────────
- `ValueError`: Raised on unsupported period formats or input errors.
- `TreasuryNoDataError`, `TreasuryDataUnavailableError`: Raised if the requested data is empty, missing, or cannot be fetched.
- All exceptions propagate with descriptive error messages for integration in ETL, analytics, or dashboards.

Design & Implementation Highlights
─────────────────────────────────
- **Automatic Period Normalization:** Flexible parsing of period (year, month, or both), with strict validation.
- **No Side Effects:** Methods are pure data fetchers/parsers—no state mutation or persistent objects.
- **Version-Agnostic:** Parsing logic adapts to changing or legacy Treasury.gov CSV field names.

Example Usage
─────────────
    >>> from quantsumore.api import treasury
    >>> engine = treasury.APIClient(treasury.treasury_adapter)
    >>> rates = engine.TBill(period='CY')
    >>> print(rates)
    {'1-Month T-Bill': 0.0542, '3-Month T-Bill': 0.0571, ...}

    >>> yields = engine.Yield(period=2022)
    >>> print(yields['10-Year Treasury Note'])
    0.0354

    >>> df = engine.YieldAll(period=2021)
    >>> print(df.head())

Reference Table: Method Inputs/Outputs
──────────────────────────────────────
| Method     | Input(s)      | Output                | Notes                               |
|------------|---------------|-----------------------|-------------------------------------|
| TBill      | period, full  | dict or DataFrame     | Treasury bill summary or full table |
| Yield      | period, full  | dict or DataFrame     | Yield curve summary or full table   |
| YieldAll   | period        | DataFrame             | All available maturities            |

Attribution
───────────
- All data sourced from the U.S. Department of the Treasury (https://home.treasury.gov/).
- No endorsement by or affiliation with the U.S. government. Data is for research and analysis only.
"""
from io import StringIO

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..prep import treasury_adapter
from .parse._securities import riskfreerate
from ...date_parser import dtparse


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

    def _exists(self, df):
        """
        Check if a DataFrame is not None and not empty.

        Returns True if the given DataFrame exists and contains at least one row.

        Parameters:
        ----------
        df : pandas.DataFrame or None
            The DataFrame to check.

        Returns:
        -------
        bool
            True if the DataFrame exists and is not empty, False otherwise.
        """
        import pandas as pd # Third-party library imports (from PyPI or other package sources)
        # return df is not None and hasattr(df, 'empty') and not df.empty
        return df is not None and getattr(df, "empty", True) is False       

    def _request_csv(self, url, period):
        """
        Downloads and filters a Treasury CSV file from the specified URL as a pandas DataFrame.

        This method performs an HTTP GET request to download the CSV data, parses it into a DataFrame,
        and filters the result by the requested period (year or month).

        Parameters:
        ----------
        url : str
            The full download URL for the Treasury CSV resource.
        period : None, str, or int
            The period for which data should be returned:
                - None or "CY" (case-insensitive): Use the current calendar year.
                - 4-digit year (e.g., 2022): Filter for that entire year.
                - 6-digit year and month (e.g., 202204): Filter for that year and month.

        Returns:
        -------
        pandas.DataFrame
            The filtered DataFrame indexed by row, with 'Date' as a pandas datetime column.
            Returns an empty DataFrame if there are no matches.

        Raises:
        ------
        ValueError
            If the period is not one of the supported formats.
        """
        today = dtparse.nowCT()
        if period is None or str(period).lower() == 'cy':
            year, month = today.year, None
        else:
            ps = str(period)
            if len(ps) == 6 and ps.isdigit():
                year, month = int(ps[:4]), int(ps[4:])
            elif len(ps) == 4 and ps.isdigit():
                year, month = int(ps), None
            else:
                raise ValueError("`period` must be None, 'CY', YYYY, or YYYYMM")

        # Fetch
        headers = {"User-Agent": "Mozilla/5.0"}
        
        import requests # Third-party library imports (from PyPI or other package sources)        
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Optional: will raise an error for 4xx/5xx responses
        
        import pandas as pd # Third-party library imports (from PyPI or other package sources)        
        response = pd.read_csv(StringIO(resp.text))

        # Filter
        if 'Date' in response.columns:
            response['Date'] = pd.to_datetime(response['Date'], errors='coerce')
            mask = response['Date'].dt.year == year
            if month is not None:
                mask &= response['Date'].dt.month == month
            response = response.loc[mask]
            response = response.reset_index(drop=True)
        return response        

    def TBill(
        self,
        period=None,
        full_table=False,
        # api_key=None   # <-- api key no longer required
    ):
        """
        Fetches and returns the most up-to-date daily Treasury bill rates.

        Downloads the latest Treasury bill rates from the U.S. Treasury (CSV API), filters
        the result to the requested period, and returns either summary rates or the full table.

        Parameters:
        ----------
        period : str, int, or None, optional
            The period for the data query:
                - 'CY' (str): Current year.
                - YYYY (int): Specific year (e.g., 2021).
                - YYYYMM (int): Specific month of a year (e.g., 202308).
                - None: Defaults to the current month of the current year.
        full_table : bool, default False
            If True, returns the full filtered DataFrame instead of summary rates.

        Returns:
        -------
        dict or pandas.DataFrame
            The latest daily Treasury bill rates as a dictionary (summary),
            or as a DataFrame if `full_table` is True.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='tbill', period=period)
        content = self._request_csv(url=url, period=period)
        if self._exists(content):
            obj = riskfreerate(content, kind="tbill", full=full_table)
            return obj.DATA()
           
    def Yield(
        self,
        period=None,
        full_table=False,
        # api_key=None   # <-- api key no longer required
    ):
        """
        Fetches and returns the most up-to-date Daily Treasury Par Yield Curve Rates.

        Downloads the latest yield curve rates for U.S. Treasury notes and bonds (maturities: 1, 2, 3, 5, 7, 10, 20, 30 years)
        from the U.S. Treasury CSV endpoint, filters to the requested period, and returns either a summary dictionary
        or the full filtered table.

        Parameters:
        ----------
        period : str, int, or None, optional
            The time period for the data query:
                - 'CY' (str): Current year.
                - YYYY (int): Specific year (e.g., 2021).
                - YYYYMM (int): Specific month of a year (e.g., 202308).
                - None: Defaults to the current month of the current year.
        full_table : bool, default False
            If True, returns the full filtered DataFrame instead of summary rates.

        Returns:
        -------
        dict or pandas.DataFrame
            The latest Daily Treasury Par Yield Curve Rates as a dictionary (summary),
            or as a DataFrame if `full_table` is True.
        """
        make_method = getattr(self.adapter, 'make')
        url = make_method(query='tyield', period=period)
        content = self._request_csv(url=url, period=period)       
        if self._exists(content):
            obj = riskfreerate(content, kind="tyield", full=full_table)
            return obj.DATA()
           
    def YieldAll(
        self,
        period=None,
        # api_key=None   # <-- api key no longer required
    ):
        """
        Fetches and returns the most up-to-date Treasury Yield Curve Rates for all available maturities.

        Retrieves the latest yield curve rates from the U.S. Treasury for a comprehensive set of maturities,
        including short-term bills and long-term notes and bonds.

        Parameters:
        ----------
        period : str, int, or None, optional
            The time period for the data query:
                - 'CY' (str): Current year.
                - YYYY (int): Specific year (e.g., 2021).
                - YYYYMM (int): Specific month and year (e.g., 202308).
                - None: Defaults to the current month of the current year.

        Returns:
        -------
        pandas.DataFrame
            The latest Treasury yield curve rates for all available maturities as a DataFrame.
        """
        return self.Yield(period=period, full_table=True)

    def __dir__(self):
        return [
            'TBill',
            'Yield',
            'YieldAll',
        ]       


engine = APIClient(treasury_adapter)

def __dir__():
    return __all__

