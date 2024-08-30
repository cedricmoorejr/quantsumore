import re

# Custom
from .market_utils import currencyquery
from ..tools.tool import dtparse
from ..tools.maskoff import Mask
from ..configuration.generatedcrypto import CurrencyQuery, ExchangeQuery, CoinQuery

class identifier_validation:
    def __init__(self):
        self.validated_identifier = None
           
    def stock_ticker(self, stock_ticker):
        """ Validate a stock ticker symbol."""
        self.validated_identifier = None
        if not isinstance(stock_ticker, str):
            raise TypeError("Please enter a valid stock ticker symbol.")
        stock_ticker = stock_ticker.strip()
        if len(stock_ticker) == 0:
            raise ValueError("Please enter a valid stock ticker symbol.")
        if not 1 <= len(stock_ticker) <= 5:
            raise ValueError("Stock ticker symbol must be between 1 and 5 characters.")
        self.validated_identifier = stock_ticker

    def fx_currency(self, currency_pair, currency_dict_type="major"):
        """ Validate a foreign exchange currency pair."""
        self.validated_identifier = None
        tokens = currencyquery.tokenize(currency_pair)
        if not tokens:
            raise TypeError("Please enter a valid currency pair as a string or a list of strings.")
        token_len = len(tokens)
        validated = []
        for t in tokens:
            tok = currencyquery.query(t, query_type=currency_dict_type, ret_type="code")
            if tok:
                validated.append(tok)
        if len(validated) == token_len:
            self.validated_identifier = validated
        if not (isinstance(self.validated_identifier, list) and
                all(isinstance(item, str) for item in self.validated_identifier)):
            raise ValueError("Invalid currency. Currently, the only currencies accepted are from: " +
                  ", ".join(currencyquery.which.major()) + ". Please enter a valid currency.")
        if len(self.validated_identifier) == 0:
            raise ValueError("Please enter a valid currency pair.")
        if self.validated_identifier is None:
            raise ValueError(f"{currency_pair} is not in the list of accepted currency pairs.") 
          
    def crypto_slug_name(self, slug):
        """ Validate crypto currency coin slug name."""
        self.validated_identifier = None
        if not isinstance(slug, str):
            raise TypeError("Please enter a valid coin slug and NOT a symbol.")
        slug = slug.lower()
        slug = CoinQuery.Slug(slug=slug)
        if len(slug) == 0:
            raise ValueError("Please enter a valid coin slug and NOT a symbol.")
        found_slug = slug[0]['slug']
        cryptoID = slug[0]['id']
        self.validated_identifier = (found_slug, cryptoID)
         
    def __dir__(self):
        return ['stock_ticker', 'fx_currency', 'crypto_slug_name', 'validated_identifier']




class Equity:
    def __init__(self):
        self.base_url = "aHR0cHM6Ly9maW5hbmNlLnlhaG9vLmNvbS9xdW90ZS8="

    def _construct_url(self, identifier, period1=None, period2=None):
        if period1 is None or period2 is None:
            return f"{Mask.format.chr(self.base_url, 'format')}{identifier}/"
        url = f"{Mask.format.chr(self.base_url, 'format')}{identifier}/history/?period1={period1}&period2={period2}"
        return url

    def _prepare_dates(self, start_date, end_date):
        if isinstance(start_date, str):
            start_date = dtparse.parse(start_date)
        if isinstance(end_date, str):
            end_date = dtparse.parse(end_date)
        if start_date > end_date:
            raise ValueError("The start date must be before or equal to the end date.")
        period1 = dtparse.unix_timestamp(start_date)
        period2 = dtparse.unix_timestamp(end_date)
        return period1, period2

    def make(self, *args, **kwargs):
        query = args[1] if len(args) > 1 else kwargs.get('query')        
        ticker = args[0] if len(args) > 0 else kwargs.get('ticker')
        start = kwargs.get('start', None)
        end = kwargs.get('end', None)  
        ticker = ticker.upper()
        validate.stock_ticker(ticker)
        if query.lower()  == "profile":
            return f"{Mask.format.chr(self.base_url, 'format')}{ticker}/profile/"
        elif query.lower()  == "stats":
            return f"{Mask.format.chr(self.base_url, 'format')}{ticker}/"
        elif query.lower()  == "price":
            if start and end:
                period1, period2 = self._prepare_dates(start, end)
                return self._construct_url(ticker, period1, period2)
            return f"{Mask.format.chr(self.base_url, 'format')}{ticker}/"
           
    def __dir__(self):
        return ['make']





