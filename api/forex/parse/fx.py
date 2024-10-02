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
import json
import html
from copy import deepcopy
import time

# Custom
from ...market_utils import forexquery, forex_hours
from ....web_utils import HTMLclean
from ....date_parser import dtparse
from ...._http.response_utils import clean_initial_content, get_top_level_key



# Helper
def fix_and_validate_dict_string_or_list(input_data):
    def fix_and_validate_dict_string(dict_string):
        try:
            parsed_dict = json.loads(dict_string)
            return parsed_dict
        except json.JSONDecodeError as e:
            pass
        open_braces = dict_string.count('{')
        close_braces = dict_string.count('}')
        if open_braces > close_braces:
            dict_string += '}' * (open_braces - close_braces)
        if dict_string[-1] != '}':
            dict_string += '}'
        dict_string = dict_string.replace('", "', '", "')
        dict_string = dict_string.replace('": "', '": "')
        dict_string = dict_string.replace(', "', ', "')
        try:
            parsed_dict = json.loads(dict_string)
            return parsed_dict
        except json.JSONDecodeError as e:
            return None
    if isinstance(input_data, list):
        return [fix_and_validate_dict_string(item) for item in input_data]
    elif isinstance(input_data, str):
        return fix_and_validate_dict_string(input_data)
    else:
        raise ValueError("Input data must be either a string or a list of strings.")

def process_dict_or_list(data):
    def convert_to_float(value):
        try:
            return float(value)
        except ValueError:
            return value    
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                new_dict[key] = process_dict_or_list(value)
            elif isinstance(value, str):
                if ' - ' in value: 
                    parts = value.split(' - ')
                    if len(parts) == 2:
                        new_dict[key] = convert_to_float(parts[0])
                    else:
                        new_dict[key] = value
                else:
                    new_dict[key] = convert_to_float(value)
            else:
                new_dict[key] = value
        return new_dict
    elif isinstance(data, list):
        return [process_dict_or_list(item) for item in data]
    else:
        return data

def remove_nested_keys(data):
    data_dict = deepcopy(data)
    def _remove_nested_keys(d):
        if isinstance(d, dict):
            keys_to_remove = []
            for key, value in d.items():
                if isinstance(value, dict):
                    keys_to_remove.append(key)
                else:
                    d[key] = value
            for key in keys_to_remove:
                del d[key]
        elif isinstance(d, list):
            for item in d:
                _remove_nested_keys(item)
    _remove_nested_keys(data_dict)
    return data_dict

def combine_dicts(dict_list):
    result = {}
    def add_key(key, value):
        if key not in result:
            result[key] = value
        else:
            index = 1
            new_key = f"{key}_{index}"
            while new_key in result:
                index += 1
                new_key = f"{key}_{index}"
            result[new_key] = value
    for d in dict_list:
        for key, value in d.items():
            if isinstance(value, dict):
                add_key(key, combine_dicts([value]))
            else:
                add_key(key, value)
    return result

def rename_keys(data, old_keys, new_keys):
    if len(old_keys) != len(new_keys):
        raise ValueError("The list of old keys and new keys must have the same length.")
    new_data = deepcopy(data)
    for old_key, new_key in zip(old_keys, new_keys):
        if old_key in new_data:
            new_data[new_key] = new_data.pop(old_key)
        else:
            raise KeyError(f"The key '{old_key}' does not exist in the dictionary.")
    return new_data

def reorder_dict(original_dict, new_order):
    reordered_dict = {key: original_dict[key] for key in new_order if key in original_dict}
    return reordered_dict









