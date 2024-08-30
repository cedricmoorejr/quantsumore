import time
import datetime
from html.parser import HTMLParser
import re
import pandas as pd
import numpy as np

# Custom
from ....tools.tool import dtparse
from ...market_utils import *
from ...parse_tools import market_find, extract_company_name

class historical:
    def __init__(self, html_content=None):
        self.html_content = html_content
        self.headers = []
        self.rows = []
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        self.exchange_type = None
        self.ticker = None        
        self.exchange_validation = self.validate_stock_exchange()
        
        if html_content:
            self.parse()
            self.exchange_type = market_find(html_content)
            self.exchange_validation = self.validate_stock_exchange()

    def validate_stock_exchange(self):
        return bool(self.exchange_type and self.exchange_type.market in self.exchanges)
        
    def parse(self):
        self.extract_ticker_content()    	
        self.extract_headers()
        self.extract_rows()

    def extract_ticker_content(self):
        pattern = re.compile(r'<section class="container yf-3a2v0c paddingRight">\s*<h1 class="[^"]+">(.*?)</h1>\s*</section>')
        company_info = pattern.search(self.html_content)
        company_name_and_symbol = company_info.group(1).strip() if company_info else None
        match = re.search(r'\(([^)]+)\)', company_name_and_symbol)
        if match:
            self.ticker = match.group(1)

    def extract_headers(self):
        header_pattern = re.compile(r'<th class="[^"]*">(.*?)</th>')
        headers = header_pattern.findall(self.html_content)
        self.headers = [self.clean_header(header) for header in headers]

    def extract_rows(self):
        row_pattern = re.compile(r'<tr class="yf-ewueuo">(.*?)</tr>', re.DOTALL)
        rows = row_pattern.findall(self.html_content)
        data_pattern = re.compile(r'<td class="yf-ewueuo">(.*?)</td>')
        
        for row in rows:
            cells = data_pattern.findall(row)
            if cells:
                cleaned_cells = [cell.strip() for cell in cells]
                if len(cleaned_cells) == 7:
                    self.rows.append(cleaned_cells)

    def clean_header(self, text):
        clean_text = re.sub(r'<[^>]*>', '', text).strip()
        clean_text = re.split(r'\s{2,}', clean_text)[0].strip()
        return clean_text
       
    def format_date(self, date_str, from_format=None, to_format=None):
        return dtparse.parse(date_str, from_format, to_format)
       
    def DATA(self):
        """ Converts the parsed headers and rows into a pandas DataFrame."""
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
           
        df = pd.DataFrame(self.rows, columns=self.headers)
        if 'Date' in df.columns:
            df['Date'] = df['Date'].apply(self.format_date)
            df = df.sort_values('Date')
            df = df.reset_index(drop=True)
            df.insert(0, 'Ticker', self.ticker)
            df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
            df['High'] = pd.to_numeric(df['High'], errors='coerce')
            df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
            df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
            df['Adj Close'] = pd.to_numeric(df['Adj Close'], errors='coerce')
            df['Volume'] = pd.to_numeric(df['Volume'].str.replace(',', ''), errors='coerce')
        return df
       
    def __dir__(self):
        return ['DATA']




class latest:
    def __init__(self, html_content=None):
        self.html_content = html_content
        self.price = None        
        self.ticker = None   
        self.latest_price = None        
        self.market_time_notice = None      
        self.stock_market_hours = self.market_status()
        self.stock_market_last = self.last_open()

        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        self.exchange_type = None
        self.exchange_validation = self.validate_stock_exchange()
        
        if html_content:
            self.parse()
            self.exchange_type = market_find(html_content)
            self.exchange_validation = self.validate_stock_exchange()

    def validate_stock_exchange(self):
        return bool(self.exchange_type and self.exchange_type.market in self.exchanges)

    def parse(self):
        self.extract_price()
        self.extract_ticker_content()
        self.extract_market_time_notice()

    def extract_price(self):
        """Extracts the regular market price from the data-value attribute."""
        price_pattern = re.compile(r'<fin-streamer[^>]+data-field="regularMarketPrice"[^>]+data-value="([^"]+)"')
        price_match = price_pattern.search(self.html_content)
        self.price = price_match.group(1) if price_match else None

    def extract_ticker_content(self):
        """Cleans the additional content to extract the desired pattern."""
        pattern = re.compile(r'<section class="container yf-3a2v0c paddingRight">\s*<h1 class="[^"]+">(.*?)</h1>\s*</section>')
        company_info = pattern.search(self.html_content)
        company_name_and_symbol = company_info.group(1).strip() if company_info else None
        match = re.search(r'\(([^)]+)\)', company_name_and_symbol)
        if match:
            self.ticker = match.group(1)

    def extract_market_time_notice(self):
        """Extracts the market time notice to extract and format the updated time."""        
        market_time_notice_pattern = re.compile(r'<div slot="marketTimeNotice"><span class="[^"]+">(.*?)</span>')
        market_time_notice = market_time_notice_pattern.search(self.html_content)
        market_time_notice_text = market_time_notice.group(1).strip() if market_time_notice else None

        if self.stock_market_hours == "closed":
            self.market_time_notice = self.stock_market_last

        elif "market open" in market_time_notice_text.lower():
            pattern = r"As of (\d+:\d+ \w+ \w+)\."
            match = re.search(pattern, market_time_notice_text)
            if match:
                time_portion = match.group(1)
                current_time = time.localtime()
                current_date = time.strftime("%Y-%m-%d", current_time)
                self.market_time_notice =  f"{current_date} {time_portion}"

    def market_status(self):
        if is_market_open():
            return "open"
        return "closed"

    def last_open(self):
        return last_open_date(format=True)

    def format_price(self, value):
        try:
            return float(value)
        except ValueError:
            return None

    def DATA(self):
        if not self.exchange_validation:
            return "Equity data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        data = {
            'ticker': [self.ticker],
            'last_price': [self.price],
            'last_updated': [self.market_time_notice]
        }
        df = pd.DataFrame(data)
        return df
       
    def __dir__(self):
        return ['DATA']



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




