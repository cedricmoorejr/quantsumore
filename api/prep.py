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

# Custom
from .market_utils import forexquery, equityquery, CurrencyQuery, ExchangeQuery, CoinQuery, SlugValidateQuery
from ..date_parser import dtparse
from ..web_utils import url_encode_decode, Mask


class identifier_validation:
    def __init__(self):
        self.validated_identifier = None
           
    def stock_ticker(self, stock_ticker, search_type="standard"):
        """ Validate a stock ticker symbol."""
        self.validated_identifier = None
        stock_ticker = stock_ticker.strip()
        if search_type == "standard":
            result = equityquery.search_symbol(stock_ticker)
            if not result:
                raise TypeError(f"Could not locate ticker symbol: {stock_ticker}")
        elif search_type == "yahoo":
            result = equityquery.search_yahoo_symbol(stock_ticker)
            if not result:
                raise TypeError(f"Could not locate ticker symbol: {stock_ticker}")
        elif search_type == "nasdaq":
            result = equityquery.search_nasdaq_symbol(stock_ticker)
            if not result:
                raise TypeError(f"Could not locate ticker symbol: {stock_ticker}")
        self.validated_identifier = stock_ticker
    
    def fx_currency(self, currency_pair, currency_dict_type="major"):
        """ Validate a single foreign exchange currency pair."""
        self.validated_identifier = None
        self.validated_identifier = forexquery.check(currency_pair=currency_pair, currency_dict_type=currency_dict_type)

    def crypto_slug_name(self, slug):
        """ Validate crypto currency coin slug name."""
        self.validated_identifier = None
        self.validated_identifier = SlugValidateQuery.validate(slug) 
         
    def __dir__(self):
        return ['stock_ticker', 'fx_currency', 'crypto_slug_name', 'validated_identifier']


def _normalize_dates(start_date, end_date=None, future_date_check=False, date_format="unix"):
    """
    Normalizes and validates start and end dates, ensuring they conform to specified constraints.

    This function processes input dates (either as string or datetime objects), verifies their
    chronological order, and optionally checks against future dates. It converts the dates to the
    specified format before returning them.

    Parameters:
    - start_date (str or datetime): The starting date of the period. Can be a string or datetime object.
    - end_date (str or datetime, optional): The ending date of the period. Can be a string or datetime object.
      Defaults to the current date if None.
    - future_date_check (bool, optional): If True, checks whether the start and end dates are in the future
      relative to the current date and time. Defaults to False.
    - date_format (str, optional): The format in which to return the dates. Can be 'unix' for Unix timestamp,
      'utc_unix', or a valid strftime format string. Defaults to 'unix'.
    """	
    if not end_date:
        end_date = dtparse.now(utc=True)
    else:
        if isinstance(end_date, str):
            end_date = dtparse.parse(end_date)
        
    if isinstance(start_date, str):
        start_date = dtparse.parse(start_date)  
        
    if start_date > end_date:
        raise ValueError("The start date must be before or equal to the end date.")
       
    if future_date_check:
        if start_date > dtparse.now(utc=True) or end_date > dtparse.now(utc=True):
            raise ValueError("Data not available on requested date. Please try another date.")

    if date_format == "unix":
        start_date = dtparse.unix_timestamp(start_date)
        end_date = dtparse.unix_timestamp(end_date)
        
    elif date_format == "utc_unix":
        start_date = dtparse.unix_timestamp(start_date, utc=True)
        end_date = dtparse.unix_timestamp(end_date, utc=True)
        
    else:
        start_date = start_date.strftime(date_format)
        end_date = end_date.strftime(date_format)            
            
    return start_date, end_date



