import json
import sqlite3
import unicodedata
import re
import os
from datetime import datetime, timedelta
from copy import deepcopy

from .._http.connection import http_client
from ..tools.sys_utils import JsonFileHandler, SQLiteDBHandler

class CONTROL:
    def __init__(self, url="https://resonant-cascaron-556ce0.netlify.app/data.json"):
        self.url = url
        self.data_loaded = False   
        self.saved_json_content = None
        self.loaded_data = None        
        self.exchanges = None
        self.pairs = None          
        
        self.to_json()
        self.to_sqlite()
        self.parse_json()      
        
    def _make_request(self, url, headers_to_update=None):
        """ Note: http_client is a Singleton class instance."""
        http_client.update_base_url(url)
        original_headers = {}
        if headers_to_update:
            for header, value in headers_to_update.items():
                original_headers[header] = http_client.get_headers(header)
                http_client.update_header(header, value)
        response = http_client.make_request(params={})
        for header, original_value in original_headers.items():
            http_client.update_header(header, original_value)
        content = response["response"]
        return content if content else None

    def to_json(self):
        if JsonFileHandler("crypto.json").is_outdated():
            url = self.url
            headers_to_update = {"Accept": "application/json"}
            content = self._make_request(url, headers_to_update=headers_to_update)
            if content:            
                try:
                    self.saved_json_content = content
                    JsonFileHandler("crypto.json").save(self.saved_json_content)
                    self.loaded_data = json.loads(self.saved_json_content)                
                    if self.saved_json_content:
                        self.data_loaded = True
                        # print("Data Loaded")
                except Exception as e:
                    print(f"Data Not Loaded: {str(e)}")
                    self.data_loaded = False
        else:                    
            try:
                self.loaded_data = JsonFileHandler("crypto.json").load()
                if self.loaded_data:
                    self.data_loaded = True
                    # print("Data Loaded")                
            except Exception as e:
                print(f"Data Not Loaded: {str(e)}")
                self.data_loaded = False            

    def to_sqlite(self):
        sqliteDB = SQLiteDBHandler("crypto.db")
        if sqliteDB.is_outdated():
            sqliteDB.reset_database()
            sqliteDB.save("crypto.db")

    def transform_exchanges(self):
        if self.data_loaded:
            self.exchanges = list(self.loaded_data['crypto_exchanges'].values())        

    def transform_pairs(self):
        if self.data_loaded:
            data = self.loaded_data['pairs']
            data = {
                currency_name: {
                    **currency_info,
                    'currency': currency_name
                }
                for currency_name, currency_info in data.items()
            }
            self.pairs = list(data.values())

    def parse_json(self):
        self.transform_exchanges()
        self.transform_pairs()



class Query:
    def __init__(self, file=None):
        self.file = file

    class Currency:
        def __init__(self, file):
            self.handler = JsonFileHandler(filename=file)                    
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
            self.handler = JsonFileHandler(filename=file)
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
            query = 'SELECT * FROM cryptos WHERE id = ?'
            return self.execute_query(query, (crypto_id,))

        def Name(self, name):
            normalized_name = self.normalize_string(name)
            query = 'SELECT * FROM cryptos WHERE name LIKE ?'
            data = self.execute_query(query, (f'%{normalized_name}%',))
            return [item for item in data if self.case_sensitive_search(name, item['name'])]

        def Slug(self, slug):
            slug = slug.lower()
            query = 'SELECT * FROM cryptos WHERE slug = ?'
            return self.execute_query(query, (slug,))
           
        def ListSlugs(self):
            query = 'SELECT name, symbol, slug FROM cryptos'
            return self.execute_query(query, ())

        def __dir__(self):
            return ['ID', 'Name', 'Slug', 'ListSlugs']        






GEARBOX = CONTROL()         

# # Create an instance of Probe
# DBGates = Probe(db="crypto.db")

# Create an instance of ExchangeQuery, CurrencyQuery, and db query
query = Query()
CurrencyQuery = query.Currency(file="crypto.json")
ExchangeQuery = query.Exchange(file="crypto.json")
CoinQuery = query.Coin(file="crypto.db")


def __dir__():
    return ['CurrencyQuery', 'ExchangeQuery', 'CoinQuery']

__all__ = ['CurrencyQuery', 'ExchangeQuery', 'CoinQuery']


