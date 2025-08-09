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

__all__ = ['DirectionalMovementIndex']


        
# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire modules; actual imports occurs on first use.
# pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  
plt = Proxy("matplotlib.pyplot")  # Third-party library imports (from PyPI or other package sources)  
np = Proxy("numpy")  # Third-party library imports (from PyPI or other package sources)  


class DirectionalMovementIndex:
    def __init__(self, parent, period=14, adx_threshold=25):
        self.parent = parent
        self.df = self.parent.df
        self.period = period
        self.adx_threshold = adx_threshold

        self.parent.verify_period_sufficiency(self.period)
        self._calculate_indicators()
        self._calculate_signals()

    def _calculate_indicators(self):
        self.df['High-Low'] = self.df['High'] - self.df['Low']
        self.df['High-PrevClose'] = abs(self.df['High'] - self.df['Close'].shift(1))
        self.df['Low-PrevClose'] = abs(self.df['Low'] - self.df['Close'].shift(1))
        self.df['TR'] = self.df[['High-Low','High-PrevClose','Low-PrevClose']].max(axis=1)

        self.df['+DM'] = np.where(
            (self.df['High'] - self.df['High'].shift(1)) > (self.df['Low'].shift(1) - self.df['Low']),
            np.maximum(self.df['High'] - self.df['High'].shift(1), 0), 0
        )
        self.df['-DM'] = np.where(
            (self.df['Low'].shift(1) - self.df['Low']) > (self.df['High'] - self.df['High'].shift(1)),
            np.maximum(self.df['Low'].shift(1) - self.df['Low'], 0), 0
        )

        self.df['ATR'] = self.df['TR'].rolling(window=self.period).mean()
        self.df['+DM_smooth'] = self.df['+DM'].rolling(window=self.period).mean()
        self.df['-DM_smooth'] = self.df['-DM'].rolling(window=self.period).mean()

        self.df['+DI'] = 100 * (self.df['+DM_smooth'] / self.df['ATR'])
        self.df['-DI'] = 100 * (self.df['-DM_smooth'] / self.df['ATR'])
        self.df['DX'] = 100 * (abs(self.df['+DI'] - self.df['-DI']) / (self.df['+DI'] + self.df['-DI']))
        self.df['ADX'] = self.df['DX'].rolling(window=self.period).mean()

    def _calculate_signals(self):
        self.df['Buy_Signal'] = np.where(
            (self.df['+DI'] > self.df['-DI']) & (self.df['+DI'].shift(1) <= self.df['-DI'].shift(1)), 1, 0
        )
        self.df['Sell_Signal'] = np.where(
            (self.df['-DI'] > self.df['+DI']) & (self.df['-DI'].shift(1) <= self.df['+DI'].shift(1)), 1, 0
        )
        self.df['Strong_Buy'] = np.where(
            (self.df['Buy_Signal'] == 1) & (self.df['ADX'] >= self.adx_threshold), 1, 0
        )
        self.df['Strong_Sell'] = np.where(
            (self.df['Sell_Signal'] == 1) & (self.df['ADX'] >= self.adx_threshold), 1, 0
        )

    def get_signals(self):
        return self.df[['Date', '+DI', '-DI', 'ADX', 'Buy_Signal', 'Sell_Signal', 'Strong_Buy', 'Strong_Sell']]

    def get_trend_strength(self):
        import numpy as _np  # safe to import local; or reuse Proxy if you want
        conditions = [
            (self.df['ADX'] >= 25),
            (self.df['ADX'] < 25) & (self.df['ADX'] >= 20),
            (self.df['ADX'] < 20),
        ]
        choices = ['Strong Trend', 'Weak Trend', 'Trendless Market']
        self.df['Trend_Strength'] = _np.select(conditions, choices, default='Unknown')
        return self.df[['Date', 'ADX', 'Trend_Strength']]

    def plot_indicators(self):
        plt.figure(figsize=(14, 8))
        plt.plot(self.df['Date'], self.df['+DI'], label='+DI', color='green')
        plt.plot(self.df['Date'], self.df['-DI'], label='-DI', color='red')
        plt.plot(self.df['Date'], self.df['ADX'], label='ADX', color='blue')
        plt.fill_between(self.df['Date'], 0, self.df['ADX'], where=self.df['ADX'] >= 25, color='blue', alpha=0.1)
        plt.title('DMI and ADX Indicators'); plt.xlabel('Date'); plt.ylabel('Indicator Value')
        plt.legend(loc='upper right'); plt.grid(True); plt.show()

    def plot_trend_strength(self):
        trend_df = self.get_trend_strength()
        plt.figure(figsize=(14, 8))
        plt.plot(trend_df['Date'], trend_df['ADX'], label='ADX', color='blue')
        plt.fill_between(trend_df['Date'], 0, trend_df['ADX'],
                         where=trend_df['Trend_Strength'] == 'Strong Trend', color='blue', alpha=0.1, label='Strong Trend')
        plt.fill_between(trend_df['Date'], 0, trend_df['ADX'],
                         where=trend_df['Trend_Strength'] == 'Trendless Market', color='gray', alpha=0.1, label='Trendless Market')
        plt.title('ADX and Trend Strength'); plt.xlabel('Date'); plt.ylabel('ADX Value')
        plt.legend(loc='upper right'); plt.grid(True); plt.show()

def __dir__():
    return __all__
