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
technical: Unified Engine for Technical Indicator Computation & Signal Analysis
════════════════════════════════════════════════════════════════════════════════

Module Purpose
────────────────────────────────────────────────────
`technical` provides a single, robust interface for calculating, visualizing,
and analyzing a full suite of technical indicators on historical financial data.
Its flagship class, `tAnalyze`, is designed for analysts, quant developers,
and automated trading systems that need reliable, extensible computation of
trend, momentum, volatility, and volume-based signals for equities, crypto, or FX.

Unlike “black box” wrappers, this module emphasizes **data validation,
transparency, and extendibility**, with DataFrame-in/DataFrame-out idioms and
plot-ready methods for every signal.

Key Features
────────────────────────────────────────────────────
- **Unified API**: All indicator logic, signal detection, and plotting tools are accessed via the `tAnalyze` object.
- **Schema-agnostic preprocessing**: Accepts nearly any time series format (crypto or equity), with automatic column normalization and type enforcement.
- **Production-grade validation**: All methods raise descriptive exceptions for missing columns, bad data, or insufficient history.
- **Rich indicator set**: Supports industry-standard signals (DMI/ADX, Aroon, OBV, MACD, RSI, Stochastic, MA/EMA/Bollinger Bands, ATR) with “get” and “plot” accessors for all.
- **Signal detection**: Buy/sell/neutral/crossover and divergence signals are included for most indicators, enabling strategy backtesting or visual scanning.
- **Self-contained plotting**: Every major indicator provides matplotlib visualizations with annotated signals and trend zones.

Supported Indicators & Methods
────────────────────────────────────────────────────
• `DirectionalMovementIndex(period=14, adx_threshold=25)`  
  Computes +DI, -DI, ADX, and trend signals (buy/sell, strong trend).
• `AroonIndicator(period=25)`  
  Calculates Aroon Up/Down and detects uptrend/downtrend/range signals.
• `OnBalanceVolume()`  
  OBV calculation, with price/OBV divergence detection and visualization.
• `AccumulationDistributionLine()`  
  Computes A/D Line, detects price-volume divergences, plots overlay.
• `MACD(short_window=12, long_window=26, signal_window=9)`  
  Full MACD, Signal, Histogram, and crossover/zero-line analysis.
• `RelativeStrengthIndex(period=14)`  
  RSI values, overbought/oversold detection, divergence, support/resistance mapping.
• `FastStochasticOscillator(k_period=14, d_period=3)`  
  %K/%D calculation, overbought/oversold, crosses, divergence.
• `MovingAveragesAndBollingerBands(sma_period=20, ema_period=20, bb_period=20, bb_std=2)`  
  SMA, EMA, Bollinger Bands, and all crossover signals.
• `AverageTrueRange(atr_period=14)`  
  ATR/volatility analysis, regime shifts, and volatility plotting.

System Architecture & Workflow
────────────────────────────────────────────────────
1. **Data Preparation**
   - Incoming data is normalized and validated by `tAnalyze.Dataframe`.
   - Supports flexible naming for 'Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', using regex-based matching.
   - Dates are standardized and filtered to a single asset per object.

2. **Indicator Computation**
   - Each technical indicator is encapsulated in a dedicated sub-class, providing its own computation, signal detection, and plotting logic.
   - Methods return enriched DataFrames (all columns preserved, new columns for signals).

3. **Signal & Divergence Analysis**
   - All indicators produce not only the “raw” values, but also columns for buy/sell/cross/divergence signals, aiding both manual and programmatic use.

4. **Visualization**
   - All core methods include matplotlib-powered plotting routines, with labeled signals, highlighted regions, and dual-axis overlays where appropriate.
   - Plots are consistent, visually annotated, and ready for Jupyter, scripts, or web integration.

5. **Error Handling & Robustness**
   - All methods verify period sufficiency and input schema.
   - Missing or insufficient data triggers clear, instructive error messages.

Example Usage
────────────────────────────────────────────────────
from quantsumore.api import tAnalysis

# Load raw price data (works with equities or crypto)
df = pd.DataFrame({
    'Date': pd.date_range('2020-01-01', periods=100),
    'High': np.random.rand(100)*100+150,
    'Low': np.random.rand(100)*100+100,
    'Open': np.random.rand(100)*100+125,
    'Close': np.random.rand(100)*100+130,
    'Volume': np.random.randint(100, 1000, 100),
    'Symbol': ['AAPL']*100
})
analyze = tAnalysis(df)

