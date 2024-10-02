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
        self.html = html
        self.market = None
        self._exchange_text = None
        self._extract_exchange_text()

    def _extract_exchange_text(self):
        start_tag = '<span class="exchange yf-1fo0o81">'
        end_tag = '</span>'
        
        start_index = self.html.find(start_tag)
        if start_index == -1:
            return
        
        # Move the index to the end of the start tag
        start_index += len(start_tag)
        
        # Find the closing span tag
        end_index = self.html.find(end_tag, start_index)
        if end_index == -1:
            return
        
        # Extract the inner HTML
        inner_html = self.html[start_index:end_index]
        
        # Remove nested tags to get the text
        text = self._remove_tags(inner_html)
        self._exchange_text = text.strip()
        self._tokenize_and_extract_market(self._exchange_text)

    def _remove_tags(self, html):
        inside_tag = False
        text = []
        for char in html:
            if char == '<':
                inside_tag = True
            elif char == '>':
                inside_tag = False
            elif not inside_tag:
                text.append(char)
        return ''.join(text)

    def _tokenize_and_extract_market(self, text):
        tokens = text.split()
        if tokens:
            self.market = tokens[0]
       
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



       
       

def __dir__():
    return ['market_find', 'extract_company_name', 'extract_sector']

__all__ = ['market_find', 'extract_company_name', 'extract_sector']




