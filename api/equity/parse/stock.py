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
from copy import deepcopy

# Custom
from ....date_parser import dtparse
from ...._http.response_utils import validateHTMLResponse
from ....strata_utils import IterDict
from ....web_utils import HTMLclean
from ...parse_tools import(
    market_find,
    extract_company_name,
    extract_ticker,
    convert_to_float, 
    convert_date, 
    parse_scaled_number,
    extract_symbol_from_url,
    extract_html_element_by_keyword
)

from ...shape_tools import(
    filter_dataframe_columns, 
    rename_dataframe_columns, 
    apply_conversion_to_columns, 
    is_valid_dataframe
)


## Via JSON
##========================================================================
class ipo:
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
            for message in self.error_messages:
                print(message)
                
    def check_data(self):
        json_content = self.json_content
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
                        if 'message' in key.lower():
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
        
        validate_ipo_data = IterDict.find(json_content, target_key='totalResults')
        if validate_ipo_data > 0:
            self.error = False

        error_messages_list = process_messages(json_content)             
        if len(error_messages_list)  ==1 and error_messages_list[0] == 'Upcoming:No record found.':
            error_messages_list = []            
            self.error_messages = error_messages_list
        
    def parse(self):
        try:
            data = IterDict.extract_from(self.json_content)
            df = pd.DataFrame(data)
            df = filter_dataframe_columns(df, column_names=['proposedTickerSymbol', 'companyName', 'proposedExchange', 'proposedSharePrice', 'sharesOffered', 'pricedDate', 'dollarValueOfSharesOffered'])
            df = rename_dataframe_columns(
                df,
                rename_dict={
                    'proposedTickerSymbol': 'Ticker_Symbol',
                    'companyName': 'Company_Name',
                    'proposedExchange': 'Exchange',
                    'proposedSharePrice': 'IPO_Price',
                    'sharesOffered': 'Shares_Offered',
                    'pricedDate': 'IPO_Date',
                    'dollarValueOfSharesOffered': 'Total_Offer_Amount'
                }
            )
            converted_data = apply_conversion_to_columns(df, 'Total_Offer_Amount', fun=convert_to_float)
            converted_data = apply_conversion_to_columns(converted_data, 'IPO_Date', fun=convert_date)
            self.data = converted_data
        except:
            self.data = None
            
    def DATA(self):
        if not is_valid_dataframe(self.data):
            if not self.error_messages:
                return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




