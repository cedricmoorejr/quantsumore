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

# Custom
from ....date_parser import dtparse
from ...parse_tools import market_find, extract_company_name, extract_ticker
from ...._http.response_utils import clean_initial_content
from ....strata_utils import IterDict
from ....web_utils import HTMLclean


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
        top_key = IterDict.top_key(cleaned_content, exclusion='error', exclusion_sensitive=True) 
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
class quote_statistics:
    def __init__(self, html_content=None):
        self.statistics = None
        self.company_name = ''    
        self.target_fields = [
            'Previous Close', 'Open', 'Bid', 'Ask', "Day's Range", '52 Week Range', 'Volume', 'Avg. Volume',
            'Market Cap (intraday)', 'Beta (5Y Monthly)', 'PE Ratio (TTM)', 'EPS (TTM)', 'Earnings Date',
            'Forward Dividend & Yield', 'Ex-Dividend Date', '1y Target Est'
        ]
        
        if html_content:
            self.html_content = HTMLclean.decode(html_content)
            self.company_name = extract_company_name(self.html_content).name
            self.exchange_validation = self.validate_stock_exchange(self.html_content)
            self.parse(html=self.html_content, company_name=self.company_name)
            
    def validate_stock_exchange(self, html):
        market = market_find(html).market
        return market is not None

    def extract_stats(self, html, company_name):
        pattern = r'<span class="label yf-mrt107">(.*?)</span>\s*<span class="value yf-mrt107">(.*?)</span>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        if matches:
            cleaned_data = [(label, re.sub(r'<.*?>', '', value)) for label, value in matches]
            company_name = company_name if isinstance(company_name, str) else ''            
            statistics_dict = {label: value.strip() for label, value in cleaned_data}
            self.statistics = statistics_dict

    def extract_stats_retry(self, html, company_name):
        container_pattern = r'(<div[^>]*>.*?</div>)'
        containers = re.findall(container_pattern, html, re.DOTALL)
        matched_html = ""

        for container in containers:
            if '<ul' in container and '<li' in container:
                found_fields = [field for field in self.target_fields if field in container]
                
                if found_fields:
                    matched_html += container + "\n"
        
        if matched_html:
            matched_html = HTMLclean.decode(matched_html)
            self.extract_stats(matched_html, company_name)

    def parse(self, html, company_name):
        self.extract_stats(html, company_name)        
        if not self.statistics:
            print("Primary extraction failed. Attempting backup extraction...")
            self.extract_stats_retry(html, company_name)
                    
    def DATA(self):
        """Converts the sanitized data into a pandas DataFrame or returns error message."""
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.company_name, self.statistics
           
    def __dir__(self):
        return ['DATA']


class profile:
    def __init__(self, html_content=None):
        self.company_description = 'Not found.'        
        self.detail_keys = ["Address", "Phone Number", "Website", "Sector", "Industry", "Full Time Employees"]        
        self.company_details = {key: None for key in self.detail_keys}
        self.company_execs = pd.DataFrame([['Not found'] * 5], columns=['Name', 'Title', 'Pay', 'Exercised', 'Year Born'])       
        
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        self.exchange_type = None
        self.company_name = None        
        self.exchange_validation = self.validate_stock_exchange()
     
        if html_content:
            self.html_content = html_content
            self.exchange_type = market_find(self.html_content)
            self.company_name = extract_company_name(html_content).name
            self.exchange_validation = self.validate_stock_exchange()
            self.parse(self.html_content)

    def validate_stock_exchange(self):
        return bool(self.exchange_type and self.exchange_type.market in self.exchanges)

    def extract_bio(self, html):
        company_bio_pattern = r'<section[^>]*data-testid="description"[^>]*>.*?<p>(.*?)</p>'
        company_bio_match = re.search(company_bio_pattern, html, re.DOTALL)
        if company_bio_match:
            self.company_description = company_bio_match.group(1)

    def extract_details(self, html):
        section_pattern = r'<section[^>]*data-testid="asset-profile"[^>]*>(.*?)</section>'
        section_match = re.search(section_pattern, html, re.DOTALL)
        if section_match:
            section_content = section_match.group(0)

            address_pattern = r'<div class="address yf-wxp4ja">\s*((<div>.*?<\/div>\s*)+)<\/div>'
            phone_pattern = r'<a[^>]+href="tel:([^"]+)"'
            website_pattern = r'<a[^>]+href="(https?://[^"]+)"[^>]*aria-label="website link"'
            sector_pattern = r'Sector:\s*</dt>\s*<dd><a[^>]*>([^<]+)<\/a>'
            industry_pattern = r'Industry:\s*</dt>\s*<a[^>]*>([^<]+)<\/a>'
            employees_pattern = r'Full Time Employees:\s*</dt>\s*<dd><strong>([\d,]+)<\/strong>'

            address = re.search(address_pattern, section_content)
            address_text = ', '.join(part.strip() for part in re.findall(r'<div>(.*?)<\/div>', address.group(1))) if address else 'Not found'

            phone = re.search(phone_pattern, section_content)
            phone_text = phone.group(1).strip() if phone else 'Not found'

            website = re.search(website_pattern, section_content)
            website_text = website.group(1).strip() if website else 'Not found'

            sector = re.search(sector_pattern, section_content)
            sector_text = sector.group(1).strip() if sector else 'Not found'

            industry = re.search(industry_pattern, section_content)
            industry_text = industry.group(1).strip() if industry else 'Not found'

            employees = re.search(employees_pattern, section_content)
            employees_text = employees.group(1).strip() if employees else 'Not found'

            # Updating dictionary with found data
            self.company_details.update({
                "Address": address_text,
                "Phone Number": phone_text,
                "Website": website_text,
                "Sector": sector_text,
                "Industry": industry_text,
                "Full Time Employees": employees_text
            })

    def extract_execs(self, html):
        section_pattern = r'<section[^>]*data-testid="key-executives"[^>]*>(.*?)</section>'
        section_match = re.search(section_pattern, html, re.DOTALL)
        if section_match:
            section_content = section_match.group(0)

            headers_pattern = r'<th[^>]*>(.*?)</th>'
            headers = re.findall(headers_pattern, section_content)

            if headers:
                headers_cleaned = [re.sub(r'\s*<.*?>\s*', '', f) for f in headers]
                table_rows = []
                row_pattern = r'<tr[^>]*>(.*?)</tr>'
                row_matches = re.findall(row_pattern, section_content, re.DOTALL)
                cell_pattern = r'<td[^>]*>(.*?)</td>'

                for row in row_matches:
                    cells = re.findall(cell_pattern, row)
                    if cells:
                        table_rows.append(cells)
                        
            if table_rows:
                self.company_execs = pd.DataFrame(table_rows, columns=headers_cleaned)
                                
    def parse(self, html):
        self.extract_bio(html)
        self.extract_details(html)
        self.extract_execs(html)  
       
    def DATA(self):
        """ Combines all parsed data into a single dictionary."""
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
           
        full_report = {
            "Company Name": self.company_name,        	
            "Company Description": self.company_description,
            "Company Details": self.company_details,
            "Company Executives": self.company_execs
        }
        return full_report
       
    def __dir__(self):
        return ['DATA']


def __dir__():
    return ['historical', 'latest', 'profile', 'quote_statistics']

__all__ = ['historical', 'latest', 'profile', 'quote_statistics']




