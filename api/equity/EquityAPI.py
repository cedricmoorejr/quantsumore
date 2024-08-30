from copy import deepcopy

# Custom
from ..._http.connection import http_client
from ..prep import stocks_asset
from .parse import stock
from ...render.d import Table, Border, Grid
# from types._types import DataAnalysis



class APIClient:
    def __init__(self, asset):
        self.asset = asset  
        self.data_cache = {}
        self.historical_cache = {}         
        
    def _ensure_company_description_period(self, profile):
        if 'Company Description' in profile:
            description = profile['Company Description']
            if description and description.strip():
                if not description.endswith('.'):
                    profile['Company Description'] = description.strip() + '.'
        return profile

    def _make_request(self, url):
        """ Note: http_client is a Singleton class instance."""     	
        http_client.update_base_url(url)
        response = http_client.make_request(params={})
        html_content = response["response"]
        return html_content if html_content else None

    def _get_or_fetch_data(self, ticker):
        if ticker in self.data_cache:
            return self.data_cache[ticker]
        else:
            make_method = getattr(self.asset, 'make')
            url = make_method(query='profile', ticker=ticker)
            html_content = self._make_request(url)
            if html_content:
                obj = stock.profile(html_content)
                data = obj.DATA()
                data = self._ensure_company_description_period(data)
                self.data_cache[ticker] = data
                return data
            else:
                return None

    def clear_cache(self, ticker=None):
        if ticker:
            self.data_cache.pop(ticker, None)
            self.historical_cache = {key: val for key, val in self.historical_cache.items() if key[0] != ticker}
        else:
            self.data_cache.clear()
            self.historical_cache.clear()

    def CompanyBio(self, ticker, verbose=True):
        """
        Provides an overview or summary of a company's information based on its ticker symbol.

        This method retrieves and displays information about a company identified by its ticker symbol.
        It returns the company's description and, if the `verbose` parameter is set to True, displays the
        company's name and description using a styled border.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose information is to be retrieved.

        verbose : bool, optional (default=True)
            If set to True, the method displays the company's name and description using a bordered style.
            If set to False, only the company description is returned as a string.

        Returns:
        -------
        str or None
            Returns the company description as a string if `verbose` is False. If `verbose` is True,
            the description is displayed with a border, and the method returns None. Returns None if no
            data is found for the given ticker symbol.
        """    	
        data = self._get_or_fetch_data(ticker)
        if data:
            companyName = data['Company Name']
            companyDescription = data['Company Description']
            
            if verbose:
                bd = Border(companyName, companyDescription)
                bd.display()
                return
            return companyDescription
        return None        
       
    def CompanyExecutives(self, ticker, verbose=True):
        """
        Provides information about a company's executives based on its ticker symbol.

        This method retrieves and displays information about the executives of a company identified
        by its ticker symbol. If the `verbose` parameter is set to True, the information is displayed
        in a tabular format. Otherwise, the data is returned as a list or dictionary.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company whose executive information is to be retrieved.

        verbose : bool, optional (default=True)
            If set to True, the method displays the list of company executives in a tabular format.
            If set to False, the list of executives is returned as a raw data structure (e.g., list or
            dictionary).

        Returns:
        -------
        list or dict or None
            Returns the list or dictionary of company executives if `verbose` is False. If `verbose` is
            True, the list is displayed in a tabular format, and the method returns None. Returns None if
            no data is found for the given ticker symbol.
        """    	
        data = self._get_or_fetch_data(ticker)
        if data:
            companyExecs = data['Company Executives']
            
            if verbose:
                db = Table(companyExecs)
                db.display()
                return
            return companyExecs
        return None        
       
    def CompanyDetails(self, ticker, verbose=True):
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

        verbose : bool, optional (default=True)
            If set to True, the method displays the company details in a tabular format.
            If set to False, the details are returned as a raw data structure (e.g., list or dictionary).

        Returns:
        -------
        dict or None
            Returns a dictionary containing the company details if `verbose` is False. If `verbose` is
            True, the details are displayed in a tabular format, and the method returns None. Returns
            None if no data is found for the given ticker symbol.
        """    	
        data = self._get_or_fetch_data(ticker)
        if data:
            companyDetails = data['Company Details']
            if verbose:
                db = Table(companyDetails)
                db.display()
                return
            return companyDetails
        return None

    def Stats(self, ticker, verbose=True):
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

        verbose : bool, optional (default=True)
            If set to True, the method displays the statistical information in a grid or chart format.
            If set to False, the data is returned as a dictionary or structured data.

        Returns:
        -------
        dict or None
            Returns a dictionary containing statistical data if `verbose` is False. If `verbose` is
            True, the data is displayed in a grid format, and the method returns None. Returns None if
            no data is found for the given ticker symbol.
        """    	
        make_method = getattr(self.asset, 'make')
        url = make_method(query='stats', ticker=ticker)
        html_content = self._make_request(url)
        if html_content:
            obj = stock.quote_statistics(html_content)
            chart_title, stats = obj.DATA()
            
            if verbose:
                dg = Grid(statistics=stats, Title=chart_title)
                dg.display()
                return
            return stats
        return None           

    def sHistorical(self, ticker, start, end):
        """
        Retrieves historical stock price data for a company based on its ticker symbol and a specified date range.

        This method fetches historical price data for a company identified by its ticker symbol over a given
        date range. The data includes the date, opening price, highest price, lowest price, closing price,
        adjusted closing price, and trading volume for each trading day within the specified range.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the company for which historical data is to be retrieved.

        start : str
            The start date for the historical data in a format 'YYYY-MM-DD'. This date is inclusive.

        end : str
            The end date for the historical data in a format 'YYYY-MM-DD'. This date is inclusive.

        Returns:
        -------
        pandas.DataFrame or None
            Returns a DataFrame containing historical price data for each trading day in the specified date range.
            Each row represents a trading day, with columns for the date, open, high, low, close, adjusted close,
            and volume. Returns None if no data is found for the given ticker symbol or if the data request fails.

        Raises:
        ------
        ValueError
            If either the start or end date is not provided, a ValueError is raised.
        """    	
        cache_key = (ticker, start, end)
        if cache_key in self.historical_cache:
            return self.historical_cache[cache_key]
        else:
            if start is None or end is None:
                raise ValueError("Start and end dates must be provided for historical data requests.")
            make_method = getattr(self.asset, 'make')
            url = make_method(query='price', ticker=ticker, start=start, end=end)
            html_content = self._make_request(url)
            if html_content:
                obj = stock.historical(html_content)
                historical_data = obj.DATA()
                self.historical_cache[cache_key] = historical_data
                return historical_data
            else:
                return None

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
        make_method = getattr(self.asset, 'make')
        url = make_method(query='price', ticker=ticker)
        html_content = self._make_request(url)
        if html_content:
            obj = stock.latest(html_content)
            return obj.DATA()

    def __dir__(self):
        return ['CompanyBio','CompanyExecutives', 'CompanyDetails', 'Stats', 'sHistorical', 'sLatest', 'clear_cache']            
            
            
            

engine = APIClient(stocks_asset)


def __dir__():
    return ['engine']

__all__ = ['engine']


