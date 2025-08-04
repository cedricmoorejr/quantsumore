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
ConsumerPriceIndexAPI — Unified CPI and Inflation Adjustment Interface
══════════════════════════════════════════════════════════════════════

Purpose
───────
    The `ConsumerPriceIndexAPI.py` module delivers a streamlined, provider-agnostic interface
    for retrieving, analyzing, and adjusting for inflation using official Consumer Price Index (CPI)
    time series data within the Quantsumore library. It abstracts away external data quirks and
    provides reliable inflation calculation utilities, allowing users to query raw CPI values or
    perform dollar-value adjustments across years and months with minimal effort.

Key Capabilities
────────────────
- **Fetches Official CPI Data:** Retrieves and parses Consumer Price Index data for “All Urban Consumers”
  (series ID: `CPIAUCNS` or variants), directly from the FRED (Federal Reserve Economic Data) system.
- **Canonical DataFrame Output:** All CPI data is returned as pandas DataFrames with normalized columns
  (`series_id`, `year`, `period`, `value`), including monthly and annual averages.
- **No API Key Needed:** All CPI and inflation utilities work out of the box without authentication.
- **Inflation Adjustment Utilities:** Provides drop-in methods for converting historical dollar amounts to
  current dollars (or any target year), as well as year-by-year and month-by-month inflation adjustment.
- **Strict Validation:** Every query is validated for valid series IDs, date ranges, and amount types, with
  explicit error reporting for out-of-bounds or malformed inputs.
- **Extensible:** While focused on the flagship CPI series for all urban consumers, the design supports
  any compatible FRED time series for economic indicators.

Design Overview
───────────────
- **Single Entry Point:** End users interact only with the top-level `APIClient`, which auto-initializes
  all helper classes (notably `CPI_U`) and orchestrates all CPI data requests and inflation adjustment.
- **Data Routing and Normalization:** All URL building, FRED-series normalization, and HTML/CSV parsing
  are abstracted in the `prep.py` adapter registry and the `cpi` parser.
- **Automatic Inflation Adjustment:** The `CPI_U` property on every client exposes an `InflationAdjustment`
  property, which wraps a dedicated inflation adjustment class initialized with up-to-date CPI data.
- **DataFrame-first:** All CPI data is fetched, parsed, and returned as pandas DataFrames, ensuring
  consistency and downstream compatibility for analysis and modeling.
- **Real-time/Recent Data:** By default, all methods use the latest available CPI data, automatically
  adjusting for any reporting lag.

Typical Workflow
────────────────
1. **Install and Import:**
       from quantsumore.api import cpi
2. **Initialize the Client:**
       engine = cpi.APIClient(cpi.cpi_adapter)
3. **Fetch All-Urban CPI Data:**
       df = engine._all_urban(series_id='CPIAUCNS')    # Returns a DataFrame with year/month CPI values
4. **Access Inflation Adjustment Helper:**
       inflation = engine.CPI_U.InflationAdjustment
5. **Inflation-adjust a Dollar Amount:**
       adjusted = inflation.select(original_amount=100, original_year=1980, target_year=2024, month_input='March')
       print(adjusted)   # e.g., "$100 from 1980 is equivalent to $362.47 in 2024 dollars."
6. **Year-by-Year Inflation History:**
       results = inflation.year_by_year(original_amount=50, n_years=10)  # Returns {2014: value, ..., 2023: value}
7. **Month-by-Month for Current Year:**
       monthly = inflation.month_by_month(amount=100)

Class Structure
───────────────
- **APIClient(adapter)**
    - Core client for CPI queries. Automatically creates:
        - `CPI_U` (exposes inflation adjustment methods for “All Urban Consumers”)
    - Methods:
        - `._all_urban(series_id='CPIAUCNS')` — Fetch CPI DataFrame for specified FRED series.
- **APIClient._CPI_U**
    - Internal helper class (attached as `CPI_U`) for all-urban CPI workflows.
    - Properties:
        - `.InflationAdjustment` — Returns a `_InflationAdjustment` instance, initialized with latest CPI data.
