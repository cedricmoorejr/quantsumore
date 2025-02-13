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
import pandas as pd

# Custom
from ..date_parser import dtparse
# from ..web_utils import url_encode_decode



# Precompile regex patterns for efficiency
_SCRIPT_STYLE_RE = re.compile(
    r'<(?:script|style)[^>]*>.*?</(?:script|style)>',
    flags=re.IGNORECASE | re.DOTALL
)
_COMMENT_RE = re.compile(
    r'<!--.*?-->',
    flags=re.DOTALL
)
_TAG_RE = re.compile(
    r'<[^>]+>'
)
_WHITESPACE_RE = re.compile(
    r'\s+'
)

def remove_html_tags(html_string):
    """
    Removes HTML tags, script/style blocks, and HTML comments from the input string using regex.
    """
    # 1. Remove script/style blocks
    text = _SCRIPT_STYLE_RE.sub('', html_string)
    # 2. Remove HTML comments
    text = _COMMENT_RE.sub('', text)
    # 3. Remove all remaining HTML tags
    text = _TAG_RE.sub('', text)
    # 4. Normalize whitespace
    text = _WHITESPACE_RE.sub(' ', text).strip()
    
    return text


def extract_html_element_by_keyword(html_content, keyword, tag_name="section"):
    """
    Extract an HTML element containing a specific keyword.

    This function searches the provided HTML content for the first occurrence of a given keyword.
    It then looks backwards to find the nearest opening tag of the specified tag name (default is "section")
    that appears before the keyword. Using a regex to handle nested tags of the same type, the function
    extracts and returns the entire HTML element, including its content. If the keyword or the matching tag
    is not found, or if the HTML is malformed, the function returns None.

    Args:
        html_content (str): The HTML content as a string.
        keyword (str or list): The keyword(s) to locate within the desired HTML element.
        tag_name (str): The name of the HTML tag to extract (default is "section").

    Returns:
        str or None: The full HTML element as a string if found, otherwise None.
    """
    import html as HTML

    html_content = HTML.unescape(html_content)
    
    # Determine the first occurrence of any keyword in the HTML content.
    keyword_index = -1
    found_keyword = None

    if isinstance(keyword, list):
        for key in keyword:
            index = html_content.find(key)
            if index != -1:
                found_keyword = key
                keyword_index = index
                break  # Exit as soon as a match is found

        if keyword_index == -1:
            # print("No matching keyword found in the HTML content.")
            return None
    else:
        # Locate the single keyword in the HTML content.
        keyword_index = html_content.find(keyword)
        if keyword_index == -1:
            # print("Keyword not found in the HTML content.")
            return None
        found_keyword = keyword  # Store the found keyword

    # Find the nearest opening tag (e.g., <section>) before the keyword.
    element_start_index = html_content.rfind(f"<{tag_name}", 0, keyword_index)
    if element_start_index == -1:
        # print(f"No opening <{tag_name}> tag found before the keyword '{found_keyword}'.")
        return None

    # Compile a regex to match opening or closing tags of the specified tag name.
    element_pattern = re.compile(rf"</?{tag_name}\b", re.IGNORECASE)
    nesting_depth = 0
    element_end_index = None

    # Iterate over all occurrences of the tag in the HTML.
    for match in element_pattern.finditer(html_content, element_start_index):
        tag_fragment = match.group()  # Matches either '<tag_name' or '</tag_name>'
        if tag_fragment.startswith("</"):
            nesting_depth -= 1  # Found a closing tag.
        else:
            nesting_depth += 1  # Found an opening tag.

        # When nesting depth returns to zero, we've closed the initial tag.
        if nesting_depth == 0:
            closing_bracket_index = html_content.find(">", match.start())
            if closing_bracket_index == -1:
                # print(f"Malformed HTML: closing '>' not found for <{tag_name}> tag.")
                return None
            element_end_index = closing_bracket_index
            break

    if element_end_index is None:
        # print(f"Matching closing </{tag_name}> tag not found.")
        return None

    # Extract and return the complete HTML element.
    extracted_element = html_content[element_start_index:element_end_index+1]
    return extracted_element