class latest:
    def __init__(self, json_content=None):
        self.cleaned_data = None  
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

                if self.cleaned_data:
                    self._create_dataframe()

    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')                       

    def check_data(self):
        json_content = self.json_content
        def verify_price_data(price_datasets):
            acceptable_data = []
            for entry in price_datasets:
                (url, response_info), = entry.items()

                if 'error' in response_info and response_info['error'] is not None:
                    acceptable_data.append((url, False))
                else:
                    acceptable_data.append((url, True))
            return acceptable_data
           
        validate_price_data = verify_price_data(json_content)
        error_messages_list = []

        for url, check in validate_price_data:
            if not check: 
                ticker = extract_symbol_from_url(url)
                data = IterDict.find(json_content, target_key=url)
                message = "Stock was either Delisted or Acquired." 
                error_messages_list.append((ticker, message))
                
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_price_data if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False
       
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['date'] = df['date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['firstTradeDate'] = df['firstTradeDate'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['marketTime'] = df['marketTime'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['timeQueried'] = dtparse.now(utc=True, as_unix=True) 
        df['timeQueried'] = df['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))        
        self.data = df
        
    def parse(self):
        cleaned_content = IterDict.find(self.json_content, first_only=False, target_key="response", wrap=False)    	
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
        if not is_valid_dataframe(self.data):
            if not self.error_messages:              	
                return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']



class historical:
    def __init__(self, json_content=None):
        self.cleaned_data = None  
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

                if self.cleaned_data:
                    self._create_dataframe()
                    
    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')                       

    def check_data(self):
        json_content = self.json_content
        def verify_price_data(price_datasets):
            acceptable_data = []
            for entry in price_datasets:
                (url, response_info), = entry.items()

                if 'error' in response_info and response_info['error'] is not None:
                    acceptable_data.append((url, False))
                else:
                    acceptable_data.append((url, True))
            return acceptable_data

        validate_price_data = verify_price_data(json_content)
        error_messages_list = []

        for url, check in validate_price_data:
            if not check: 
                ticker = extract_symbol_from_url(url)
                data = IterDict.find(json_content, target_key=url)
                message = "Stock was either Delisted or Acquired." 
                error_messages_list.append((ticker, message))
                
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_price_data if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False
           
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['date'] = df['date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['firstTradeDate'] = df['firstTradeDate'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['marketTime'] = df['marketTime'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        df['timeQueried'] = dtparse.now(utc=True, as_unix=True) 
        df['timeQueried'] = df['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))    
        self.data = df

    def parse(self):
        cleaned_content = IterDict.find(self.json_content, first_only=False, target_key="response", wrap=False)    	
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
        if not is_valid_dataframe(self.data):
            if not self.error_messages:
                return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




class last:
    def __init__(self, json_content=None):
        self.cleaned_data = None          
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

                if self.cleaned_data:
                    self._create_dataframe()
                    
    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')                       

    def check_data(self):
        json_content = self.json_content
        def verify_price_data(price_datasets):
            acceptable_data = []
            for entry in price_datasets:
                (url, response_info), = entry.items()
                if 'error' in response_info and response_info['error'] is not None:
                    acceptable_data.append((url, False))
                else:
                    acceptable_data.append((url, True))
            return acceptable_data

        validate_price_data = verify_price_data(json_content)
        error_messages_list = []

        for url, check in validate_price_data:
            if not check: 
                ticker = extract_symbol_from_url(url)
                data = IterDict.find(json_content, target_key=url)
                message = "Stock was either Delisted or Acquired." 
                error_messages_list.append((ticker, message))
                
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_price_data if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False
           
    def _create_dataframe(self):
        rows = self.cleaned_data
        df = pd.DataFrame(rows)
        df['Timestamp'] = df['Timestamp'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        self.data = df
        
    def parse(self):
        cleaned_content = IterDict.extract_from(self.json_content, target_keys={'symbol', 'response'})
        structured_data = []
        
        for result in cleaned_content:
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
        if not is_valid_dataframe(self.data):
            if not self.error_messages:
                return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.data

    def __dir__(self):
        return ['DATA']




#────────── Via HTML ───────────────────────────────────────────────────────────────────────────────────
class quote_statistics:
    def __init__(self, html_content=None):
        self.statistics = None
        self.company_name = ''
        self.target_fields = [
            'Previous Close', 'Open', 'Bid', 'Ask', "Day's Range", '52 Week Range', 'Volume', 'Avg. Volume',
            'Market Cap (intraday)', 'Beta (5Y Monthly)', 'PE Ratio (TTM)', 'EPS (TTM)', 'Earnings Date',
            'Forward Dividend & Yield', 'Ex-Dividend Date', '1y Target Est'
        ]
        self.error = True

        if html_content:
            self.url = IterDict.top_key(html_content)        	
            self.html_content = IterDict.HTMLcontent(html_content) 
            if self.html_content:
                self.html_content = HTMLclean.decode(self.html_content)
                self.validate_content(self.html_content)
                if not self.error:                
                    self.company_name = extract_company_name(self.html_content).name
                    self.parse(html=self.html_content, company_name=self.company_name)

    def validate_content(self, html):
        self.error = False

        # Validate stock exchange
        market = market_find(html).market
        if not market:
            self.error = True

        # Validate if correct html content
        identifier = self.url
        if identifier:
            identifier = extract_symbol_from_url(identifier)
            html_check = validateHTMLResponse(html).equity(ticker=identifier)
            if not html_check:
                self.error = True
        
    # def extract_stats(self, html, company_name):
    #     containers = re.findall(r'(<div[^>]*>.*?</div>)', html, re.DOTALL)
    #     matched_html = ""
    # 
    #     for container in containers:
    #         if '<ul' in container and '<li' in container:
    #             found_fields = [field for field in self.target_fields if field in container]                
    #             if found_fields:
    #                 matched_html += container + "\n"
    #     if matched_html:
    #         matched_html = HTMLclean.decode(matched_html)
    #         matches = re.findall(r'<span class="label yf-mrt107">(.*?)</span>\s*<span class="value yf-mrt107">(.*?)</span>', matched_html, re.DOTALL) 
    #         if matches:
    #             cleaned_data = [(label, re.sub(r'<.*?>', '', value)) for label, value in matches]
    #             company_name = company_name if isinstance(company_name, str) else ''  
    #             statistics_dict = {label: value.strip() for label, value in cleaned_data}
    #             self.statistics = statistics_dict                
    #     return None

    def extract_stats(self, html, company_name):
        section_content = extract_html_element_by_keyword(html, "quote-statistics", tag_name="div")
        containers = re.findall(r'(<div[^>]*>.*?</div>)', section_content, re.DOTALL)
        matched_html = ""

        for container in containers:
            if '<ul' in container and '<li' in container:
                found_fields = [field for field in self.target_fields if field in container]                
                if found_fields:
                    matched_html += container + "\n"
                    
        if matched_html:
            matched_html = HTMLclean.decode(matched_html)

            stats = {}
            # Find each <li> ... </li> block (non-greedy)
            li_blocks = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL)
            
            for block in li_blocks:
                # Extract the label using a regex that targets the <span> with class "label"
                label_match = re.search(
                    r'<span[^>]*class="[^"]*\blabel\b[^"]*"[^>]*>(.*?)</span>',
                    block,
                    re.DOTALL
                )
                # Extract the value using a regex that targets the <span> with class "value"
                value_match = re.search(
                    r'<span[^>]*class="[^"]*\bvalue\b[^"]*"[^>]*>(.*?)</span>',
                    block,
                    re.DOTALL
                )
                
                if label_match and value_match:
                    label = label_match.group(1).strip()
                    value_html = value_match.group(1).strip()
                    # Remove any inner HTML tags from the value (for example, <fin-streamer> tags)
                    value = re.sub(r'<[^>]+>', '', value_html).strip()
                    stats[label] = value
                self.statistics = stats
               
        return None

    def parse(self, html, company_name):
        self.extract_stats(html, company_name)

    def DATA(self):
        """Converts the sanitized data into a pandas DataFrame or returns error message."""
        if self.error:
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
        self.company_name = None        
        self.error = True

        if html_content:
            self.url = IterDict.top_key(html_content)        	
            self.html_content = IterDict.HTMLcontent(html_content) 
            if self.html_content:
                self.html_content = HTMLclean.decode(self.html_content)
                self.validate_content(self.html_content)
                if not self.error:                
                    self.company_name = extract_company_name(self.html_content).name
                    self.parse(html=self.html_content)

    def validate_content(self, html):
        self.error = False

        # Validate stock exchange
        market = market_find(html).market
        if not market:
            self.error = True

        # Validate if correct html content
        identifier = self.url
        if identifier:
            identifier = extract_symbol_from_url(identifier)
            html_check = validateHTMLResponse(html).equity(ticker=identifier)
            if not html_check:
                self.error = True

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
        """Converts the sanitized data into a pandas DataFrame or returns error message."""
        if self.error:
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