# Compute indicators and get DataFrames or plots
dmi = analyze.DirectionalMovementIndex(period=14, adx_threshold=25)
dmi.get_signals()
dmi.plot_indicators()

macd = analyze.MACD()
macd.plot_macd()

rsi = analyze.RelativeStrengthIndex()
rsi.plot_rsi()

Design Features
────────────────────────────────────────────────────
• Extensible by design: Add new indicators or signal logic by subclassing and plugging into the tAnalyze framework.
• Pure DataFrame logic: All calculations are pandas-native; intermediate and final values always accessible.
• No external dependencies except pandas, numpy, matplotlib.
• Error transparency: All user-facing errors are descriptive and suggest correctable input problems.

• Integration & Usage Notes
────────────────────────────────────────────────────
• Best used as a backend analysis layer for dashboards, scripts, or batch processing pipelines.
• Visualization is matplotlib-based; for production UIs, access .get_*() methods and plot elsewhere as needed.
• To analyze multiple tickers, instantiate one tAnalyze per symbol.
• To avoid column name conflicts, only pass data for a single asset per instance.

Warnings & Best Practices
────────────────────────────────────────────────────
• Ensure at least max(period) unique dates for the desired indicator before calling methods.
• Data must include 'Open', 'High', 'Low', 'Close', 'Volume', and 'Date'; column names are flexible but must match the schema after normalization.
• Always inspect returned DataFrames before using buy/sell signals in live trading logic.
• Indicators are intended for research and educational purposes; verify any trading strategy with robust backtesting.

