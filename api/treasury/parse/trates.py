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
from ...date_parser import dtparse
from ...proxy import Proxy
from ...exceptions import (
    # TreasuryPipelineError,
    TreasuryDataValidationError,
    TreasuryNoDataError,
    TreasuryDataUnavailableError,
)


__all__ = ['scan']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire module; actual import occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  


class scan:

    # -------- Helpers ------
    @staticmethod
    def _format_date(date_str):
        try:
            return dtparse.parse(date_str)
        except Exception:
            return pd.NaT

    @staticmethod
    def _format_rates(rates: dict) -> dict:
        out = {}
        for k, v in rates.items():
            if v is None:
                out[k] = None
            elif 0 <= v <= 1:
                out[k] = round(v, 4)
            else:                       # convert % → decimal
                out[k] = round(v / 100, 4)
        return out

    # -------- Construct ---------
    def __init__(self, df: pd.DataFrame, kind: str, *, full: bool = False):
        self.kind = kind.lower()
        if self.kind not in {"tbill", "tyield"}:
            raise TreasuryDataValidationError("kind must be 'tbill' or 'tyield'")
        self.full_requested = full

        self.df = self._clean_and_prepare(df)
        if self.df.empty:
            # self.result = None 
            raise TreasuryNoDataError("Input DataFrame is empty or invalid for treasury scan.")
        elif self.full_requested:
            self.result = (self._full_tbill_table(self.df) if self.kind == "tbill"
                            else self._full_yield_table(self.df))
        else:
            latest = (self._extract_latest_tbills(self.df) if self.kind == "tbill"
                      else self._extract_latest_yield(self.df))
            self.result = self._format_rates(latest)

    def _clean_and_prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = df.columns.str.title()
        if "Date" in df.columns:
            df["Date"] = df["Date"].apply(self._format_date)
            df = df.sort_values("Date")
        return df.reset_index(drop=True)

    # ---- T-Bill helpers --------
    _tbill_column_map = {
        "1-Month T-Bill":  "4 Weeks Coupon Equivalent",
        "2-Month T-Bill":  "8 Weeks Coupon Equivalent",
        "3-Month T-Bill":  "13 Weeks Coupon Equivalent",
        "4-Month T-Bill":  "17 Weeks Coupon Equivalent",
        "6-Month T-Bill":  "26 Weeks Coupon Equivalent",
        "12-Month T-Bill": "52 Weeks Coupon Equivalent",
    }

    def _extract_latest_tbills(self, df):
        last = df.loc[df["Date"] == df["Date"].max()]
        out = {}
        for display, col in self._tbill_column_map.items():
            try:
                out[display] = float(last.iloc[0][col])
            except Exception:
                out[display] = None
        return out

    # def extract_latest_tbills(self, df):
    #     last_row = df.loc[df['Date'] == df['Date'].max()]
    # 
    #     rates = {}
    #     for label, col in self._tbill_column_map.items():
    #         if col in last_row.columns:
    #             value = last_row.iloc[0][col]
    #             try:
    #                 rates[label] = float(value)
    #             except Exception:
    #                 rates[label] = None
    #         else:
    #             rates[label] = None
    #     return rates
       
    def _full_tbill_table(self, df):
        keep = ["Date"] + [v for v in self._tbill_column_map.values() if v in df.columns]
        table = df[keep].rename(columns={v: k for k, v in self._tbill_column_map.items()})
        return table

    # ---- Yield-Curve helpers ------
    _yield_column_map = {
        "1 Mo":  "1-Month Treasury Bill (T-Bill)",
        "2 Mo":  "2-Month Treasury Bill (T-Bill)",
        "3 Mo":  "3-Month Treasury Bill (T-Bill)",
        "4 Mo":  "4-Month Treasury Bill (T-Bill)",
        "6 Mo":  "6-Month Treasury Bill (T-Bill)",
        "1 Yr":  "1-Year Treasury Note",
        "2 Yr":  "2-Year Treasury Note",
        "3 Yr":  "3-Year Treasury Note",
        "5 Yr":  "5-Year Treasury Note",
        "7 Yr":  "7-Year Treasury Note",
        "10 Yr": "10-Year Treasury Note",
        "20 Yr": "20-Year Treasury Bond",
        "30 Yr": "30-Year Treasury Bond",
    }

    # def _extract_latest_yield(self, df):
    #     last = df.loc[df["Date"] == df["Date"].max()]
    #     out = {}
    #     for col, display in self._yield_column_map.items():
    #         try:
    #             out[display] = float(last.iloc[0][col])
    #         except Exception:
    #             out[display] = None
    #     return out

    def _extract_latest_yield(self, df):
        last_row = df.loc[df['Date'] == df['Date'].max()]
        rates = {}
        for col, display in self._yield_column_map.items():
            if col in last_row.columns:
                value = last_row.iloc[0][col]
                try:
                    rates[display] = float(value)
                except Exception:
                    rates[display] = None
            else:
                rates[display] = None
        return rates

    def _full_yield_table(self, df):
        keep = ["Date"] + [c for c in self._yield_column_map if c in df.columns]
        table = df[keep].rename(columns=self._yield_column_map)
        return table

    # -------- API ---------
    # def DATA(self):
    #     """Return either a dict of latest rates (default) or the full DataFrame."""
    #     return self.result
    
    def DATA(self):
        """
        Return either a dict of latest rates (default) or the full DataFrame.
        Raises:
            TreasuryDataUnavailableError: If .result is None or empty.
        """
        if self.result is None or (isinstance(self.result, dict) and not any(self.result.values())):
            raise TreasuryDataUnavailableError()
        return self.result

