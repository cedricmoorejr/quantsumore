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



import time
import datetime
import re
import csv
from io import StringIO
import sqlite3
import unicodedata

# Custom
from ..sys_utils import filePaths, JSON, SQLiteDBHandler
from .._http.response_utils import locKeyInStructure, locMultipleKeyInStructure



## Equity Utils
##=================================================================================================================================
__STOCK_TICKERS_FILE = "\\stock_tickers.txt"
class equityquery:
    _registry = {}
    configuration_path = None

    def __init__(self, symbol, company, exchange, yahoo_mapping, nasdaq_mapping):
        self.symbol = symbol
        self.company = company
        self.exchange = exchange
        self.yahoo_mapping = yahoo_mapping
        self.nasdaq_mapping = nasdaq_mapping
        equityquery._registry[symbol] = self

    def __repr__(self):
        return (f"equityquery(Symbol={self.symbol}, Company={self.company}, "
                f"Exchange={self.exchange}, yahoo_mapping={self.yahoo_mapping}, "
                f"nasdaq_mapping={self.nasdaq_mapping})")

    @staticmethod
    def initial_symbol_check(symbol):
        """Check if the symbol length is within the allowed range, contains no digits, and is not None."""
        if symbol is None:
            return False
        if not isinstance(symbol, str):
            return False
        if len(symbol) > 0 and len(symbol) <= 6:
            return not any(char.isdigit() for char in symbol)
        return False

    @classmethod
    def search_symbol(cls, symbol):
        """Search for a symbol in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symbol.lower()
        return any(stock.symbol.lower() == search_symbol_lower for stock in cls._registry.values())

    @classmethod
    def search_yahoo_symbol(cls, symbol):
        """Search for a symbol specifically in yahoo_mapping in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symbol.lower()
        return any(stock.yahoo_mapping.lower() == search_symbol_lower for stock in cls._registry.values())

    @classmethod
    def search_nasdaq_symbol(cls, symboll):
        """Search for a symbol specifically in nasdaq_mapping in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symboll.lower()
        return any(stock.nasdaq_mapping.lower() == search_symbol_lower for stock in cls._registry.values())

    @classmethod
    def initialize_directory(cls, directory="configuration"):
        # filePaths.trace() retrieves the full path
        cls.configuration_path = filePaths.trace(directory=directory)
        return cls.configuration_path

    @classmethod
    def load_data(cls, file_name):
        if cls.configuration_path is None:
            cls.initialize_directory()  # Initialize with default directory if not already set
        full_path = cls.configuration_path + file_name
        # filePaths.extract() reads the file and returns its content
        data = filePaths.extract(full_path, silent=False)
        cls.initialize_from_file(data)

    @classmethod
    def initialize_from_file(cls, data):
        f = StringIO(data)
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row:
                cls(*row)

# Load the data from a specified file
equityquery.load_data(file_name=__STOCK_TICKERS_FILE)






## Crypto Utils
##=================================================================================================================================
__CRYPTO_JSON_CONFIG_FILE = 'crypto.json'
__CRYPTO_DATABASE_FILE = 'crypto.db'
class Query:
    def __init__(self, file=None):
        self.file = file

    class Currency:
        def __init__(self, file):
            self.handler = JSON(filename=file)                   
            self._data = None

        @property
        def data(self):
            if self._data is None:
                json_data = self.handler.load(key='pairs')
                self._data = [
                    {**currency_info, 'currency': currency_name}
                    for currency_name, currency_info in json_data.items()
                ] if json_data else []
            return self._data

        def ID(self, qID):
            return [ccy for ccy in self.data if str(ccy['currencyId']) == str(qID)]

        def Symbol(self, symbol):
            symbol = symbol.lower()
            return [ccy for ccy in self.data if ccy['currencySymbol'].lower() == symbol]

        def SymbolreturnID(self, symbol):
            symbol = symbol.lower()
            for ccy in self.data:
                if ccy['currencySymbol'].lower() == symbol:
                    return ccy['currencyId']
            return None
           
        def __dir__(self):
            return ['ID', 'Symbol', 'SymbolreturnID', 'data']  

    class Exchange:
        def __init__(self, file):
            self.handler = JSON(filename=file)
            self._data = None

        @property
        def data(self):
            if self._data is None:
                json_data = self.handler.load(key='crypto_exchanges')
                self._data = list(json_data.values()) if json_data else []
            return self._data

        def ID(self, exchange_id):
            exch = str(exchange_id)
            return [exchange for exchange in self.data if exchange['exchangeId'] == exch]

        def Name(self, exchange_name):
            exchange_name = exchange_name.lower()
            return [exchange for exchange in self.data if exchange['exchangeName'].lower() == exchange_name]

        def Slug(self, exchange_slug):
            exchange_slug = exchange_slug.lower()
            return [exchange for exchange in self.data if exchange['exchangeSlug'].lower() == exchange_slug]

        def FindID(self, identifier):
            identifier = identifier.lower()
            for exchange in self.data:
                if exchange['exchangeName'].lower() == identifier or exchange['exchangeSlug'].lower() == identifier:
                    return int(exchange['exchangeId'])
            return None

        def __dir__(self):
            return ['ID', 'Name', 'Slug', 'FindID', 'data']        

    class Coin:
        def __init__(self, file):
            self.db_path = SQLiteDBHandler(file).path  
            self.cache = {
                'ID': {},
                'Name': {},
                'Slug': {},
                'ListSlugs': None
            }
        def append_active_condition(self, query):
            """Append an is_active = 1 condition to the WHERE clause in a query."""
            if 'WHERE' in query:
                return query + ' AND is_active = 1'
            else:
                return query + ' WHERE is_active = 1'

        def case_sensitive_search(self, word_to_find, word_to_check):
            return word_to_find == word_to_check
           
        def execute_query(self, query, params):
            query = self.append_active_condition(query)
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
            except sqlite3.Error as e:
                return []

        @staticmethod
        def normalize_string(input_string):
            """Normalize a string by removing special characters and accents but keep the case intact."""
            nfkd_form = unicodedata.normalize('NFKD', input_string)
            ascii_string = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
            return re.sub(r'[^\w\s]', '', ascii_string)

        def ID(self, crypto_id):
            # Check cache first
            if crypto_id in self.cache['ID']:
                return self.cache['ID'][crypto_id]
            query = 'SELECT * FROM cryptos WHERE id = ?'
            result = self.execute_query(query, (crypto_id,))
            # Cache the result
            self.cache['ID'][crypto_id] = result
            return result

        def Name(self, name):
            # Check cache first
            if name in self.cache['Name']:
                return self.cache['Name'][name]
            normalized_name = self.normalize_string(name)
            query = 'SELECT * FROM cryptos WHERE name LIKE ?'
            data = self.execute_query(query, (f'%{normalized_name}%',))
            filtered_data = [item for item in data if self.case_sensitive_search(name, item['name'])]
            # Cache the result
            self.cache['Name'][name] = filtered_data
            return filtered_data

        def Slug(self, slug):
            slug = slug.lower()
            # Check cache first
            if slug in self.cache['Slug']:
                return self.cache['Slug'][slug]
            query = 'SELECT * FROM cryptos WHERE slug = ?'
            result = self.execute_query(query, (slug,))
            # Cache the result
            self.cache['Slug'][slug] = result
            return result

        def ListSlugs(self):
            # Cache ListSlugs globally, as it has no parameters
            if self.cache['ListSlugs'] is not None:
                return self.cache['ListSlugs']
            query = 'SELECT name, symbol, slug FROM cryptos'
            result = self.execute_query(query, ())
            # Cache the result
            self.cache['ListSlugs'] = result
            return result

        def __dir__(self):
            return ['ID', 'Name', 'Slug', 'ListSlugs']


        def createValidator(self):
            return Query.Coin.ValidateSlug(self)

        class ValidateSlug:
            def __init__(self, coin):
                self.coin = coin
                self.validated_slug = None
                self.validated_slug_id = None                

            def _extract(self, data, key):
                return locKeyInStructure(data, target_key=key, value_only=True, first_only=True, return_all=False)

            def validate(self, slug):
                if not isinstance(slug, str):
                    raise TypeError("Please enter a valid coin slug and NOT a symbol.")
                
                slug = slug.lower()
                data = self.coin.Slug(slug)
                result = locMultipleKeyInStructure(data, target_keys=["slug", "id"], value_only=False, first_only=False, return_all=False)
                if result:
                    if len(result) == 2:
                        SLUG = self._extract(result, "slug")
                        ID = self._extract(result, "id")                        
                        self.validated_slug = SLUG
                        self.validated_slug_id = ID
                        return (SLUG, ID)
                    else:
                        raise ValueError("Id or slug name not found! Check the slug name you entered.")
                else:
                    raise ValueError("Please enter a valid coin slug and NOT a symbol.")


# Create an instance of ExchangeQuery, CurrencyQuery, and db query
query = Query()
CurrencyQuery = query.Currency(file=__CRYPTO_JSON_CONFIG_FILE)
ExchangeQuery = query.Exchange(file=__CRYPTO_JSON_CONFIG_FILE)
CoinQuery = query.Coin(file=__CRYPTO_DATABASE_FILE)
SlugValidateQuery = CoinQuery.createValidator()






## Forex Utils
##=================================================================================================================================
major_currencies = {
    'AUD': 'Australian Dollar', 'CAD': 'Canadian Dollar', 'CHF': 'Swiss Franc', 'CNY': 'Chinese Yuan Renminbi', 'CZK': 'Czech Koruna',
    'DKK': 'Danish Kroner', 'EUR': 'Euro', 'GBP': 'Pound Sterling', 'HKD': 'Hong Kong Dollar', 'HRK': 'Croatia Kuna',
    'HUF': 'Hungary Forint', 'ILS': 'Israel Shekel', 'INR': 'Indian Rupee', 'JPY': 'Japanese Yen', 'MXN': 'Mexican Peso',
    'NZD': 'New Zealand Dollar', 'PLN': 'Polish Zloty', 'SEK': 'Swedish Kroner', 'USD': 'US Dollar', 'ZAR': 'South African Rand'
}
bchart_currencies = {
    'AFN': 'Afghan Afghanis', 'DZD': 'Algerian Dinar', 'ARS': 'Argentine Peso', 'AMD': 'Armenia Drams', 'AWG': 'Aruba Guilder',
    'AUD': 'Australian Dollar', 'BSD': 'Bahamian Dollar', 'BHD': 'Bahrain Dinar', 'BDT': 'Bangladesh Taka', 'BBD': 'Barbados Dollars',
    'LSL': 'Basotho Loti', 'BYR': 'Belarus Rubles', 'BZD': 'Belize Dollars', 'BMD': 'Bermudian Dollar', 'BTN': 'Bhutanese Ngultrum',
    'BOB': 'Bolivia Bolivianos', 'BAM': 'Bosnian Marka', 'BWP': 'Botswana Pula', 'BRL': 'Brazilian Real', 'GBP': 'British Pound',
    'BND': 'Brunei Darussalam Dollars', 'BGN': 'Bulgarian Lev', 'BIF': 'Burundi Francs', 'KHR': 'Cambodia Riels', 'CAD': 'Canadian Dollar',
    'CVE': 'Cape Verde Escudos', 'KYD': 'Caymanian Dollar', 'XAF': 'Central African Cfa Franc Beac', 'XOF': 'Cfa Franc', 'XPF': 'Cfp Franc',
    'CLP': 'Chilean Peso', 'CNH': 'Chinese Offshore Spot', 'CNY': 'Chinese Yuan', 'COP': 'Colombian Peso', 'KMF': 'Comorian Franc',
    'CDF': 'Congolese Franc', 'CRC': 'Costa Rica Colones', 'HRK': 'Croatian Kuna', 'CUP': 'Cuba Pesos', 'CYP': 'Cyprus Pound',
    'CZK': 'Czech Koruna', 'DKK': 'Danish Krone', 'DJF': 'Djibouti Francs', 'DOP': 'Dominican Peso', 'XCD': 'East Caribbean Dollar',
    'EGP': 'Egyptian Pound', 'SVC': 'El Salvador Colones', 'EEK': 'Estonian Kroon', 'ETB': 'Ethiopia Birr', 'EUR': 'Euro',
    'FJD': 'Fiji Dollar', 'GMD': 'Gambia Dalasi', 'GEL': 'Georgian Lari', 'GHS': 'Ghanaian Cedi', 'XAU': 'Gold',
    'GTQ': 'Guatemala Quetzal', 'GNF': 'Guinean Franc', 'GYD': 'Guyanese Dollar', 'HTG': 'Haiti Gourdes', 'HNL': 'Honduras Lempira',
    'HKD': 'Hong Kong Dollar', 'HUF': 'Hungarian Forint', 'ISK': 'Icelandic Krona', 'XDR': 'Imf Drawing Rights', 'INR': 'Indian Rupee',
    'IDR': 'Indonesian Rupiah', 'IRR': 'Iran Rials', 'IQD': 'Iraq Dinars', 'ILS': 'Israeli Shekel', 'JMD': 'Jamaican Dollar',
    'JPY': 'Japanese Yen', 'JOD': 'Jordanian Dinar', 'KZT': 'Kazakhstan Tenge', 'KES': 'Kenyan Shilling', 'LFX': 'Khazanah Sukuk',
    'KRW': 'Korean Won', 'KWD': 'Kuwaiti Dinar', 'KGS': 'Kyrgyzstani Som', 'LAK': 'Laos Kips', 'LVL': 'Latvian Lats',
    'LBP': 'Lebanese Pound', 'LRD': 'Liberia Dollar', 'LYD': 'Libya Dinars', 'LTL': 'Lithuanian Litas', 'MOP': 'Macau Patacas',
    'MKD': 'Macedonian Denar', 'MGA': 'Madagascar Ariary', 'MWK': 'Malawian Kwacha', 'MYR': 'Malaysian Ringgit', 'MVR': 'Maldives Rufiyaa',
    'MRO': 'Mauritania Ouguiyas', 'MUR': 'Mauritian Rupee', 'MXN': 'Mexican Peso', 'MDL': 'Moldova Lei', 'MAD': 'Moroccan Dirham',
    'MZN': 'Mozambique Metical', 'MMK': 'Myanmar Burma Kyats', 'NAD': 'Namibian Dollar', 'NPR': 'Nepal Nepal Rupees', 'NZD': 'New Zealand Dollar',
    'NIO': 'Nicaraguan Cordoba', 'NGN': 'Nigerian Naira', 'NOK': 'Norwegian Krone', 'OMR': 'Omani Rial', 'PKR': 'Pakistan Rupee',
    'XPD': 'Palladium', 'PAB': 'Panama Balboa', 'PGK': 'Papua New Guinea Kina', 'PYG': 'Paraguayan Guarani', 'PEN': 'Peruvian Sol',
    'PHP': 'Philippine Peso', 'XPT': 'Platinum', 'PLN': 'Polish Zloty', 'QAR': 'Qatari Riyal', 'RON': 'Romanian Lei',
    'RUB': 'Russian Ruble', 'RWF': 'Rwandan Franc', 'STD': 'Sao Tome Dobra', 'SAR': 'Saudi Riyal', 'RSD': 'Serbian Dinar',
    'SCR': 'Seychelles Rupee', 'SLL': 'Sierra Leonean', 'XAG': 'Silver', 'SGD': 'Singapore Dollar', 'SKK': 'Slovak Koruna',
    'SOS': 'Somali Shillings', 'ZAR': 'South African Rand', 'SDR': 'Special Drawing Rights', 'LKR': 'Sri Lankan Rupee', 'SHP': 'St Helena Pound',
    'SDG': 'Sudan Pounds', 'SDD': 'Sudanese Dinars', 'SZL': 'Swazi Lilangeni', 'SEK': 'Swedish Krone', 'CHF': 'Swiss Franc',
    'SYP': 'Syria Pounds', 'TWD': 'Taiwan Dollar', 'TJS': 'Tajikistani Somoni', 'TZS': 'Tanzania Shillings', 'THB': 'Thai Baht',
    'TTD': 'Trinidadian Dollar', 'TND': 'Tunisian Dinar', 'TRY': 'Turkish New Lira', 'TMT': 'Turkmenistan Manat', 'AED': 'U.A.E. Dirham',
    'USD': 'U.S. Dollar', 'UGX': 'Ugandan Shillings', 'UAH': 'Ukraine Hryvnia', 'UYU': 'Uruguayan Peso', 'UZS': 'Uzbekistani Som',
    'VEF': 'Venezuelan Bolivars', 'VND': 'Vietnam Dong', 'YER': 'Yemeni Rials', 'ZMK': 'Zambia Kwacha', 'ZMW': 'Zambian Kwacha'
}
nsdq_currencies = {
    "EURUSD": "EURO US DOLLAR", "GBPUSD": "BRITISH POUND US DOLLAR", "USDJPY": "US DOLLAR JAPANESE YEN",
    "USDCHF": "US DOLLAR SWISS FRANC", "USDCAD": "US DOLLAR CANADIAN DOLLAR", "AUDUSD": "AUSTRALIAN DOLLAR US DOLLAR",
    "USDMXN": "US DOLLAR MEXICAN PESO", "USDINR": "US DOLLAR INDIAN RUPEE", "USDRUB": "US DOLLAR RUSSIAN RUBLE",
    "USDBRL": "US DOLLAR BRAZILIAN REAL"
}

class forexquery:
    class which:
        @staticmethod
        def major(currencies=major_currencies):
            return list(currencies.keys())
           
        @staticmethod
        def quote(currencies=bchart_currencies):
            return list(currencies.keys())

    @staticmethod  
    def _join_currency(currency):
        if isinstance(currency, list) and len(currency) == 2:
            if all(isinstance(item, str) and len(item) == 3 for item in currency):
                return ''.join(currency)
        if isinstance(currency, list) and len(currency) == 1:
            return currency[0]
        return currency
       
    @staticmethod   
    def tokenize(currency, as_tuple=False):
        if isinstance(currency, list):
            results = []
            for item in currency:
                item = re.sub(r'\s+', chr(32), item).strip().upper()
                match = re.match(r'^([A-Z]{3})([-_/]?)([A-Z]{3})$', item)
                if match:
                    currency1, separator, currency2 = match.groups()
                    if currency1 != currency2:
                        results.append(currency1)
                        results.append(currency2)
                        continue
                match = re.match(r'^([A-Z]{3})$', item)
                if match:
                    results.append(match.group(1))
            
            if len(results) == 1:
                return (results[0],) if as_tuple else [results[0]]
            elif len(results) == 2:
                return tuple(results) if as_tuple else results
            return None
        else:
            currency = re.sub(r'\s+', chr(32), currency).strip().upper()
            match = re.match(r'^([A-Z]{3})([-_/]?)([A-Z]{3})$', currency)
            if match:
                currency1, separator, currency2 = match.groups()
                if currency1 != currency2:
                    return (currency1, currency2) if as_tuple else [currency1, currency2]
            match = re.match(r'^([A-Z]{3})$', currency)
            if match:
                return (match.group(1),) if as_tuple else [match.group(1)]
            return None

    @staticmethod
    def query(query, query_type="major", ret_type=None):
        currency_dict = major_currencies if query_type == "major" else bchart_currencies        
        query_lower = query.lower()
        for key, value in currency_dict.items():
            if query_lower == key.lower() or query_lower == value.lower():
                if ret_type is not None:
                    if ret_type.lower() == "code":
                        return key
                    elif ret_type.lower() == "name":
                        return value
                else:
                    return (key, value)
        return None
       
    @staticmethod
    def check(currency_pair, currency_dict_type="major"):
        validated_identifier = None       
        tokens = forexquery.tokenize(currency_pair)
        if not tokens:
            raise TypeError("Please enter a valid currency pair as a string or a list of strings.")
        token_len = len(tokens)
        validated = []
        for t in tokens:
            tok = forexquery.query(t, query_type=currency_dict_type, ret_type="code")
            if tok:
                validated.append(tok)
        if len(validated) == token_len:
            validated_identifier = validated
        if not (isinstance(validated_identifier, list) and
                all(isinstance(item, str) for item in validated_identifier)):
            raise ValueError("Invalid currency. Currently, the only currencies accepted are from: " +
                  ", ".join(forexquery.which.major()) + ". Please enter a valid currency.")
        if len(validated_identifier) == 0:
            raise ValueError("Please enter a valid currency pair.")
        if validated_identifier is None:
            raise ValueError(f"{currency_pair} is not in the list of accepted currency pairs.") 
        return forexquery._join_currency(validated_identifier)



class ForexMarketHours:
    def __init__(self, timezone="US/Central"):
        self.timezone = timezone
        
    def is_dst(self, dt=None):
        """Determine whether Daylight Saving Time (DST) is in effect for a given datetime."""
        if dt is None:
            dt = datetime.datetime.utcnow()
        dst_start = datetime.datetime(dt.year, 3, 8)
        dst_end = datetime.datetime(dt.year, 11, 1)
        while dst_start.weekday() != 6:
            dst_start += datetime.timedelta(days=1)
        while dst_end.weekday() != 6:
            dst_end += datetime.timedelta(days=1)
        dst_start = dst_start.replace(hour=2)
        dst_end = dst_end.replace(hour=2)
        return dst_start <= dt < dst_end

    def get_central_time(self):
        now_utc = datetime.datetime.utcnow()
        current_utc_time = now_utc + datetime.timedelta(hours=5)
        if self.is_dst(current_utc_time):
            central_time = current_utc_time - datetime.timedelta(hours=1)
        else:
            central_time = current_utc_time - datetime.timedelta(hours=2)
        return central_time

    def is_forex_market_open(self):
        central_time = self.get_central_time()
        sessions = {
            'sydney': {'start': 22, 'end': 6},
            'tokyo': {'start': 0, 'end': 8},  
            'london': {'start': 8, 'end': 16}, 
            'new_york': {'start': 13, 'end': 21}
        }
        if self.is_dst(central_time):
            utc_time = central_time + datetime.timedelta(hours=5) 
        else:
            utc_time = central_time + datetime.timedelta(hours=6)
        utc_hour = utc_time.hour
        for session, hours in sessions.items():
            if hours['start'] <= utc_hour < hours['end'] or (hours['end'] < hours['start'] and (utc_hour >= hours['start'] or utc_hour < hours['end'])):
                return True
        return False
    
    @property
    def time(self):
        """Property to get the current Forex time if the market is open, or None if closed."""
        if self.is_forex_market_open():
            return self.get_central_time().strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

forex_hours = ForexMarketHours()




def __dir__():
    return ['forexquery', 'forex_hours', 'equityquery', 'CurrencyQuery', 'ExchangeQuery', 'CoinQuery', 'SlugValidateQuery']


__all__ = ['forexquery', 'forex_hours', 'equityquery', 'CurrencyQuery', 'ExchangeQuery', 'CoinQuery', 'SlugValidateQuery']