Available Classes
────────────────────────────────────────────────────
• tAnalyze — Unified interface for technical analysis
• All indicator-specific classes are accessed through tAnalyze methods
"""
import re
from copy import deepcopy

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..date_parser import dtparse
from ..proxy import Proxy
from ..exceptions import DataInitializationError
from .indicators import (
    DirectionalMovementIndex as _DirectionalMovementIndex,
    AroonIndicator as _AroonIndicator,
    OnBalanceVolume as _OnBalanceVolume,
    AccumulationDistributionLine as _AccumulationDistributionLine,
    MACD as _MACD,
    RelativeStrengthIndex as _RelativeStrengthIndex,
    FastStochasticOscillator as _FastStochasticOscillator,
    MovingAveragesAndBollingerBands as _MovingAveragesAndBollingerBands,
    AverageTrueRange as _AverageTrueRange,
)

__all__ = ['tAnalyze']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# Lazily load the entire modules; actual imports occurs on first use.
pd = Proxy("pandas", None)  # Third-party library imports (from PyPI or other package sources)  
plt = Proxy("matplotlib.pyplot")  # Third-party library imports (from PyPI or other package sources)  
np = Proxy("numpy")  # Third-party library imports (from PyPI or other package sources)  


class tAnalyze:
    """
    Central interface for preprocessing historical price data and computing technical indicators,
    providing a unified, object-oriented API for trend, momentum, volume, and volatility analysis.

    Purpose:
    --------
        The `tAnalyze` class orchestrates the end-to-end workflow for technical analysis.
        It standardizes raw price data (cryptocurrency or equity), validates structure, and
        exposes a suite of methods for generating industry-standard technical indicators.

    Workflows:
    ----------
        - Data preprocessing: Load and standardize OHLCV data for a single symbol, with automatic
          column mapping and type conversion.
        - Indicator calculation: Compute trend, momentum, volume, and volatility metrics using
          specialized indicator classes.
        - Symbol consistency: Ensure all operations are performed on a single, validated symbol.

    Attributes:
    -----------
        dataframe : Dataframe
            Helper object responsible for preprocessing, validating, and structuring the input data.
        df : pandas.DataFrame
            Standardized OHLCV data for the selected symbol, with consistent column names and data types.
        ticker : str
            The ticker symbol or asset identifier for the loaded data.

    Methods:
    --------
        DirectionalMovementIndex(period=14, adx_threshold=25)
            Compute the DMI and ADX indicators to measure directional strength and trend quality.

        AroonIndicator(period=25)
            Compute the Aroon Up and Aroon Down indicators to identify emerging trends.

        OnBalanceVolume()
            Compute the OBV indicator to analyze price-volume relationships.

        AccumulationDistributionLine()
            Compute the A/D Line to assess the cumulative flow of volume.

        MACD(short_window=12, long_window=26, signal_window=9)
            Compute MACD, Signal line, and MACD Histogram for momentum analysis.

        RelativeStrengthIndex(period=14)
            Compute the RSI to identify overbought and oversold conditions.

        FastStochasticOscillator(k_period=14, d_period=3)
            Compute %K and %D lines for stochastic momentum evaluation.

        MovingAveragesAndBollingerBands(sma_period=20, ema_period=20, bb_period=20, bb_std=2)
            Compute SMA, EMA, and Bollinger Bands for trend and volatility analysis.

        AverageTrueRange(atr_period=14)
            Compute the ATR to measure market volatility.

    Notes:
    ------
        - Automatically detects and renames columns for standard OHLCV format if column_map is not provided.
        - Supports generating 'Symbol' column from a provided `ticker` when missing from data.
        - Ensures that only one unique symbol is present in the dataset for consistent analysis.
        - Date values are normalized to 'YYYY-MM-DD' format.
        - Raises detailed errors for missing columns, type conversion failures, or insufficient data length.

    Example:
    --------
        >>> data = pd.DataFrame({
        ...     'Date': pd.date_range(start='2020-01-01', periods=100),
        ...     'High': np.random.rand(100) * 100 + 150,
        ...     'Low': np.random.rand(100) * 100 + 100,
        ...     'Open': np.random.rand(100) * 100 + 125,
        ...     'Close': np.random.rand(100) * 100 + 130,
        ...     'Volume': np.random.randint(100, 1000, size=100),
        ...     'Symbol': ['AAPL'] * 100
        ... })
        >>> analyze = tAnalyze(data)
        >>> dmi = analyze.DirectionalMovementIndex(period=14, adx_threshold=25)
        >>> aroon = analyze.AroonIndicator(period=25)
        >>> obv = analyze.OnBalanceVolume()
        >>> adl = analyze.AccumulationDistributionLine()
        >>> macd = analyze.MACD()
        >>> rsi = analyze.RelativeStrengthIndex()
        >>> fast_stochastic = analyze.FastStochasticOscillator()
        >>> moving_avg_bb = analyze.MovingAveragesAndBollingerBands()
        >>> atr = analyze.AverageTrueRange()
    """
    def __init__(self, df, column_map=None, ticker=None, require_all=True):
        """
        Initialize a `tAnalyze` instance with validated and standardized historical price data.

        Parameters:
        -----------
            df : pandas.DataFrame
                Source OHLCV data containing columns for symbol, date, open, high, low, close, and volume.
                Column names can be in any format; mapping and auto-detection will be applied.

            column_map : dict or None, optional
                Explicit mapping from the DataFrame’s existing column names to the required
                standard names: {'Symbol','Date','Open','High','Low','Close','Volume'}.
                Example: {'date_time':'Date', 'open_price':'Open', ...}.
                Can be partial; any unmapped columns will be auto-detected.
                Default is None.

            ticker : str or None, optional
                Symbol to assign if the input DataFrame has no 'Symbol' column.
                Used to synthesize the column when missing. Default is None.

            require_all : bool, optional
                If True (default), all required columns must be present after mapping.
                If False, only critical columns are required, and 'Symbol' may be generated from `ticker`.

        Initializes:
        -----------
            dataframe : Dataframe
                Preprocessing helper instance containing validated and standardized OHLCV data.
            df : pandas.DataFrame
                The standardized OHLCV DataFrame ready for technical analysis.
            ticker : str
                The symbol for the loaded dataset, taken from the first row of 'Symbol'.

        Raises:
        -------
            DataInitializationError
                If preprocessing fails due to missing columns, invalid types, or empty data.

        Notes:
        ------
            - Automatically detects standard column names if not fully specified in `column_map`.
            - Ensures only a single symbol is present in the dataset.
            - Dates are normalized to 'YYYY-MM-DD' format before analysis.
            - Prints a success message with the loaded symbol if initialization completes successfully.
        """    	
        self.dataframe = None
        self.df = None
        self.ticker = None
        try:
            self.dataframe = self.Dataframe(df, column_map=column_map, ticker=ticker, require_all=require_all)
            self.df = self.dataframe.df
            self.ticker = self.df['Symbol'].iloc[0]
            print(f"Historical prices successfully loaded for {self.ticker}.")
        except Exception as e:
            raise DataInitializationError(
                f"Historical prices could not be loaded for {self.ticker or 'ticker symbol'}. Error: {e}"
            )

    def __dir__(self):
        return [
            "DirectionalMovementIndex", "AroonIndicator", "OnBalanceVolume",
            "AccumulationDistributionLine", "MACD", "RelativeStrengthIndex",
            "FastStochasticOscillator", "MovingAveragesAndBollingerBands", "AverageTrueRange",
            "ticker", "df",
        ]

    class Dataframe:
        """
        A class to preprocess and validate data for technical analysis. This class is 
        designed to handle and standardize data for both cryptocurrency and equity datasets.
        """	
        def __init__(self, df: pd.DataFrame, column_map=None, ticker=None, require_all=True):
            if df.empty:
                raise ValueError("DataFrame is empty")
            self.df = deepcopy(df)
            self._user_map = column_map or {}
            self._ticker = ticker
            self._require_all = require_all

            self.rename_cols()
            self._maybe_add_symbol_from_ticker()
            self.convert_to_floats()
            self.filter_to_single_symbol()
            self.normalize_date()

            has_columns, missing = self.check_columns()
            if not has_columns:
                raise ValueError(f"Missing required columns: {missing}")

        def rename_cols(self):
            original_cols = list(self.df.columns)
            final_map = {}
            allowed_targets = {'Symbol','Date','High','Low','Open','Close','Volume'}
            bad_targets = [t for t in self._user_map.values() if t not in allowed_targets]
            if bad_targets:
                raise ValueError(f"Invalid target names in column_map: {bad_targets}. Allowed: {sorted(allowed_targets)}")
            missing_sources = [s for s in self._user_map if s not in original_cols]
            if missing_sources:
                raise ValueError(f"column_map refers to columns not in DataFrame: {missing_sources}")
            final_map.update(self._user_map)
            if 'Date' not in final_map.values() and 'Timestamp' in self.df.columns:
                final_map['Timestamp'] = 'Date'

            # Auto-detect the rest
            def find_best_matches(df):
                keyword_map = {
                    'Symbol': ['ticker', 'symbol'],
                    'Date':   ['date'],
                    'High':   ['high','h'],
                    'Low':    ['low','l'],
                    'Open':   ['open','o'],
                    'Close':  ['close','c','adjclose','adj_close','adjustedclose'],
                    'Volume': ['volume','vol','qty','quantity']
                }
                column_renames = {}
                for standard_name, keywords in keyword_map.items():
                    if standard_name in final_map.values():
                        continue
                    for keyword in keywords:
                        pattern = re.compile(r'^' + keyword + r'|' + keyword, re.IGNORECASE)
                        best = sorted([c for c in df.columns if pattern.search(c)],
                                      key=lambda x: not x.lower().startswith(keyword))
                        if best:
                            src = best[0]
                            if src not in final_map:
                                column_renames[src] = standard_name
                                break
                return column_renames

            auto_map = find_best_matches(self.df)
            for src, tgt in auto_map.items():
                if tgt not in self._user_map.values() and src not in final_map:
                    final_map[src] = tgt

            if not final_map:
                raise ValueError("Failed to match critical columns based on user mapping and keywords.")

            self.df = self.df.rename(columns=final_map, inplace=False)

            required = ['Symbol','Date','Open','High','Low','Close','Volume']
            present_required = [c for c in required if c in self.df.columns]
            if self._require_all:
                self.df = self.df[present_required]

        def _maybe_add_symbol_from_ticker(self):
            required = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if 'Symbol' not in self.df.columns:
                if self._ticker:
                    self.df['Symbol'] = str(self._ticker)
                elif self._require_all:
                    raise ValueError("Symbol column is missing and no `ticker` was provided to synthesize it.")
            if all(col in self.df.columns for col in required):
                self.df = self.df[required + [c for c in self.df.columns if c not in required]]

        def convert_to_floats(self):
            float_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_floats = [col for col in float_columns if col not in self.df.columns]
            if missing_floats:
                raise ValueError(f"Missing float columns: {missing_floats}")
            for col in float_columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                if self.df[col].isna().any():
                    raise ValueError(f"Conversion to float failed for column: {col}")

        def normalize_date(self):
            if 'Date' not in self.df.columns:
                raise ValueError("Date column is missing")
            try:
                self.df['Date'] = self.df['Date'].apply(lambda x: dtparse.parse(x, to_format='%Y-%m-%d'))
            except Exception as e:
                raise ValueError(f"Date conversion failed: {str(e)}")

        def check_columns(self):
            required_cols = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_cols if col not in self.df.columns]
            return (not missing_columns, missing_columns)

        def filter_to_single_symbol(self):
            if 'Symbol' not in self.df.columns:
                raise ValueError("Symbol column is missing for filtering")
            first_symbol = self.df['Symbol'].iloc[0]
            self.df = self.df[self.df['Symbol'] == first_symbol]

    def verify_period_sufficiency(self, period):
        unique_dates = self.df['Date'].nunique()
        if unique_dates < period:
            raise ValueError(f"Insufficient data: The DataFrame contains only {unique_dates} unique dates, but at least {period} unique dates are required.")
      
    # ────────── Call Indicators ──── 
    def DirectionalMovementIndex(self, period=14, adx_threshold=25):
        """
        Calculate and analyze the Directional Movement Index (DMI) and Average Directional Index (ADX)
        for financial time series data.

        The Directional Movement Index is a technical analysis indicator used to measure the strength and direction
        of a market trend. It includes two main components, +DI (positive directional indicator) and -DI (negative
        directional indicator), which are used to identify bullish or bearish trends. The ADX (Average Directional
        Index) measures the strength of the trend. This class also provides methods to generate buy/sell signals
        based on the indicators and the strength of the trend using ADX.

        Parameters:
        -----------
        period : int
            The period for calculating the DMI and ADX, default is 14.
        adx_threshold : float
            The ADX threshold to classify trend strength, default is 25.

        Methods:
        --------        
        _calculate_indicators():
            Computes the True Range (TR), +DM, -DM, ATR, +DI, -DI, DX, and ADX indicators.
        _calculate_signals():
            Generates buy/sell signals and identifies strong trends based on +DI, -DI, and ADX values.
        get_signals():
            Returns a DataFrame with calculated indicators and generated buy/sell signals.
        get_trend_strength():
            Classifies the trend strength based on ADX values and returns a DataFrame with the trend classification.
        plot_indicators():
            Plots the +DI, -DI, and ADX indicators to visualize trend signals and market strength.
        plot_trend_strength():
            Plots the ADX values along with trend strength classifications, highlighting areas of strong trends.
        """        
        # return self._DirectionalMovementIndex(self, period, adx_threshold)
        return _DirectionalMovementIndex(self, period, adx_threshold)        
       
    def AroonIndicator(self, period=25):
        """
        Calculate and analyze the Aroon Indicator for a given dataset.

        The AroonIndicator class computes the Aroon Up and Aroon Down indicators for a financial dataset,
        detects trend signals and consolidations based on these indicators, and provides visualization methods
        to aid in technical analysis. It operates on a DataFrame containing financial data and supports both 
        cryptocurrency and equity datasets.

        Parameters:
        -----------
            period (int, optional): The period over which to calculate the Aroon indicators. Default is 25 days.

        Methods:
        --------
            _calculate_aroon():
                Calculates the Aroon Up and Aroon Down indicators and stores them in the DataFrame.

            _detect_trends():
                Detects trends and consolidations based on Aroon Up and Aroon Down interactions.

            get_aroon():
                Returns the DataFrame with the Aroon Up, Aroon Down, and Trend Signal columns.

            plot_aroon():
                Plots the Aroon Up and Aroon Down indicators, highlighting areas of detected trend signals.
        """	        
        return _AroonIndicator(self, period)
       
    def OnBalanceVolume(self):
        """
        Calculate and analyze On-Balance Volume (OBV) for a given dataset.

        The OnBalanceVolume class computes the On-Balance Volume (OBV) for a financial dataset,
        detects divergences between OBV and price, and provides visualization methods to aid in
        technical analysis. It operates on a DataFrame containing financial data and supports
        both cryptocurrency and equity datasets.

        Parameters:
        -----------
            df (pandas.DataFrame): DataFrame containing financial data with 'Date', 'Close', and 'Volume' columns.
        
        Methods:
        --------
            _calculate_obv():
                Calculates the On-Balance Volume (OBV) and stores it in the DataFrame.

            get_obv():
                Returns the DataFrame with the OBV column included.

            detect_divergence():
                Detects divergence between OBV and price and returns a DataFrame with detected divergence points.
            
            plot_obv_with_divergence():
                Plots the OBV and closing price, highlighting points where divergence between OBV and price occurs.
        """        
        return _OnBalanceVolume(self)

    def AccumulationDistributionLine(self):
        """
        Calculate and analyze the Accumulation/Distribution (A/D) Line for a given dataset.

        The AccumulationDistributionLine class computes the Accumulation/Distribution (A/D) Line for a financial dataset,
        detects divergences between the A/D Line and the price, and provides visualization methods to aid in
        technical analysis. It operates on a DataFrame containing financial data and supports both cryptocurrency and equity datasets.

        Parameters:
        -----------
            df (pandas.DataFrame): DataFrame containing financial data with 'Date', 'Close', 'High', 'Low', and 'Volume' columns.

        Methods:
        --------
            _calculate_ad_line():
                Calculates the Accumulation/Distribution (A/D) Line and stores it in the DataFrame.

            get_ad_line():
                Returns the DataFrame with the A/D Line column included.

            detect_divergence():
                Detects divergence between the A/D Line and price and returns a DataFrame with detected divergence points.
            
            plot_ad_line_with_divergence():
                Plots the A/D Line and closing price, highlighting points where divergence between the A/D Line and price occurs.
        """        
        return _AccumulationDistributionLine(self)

    def MACD(self, short_window=12, long_window=26, signal_window=9):
        """
        Calculate and analyze the Moving Average Convergence Divergence (MACD) for a given dataset.

        The MACD class computes the MACD line, Signal line, and MACD Histogram for a financial dataset,
        detects crossovers between the MACD line and Signal line, and provides visualization methods
        to aid in technical analysis. It operates on a DataFrame containing financial data and supports
        both cryptocurrency and equity datasets.

        Parameters:
        -----------
            short_window (int): The period for the short-term EMA, default is 12 days.
            long_window (int): The period for the long-term EMA, default is 26 days.
            signal_window (int): The period for the Signal line EMA, default is 9 days.

        Methods:
        --------
            _calculate_macd():
                Calculates the MACD line, Signal line, and MACD Histogram and stores them in the DataFrame.

            _detect_crossovers():
                Detects crossovers between the MACD line and the Signal line, as well as the MACD line's position
                relative to the zero line to identify bullish and bearish signals.

            get_macd():
                Returns the DataFrame with the MACD line, Signal line, Histogram, and crossover signals.

            plot_macd():
                Plots the MACD line, Signal line, and MACD Histogram, highlighting crossover signals.
        """        
        return _MACD(self, short_window, long_window, signal_window)

    def RelativeStrengthIndex(self, period=14):
        """
        Calculate and analyze the Relative Strength Index (RSI) for a given dataset.

        The RelativeStrengthIndex class computes the RSI for a financial dataset, detects overbought and
        oversold conditions, identifies divergence between RSI and price, and detects support and resistance
        levels using RSI. It operates on a DataFrame containing financial data and is applicable to both
        cryptocurrency and equity datasets.

        Parameters:
        -----------
            period (int): The period for calculating RSI, default is 14 days.

        Methods:
        --------
            _calculate_rsi():
                Calculates the RSI based on the specified period and stores it in the DataFrame.

            _detect_overbought_oversold():
                Detects overbought and oversold conditions based on RSI values, and generates buy/sell signals.

            _detect_divergence():
                Detects divergence between RSI and price by comparing their trends.

            _detect_support_resistance():
                Detects support and resistance levels using RSI values.

            get_rsi():
                Returns the DataFrame with the RSI, overbought/oversold signals, buy/sell signals, divergence, and support/resistance levels.

            plot_rsi():
                Plots the RSI with overbought/oversold levels, divergence points, and support/resistance levels.
        """        
        return _RelativeStrengthIndex(self, period)
       
    def FastStochasticOscillator(self, k_period=14, d_period=3):
        """
        Calculate and analyze the Fast Stochastic Oscillator for a given dataset.

        The FastStochasticOscillator class computes the %K and %D lines of the Stochastic Oscillator, 
        detects overbought and oversold conditions, identifies crosses between the %K and %D lines, 
        and analyzes divergence between the Stochastic Oscillator and price. It operates on a DataFrame 
        containing financial data and is suitable for both cryptocurrency and equity datasets.

        Parameters:
        -----------
            k_period (int): The period over which to calculate the %K line. Default is 14 days.
            d_period (int): The period over which to calculate the %D line. Default is 3 days.

        Methods:
        --------
            _calculate_stochastic():
                Calculates the %K and %D lines of the Stochastic Oscillator and stores them in the DataFrame.

            _detect_overbought_oversold():
                Detects overbought and oversold conditions based on the %K line values.

            _detect_crosses():
                Detects intersections (crosses) between the %K and %D lines, signaling potential momentum shifts.

            _detect_divergence():
                Detects divergence between the Stochastic Oscillator and price by comparing their trends.

            get_stochastic():
                Returns the DataFrame with the Stochastic Oscillator %K, %D lines, and detected signals.

            plot_stochastic():
                Plots the %K and %D lines of the Stochastic Oscillator, highlighting overbought/oversold conditions, crosses, and divergence.
        """        
        return _FastStochasticOscillator(self, k_period, d_period)

    def MovingAveragesAndBollingerBands(self, sma_period=20, ema_period=20, bb_period=20, bb_std=2):
        """
        A class to compute and analyze Simple Moving Averages (SMA), Exponential Moving Averages (EMA), 
        and Bollinger Bands for a given dataset.

        The MovingAveragesAndBollingerBands class calculates the SMA, EMA, and Bollinger Bands, and detects 
        crossover signals between the SMA and EMA. It operates on a DataFrame containing financial data and 
        is suitable for both cryptocurrency and equity datasets.

        Parameters:
        -----------
            sma_period (int): The period over which to calculate the Simple Moving Average. Default is 20 days.
            ema_period (int): The period over which to calculate the Exponential Moving Average. Default is 20 days.
            bb_period (int): The period over which to calculate the Bollinger Bands. Default is 20 days.
            bb_std (float): The number of standard deviations to use for the Bollinger Bands. Default is 2.

        Methods:
        --------
            _calculate_sma():
                Calculates the Simple Moving Average (SMA) and adds it to the DataFrame.

            _calculate_ema():
                Calculates the Exponential Moving Average (EMA) and adds it to the DataFrame.

            _calculate_bollinger_bands():
                Calculates the Bollinger Bands (Upper, Middle, and Lower) and adds them to the DataFrame.

            _detect_crossovers():
                Detects when the EMA crosses above or below the SMA and adds these signals to the DataFrame.

            get_indicators():
                Returns the DataFrame with SMA, EMA, Bollinger Bands, and detected signals.

            plot_indicators():
                Plots the Close price, SMA, EMA, Bollinger Bands, and highlights Buy and Sell signals on a chart.
        """        
        return _MovingAveragesAndBollingerBands(self, sma_period, ema_period, bb_period, bb_std)

    def AverageTrueRange(self, atr_period=14):
        """
        A class to compute and analyze the Average True Range (ATR) of a financial time series.

        The AverageTrueRange class calculates the ATR, which is a measure of volatility in a time series. 
        ATR is used to understand market volatility and can assist in determining trade positions and risk management.

        Parameters:
        -----------
            atr_period (int): The period over which to calculate the ATR. Default is 14 days.

        Methods:
        --------
            _calculate_tr():
                Calculates the True Range (TR) for each period and adds it to the DataFrame.

            _calculate_atr():
                Calculates the Average True Range (ATR) based on the True Range and adds it to the DataFrame.

            get_atr():
                Returns the DataFrame with the ATR and other relevant columns.

            plot_atr():
                Plots the ATR alongside the closing price on a chart.

            identify_volatility_shifts():
                Identifies and prints periods of expanding or contracting volatility based on changes in ATR.
        """        
        return _AverageTrueRange(self, atr_period)

def __dir__():
    return __all__