## Via JSON
##========================================================================
class fx_historical:
    def __init__(self, json_content=None):
        self.cleaned_data = None          
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.data = None       

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.json_content:
            self.parse()

            if self.cleaned_data:
                self._create_dataframe()
            
    def _clean_content(self, content):
        return clean_initial_content(content)   
        
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['InverseRate'] = round((1 / df['RatePairValue']), 6)
        df['LastUpdate'] = df['LastUpdate'].apply(dtparse.parse, to_format='%Y-%m-%d') # Convert Date Column  
        df['BaseCurrency'] = df['RatePair'].str.slice(0, 3)  # First 3 characters for the base currency
        df['QuoteCurrency'] = df['RatePair'].str.slice(3, 6)  # Last 3 characters for the quote currency
        df['QueriedAt'] = self.timestamp
        df.rename(columns={'LastUpdate': 'Date', 'RatePair': 'CurrencyPair', 'RatePairValue': 'Rate'}, inplace=True)

        column_order=['Date', 'CurrencyPair', 'BaseCurrency', 'QuoteCurrency', 'Rate', 'InverseRate','QueriedAt']
        filtered_columns = [col for col in column_order if col in df.columns]
        self.data = df[filtered_columns]

    def _is_data(self, dataframe):
        if dataframe is None:
            return True
        elif dataframe.empty:
            return True
        else:
            return False

    def parse(self):
        # Flatten the list of dictionaries and remove 'CallCount' key using dictionary comprehension
        cleaned_content = self._clean_content(self.json_content)         
        flattened_data = []
        responses = cleaned_content
        for response in responses:
            for item in response['d']:
                new_item = {key: value for key, value in item.items() if key != 'CallCount'}
                flattened_data.append(new_item)

        if flattened_data:
            self.cleaned_data = flattened_data

    def DATA(self):
        if self._is_data(self.data):
            return "Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']



class fx_interbank_rates:
    def __init__(self, json_content=None):
        self.cleaned_data = None          
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.data = None       

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.json_content:
            self.parse()

            if self.cleaned_data:
                self._create_dataframe()
    
    def _clean_content(self, content):
        return clean_initial_content(content)   
        
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df.rename(columns={'ChangePercent': 'PercentageChange', 'RatePair': 'CurrencyPair', 'Amount':'Rate'}, inplace=True)
        df['QueriedAt'] = self.timestamp
        df["QuoteCurrency"] = df['CurrencyPair'].str.slice(0, 3)
        df = df[["CurrencyPair", "QuoteCurrency", "Rate", "PercentageChange", "QueriedAt"]]
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None:
            return True
        elif dataframe.empty:
            return True
        else:
            return False
        
    def parse(self):
        cleaned_content = self._clean_content(self.json_content)        	
        flattened_data = []
        responses = cleaned_content
        for response in responses:
            for item in response:            
                new_item = {key: value for key, value in item.items() if key != 'ChartData'}
                flattened_data.append(new_item)

        if flattened_data:
            self.cleaned_data = flattened_data

    def DATA(self):
        if self._is_data(self.data):
            return "Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']



class live_bid_ask:
    def __init__(self, json_content=None):
        self.cleaned_data = None          
        self.data = None         

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.json_content:
            self.parse()

            if self.cleaned_data:
                self._create_dataframe()

    def _clean_content(self, content):
        return clean_initial_content(content)   
        
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None:
            return True
        elif dataframe.empty:
            return True
        else:
            return False

    def parse(self):
        cleaned_content = self._clean_content(self.json_content)          
        top_key = get_top_level_key(cleaned_content)
        rows = []
        for entry in cleaned_content:
            row = {}
            row['Symbol'] = entry[top_key]['symbol']
            row['Asset Class'] = entry[top_key]['assetClass']
            for key, val in entry[top_key]['summaryData'].items():
                row[val['label']] = val['value']
            rows.append(row)

        if rows:
            self.cleaned_data = rows

    def DATA(self):
        if self._is_data(self.data):
            return "Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']