def extract_by_keyword(html_content, keyword, tag_name="section", first_only=True):
    """
    Extract HTML element(s) of a given tag type that contain a specific keyword.
    
    Args:
        html_content (str): The HTML content as a string.
        keyword (str or list): The keyword(s) to locate within the desired HTML element(s).
        tag_name (str): The HTML tag name to search for (default is "section").
        first_only (bool): If True, return only the first occurrence found (default).
                           If False, return a list of all matching elements.
                           
    Returns:
        str or list or None: If first_only is True, returns the first matching element as a string,
                             or None if no match is found.
                             If first_only is False, returns a list of all matching elements (as strings),
                             which may be empty if no match is found.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    matches = []
    
    for element in soup.find_all(tag_name):
        text = element.get_text()
        if isinstance(keyword, list):
            # Check if any keyword in the list appears in the element's text.
            if any(key in text for key in keyword):
                if first_only:
                    return str(element)
                else:
                    matches.append(str(element))
        else:
            if keyword in text:
                if first_only:
                    return str(element)
                else:
                    matches.append(str(element))
                    
    if first_only:
        return None
    else:
        return matches



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
           

class extract_ticker:
    """ From YahooFinance """
    def __init__(self, html):
        self.ticker = None
        if html:
            self.html = html
            self.safely_find_ticker(html=html)

    def safely_find_ticker(self, html):
        import html as HTML
        html = HTML.unescape(html_content)
        start_tag = '<title>'
        end_tag = '</title>'
        start_pos = self.html.find(start_tag)
        end_pos = self.html.find(end_tag, start_pos)
        if start_pos != -1 and end_pos != -1:
            title_content = self.html[start_pos + len(start_tag):end_pos]
            cleaned_content = HTMLclean.decode(title_content)
            match = re.search(r'\((.*?)\)', cleaned_content)
            if match:
                self.ticker = match.group(1)            
        return None


# class market_find:
#     def __init__(self, html):
#         self.market = None
#         self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
#         
#         if html:
#             self.html = html
#             self._extract_exchange_text(html=html)
#             
#     def _extract_exchange_text(self, html):
#         try:
#             section_pattern = r'<div class="top yf-1s1umie">(.*?)</div>\s*</div>\s*</div>'
#             section_match = re.search(section_pattern, html, re.DOTALL)
# 
#             if section_match:
#                 section_content = section_match.group(0)
#             else:
#                 raise ValueError("No section match found")
# 
#             exchange_pattern = r'<span class="exchange yf-wk4yba">.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
#             exchange_match = re.search(exchange_pattern, section_content, re.DOTALL)
# 
#             if exchange_match:
#                 exchange_info = list(exchange_match.groups())
#                 for exchange in self.exchanges:
#                     if any(exchange in item for item in exchange_info):
#                         self.market = exchange
#                         break
#             else:
#                 raise ValueError("No exchange match found")
# 
#         except Exception:
#             print("No exchange match found")
#             self.market = None
# 
#     def __dir__(self):
#         return ['market']

class market_find:
    def __init__(self, html):
        self.market = None
        self.exchanges = ['NasdaqGS', 'NYSE', 'NYSEArca']
        
        if html:
            self.html = html
            self._extract_exchange_text(html=html)
            
    def _extract_exchange_text(self, html):
        try:
            section = extract_html_element_by_keyword(html, keyword=[e + " - " for e in self.exchanges], tag_name="section")    
            text = extract_html_element_by_keyword(section, keyword=self.exchanges, tag_name="span")
            text_clean = remove_html_tags(text)

            if text_clean:
                # Check which exchange name the text starts with
                self.market = next((exchange for exchange in self.exchanges if text_clean.startswith(exchange)), None)
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


       
class isDelisted:
    """ From YahooFinance """	
    def __init__(self, html):
        self.listed = True
        self.exchange_verify = 'YHD - Delayed Quote'
        
        if html:
            self.html = html
            self._extract_exchange_text(html=html)
            
    def _extract_exchange_text(self, html):
        try:
            section_pattern = r'<div class="top yf-1s1umie">(.*?)</div>\s*</div>\s*</div>'
            section_match = re.search(section_pattern, html, re.DOTALL)
            if not section_match:
                raise ValueError("No section match found")
            section_content = section_match.group(0)
            exchange_pattern = r'<span class="exchange yf-wk4yba">.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
            exchange_match = re.search(exchange_pattern, section_content, re.DOTALL)

            if not exchange_match:
                raise ValueError("No exchange match found")
            exchange_info = list(exchange_match.groups())
            if any(self.exchange_verify in item for item in exchange_info):
                self.listed = False
        except Exception:
            self.listed = True
    def __dir__(self):
        return ['listed']



def convert_to_float(value, roundn=0):
    """
    Converts a given string value to a float after removing any dollar signs and commas,
    except when the string contains a percentage sign or a slash, in which case the original
    string is returned unchanged.

    Args:
    value (str): The string value to convert.
    roundn (int): The number of decimal places to round the float to; if 0, rounding is skipped.

    Returns:
    float or str: Returns the float conversion if applicable, rounded as specified, 
                  or the original value if it contains '%' or '/'.
    """
    try:
        cleaned_value = re.sub(r'[\$,]', '', value)
        
        if '%' in cleaned_value or '/' in cleaned_value:
            return value
        
        float_value = float(cleaned_value)
        return round(float_value, roundn) if roundn else float_value
    except ValueError:
        return value

def convert_date(date, from_format=None, to_format='%Y-%m-%d %H:%M:%S', to_unix_timestamp=False):
    try:
        dt = dtparse.parse(date_input=str(date), from_format=from_format, to_format=to_format, to_unix_timestamp=to_unix_timestamp)
        return dt
    except:
        return date
       
def parse_scaled_number(input_string):
    input_string = input_string.replace(',', '')
    if input_string.endswith('T'):
        return float(input_string[:-1]) * 1_000_000_000_000
    elif input_string.endswith('B'):
        return float(input_string[:-1]) * 1_000_000_000
    elif input_string.endswith('M'):
        return float(input_string[:-1]) * 1_000_000
    else:
        return float(input_string)

def extract_symbol_from_url(url):
    if isinstance(url, list) and len(url) == 1:
        if isinstance(url[0], str):
            url = url[0]    
    match = re.search(r'(?:\/|\?|&|symbols=)([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[\/\?&]|$)', url)
    return match.group(1) if match else None

def extract_currency_pair_from_url(url):
    if isinstance(url, list) and len(url) == 1:
        if isinstance(url[0], str):
            url = url[0]       
    pattern = r'ratepair=([A-Z]+)|/quotes/%5E([A-Z]+)'
    match = re.search(pattern, url, re.IGNORECASE)
    if match:
        return match.group(1) if match.group(1) is not None else match.group(2)
    else:
        return None
       
def extract_slug_from_url(url):
    if isinstance(url, list) and len(url) == 1:
        if isinstance(url[0], str):
            url = url[0]       
    match = re.search(r'slug=([^&]+)', url)
    return match.group(1) if match else None

def extract_cryptoID_from_url(url):
    if isinstance(url, list) and len(url) == 1:
        if isinstance(url[0], str):
            url = url[0]       
    match = re.search(r'id=(\d+)', url)
    if match:
        return int(match.group(1)) 
    else:
        return None
       
def convert_to_yield(dyield):
    if dyield is None:
        return None
    if isinstance(dyield, str) and dyield.endswith('%'):
        dyield = dyield.replace('%', '')
        if dyield.replace('.', '', 1).isdigit():
            dyield = float(dyield) / 100
        else:
            return None 
    elif isinstance(dyield, str):
        if dyield.replace('.', '', 1).isdigit():
            dyield = float(dyield)
        else:
            return None
    if isinstance(dyield, (float, int)):
        return round(dyield, 4)
    return None






def __dir__():
    return ['market_find', 'extract_company_name', 'extract_sector', 'extract_ticker', 'isDelisted', 'extract_html_element_by_keyword', 'remove_html_tags', 'extract_by_keyword']

__all__ = ['market_find', 'extract_company_name', 'extract_sector', 'extract_ticker', 'isDelisted', 'extract_html_element_by_keyword', 'remove_html_tags', 'extract_by_keyword']