class Forex:
    def __init__(self):
        self.major_currencies = currencyquery.which.major()
        self.quote_base_url = "aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2ZvcmV4L3F1b3Rlcy8lNUU="
        self.interbank_base_url = "aHR0cHM6Ly93d3cubXRmeGdyb3VwLmNvbS9hcGkvcmF0ZXMvZ2V0TGl2ZUV4aGFuZ2VSYXRlLz9jdXJyZW5jaWVzPQ=="          
        self.historical_base_url = "aHR0cHM6Ly93d3cubXRmeGdyb3VwLmNvbS9hcGkvcmF0ZXMvZnJlcXVlbmN5UmF0ZUN1c3RvbS8="        
        self.ccy = None        

    @staticmethod
    def join_currency(currency):
        if isinstance(currency, list) and len(currency) == 2:
            if all(isinstance(item, str) and len(item) == 3 for item in currency):
                return ''.join(currency)
        return currency
    
    def _construct_url(self, identifier, include=None, exclude=None, period1=None, period2=None):
        if period1 is None or period2 is None:
            currencies = self.major_currencies
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
            else:
                return f"{Mask.format.chr(self.quote_base_url,'format')}{identifier}"
        formatted_start_date = period1.replace('/', '%2F')
        formatted_end_date = period2.replace('/', '%2F')
        return f"{Mask.format.chr(self.historical_base_url,'format')}?ratepair={identifier}&start_date={formatted_start_date}&end_date={formatted_end_date}"
    
    def _prepare_dates(self, start_date, end_date):
        if isinstance(start_date, str):
            start_date = dtparse.parse(start_date)
        if isinstance(end_date, str):
            end_date = dtparse.parse(end_date)
        if start_date > end_date:
            raise ValueError("The start date must be before or equal to the end date.")
        if start_date > dtparse.now(utc=True) or end_date > dtparse.now(utc=True):
            raise ValueError("Rates not available on requested date. Please try another date.")  
        period1 = start_date.strftime('%d/%m/%Y')
        period2 = end_date.strftime('%d/%m/%Y')
        return period1, period2

    def make(self, *args, **kwargs):
        if 'query' not in kwargs:
            raise ValueError("A query type (e.g., 'historical', 'convert', 'current', or 'interbank') must be provided.")
        query = kwargs['query'].lower()
        if query == "historical":
            currency_pair = args[0] if len(args) > 0 else kwargs.get('currency_pair')
            start = kwargs.get('start', None)
            end = kwargs.get('end', None)            
            validate.fx_currency(currency_pair, currency_dict_type="major")
            self.ccy = self.join_currency(validate.validated_identifier)
            startdate, enddate = self._prepare_dates(start, end)
            return self._construct_url(identifier=self.ccy, period1=startdate, period2=enddate)
        elif query == "interbank": 
            currency_code = args[0] if len(args) > 0 else kwargs.get('currency_code', None)
            if currency_code is None:
                raise ValueError("Currency code must be provided for 'interbank' queries.")
            include = args[1] if len(args) > 1 else kwargs.get('include', [])
            exclude = args[2] if len(args) > 2 else kwargs.get('exclude', [])
            include = [include] if isinstance(include, str) else include
            exclude = [exclude] if isinstance(exclude, str) else exclude
            validate.fx_currency(currency_code, currency_dict_type="major")            
            self.ccy = self.join_currency(validate.validated_identifier)
            return self._construct_url(identifier=currency_code, include=include, exclude=exclude)
        elif query in ["convert", "current"]:               
            currency_pair = args[0] if len(args) > 0 else kwargs.get('currency_pair')
            validate.fx_currency(currency_pair, currency_dict_type="bchart")            
            self.ccy = self.join_currency(validate.validated_identifier)
            return self._construct_url(identifier=self.ccy)

    def __dir__(self):
        return ['make'] 


