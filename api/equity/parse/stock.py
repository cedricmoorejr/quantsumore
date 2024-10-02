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
import pandas as pd
import numpy as np
import json
from html.parser import HTMLParser

# Custom
from ....date_parser import dtparse
from ...parse_tools import market_find, extract_company_name
from ...._http.response_utils import clean_initial_content, get_top_level_key



## Via JSON
##========================================================================
class latest:
    def __init__(self, json_content=None):
        self.cleaned_data = None  
        self.data = None
        # self.error = False       

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
        
    def _query_time(self):
        return dtparse.now(utc=True, as_unix=True) 
       
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['date'] = df['date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['firstTradeDate'] = df['firstTradeDate'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['marketTime'] = df['marketTime'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['timeQueried'] = self._query_time()
        df['timeQueried'] = df['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))        
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None or dataframe.empty:
            return False
        else:
            return True
        
    def parse(self):
        cleaned_content = self._clean_content(self.json_content)    	
        rows = []
        for entry in cleaned_content:
            result = entry['chart']['result']
            for item in result:
                meta = item['meta']
                indicators = item['indicators']
                quote = indicators.get('quote', [{}])[0]
                adjclose = indicators.get('adjclose', [{}])[0]
                
                row = {
                    "date": item.get("timestamp", [0])[0],     	
                    "currency": meta.get("currency", pd.NA),
                    "symbol": meta.get("symbol", pd.NA),
                    "exchangeName": meta.get("exchangeName", pd.NA),
                    "fullExchangeName": meta.get("fullExchangeName", pd.NA),
                    "instrumentType": meta.get("instrumentType", pd.NA),
                    "firstTradeDate": meta.get("firstTradeDate", 0),
                    "regularMarketPrice": meta.get("regularMarketPrice", 0.0),
                    "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh", 0.0),
                    "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow", 0.0),
                    "regularMarketDayHigh": meta.get("regularMarketDayHigh", 0.0),
                    "regularMarketDayLow": meta.get("regularMarketDayLow", 0.0),
                    "regularMarketVolume": meta.get("regularMarketVolume", 0),
                    "longName": meta.get("longName", pd.NA),
                    "marketTime": meta.get("regularMarketTime", 0),                      
                }
                rows.append(row)
        if rows:
            self.cleaned_data = rows

    def DATA(self):
        if not self._is_data(self.data):
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']



class historical:
    def __init__(self, json_content=None):
        self.cleaned_data = None  
        self.data = None
        # self.error = False       

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
       
    def _query_time(self):
        return dtparse.now(utc=True, as_unix=True) 
           
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['date'] = df['date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['firstTradeDate'] = df['firstTradeDate'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['marketTime'] = df['marketTime'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['timeQueried'] = self._query_time()
        df['timeQueried'] = df['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))    
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None or dataframe.empty:
            return False
        else:
            return True
        
    def parse(self):
        cleaned_content = self._clean_content(self.json_content)    	
        rows = []
        for entry in cleaned_content:
            result = entry['chart']['result']
            for item in result:
                meta = item['meta']
                timestamps = item.get('timestamp', [])
                quote = item['indicators']['quote'][0]
                adjclose = item['indicators']['adjclose'][0]

                for i, timestamp in enumerate(timestamps):
                    row = {
                        # Meta fields
                        "date": timestamp,                        
                        "currency": meta.get("currency", pd.NA),
                        "symbol": meta.get("symbol", pd.NA),
                        "exchangeName": meta.get("exchangeName", pd.NA),
                        "fullExchangeName": meta.get("fullExchangeName", pd.NA),
                        "instrumentType": meta.get("instrumentType", pd.NA),
                        "firstTradeDate": meta.get("firstTradeDate", 0),
                        # "regularMarketTime": meta.get("regularMarketTime", 0),
                        # "gmtoffset": meta.get("gmtoffset", 0),
                        # "timezone": meta.get("timezone", pd.NA),
                        # "exchangeTimezoneName": meta.get("exchangeTimezoneName", pd.NA),
                        "regularMarketPrice": meta.get("regularMarketPrice", 0.0),
                        "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh", 0.0),
                        "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow", 0.0),
                        "regularMarketDayHigh": meta.get("regularMarketDayHigh", 0.0),
                        "regularMarketDayLow": meta.get("regularMarketDayLow", 0.0),
                        "regularMarketVolume": meta.get("regularMarketVolume", 0),
                        "longName": meta.get("longName", pd.NA),
                        # "shortName": meta.get("shortName", pd.NA),
                        # "chartPreviousClose": meta.get("chartPreviousClose", 0.0),
                        # "priceHint": meta.get("priceHint", 0),
                        
                        # Timestamp and quote fields
                        "open": quote.get("open", [None])[i],
                        "low": quote.get("low", [None])[i],
                        "close": quote.get("close", [None])[i],
                        "high": quote.get("high", [None])[i],
                        "volume": quote.get("volume", [None])[i],
                        "adjclose": adjclose.get("adjclose", [None])[i],
                        "marketTime": meta.get("regularMarketTime", 0),                
                    }
                    rows.append(row)

        if rows:
            self.cleaned_data = rows

    def DATA(self):
        if not self._is_data(self.data):
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