## Equity
##------------------------------------------------------------------------
class Equity:
    def __init__(self):
        self.base_url_v1 = 'aHR0cHM6Ly9maW5hbmNlLnlhaG9vLmNvbS9xdW90ZS8='
        self.base_url_v2 = 'aHR0cHM6Ly9xdWVyeTEuZmluYW5jZS55YWhvby5jb20vdjgvZmluYW5jZS9jaGFydC8='
        self.base_url_v3 = 'aHR0cHM6Ly9xdWVyeTEuZmluYW5jZS55YWhvby5jb20vdjcvZmluYW5jZS9zcGFyaz9zeW1ib2xzPQ=='        
        self.base_url_v4 = 'aHR0cHM6Ly9hcGkubmFzZGFxLmNvbS9hcGkvY29tcGFueS8='          
        self.base_url_v5 = 'aHR0cHM6Ly9hcGkubmFzZGFxLmNvbS9hcGkvcXVvdGUv'         

    def _normalize_tickers(self, tickers):
        if isinstance(tickers, str):
            tickers = [tickers]
            [validate.stock_ticker(t) for t in tickers]
        elif isinstance(tickers, list):
            if not all(isinstance(ticker, str) for ticker in tickers):
                raise ValueError("All elements in the ticker list must be strings.")
        else:
            raise ValueError("Input must be either a string or a list of strings.")
        normalized_tickers = list(dict.fromkeys(ticker.upper() for ticker in tickers))
        [validate.stock_ticker(t) for t in normalized_tickers]
        return normalized_tickers

    def _construct_url(self, identifier, period1=None, period2=None, financial_period=None, financial_interval=None, Type=None):    
        if period1 is None and period2 is None:
            if Type == "yahoo_spark":
                ticker = url_encode_decode.encode_str(i=identifier, chars_to_encode=",", join_char=",")
                return f"{Mask.format.chr(self.base_url_v3, 'format')}{ticker}&range=1d&interval={financial_interval}&indicators=close&includeTimestamps=true&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance"
            if Type == "nasdaq_company":
                selected_period = 'Quarterly' if financial_period == 'Quarterly' or financial_period is None else 'Annually'
                period = "2" if selected_period == 'Quarterly' else "1"
                return f"{Mask.format.chr(self.base_url_v4, 'format')}{identifier}/financials?frequency={period}"
            if Type == "div_payout":
                return f"{Mask.format.chr(self.base_url_v5, 'format')}{identifier}/dividends?assetclass=stocks"               
            return f"{Mask.format.chr(self.base_url_v1, 'format')}{identifier}/"
           
        url = (
            f"{Mask.format.chr(self.base_url_v2, 'format')}{identifier}?"
            "formatted=true&includeAdjustedClose=true&interval=1d&userYfid=false&lang=en-US&region=US"
            f"&period1={period1}&period2={period2}"
        )
        return url

    def make(self, query, *args, **kwargs):
        ticker = args[0] if len(args) > 0 else kwargs.get('ticker')
        start = kwargs.get('start', None)
        end = kwargs.get('end', None)
        ticker = self._normalize_tickers(ticker)
        urls = []

        if query.lower() == "profile":
            if isinstance(ticker, list):
                ticker = ticker[0]            
            return self._construct_url(identifier=ticker, period1=None, period2=None, financial_period=None, financial_interval=None, Type=None) + "profile/" 
           
        if query.lower() == "stats":
            if isinstance(ticker, list):
                ticker = ticker[0]             
            return self._construct_url(identifier=ticker, period1=None, period2=None, financial_period=None, financial_interval=None, Type=None)
           
        if query.lower() == "last":
            interval = kwargs.get('interval', '1m')
            return self._construct_url(identifier=ticker, period1=None, period2=None, financial_period=None, financial_interval=interval, Type="yahoo_spark")
           
        if query.lower() == "financials":
            period = kwargs.get('period', None)
            if isinstance(ticker, list):
                ticker = ticker[0]             
            return self._construct_url(identifier=ticker, period1=None, period2=None, financial_period=period, financial_interval=None, Type="nasdaq_company")
           
        if query.lower() == "dividend_history":
            if isinstance(ticker, list) and len(ticker) > 1:
                # If contains multiple currency_pairs
                for t in ticker:
                    urls.append(self._construct_url(identifier=t, period1=None, period2=None, financial_period=None, financial_interval=None, Type="div_payout"))
                return urls if len(urls) > 1 else urls[0]
            else:
                if isinstance(ticker, list):
                    ticker = ticker[0]                  
                return self._construct_url(identifier=ticker, period1=None, period2=None, financial_period=None, financial_interval=None, Type="div_payout") 
           
        if query.lower() == "price":
            if start and end:
                # start, end = self._normalize_dates(start, end)
                start, end = _normalize_dates(start, end)                
                for t in ticker:
                    urls.append(self._construct_url(identifier=t, period1=start, period2=end, financial_period=None, financial_interval=None, Type=None))
            else:
                for t in ticker:
                    urls.append(self._construct_url(t))
            return urls if len(urls) > 1 else urls[0]

    def __dir__(self):
        return ['make']