class Crypto:
    def __init__(self):
        self.historical_base_url = "aHR0cHM6Ly9hcGkuY29pbm1hcmtldGNhcC5jb20vZGF0YS1hcGkvdjMuMS9jcnlwdG9jdXJyZW5jeS9oaXN0b3JpY2FsP2lkPQ=="        
        self.live_base_url = "aHR0cHM6Ly9hcGkuY29pbm1hcmtldGNhcC5jb20vZGF0YS1hcGkvdjMvY3J5cHRvY3VycmVuY3kvbWFya2V0LXBhaXJzL2xhdGVzdD9zbHVnPQ=="           
        self.slug = None 
        self.id = None        
        
    def _construct_url(self, identifier, baseCurrency=None, quoteCurrency=None, limit=100, exchange_type='all', period1=None, period2=None): 
        if period1 is None or period2 is None:
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
    
    def _prepare_dates(self, start_date, end_date):
        if not end_date:            
            end_date = dtparse.now(utc=True, as_unix=True)
        if isinstance(start_date, str):
            start_date = dtparse.parse(start_date, to_unix_timestamp=True)
        if isinstance(end_date, str):
            end_date = dtparse.parse(end_date, to_unix_timestamp=True)
        if start_date > end_date:
            raise ValueError("The start date must be before or equal to the end date.")
        current_unix_time = dtparse.now(utc=True, as_unix=True)
        if start_date > current_unix_time or end_date > current_unix_time:
            raise ValueError("Rates not available on requested date. Please try another date.")
        return start_date, end_date

    def make(self, query_type, *args, **kwargs):
        query_type = query_type.lower()

        if query_type == "historical":
            slug = args[0] if len(args) > 0 else kwargs.get('slug')
            start = kwargs.get('start', None)
            end = kwargs.get('end', None)
            validate.crypto_slug_name(slug)
            _, self.id = validate.validated_identifier
            startdate, enddate = self._prepare_dates(start, end)
            return self._construct_url(identifier=self.id, period1=startdate, period2=enddate)

        elif query_type == "live":
            slug, baseCurrencySymbol, quoteCurrencySymbol, limit, exchangeType = args
            cryptoExchange = kwargs.get('cryptoExchange', None)
            validate.crypto_slug_name(slug)
            self.slug, _ = validate.validated_identifier
            return self._construct_url(identifier=self.slug, baseCurrency=baseCurrencySymbol, quoteCurrency=quoteCurrencySymbol, limit=limit, exchange_type=exchangeType)

    def __dir__(self):
        return ['make']


class CPI:
    def __init__(self):
        self.base_url_cpi = 'aHR0cHM6Ly9mcmVkLnN0bG91aXNmZWQub3JnL3Nlcmllcy8='

    def _construct_url(self, series_id):
        """Constructs URL based on series id."""
        return f"{Mask.format.chr(self.base_url_cpi, 'format')}{series_id}"
       
    def make(self, *args, **kwargs):
        series_id = args[0] if args else kwargs.get('series_id')
        if not series_id:
            raise ValueError("Series ID is required")
        return self._construct_url(series_id=series_id)
       
    def __dir__(self):
        return ['make']



class Treasury_gov:
    def __init__(self):
        self.base_url = 'aHR0cHM6Ly9ob21lLnRyZWFzdXJ5Lmdvdi9yZXNvdXJjZS1jZW50ZXIvZGF0YS1jaGFydC1jZW50ZXIvaW50ZXJlc3QtcmF0ZXMvVGV4dFZpZXc/dHlwZT0='

    def _construct_url(self, identifier, period=None):
        """
        Parameters:
            identifier (str): The type of data to query. Options are:
                - 'tbill': Daily Treasury Bill Rates
                - 'tyield': Daily Treasury Yield Curve Rates
            period (str|int|None): The time period for the data query. Formats are:
                - 'CY' (str): Refers to the current year.
                - YYYY (int): A specific year (e.g., 2021).
                - YYYYMM (int): A specific month and year (e.g., 202308).
                - None: If no period is specified, the current month of the current year is used as the default period.
        """
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
    
    def make(self, *args, **kwargs):
        query = args[0] if len(args) > 0 else kwargs.get('query')  
        period = kwargs.get('period', None)       

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
