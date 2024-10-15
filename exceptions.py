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

class FinancialStatementUnavailableError(Exception):
    """Exception raised when financial statement data is unavailable."""
    def __init__(self, message="Quarterly data not available"):
        modified_message = re.sub(
            "Our data provider is not providing us with",
            "The data provider is not providing",
            message
        )
        self.message = modified_message
        super().__init__(self.message)
        
class HTTP404TickerError(Exception):
    """
    HTTP404TickerError Exception

    Example of using the class with a manually specified ticker:
    --
    
    try:
        raise HTTP404TickerError("http://example.com/api?symbols=XYZ", ticker="AAPL")
    except HTTP404TickerError as e:
        print(e)


    Example of using the class with an extracted ticker:
    --
    
    try:
        raise HTTP404TickerError("http://example.com/api?symbols=XYZ")
    except HTTP404TickerError as e:
        print(e)
    """	
    def __init__(self, url, ticker=None, message="Data not found for ticker:"):
        self.url = url
        self.ticker = ticker if ticker is not None else self._extract_ticker(url)
        self.message = f"{message} {self.ticker}"
        super().__init__(self.message)

    def _extract_ticker(self, url):
        match = re.search(r'(?:\/|\?|&|symbols=)([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[\/\?&]|$)', url)
        return match.group(1) if match else ''

class LatestStockPriceRetrievalError(Exception):
    """Exception raised for errors in the retrieval of the latest stock price.

    Attributes:
        ticker -- optional ticker symbol for which the latest stock price was requested
        message -- explanation of the error
    """
    def __init__(self, ticker=None, message="Failed to retrieve the latest stock price"):
        self.ticker = ticker
        if ticker:
            message = f"{message} for ticker: {ticker}"
        super().__init__(message)

class HistoricalDataRetrievalError(Exception):
    """Exception raised for errors in the retrieval of historical stock price data.

    Attributes:
        tickers -- optional ticker symbol(s) for which the historical data was requested
        start_date -- optional start date of the requested historical data range
        end_date -- optional end date of the requested historical data range
        message -- explanation of the error
    """
    def __init__(self, tickers=None, start_date=None, end_date=None, message="Failed to retrieve historical data"):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        message_details = []
        if tickers:
            message_details.append(f"ticker(s): {tickers}")
        if start_date and end_date:
            message_details.append(f"from {start_date} to {end_date}")
        full_message = f"{message} {' '.join(message_details)}"
        super().__init__(full_message)
        
class RetrievalError(Exception):
    """Exception raised for errors in the retrieval stock data."""
    def __init__(self, ticker=None, message="Failed to retrieve the data."):
        self.ticker = ticker
        if ticker:
            message = f"{message} for ticker: {ticker}"
        super().__init__(message)
        
class DividendError(Exception):
    def __init__(self, url, ticker=None, message="Dividend not found for ticker:"):
        self.url = url        
        self.ticker = ticker if ticker is not None else self._extract_ticker(url)
        self.default_message = f"Dividend not found for ticker: {self.ticker}"        
        self.message = self.default_message if message is None else f"{self.ticker}'s {message}"        
        super().__init__(self.message)

    def _extract_ticker(self, url):
        match = re.search(r'(?:\/|\?|&|symbols=)([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[\/\?&]|$)', url)
        return match.group(1) if match else ''