## Forex
##------------------------------------------------------------------------
class Forex:
    def __init__(self):
        self.major_currencies = forexquery.which.major()
        self.quote_base_url = "aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2ZvcmV4L3F1b3Rlcy8lNUU="
        self.interbank_base_url = "aHR0cHM6Ly93d3cubXRmeGdyb3VwLmNvbS9hcGkvcmF0ZXMvZ2V0TGl2ZUV4aGFuZ2VSYXRlLz9jdXJyZW5jaWVzPQ=="          
        self.historical_base_url = "aHR0cHM6Ly93d3cubXRmeGdyb3VwLmNvbS9hcGkvcmF0ZXMvZnJlcXVlbmN5UmF0ZUN1c3RvbS8="        
        self.bid_ask_url = "aHR0cHM6Ly9hcGkubmFzZGFxLmNvbS9hcGkvcXVvdGUv"            
        self.ccy = None        
       
    def _normalize_currencies(self, currencies, currency_dict_type="major"):
        currency_list = []
        if isinstance(currencies, str):
            currencies = [currencies]
        if isinstance(currencies, list):
            if not all(isinstance(currency, str) for currency in currencies):
                raise ValueError("All elements in the currency list must be strings.")
            for c in currencies:
                result = validate.fx_currency(c, currency_dict_type=currency_dict_type)
                if result is None: 
                    currency_list.append(validate.validated_identifier)
        else:
            raise ValueError("Input must be either a string or a list of strings.")
        normalized_currencies = list(dict.fromkeys(currency.upper() for currency in currency_list))
        return (normalized_currencies[0] if len(normalized_currencies) == 1 else normalized_currencies)         

    def _construct_url(self, identifier, include=None, exclude=None, period1=None, period2=None):
        if all(x is None for x in [period1, period2]):
            currencies = self.major_currencies
            # Check for currency only
            if len(re.sub(r'\s+', chr(32), identifier).strip()) == 3:
                if isinstance(include, str):
                    include = [include]
                if isinstance(exclude, str):
                    exclude = [exclude]
                if include:
                    currencies = [curr for curr in include if curr in currencies]
                elif exclude:
                    currencies = [curr for curr in currencies if curr not in exclude]
                else:
                    currencies.remove(identifier) if identifier in currencies else None
                currency_string = '%2C'.join(currencies)
                return f"{Mask.format.chr(self.interbank_base_url,'format')}{currency_string}&source={identifier}"
        formatted_start_date = period1.replace('/', '%2F')
        formatted_end_date = period2.replace('/', '%2F')
        return f"{Mask.format.chr(self.historical_base_url,'format')}?ratepair={identifier}&start_date={formatted_start_date}&end_date={formatted_end_date}"
       
    def make(self, query, *args, **kwargs):
        urls = []
        if query.lower() == "historical":
            currency_pair = args[0] if len(args) > 0 else kwargs.get('currency_pair')
            start = kwargs.get('start', None)
            end = kwargs.get('end', None)
            currency_pair = self._normalize_currencies(currency_pair)
            if start and end:
                startdate, enddate = _normalize_dates(start, end, future_date_check=True, date_format='%d/%m/%Y')                
            elif start and not end:
                startdate, enddate = _normalize_dates(start, start, future_date_check=True, date_format='%d/%m/%Y')                
            else:
                raise ValueError("Both start and end dates are required for historical data.")
            if isinstance(currency_pair, list) and len(currency_pair) > 1:
                # If contains multiple currency_pairs
                for c in currency_pair:
                    urls.append(self._construct_url(identifier=c, period1=startdate, period2=enddate))
                return urls if len(urls) > 1 else urls[0]
            else:
                return self._construct_url(identifier=currency_pair, period1=startdate, period2=enddate)  
               
        elif query.lower() == "interbank": 
            currency_code = args[0] if len(args) > 0 else kwargs.get('currency_code', None)
            if currency_code is None:
                raise ValueError("Currency code must be provided for 'interbank' queries.")
            include = args[1] if len(args) > 1 else kwargs.get('include', [])
            exclude = args[2] if len(args) > 2 else kwargs.get('exclude', [])
            include = [include] if isinstance(include, str) else include
            exclude = [exclude] if isinstance(exclude, str) else exclude
            currency_code = self._normalize_currencies(currency_code)
            if isinstance(currency_code, list) and len(currency_code) > 1:
                # If contains multiple currency codes we will skip include/exclude
                for c in currency_code:
                    urls.append(self._construct_url(identifier=c, include=None, exclude=None, period1=None, period2=None))
                return urls if len(urls) > 1 else urls[0]
            else:
                return self._construct_url(identifier=currency_code, include=include, exclude=exclude, period1=None, period2=None)           

        elif query.lower() == "bid_ask":
            currency_pair = args[0] if len(args) > 0 else kwargs.get('currency_pair')
            currency_pair = self._normalize_currencies(currency_pair, currency_dict_type="bchart")
            if isinstance(currency_pair, list) and len(currency_pair) > 1:
                # If contains multiple currency_pairs
                for c in currency_pair:
                    urls.append(f"{Mask.format.chr(self.bid_ask_url,'format')}{c}/summary?assetclass=currencies")
                return urls if len(urls) > 1 else urls[0]
            else:
                return f"{Mask.format.chr(self.bid_ask_url,'format')}{currency_pair}/summary?assetclass=currencies"
           
        elif query.lower() in ["convert", "current"]:               
            currency_pair = args[0] if len(args) > 0 else kwargs.get('currency_pair')
            validate.fx_currency(currency_pair, currency_dict_type="bchart")            
            self.ccy = validate.validated_identifier            
            return f"{Mask.format.chr(self.quote_base_url,'format')}{self.ccy}"

    def __dir__(self):
        return ['make'] 




