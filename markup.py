# -*- coding: utf-8 -*-
#
## ╭────────────────────────────────────────────────────────────────────────────────────────────╮
## │  Library         : doydl's Finance API Client — quantsumore                                 │
## │                                                                                             │
## │                                                                                             │
## │  Description     : `quantsumore` is a comprehensive Python library designed to streamline   │
## │                    the process of accessing and analyzing real-time financial data across   │
## │                    various markets. It provides specialized API clients to fetch data       │
## │                    from multiple financial instruments, including:                          │
## │                      - Cryptocurrencies                                                     │
## │                      - Equities and Stock Markets                                           │
## │                      - Foreign Exchange (Forex)                                             │
## │                      - Treasury Instruments                                                 │
## │                      - Consumer Price Index (CPI) Metrics                                   │
## │                                                                                             │
## │                    The library offers a unified interface for retrieving diverse financial  │
## │                    data, enabling users to perform in-depth financial and technical         │
## │                    analysis. Whether you're developing trading algorithms, conducting       │
## │                    market research, or building financial dashboards, `quantsumore` serves  │
## │                    as a reliable and efficient tool in your data pipeline.                  │
## │                                                                                             │
## │                                                                                             │
## │  Key Features    : - Real-time data retrieval from multiple financial markets               │
## │                    - Support for various financial instruments and metrics                  │
## │                    - Simplified API clients for ease of integration                         │
## │                    - Designed for both personal and non-commercial use                      │
## │                                                                                             │
## │                                                                                             │
## │  Legal Disclaimer: `quantsumore` is an independent Python library and is not affiliated     │
## │                    with any financial institutions or data providers. Likewise, doydl       │
## │                    technologies is not affiliated with, endorsed by, or sponsored by any    │
## │                    government, corporate, or financial institutions. Users should verify    │
## │                    the accuracy of the data obtained and consult professional advice        │
## │                    before making investment decisions.                                      │
## │                                                                                             │
## │                                                                                             │
## │  Copyright       : © 2023–2025 by doydl technologies. All rights reserved.                  │
## │                                                                                             │
## │                                                                                             │
## │  License         : Licensed under the Apache License, Version 2.0 (the "License");          │
## │                    you may not use this file except in compliance with the License.         │
## │                    You may obtain a copy of the License at:                                 │
## │                                                                                             │
## │                        http://www.apache.org/licenses/LICENSE-2.0                           │
## │                                                                                             │
## │                    Unless required by applicable law or agreed to in writing, software      │
## │                    distributed under the License is distributed on an "AS IS" BASIS,        │
## │                    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or          │
## │                    implied. See the License for the specific language governing             │
## │                    permissions and limitations under the License.                           │
## ╰────────────────────────────────────────────────────────────────────────────────────────────╯
#

import html as std_html
import re
from urllib.parse import parse_qs
# import json
# from collections.abc import Mapping, Sequence
# from abc import ABC, abstractmethod

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
# # from .proxy import Proxy


__all__ = [
    'url_encode_decode',
    'HTMLclean',
    'idextract',    
]


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# # Replace the real import with a lazy proxy
# BeautifulSoup = Proxy("bs4", "BeautifulSoup") # Third-party library imports (from PyPI or other package sources) 

class HTMLCleaner:
    def __init__(self):
        self.html_comment_pattern = re.compile(r'<!--.*?-->', flags=re.DOTALL)
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U0001F1E0-\U0001F1FF"  # Flags
            "]+", flags=re.UNICODE
        )
        self.newline_tab_pattern = re.compile(r'\\[ntr]|[\n\t\r]')
        self.space_pattern = re.compile(r'\s+')

    def remove_comments(self, html):
        return self.html_comment_pattern.sub('', html)

    def remove_emojis(self, text):
        return self.emoji_pattern.sub('', text)

    def decode(self, html):
        text = self.newline_tab_pattern.sub('', html)
        text = self.space_pattern.sub(' ', text).strip()
        decoded_text = std_html.unescape(text)
        return decoded_text
       
    def __dir__(self):
        return ['remove_comments','remove_emojis', 'decode']


