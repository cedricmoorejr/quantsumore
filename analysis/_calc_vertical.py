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

from copy import deepcopy

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..strata_utils import IterDict


__all__ = ['Vertical_Analysis']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

class Vertical_Analysis:
    def __init__(self, analyze_instance):
        self.parent = analyze_instance

    def _VerticalAnalysis(self, financial_statement):
        import pandas as pd  # Third-party library imports (from PyPI or other package sources)    	
        
        valid_statements = {
            "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
            "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
            "Cash Flow Statement": ["Cash Flow Statement", "Cash_Flow_Statement", "C", "CF", "Cash Flow", "Cash_Flow", "Cash"],
        }
        financial_statement = IterDict.key_from_mapping(financial_statement, valid_statements, invert=False)
        
        if financial_statement == 'Income Statement':
            statement = deepcopy(self.parent.income_statement)
            if statement is not None and not statement.empty:                      
                statement.replace(['--', ''], pd.NA, inplace=True)
                statement = statement.apply(pd.to_numeric, errors='coerce')
                vertical_analysis = statement.div(statement.loc['Total Revenue'])
                vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.income_statement.isin(['--', '']), self.parent.income_statement)
                return vertical_analysis_formatted
            
        if financial_statement == 'Balance Sheet':
            statement = deepcopy(self.parent.balance_sheet)
            if statement is not None and not statement.empty:                
                statement.replace(['--', ''], pd.NA, inplace=True)
                statement = statement.apply(pd.to_numeric, errors='coerce')
                vertical_analysis = statement.div(statement.loc['Total Assets'])
                vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.balance_sheet.isin(['--', '']), self.parent.balance_sheet)
                return vertical_analysis_formatted
            
        if financial_statement == 'Cash Flow Statement':
            statement = deepcopy(self.parent.cash_flow_statement)
            if statement is not None and not statement.empty:                    
                statement.replace(['--', ''], pd.NA, inplace=True)
                statement = statement.apply(pd.to_numeric, errors='coerce')
                vertical_analysis = statement.div(statement.loc['Net Cash Flow-Operating'])
                vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.cash_flow_statement.isin(['--', '']), self.parent.cash_flow_statement)
                return vertical_analysis_formatted

def __dir__():
    return __all__
