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
from ...market_utils import ExchangeQuery


class live_quote:
    def __init__(self, json_content=None, cryptoExchange=None):
        self.crypto_exchange = cryptoExchange
        self.crypto_exchange_ids = None        
        self.data = None
        self.error = False

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.crypto_exchange:
            if not isinstance(self.crypto_exchange , list):
                self.crypto_exchange  = [self.crypto_exchange]

        if self.json_content:
            self.parse()

    def inspect_json(self):
        if not self.json_content or 'data' not in self.json_content[0]:
            raise Exception("No data available for the cryptocurrency.")

    def normalize_time(self, column_names):
        """Normalize the time part of datetime in the specified column to 00:00:00."""
        if self.data.empty:
            return None
        df = self.data
        if not isinstance(column_names, list):
            column_names = [column_names]
        for column_name in column_names:
            df[column_name] = pd.to_datetime(df[column_name]) # Ensure the column is in datetime format
            df[column_name] = df[column_name].dt.normalize() # Normalize time to midnight
        self.data = df
        
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
        dataset = self.json_content
        for data in dataset:
            result = self.process_json(data)
            if result:
                rows.append(result)                
        row_data = rows

        flattened_data = [item for sublist in row_data for item in sublist]
        df = pd.DataFrame(flattened_data)
        df['timeQueried'] = pd.to_datetime(df['timeQueried'] )
        df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
        
        self.data = df
                
    def parse(self):
        try:
            self.inspect_json()
            self.clean_exchanges()
            self.iterate()
            self.normalize_time("lastUpdated")
        except Exception as e:
            self.error = True

    def DATA(self):
        if self.error:
            return "Crypto currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




# For Historical
class crypto_historical:
    def __init__(self, json_content=None):
        self.data = None
        self.error = False

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.json_content:
            self.parse()

    def inspect_json(self):
        if not self.json_content or 'data' not in self.json_content[0]:
            raise Exception("No data available for the cryptocurrency.")

    def normalize_time(self, column_names):
        """Normalize the time part of datetime in the specified column to 00:00:00."""
        if self.data.empty:
            return None
        df = self.data
        if not isinstance(column_names, list):
            column_names = [column_names]
        for column_name in column_names:
            df[column_name] = pd.to_datetime(df[column_name])
            df[column_name] = df[column_name].dt.normalize()
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None:
            return True
        elif dataframe.empty:
            return True
        else:
            return False
           
    def process_json(self):
        rows = []

        # Iterate through each entry in json_content
        for content in self.json_content:
            data = content.get('data', {})
            status = content.get('status', {})
            individual_data = []
            quotes = data.get('quotes', [])

            for quote in quotes:
                row = {
                    'symbol': data.get('symbol', pd.NA),
                    'name': data.get('name', pd.NA),
                    # 'timeOpen': quote.get('timeOpen', pd.NA),
                    # 'timeClose': quote.get('timeClose', pd.NA),
                    # 'timeHigh': quote.get('timeHigh', pd.NA),
                    # 'timeLow': quote.get('timeLow', pd.NA),
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

            # Create a DataFrame from the individual data collected
            df = pd.DataFrame(individual_data)
            rows.append(df)

        # Concatenate all individual DataFrames into a single DataFrame
        data = pd.concat(rows, ignore_index=True) if rows else None

        column_order = [
            'timestamp', 'symbol', 'name',
            # 'timeOpen', 'timeClose', 'timeHigh', 'timeLow',
            'open', 'high', 'low', 'close',
            'volume', 'marketCap', 'time_queried'
        ]

        data = data[column_order]

        # Convert date columns to datetime if not already
        # data['timeOpen'] = pd.to_datetime(data['timeOpen'])
        # data['timeClose'] = pd.to_datetime(data['timeClose'])
        # data['timeHigh'] = pd.to_datetime(data['timeHigh'])
        # data['timeLow'] = pd.to_datetime(data['timeLow'])
        data.rename(columns={'timestamp':'date'}, inplace=True)
        data['date'] = pd.to_datetime(data['date'])
        data['time_queried'] = pd.to_datetime(data['time_queried'])

        self.data = data

    def parse(self):
        try:
            self.inspect_json()
            self.process_json()
            self.normalize_time("date")
        except Exception as e:
            self.error = True
            print(f"Error: {e}")

    def DATA(self):
        if self.error:
            return "Crypto currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




def __dir__():
    return ['live_quote', 'crypto_historical']


__all__ = ['live_quote', 'crypto_historical']

