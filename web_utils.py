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
import base64
import html as hhtml
from urllib.parse import urlparse, parse_qs


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
        decoded_text = hhtml.unescape(text)
        return decoded_text
       
    def __dir__(self):
        return ['remove_comments','remove_emojis', 'decode']

# Initialize
HTMLclean = HTMLCleaner()



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
       
# Initialize
url_encode_decode = URLEncoderDecoder()



def find_url_in_text(text):
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^ \n]*'
    urls = re.findall(url_pattern, text)
    return urls
   
def parse_url(url, include_notation=True, parts=None):
    parsed_url = urlparse(url)
    full_domain = parsed_url.netloc
    domain_parts = full_domain.split('.')
    
    if len(domain_parts) > 2:
        subdomain = domain_parts[0]
        domain_name = '.'.join(domain_parts[1:])
    else:
        subdomain = None  
        domain_name = full_domain
    
    protocol = parsed_url.scheme
    if include_notation:
        protocol += "://"
        if subdomain:
            subdomain += "."
        query_string = f"?{parsed_url.query}" if parsed_url.query else ""
    else:
        query_string = parsed_url.query

    path = parsed_url.path
    components = {
        "protocol": protocol,
        "subdomain": subdomain,
        "domain_name": domain_name,
        "path": path,
        "query_string": query_string
    }
    if parts:
        if isinstance(parts, str):
            parts = [parts]
        return {key: components[key] for key in parts if key in components}
    return components





class Mask:
    class bool:
        @staticmethod
        def bytes(s):
            """ base64 """
            if len(s) % 4 != 0:
                return False
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', s):
                return False
            try:
                decoded_bytes = base64.b64decode(s, validate=True)
                decoded_str = decoded_bytes.decode('utf-8')
                return True
            except (base64.binascii.Error, UnicodeDecodeError):
                return False
        @staticmethod
        def bin(s):
            """ Binary """
            if not all(c in '01' for c in s):
                return False
            if len(s) % 8 != 0:
                return False
            try:
                bytes_list = [s[i:i+8] for i in range(0, len(s), 8)]
                decoded_chars = [chr(int(byte, 2)) for byte in bytes_list]
                decoded_str = ''.join(decoded_chars)
                return True
            except ValueError:
                return False
    class format:
        @staticmethod
        def chr(data, call):
            """ base64 """
            if call == "unformat":
                if not Mask.bool.bytes(data):
                    return base64.b64encode(data.encode('utf-8')).decode('utf-8')
            elif call == "format":
                if url_encode_decode.is_valid_url(data):
                    return data
                
                if Mask.bool.bytes(data):
                    try:
                        return base64.b64decode(data).decode('utf-8')
                    except (base64.binascii.Error, UnicodeDecodeError):
                        raise ValueError("Invalid base64 input.")
            else:
                raise ValueError("Invalid call. Use 'unformat' or 'format'.")
        @staticmethod
        def str(data, call):
            """ Binary """
            if call == "unformat":
                if not Mask.bool.bin(data):
                    return ''.join(format(ord(char), '08b') for char in data)
            elif call == "format":
                if Mask.bool.bin(data):
                    try:
                        chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8)]
                        return ''.join(chars)
                    except ValueError:
                        raise ValueError("Invalid binary input.")
            else:
                raise ValueError("Invalid call. Use 'unformat' or 'format'.")               
    class type:
        @staticmethod
        def map(s, add=None, ret=False):
            formatted = Mask.format.chr(s, "format")
            str_formatted = formatted
            if add:
                str_formatted += add
            unformatted = Mask.format.chr(str_formatted, "unformat")

            if ret:
                return Mask.format.chr(unformatted, "format")
            return unformatted




def __dir__():
    return [
    'url_encode_decode',
    'HTMLclean',
    'Mask'
    ]

__all__ = [
	'url_encode_decode',
  'HTMLclean',
  'Mask'
	]