def __dir__():
    return __all__






# def full_yield_curve_table(df):
#     df = df.copy()
#     yield_cols = [
#         ('1 Mo', '1-Month Treasury Bill (T-Bill)'),
#         ('2 Mo', '2-Month Treasury Bill (T-Bill)'),
#         ('3 Mo', '3-Month Treasury Bill (T-Bill)'),
#         ('4 Mo', '4-Month Treasury Bill (T-Bill)'),
#         ('6 Mo', '6-Month Treasury Bill (T-Bill)'),
#         ('1 Yr', '1-Year Treasury Note'),
#         ('2 Yr', '2-Year Treasury Note'),
#         ('3 Yr', '3-Year Treasury Note'),
#         ('5 Yr', '5-Year Treasury Note'),
#         ('7 Yr', '7-Year Treasury Note'),
#         ('10 Yr', '10-Year Treasury Note'),
#         ('20 Yr', '20-Year Treasury Bond'),
#         ('30 Yr', '30-Year Treasury Bond')
#     ]
#     cols = ['Date'] + [col for col, _ in yield_cols if col in df.columns]
#     table = df[cols]
#     rename_map = {old: new for old, new in yield_cols if old in df.columns}
#     table = table.rename(columns=rename_map)
#     return table
# 
# 
# 
# def full_tbill_table(df):
#     df = df.copy()
#     coupon_cols = [
#         ('4 Weeks Coupon Equivalent', '1-Month T-Bill'),
#         ('8 Weeks Coupon Equivalent', '2-Month T-Bill'),
#         ('13 Weeks Coupon Equivalent', '3-Month T-Bill'),
#         ('17 Weeks Coupon Equivalent', '4-Month T-Bill'),
#         ('26 Weeks Coupon Equivalent', '6-Month T-Bill'),
#         ('52 Weeks Coupon Equivalent', '12-Month T-Bill'),
#     ]
#     cols = ['Date'] + [col for col, _ in coupon_cols if col in df.columns]
#     table = df[cols]
#     rename_map = {old: new for old, new in coupon_cols if old in df.columns}
#     table = table.rename(columns=rename_map)
#     return table