## Via HTML
##========================================================================
class live_quote:
    def __init__(self, html_content=None):
        self.html_content = html_content
        self.currency_pair = None
        self.timestamp = None
        self.bid_ask_prices = None
        self.intraday = None        
        self.quote_headers = {
          "lowPrice": "Low",
          "openPrice": "Open",
          "highPrice": "High",
          "lastPrice": "Last",
          "previousPrice": "Previous Close",
          "highPriceYtd": "YTD High",
          "lowPriceYtd": "YTD Low",
          "stochasticK14d": "Stochastic %K",
          "weightedAlpha": "Weighted Alpha",
          "priceChange5d": "5-Day Change",
          "lowPrice1y": "52-Week Range",
          "labelLow": "Day Low",
          "labelHigh": "Day High"
        }
        self.stats_raw = None
        self.stats_clean = None    
        self.data = None       
        self.error = False         

        if html_content:
            self.parse()
            if not self.error:
                self.compile_data()
                
    def __format_price(self, value):
        try:
            return round(float(value), 6)
        except ValueError:
            return value

    def clean_html_content(self):
        self.html_content = HTMLclean.decode(self.html_content)

    def extract_ccy_pair(self):
        div_pattern = r'<div class="symbol-name[^>]*>.*?<span>\(([^)]*)\)</span>'
        div_match = re.search(div_pattern, self.html_content, re.DOTALL)
        if div_match:
            symbol_in_parentheses = div_match.group(1)
            cleaned_symbol = re.sub(r'[^A-Za-z]', '', symbol_in_parentheses)
            if len(cleaned_symbol) == 6:
                self.currency_pair = f"{cleaned_symbol.upper()}"
        return None

    def extract_bid_ask_prices(self):
        pattern = r'data-ng-init=\'init\((\{.*?\})\)\''
        match = re.search(pattern, self.html_content, re.DOTALL)
        if match:
            json_like_string = match.group(1)
            bid_price_pattern = r'"bidPrice":"([0-9.]+)"'
            ask_price_pattern = r'"askPrice":"([0-9.]+)"'
            bid_price_match = re.search(bid_price_pattern, json_like_string)
            ask_price_match = re.search(ask_price_pattern, json_like_string)
            bid_price = bid_price_match.group(1) if bid_price_match else None
            ask_price = ask_price_match.group(1) if ask_price_match else None
            ask = self.__format_price(ask_price)
            bid = self.__format_price(bid_price)
            spread = round((ask - bid), 6)
            self.bid_ask_prices = {"bidPrice":bid, "askPrice":ask, "bid-askSpread":spread}
        return None
       
    def extract_other_prices(self):
        pattern = r'data-ng-init=\'init\((\{.*?\})\)\''
        match = re.search(pattern, self.html_content, re.DOTALL)
        if match:
            json_like_string = match.group(1)
            price_change_pattern = r'"priceChange":"([+\\-]?[0-9.]+)"'
            price_change_match = re.search(price_change_pattern, json_like_string)
            price_change = price_change_match.group(1) if price_change_match else None
            self.intraday = {'lastChangeInRate':self.__format_price(price_change)}
        return None

    def extract_date_time(self):
        json_pattern = r'<script type="application/json" id="barchart-www-inline-data">(.*?)</script>'
        json_match = re.search(json_pattern, self.html_content, re.DOTALL)        
        if json_match:
            json_content = json_match.group(1)
            data = json.loads(json_content)
            first_key = list(data.keys())[0]
            if forex_hours.time:
                self.timestamp = forex_hours.time
            else:
                try:
                    trade_time = data[first_key]["quote"]["tradeTime"]
                    self.timestamp = trade_time.replace("T", " ")
                except:
                    date_pattern = r'"sessionDateDisplayLong":"([^"]+)"'
                    time_pattern = r'"tradeTime":"([^"]+)"'
                    date_match = re.search(date_pattern, self.html_content)
                    time_match = re.search(time_pattern, self.html_content)
                    if date_match and time_match:
                        date_part = date_match.group(1)
                        time_part = time_match.group(1)
                        self.timestamp = f"{date_part} {time_part}"
        return None

    def extract_raw_stats(self):
        pattern = (
            r'<div\s+class="bc-quote-overview row"\s+'
            r'data-ng-controller="QuoteOverview\.quoteOverviewCtrl"\s+'
            r'data-ng-init[^>]*>'
        )
        matches = re.findall(pattern, self.html_content, re.IGNORECASE)
        dict_matches = re.findall(rf'data-ng-init=\'init\("\^{self.currency_pair}",(\{{.*?\}}),(\{{.*?\}}),(\{{.*?\}})', matches[0])
        dict_unnested = [result for result in dict_matches[0]]
        fixed_dict = fix_and_validate_dict_string_or_list(dict_unnested)
        converted_data = process_dict_or_list(fixed_dict)
        self.stats_raw = remove_nested_keys(converted_data)      

    def clean_data(self):
        def innerrenameKeys(data):
            key_map = data[0] # First dict contains header/quote names
            data_dict = data[1]
            new_data = {key_map[k]: data_dict[k] for k in key_map if k in data_dict}
            return new_data 
        new_headers = self.quote_headers
        nested_list = deepcopy(self.stats_raw)
        nested_list.pop(0)
        for item in nested_list:
            keys_to_remove = [key for key in item if key in new_headers and item[key] == new_headers[key]]
            for key in keys_to_remove:
                item.pop(key, None)
        nested_list = [item for item in nested_list if item] 
        nested_list = [combine_dicts(nested_list)]
        nested_list.insert(0, new_headers)
        self.stats_clean = innerrenameKeys(nested_list)
        return None
    
    def parse(self):
        try:
            self.clean_html_content()
            self.extract_ccy_pair()
            self.extract_bid_ask_prices()
            self.extract_other_prices()
            self.extract_date_time()
            self.extract_raw_stats()
            self.clean_data()
        except:
            self.error = True

    def compile_data(self):
        data = combine_dicts([{'currencyPair':self.currency_pair}, self.bid_ask_prices, self.intraday, self.stats_clean, {'lastUpdated':self.timestamp}])
        data = rename_keys(
            data,
            old_keys=['Low', 'Open', 'High', 'Last', 'Previous Close', 'YTD High', 'YTD Low', 'Stochastic %K', 'Weighted Alpha', '5-Day Change', '52-Week Range'],
            new_keys=['dailyLow', 'openPrice', 'dailyHigh', 'lastTradedPrice', 'previousClose', 'ytdHigh', 'ytdLow', 'stochastic%K', 'weightedAlpha', '5dayChange', '52weekRange']
            )
        data = reorder_dict(
            data,
            new_order = [
                'currencyPair', 
                'openPrice', 
                'bidPrice', 
                'askPrice', 
                'bid-askSpread',                 
                'lastTradedPrice', 
                'previousClose',
                'dailyLow', 
                'dailyHigh', 
                'lastChangeInRate',
                'ytdLow', 
                'ytdHigh', 
                '52weekRange',
                'stochastic%K', 
                'weightedAlpha', 
                '5dayChange', 
                'lastUpdated'
            ])
        self.data = data

    def DATA(self):
        if not self.error:
            return self.currency_pair, self.data
        else:
            return "Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."

    def __dir__(self):
        return ['DATA']



