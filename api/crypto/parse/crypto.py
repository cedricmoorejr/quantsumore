import datetime
import re
from copy import deepcopy
import pandas as pd
import json
import time

# Custom
# from exchanges.market_utils import *
from ....tools._html_cl import HTMLclean
from ....configuration.generatedcrypto import ExchangeQuery



class live_quote:
    def __init__(self, json_content=None, cryptoExchange=None):
        self.crypto_exchange = cryptoExchange
        self.crypto_exchange_ids = None        
        self.data = None
        self.error = False

        if isinstance(json_content, str):
            self.json_content = json.loads(json_content)
        elif isinstance(json_content, dict):
            self.json_content = json_content
        else:
            self.json_content = {}

        if self.crypto_exchange:
            if not isinstance(self.crypto_exchange , list):
                self.crypto_exchange  = [self.crypto_exchange]

        if self.json_content:
            self.parse()

    def inspect_json(self):
        if 'data' not in self.json_content:
            raise Exception("No data available for the crypto currency.")

    def clean_exchanges(self):
        if self.crypto_exchange:            
            exchanges = self.crypto_exchange
            unique_exchanges = list(set(exchanges))
            exchange_ids = [ExchangeQuery.FindID(ex) for ex in unique_exchanges]
            self.crypto_exchange_ids = [item for item in exchange_ids if item is not None]

    def process_json(self):
        data = self.json_content
        market_pairs_data = data['data']['marketPairs']
        rows = []

        for market_pair in market_pairs_data:
            row = {
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
                'exchangeType': market_pair.get('type', pd.NA)
            }
            rows.append(row)

        if self.crypto_exchange_ids:
            rows = [pair for pair in rows if pair["exchangeId"] in self.crypto_exchange_ids]

        rows = [
            {key: value for key, value in row.items() if key not in ['exchangeId', 'baseCurrencyId', 'quoteCurrencyId', 'exchangeSlug']}
            for row in rows
        ]        

        # Convert list of dicts to DataFrame
        df = pd.DataFrame(rows)
        df.insert(0, 'coinSymbol', data['data']["symbol"])
        df.insert(0, 'coinName', data['data']["name"])

        df['timeQueried'] = pd.to_datetime(data['status']["timestamp"])
        # df['timeQueried'] = df['timeQueried'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
        # df['lastUpdated'] = df['lastUpdated'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        # df.rename(columns={
        #     'timeOpen': 'open_time',
        #     'timeClose': 'close_time',
        #     'timeHigh': 'high_time',
        #     'timeLow': 'low_time',
        #     'open': 'opening_price',
        #     'high': 'highest_price',
        #     'low': 'lowest_price',
        #     'close': 'closing_price',
        #     'volume': 'trading_volume',
        #     'marketCap': 'market_capitalization',
        #     'timestamp': 'recorded_timestamp'
        # }, inplace=True)
        
        self.data = df

    def parse(self):
        try:
            self.inspect_json()
            self.clean_exchanges()
            self.process_json()
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

        if isinstance(json_content, str):
            self.json_content = json.loads(json_content)
        elif isinstance(json_content, dict):
            self.json_content = json_content
        else:
            self.json_content = {}

        if self.json_content:
            self.parse()

    def inspect_json(self):
        if 'data' not in self.json_content:
            raise Exception("No data available for the crypto currency.")
    
    def process_json(self):
        data = self.json_content        
        quotes_data = data['data']['quotes']

        # Flatten the nested 'quote' dictionary into the parent dictionary for each quote entry
        for quote in quotes_data:
            quote.update(quote.pop('quote'))

        # Create DataFrame
        df = pd.DataFrame(quotes_data)

        # Add additional columns for 'id', 'name', and 'symbol'
        df['name'] = data['data']['name']
        df['symbol'] = data['data']['symbol']
        df['time_queried'] = data['status']['timestamp']

        column_order = [
            'symbol', 'name',
            'timeOpen', 'timeClose', 'timeHigh', 'timeLow',
            'open', 'high', 'low', 'close',
            'volume', 'marketCap', 'timestamp', 'time_queried'
        ]

        df = df[column_order]

        # Convert date columns to datetime if not already
        df['timeOpen'] = pd.to_datetime(df['timeOpen'])
        df['timeClose'] = pd.to_datetime(df['timeClose'])
        df['timeHigh'] = pd.to_datetime(df['timeHigh'])
        df['timeLow'] = pd.to_datetime(df['timeLow'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_queried'] = pd.to_datetime(df['time_queried'])

        # # Format these datetime objects to the specified string format
        # df['timeOpen'] = df['timeOpen'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        # df['timeClose'] = df['timeClose'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        # df['timeHigh'] = df['timeHigh'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        # df['timeLow'] = df['timeLow'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        # df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        # df['time_queried'] = df['time_queried'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        # df.rename(columns={
        #     'timeOpen': 'open_time',
        #     'timeClose': 'close_time',
        #     'timeHigh': 'high_time',
        #     'timeLow': 'low_time',
        #     'open': 'opening_price',
        #     'high': 'highest_price',
        #     'low': 'lowest_price',
        #     'close': 'closing_price',
        #     'volume': 'trading_volume',
        #     'marketCap': 'market_capitalization',
        #     'timestamp': 'recorded_timestamp'
        # }, inplace=True)
        
        self.data = df

    def parse(self):
        try:
            self.inspect_json()
            self.process_json()
        except Exception as e:
            self.error = True

    def DATA(self):
        if self.error:
            return "Crypto currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




def __dir__():
    return ['live_quote', 'crypto_historical']


__all__ = ['live_quote', 'crypto_historical']




# class live_stats:
#     def __init__(self, html_content=None):
#         self.html_content = html_content
#         self.data_points = {
#             "coin_name":None,
#             "coin_symbol":None,
#             "price": None,
#             "percentage_change_1d": None,
#             "market_cap": None,
#             "market_cap_percentage_change": None,
#             "volume_24h": None,
#             "volume_24h_percentage_change": None,
#             "volume_market_cap_ratio": None,
#             "circulating_supply": None,
#             "total_supply": None,
#             "max_supply": None,
#             "fully_diluted_market_cap": None,
#             "all_time_high": None,
#             "all_time_high_percentage_change": None,
#             "all_time_low": None,
#             "all_time_low_percentage_change": None,
#             "last_updated":None
#         }
# 
#         self.error = False
# 
#         if html_content:
#             self.parse()
# 
#     def _add(self, key, value):
#         updated_dict = deepcopy(self.data_points)
#         updated_dict[key] = value
#         self.data_points = updated_dict
# 
#     def _get(self, key):
#         return self.data_points.get(key, None)
# 
#     def _format_price(self, value):
#         try:
#             # Handling percentage
#             if '%' in value:
#                 return round((float(value.strip('%')) / 100), 6)
#             # Handling infinity symbol
#             if value == '∞':
#                 return float('inf')
#             # Removing currency symbols and commas, then convert to float and round
#             clean_str = value.replace('$', '').replace(',', '')
#             return round(float(clean_str), 6)
#         except ValueError:
#             return value
#         except Exception:
#             return value
# 
#     def set_timestamp(self):
#         timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
#         self._add("last_updated", timestamp)
# 
#     def extract_price_and_change(self):
#         block_pattern = re.compile(
#             r'<div\s+class="sc-65e7f566-0\s+DDohe\s+flexStart\s+alignBaseline".*?'
#             r'<span\s+class="sc-65e7f566-0\s+clvjgF\s+base-text"\s+data-test="text-cdp-price-display">\s*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)</span>'
#             r'.*?<p\s+color="(red|green)"\s+data-change="(down|up)".*?>(-?\d+\.\d+%)',
#             re.DOTALL
#         )
#         matches = re.findall(block_pattern, self.html_content)
#         for match in matches:
#             price = self._format_price(match[0])
#             color = match[1]
#             # direction = match[2]
#             change_percentage = match[3]
#             if color == 'red':
#                change_percentage = "-" + change_percentage
#             else:
#                 change_percentage = "+" + change_percentage
# 
#             change_percentage = self._format_price(change_percentage)
#             self._add("price", price)
#             self._add("percentage_change_1d", change_percentage)
# 
#         if not matches:
#             price_pattern = re.compile(
#                 r'<div\s+class="sc-65e7f566-0\s+DDohe\s+flexStart\s+alignBaseline".*?>.*?'
#                 r'<span\s+class="sc-65e7f566-0\s+clvjgF\s+base-text"\s+data-test="text-cdp-price-display">\s*'
#                 r'(\$[0-9,.]+)',
#                 re.DOTALL
#             )
#             price_match = re.search(price_pattern, self.html_content)
#             if price_match:
#                 price = price_match.group(1)
#                 self._add("price", price)
# 
#     def extract_coin_name(self):
#         name_pattern = r'data-role="coin-name" title="([^"]+)"'
#         name_match = re.search(name_pattern, self.html_content)
#         if name_match:
#             coin_name = name_match.group(1).strip()
#             self._add("coin_name", coin_name)
# 
#     def extract_coin_symbol(self):
#         symbol_pattern = r'data-role="coin-symbol">([^<]+)</span>'
#         symbol_match = re.search(symbol_pattern, self.html_content)
#         if symbol_match:
#             coin_symbol = symbol_match.group(1).strip()
#             self._add("coin_symbol", coin_symbol)
# 
#     def extract_market_cap_and_change(self):
#         pattern = re.compile(
#             r'<div\s+itemscope=""\s+itemType="https://schema\.org/Table".*?id="section-coin-stats".*?>.*?'
#             r'<dt\s+class="[^"]*">.*?Market\s+cap.*?</dt>.*?'
#             r'<dd\s+class="[^"]*">.*?'
#             r'<p[^>]*>\s*<svg[^>]*>.*?</svg>\s*([-+]?\d+\.\d+%)\s*</p>.*?'
#             r'(\$[0-9,.]+)',
#             re.DOTALL
#         )
#         # pattern = r'Market cap.*?\$([0-9,]+(?:\.[0-9]{1,2})?).*?<p.*?>([-+]?\d+\.?\d*%)<\/p>'
#         match = re.search(pattern, self.html_content)
#         if match:
#             percentage_change = self._format_price(match.group(1))
#             market_cap = self._format_price(match.group(2))
#             self._add("market_cap", market_cap)
#             self._add("market_cap_percentage_change", percentage_change)
# 
#     def extract_volume_and_change(self):
#         pattern = re.compile(
#             r'<dt\s+class="[^"]*">.*?Volume\s*\(24h\).*?</dt>.*?'
#             r'<dd\s+class="[^"]*">.*?'
#             r'<p[^>]*>\s*<svg[^>]*>.*?</svg>\s*([-+]?\d+\.\d+%)\s*</p>.*?'
#             r'(\$[0-9,.]+)',
#             re.DOTALL
#         )
#         match = re.search(pattern, self.html_content)
#         if match:
#             percentage_change = self._format_price(match.group(1))
#             volume_24h = self._format_price(match.group(2))
#             self._add("volume_24h", volume_24h)
#             self._add("volume_24h_percentage_change", percentage_change)
# 
#     def extract_volume_market_cap_ratio(self):
#         pattern = r'Volume/Market cap \(24h\).*?<dd.*?>([^<]+)<'
#         match = re.search(pattern, self.html_content, re.DOTALL)
#         if match:
#             volume_market_cap_ratio = self._format_price(match.group(1).strip())
#             self._add("volume_market_cap_ratio", volume_market_cap_ratio)
# 
#     def extract_circulating_supply(self):
#         pattern = r'Circulating supply.*?>([0-9,]+(?:\.[0-9]+)?\s*[A-Za-z]+)<\/dd>'
#         match = re.search(pattern, self.html_content, re.DOTALL)
#         if match:
#             supply = match.group(1)
#             cir_supply = re.sub(r'[A-Za-z]', '', supply).strip()
#             cir_supply = self._format_price(cir_supply)
#             self._add("circulating_supply", cir_supply)
# 
#     def extract_total_supply(self):
#         pattern = r'Total supply.*?>([0-9,]+(?:\.[0-9]+)?\s*[A-Za-z]+)<\/dd>'
#         match = re.search(pattern, self.html_content, re.DOTALL)
#         if match:
#             supply = match.group(1)
#             tot_supply = re.sub(r'[A-Za-z]', '', supply).strip()
#             tot_supply = self._format_price(tot_supply)
#             self._add("total_supply", tot_supply)
# 
#     def extract_max_supply(self):
#         pattern = r'Max\. supply.*?<dd.*?>([^<]+)<'
#         match = re.search(pattern, self.html_content, re.DOTALL)
#         if match:
#             max_supply = match.group(1).strip()
#             if max_supply == "--":
#                 self._add("max_supply", max_supply)
#             else:
#                 max_supply = re.sub(r'[A-Za-z]', '', max_supply).strip()
#                 max_supply = self._format_price(max_supply)
#                 self._add("max_supply", max_supply)
# 
#     def extract_fully_diluted_market_cap(self):
#         pattern = r'Fully diluted market cap.*?<dd.*?>([^<]+)<'
#         # pattern = r'Fully diluted market cap.*?\$([0-9,]+(?:\.[0-9]+)?)<\/dd>'
#         match = re.search(pattern, self.html_content, re.DOTALL)
#         if match:
#             fully_diluted_market_cap = match.group(1).strip()
#             if fully_diluted_market_cap == "--":
#                 self._add("fully_diluted_market_cap", fully_diluted_market_cap)
#             else:
#                 fully_diluted = re.sub(r'\$', '', fully_diluted_market_cap)
#                 fully_diluted = self._format_price(fully_diluted)
#                 self._add("fully_diluted_market_cap", fully_diluted)
# 
#     def extract_all_time_high_low(self):
#         def extract_value(pattern, html):
#             match = re.search(pattern, html, re.DOTALL)
#             if match:
#                 value = self._format_price(match.group(1))
#                 percentage_change = self._format_price(match.group(2))
#                 return value, percentage_change
#             else:
#                 return None, None
#         html_content = HTMLclean.remove_comments(self.html_content)
#         high_pattern = r'All-time high.*?\$(.*?)<\/span>.*?percentage">(.*?)<\/div>'
#         low_pattern = r'All-time low.*?\$(.*?)<\/span>.*?percentage">(.*?)<\/div>'
#         highValue, highPercent = extract_value(high_pattern, html_content)
#         lowValue, lowPercent = extract_value(low_pattern, html_content)
#         self._add("all_time_high", highValue)
#         self._add("all_time_high_percentage_change", highPercent)
#         self._add("all_time_low", lowValue)
#         self._add("all_time_low_percentage_change", lowPercent)
# 
#     def parse(self):
#         try:
#             self.set_timestamp()
#             self.extract_coin_name()
#             self.extract_coin_symbol()
#             self.extract_price_and_change()
#             self.extract_market_cap_and_change()
#             self.extract_volume_and_change()
#             self.extract_volume_market_cap_ratio()
#             self.extract_circulating_supply()
#             self.extract_total_supply()
#             self.extract_max_supply()
#             self.extract_fully_diluted_market_cap()
#             self.extract_all_time_high_low()
#         except:
#             self.error = True
# 
#     def DATA(self):
#         if not self.error:
#             return self._get("coin_name"), self.data_points
#         else:
#             return "Crypto-Currency data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
# 
#     def __dir__(self):
#         return ['DATA']





