## Crypto
##------------------------------------------------------------------------
class Crypto:
    def __init__(self):
        self.historical_base_url = "aHR0cHM6Ly9hcGkuY29pbm1hcmtldGNhcC5jb20vZGF0YS1hcGkvdjMuMS9jcnlwdG9jdXJyZW5jeS9oaXN0b3JpY2FsP2lkPQ=="        
        self.live_base_url = "aHR0cHM6Ly9hcGkuY29pbm1hcmtldGNhcC5jb20vZGF0YS1hcGkvdjMvY3J5cHRvY3VycmVuY3kvbWFya2V0LXBhaXJzL2xhdGVzdD9zbHVnPQ=="           

    def _normalize_slugs(self, slugs):
        if isinstance(slugs, str):
            slugs = [slugs]
            [validate.crypto_slug_name(s) for s in slugs]
        elif isinstance(slugs, list):
            if not all(isinstance(slug, str) for slug in slugs):
                raise ValueError("All elements in the slug list must be strings.")
        else:
            raise ValueError("Input must be either a string or a list of strings.")
           
        normalized_slugs = list(dict.fromkeys(slug.lower() for slug in slugs))
        return (normalized_slugs[0] if len(normalized_slugs) == 1 else normalized_slugs) 

    def _normalize_ids(self, ids):
        ID_list = []
        if isinstance(ids, str):
            ids = [ids]
        if isinstance(ids, list):
            if not all(isinstance(ID, str) for ID in ids):
                raise ValueError("All elements in the ID list must be strings.")
            for i in ids:
                result = validate.crypto_slug_name(i)
                if result is None: 
                    ID_list.append(validate.validated_identifier[1])
        else:
            raise ValueError("Input must be either a string or a list of strings.")
        normalized_ids = list(dict.fromkeys(ID for ID in ID_list))
        return (normalized_ids[0] if len(normalized_ids) == 1 else normalized_ids)  

    def _construct_url(self, identifier, baseCurrency=None, quoteCurrency=None, limit=100, exchange_type='all', period1=None, period2=None): 
        if all(x is None for x in [period1, period2]):
            # Live data request
            url = f"{Mask.format.chr(self.live_base_url, 'format')}{identifier}&start=1&limit={limit}&category=spot&centerType=all&sort=cmc_rank_advanced&direction=desc&spotUntracked=true"
            if baseCurrency:
                baseCurrencyID = CurrencyQuery.SymbolreturnID(baseCurrency)
                url += f'&baseCurrencyId={baseCurrencyID}'            
            if quoteCurrency:
                quoteCurrencyID = CurrencyQuery.SymbolreturnID(quoteCurrency)
                url += f'&quoteCurrencyId={quoteCurrencyID}'
            if exchange_type.lower() not in ['all', 'dex', 'cex']:
                exchange_type = 'all'
            url = url.replace("centerType=all", f'centerType={exchange_type.lower()}')
            return url           
        else:
            # Historical data request
            return f"{Mask.format.chr(self.historical_base_url, 'format')}{identifier}&convertId=2781&timeStart={period1}&timeEnd={period2}&interval=1d"

    def make(self, query, *args, **kwargs):
        urls = []
        
        if query.lower() == "historical":
            slug = args[0] if len(args) > 0 else kwargs.get('slug')
            if slug is None:
                raise ValueError("Slug name must be provided for 'historical' queries.")               
            start = kwargs.get('start', None)
            end = kwargs.get('end', None)    
            
            ID = self._normalize_ids(slug)

            if not isinstance(ID, list):
                ID = [str(ID)]
            else:
                ID = [str(i) for i in ID]
 
            if start:
                start, end = _normalize_dates(start, end, future_date_check=True, date_format="utc_unix") 
            else:
                raise ValueError("Both start and end dates are required for historical data.")
            for i in ID:
                urls.append(self._construct_url(identifier=i, period1=start, period2=end))
            return urls if len(urls) > 1 else urls[0]

        elif query.lower() == "live":
            slug = args[0] if len(args) > 0 else kwargs.get('slug')
            if slug is None:
                raise ValueError("Slug name must be provided for 'live' queries.")
            baseCurrencySymbol = args[1] if len(args) > 1 else kwargs.get('baseCurrencySymbol')
            quoteCurrencySymbol = args[2] if len(args) > 2 else kwargs.get('quoteCurrencySymbol')
            limit = args[3] if len(args) > 3 else kwargs.get('limit')
            exchangeType = args[4] if len(args) > 4 else kwargs.get('exchangeType')
            cryptoExchange = args[5] if len(args) > 5 else kwargs.get('cryptoExchange')
            
            slug = self._normalize_slugs(slug)

            if isinstance(slug, list) and len(slug) > 1:
                for s in slug:
                    urls.append(self._construct_url(identifier=s, baseCurrency=baseCurrencySymbol, quoteCurrency=quoteCurrencySymbol, limit=limit, exchange_type=exchangeType, period1=None, period2=None))
                return urls if len(urls) > 1 else urls[0]
            else:
                return self._construct_url(identifier=slug, baseCurrency=baseCurrencySymbol, quoteCurrency=quoteCurrencySymbol, limit=limit, exchange_type=exchangeType, period1=None, period2=None) 

    def __dir__(self):
        return ['make']





