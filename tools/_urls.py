import re
from urllib.parse import urljoin, urlparse

def is_valid_url(string):
    url_pattern = re.compile(
        r'^(https?|ftp):\/\/'  # protocol
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # port
        r'(?:\/?|[\/?]\S+)$', re.IGNORECASE) 
    return re.match(url_pattern, string) is not None

def findhost(url):
    """Extract the host from a URL or return the hostname if that's what is provided."""
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return parsed_url.netloc
    elif not parsed_url.netloc and not parsed_url.scheme:
        return url
    else:
        parsed_url = urlparse('//'+url)
        return parsed_url.netloc


url_encoding_dict = {
    "%20": " ",   # Space
    "%21": "!",   # Exclamation mark
    "%22": "\"",  # Double quote
    "%23": "#",   # Hash
    "%24": "$",   # Dollar sign
    "%25": "%",   # Percent sign
    "%26": "&",   # Ampersand
    "%27": "'",   # Single quote
    "%28": "(",   # Left parenthesis
    "%29": ")",   # Right parenthesis
    "%2A": "*",   # Asterisk
    "%2B": "+",   # Plus sign
    "%2C": ",",   # Comma
    "%2D": "-",   # Hyphen
    "%2E": ".",   # Period
    "%2F": "/",   # Forward slash
    "%3A": ":",   # Colon
    "%3B": ";",   # Semicolon
    "%3C": "<",   # Less-than sign
    "%3D": "=",   # Equals sign
    "%3E": ">",   # Greater-than sign
    "%3F": "?",   # Question mark
    "%40": "@",   # At sign
    "%5B": "[",   # Left square bracket
    "%5C": "\\",  # Backslash
    "%5D": "]",   # Right square bracket
    "%5E": "^",   # Caret
    "%5F": "_",   # Underscore
    "%60": "`",   # Grave accent
    "%7B": "{",   # Left curly brace
    "%7C": "|",   # Vertical bar
    "%7D": "}",   # Right curly brace
    "%7E": "~"    # Tilde
}

# Inverting the dictionary
char_to_url_encoding_dict = {v: k for k, v in url_encoding_dict.items()}

def decode_url(encoded_url, encoding_dict=url_encoding_dict):
    decoded_url = encoded_url
    for encoded_char, decoded_char in encoding_dict.items():
        decoded_url = decoded_url.replace(encoded_char, decoded_char)
    return decoded_url
   
def encode_url(url, encoding_dict=char_to_url_encoding_dict, chars_to_encode=None):
    match = re.match(r'^(https?://)', url)
    protocol = match.group(1) if match else ''
    url = url[len(protocol):] 

    encoded_url = protocol 
    for char in url:
        if chars_to_encode is not None and char not in chars_to_encode:
            encoded_url += char 
        elif char in encoding_dict:
            encoded_url += encoding_dict[char]
        else:
            encoded_url += char
    return encoded_url


def __dir__():
    return [
    'decode_url',
    'encode_url',
    'is_valid_url',
    'findhost'
    ]

__all__ = [
	'decode_url',
	'encode_url',
	'is_valid_url',
	'findhost'
	]


