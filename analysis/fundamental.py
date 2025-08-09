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
fAnalyze: Unified Engine for Financial Statement Analysis, Ratio Computation, and Excel Export
────────────────────────────────────────────────────────────────────────────────────────────────

Module Purpose
────────────────────────────────────────────────────
`fAnalyze` is the core financial statement analysis interface in the Quantsumore ecosystem.
It encapsulates all logic required to **retrieve, validate, structure, analyze, and export**
company financial statements — including income statements, balance sheets, cash flow
statements, and dividend histories — into a single, reusable analysis object.

This module allows both **analysts** and **programmatic consumers** to load raw financials,
derive industry-standard ratios, conduct vertical/common-size analysis, and export results
into a professionally formatted Excel file — all through a fluent, object-oriented API.

All data is accessed through a single callable interface, powered by a backend `engine`
object (typically `PROC`) that handles URL construction, API routing, scraping, and
response decoding.

Key Use Cases
────────────────────────────────────────────────────
- Institutional-style ratio computation on quarterly or annual data
- Automated Excel export of financials with styling and indentation
- Common-size statement transformation for benchmarking and trend analysis
- Programmatic workflows needing batch loading of fundamentals
- Backend-agnostic data structuring from NASDAQ-sourced JSON APIs

System Architecture
────────────────────────────────────────────────────
1. **Data Acquisition (via `engine.Process`)**  
   The `engine` provided at initialization is responsible for fetching and parsing raw
   statement data and dividends via the NASDAQ backend. This includes:
   - Raw JSON extraction and classification into `income`, `balance`, and `cash_flow`
   - Dividend data transformation into two parts: summary and history
   - Validity checks on URLs, ticker presence, and status codes

2. **Data Wrapping and Validation**  
   Each financial statement is wrapped into a specialized Pandas DataFrame subclass
   that enables:
   - Safe property access (e.g., `self.income_statement`, `self.balance_sheet`)
   - Shape validation (to confirm data presence)
   - Type-safe access to statement rows/columns

3. **Computed Ratio Layer**  
   Once loaded, the module supports dozens of commonly-used ratios derived from
   accounting and finance standards — such as:

   - **Liquidity:** current ratio, quick ratio, cash ratio
   - **Efficiency:** asset turnover, inventory turnover, receivables turnover
   - **Profitability:** net margin, operating margin, return on equity/assets/capital
   - **Solvency:** debt-to-equity, interest coverage, equity multiplier
   - **Dividend-based:** yield, payout ratio, per-share distributions

   These methods internally extract key line items by account name and raise
   descriptive errors when required fields are missing.

4. **Common-Size and Comparative Analysis**  
   Full support is built-in for converting financial statements into "common-size"
   format — where all values are expressed as a % of a reference item:

   - Income Statement → % of Total Revenue
   - Balance Sheet → % of Total Assets
   - Cash Flow → % of Net Cash Flow from Operations

   This enables historical trend analysis or peer comparison.

5. **Excel Export Layer**  
   Financials (in raw or common-size format) can be exported via `writeStatement()`:
   
   - Professionally formatted Excel sheets (via `WriteExcel`)
   - Automatic indentation, alignment, and bolding based on account type
   - Support for overwriting or safely appending sheets to existing workbooks

Design Features
────────────────────────────────────────────────────
- **Single-entry point:** `fAnalysis(...)` acts as a function that loads all financials
  for a given ticker and period. Re-accessing previously loaded data reuses the cache.
- **Robust error handling:** All accessors are guarded by null/dataframe checks,
  ensuring clean fallback if data is unavailable or malformed.
- **Built-in introspection:** Properties and methods adjust visibility based on which
  statements are currently loaded (`__dir__` reflects current data context).
- **Engine-agnostic:** As long as the engine adheres to the expected contract
  (returning a dict with `financial_statements` and optionally `dividend`),
  it can be swapped in.
- **Developer-extensible:** New ratios, export formats, or sources can be added with
  minimal changes due to strong modular boundaries.

Data Guarantees
────────────────────────────────────────────────────
- Financial data is always returned as Pandas DataFrames, unless missing — in which case
  None is returned.
- Ratio methods return a single float value (or None), with clear failure messages if
  dependent line items are not present.
- If the backend fails or returns invalid data, the user is shown a descriptive
  error (e.g., delisted ticker, no dividend history available, malformed payload).
- Dividend data includes both summary stats (yield, annual payout) and a full
  historical table with ex-dates, declaration dates, and payout amounts.

Usage
────────────────────────────────────────────────────
from quantsumore.analysis import fAnalysis

# Load Apple Inc. financials (annual)
fAnalysis("AAPL", "Annual")

# Access full balance sheet
fAnalysis.balance_sheet

# Compute key ratios
print(fAnalysis.current_ratio())     # Current Assets / Current Liabilities
print(fAnalysis.net_margin())        # Net Income / Total Revenue

# Write all statements to Excel
fAnalysis.writeStatement("AAPL_fundamentals.xlsx", include_common_size=True)

Available Statements (after calling fAnalysis(ticker, period))
────────────────────────────────────────────────────
• `fAnalysis.income_statement`
• `fAnalysis.balance_sheet`
• `fAnalysis.cash_flow_statement`
• `fAnalysis.dividend_report` → Summary statistics (yield, annual payout)
• `fAnalysis.dividend_data` → Historical dividends (date, amount)

Available Export
────────────────────────────────────────────────────
• `fAnalysis.writeStatement(path, include_common_size=False)`
  • `path`: file path to save Excel workbook
  • `include_common_size`: include common-size versions of all statements

Implementation Notes
────────────────────────────────────────────────────
• Relies on `engine.Process()` to retrieve and categorize EquityProviderD financials
• Uses deep pandas indexing and alignment logic for cross-statement calculations
• Statement formatting is governed by `frameworks.statement_layouts`, which provides
  indentation, parent-child logic, and subtotal identification
• Excel output is powered by OpenPyXL and is 100% file-format compatible with
  Microsoft Excel and Google Sheets