class URLEncoderDecoder:
    def __init__(self):
        self.encoding_dict = {
            "%20": " ",   "%21": "!",   "%22": "\"",  "%23": "#",   "%24": "$",
            "%25": "%",   "%26": "&",   "%27": "'",   "%28": "(",   "%29": ")",
            "%2A": "*",   "%2B": "+",   "%2C": ",",   "%2D": "-",   "%2E": ".",
            "%2F": "/",   "%3A": ":",   "%3B": ";",   "%3C": "<",   "%3D": "=",
            "%3E": ">",   "%3F": "?",   "%40": "@",   "%5B": "[",   "%5C": "\\",
            "%5D": "]",   "%5E": "^",   "%5F": "_",   "%60": "`",   "%7B": "{",
            "%7C": "|",   "%7D": "}",   "%7E": "~"
        }
        self.inverted_encoding_dict = {v: k for k, v in self.encoding_dict.items()}
        
    def is_valid_url(self, url):
        url_pattern = re.compile(
            r'^(https?|ftp):\/\/'  # protocol
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
            r'(?::\d+)?'  # port
            r'(?:\/?|[\/?]\S+)$', re.IGNORECASE) 
        return re.match(url_pattern, url) is not None

    def decode_url(self, encoded_url):
        decoded_url = encoded_url
        for encoded_char, decoded_char in self.encoding_dict.items():
            decoded_url = decoded_url.replace(encoded_char, decoded_char)
        return decoded_url

    def encode_url(self, url, chars_to_encode=None):
        match = re.match(r'^(https?://)', url)
        protocol = match.group(1) if match else ''
        url = url[len(protocol):] 
        encoded_url = protocol 
        for char in url:
            if chars_to_encode is not None and char not in chars_to_encode:
                encoded_url += char 
            elif char in self.inverted_encoding_dict:
                encoded_url += self.inverted_encoding_dict[char]
            else:
                encoded_url += char
        return encoded_url

    def encode_str(self, i, chars_to_encode=None, join_char=","):
        if not isinstance(i, list):
            i = [i]
        if chars_to_encode:
            if not isinstance(chars_to_encode, list):
                chars_to_encode = [chars_to_encode]
        encoded_list = []
        for item in i:
            encoded_item = ""
            for char in item:
                if chars_to_encode is not None and char not in chars_to_encode:
                    encoded_item += char
                elif char in self.inverted_encoding_dict:
                    encoded_item += self.inverted_encoding_dict[char]
                else:
                    encoded_item += char
            encoded_list.append(encoded_item)
        if join_char in self.inverted_encoding_dict and (chars_to_encode is None or join_char in chars_to_encode):
            encoded_join_char = self.inverted_encoding_dict[join_char]
        else:
            encoded_join_char = join_char
        return encoded_join_char.join(encoded_list)
       
       
# ────────── Instrument Extractors ────────────  
class identifier:
    SYMBOL          = 'symbol'
    CURRENCY_PAIR   = 'currency_pair'
    CRYPTO_SLUG     = 'slug'
    CRYPTO_ID       = 'crypto_id'

    def __init__(self):
        self._extractors = {
            self.SYMBOL:        self._extract_symbol,
            self.CURRENCY_PAIR: self._extract_currency_pair,
            self.CRYPTO_SLUG:   self._extract_slug,
            self.CRYPTO_ID:     self._extract_crypto_id,
        }

    def extract(self, url, instrument):
        """
        Extract the code for the given instrument from the URL.

        instrument must be one of:
          - identifier.SYMBOL
          - identifier.CURRENCY_PAIR
          - identifier.CRYPTO_SLUG
          - identifier.CRYPTO_ID

        Returns the extracted string (or int for CRYPTO_ID) or None.
        """
        fn = self._extractors.get(instrument)
        if not fn:
            raise ValueError(f"No extractor for '{instrument}'")
        return fn(url)

    def _unwrap(self, url):
        if isinstance(url, list) and len(url) == 1 and isinstance(url[0], str):
            return url[0]
        return url

    def _extract_symbol(self, url):
        url = self._unwrap(url)
        after_plus = url.split('+', 1)[1] if '+' in url else url
        # 1) first segment before / ? or &
        seg = re.split(r'[/?&]', after_plus, 1)[0]
        if re.fullmatch(r'[A-Z]{1,4}[-.^]?[A-Z]{0,4}', seg):
            return seg.upper()
        # 2) /stocks/FOO/...
        m = re.search(r'/stocks/([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[/?&]|$)', after_plus)
        if m: return m.group(1).upper()
        # 3) ?symbols=FOO or &symbols=FOO
        m = re.search(r'[?&]symbols=([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[/?&]|$)', after_plus)
        if m: return m.group(1).upper()
        # 4) screener f=s-is-%2524FOO
        m = re.search(r'f=s-is-%2524([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[&]|$)', after_plus)
        if m: return m.group(1).upper()
        # 5) generic catch‑all
        m = re.search(r'(?:/|[?&]|symbols=)([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[/?&]|$)', after_plus)
        return m.group(1).upper() if m else None

    def _extract_slug(self, url):
        url = self._unwrap(url)
        m = re.search(r'slug=([^&]+)', url)
        return m.group(1) if m else None

    def _extract_crypto_id(self, url):
        url = self._unwrap(url)
        m = re.search(r'id=(\d+)', url)
        return int(m.group(1)) if m else None

    def _extract_currency_pair(self, url):
        url = self._unwrap(url)
        after_plus = url.split('+', 1)[1] if '+' in url else url
        # 1) before any / or ?
        seg = re.split(r'[/?]', after_plus, 1)[0]
        if re.fullmatch(r'[A-Za-z]{6}', seg):
            return seg.upper()
        # 2) ?ratepair=EURUSD
        qs = after_plus.lstrip('?')
        params = parse_qs(qs)
        if 'ratepair' in params and params['ratepair']:
            pair = params['ratepair'][0]
            if re.fullmatch(r'[A-Za-z]{6}', pair):
                return pair.upper()
        # 3) /quotes/%5EFOO
        m = re.search(r'/quotes/%5E([A-Za-z]+)', after_plus)
        return m.group(1).upper() if m else None

    def __dir__(self):
        return ['extract']       
       
