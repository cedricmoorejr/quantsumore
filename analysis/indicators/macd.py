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

__all__ = ['MACD']


  
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


class MACD:
    def __init__(self, parent, short_window=12, long_window=26, signal_window=9):
        self.parent = parent
        self.df = self.parent.df
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        
        # Calculate indicators and signals            
        self._calculate_macd()
        self._detect_crossovers()

    def _calculate_macd(self):
        """Calculate the MACD, Signal line, and MACD Histogram."""
        # Calculate the Short-term EMA (12 periods by default)
        self.df['EMA_12'] = self.df['Close'].ewm(span=self.short_window, adjust=False).mean()

        # Calculate the Long-term EMA (26 periods by default)
        self.df['EMA_26'] = self.df['Close'].ewm(span=self.long_window, adjust=False).mean()

        # Calculate the MACD Line
        self.df['MACD_Line'] = self.df['EMA_12'] - self.df['EMA_26']

        # Calculate the Signal Line (9 periods by default)
        self.df['Signal_Line'] = self.df['MACD_Line'].ewm(span=self.signal_window, adjust=False).mean()

        # Calculate the MACD Histogram
        self.df['MACD_Histogram'] = self.df['MACD_Line'] - self.df['Signal_Line']

    def _detect_crossovers(self):
        """Detect crossovers between the MACD line and the Signal line, and the significance of the zero line."""
        self.df['MACD_Signal'] = 'None'

        # Detect when MACD crosses above the Signal line (Bullish Signal)
        self.df['MACD_Signal'] = np.where(
            (self.df['MACD_Line'] > self.df['Signal_Line']) & (self.df['MACD_Line'].shift(1) <= self.df['Signal_Line'].shift(1)),
            'Bullish Crossover',
            self.df['MACD_Signal']
        )

        # Detect when MACD crosses below the Signal line (Bearish Signal)
        self.df['MACD_Signal'] = np.where(
            (self.df['MACD_Line'] < self.df['Signal_Line']) & (self.df['MACD_Line'].shift(1) >= self.df['Signal_Line'].shift(1)),
            'Bearish Crossover',
            self.df['MACD_Signal']
        )

        # Highlight signals depending on the MACD line's position relative to the zero line
        self.df['MACD_Signal'] = np.where(
            (self.df['MACD_Signal'] == 'Bullish Crossover') & (self.df['MACD_Line'] > 0),
            'Bullish Crossover (Above Zero)',
            self.df['MACD_Signal']
        )

        self.df['MACD_Signal'] = np.where(
            (self.df['MACD_Signal'] == 'Bearish Crossover') & (self.df['MACD_Line'] < 0),
            'Bearish Crossover (Below Zero)',
            self.df['MACD_Signal']
        )

    def get_macd(self):
        """Return the DataFrame with the MACD, Signal line, Histogram, and Crossover signals."""
        return self.df[['Date', 'Close', 'MACD_Line', 'Signal_Line', 'MACD_Histogram', 'MACD_Signal']]

    def plot_macd(self):
        """Plot the MACD, Signal line, and Histogram, highlighting crossover signals."""
        plt.figure(figsize=(14, 8))

        # Plot MACD Line and Signal Line
        plt.plot(self.df['Date'], self.df['MACD_Line'], label='MACD Line', color='blue')
        plt.plot(self.df['Date'], self.df['Signal_Line'], label='Signal Line', color='red')

        # Plot MACD Histogram
        plt.bar(self.df['Date'], self.df['MACD_Histogram'], label='MACD Histogram', color='gray', alpha=0.5)

        # Highlight crossover points
        crossover_dates = self.df[self.df['MACD_Signal'] != 'None']['Date']
        for signal in ['Bullish Crossover (Above Zero)', 'Bearish Crossover (Below Zero)']:
            plt.scatter(self.df[self.df['MACD_Signal'] == signal]['Date'], 
                        self.df[self.df['MACD_Signal'] == signal]['MACD_Line'],
                        label=signal, s=50, alpha=0.7)

        plt.axhline(0, color='black', linestyle='--', label='Zero Line')

        plt.title('MACD (Moving Average Convergence Divergence) with Crossovers')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()

def __dir__():
    return __all__