Warnings & Best Practices
────────────────────────────────────────────────────
• Always call `fAnalysis(ticker, period)` before trying to access statements or ratios
• Not all companies report the same accounts — expect missing data for some metrics
• Dividend data may be unavailable for delisted or pre-IPO tickers
• Ratios return `None` (not errors) when key accounts are missing
"""
from copy import deepcopy

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ._frameworks import WriteExcel
from ..date_parser import dtparse
from ..exceptions import (
    FinancialDataNotLoadedError,
    DividendDataNotLoadedError,
    WorkbookSaveError,
    InvalidFinancialStatementIdentifier,
    NoFinancialStatementsProvided,
    TickerNotFoundError,
)
from ._calc_ratio import Ratios
from ._calc_common import Common_Size
from ._calc_vertical import Vertical_Analysis
from ..proxy import Proxy
from ..strata_utils import IterDict


__all__ = ['fAnalyze']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.


# Lazily load the entire module; actual import occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  

class fAnalyze:
    """
    Central interface for the retrieval, validation, analysis, and export of company financial statements
    and ratios, unifying access to raw data, computed metrics, and Excel output within a single object.

    Purpose:
    -----------
        The `fAnalyze` class orchestrates the end-to-end workflow for financial statement analysis.
        It loads, structures, and verifies a company’s income statement, balance sheet, cash flow statement,
        and dividend history, then provides tools for industry-standard ratio calculations, 
        common-size analysis, and formatted Excel exports—all accessible through a fluent, object-oriented API.

    Workflows:
    -----------
        - Data acquisition:   Fetch all financial statements and dividend data for a given ticker/period via the configured engine.
        - Ratio analysis:     Compute key accounting and market ratios for liquidity, efficiency, profitability, solvency, and returns.
        - Comparative analysis: Perform common-size and vertical analyses to normalize statements for period-to-period or peer comparison.
        - Excel export:       Save selected statements (standard or common-size) to a professionally formatted Excel file.

    Attributes:
    -----------
        income_statement      : Wrapped Pandas DataFrame containing the company’s income statement.
        balance_sheet         : Wrapped Pandas DataFrame containing the balance sheet.
        cash_flow_statement   : Wrapped Pandas DataFrame containing the cash flow statement.
        dividend_data         : Pandas DataFrame or None, providing historical dividend details.
        dividend_report       : Pandas DataFrame or None, providing summary dividend statistics.
        ratios                : Helper object exposing all available ratio calculation methods.
        common_size           : Helper object for generating common-size versions of all statements.
        vertical_analysis     : Helper object for performing vertical analysis.
        ticker                : Current company ticker symbol loaded.
        cache                 : Internal cache to prevent redundant data loads by ticker/period.

    Methods:
    -----------
        current_ratio(), quick_ratio(), debt_to_equity_ratio(), ...
            Compute and return standard liquidity, solvency, efficiency, and profitability ratios.

        dividend_yield(), annual_dividend(), ex_dividend_date()
            Access key dividend statistics and recent ex-dividend information.

        CommonSize(financial_statement)
            Generate a common-size statement for income, balance sheet, or cash flow as percentages of a key base item.

        VerticalAnalysis(financial_statement)
            Perform vertical analysis to present each line item as a percentage of statement total.

        writeStatement(save_path, financial_statements=None, include_common_size=False)
            Export selected statements (raw or common-size) to a formatted Excel file at the specified path.

    Notes:
    -----------
        - Always invoke the instance (i.e., `fAnalyze(ticker, period)`) before accessing statements or ratios.
        - All statement and dividend data are delivered as Pandas DataFrames for seamless analysis and export.
        - Ratio methods return either a float, Series, or None if required accounts are unavailable—never raise on missing line items.
        - Designed to be backend-agnostic: any engine implementing the expected `Process()` contract is supported.
        - Built-in validation and custom exceptions guard against accessing uninitialized or incomplete data.
        - Excel output is 100% compatible with Microsoft Excel and Google Sheets, with auto-formatting for clarity.
    """
    def __init__(self, engine):
        """
        Initialize an fAnalyze instance and prepare all attributes for financial data analysis.

        Parameters:
        -----------
            engine : object
                Backend engine responsible for fetching, parsing, and structuring financial statement
                and dividend data for a given ticker and reporting period. Must provide a compatible
                `Process(ticker, period)` interface.

        Initializes:
        -----------
            engine                : Stores the provided backend engine for all subsequent data operations.
            ticker                : Set to None; will hold the ticker symbol once data is loaded.
            _income_statement     : Internal storage for the wrapped income statement DataFrame.
            _balance_sheet        : Internal storage for the wrapped balance sheet DataFrame.
            _cash_flow_statement  : Internal storage for the wrapped cash flow statement DataFrame.
            dividend_data         : Set to None; will hold dividend history data if available.
            dividend_report       : Set to None; will hold dividend summary data if available.
            ratios                : Helper object, exposing all ratio calculation methods.
            common_size           : Helper object for generating common-size statements.
            vertical_analysis     : Helper object for vertical analysis of statements.
            cache                 : In-memory dictionary for caching financial data by (ticker, period).

        Notes:
        -----------
            - The instance is not ready for analysis until `__call__` is used to load a specific ticker and period.
            - All statement attributes are initialized empty and will be replaced with validated, structured data
              after successful data acquisition.
            - Helper objects (`ratios`, `common_size`, `vertical_analysis`) are pre-initialized for immediate use
              once data is loaded.
        """  	
        self.engine = engine
        self.ticker = None       
        self._income_statement = pd.DataFrame()  
        self._balance_sheet = pd.DataFrame()  
        self._cash_flow_statement = pd.DataFrame() 
        self.dividend_data = None
        self.dividend_report = None
        
        # ──── Imports ────        
        self.ratios = Ratios(self)   
        self.common_size = Common_Size(self)       
        self.vertical_analysis = Vertical_Analysis(self)   
        self.cache = {}      

    class Statement:
        """
        A wrapper for individual financial statements, providing structured access and
        enhanced utilities over a Pandas DataFrame representation.

        Purpose:
        -----------
            The `Statement` class encapsulates a single financial statement (such as an income statement,
            balance sheet, or cash flow statement) and offers specialized accessors, 
            property delegation, and convenience methods for financial analysis.

        Attributes:
        -----------
            data              : Pandas DataFrame holding the raw statement data, indexed by account name and
                                with columns representing reporting periods.
            _parsed_dates     : Internal cache mapping original column headers to parsed datetime objects.

        Methods:
        -----------
            __getattr__(item)
                Delegates attribute access directly to the underlying DataFrame.

            __getitem__(key), __setitem__(key, value)
                Enable dictionary-like access and mutation of the wrapped DataFrame.

            list_accounts()
                Return a list of all account names (row indices) present in the statement,
                excluding empty or missing rows.

            LineItem(account_name, timeframe=None)
                Retrieve the value(s) for a given account name, optionally filtered by
                a specific reporting period ("current", "past", or a column label).
                Case-insensitive and raises KeyError if the account is not found.

            _get_parsed_dates()
                Parse column headers into datetime objects, used for robust time-based lookups.

            __repr__()
                Returns the standard string representation of the DataFrame.

        Notes:
        -----------
            - Most DataFrame functionality is accessible directly through the `Statement` object,
              including attribute and item access.
            - Provides robust account lookups, forgiving to minor inconsistencies in statement row naming.
            - Intended for internal use within the `fAnalyze` workflow, but may be reused for
              custom statement analysis elsewhere.
        """    	
        def __init__(self, data):
            """
            Initialize a Statement instance with provided financial statement data.

            Parameters:
            -----------
                data : pandas.DataFrame or array-like
                    The raw financial statement data, either as a DataFrame or an object convertible
                    to a DataFrame. Rows should represent account names, and columns should represent
                    reporting periods (typically as date strings).

            Initializes:
            -----------
                data           : Stores the provided financial data as a Pandas DataFrame.
                _parsed_dates  : Internal cache for parsed column date labels, set to None initially.

            Notes:
            -----------
                - If `data` is not already a DataFrame, it will be converted automatically.
                - This constructor does not validate account or column structure; validation occurs elsewhere.
            """
            self.data = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
            self._parsed_dates = None

        def __getattr__(self, item):
            return getattr(self.data, item)

        def __getitem__(self, key):
            return self.data[key]

        def __setitem__(self, key, value):
            self.data[key] = value

        def __repr__(self):
            return repr(self.data)

        def list_accounts(self):
            statement = self.data.replace('', pd.NA)
            filtered_statement = statement.dropna(how='all')
            accounts = filtered_statement.index.tolist()
            return accounts

        def _get_parsed_dates(self):
            if self._parsed_dates is None:
                self._parsed_dates = {col: dtparse.parse(date_input=col) for col in self.data.columns}
            return self._parsed_dates

        def LineItem(self, account_name, timeframe=None):
            account_name_lower = account_name.lower()
            accounts_lower_map = {acct.lower(): acct for acct in self.list_accounts()}
            if account_name_lower not in accounts_lower_map:
                raise KeyError(f"Account '{account_name}' not found in the financial statement.")
            original_account_name = accounts_lower_map[account_name_lower]
            if timeframe:
                dates = self._get_parsed_dates()
                if timeframe == "current":
                    selected_date = dtparse.parse(date_input=max(dates.values()), to_format='%Y-%m-%d')
                elif timeframe == "past":
                    selected_date = dtparse.parse(date_input=min(dates.values()), to_format='%Y-%m-%d')
                else:
                    if timeframe in dates:
                        selected_date = timeframe
                    else:
                        raise ValueError("Invalid timeframe specified.")
                return self.data.loc[original_account_name, selected_date]
            return self.data.loc[original_account_name]
           
        def __dir__(self):
            return ['LineItem'] 
           
    def __assert_data_available(self, required_data):
        """ Verify that all required data objects are present and non-empty."""
        for data in required_data:
            if data is None or (hasattr(data, 'empty') and data.empty):
                raise AttributeError("Required financial data is not available.")

    def __fillna_empty(self, df):
        """ Return a copy of the DataFrame with all missing values (NaN/NA) replaced by empty strings."""    	
        df = deepcopy(df)
        return df.fillna("")
       
    def is_loaded(self, df):
        return df is not None and not df.empty      
           
    def __call__(self, ticker, period, api_key=None):
        """ Calls the instance as a function to fetch and process financial data for a specified ticker and period."""    	
        self.get_financial_data(ticker, period, api_key=api_key)    
        
    def get_financial_data(self, ticker, period, api_key=None):    
        """
        Fetch and load all available financial statements and dividend data for a specified ticker and period.

        Parameters:
        -----------
            ticker : str or list of str
                The company ticker symbol to fetch data for. If a list is provided, the first element is used.
            period : str
                The reporting period to retrieve (e.g., "Annual", "Quarterly").

        Workflow:
        -----------
            - If data for the given (ticker, period) is cached, reload all statements and dividends from cache.
            - If not cached, uses the engine's `Process` method to retrieve raw financial data from the backend.
            - Loads and validates the income statement, balance sheet, and cash flow statement; clears all if any are missing.
            - Separately attempts to load dividend summary and history, updating the cache if successful.

        Sets:
        -----------
            income_statement     : Populated with wrapped DataFrame if successfully loaded, else set to None.
            balance_sheet        : Populated with wrapped DataFrame if successfully loaded, else set to None.
            cash_flow_statement  : Populated with wrapped DataFrame if successfully loaded, else set to None.
            dividend_data        : Populated with DataFrame if successfully loaded, else set to None.
            dividend_report      : Populated with summary DataFrame if successfully loaded, else set to None.
            cache                : Updated with all successfully loaded data for the (ticker, period) key.

        Raises:
        -----------
            ValueError           : If the ticker argument is missing or of invalid type.

        Notes:
        -----------
            - If any of the main statements are missing or empty, all are set to None to avoid partial data issues.
            - Errors encountered during loading are printed to the console, but do not halt execution.
            - Dividend data is optional and may not be available for some tickers (e.g., delisted or pre-IPO companies).
            - This method should be called before accessing any analysis or export features.
        """       	
        if isinstance(ticker, (list, tuple)):
            if not ticker:
                raise TickerNotFoundError("Cannot find ticker symbol!")
            ticker = ticker[0]

        if not isinstance(ticker, str):
            raise ValueError("Ticker must be a single string value.")

        self.ticker = ticker.strip()
        
        cache_key = (self.ticker, period)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            self.income_statement = cached_data['income_statement']
            self.balance_sheet = cached_data['balance_sheet']
            self.cash_flow_statement = cached_data['cash_flow_statement']
            self.dividend_data = cached_data.get('dividend_data', None)
            self.dividend_report = cached_data.get('dividend_report', None)
        else:
            # 1. Attempt to Load Financial Statements
            data = self.engine.Process(self.ticker, period, api_key=api_key)   
            statements = data.get('financial_statements', [])

            # 1a. No statements returned at all
            if not statements:
                self.income_statement     = None
                self.balance_sheet        = None
                self.cash_flow_statement  = None
                print(f"Financial Statements could not be loaded for {self.ticker}.")

            # 1b. At least one statement triple returned—unpack safely
            else:
                income, balance, cash_flow = statements[0]

                # 1b-i. Check for usable DataFrames and sanitize or set None per statement
                loaded_income = (
                    self.__fillna_empty(income)
                    if isinstance(income, pd.DataFrame) and not income.empty else None
                )
                loaded_balance = (
                    self.__fillna_empty(balance)
                    if isinstance(balance, pd.DataFrame) and not balance.empty else None
                )
                loaded_cashflow = (
                    self.__fillna_empty(cash_flow)
                    if isinstance(cash_flow, pd.DataFrame) and not cash_flow.empty else None
                )

                # 1b-ii. Assign to class and cache
                self.income_statement     = loaded_income
                self.balance_sheet        = loaded_balance
                self.cash_flow_statement  = loaded_cashflow

                self.cache[cache_key] = {
                    'income_statement':     loaded_income,
                    'balance_sheet':        loaded_balance,
                    'cash_flow_statement':  loaded_cashflow,
                }

                # 1b-iii. Reporting: check if all were loaded, or note which are missing
                if self.is_loaded(loaded_income) and self.is_loaded(loaded_balance) and self.is_loaded(loaded_cashflow):
                    print(f"Financial Statements successfully loaded for {self.ticker}.")
                else:
                    missing = []
                    if loaded_income is None or loaded_income.empty:
                        missing.append("Income Statement")
                    if loaded_balance is None or loaded_balance.empty:
                        missing.append("Balance Sheet")
                    if loaded_cashflow is None or loaded_cashflow.empty:
                        missing.append("Cash Flow Statement")

                    print(f"Financial Statements loaded for {self.ticker}.")
                    print(f"  • Missing: {', '.join(missing)}")                

            # 2. Attempt to Load Dividend Data
            divs = data.get('dividend', [])

            # 2a. API returned a string error
            if isinstance(divs, str) and divs.startswith("Error:"):
                self.dividend_report = None
                self.dividend_data   = None
                print(divs.replace("Error: ", ""))

            # 2b. No entries at all
            elif not divs:
                self.dividend_report = None
                self.dividend_data   = None
                print(f"No dividend data available for {self.ticker}.")

            # 2c. At least one entry returned—unpack safely
            else:
                report, hist = divs[0]
                if report is not None and hist is not None:
                    self.dividend_report = report
                    self.dividend_data   = hist
                    self.cache[cache_key].update({
                        'dividend_report': report,
                        'dividend_data':   hist
                    })
                    print(f"Dividend data successfully loaded for {self.ticker}.")
                else:
                    self.dividend_report = None
                    self.dividend_data   = None
                    print(f"No valid dividend data found for {self.ticker}.")

                
    # These property methods manage access to core financial data objects.
    #
    # Each property enforces that the underlying data is both present and loaded
    # (i.e., not empty), raising a custom exception if the required information is missing.
    # This prevents accidental analysis or export of incomplete financial datasets.
    # 
    # The getter methods always return a deep copy of the underlying data to ensure 
    # that calling code cannot inadvertently modify the original object. The setters 
    # convert incoming raw data to a standardized internal format where appropriate,
    # or clear the internal state if `None` is assigned.
    
    # ────────── Income Statement ────   
    @property
    def income_statement(self):
        stmt = self._income_statement
        if not hasattr(stmt, 'data') or stmt.data.empty:
            raise FinancialDataNotLoadedError(f"No income‐statement data loaded for ticker {self.ticker!r}.")
        return deepcopy(stmt)
       
    @income_statement.setter
    def income_statement(self, value):
        self._income_statement = self.Statement(value) if value is not None else pd.DataFrame()

    # ────────── Balance Sheet ──── 
    @property
    def balance_sheet(self):
        bs = self._balance_sheet
        if not hasattr(bs, 'data') or bs.data.empty:
            raise FinancialDataNotLoadedError(f"No balance‐sheet data loaded for ticker {self.ticker!r}.")
        return deepcopy(bs)   
       
    @balance_sheet.setter
    def balance_sheet(self, value):
        self._balance_sheet = self.Statement(value) if value is not None else pd.DataFrame()

    # ────────── Cash Flow Statement ────    
    @property
    def cash_flow_statement(self):
        cf = self._cash_flow_statement
        if not hasattr(cf, 'data') or cf.data.empty:
            raise FinancialDataNotLoadedError(f"No cash‐flow‐statement data loaded for ticker {self.ticker!r}.")
        return deepcopy(cf)
       
    @cash_flow_statement.setter
    def cash_flow_statement(self, value):
        self._cash_flow_statement = self.Statement(value) if value is not None else pd.DataFrame()

    # ────────── Dividends ────     
    @property
    def dividend_data(self):
        if self._dividend_data is None:
            raise DividendDataNotLoadedError(f"No raw dividend data loaded for ticker {self.ticker!r}.")
        return deepcopy(self._dividend_data)    
       
    @dividend_data.setter
    def dividend_data(self, value):
        self._dividend_data = value

    @property
    def dividend_report(self):
        if self._dividend_report is None:
            raise DividendDataNotLoadedError(f"No dividend‐summary report loaded for ticker {self.ticker!r}.")
        return deepcopy(self._dividend_report)   
       
    @dividend_report.setter
    def dividend_report(self, value):
        self._dividend_report = value


    
    ######################################################################
    # Calculate key financial ratios for company analysis
    ######################################################################  

    # A comprehensive set of methods for calculating key financial ratios
    # using data from a company’s financial statements. It covers all major categories—liquidity,
    # solvency, profitability, efficiency, and coverage—enabling robust analysis and benchmarking.
    # Each method is designed to pull and clean the required accounts from the parent Analyze instance,
    # handling missing data where possible.     
    
    def dividend_yield(self):
        """
        Calculate and return the company’s dividend yield.

        Returns:
        ---------
            float or None: The dividend yield as a decimal (e.g., 0.024 for 2.4%), or None if unavailable.

        Raises:
        --------
            ValueError: If required dividend data is not available.

        Notes:
        -------
            Dividend yield represents the ratio of annual dividends per share to the share price.
        """        
        self.__assert_data_available([self.dividend_data, self.dividend_report])
        return self.ratios._dividend_yield()

    def ex_dividend_date(self):
        """
        Retrieve the company’s most recent ex-dividend date.

        Returns:
        --------
            str or None: The ex-dividend date as a string in 'YYYY-MM-DD' format, or None if unavailable.

        Raises:
        -------
            ValueError: If required dividend data is not available.

        Notes:
        ------
            The ex-dividend date is the cutoff date for being eligible to receive the next dividend payment.
        """
        self.__assert_data_available([self.dividend_data, self.dividend_report])
        return self.ratios._ex_dividend_date()

    def annual_dividend(self):
        """
        Return the total annual dividend paid per share.

        Returns:
        --------
            float or None: The annual dividend per share, or None if unavailable.

        Raises:
        -------
            ValueError: If required dividend data is not available.

        Notes:
        ------
            This value reflects the sum of all dividends paid over the past year for each outstanding share.
        """
        self.__assert_data_available([self.dividend_data, self.dividend_report])
        return self.ratios._annual_dividend()

    def current_ratio(self):
        """
        Calculate and return the current ratio from the balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The current ratio (current assets divided by current liabilities),
            either as a single float or a series by period, or None if unavailable.

        Raises:
        -------
            ValueError: If required balance sheet data is not available.

        Notes:
        ------
            The current ratio is a key liquidity metric indicating the company’s ability to cover short-term obligations.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._current_ratio()
           
    def quick_ratio(self):
        """
        Calculate and return the quick ratio from the balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The quick ratio (also known as the acid-test ratio), or None if unavailable.

        Raises:
        -------
            ValueError: If required balance sheet data is not available.

        Notes:
        ------
            The quick ratio measures a company’s ability to meet short-term obligations using its most liquid assets
            (excluding inventory). A ratio above 1 generally indicates good short-term financial health.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._quick_ratio()


    def cash_ratio(self):
        """
        Calculate and return the cash ratio from the balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The cash ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required balance sheet data is not available.

        Notes:
        ------
            The cash ratio is the most conservative liquidity ratio, measuring a company’s ability to pay
            short-term obligations with only its cash and cash equivalents.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._cash_ratio()


    def debt_to_equity_ratio(self):
        """
        Calculate and return the debt to equity ratio from the balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The debt-to-equity ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required balance sheet data is not available.

        Notes:
        ------
            This ratio indicates the relative proportion of shareholders' equity and debt used to finance a company’s assets.
            A higher ratio may indicate greater financial risk.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._debt_to_equity_ratio()

    def debt_to_capital_ratio(self):
        """
        Calculate and return the debt-to-capital ratio from the balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The debt-to-capital ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required balance sheet data is not available.

        Notes:
        ------
            The debt-to-capital ratio measures the proportion of a company’s capital structure that is financed by debt,
            providing insights into leverage and risk.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._debt_to_capital_ratio()

    def gross_profit_margin_ratio(self):
        """
        Calculate and return the gross profit margin ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The gross profit margin ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is not available.

        Notes:
        ------
            Gross profit margin is a profitability ratio that shows the percentage of revenue that exceeds the cost of goods sold (COGS).
            It provides insight into a company’s production efficiency.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._gross_profit_margin_ratio()

    def operating_profit_margin_ratio(self):
        """
        Calculate and return the operating profit margin ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The operating profit margin ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is not available.

        Notes:
        ------
            Operating profit margin measures the proportion of revenue left after covering operating expenses.
            It’s a key indicator of operational efficiency.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._operating_profit_margin_ratio()

    def net_profit_margin(self):
        """
        Calculate and return the net profit margin from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The net profit margin, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is not available.

        Notes:
        ------
            Net profit margin is the percentage of revenue remaining after all expenses, taxes, and costs have been deducted.
            It is a comprehensive measure of profitability.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._net_profit_margin()

    def ebit_margin(self):
        """
        Calculate and return the EBIT margin from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The EBIT (Earnings Before Interest and Taxes) margin, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The EBIT margin shows the percentage of revenue remaining after operating and non-operating expenses, 
            excluding interest and taxes. It’s a key indicator of operating profitability.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._ebit_margin()

    def rd_to_revenue_ratio(self):
        """
        Calculate and return the R&D to revenue ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The ratio of research & development (R&D) expense to total revenue, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            This ratio measures the portion of revenue invested in research and development. It’s useful for evaluating a company’s focus on innovation.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._rd_to_revenue_ratio()

    def sga_to_revenue_ratio(self):
        """
        Calculate and return the SG&A to revenue ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The ratio of selling, general, and administrative (SG&A) expense to revenue, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The SG&A to revenue ratio reflects operating expenses (excluding COGS) as a share of total revenue,
            helping to assess cost control and operational efficiency.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._sga_to_revenue_ratio()

    def interest_coverage_ratio(self):
        """
        Calculate and return the interest coverage ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The interest coverage ratio (EBIT / interest expense), or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The interest coverage ratio shows how easily a company can pay interest on outstanding debt.
            Higher values indicate stronger ability to meet interest obligations.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._interest_coverage_ratio()

    def pretax_profit_margin_ratio(self):
        """
        Calculate and return the pretax profit margin ratio from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The pretax profit margin ratio, or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The pretax profit margin measures earnings before tax as a percentage of revenue, 
            highlighting profitability before tax obligations.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._pretax_profit_margin_ratio()

    def tax_burden(self):
        """
        Calculate and return the tax burden from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The tax burden ratio (net income / earnings before tax), or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The tax burden reflects the proportion of earnings before tax that remains after taxes are paid, 
            indicating the effective tax rate.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._tax_burden()

    def interest_burden(self):
        """
        Calculate and return the interest burden from the income statement.

        Returns:
        --------
            float or pandas.Series or None: The interest burden ratio (earnings before tax / EBIT), or None if unavailable.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The interest burden measures how much EBIT is reduced by interest expense before tax, providing insight into financing costs.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._interest_burden()

    def capex_ratio(self):
        """
        Calculate and return the CAPEX ratio from the cash flow statement.

        Returns:
        --------
            float or pandas.Series or None: The ratio of net operating cash flow to capital expenditures (CAPEX).

        Raises:
        -------
            ValueError: If required cash flow statement data is missing.

        Notes:
        ------
            This ratio shows how much operating cash flow is being used for capital investment.
            It provides insight into the sustainability of a company’s capital spending.
        """
        self.__assert_data_available([self.cash_flow_statement])
        return self.ratios._capex_ratio()

    def free_cash_flow_to_operating_cash_flow_ratio(self):
        """
        Calculate and return the ratio of free cash flow to operating cash flow from the cash flow statement.

        Returns:
        --------
            float or pandas.Series or None: The ratio of free cash flow to operating cash flow.

        Raises:
        -------
            ValueError: If required cash flow statement data is missing.

        Notes:
        ------
            This ratio indicates the proportion of operating cash flow that remains after capital expenditures,
            reflecting the company’s financial flexibility.
        """
        self.__assert_data_available([self.cash_flow_statement])
        return self.ratios._free_cash_flow_to_operating_cash_flow_ratio()

    def defensive_interval_ratio(self):
        """
        Calculate and return the defensive interval ratio using the income statement and balance sheet.

        Returns:
        --------
            float or pandas.Series or None: The defensive interval ratio (liquid assets / daily operating expenses).

        Raises:
        -------
            ValueError: If required financial statement data is missing.

        Notes:
        ------
            The defensive interval ratio measures how many days a company can cover its operating expenses
            using only its most liquid assets. It is a conservative liquidity metric.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])   
        return self.ratios._defensive_interval_ratio()

    def fixed_charge_coverage_ratio(self, lease_payments=0):
        """
        Calculate and return the fixed charge coverage ratio from the income statement.

        Args:
        -----
            lease_payments (float, optional): Additional lease payments to include in fixed charges. Default is 0.

        Returns:
        --------
            float or pandas.Series or None: The fixed charge coverage ratio, or None if data is missing.

        Raises:
        -------
            ValueError: If required income statement data is missing.

        Notes:
        ------
            The fixed charge coverage ratio evaluates a company’s ability to meet its fixed financial obligations,
            including interest and lease payments.
        """
        self.__assert_data_available([self.income_statement])
        return self.ratios._fixed_charge_coverage_ratio(lease_payments=lease_payments)

    def receivables_turnover_ratio(self):
        """
        Calculate and return the receivables turnover ratio using the income statement and balance sheet.

        Returns:
        --------
            pandas.Series or None: The receivables turnover ratio for each period, or None if data is missing.

        Raises:
        -------
            ValueError: If required statement data is missing.

        Notes:
        ------
            This ratio measures how many times receivables are collected during a period,
            indicating the effectiveness of credit and collection policies.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])   
        return self.ratios._receivables_turnover_ratio()

    def inventory_turnover_ratio(self):
        """
        Calculate and return the inventory turnover ratio using the income statement and balance sheet.

        Returns:
        --------
            pandas.Series or None: The inventory turnover ratio for each period, or None if data is missing.

        Raises:
        -------
            ValueError: If required statement data is missing.

        Notes:
        ------
            The inventory turnover ratio shows how often inventory is sold and replaced over a period.
            Higher values may indicate efficient inventory management.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])        
        return self.ratios._inventory_turnover_ratio()

    def days_sales_outstanding(self):
        """
        Calculate and return the Days Sales Outstanding (DSO) using the income statement and balance sheet.

        Returns:
        --------
            pandas.Series or None: The DSO for each period, or None if data is missing.

        Raises:
        -------
            ValueError: If required statement data is missing.

        Notes:
        ------
            DSO measures the average number of days it takes to collect payment after a sale.
            Lower values generally indicate more efficient collections.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._days_sales_outstanding()
      
    def days_inventory_on_hand(self):
        """
        Calculate and return the Days Inventory On Hand (DIOH).

        Returns:
        --------
            pandas.Series or None: The average number of days inventory is held before being sold, for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            DIOH measures inventory efficiency, indicating how quickly a company sells its inventory.
            Lower values generally reflect more efficient inventory management.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._days_inventory_on_hand()

    def payables_turnover_ratio(self):
        """
        Calculate and return the Payables Turnover Ratio.

        Returns:
        --------
            pandas.Series or None: The ratio for each period, indicating how quickly payables are paid.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            This ratio shows how many times a company pays off its accounts payable during a period.
            Higher values may signal prompt payment to suppliers.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._payables_turnover_ratio()

    def days_of_payables(self):
        """
        Calculate and return the Number of Days Payables Ratio.

        Returns:
        --------
            pandas.Series or None: The average number of days the company takes to pay its suppliers, for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            This metric indicates the average time the company takes to settle its accounts payable.
            Higher values may indicate longer credit terms from suppliers or delayed payments.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._days_of_payables()

    def cash_conversion_cycle(self):
        """
        Calculate and return the Cash Conversion Cycle (CCC).

        Returns:
        --------
            pandas.Series or None: The cash conversion cycle for each period.

        Raises:
        -------
            ValueError: If required component data is missing.

        Notes:
        ------
            The CCC measures the time (in days) it takes for a company to convert its investments in inventory
            and other resources into cash flows from sales. It combines DSO, DIOH, and days of payables.
        """
        return self.ratios._cash_conversion_cycle()

    def return_on_equity(self):
        """
        Calculate and return the Return on Equity (ROE).

        Returns:
        --------
            pandas.Series or None: The ROE for each period, representing net income as a percentage of average shareholders' equity.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            ROE measures a company's profitability by revealing how much profit a company generates with the money
            shareholders have invested.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_equity()

    def working_capital_turnover(self):
        """
        Calculate and return the Working Capital Turnover Ratio.

        Returns:
        --------
            pandas.Series or None: The working capital turnover ratio for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            This ratio measures how efficiently a company uses its working capital to generate sales.
            Higher values indicate efficient use of short-term assets and liabilities.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._working_capital_turnover()

    def fixed_asset_turnover(self):
        """
        Calculate and return the Fixed Asset Turnover Ratio.

        Returns:
        --------
            pandas.Series or None: The fixed asset turnover ratio for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            The fixed asset turnover ratio measures how effectively a company uses its fixed assets
            to generate revenue. Higher values typically indicate better utilization of fixed assets.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._fixed_asset_turnover()

    def total_asset_turnover(self):
        """
        Calculate and return the Total Asset Turnover Ratio.

        Returns:
        --------
            pandas.Series or None: The total asset turnover ratio for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            This ratio measures how efficiently a company uses all of its assets to generate revenue.
            Higher values typically indicate better asset utilization.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._total_asset_turnover()

    def operating_return_on_assets(self):
        """
        Calculate and return the Operating Return on Assets (OROA).

        Returns:
        --------
            pandas.Series or None: The operating return on assets for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            OROA measures how efficiently a company’s operating income is generated from its total assets.
            It is useful for evaluating core business profitability, excluding non-operating items.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._operating_return_on_assets()

    def return_on_assets(self):
        """
        Calculate and return the Return on Assets (ROA).

        Returns:
        --------
            pandas.Series or None: The return on assets for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            ROA expresses net income as a percentage of average total assets.
            It is a key metric for understanding overall profitability and asset efficiency.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_assets()

    def equity_multiplier(self):
        """
        Calculate and return the Equity Multiplier.

        Returns:
        --------
            pandas.Series or None: The equity multiplier (financial leverage) for each period.

        Raises:
        -------
            ValueError: If required balance sheet data is missing.

        Notes:
        ------
            The equity multiplier reflects a company’s financial leverage by showing how much of assets
            are financed by shareholders’ equity. Higher values indicate greater leverage.
        """
        self.__assert_data_available([self.balance_sheet])
        return self.ratios._equity_multiplier()

    def return_on_invested_capital_pre_tax(self):
        """
        Calculate and return the Pre-Tax Return on Invested Capital (ROIC).

        Returns:
        --------
            pandas.Series or None: The pre-tax ROIC for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            Pre-tax ROIC measures the efficiency and profitability of company capital investments before taxes.
            It is useful for comparing returns across companies regardless of their tax environments.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_invested_capital_pre_tax()

    def return_on_invested_capital_after_tax(self):
        """
        Calculate and return the After-Tax Return on Invested Capital (ROIC).

        Returns:
        --------
            pandas.Series or None: The after-tax ROIC for each period.

        Raises:
        -------
            ValueError: If required income statement or balance sheet data is missing.

        Notes:
        ------
            After-tax ROIC accounts for the impact of income taxes and provides a realistic measure of capital returns.
            It is a key metric for evaluating value creation from the company’s invested capital.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_invested_capital_after_tax()



    ######################################################################
    # Normalize financial statements for comparative analysis
    ######################################################################
    
    # The CommonSize and VerticalAnalysis methods provide tools for normalizing financial statements
    # to facilitate comparison across companies and periods:
    #
    # - CommonSize: Expresses each line item as a percentage of a key figure (e.g., Total Revenue or Total Assets).
    # - VerticalAnalysis: Presents each line item as a proportion of a statement total within the same period.
    # 
    # These approaches are useful for analyzing company structure, cost breakdowns, and trends,
    # regardless of the absolute scale of the business.
    
    def CommonSize(self, financial_statement):
        """
        Generate a common size version of the specified financial statement.

        Parameters:
        -----------
            financial_statement : str
                Identifier for the financial statement to analyze. Accepts any of the following:
                - Income Statement: "I", "IS", "Income", "Income_Statement", "Income Statement"
                - Balance Sheet: "B", "BS", "Balance Sheet", "Balance_Sheet"
                - Cash Flow Statement: "C", "CF", "Cash", "Cash Flow", "Cash_Flow",
                  "Cash Flow Statement", "Cash_Flow_Statement"

        Returns:
        -----------
            pandas.DataFrame : A common size financial statement where each value is expressed
                               as a percentage of a key base (e.g., total revenue or total assets).

        Notes:
        -----------
            This is useful for comparing financial performance across companies or time periods
            regardless of absolute scale.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet, self.cash_flow_statement])
        return self.common_size._CommonSize(financial_statement=financial_statement) 

    def VerticalAnalysis(self, financial_statement):
        """
        Perform a vertical analysis on the specified financial statement.

        Parameters:
        -----------
            financial_statement : str
                Identifier for the financial statement to analyze. Accepts any of the following:
                - Income Statement: "I", "IS", "Income", "Income_Statement", "Income Statement"
                - Balance Sheet: "B", "BS", "Balance Sheet", "Balance_Sheet"
                - Cash Flow Statement: "C", "CF", "Cash", "Cash Flow", "Cash_Flow",
                  "Cash Flow Statement", "Cash_Flow_Statement"

        Returns:
        -----------
            pandas.DataFrame : A DataFrame showing the vertical analysis, where each line item
                               is presented as a percentage of a key figure (e.g., total revenue or assets).

        Notes:
        -----------
            Vertical analysis highlights the relative weight of each line item within a statement,
            aiding internal structure analysis and trend detection.
        """  	
        self.__assert_data_available([self.income_statement, self.balance_sheet, self.cash_flow_statement])
        return self.vertical_analysis._VerticalAnalysis(financial_statement=financial_statement) 



    ######################################################################
    # Write selected financial statements to an Excel file
    ######################################################################
    
    # The writeStatement method writes selected financial statements to an Excel file at the specified path. It allows for the   
    # inclusion of standard or common size formats depending on the include_common_size flag. This method simplifies the process 
    # of exporting financial data by providing options to export as standard numbers or as percentages of a key total figure,    
    # making it versatile for comparative and period-over-period financial analysis.               
    
    def writeStatement(self, save_path, financial_statements=None, include_common_size=False):
        """
        Export one or more financial statements to an Excel file.

        Parameters:
        -----------
            save_path : str
                Path where the Excel file will be saved. If the file exists, it will be overwritten.

            financial_statements : str or list of str, optional
                Names or aliases of financial statements to write. If None or 'all',
                all available statements will be included. Valid identifiers include:
                  - Income Statement: "I", "IS", "Income", "Income_Statement", "Income Statement"
                  - Balance Sheet: "B", "BS", "Balance Sheet", "Balance_Sheet"
                  - Cash Flow Statement: "C", "CF", "Cash", "Cash Flow", "Cash_Flow",
                    "Cash Flow Statement", "Cash_Flow_Statement"

            include_common_size : bool, optional
                If True, write each statement in common size format (as percentages of a base figure).
                If False, write standard absolute values. Defaults to False.

        Returns:
        -----------
            None

        Raises:
        -----------
            ValueError : If no valid financial statements are provided, or if identifiers are invalid.
            Exception : Propagates errors from file I/O or Excel writing.

        Notes:
        -----------
            This method simplifies exporting financial data for reporting or comparative analysis.
            Supports both standard and common size formats for greater flexibility.
        """
        self.__assert_data_available([self.income_statement, self.balance_sheet, self.cash_flow_statement])

        valid_statements = {
            "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
            "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
            "Cash Flow Statement": ["Cash Flow Statement", "Cash_Flow_Statement", "C", "CF", "Cash Flow", "Cash_Flow", "Cash"],
        }
        if include_common_size:
            formats = "common_size"
        else:
            formats = "standard"
            
        statements = {
            "standard": {
                "Income Statement": self.income_statement,
                "Balance Sheet": self.balance_sheet,
                "Cash Flow Statement": self.cash_flow_statement
            },
            "common_size": {
                "Income Statement": self.common_size._CommonSize(financial_statement="Income Statement"),
                "Balance Sheet": self.common_size._CommonSize(financial_statement="Balance Sheet"),
                "Cash Flow Statement": self.common_size._CommonSize(financial_statement="Cash Flow Statement")
            }
        }[formats]               

        if financial_statements:
            if isinstance(financial_statements, str):
                financial_statements = [financial_statements]
            try:
                resolved_statements = [IterDict.key_from_mapping(f, valid_statements, invert=False) for f in financial_statements]
                statements = {name: stmt for name, stmt in statements.items() if name in resolved_statements}
            except KeyError as e:
                raise InvalidFinancialStatementIdentifier(f"Invalid financial statement identifier: {e}")

        if not statements:
            raise NoFinancialStatementsProvided("No valid financial statements provided to write.")

        try:
            with WriteExcel() as excel_writer:
                for name, statement in statements.items():
                    excel_writer.write_statement(statement)
                excel_writer.save(filename=save_path)
        except WorkbookSaveError:
            raise
        except Exception as e:
            raise WorkbookSaveError(f"An error occurred while writing statements: {e}") from e

    # __dir__ method provides dynamic introspection support for the fAnalyze instance.
    #
    # It constructs and returns a list of available attributes and methods based on which
    # financial statements and dividend data are currently loaded and accessible.
    #
    # Only methods and properties relevant to the present data context are exposed—analysis
    # and ratio methods appear if all core statements are loaded, and dividend-related
    # methods appear only when both dividend data and report are available.
    #
    # This design enables more intuitive autocompletion, prevents confusion when certain
    # data is missing, and helps interactive environments reflect only valid, actionable
    # features at any point in time.    
    
    def __dir__(self):
        available_attributes = []       
        financial_statements_exist = (
            hasattr(self._income_statement, 'data') and not self._income_statement.data.empty and
            hasattr(self._balance_sheet, 'data') and not self._balance_sheet.data.empty and
            hasattr(self._cash_flow_statement, 'data') and not self._cash_flow_statement.data.empty
        )
        if financial_statements_exist:
            available_attributes.extend([
                "CommonSize", "balance_sheet", "capex_ratio", "cash_flow_statement", "current_ratio",
                "debt_to_equity_ratio", "ebit_margin", "free_cash_flow_to_operating_cash_flow_ratio", "gross_profit_margin_ratio", "income_statement",
                "interest_coverage_ratio", "net_profit_margin", "operating_profit_margin_ratio", "quick_ratio", "rd_to_revenue_ratio",
                "sga_to_revenue_ratio", "cash_ratio", "pretax_profit_margin_ratio", "tax_burden", "interest_burden",
                "debt_to_capital_ratio", "defensive_interval_ratio", "fixed_charge_coverage_ratio", "receivables_turnover_ratio", "inventory_turnover_ratio",
                "writeStatement", "Statement", "VerticalAnalysis", "days_sales_outstanding", "days_inventory_on_hand",
                "payables_turnover_ratio", "days_of_payables", "cash_conversion_cycle", "return_on_equity", "working_capital_turnover",
                "fixed_asset_turnover", "total_asset_turnover", "operating_return_on_assets", "return_on_assets", "equity_multiplier",
                "return_on_invested_capital_pre_tax", "return_on_invested_capital_after_tax",
            ])
            if self.dividend_data is not None and self.dividend_report is not None:
                available_attributes.extend([
                    "dividend_data", "dividend_report", "dividend_yield",
                    "ex_dividend_date", "annual_dividend"
                ])
        return available_attributes  

def __dir__():
    return __all__
