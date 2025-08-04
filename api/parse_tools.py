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
from ..date_parser import dtparse


__all__ = [
    'convert_to_float',
    'convert_date',
    'convert_to_yield',  
]


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.
# Precompile regex patterns for efficiency

def convert_to_float(value, roundn=0):
    """
    Converts a given string value to a float after removing any dollar signs and commas,
    except when the string contains a percentage sign or a slash, in which case the original
    string is returned unchanged.

    Args:
    value (str): The string value to convert.
    roundn (int): The number of decimal places to round the float to; if 0, rounding is skipped.

    Returns:
    float or str: Returns the float conversion if applicable, rounded as specified, 
                  or the original value if it contains '%' or '/'.
    """
    try:
        str_value = str(value)
        cleaned_value = re.sub(r'[\$,]', '', str_value)
        
        if '%' in cleaned_value or '/' in cleaned_value:
            return value
        
        float_value = float(cleaned_value)
        return round(float_value, roundn) if roundn else float_value
    except (ValueError, TypeError):
        return value

def convert_date(date, from_format=None, to_format='%Y-%m-%d %H:%M:%S', to_unix_timestamp=False):
    try:
        dt = dtparse.parse(date_input=str(date), from_format=from_format, to_format=to_format, to_unix_timestamp=to_unix_timestamp)
        return dt
    except:
        return date
       
def convert_to_yield(dyield):
    if dyield is None:
        return None
    if isinstance(dyield, str) and dyield.endswith('%'):
        dyield = dyield.replace('%', '')
        if dyield.replace('.', '', 1).isdigit():
            dyield = float(dyield) / 100
        else:
            return None 
    elif isinstance(dyield, str):
        if dyield.replace('.', '', 1).isdigit():
            dyield = float(dyield)
        else:
            return None
    if isinstance(dyield, (float, int)):
        return round(dyield, 4)
    return None       
       
def __dir__():
    return __all__