class last:
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
        df['Timestamp'] = df['Timestamp'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        self.data = df

    def _is_data(self, dataframe):
        if dataframe is None or dataframe.empty:
            return False
        else:
            return True
        
    def parse(self):
        cleaned_content = self._clean_content(self.json_content)
        top_key = get_top_level_key(cleaned_content)
        structured_data = []
        
        try:
            data = cleaned_content[top_key]['result']
        except TypeError:
            data = cleaned_content[0][top_key]['result']
        except KeyError:
            return pd.DataFrame()
        
        for result in data:
            symbol = result['symbol']
            meta = result['response'][0]['meta']
            timestamps = result['response'][0]['timestamp']
            closes = result['response'][0]['indicators']['quote'][0]['close']
            
            for timestamp, close in zip(timestamps, closes):
                structured_data.append({
                    'Symbol': symbol,
                    'Timestamp': timestamp,
                    'Close Price': close,
                    'Market Price': meta['regularMarketPrice'],
                    'Day High': meta['regularMarketDayHigh'],
                    'Day Low': meta['regularMarketDayLow'],
                    'Volume': meta['regularMarketVolume']
                })
        if structured_data:
            self.cleaned_data = structured_data

    def DATA(self):
        if not self._is_data(self.data):
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']



## Via HTML
##========================================================================
class quote_statistics(HTMLParser):
    def __init__(self, html_content=None):
        super().__init__()
        self.found_statistics = False
        self.statistics = ''
        self.company_name = None        
        self.headers = ['Previous Close', 'Open', 'Bid', 'Ask', "Day's Range", '52 Week Range', 'Volume', 'Avg. Volume',
                				'Market Cap (intraday)', 'Beta (5Y Monthly)', 'PE Ratio (TTM)', 'EPS (TTM)', 'Earnings Date',
                				'Forward Dividend & Yield', 'Ex-Dividend Date', '1y Target Est']
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        self.exchange_type = None
        self.exchange_validation = self.validate_stock_exchange()
        
        if html_content:
            self.feed(html_content)
            self.exchange_type = market_find(html_content)
            self.company_name = extract_company_name(html_content).name            
            self.exchange_validation = self.validate_stock_exchange()

    def validate_stock_exchange(self):
        return bool(self.exchange_type and self.exchange_type.market in self.exchanges)

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attrs_dict = dict(attrs)
            if attrs_dict.get('data-testid') == 'quote-statistics':
                self.found_statistics = True
                self.statistics += self.get_starttag_text()

    def handle_endtag(self, tag):
        if self.found_statistics and tag == 'div':
            self.statistics += f"</{tag}>"
            self.found_statistics = False
            self.sanitize()

    def handle_data(self, data):
        if self.found_statistics:
            self.statistics += data

    def sanitize(self):
        """Sanitizes the parsed data and converts it into a dictionary."""
        text = self.statistics
        cleaned_div_content = re.sub(r'\s*<.*?>\s*', '', text)
        cleaned_text = re.sub(r' {3,}', '\n', cleaned_div_content)
        cleaned_text = re.sub(r'[ \t]*\n[ \t]*', '\n', cleaned_text)
        data_dict = {}
        lines = cleaned_text.split('\n')
        for line in lines:
            for key in self.headers:
                if line.startswith(key):
                    value = line[len(key):].strip()
                    data_dict[key] = value
        self.statistics = data_dict

    def DATA(self):
        """Converts the sanitized data into a pandas DataFrame."""
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.company_name, self.statistics
           
    def __dir__(self):
        return ['DATA']



class profile(HTMLParser):
    def __init__(self, html_content=None):
        super().__init__()
        # Description and executive table parsing variables
        self.found_section = False
        self.description = ''
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.headers = []
        self.current_row = []
        self.data = []
        self.is_header = False
        self.exec_table = {}
        
        # Company details parsing variables
        self.found_details_section = False
        self.company_details = ''
        self.detail_keys = ["Address", "Phone Number", "Website", "Sector", "Industry", "Full Time Employees"]
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        self.exchange_type = None
        self.company_name = None        
        self.exchange_validation = self.validate_stock_exchange()
        # Feed HTML if provided        
        if html_content:
            self.feed(html_content)
            self.exchange_type = market_find(html_content)
            self.company_name = extract_company_name(html_content).name
            self.exchange_validation = self.validate_stock_exchange()

    def validate_stock_exchange(self):
        return bool(self.exchange_type and self.exchange_type.market in self.exchanges)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'section' and attrs_dict.get('data-testid') in ['description', 'asset-profile']:
            if attrs_dict.get('data-testid') == 'description':
                self.found_section = True
            else:
                self.found_details_section = True
            self.description += self.get_starttag_text()
        elif tag == 'table' and 'yf-mj92za' in attrs_dict.get('class', ''):
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag == 'thead':
            self.is_header = True
        elif tag in ['td', 'th'] and self.in_row:
            self.in_cell = True

    def handle_endtag(self, tag):
        if self.found_section and tag == 'section':
            self.description += f"</{tag}>"
            self.found_section = False
            self.sanitize()
        elif self.found_details_section and tag == 'section':
            self.company_details += f"</{tag}>"
            self.found_details_section = False
            self.sanitize_details()
        elif tag == 'table' and self.in_table:
            self.in_table = False
            if self.headers and self.data:
                self.exec_table = self.to_dict(self.headers, self.data)
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if self.is_header:
                self.headers = self.current_row
                self.is_header = False
            else:
                self.data.append(self.current_row)
        elif tag in ['td', 'th'] and self.in_cell:
            self.in_cell = False

    def handle_data(self, data):
        if self.found_section:
            self.description += data
        if self.found_details_section:
            self.company_details += data
        if self.in_cell:
            self.current_row.append(data.strip())

    def sanitize(self):
        """Sanitizes the parsed description data."""
        cleaned_text = re.sub(r'\s*<.*?>\s*', '', self.description)
        self.description = re.sub(r'.*\s{4,}', '', cleaned_text)

    def sanitize_details(self):
        """Process and sanitize the company details."""
        text = self.company_details
        if text is None or text == '':
            return
        
        text = re.sub(r"(Sector|Industry|Full Time Employees):", r"\1", text)
        cleaned_section_content = re.sub(r'\s*<.*?>\s*', '', text).replace('\xa0', '')
        cleaned_text = re.sub(r'.*\s{4,}', '', cleaned_section_content)

        ## Get Website
        website_match = re.search(r'https?:\/\/([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}(:\d+)?(\/\S*)?', cleaned_text)
        if website_match:
            url = website_match.group(0)
            url_start_pos = website_match.start()
            insert_text = f'Website '
            new_text = cleaned_text[:url_start_pos] + insert_text + cleaned_text[url_start_pos:]

        # Get Phone Number
        phone_match = re.search(r'\b\d{1,4}(?:\s\d{1,4}){2,3}\b', new_text)
        if phone_match:
            phone_number = phone_match.group(0)
            phone_number_start_pos = phone_match.start()
            insert_text = f'Phone Number '
            new_text = new_text[:phone_number_start_pos] + insert_text + new_text[phone_number_start_pos:]

        # Find Address
        address_match = re.compile(r'^(.+?),\s*(.+?\s*\d+.*?)(?=\s*(Phone Number|Website|Sector|Industry|Full Time Employees))').search(new_text)
        if address_match:
            address = address_match.group(0)
            address_start_pos = address_match.start()
            insert_text = f'Address '
            new_text = new_text[:address_start_pos] + insert_text + new_text[address_start_pos:]
        else:
            if len(new_text) >= 7:
                new_text = 'Address ' + new_text    
        data_dict = {}
        pattern = '|'.join([re.escape(key) for key in self.detail_keys])
        parts = re.split(f"({pattern})", new_text)
        temp_dict = {}
        for i in range(1, len(parts), 2):
            temp_dict[parts[i]] = parts[i+1].strip()
        for key in self.detail_keys:
            value = temp_dict.get(key, '--')
            if key in temp_dict:
                next_key_index = min([value.find(next_key) for next_key in self.detail_keys if value.find(next_key) != -1], default=len(value))
                value = value[:next_key_index].strip()
            data_dict[key] = value
        self.company_details = data_dict

    def to_dict(self, headers, data):
        """ Converts the parsed headers and rows into a dictionary."""
        table_dict = {header: [] for header in headers}
        for row in data:
            for header, value in zip(headers, row):
                table_dict[header].append(value)
        return table_dict

    def to_dataframe(self):
        """ Converts the parsed headers and rows into a pandas DataFrame."""
        return pd.DataFrame(self.data, columns=self.headers)
       
    def DATA(self):
        """ Combines all parsed data into a single dictionary."""
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
           
        full_report = {
            "Company Name": self.company_name,        	
            "Company Description": self.description,
            "Company Details": self.company_details,
            "Company Executives": self.exec_table if self.exec_table else self.to_dataframe().to_dict(orient='list')
        }
        return full_report
       
    def __dir__(self):
        return ['DATA']



def __dir__():
    return ['historical', 'latest', 'profile', 'quote_statistics']

__all__ = ['historical', 'latest', 'profile', 'quote_statistics']