# Instantiate objects
url_encode_decode = URLEncoderDecoder()
HTMLclean = HTMLCleaner()
idextract = identifier()

def __dir__():
    return __all__



# # HTML‐detection logic
# # ————————————————————————————————————
# _HTML_DOCTYPE_RE = re.compile(r'^\s*<!doctype\s+html', re.I)
# _HTML_TAG_RE     = re.compile(r'<html\b', re.I)

# def is_html_string(s: str) -> bool:
#     if not isinstance(s, str):
#         return False    
#     head = s[:1024]
#     if _HTML_DOCTYPE_RE.match(head) or _HTML_TAG_RE.search(head):
#         return True
#     # only now do we import/parse
#     return bool(BeautifulSoup(s, 'html.parser').find('html'))


# # Recursive finders
# # ————————————————————————————————————
# def find_html_strings(obj):
#     """
#     Recursively traverse nested dicts/lists and yield any strings
#     that pass `is_html_string`.
#     """
#     if isinstance(obj, Mapping):
#         for value in obj.values():
#             yield from find_html_strings(value)

#     elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
#         for item in obj:
#             yield from find_html_strings(item)

#     elif is_html_string(obj):
#         yield obj

# def find_first_html(obj):
#     """
#     Recursively find and return the first HTML-like string.
#     Returns None if none is found.
#     """
#     if isinstance(obj, Mapping):
#         for value in obj.values():
#             result = find_first_html(value)
#             if result is not None:
#                 return result
#     elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
#         for item in obj:
#             result = find_first_html(item)
#             if result is not None:
#                 return result
#     elif is_html_string(obj):
#         return obj
#     return None

# class _PageValidator(ABC):
#     def __init__(self, html):
#         # this calls BeautifulSoup(...) internally
#         self.soup = BeautifulSoup(html, 'html.parser')

#     @abstractmethod
#     def is_valid(self) -> bool:
#         """Return True if this HTML matches the expected page structure."""
#         ...

# class _FinanceValidator(_PageValidator):
#     REQUIRED_SECTIONS = [
#         "Key Executives", "Corporate Governance", "Description",
#         "Financial Highlights", "Valuation Measures", "Trading Information"
#     ]

#     def _has_ticker(self, expected) -> bool:
#         # Extract <title> and parse out the ticker in parentheses:
#         title = self.soup.title and self.soup.title.get_text()
#         if not title:
#             return False
#         # e.g. "Meta Platforms, Inc. (META) Stock Price..."
#         import re
#         m = re.search(r'\(([A-Z0-9\-\.]+)\)', title)
#         return bool(m and m.group(1).upper() == expected.upper())

#     def _has_any_section(self, headings) -> bool:
#         for h3 in self.soup.find_all("h3"):
#             text = h3.get_text(strip=True)
#             for kw in headings:
#                 if kw.lower() in text.lower():
#                     return True
#         return False

#     def is_valid(self, expected_ticker=None) -> bool:
#         # 1) Ticker match (if provided)
#         if expected_ticker:
#             if not self._has_ticker(expected_ticker):
#                 return False

#         # 2) Must have at least one of the profile or stats sections
#         profile_ok = self._has_any_section(self.REQUIRED_SECTIONS[:3])
#         stats_ok   = self._has_any_section(self.REQUIRED_SECTIONS[3:])
#         return profile_ok or stats_ok

# class _FXCurrencyValidator(_PageValidator):
#     def _find_pair_in_header(self, pair) -> bool:
#         # Many Bchart pages include the symbol in a <h1> or in JSON-LD
#         header = self.soup.find('h1')
#         if header and pair.upper() in header.get_text():
#             return True
#         # fallback: look for JSON-LD <script type="application/ld+json">
#         for script in self.soup.find_all("script", type="application/ld+json"):
#             try:
#                 data = json.loads(script.string)
#                 if pair.upper() in json.dumps(data):
#                     return True
#             except Exception:
#                 pass
#         return False

#     def is_valid(self, expected_pair=None) -> bool:
#         if expected_pair:
#             normalized = re.sub(r'[^A-Za-z]', '', expected_pair).upper()
#             return self._find_pair_in_header(normalized)
#         return False

# def validateHTMLResponse(
#     html: str,
#     source: str,
#     symbol: str
# ) -> bool:
#     """
#     :param html: raw HTML string
#     :param source: either "yahoo" or "barchart"
#     :param symbol: ticker or currency pair
#     """
#     validators = {
#         "yahoo": _FinanceValidator,
#         "barchart": _FXCurrencyValidator,
#     }
#     ValidatorCls = validators.get(source)
#     if not ValidatorCls:
#         raise ValueError(f"Unknown source {source!r}")
#     validator = ValidatorCls(html)
#     return validator.is_valid(symbol)