- **_InflationAdjustment(data)**
    - Used internally by API to perform robust inflation adjustment using provided CPI DataFrame.
    - Key Methods:
        - `.select(original_amount, original_year, target_year, month_input)` — Adjusts amount to target year.
        - `.year_by_year(original_amount, n_years)` — Adjusts amount for each of last n years.
        - `.month_by_month(amount)` — Adjusts amount for each month of current year.

Return Types and Data Structures
────────────────────────────────
- **CPI DataFrame:** Columns: `series_id`, `year`, `period` (month or 'Average'), `value` (index).
- **Inflation-adjusted Value:** Float (rounded to 2 decimals).
- **Year/Month Mapping:** Dict mapping year or month to adjusted float values.

Supported Data Series
────────────────────
- Default: `"CPIAUCNS"` (Consumer Price Index for All Urban Consumers: All Items in U.S. City Average)
- Other FRED series supported by passing a different `series_id`.

Error Handling
──────────────
- `ValueError`: Raised on invalid amount/year/month/n_years, or if data is missing.
- `CPIDataUnavailableError`, `CPIDateParseError`: Raised on fetch/parse failures or malformed source data.

Design & Implementation Highlights
─────────────────────────────────
- **Automatic Normalization:** All months are normalized (e.g., `'03'`, `'Mar'`, `'March'` → `'March'`)
- **Fallbacks:** If month-specific CPI data is missing, calculations fall back to yearly average with clear warning.
- **No External Provider Lock-In:** All upstream requests route through `prep.py`, with FRED as default data source.

Example Usage
─────────────
    >>> from quantsumore.api import cpi
    >>> engine = cpi.APIClient(cpi.cpi_adapter)
    >>> df = engine._all_urban()
    >>> print(df.head())

    >>> inflation = engine.CPI_U.InflationAdjustment
    >>> inflation.select(100, 1975, 2024, 'Average')  # $100 in 1975 → $572.31 in 2024

    >>> inflation.year_by_year(50, 5)    # Show value of $50 for each of last 5 years
    {2019: 52.14, 2020: 52.99, ...}

    >>> inflation.month_by_month(25)     # How does $25 change, Jan–Dec, this year?
    {'January': 24.96, 'February': 25.01, ...}

Reference Table: Method Inputs/Outputs
──────────────────────────────────────
| Method            | Input(s)                                                       | Output               | Notes                                 |
|-------------------|----------------------------------------------------------------|----------------------|---------------------------------------|
| _all_urban        | series_id                                                      | DataFrame            | CPI for all-urban                     |
| select            | original_amount, original_year, target_year, month_input			 | float                | Adjusts amount to target year         |
| year_by_year      | original_amount, n_years                                       | dict                 | Last n years                          |
| month_by_month    | amount                                                         | dict                 | All months, current                   |