class conversion:
    def __init__(self, html_content=None, conversion_amount=1):
        self.html_content = html_content
        self.currency_pair = None
        self.exchange_rate = None
        self.converted_exchange_rate = None        
        self.conversion_amount = conversion_amount
        self.timestamp = None        
        self.data = None      
        self.error = False             

        if html_content:
            self.parse()
            if not self.error:
                self.restructure()

    def __format_price(self, value):
        try:
            return float(value)
        except ValueError:
            return value

    def clean_html_content(self):
        self.html_content = HTMLclean.decode(self.html_content)

    def extract_ccy_pair(self):
        div_pattern = r'<div class="symbol-name[^>]*>.*?<span>\(([^)]*)\)</span>'
        div_match = re.search(div_pattern, self.html_content, re.DOTALL)
        if div_match:
            symbol_in_parentheses = div_match.group(1)
            cleaned_symbol = re.sub(r'[^A-Za-z]', '', symbol_in_parentheses)
            if len(cleaned_symbol) == 6:
                self.currency_pair = f"{cleaned_symbol.upper()}"
        return None

    def extract_date_time(self):
        json_pattern = r'<script type="application/json" id="barchart-www-inline-data">(.*?)</script>'
        json_match = re.search(json_pattern, self.html_content, re.DOTALL)        
        if json_match:
            json_content = json_match.group(1)
            data = json.loads(json_content)
            first_key = list(data.keys())[0]
            if forex_hours.time:
                self.timestamp = forex_hours.time
            else:
                try:
                    trade_time = data[first_key]["quote"]["tradeTime"]
                    self.timestamp = trade_time.replace("T", " ")
                except:
                    date_pattern = r'"sessionDateDisplayLong":"([^"]+)"'
                    time_pattern = r'"tradeTime":"([^"]+)"'
                    date_match = re.search(date_pattern, self.html_content)
                    time_match = re.search(time_pattern, self.html_content)
                    if date_match and time_match:
                        date_part = date_match.group(1)
                        time_part = time_match.group(1)
                        self.timestamp = f"{date_part} {time_part}"
        return None

    def extract_exchange_rate(self):
        pattern = r'data-ng-init=\'init\((\{.*?\})\)\''
        match = re.search(pattern, self.html_content, re.DOTALL)
        if match:
            json_like_string = match.group(1)
            last_price_pattern = r'"lastPrice":"([0-9.]+)"'
            last_price_match = re.search(last_price_pattern, json_like_string)
            last_price = last_price_match.group(1) if last_price_match else None
            self.exchange_rate = self.__format_price(last_price)
            self.converted_exchange_rate = round(1/self.exchange_rate, 6)
        return None

    def restructure(self):
        from_currency_code = self.currency_pair[:3].strip()
        to_currency_code = self.currency_pair[3:].strip()

        from_currency = forexquery.query(from_currency_code, query_type="bchart",ret_type="name")
        to_currency = forexquery.query(to_currency_code, query_type="bchart",ret_type="name")

        rate_from = self.exchange_rate
        rate_to = self.converted_exchange_rate 

        amount_from = self.conversion_amount
        amount_to = round((self.conversion_amount * self.exchange_rate),6)

        last_updated = self.timestamp

        self.data = {
            'from_currency': from_currency,
            'from_currency_code': from_currency_code,
            'to_currency': to_currency,
            'to_currency_code': to_currency_code,
            
            f'conversion_rate_{from_currency_code}_to_{to_currency_code}': rate_from,
            f'conversion_rate_{to_currency_code}_to_{from_currency_code}': rate_to,
            f'amount_converted_from_{from_currency_code}': {
                f'original_amount_{from_currency_code}': amount_from,
                f'converted_amount_to_{to_currency_code}': amount_to
            },
            f'amount_converted_from_{to_currency_code}': {
                f'original_amount_{to_currency_code}': amount_from,
                f'converted_amount_to_{from_currency_code}': round((self.conversion_amount * self.converted_exchange_rate),6)
            },
            'last_updated': last_updated,
        }

    def parse(self):
        try:
            self.clean_html_content()
            self.extract_ccy_pair()
            self.extract_exchange_rate()
            self.extract_date_time()
        except:
            self.error = True

    def DATA(self):
        if not self.error:
            return self.data
        else:
            return "Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."

    def __dir__(self):
        return ['DATA']


def __dir__():
    return [
    'fx_historical', 
    'conversion', 
    'live_quote',
    'fx_interbank_rates',
    'live_bid_ask'
    ]

__all__ = [
	'fx_historical', 
	'conversion', 
	'live_quote',
	'fx_interbank_rates',
	'live_bid_ask'
	]