## Consumer Price Index
##------------------------------------------------------------------------
class CPI:
    def __init__(self):
        self.base_url_cpi = 'aHR0cHM6Ly9mcmVkLnN0bG91aXNmZWQub3JnL3Nlcmllcy8='

    def _construct_url(self, series_id):
        """Constructs URL based on series id."""
        return f"{Mask.format.chr(self.base_url_cpi, 'format')}{series_id}"
       
    def make(self, series_id, *args, **kwargs):
        if not series_id:
            raise ValueError("Series ID is required")
        return self._construct_url(series_id=series_id)
       
    def __dir__(self):
        return ['make']




## Treasury
##------------------------------------------------------------------------
class Treasury_gov:
    def __init__(self):
        self.base_url = 'aHR0cHM6Ly9ob21lLnRyZWFzdXJ5Lmdvdi9yZXNvdXJjZS1jZW50ZXIvZGF0YS1jaGFydC1jZW50ZXIvaW50ZXJlc3QtcmF0ZXMvVGV4dFZpZXc/dHlwZT0='

    def _construct_url(self, identifier, period=None):
        today = dtparse.nowCT()
        date_value_month = today.strftime('%Y%m')
        date_value_high = today.year
        date_value_low = 1990
        date_value_month_low = 199001

        if identifier == 'tbill':
            identifier = 'daily_treasury_bill_rates'
            url = f"{Mask.format.chr(self.base_url,'format')}{identifier}"
            if not period:
                return url + f'&field_tdr_date_value_month={date_value_month}'

            else:
                if str(period).lower()  == 'cy':
                    return url + f'&field_tdr_date_value={date_value_high}'
                elif date_value_low <= int(period) <= date_value_high:
                    return url + f'&field_tdr_date_value={period}'
                elif date_value_month_low <= int(period) <= int(date_value_month):
                    return url + f'&field_tdr_date_value_month={period}'
                
        elif identifier == 'tyield':
            identifier = 'daily_treasury_yield_curve'
            url = f"{Mask.format.chr(self.base_url,'format')}{identifier}"
            if not period:
                return url + f'&field_tdr_date_value_month={date_value_month}'

            else:
                if str(period).lower()  == 'cy':
                    return url + f'&field_tdr_date_value={date_value_high}'
                elif date_value_low <= int(period) <= date_value_high:
                    return url + f'&field_tdr_date_value={period}'
                elif date_value_month_low <= int(period) <= int(date_value_month):
                    return url + f'&field_tdr_date_value_month={period}'
    
    def make(self, query, *args, **kwargs):
        period = args[0] if len(args) > 0 else kwargs.get('period', None)      

        if query.lower() == "tbill":
            return self._construct_url(identifier='tbill', period=period)
        
        elif query.lower() == "tyield":
            return self._construct_url(identifier='tyield', period=period)

    def __dir__(self):
        return ['make']



validate = identifier_validation()
crypto_asset = Crypto()
fx_asset = Forex()
stocks_asset = Equity()
cpi_asset = CPI()
treasuryasset = Treasury_gov()


def __dir__():
    return ['stocks_asset', 'fx_asset', 'crypto_asset', 'cpi_asset', 'treasuryasset']

__all__ = ['stocks_asset', 'fx_asset', 'crypto_asset', 'cpi_asset', 'treasuryasset']