Attribution
───────────
- All data is retrieved from the Federal Reserve Economic Data (FRED) system, “Consumer Price Index for All Urban Consumers: All Items in U.S. City Average” (CPIAUCNS) or as specified.
- No API key or authentication required. No affiliation with, or endorsement by, the U.S. Federal Reserve.
"""
# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..prep import cpi_adapter
from .parse import cpi


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
        self.CPI_U = self._CPI_U(self) # Auto create CPI_U instance that knows about its parent APIClient instance
       
    def _all_urban(
        self,
        series_id='CPIAUCNS',
        # api_key=None   # <-- api key no longer required
    ):  
        """
        Fetches and returns Consumer Price Index (CPI) data for all urban consumers.

        This method retrieves CPI data for all urban consumers based on the specified `series_id`.
        The default `series_id` of 'CPIAUCNS' corresponds to the all-items Consumer Price Index for
        all urban consumers in the United States. The data is fetched, processed, and returned as a 
        DataFrame containing CPI metrics by year and month.

        Parameters:
        ----------
        series_id : str, optional
            The series ID for the CPI data to query. Defaults to 'CPIAUCNS' (all-items CPI for all urban consumers in the U.S.).

        Returns:
        -------
        pandas.DataFrame or None
            A DataFrame containing the processed CPI data for the requested series. Columns typically include:
            - 'year': The year of the CPI data.
            - 'period': The period or month (e.g., 'January', 'Average').
            - 'value': The CPI value for the specified period.
            If data retrieval fails, returns None.
        """    	
        make_method = getattr(self.adapter, 'make')
        url = make_method(series_id=series_id)

        # Fetch
        headers = {"User-Agent": "Mozilla/5.0"}
        import requests # Third-party library imports (from PyPI or other package sources)        
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Optional: will raise an error for 4xx/5xx responses
        content = resp.text
        if not content:
            return None  # Or raise a warning/log it
        else:        
            obj1 = cpi.CUUR0000AA0.Date(content)
            end_date = obj1.date()
            obj2 = cpi.CUUR0000AA0.Data(end_date=end_date)
            data = obj2.all_items_index()
            return data          

    # Notes:
    # -----
    # This class is intended for internal use within APIClient and is accessed via
    # the CPI_U property. It provides a streamlined interface for CPI data access
    # and inflation adjustment calculations.
    class _CPI_U:
        """
        Private helper class for managing Consumer Price Index (CPI) adjustments for all urban consumers.

        This class acts as an interface for accessing and adjusting for inflation using CPI data.
        It leverages the parent APIClient's data retrieval methods to ensure all adjustments use up-to-date CPI data.
        Access is provided via the InflationAdjustment property, which initializes an inflation adjustment
        helper using freshly fetched CPI data.

        Attributes:
        ----------
        engine : APIClient
            Reference to the parent APIClient instance for data access and method calls.

        Properties:
        ----------
        InflationAdjustment : _InflationAdjustment
            Property that initializes and returns an _InflationAdjustment instance
            using CPI data fetched via the parent's _all_urban method. Ensures all
            inflation adjustments are based on the most current data.
        """
        def __init__(self, engine):
            self.engine = engine

        @property
        def InflationAdjustment(self):
            data = self.engine._all_urban() # Property ensures that we can access InflationAdjustment
            return _InflationAdjustment(data)
           
    def __dir__(self):
        return ['CPI_U'] 


# Notes:
# -----
# This class is not intended for direct use by end users, but rather as a behind-the-scenes utility
# for inflation adjustment in financial data pipelines, web APIs, or analytic tools.
class _InflationAdjustment:
    """
    Helper class for inflation adjustment calculations using Consumer Price Index (CPI) data.

    This class is designed to facilitate the calculation of inflation-adjusted monetary values
    based on historical and current CPI data. It is used internally by the API to provide accurate
    conversions of dollar amounts between different years and months, making it easy to analyze the
    changing value of money over time.

    Core Features:
    -------------
    - Normalizes diverse month representations (e.g., '03', 'Mar', 'March') to a standard format.
    - Validates and processes monetary amounts, years, months, and period ranges for calculation.
    - Calculates the equivalent value of an amount from one year in the currency of another year,
      supporting both yearly averages and specific months.
    - Provides utilities for year-by-year and month-by-month inflation adjustment, using the most
      recent CPI data available.
    - Raises clear, descriptive errors if inputs are invalid or if the required CPI data is missing.

    Parameters:
    ----------
    data : pandas.DataFrame
        CPI data as a DataFrame, with columns for 'year', 'period' (month), and 'value' (CPI index).

    Raises:
    ------
    ValueError
        If the provided data is None or does not support the required operations.
    """	
    def __init__(self, data):
        if data is None:
            raise ValueError("Failed to fetch or process CPI data.")
        self.data = data
        self.max_year = self.data['year'].max()
        self.min_year = self.data['year'].min()
        self.month_map = {
            '1': 'January', '01': 'January', 'January': 'January', 'Jan': 'January',
            '2': 'February', '02': 'February', 'February': 'February', 'Feb': 'February',
            '3': 'March', '03': 'March', 'March': 'March', 'Mar': 'March',
            '4': 'April', '04': 'April', 'April': 'April', 'Apr': 'April',
            '5': 'May', '05': 'May', 'May': 'May',
            '6': 'June', '06': 'June', 'June': 'June',
            '7': 'July', '07': 'July', 'July': 'July',
            '8': 'August', '08': 'August', 'August': 'August', 'Aug': 'August',
            '9': 'September', '09': 'September', 'September': 'September', 'Sep': 'September',
            '10': 'October', 'October': 'October', 'Oct': 'October',
            '11': 'November', 'November': 'November', 'Nov': 'November',
            '12': 'December', 'December': 'December', 'Dec': 'December'
        }
        self.current_month = self.data[(self.data['year'] == self.max_year) & (self.data['period'] != 'Average')].sort_values(by='period', key=lambda x: x.apply(self._normalize_month))['period'].iloc[-1]

    def _normalize_month(self, month_input):
        """
        Normalizes a month input to a standard month name used in the CPI data.

        This method takes various representations of a month (numeric strings, abbreviations, or full names)
        and converts them to a canonical month name that matches the format used in the CPI DataFrame.

        Parameters:
        ----------
        month_input : str or int
            The month input to normalize. Can be a numeric string (e.g., '03', '3'), 
            a full month name (e.g., 'March'), or a common abbreviation (e.g., 'Mar').

        Returns:
        -------
        str or None
            The standardized month name (e.g., 'March'), or None if the input could not be matched.
        """
        month_input = str(month_input).capitalize()
        return self.month_map.get(month_input, None)

    def _validate(self, amount=None, year=None, month=None, n_years=None):
        """
        Validates and converts input parameters for inflation adjustment calculations.

        This method checks and converts the provided parameters to the correct types, and ensures that
        all values are within valid ranges for CPI calculations. Raises descriptive ValueErrors if any
        validation fails.

        Parameters:
        ----------
        amount : float or None, optional
            The monetary amount to validate and convert to float, if provided.
        year : int or None, optional
            The year to validate and convert to int, if provided. Must be within the range of available CPI years.
        month : str or None, optional
            The month to validate and normalize, if provided. Accepted values include numeric strings, abbreviations, or full names.
        n_years : int or None, optional
            The number of years for a year-by-year calculation. Must be a non-negative integer if provided.

        Returns:
        -------
        tuple
            A tuple containing the validated and converted (amount, year, month, n_years) values.

        Raises:
        ------
        ValueError
            If any of the input parameters are of an incorrect type or outside of valid ranges.
        """
        if amount is not None:
            try:
                amount = float(amount)
            except ValueError:
                raise ValueError("Amount must be a number.")
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                raise ValueError("Year must be a numeric value.")
            if year > self.max_year or year < self.min_year:
                raise ValueError(f"Year must be between {self.min_year} and {self.max_year}.")
        if month is not None:
            month = self._normalize_month(month)
            if month is None:
                raise ValueError("Please enter a valid month.")
        if n_years is not None:
            try:
                n_years = int(n_years)
            except ValueError:
                raise ValueError("n_years must be a numeric value.")
            if n_years < 0:
                raise ValueError("n_years must be a non-negative integer.")
        return (amount, year, month, n_years)

    def _get_cpi(self, year, period='Average'):
        """
        Retrieves the Consumer Price Index (CPI) value for a given year and period.

        This method looks up the CPI value in the data for the specified year and period
        (month or 'Average'). If a matching entry is found, the corresponding CPI value is returned;
        otherwise, returns None.

        Parameters:
        ----------
        year : int
            The year for which to retrieve the CPI value.
        period : str, optional
            The period (typically a month name or 'Average') for which to retrieve the CPI.
            Defaults to 'Average'.

        Returns:
        -------
        float or None
            The CPI value for the specified year and period, or None if not available.
        """
        cpi_value = self.data[(self.data['year'] == year) & (self.data['period'] == period)]['value']
        return cpi_value.iloc[0] if not cpi_value.empty else None

    def select(self, original_amount, original_year, target_year, month_input):
        """
        Calculates and returns the inflation-adjusted value for a given amount and time period.

        This method computes the equivalent value of a specified amount of money from one year
        in the dollars of another year, optionally using a specific month. If data for the exact
        month is unavailable, the calculation defaults to yearly averages.

        Parameters:
        ----------
        original_amount : float
            The amount of money to adjust for inflation.
        original_year : int
            The year from which the original amount originates.
        target_year : int
            The year to which the amount should be adjusted.
        month_input : str
            The month for the calculation (e.g., "January", "03", "Mar"), or 'Average' to use the yearly average.

        Returns:
        -------
        float
            The adjusted value in the target year's dollars, rounded to two decimal places.
        """
        # Validate and convert inputs
        original_amount, original_year, month, _  = self._validate(amount=original_amount, year=original_year, month=month_input)
        _, target_year, _, _ = self._validate(year=target_year)

        cpi_original = self._get_cpi(original_year, month)
        cpi_target = self._get_cpi(target_year, month)

        # If either CPI data point is missing, default both to yearly averages and alert the user
        if cpi_original is None or cpi_target is None:
            print(f"Since we do not have the month value for {month} {target_year if cpi_target is None else original_year}, we will be switching to averages of the years.")
            cpi_original = self._get_cpi(original_year)
            cpi_target = self._get_cpi(target_year)

        if cpi_original is None or cpi_target is None:
            raise ValueError("CPI data not available for the provided dates.")

        adjusted_value = (original_amount / cpi_original) * cpi_target
        print(f"${original_amount:.2f} from {original_year} is equivalent to ${adjusted_value:.2f} in {target_year} dollars.")
        return round(adjusted_value, 2)

    def year_by_year(self, original_amount, n_years):
        """
        Calculates the inflation-adjusted value of an amount for each year over a specified period.

        This method computes the equivalent value of a given amount in each of the past `n_years`,
        relative to the most recent CPI data. Adjustments use monthly data when available,
        or fallback to yearly averages.

        Parameters:
        ----------
        original_amount : float
            The original amount of money to evaluate.
        n_years : int
            The number of years back from the most current year to include in the calculation.

        Returns:
        -------
        dict
            A dictionary where each key is a year and the value is the inflation-adjusted amount
            for that year, rounded to two decimal places.
        """
        # Validate and convert inputs
        original_amount, _, _, n_years = self._validate(amount=original_amount, n_years=n_years)
        results = {}
        current_cpi = self._get_cpi(self.max_year, self.current_month) or self._get_cpi(self.max_year, 'Average')
        target_years = range(self.max_year - n_years, self.max_year)
        for year in target_years:
            month_cpi = self._get_cpi(year, self.current_month)
            if not month_cpi:
                month_cpi = self._get_cpi(year, 'Average')
                print(f"Month-specific CPI for {self.current_month} {year} not available, using yearly average.")
            if month_cpi:
                adjusted_value = (original_amount / month_cpi) * current_cpi
                results[year] = round(adjusted_value, 2)
        return results

    def month_by_month(self, amount):
        """
        Calculates the value of a specified amount for each month of the current year using CPI data.

        This method evaluates the given amount against the Consumer Price Index for each month of
        the most recent year available, showing how the value changes with inflation throughout the year.

        Parameters:
        ----------
        amount : float
            The amount of money to adjust using monthly CPI values.

        Returns:
        -------
        dict
            A dictionary where each key is a month and the value is the equivalent amount
            in the most current month's dollars, rounded to two decimal places.
        """
        amount = self._validate(amount=amount)[0]
        results = {}
        monthly_data = self.data[(self.data['year'] == self.max_year) & (self.data['period'] != 'Average')]
        current_cpi = self._get_cpi(self.max_year, self.current_month)

        for _, row in monthly_data.iterrows():
            month = row['period']
            cpi_value = row['value']
            if current_cpi:
                adjusted_value = (amount / cpi_value) * current_cpi
                results[month] = round(adjusted_value, 2)
            else:
                results[month] = 'CPI data missing for current month'
        return results

    def __dir__(self):
        return ['select', 'year_by_year', 'month_by_month', 'data']


engine = APIClient(cpi_adapter)

def __dir__():
    return __all__




