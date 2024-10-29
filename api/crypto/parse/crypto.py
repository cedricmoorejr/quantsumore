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
from copy import deepcopy
import pandas as pd
import json
import time

# Custom
from ....web_utils import HTMLclean
from ...market_utils import ExchangeQuery, CoinQuery
from ...parse_tools import extract_slug_from_url, extract_cryptoID_from_url
from ...shape_tools import normalize_time, is_valid_dataframe
from ....strata_utils import IterDict


class live_quote:
    def __init__(self, json_content=None, cryptoExchange=None):
        self.crypto_exchange = cryptoExchange
        self.crypto_exchange_ids = None        
        self.data = None
        self.error_messages = []
        self.error = True 

        if json_content:
            self.json_content = IterDict.isNested(json_content)
            
        if self.crypto_exchange:
            if not isinstance(self.crypto_exchange , list):
                self.crypto_exchange  = [self.crypto_exchange]            
            
        if self.json_content:
            self.check_data()  
            self.display_error_messages()  
            if not self.error:
                self.parse()

    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')   

    def check_data(self):
        json_content = self.json_content    
        def validate_api_responses(api_responses):
            validation_list = []
            for index, response in enumerate(api_responses):
                for url, content in response.items():
                    error_message = content.get('response', {}).get('status', {}).get('error_message', "")
                    if error_message != "SUCCESS":
                        validation_list.append((url, False))
                    else:
                        validation_list.append((url, True))
            return validation_list
        
        def process_messages(data, verbose=False):
            messages = []        
            def clean(msgs):
                try:
                    messages_list = [f for f in msgs if 'code:' not in f]
                    return [f.split("-")[-1].split(": ")[-1] for f in messages_list]
                except:
                    return msgs

            def extract_message_fields(data):
                result = {}
                if isinstance(data, dict):
                    for key, value in data.items():
                        if 'error_message' in key.lower():
                            result[key] = value
                        elif isinstance(value, (dict, list)):
                            result.update(extract_message_fields(value))
                elif isinstance(data, list):
                    for item in data:
                        result.update(extract_message_fields(item))
                return result

            def process_entry(key, value):
                if value is None:
                    return 
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                if v is not None:
                                    messages.append(f"{key} - {k}: {v}")
                        else:
                            if item is not None:
                                messages.append(f"{key}: {item}")
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        process_entry(f"{key} - {sub_key}", sub_value)
                else:
                    messages.append(f"{key}: {value}")
                    
            extracted_data = extract_message_fields(data)
            for key, value in extracted_data.items():
                process_entry(key, value)
            if verbose:
                for message in messages:
                    print(message)
            else:
                return clean(messages)
        
        validate_crypto_content = validate_api_responses(json_content)
        error_messages_list = []

        for url, check in validate_crypto_content:
            if not check: 
                slug_name = extract_slug_from_url(url)
                data = IterDict.find(content, target_key=url)
                n_message = process_messages(data)
                message = n_message[0] if n_message else None 
                error_messages_list.append((slug_name, message))
                
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_crypto_content if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False

    def clean_exchanges(self):
        if self.crypto_exchange:            
            exchanges = self.crypto_exchange
            unique_exchanges = list(set(exchanges))
            exchange_ids = [ExchangeQuery.FindID(ex) for ex in unique_exchanges]
            self.crypto_exchange_ids = [item for item in exchange_ids if item is not None]

    def process_json(self, data):       
        market_pairs_data = data['data']['marketPairs']
        rows = []

        for market_pair in market_pairs_data:
            row = {
                'coinSymbol': data['data']["symbol"],
                'coinName': data['data']["name"],                
                'exchangeId': market_pair.get('exchangeId', pd.NA),
                'exchangeName': market_pair.get('exchangeName', pd.NA),
                'exchangeSlug': market_pair.get('exchangeSlug', pd.NA),
                'marketPair': market_pair.get('marketPair', pd.NA),
                'category': market_pair.get('category', pd.NA),
                'baseSymbol': market_pair.get('baseSymbol', pd.NA),
                'baseCurrencyId': market_pair.get('baseCurrencyId', pd.NA),
                'quoteSymbol': market_pair.get('quoteSymbol', pd.NA),
                'quoteCurrencyId': market_pair.get('quoteCurrencyId', pd.NA),
                'price': market_pair.get('price', pd.NA),
                'volumeUsd': market_pair.get('volumeUsd', pd.NA),
                'effectiveLiquidity': market_pair.get('effectiveLiquidity', pd.NA),
                'lastUpdated': market_pair.get('lastUpdated', pd.NA),
                'quote': market_pair.get('quote', pd.NA),
                'volumeBase': market_pair.get('volumeBase', pd.NA),
                'volumeQuote': market_pair.get('volumeQuote', pd.NA),
                'feeType': market_pair.get('feeType', pd.NA),
                'depthUsdNegativeTwo': market_pair.get('depthUsdNegativeTwo', pd.NA),
                'depthUsdPositiveTwo': market_pair.get('depthUsdPositiveTwo', pd.NA),
                'volumePercent': market_pair.get('volumePercent', pd.NA),
                'exchangeType': market_pair.get('type', pd.NA),
                'timeQueried': data['status']["timestamp"],              
            }
            rows.append(row)

        if self.crypto_exchange_ids:
            rows = [pair for pair in rows if pair["exchangeId"] in self.crypto_exchange_ids]

        rows = [
            {key: value for key, value in row.items() if key not in ['exchangeId', 'baseCurrencyId', 'quoteCurrencyId', 'exchangeSlug']}
            for row in rows
        ]        
        return rows

    def iterate(self):
        rows = []
        dataset = IterDict.find(self.json_content, False, 'response')
        for data in dataset:
            result = self.process_json(data)
            if result:
                rows.append(result)                
        row_data = rows

        flattened_data = [item for sublist in row_data for item in sublist]
        df = pd.DataFrame(flattened_data)
        df['timeQueried'] = pd.to_datetime(df['timeQueried'])
        df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
        df = normalize_time(df, 'lastUpdated')        
        self.data = df
                
    def parse(self):
        self.clean_exchanges()
        self.iterate()

    def DATA(self):
        if not is_valid_dataframe(self.data):
            if not self.error_messages:
                return "Crypto currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




