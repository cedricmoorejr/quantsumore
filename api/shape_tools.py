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
from ..proxy import Proxy


__all__ = [
    'filter_dataframe_columns',
    'rename_dataframe_columns',
    'apply_conversion_to_columns',
    'is_valid_dataframe',
    'normalize_time',
]



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire module; actual import occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  


def filter_dataframe_columns(df, column_names):
    """
    Filters the DataFrame to include only the specified columns.

    Args:
    df (pd.DataFrame): The DataFrame from which to filter columns.
    column_names (list of str): A list of column names to include in the new DataFrame.

    Returns:
    pd.DataFrame: A new DataFrame containing only the specified columns that exist in the original DataFrame.
    """
    df_copy = deepcopy(df)    
    if isinstance(column_names, str):
        column_names = [column_names]
    filtered_columns = [col for col in column_names if col in df_copy.columns]
    return df_copy[filtered_columns]

def rename_dataframe_columns(df, rename_dict):
    """
    Renames the columns of the DataFrame based on a provided dictionary mapping.

    Args:
    df (pd.DataFrame): The DataFrame whose columns are to be renamed.
    rename_dict (dict): A dictionary mapping current column names to new names.

    Returns:
    pd.DataFrame: A DataFrame with renamed columns, where applicable.
    """
    df_copy = deepcopy(df)    
    valid_renames = {old_name: new_name for old_name, new_name in rename_dict.items() if old_name in df_copy.columns}
    return df_copy.rename(columns=valid_renames)

def apply_conversion_to_columns(df, columns, fun):
    """
    Applies a specified function to the specified columns of a DataFrame.

    Args:
    df (pd.DataFrame): The DataFrame to modify.
    columns (list of str): List of column names to apply the conversion on.
    fun (function): The function to apply to the specified columns.

    Returns:
    pd.DataFrame: The modified DataFrame with specified columns converted.
    """
    df_copy = deepcopy(df)    
    if isinstance(columns, str):
        columns = [columns]    
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = [fun(x) if isinstance(x, (str, int, float)) else x for x in df_copy[col]]            
    return df_copy

def is_valid_dataframe(df):
    """
    Checks if the input is a valid, non-empty DataFrame.

    Args:
    df (pd.DataFrame): The DataFrame to check.
    """
    if not isinstance(df, pd.DataFrame):
        return False
    if df.empty:
        return False
    return True

def normalize_time(df, column_names):
    """Normalize the time part of datetime in the specified column to 00:00:00."""
    df_copy = deepcopy(df)    
    if isinstance(column_names, str):
        column_names = [column_names]
    for column_name in column_names:
        df[column_name] = pd.to_datetime(df[column_name])
        df[column_name] = df[column_name].dt.normalize()
    return df

def __dir__():
    return __all__
