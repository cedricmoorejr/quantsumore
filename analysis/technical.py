# -*- coding: utf-8 -*-
#
# quantsumore - finance api client
# https://github.com/cedricmoorejr/quantsumore/
#
# Copyright 2023-2024 Cedric Moore Jr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import re
import pandas as pd
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt


class tAnalyze:
    """
    tAnalyze class to handle and preprocess financial data, and compute various technical indicators.

    Attributes:
        dataframe (Dataframe): An instance of the Dataframe class that handles data preprocessing.
        df (pd.DataFrame): The processed DataFrame containing financial data.
        ticker (str): The ticker symbol of the stock or asset being analyzed, extracted from the DataFrame.

    Methods:
        DirectionalMovementIndex(period=14, adx_threshold=25):
            Creates an instance of the _DirectionalMovementIndex class to compute the DMI and ADX indicators.
        
        AroonIndicator(period=25):
            Creates an instance of the _AroonIndicator class to compute Aroon Up and Aroon Down indicators.
        
        OnBalanceVolume():
            Creates an instance of the _OnBalanceVolume class to compute the OBV indicator.
        
        AccumulationDistributionLine():
            Creates an instance of the _AccumulationDistributionLine class to compute the A/D Line indicator.
        
        MACD(short_window=12, long_window=26, signal_window=9):
            Creates an instance of the _MACD class to compute the MACD line, Signal line, and MACD Histogram.
        
        RelativeStrengthIndex(period=14):
            Creates an instance of the _RelativeStrengthIndex class to compute the RSI indicator.
        
        FastStochasticOscillator(k_period=14, d_period=3):
            Creates an instance of the _FastStochasticOscillator class to compute the Stochastic Oscillator (%K and %D lines).
        
        MovingAveragesAndBollingerBands(sma_period=20, ema_period=20, bb_period=20, bb_std=2):
            Creates an instance of the _MovingAveragesAndBollingerBands class to compute SMA, EMA, and Bollinger Bands.
        
        AverageTrueRange(atr_period=14):
            Creates an instance of the _AverageTrueRange class to compute the ATR indicator.

    Example Usage:
        >>> data = pd.DataFrame({
                'Date': pd.date_range(start='2020-01-01', periods=100),
                'High': np.random.rand(100) * 100 + 150,
                'Low': np.random.rand(100) * 100 + 100,
                'Open': np.random.rand(100) * 100 + 125,
                'Close': np.random.rand(100) * 100 + 130,
                'Volume': np.random.randint(100, 1000, size=100),
                'Symbol': ['AAPL'] * 100
            })
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
    def __init__(self, df):
        self.dataframe = None
        self.df = None
        self.ticker = None
        try:
            self.dataframe = self.Dataframe(df)
            self.df = self.dataframe.df  
            self.ticker = self.df['Symbol'].iloc[0] 
            print(f"Historical prices successfully loaded for {self.ticker}.")
        except Exception as e:
            print(f"Historical prices could not be loaded for {self.ticker or 'ticker symbol'}. Error: {e}")

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
        def __init__(self, df: pd.DataFrame):
            if df.empty:
                raise ValueError("DataFrame is empty")
            self.df = deepcopy(df)
            self.rename_cols()
            self.convert_to_floats()
            self.filter_to_single_symbol()
            self.normalize_date()
            has_columns, missing = self.check_columns()
            if not has_columns:
                raise ValueError(f"Missing required columns: {missing}")
               
        def rename_cols(self):
            def find_best_matches(df):
                keyword_map = {
                    'Symbol': ['ticker', 'symbol'],
                    'Date': ['date'],
                    'High': ['high'],
                    'Low': ['low'],
                    'Open': ['open'],
                    'Close': ['close'],
                    'Volume': ['volume']
                }
                column_renames = {}
                for standard_name, keywords in keyword_map.items():
                    for keyword in keywords:
                        pattern = re.compile(r'^' + keyword + r'|' + keyword, re.IGNORECASE)
                        best_matches = sorted([col for col in df.columns if pattern.search(col)],
                                              key=lambda x: not x.lower().startswith(keyword))
                        if best_matches:
                            column_renames[best_matches[0]] = standard_name
                            break
                return column_renames

            column_map = find_best_matches(self.df)
            if not column_map:
                raise ValueError("Failed to match critical columns based on keywords.")
            self.df = self.df.rename(columns=column_map, inplace=False)
            if set(column_map.values()) != set(self.df.columns):
                self.df = self.df[list(column_map.values())]

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
                self.df['Date'] = self.df['Date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d'))
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
        """Verify if the DataFrame has a sufficient number of unique dates in the 'Date' column to support the specified period for rolling calculations."""
        unique_dates = self.df['Date'].nunique()
        if unique_dates < period:
            raise ValueError(f"Insufficient data: The DataFrame contains only {unique_dates} unique dates, but at least {period} unique dates are required.")        

    ## Indicators
    ##--------------------------------------------------------------------------------------------------
    class _DirectionalMovementIndex:
        def __init__(self, parent, period=14, adx_threshold=25):
            self.parent = parent
            self.df = self.parent.df
            self.period = period
            self.adx_threshold = adx_threshold

            # Verify sufficient data before proceeding
            self.parent.verify_period_sufficiency(self.period)

            # Calculate indicators and signals
            self._calculate_indicators()
            self._calculate_signals()
            
        def _calculate_indicators(self):
            """Calculate the necessary indicators: TR, +DM, -DM, ATR, +DI, -DI, DX, and ADX."""
            # Calculate True Range (TR)
            self.df['High-Low'] = self.df['High'] - self.df['Low']
            self.df['High-PrevClose'] = abs(self.df['High'] - self.df['Close'].shift(1))
            self.df['Low-PrevClose'] = abs(self.df['Low'] - self.df['Close'].shift(1))
            self.df['TR'] = self.df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

            # Calculate Directional Movement (+DM and -DM)
            self.df['+DM'] = np.where((self.df['High'] - self.df['High'].shift(1)) > (self.df['Low'].shift(1) - self.df['Low']), 
                                      np.maximum(self.df['High'] - self.df['High'].shift(1), 0), 0)
            self.df['-DM'] = np.where((self.df['Low'].shift(1) - self.df['Low']) > (self.df['High'] - self.df['High'].shift(1)), 
                                      np.maximum(self.df['Low'].shift(1) - self.df['Low'], 0), 0)

            # Calculate Smoothed ATR, +DM, and -DM
            self.df['ATR'] = self.df['TR'].rolling(window=self.period).mean()
            self.df['+DM_smooth'] = self.df['+DM'].rolling(window=self.period).mean()
            self.df['-DM_smooth'] = self.df['-DM'].rolling(window=self.period).mean()

            # Calculate +DI and -DI
            self.df['+DI'] = 100 * (self.df['+DM_smooth'] / self.df['ATR'])
            self.df['-DI'] = 100 * (self.df['-DM_smooth'] / self.df['ATR'])

            # Calculate DX
            self.df['DX'] = 100 * (abs(self.df['+DI'] - self.df['-DI']) / (self.df['+DI'] + self.df['-DI']))

            # Calculate ADX
            self.df['ADX'] = self.df['DX'].rolling(window=self.period).mean()

        def _calculate_signals(self):
            """Determine Buy/Sell signals and their strength based on ADX."""
            # Determine Buy and Sell Signals
            self.df['Buy_Signal'] = np.where((self.df['+DI'] > self.df['-DI']) & 
                                             (self.df['+DI'].shift(1) <= self.df['-DI'].shift(1)), 1, 0)

            self.df['Sell_Signal'] = np.where((self.df['-DI'] > self.df['+DI']) & 
                                              (self.df['-DI'].shift(1) <= self.df['+DI'].shift(1)), 1, 0)

            # Strong Buy and Sell Signals based on ADX
            self.df['Strong_Buy'] = np.where((self.df['Buy_Signal'] == 1) & 
                                             (self.df['ADX'] >= self.adx_threshold), 1, 0)

            self.df['Strong_Sell'] = np.where((self.df['Sell_Signal'] == 1) & 
                                              (self.df['ADX'] >= self.adx_threshold), 1, 0)

        def get_signals(self):
            """Return the DataFrame with the calculated indicators and signals."""
            return self.df[['Date', '+DI', '-DI', 'ADX', 'Buy_Signal', 'Sell_Signal', 'Strong_Buy', 'Strong_Sell']]

        def get_trend_strength(self):
            """
            Classify the trend based on ADX values.

            :return: A DataFrame with trend strength interpretation:
                     'Strong Trend', 'Weak Trend', or 'Trendless Market'
            """
            conditions = [
                (self.df['ADX'] >= 25),
                (self.df['ADX'] < 25) & (self.df['ADX'] >= 20),
                (self.df['ADX'] < 20)
            ]
            choices = ['Strong Trend', 'Weak Trend', 'Trendless Market']

            self.df['Trend_Strength'] = np.select(conditions, choices, default='Unknown')

            return self.df[['Date', 'ADX', 'Trend_Strength']]

        def plot_indicators(self):
            """Plot +DI, -DI, and ADX to visualize trend signals."""
            plt.figure(figsize=(14, 8))

            # Plot +DI and -DI
            plt.plot(self.df['Date'], self.df['+DI'], label='+DI', color='green')
            plt.plot(self.df['Date'], self.df['-DI'], label='-DI', color='red')

            # Plot ADX
            plt.plot(self.df['Date'], self.df['ADX'], label='ADX', color='blue')

            # Highlight areas of strong trend
            plt.fill_between(self.df['Date'], 0, self.df['ADX'], where=self.df['ADX'] >= 25, color='blue', alpha=0.1)

            plt.title('DMI and ADX Indicators')
            plt.xlabel('Date')
            plt.ylabel('Indicator Value')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

        def plot_trend_strength(self):
            """Plot the ADX and trend strength classification."""
            trend_df = self.get_trend_strength()

            plt.figure(figsize=(14, 8))

            # Plot ADX
            plt.plot(trend_df['Date'], trend_df['ADX'], label='ADX', color='blue')

            # Highlight areas of strong trend
            plt.fill_between(trend_df['Date'], 0, trend_df['ADX'], where=trend_df['Trend_Strength'] == 'Strong Trend', color='blue', alpha=0.1, label='Strong Trend')

            # Highlight areas of trendless market
            plt.fill_between(trend_df['Date'], 0, trend_df['ADX'], where=trend_df['Trend_Strength'] == 'Trendless Market', color='gray', alpha=0.1, label='Trendless Market')

            plt.title('ADX and Trend Strength')
            plt.xlabel('Date')
            plt.ylabel('ADX Value')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

    class _AroonIndicator:
        def __init__(self, parent, period=25):
            self.parent = parent
            self.df = self.parent.df
            self.period = period

            # Verify sufficient data before proceeding
            self.parent.verify_period_sufficiency(self.period)

            # Calculate
            self._calculate_aroon()
            self._detect_trends()
            
        def _calculate_aroon(self):
            """Calculate the Aroon Up and Aroon Down indicators and store them in the DataFrame."""
            # Calculate Aroon Up
            self.df['Aroon_Up'] = self.df['High'].rolling(window=self.period).apply(
                lambda x: ((self.period - x[::-1].argmax()) / self.period) * 100, raw=True
            )

            # Calculate Aroon Down
            self.df['Aroon_Down'] = self.df['Low'].rolling(window=self.period).apply(
                lambda x: ((self.period - x[::-1].argmin()) / self.period) * 100, raw=True
            )

        def _detect_trends(self):
            """Detect trends and consolidations based on Aroon Up and Aroon Down interactions."""
            self.df['Trend_Signal'] = 'None'

            # Detect Aroon-Up crossing above Aroon-Down (Potential Uptrend Start)
            self.df['Trend_Signal'] = np.where(
                (self.df['Aroon_Up'] > self.df['Aroon_Down']) & (self.df['Aroon_Up'].shift(1) <= self.df['Aroon_Down'].shift(1)),
                'Uptrend Start',
                self.df['Trend_Signal']
            )

            # Detect Aroon-Down crossing above Aroon-Up (Potential Downtrend Start)
            self.df['Trend_Signal'] = np.where(
                (self.df['Aroon_Down'] > self.df['Aroon_Up']) & (self.df['Aroon_Down'].shift(1) <= self.df['Aroon_Up'].shift(1)),
                'Downtrend Start',
                self.df['Trend_Signal']
            )

            # Strong Uptrend: Aroon-Up between 70 and 100, Aroon-Down between 0 and 30
            self.df['Trend_Signal'] = np.where(
                (self.df['Aroon_Up'] >= 70) & (self.df['Aroon_Up'] <= 100) &
                (self.df['Aroon_Down'] >= 0) & (self.df['Aroon_Down'] <= 30),
                'Strong Uptrend',
                self.df['Trend_Signal']
            )

            # Strong Downtrend: Aroon-Down between 70 and 100, Aroon-Up between 0 and 30
            self.df['Trend_Signal'] = np.where(
                (self.df['Aroon_Down'] >= 70) & (self.df['Aroon_Down'] <= 100) &
                (self.df['Aroon_Up'] >= 0) & (self.df['Aroon_Up'] <= 30),
                'Strong Downtrend',
                self.df['Trend_Signal']
            )

            # Range Trading/Consolidation: Aroon-Up and Aroon-Down moving in parallel
            self.df['Trend_Signal'] = np.where(
                abs(self.df['Aroon_Up'] - self.df['Aroon_Down']) <= 10, # Adjust this threshold as needed
                'Range Trading/Consolidation',
                self.df['Trend_Signal']
            )

        def get_aroon(self):
            """Return the DataFrame with the Aroon Up, Aroon Down, and Trend Signal columns."""
            return self.df[['Date', 'Close', 'Aroon_Up', 'Aroon_Down', 'Trend_Signal']]

        def plot_aroon(self):
            """Plot the Aroon Up and Aroon Down indicators, highlighting trend signals."""
            plt.figure(figsize=(14, 8))
            plt.plot(self.df['Date'], self.df['Aroon_Up'], label='Aroon Up', color='green')
            plt.plot(self.df['Date'], self.df['Aroon_Down'], label='Aroon Down', color='red')
            plt.axhline(50, color='gray', linestyle='--', label='50 level')

            # Highlight areas of detected trend signals
            trend_signal_dates = self.df[self.df['Trend_Signal'] != 'None']['Date']
            for trend in ['Uptrend Start', 'Downtrend Start', 'Strong Uptrend', 'Strong Downtrend', 'Range Trading/Consolidation']:
                plt.scatter(self.df[self.df['Trend_Signal'] == trend]['Date'], 
                            self.df[self.df['Trend_Signal'] == trend]['Aroon_Up'],
                            label=trend, s=50, alpha=0.7)

            plt.title('Aroon Indicator with Trend Signals')
            plt.xlabel('Date')
            plt.ylabel('Aroon Value')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

    class _OnBalanceVolume:
        def __init__(self, parent):
            self.parent = parent
            self.df = self.parent.df

            # Calculate indicators and signals
            self._calculate_obv()

        def _calculate_obv(self):
            """Calculate the On-Balance Volume (OBV) and store it in the DataFrame."""
            self.df['OBV'] = 0
            
            # Calculate OBV
            self.df['OBV'] = self.df['Volume'].where(self.df['Close'] > self.df['Close'].shift(1), -self.df['Volume'])
            self.df['OBV'] = self.df['OBV'].fillna(0).cumsum()

        def get_obv(self):
            """Return the DataFrame with the OBV column."""
            return self.df[['Date', 'Close', 'Volume', 'OBV']]

        def detect_divergence(self):
            """
            Detect divergence between OBV and price.
            
            :return: DataFrame with detected divergence points.
            """
            self.df['Price_Trend'] = np.where(self.df['Close'] > self.df['Close'].shift(1), 'up', 
                                              np.where(self.df['Close'] < self.df['Close'].shift(1), 'down', 'flat'))
            self.df['OBV_Trend'] = np.where(self.df['OBV'] > self.df['OBV'].shift(1), 'up', 
                                            np.where(self.df['OBV'] < self.df['OBV'].shift(1), 'down', 'flat'))
            
            # Divergence occurs when price and OBV trends differ
            self.df['Divergence'] = np.where((self.df['Price_Trend'] == 'up') & (self.df['OBV_Trend'] == 'down'), 'bearish',
                                             np.where((self.df['Price_Trend'] == 'down') & (self.df['OBV_Trend'] == 'up'), 'bullish', 'none'))
            
            divergence_df = self.df[self.df['Divergence'] != 'none'][['Date', 'Close', 'OBV', 'Divergence']]
            
            if divergence_df.empty:
                print("No divergence detected between OBV and price.")
            return divergence_df

        def plot_obv_with_divergence(self):
            """Plot OBV and closing price with highlighted divergence points."""
            fig, ax1 = plt.subplots(figsize=(14, 8))

            ax1.set_xlabel('Date')
            ax1.set_ylabel('Close Price', color='tab:blue')
            ax1.plot(self.df['Date'], self.df['Close'], color='tab:blue', label='Close Price')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

            ax2 = ax1.twinx()
            ax2.set_ylabel('On-Balance Volume (OBV)', color='tab:orange')
            ax2.plot(self.df['Date'], self.df['OBV'], color='tab:orange', label='OBV')
            ax2.tick_params(axis='y', labelcolor='tab:orange')

            # Highlight divergence points
            divergence_points = self.df[self.df['Divergence'] != 'none']
            ax1.scatter(divergence_points['Date'], divergence_points['Close'], color='red', label='Divergence', zorder=5)

            fig.tight_layout()
            plt.title('On-Balance Volume (OBV) and Close Price with Divergence')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

    class _AccumulationDistributionLine:
        def __init__(self, parent):
            self.parent = parent
            self.df = self.parent.df

            # Calculate
            self._calculate_ad_line()
            
        def _calculate_ad_line(self):
            """Calculate the Accumulation/Distribution (A/D) Line and store it in the DataFrame."""
            # Calculate the Money Flow Multiplier (MFM)
            self.df['MFM'] = ((self.df['Close'] - self.df['Low']) - (self.df['High'] - self.df['Close'])) / (self.df['High'] - self.df['Low'])
            
            # Ensure there are no division by zero errors in case of High == Low
            self.df['MFM'] = self.df['MFM'].fillna(0)
            
            # Calculate the Money Flow Volume (MFV)
            self.df['MFV'] = self.df['MFM'] * self.df['Volume']
            
            # Calculate the Accumulation/Distribution Line (A/D Line)
            self.df['AD_Line'] = self.df['MFV'].cumsum()

        def get_ad_line(self):
            """Return the DataFrame with the A/D Line column."""
            return self.df[['Date', 'Close', 'Volume', 'AD_Line']]

        def detect_divergence(self):
            """
            Detect divergence between the A/D Line and price.
            
            :return: DataFrame with detected divergence points.
            """
            self.df['Price_Trend'] = np.where(self.df['Close'] > self.df['Close'].shift(1), 'up', 
                                              np.where(self.df['Close'] < self.df['Close'].shift(1), 'down', 'flat'))
            self.df['AD_Trend'] = np.where(self.df['AD_Line'] > self.df['AD_Line'].shift(1), 'up', 
                                           np.where(self.df['AD_Line'] < self.df['AD_Line'].shift(1), 'down', 'flat'))
            
            # Divergence occurs when price and A/D Line trends differ
            self.df['Divergence'] = np.where((self.df['Price_Trend'] == 'up') & (self.df['AD_Trend'] == 'down'), 'bearish',
                                             np.where((self.df['Price_Trend'] == 'down') & (self.df['AD_Trend'] == 'up'), 'bullish', 'none'))
            
            divergence_df = self.df[self.df['Divergence'] != 'none'][['Date', 'Close', 'AD_Line', 'Divergence']]
            
            if divergence_df.empty:
                print("No divergence detected between A/D Line and price.")
            return divergence_df

        def plot_ad_line_with_divergence(self):
            """Plot the A/D Line and closing price with highlighted divergence points."""
            fig, ax1 = plt.subplots(figsize=(14, 8))

            ax1.set_xlabel('Date')
            ax1.set_ylabel('Close Price', color='tab:blue')
            ax1.plot(self.df['Date'], self.df['Close'], color='tab:blue', label='Close Price')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

            ax2 = ax1.twinx()
            ax2.set_ylabel('Accumulation/Distribution Line (A/D Line)', color='tab:green')
            ax2.plot(self.df['Date'], self.df['AD_Line'], color='tab:green', label='A/D Line')
            ax2.tick_params(axis='y', labelcolor='tab:green')

            # Highlight divergence points
            divergence_points = self.df[self.df['Divergence'] != 'none']
            ax1.scatter(divergence_points['Date'], divergence_points['Close'], color='red', label='Divergence', zorder=5)

            fig.tight_layout()
            plt.title('Accumulation/Distribution Line (A/D Line) and Close Price with Divergence')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

    class _MACD:
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

    class _RelativeStrengthIndex:
        def __init__(self, parent, period=14):
            self.parent = parent
            self.df = self.parent.df
            self.period = period

            # Verify sufficient data before proceeding
            self.parent.verify_period_sufficiency(self.period)

            # Calculate indicators and signals
            self._detect_overbought_oversold()
            self._detect_divergence()
            self._detect_support_resistance()

        def _calculate_rsi(self):
            """Calculate the RSI based on the specified period."""
            delta = self.df['Close'].diff(1)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)

            avg_gain = pd.Series(gain).rolling(window=self.period, min_periods=1).mean()
            avg_loss = pd.Series(loss).rolling(window=self.period, min_periods=1).mean()

            rs = avg_gain / avg_loss
            self.df['RSI'] = 100 - (100 / (1 + rs))

        def _detect_overbought_oversold(self):
            """Detect overbought and oversold conditions."""
            self.df['Overbought'] = np.where(self.df['RSI'] > 70, 'Overbought', 'None')
            self.df['Oversold'] = np.where(self.df['RSI'] < 30, 'Oversold', 'None')

            # Additional logic for waiting for RSI to cross below 70 or above 30
            self.df['Sell_Signal'] = np.where((self.df['RSI'] > 70) & (self.df['RSI'].shift(1) <= 70), 'Sell Signal', 'None')
            self.df['Buy_Signal'] = np.where((self.df['RSI'] < 30) & (self.df['RSI'].shift(1) >= 30), 'Buy Signal', 'None')

        def _detect_divergence(self):
            """Detect divergence between RSI and price."""
            self.df['Price_Trend'] = np.where(self.df['Close'] > self.df['Close'].shift(1), 'up',
                                              np.where(self.df['Close'] < self.df['Close'].shift(1), 'down', 'flat'))
            self.df['RSI_Trend'] = np.where(self.df['RSI'] > self.df['RSI'].shift(1), 'up',
                                            np.where(self.df['RSI'] < self.df['RSI'].shift(1), 'down', 'flat'))

            # Divergence occurs when price and RSI trends differ
            self.df['Divergence'] = np.where((self.df['Price_Trend'] == 'up') & (self.df['RSI_Trend'] == 'down'), 'Bearish Divergence',
                                             np.where((self.df['Price_Trend'] == 'down') & (self.df['RSI_Trend'] == 'up'), 'Bullish Divergence', 'None'))

        def _detect_support_resistance(self):
            """Detect support and resistance levels using RSI."""
            self.df['Support_Resistance'] = 'None'

            # During uptrends, RSI typically holds above 30 and reaches 70 or above
            self.df['Support_Resistance'] = np.where((self.df['RSI'] >= 70) & (self.df['RSI'].shift(1) < 70), 'Resistance',
                                                     self.df['Support_Resistance'])
            self.df['Support_Resistance'] = np.where((self.df['RSI'] <= 30) & (self.df['RSI'].shift(1) > 30), 'Support',
                                                     self.df['Support_Resistance'])

        def get_rsi(self):
            """Return the DataFrame with the RSI and detected signals."""
            return self.df[['Date', 'Close', 'RSI', 'Overbought', 'Oversold', 'Sell_Signal', 'Buy_Signal', 'Divergence', 'Support_Resistance']]

        def plot_rsi(self):
            """Plot the RSI with overbought/oversold levels, divergence, and support/resistance levels."""
            plt.figure(figsize=(14, 8))

            # Plot RSI
            plt.plot(self.df['Date'], self.df['RSI'], label='RSI', color='blue')
            plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
            plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')

            # Highlight overbought and oversold signals
            plt.scatter(self.df[self.df['Overbought'] == 'Overbought']['Date'],
                        self.df[self.df['Overbought'] == 'Overbought']['RSI'], color='red', label='Overbought Signal', marker='v')
            plt.scatter(self.df[self.df['Oversold'] == 'Oversold']['Date'],
                        self.df[self.df['Oversold'] == 'Oversold']['RSI'], color='green', label='Oversold Signal', marker='^')

            # Highlight divergence points
            for div_type in ['Bearish Divergence', 'Bullish Divergence']:
                plt.scatter(self.df[self.df['Divergence'] == div_type]['Date'],
                            self.df[self.df['Divergence'] == div_type]['RSI'], label=div_type, marker='o', alpha=0.7)

            plt.title('Relative Strength Index (RSI)')
            plt.xlabel('Date')
            plt.ylabel('RSI Value')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

    class _FastStochasticOscillator:
        def __init__(self, parent, k_period=14, d_period=3):
            self.parent = parent
            self.df = self.parent.df
            self.k_period = k_period
            self.d_period = d_period

            # Verify sufficient data before proceeding
            max_period = max(self.k_period, self.d_period)
            self.parent.verify_period_sufficiency(max_period)

            # Calculate indicators and signals
            self._calculate_stochastic()
            self._detect_overbought_oversold()
            self._detect_crosses()
            self._detect_divergence()

        def _calculate_stochastic(self):
            """Calculate the %K and %D lines of the Stochastic Oscillator."""
            # Calculate the Lowest Low and Highest High over the K period
            self.df['Lowest_Low'] = self.df['Low'].rolling(window=self.k_period).min()
            self.df['Highest_High'] = self.df['High'].rolling(window=self.k_period).max()

            # Calculate the %K line
            self.df['%K'] = 100 * ((self.df['Close'] - self.df['Lowest_Low']) / (self.df['Highest_High'] - self.df['Lowest_Low']))

            # Calculate the %D line as a 3-period moving average of %K
            self.df['%D'] = self.df['%K'].rolling(window=self.d_period).mean()

        def _detect_overbought_oversold(self):
            """Detect overbought and oversold conditions."""
            self.df['Overbought'] = np.where(self.df['%K'] > 80, 'Overbought', 'None')
            self.df['Oversold'] = np.where(self.df['%K'] < 20, 'Oversold', 'None')

        def _detect_crosses(self):
            """Detect intersections of %K and %D lines, signaling potential momentum shifts."""
            self.df['Cross'] = 'None'

            # Detect when %K crosses above %D (Bullish Signal)
            self.df['Cross'] = np.where(
                (self.df['%K'] > self.df['%D']) & (self.df['%K'].shift(1) <= self.df['%D'].shift(1)),
                'Bullish Cross',
                self.df['Cross']
            )

            # Detect when %K crosses below %D (Bearish Signal)
            self.df['Cross'] = np.where(
                (self.df['%K'] < self.df['%D']) & (self.df['%K'].shift(1) >= self.df['%D'].shift(1)),
                'Bearish Cross',
                self.df['Cross']
            )

        def _detect_divergence(self):
            """Detect divergence between the Stochastic Oscillator and price."""
            self.df['Price_Trend'] = np.where(self.df['Close'] > self.df['Close'].shift(1), 'up',
                                              np.where(self.df['Close'] < self.df['Close'].shift(1), 'down', 'flat'))
            self.df['Stoch_Trend'] = np.where(self.df['%K'] > self.df['%K'].shift(1), 'up',
                                              np.where(self.df['%K'] < self.df['%K'].shift(1), 'down', 'flat'))

            # Divergence occurs when price and Stochastic trends differ
            self.df['Divergence'] = np.where((self.df['Price_Trend'] == 'up') & (self.df['Stoch_Trend'] == 'down'), 'Bearish Divergence',
                                             np.where((self.df['Price_Trend'] == 'down') & (self.df['Stoch_Trend'] == 'up'), 'Bullish Divergence', 'None'))

        def get_stochastic(self):
            """Return the DataFrame with the Stochastic Oscillator %K, %D lines, and detected signals."""
            return self.df[['Date', 'Close', '%K', '%D', 'Overbought', 'Oversold', 'Cross', 'Divergence']]

        def plot_stochastic(self):
            """Plot the Stochastic Oscillator %K and %D lines, highlighting overbought/oversold conditions, crosses, and divergence."""
            plt.figure(figsize=(14, 8))

            # Plot %K and %D lines
            plt.plot(self.df['Date'], self.df['%K'], label='%K Line', color='blue')
            plt.plot(self.df['Date'], self.df['%D'], label='%D Line', color='red')

            # Add overbought and oversold lines
            plt.axhline(80, color='red', linestyle='--', label='Overbought (80)')
            plt.axhline(20, color='green', linestyle='--', label='Oversold (20)')

            # Highlight overbought and oversold signals
            plt.scatter(self.df[self.df['Overbought'] == 'Overbought']['Date'],
                        self.df[self.df['Overbought'] == 'Overbought']['%K'], color='red', label='Overbought Signal', marker='v')
            plt.scatter(self.df[self.df['Oversold'] == 'Oversold']['Date'],
                        self.df[self.df['Oversold'] == 'Oversold']['%K'], color='green', label='Oversold Signal', marker='^')

            # Highlight cross signals
            plt.scatter(self.df[self.df['Cross'] == 'Bullish Cross']['Date'],
                        self.df[self.df['Cross'] == 'Bullish Cross']['%K'], color='green', label='Bullish Cross', marker='o')
            plt.scatter(self.df[self.df['Cross'] == 'Bearish Cross']['Date'],
                        self.df[self.df['Cross'] == 'Bearish Cross']['%K'], color='red', label='Bearish Cross', marker='o')

            # Highlight divergence points
            for div_type in ['Bearish Divergence', 'Bullish Divergence']:
                plt.scatter(self.df[self.df['Divergence'] == div_type]['Date'],
                            self.df[self.df['Divergence'] == div_type]['%K'], label=div_type, marker='x', alpha=0.7)

            plt.title('Stochastic Oscillator with Overbought/Oversold, Crosses, and Divergence')
            plt.xlabel('Date')
            plt.ylabel('Stochastic Value')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

    class _MovingAveragesAndBollingerBands:
        def __init__(self, parent, sma_period=20, ema_period=20, bb_period=20, bb_std=2):
            self.parent = parent
            self.df = self.parent.df
            self.sma_period = sma_period
            self.ema_period = ema_period
            self.bb_period = bb_period
            self.bb_std = bb_std

            # Verify sufficient data before proceeding
            max_period = max(self.sma_period, self.ema_period, self.bb_period)
            self.parent.verify_period_sufficiency(max_period)

            # Calculate indicators and signals
            self._calculate_sma()
            self._calculate_ema()
            self._calculate_bollinger_bands()
            self._detect_crossovers()

        def _calculate_sma(self):
            self.df['SMA'] = self.df['Close'].rolling(window=self.sma_period).mean()

        def _calculate_ema(self):
            self.df['EMA'] = self.df['Close'].ewm(span=self.ema_period, adjust=False).mean()

        def _calculate_bollinger_bands(self):
            self.df['BB_Middle'] = self.df['Close'].rolling(window=self.bb_period).mean()
            self.df['BB_Upper'] = self.df['BB_Middle'] + (self.bb_std * self.df['Close'].rolling(window=self.bb_period).std())
            self.df['BB_Lower'] = self.df['BB_Middle'] - (self.bb_std * self.df['Close'].rolling(window=self.bb_period).std())

        def _detect_crossovers(self):
            self.df['Signal'] = 'None'

            # Detect when EMA crosses above SMA (Bullish Crossover)
            self.df['Signal'] = np.where((self.df['EMA'] > self.df['SMA']) & (self.df['EMA'].shift(1) <= self.df['SMA'].shift(1)),
                                         'Buy', self.df['Signal'])

            # Detect when EMA crosses below SMA (Bearish Crossover)
            self.df['Signal'] = np.where((self.df['EMA'] < self.df['SMA']) & (self.df['EMA'].shift(1) >= self.df['SMA'].shift(1)),
                                         'Sell', self.df['Signal'])

        def get_indicators(self):
            return self.df[['Date', 'Close', 'SMA', 'EMA', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'Signal']]

        def plot_indicators(self):
            plt.figure(figsize=(14, 8))
            plt.plot(self.df['Date'], self.df['Close'], label='Close Price', color='black')
            plt.plot(self.df['Date'], self.df['SMA'], label=f'SMA {self.sma_period}', color='blue')
            plt.plot(self.df['Date'], self.df['EMA'], label=f'EMA {self.ema_period}', color='red')
            plt.plot(self.df['Date'], self.df['BB_Middle'], label='Bollinger Middle Band', color='green')
            plt.plot(self.df['Date'], self.df['BB_Upper'], label='Bollinger Upper Band', color='orange')
            plt.plot(self.df['Date'], self.df['BB_Lower'], label='Bollinger Lower Band', color='orange')
            plt.fill_between(self.df['Date'], self.df['BB_Upper'], self.df['BB_Lower'], color='orange', alpha=0.1)

            # Highlight Buy and Sell signals
            plt.scatter(self.df[self.df['Signal'] == 'Buy']['Date'],
                        self.df[self.df['Signal'] == 'Buy']['Close'], color='green', label='Buy Signal', marker='^')
            plt.scatter(self.df[self.df['Signal'] == 'Sell']['Date'],
                        self.df[self.df['Signal'] == 'Sell']['Close'], color='red', label='Sell Signal', marker='v')

            plt.title('SMA, EMA, Bollinger Bands, and Signals')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

    class _AverageTrueRange:
        def __init__(self, parent, atr_period=14):
            self.parent = parent
            self.df = self.parent.df
            self.atr_period = atr_period

            # Verify sufficient data before proceeding
            self.parent.verify_period_sufficiency(self.atr_period)

            # Calculate indicators and signals
            self._calculate_atr()

        def _calculate_tr(self):
            """Calculate the True Range (TR) for each period."""
            self.df['High-Low'] = self.df['High'] - self.df['Low']
            self.df['High-PrevClose'] = abs(self.df['High'] - self.df['Close'].shift(1))
            self.df['Low-PrevClose'] = abs(self.df['Low'] - self.df['Close'].shift(1))
            self.df['TR'] = self.df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

        def _calculate_atr(self):
            """Calculate the Average True Range (ATR) based on the True Range."""
            self._calculate_tr()
            self.df['ATR'] = self.df['TR'].rolling(window=self.atr_period).mean()

        def get_atr(self):
            """Return the DataFrame with the ATR."""
            return self.df[['Date', 'Close', 'ATR']]

        def plot_atr(self):
            """Plot the ATR alongside the closing price."""
            plt.figure(figsize=(14, 8))

            # Plot Close Price
            plt.plot(self.df['Date'], self.df['Close'], label='Close Price', color='black')

            # Plot ATR
            plt.plot(self.df['Date'], self.df['ATR'], label=f'ATR {self.atr_period}', color='blue')

            plt.title('Average True Range (ATR)')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.legend(loc='upper left')
            plt.grid(True)
            plt.show()

        def identify_volatility_shifts(self):
            """Identify and print periods of expanding or contracting volatility based on ATR changes."""
            self.df['ATR_Change'] = self.df['ATR'].diff()

            expanding_volatility = self.df[self.df['ATR_Change'] > 0]
            contracting_volatility = self.df[self.df['ATR_Change'] < 0]

            print("Expanding Volatility Periods:")
            print(expanding_volatility[['Date', 'Close', 'ATR', 'ATR_Change']].tail(10))

            print("\nContracting Volatility Periods:")
            print(contracting_volatility[['Date', 'Close', 'ATR', 'ATR_Change']].tail(10))

    ## Call Indicators
    ##--------------------------------------------------------------------------------------------------
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
        return self._DirectionalMovementIndex(self, period, adx_threshold)
       
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
        return self._AroonIndicator(self, period)
       
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
        return self._OnBalanceVolume(self)

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
        return self._AccumulationDistributionLine(self)

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
        return self._MACD(self, short_window, long_window, signal_window)

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
        return self._RelativeStrengthIndex(self, period)
       
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
        return self._FastStochasticOscillator(self, k_period, d_period)

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
        return self._MovingAveragesAndBollingerBands(self, sma_period, ema_period, bb_period, bb_std)

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
        return self._AverageTrueRange(self, atr_period)





def __dir__():
    return ['tAnalyze']

__all__ = ['tAnalyze']
