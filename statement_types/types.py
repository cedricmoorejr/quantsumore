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

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..proxy import Proxy

__all__ = [
    'FinancialStatement',
    'IncomeStatement',
    'BalanceSheet',
    'CashFlowStatement',
    'DividendSummary',
    'DividendHistory',
]


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire module; actual import occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  

# Notes:
# -----
# This module provides a suite of pandas DataFrame subclasses specifically designed
# to represent structured financial statement data. These classes offer a standardized
# way to encapsulate, manipulate, and identify different financial statement types
# (such as income statements, balance sheets, cash flow statements, and dividends)
# within analytic workflows or financial data pipelines.
# 
# These DataFrame subclasses serve as the **standard containers** for all tabular
# financial data within the Quantsumore stack. They are used by scraping agents,
# API layers, and analytic tools to ensure financial statement data is easily
# distinguishable and can be manipulated or validated according to its context.
# 
# The FinancialStatement subclasses do not enforce any column names, types, or
# indexing by default. They serve as semantic wrappers to make statement type
# explicit within codebases and data flows.
# 
# All subclasses inherit _constructor overrides to ensure pandas operations return the
# appropriate subclass instance.
class FinancialStatement(pd.DataFrame):
    @property
    def _constructor(self):
        return FinancialStatement
    @property
    def _constructor_sliced(self):
        return pd.Series

# ────────── Financial Statements ──────────────────────────────── 
class IncomeStatement(FinancialStatement):
    pass

class BalanceSheet(FinancialStatement):
    pass

class CashFlowStatement(FinancialStatement):
    pass

# ────────── Dividend Reports ──────────────────────────────── 
class DividendSummary(FinancialStatement):
    pass

class DividendHistory(FinancialStatement):
    pass


