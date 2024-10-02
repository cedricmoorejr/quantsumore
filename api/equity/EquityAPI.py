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



from copy import deepcopy

# Custom
from ..prep import stocks_asset
from .parse import stock, fin_statement, dividend
from ..._http.response_utils import Request, key_from_mapping, locKeyInStructure, validateHTMLResponse
from ...exceptions import FinancialStatementUnavailableError, HTTP404TickerError, RetrievalError, DividendError


class APIClient:
    def __init__(self, asset):
        self.asset = asset  
        
    def _ensure_company_description_period(self, profile):
        if 'Company Description' in profile:
            description = profile['Company Description']
            if description and description.strip():
                if not description.endswith('.'):
                    profile['Company Description'] = description.strip() + '.'
        return profile
       
    def __profile_data(self, ticker):
        """ Fetches company profile data for a given ticker symbol."""     	
        make_method = getattr(self.asset, 'make')
        url = make_method(query='profile', ticker=ticker)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        html_check = validateHTMLResponse(html_content, ticker=ticker, query="profile")
        if html_check:
            obj = stock.profile(html_content)
            data = obj.DATA()
            data = self._ensure_company_description_period(data)
            return data       
       
    def CompanyBio(self, ticker):
        """
        Provides an overview or summary of a company's information based on its ticker symbol.

        This method retrieves and displays information about a company identified by its ticker symbol.
        It returns the company's description.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose information is to be retrieved.

        Returns:
        -------
        str or None
            Returns the company description as a string.
        """
        data = self.__profile_data(ticker)
        if data:
            companyName = data['Company Name']
            companyDescription = data['Company Description']
            return companyDescription  
        return None
    
    def CompanyExecutives(self, ticker):
        """
        Provides information about a company's executives based on its ticker symbol.

        This method retrieves and displays information about the executives of a company identified
        by its ticker symbol. 

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose executive information is to be retrieved.

        Returns:
        -------
        list or dict or None
            Returns the list or dictionary of company executives.
        """    	
        data = self.__profile_data(ticker)
        if data:
            companyExecs = data['Company Executives']
            return companyExecs
        return None        
       
    def CompanyDetails(self, ticker):
        """
        Provides detailed information about a company based on its ticker symbol.

        This method retrieves and displays comprehensive details about a company identified
        by its ticker symbol. The details may include information such as the company's website,
        phone number, address, sector, industry, number of full-time employees, and other relevant
        data points.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose detailed information is to be retrieved.

        Returns:
        -------
        dict or None
            Returns a dictionary containing the company details.
        """    	
        data = self.__profile_data(ticker)
        if data:
            companyDetails = data['Company Details']
            return companyDetails
        return None

    def Stats(self, ticker):
        """
        Provides various statistical information and financial metrics about a company based on its ticker symbol.

        This method retrieves and displays statistical and financial data for a company identified by its
        ticker symbol. The data includes metrics such as the previous close price, open price, bid and ask prices,
        daily and 52-week price ranges, volume, market capitalization, beta, PE ratio, earnings per share (EPS),
        earnings date, dividend yield, ex-dividend date, and 1-year target estimate.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose statistical information is to be retrieved.

        Returns:
        -------
        dict or None
            Returns a dictionary containing statistical data.
        """    	
        make_method = getattr(self.asset, 'make')
        url = make_method(query='stats', ticker=ticker)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        html_check = validateHTMLResponse(html_content, ticker=ticker, query="stats")
        if html_check:
            obj = stock.quote_statistics(html_content)
            _, stats = obj.DATA()
            return stats
        return None          
          
    def sHistorical(self, ticker, start, end):
        """
        Retrieves historical stock price data for one or more companies based on their ticker symbols and a specified date range.

        This method fetches historical price data for one or more companies identified by their ticker symbols over a given
        date range. The data includes the date, opening price, highest price, lowest price, closing price,
        adjusted closing price, and trading volume for each trading day within the specified range.

        Parameters:
        ----------
        ticker : str or list of str
            The ticker symbol (or list of symbols) of the company (or companies) for which historical data is to be retrieved.

        start : str
            The start date for the historical data in the format 'YYYY-MM-DD'. This date is inclusive.

        end : str
            The end date for the historical data in the format 'YYYY-MM-DD'. This date is inclusive.

        Returns:
        -------
        pandas.DataFrame or None
            Returns a DataFrame containing historical price data for each trading day in the specified date range.
            If a single ticker is provided, the DataFrame contains data for that ticker.
            If a list of tickers is provided, the DataFrame will have a multi-index (or a concatenated DataFrame) with 
            data for each ticker. Each row represents a trading day, with columns for the date, open, high, low, close, 
            adjusted close, and volume. Returns None if no data is found for the given ticker(s) or if the data request fails.

        Raises:
        ------
        ValueError
            If the start and end date is not provided, a ValueError is raised.
        """   	
        try:
            if all(x is None for x in [start, end]): 
                raise ValueError("Start and end dates must be provided for historical data requests.")
            make_method = getattr(self.asset, 'make')
            url = make_method(query='price', ticker=ticker, start=start, end=end)
            content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
            if content:
                obj = stock.historical(content)
                return obj.DATA()
        except:
            raise RetrievalError(message="Failed to retrieve historical data")


    def sLatest(self, ticker):
        """
        Retrieves the latest stock price for a company based on its ticker symbol.

        This method fetches the most recent price of a stock identified by its ticker symbol. 
        During trading hours, it provides the current price. If trading is closed, it returns 
        the last available price from the most recent trading session.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose latest stock price is to be retrieved.

        Returns:
        -------
        float or None
            Returns a float representing the latest stock price. Returns None if no data 
            is found for the given ticker symbol or if the data request fails.

        Notes:
        -----
        This method is useful for obtaining real-time or near-real-time price information for a stock.
        It handles the distinction between active trading hours and after-hours or closed market scenarios,
        ensuring that the most relevant price is returned.
        """    	
        try:
            make_method = getattr(self.asset, 'make')
            url = make_method(query='price', ticker=ticker, start=dtparse.now(as_string=True), end=dtparse.now(as_string=True))
            content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
            if content:
                obj = stock.latest(content)
                return obj.DATA()
        except:
            raise RetrievalError(message="Failed to retrieve the latest stock price")

    def Lastn(self, ticker, interval="1m"):
        """
        Retrieves the latest stock price data for the specified ticker symbol over a given time interval.
        
        The method constructs a request URL, fetches the data, and parses it to return the most recent stock price along with associated metadata.

        Parameters:
        ----------
        ticker : str|list
            The ticker symbol or a list of symbols for which to retrieve stock data. Example: 'AAPL' for Apple Inc.
        interval : str, optional
            The granularity of the stock data to be retrieved, defaulting to '1m' (one minute). Supported intervals include:
            ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'].

        Returns:
        -------
        object
            An object containing the latest stock data, including prices, volume, timestamps, and additional metadata related to the trading session.

        Raises:
        ------
        ValueError
            If the specified interval is not supported.

        Notes:
        -----
        The returned data includes detailed metrics such as currency, exchange information, timestamps, and price points across specified trading periods. This allows for precise tracking of stock price movements within the last trading session.

        Example of fetched data:
        -----------------------
        Includes fields like 'currency', 'exchangeName', 'instrumentType', 'regularMarketPrice', 'fiftyTwoWeekHigh', 'chartPreviousClose', and timestamps of price data in regular trading sessions.
        """  	
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        if interval.lower() not in valid_intervals: 
            raise ValueError(f"Invalid interval. Valid intervals are: {', '.join(valid_intervals)}")
        make_method = getattr(self.asset, 'make')
        url = make_method(query='last', ticker=ticker, interval=interval)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        content_check = locKeyInStructure(content, target_key="spark", value_only=True, first_only=True, return_all=False)
        if content_check:
            obj = stock.last(content)
            return obj.DATA()
        else:
            message = locKeyInStructure(content, target_key="error", value_only=True, first_only=True, return_all=False) 
            raise HTTP404TickerError(message)

    def Financials(self, ticker, period="Quarterly"):
        """
        Retrieves financial statement data for the specified ticker symbol.

        This method fetches financial statement information such as the income statement, balance sheet, or cash flow 
        for a given company based on the `ticker`. The user can specify the type of statement (e.g., Income Statement, 
        Balance Sheet, Cash Flow Statement) and the reporting period (e.g., Quarterly or Annually). If no valid 
        statement type or period is provided, it raises an error.

        Parameters:
        ----------
        ticker : str
            The stock ticker symbol representing the company for which financial statements are requested.

        period : str, optional, default="Quarterly"
            The reporting period for the financial statement. It can be either:
            - 'Quarterly' (synonyms include 'Q', 'Quarter', 'Qtr')
            - 'Annually' (synonyms include 'A', 'Annual')
            If an invalid period is provided, a ValueError is raised.

        Returns:
        -------
        object
            A financial statement object that contains the requested data for the specified `ticker`, `statementType`, 
            and `period`. The object includes the financial data parsed from the response in JSON format.

        Raises:
        ------
        ValueError
            If an invalid `statementType` or `period` is provided, the function raises a ValueError to inform the user 
            that the input is not recognized.

        Notes:
        -----
        - The method uses an internal function `key_from_mapping` to map user-friendly terms to actual statement types 
          and periods. This allows for case-insensitive input and use of common synonyms (e.g., 'IS' for 'Income Statement').
        - The method constructs a request URL using the asset's `make` method and sends the request to retrieve the 
          financial data in JSON format.
        - This method requires that the `fin_statement.financials` object is available to parse the returned content 
          into a structured financial statement object.
        """ 	
        valid_periods = {'Quarterly': ['Q', 'Quarter', 'Qtr'], 'Annually': ['A', 'Annual']} 
        period = key_from_mapping(period, valid_periods, invert=False)
        if not period:
            raise ValueError("Invalid period.")
           
        make_method = getattr(self.asset, 'make')
        url = make_method(query='financials', ticker=ticker, period=period)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        content_check = locKeyInStructure(content, target_key="data", value_only=True, first_only=True, return_all=False) 
        if content_check:            
            obj = fin_statement.financials(json_content=content)
            return (obj.IncomeStatement, obj.BalanceSheet, obj.CashFlowStatement)
        else:
            message = locKeyInStructure(content, target_key="message", value_only=True, first_only=True, return_all=False) 
            raise FinancialStatementUnavailableError(message)
        
    def Dividends(self, ticker):
        """
        Retrieves dividend data for the specified ticker symbol.

        This method fetches dividend-related information such as ex-dividend dates, dividend yields, and payment dates 
        for a given company based on the `ticker`. It is designed to provide an overview of a company's dividend history 
        and current dividend policies.

        Parameters:
        ----------
        ticker : str|list
            The ticker symbol or a list of symbols for which to retrieve stock data. Example: 'AAPL' for Apple Inc.

        Returns:
        -------
        object
            A dividend data object that contains historical and current dividend information for the specified `ticker`. 
            The object includes the dividend data parsed from the response in JSON format.

        Raises:
        ------
        RetrievalError
            If the request fails, a RetrievalError is raised to inform the user that the dividend data could not be retrieved.

        Notes:
        -----
        - The method constructs a request URL using the asset's `make` method, tailored to query dividend information, 
          and sends the request to retrieve the data in JSON format.
        - The `dividend.dividend_history` function is used to process the JSON response and create a structured dividend 
          data object from the returned content.
        - This method assumes availability of an API or a method within `self.asset` that can generate appropriate endpoint 
          URLs for accessing dividend data.
        """
        make_method = getattr(self.asset, 'make')
        url = make_method(query='dividend_history', ticker=ticker)
        content = Request(url, headers_to_update=None, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)
        content_check = locKeyInStructure(content, target_key="data", value_only=True, first_only=True, return_all=False) 
        if content_check:            
            obj = dividend.dividend_history(content)
            return (obj.DividendReport, obj.DividendData)
        else:
            message = locKeyInStructure(content, target_key="message", value_only=True, first_only=True, return_all=False)
            raise DividendError(url=url, ticker=None, message=message)
           
    def __dir__(self):
        return ['CompanyBio','CompanyExecutives', 'CompanyDetails', 'Stats', 'sHistorical', 'sLatest', 'Lastn', 'Financials', 'Dividends']            


engine = APIClient(stocks_asset)


def __dir__():
    return ['engine']

__all__ = ['engine']