# For Historical
class crypto_historical:
    def __init__(self, json_content=None):
        self.data = None
        self.error_messages = []
        self.error = True 

        if json_content:
            self.json_content = IterDict.isNested(json_content)
            
        if self.json_content:
            self.check_data()  
            self.display_error_messages()  
            if not self.error:
                self.parse()

    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')   

    def check_data(self):
        json_content = self.json_content    
        def validate_api_responses(api_responses):
            validation_list = []
            for index, response in enumerate(api_responses):
                for url, content in response.items():
                    error_message = content.get('response', {}).get('status', {}).get('error_message', "")
                    quotes = content.get('response', {}).get('data', {}).get('quotes', None)
                    if quotes == [] or quotes is None:
                        quotes_valid = False
                    else:
                        quotes_valid = True
                    if error_message != "SUCCESS" or not quotes_valid:
                        validation_list.append((url, False))
                    else:
                        validation_list.append((url, True))
            return validation_list
        
        def process_messages(data, verbose=False):
            messages = []        
            def clean(msgs):
                try:
                    messages_list = [f for f in msgs if 'code:' not in f]
                    return [f.split("-")[-1].split(": ")[-1] for f in messages_list]
                except:
                    return msgs

            def extract_message_fields(data):
                result = {}
                if isinstance(data, dict):
                    for key, value in data.items():
                        if 'error_message' in key.lower():
                            result[key] = value
                        elif isinstance(value, (dict, list)):
                            result.update(extract_message_fields(value))
                elif isinstance(data, list):
                    for item in data:
                        result.update(extract_message_fields(item))
                return result

            def process_entry(key, value):
                if value is None:
                    return 
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                if v is not None:
                                    messages.append(f"{key} - {k}: {v}")
                        else:
                            if item is not None:
                                messages.append(f"{key}: {item}")
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        process_entry(f"{key} - {sub_key}", sub_value)
                else:
                    messages.append(f"{key}: {value}")
                    
            extracted_data = extract_message_fields(data)
            for key, value in extracted_data.items():
                process_entry(key, value)
            if verbose:
                for message in messages:
                    print(message)
            else:
                return clean(messages)
        
        validate_crypto_content = validate_api_responses(json_content)
        error_messages_list = []

        for url, check in validate_crypto_content:
            if not check: 
                crypto_id = extract_cryptoID_from_url(url)
                found_slug = CoinQuery.ID(crypto_id)
                slug_name = IterDict.search_keys_in(found_slug, "name") 
                data = IterDict.find(json_content, target_key=url)
                check_quote_values = IterDict.search_keys_in(data, "quotes")
                if not check_quote_values:
                    message = "No data exists for the specified time periods."
                else:        
                    n_message = process_messages(data)
                    message = n_message[0] if n_message else None 
                error_messages_list.append((slug_name, message))
                
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_crypto_content if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False

    def process_json(self):
        rows = []

        # Iterate through each entry in json_content
        dataset = IterDict.find(self.json_content, False, 'response')
        for content in dataset:
            data = content.get('data', {})
            status = content.get('status', {})
            individual_data = []
            quotes = data.get('quotes', [])

            for quote in quotes:
                row = {
                    'symbol': data.get('symbol', pd.NA),
                    'name': data.get('name', pd.NA),
                    'open': quote.get('quote', {}).get('open', pd.NA),
                    'high': quote.get('quote', {}).get('high', pd.NA),
                    'low': quote.get('quote', {}).get('low', pd.NA),
                    'close': quote.get('quote', {}).get('close', pd.NA),
                    'volume': quote.get('quote', {}).get('volume', pd.NA),
                    'marketCap': quote.get('quote', {}).get('marketCap', pd.NA),
                    'timestamp': quote.get('quote', {}).get('timestamp', pd.NA),
                    'time_queried': status.get('timestamp', pd.NA),
                }
                individual_data.append(row)

            df = pd.DataFrame(individual_data)
            rows.append(df)
        data = pd.concat(rows, ignore_index=True) if rows else None

        column_order = [
            'timestamp', 'symbol', 'name',
            # 'timeOpen', 'timeClose', 'timeHigh', 'timeLow',
            'open', 'high', 'low', 'close',
            'volume', 'marketCap', 'time_queried'
        ]

        data = data[column_order]
        data.rename(columns={'timestamp':'date'}, inplace=True)
        data['date'] = pd.to_datetime(data['date'])
        data = normalize_time(data, 'date')          
        data['time_queried'] = pd.to_datetime(data['time_queried'])
        self.data = data

    def parse(self):
        self.process_json()

    def DATA(self):
        if not is_valid_dataframe(self.data):
            if not self.error_messages:
                return "Crypto currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




def __dir__():
    return ['live_quote', 'crypto_historical']


__all__ = ['live_quote', 'crypto_historical']

