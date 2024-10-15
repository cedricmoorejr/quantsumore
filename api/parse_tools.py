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
from urllib.parse import urlparse

class extract_company_name:
    def __init__(self, html):
        self.html = html
        self.name = self.extract_name()
        self.clean_company_name()

    def extract_name_from_html_1(self):
        start_tag = '<title>'
        end_tag = '</title>'
        start_pos = self.html.find(start_tag)
        end_pos = self.html.find(end_tag, start_pos)
        if start_pos != -1 and end_pos != -1:
            title_content = self.html[start_pos + len(start_tag):end_pos]
            company_name = title_content.split('(')[0].strip()
            return company_name
        return None

    def extract_name_from_html_2(self):
        title_pattern = r'<title>(.*?)\s*\(.*?</title>'
        match = re.search(title_pattern, self.html)
        if match:
            company_name = match.group(1).strip()
            return company_name
        return None

    def extract_name_from_html_3(self):
        meta_title_pattern = r'<meta\s+name="title"\s+content="(.*?)\s*\(.*?"'
        match = re.search(meta_title_pattern, self.html)
        if match:
            company_name = match.group(1).strip()
            return company_name
        return None
        
    def extract_name(self):
        for method in [self.extract_name_from_html_1, self.extract_name_from_html_2, self.extract_name_from_html_3]:
            name = method()
            if name:
                return name
        return None

    def clean_company_name(self):
        if self.name is not None:
            pattern = r'[\"\'\?\:\;\_\@\#\$\%\^\&\*\(\)\[\]\{\}\<\>\|\`\~\!\+\=\-\\\/\x00-\x1F\x7F]'
            cleaned_name = re.sub(pattern, '', self.name)
            cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
            self.name = cleaned_name.strip()
            
    def __dir__(self):
        return ['name']            
           

class market_find:
    def __init__(self, html):
        self.market = None
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        
        if html:
            self.html = html
            self._extract_exchange_text(html=html)
            
    def _extract_exchange_text(self, html):
        try:
            section_pattern = r'<div class="top yf-1s1umie">(.*?)</div>\s*</div>\s*</div>'
            section_match = re.search(section_pattern, html, re.DOTALL)

            if section_match:
                section_content = section_match.group(0)
            else:
                raise ValueError("No section match found")

            exchange_pattern = r'<span class="exchange yf-wk4yba">.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
            exchange_match = re.search(exchange_pattern, section_content, re.DOTALL)

            if exchange_match:
                exchange_info = list(exchange_match.groups())
                for exchange in self.exchanges:
                    if any(exchange in item for item in exchange_info):
                        self.market = exchange
                        break
            else:
                raise ValueError("No exchange match found")

        except Exception:
            print("No exchange match found")
            self.market = None

    def __dir__(self):
        return ['market']


       
class extract_sector:
    """ From YahooFinance """
    def __init__(self, html):
        self.sector = None
        if html:
            self.html = html
            self._sector_text = self.filter_urls(html=self.html, depth=2)
            if self._sector_text:
                self._tokenize_and_extract_sector(self._sector_text)
                
    def find_sector(self, html, depth=2):
        urls = re.findall(r'<a[^>]*data-ylk="[^"]*;sec:qsp-company-overview;[^"]*"[^>]*href="([^"]+)"', html)
        return  [f for f in urls if "sectors" in f]

    def filter_urls(self, html, depth=2):
        urls = self.find_sector(html=html)
        filtered_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            parts = path.split('/')
            if len(parts) == depth:
                filtered_urls.append(url)
        return filtered_urls
    
    def _tokenize_and_extract_sector(self, text):
        if isinstance(text, list):
            text = text[0]
        path = text.strip('/')
        tokens = path.split('/')
        sector = [f for f in tokens if "sectors" not in f]  
        if sector:
            self.sector = sector[0]
       
    def __dir__(self):
        return ['sector']


class extract_ticker:
    """ From YahooFinance """
    def __init__(self, html):
        self.ticker = None
        if html:
            self.html = html
            self.safely_find_ticker(html=html)
                
    def safely_find_ticker(self, html):
        section_pattern = r'<div class="top yf-1s1umie">(.*?)</div>\s*</div>\s*</div>'
        section_match = re.search(section_pattern, html, re.DOTALL)

        if section_match:
            section_content = section_match.group(0)

        ticker_section_match = re.search(r'<section[^>]*class="container yf-xxbei9 paddingRight"[^>]*>(.*?)</section>', section_content, re.DOTALL)        
        if ticker_section_match:
            ticker_section_content = ticker_section_match.group(1)
            s = re.sub(r'\s*<.*?>\s*', '', ticker_section_content)  
            ticker_match = re.search(r'\(([^)]+)\)$', s)
            if ticker_match:
                self.ticker = ticker_match.group(1)      
        return None


def __dir__():
    return ['market_find', 'extract_company_name', 'extract_sector', 'extract_ticker']

__all__ = ['market_find', 'extract_company_name', 'extract_sector', 'extract_ticker']




