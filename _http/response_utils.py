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



import json
import re

# Custom
from .connection import http_client
from ..web_utils import url_encode_decode, HTMLclean
from ..api.parse_tools import extract_html_element_by_keyword, remove_html_tags, extract_by_keyword, extract_ticker


def normalize_response(response, target_key="response", onlyNormalize=False, keep_structure=False):
    """
    Normalizes a nested data structure (dictionary, list, or JSON string) by extracting values associated with a specified key.
    Depending on parameters, it can either extract just the values or maintain the original structure surrounding the values.
    Additionally, it can perform a deep parse of JSON strings within the data.

    Args:
        response (dict | list | str): The input data structure that may contain nested structures.
        target_key (str): The specific key to search for within the data structure.
        onlyNormalize (bool, optional): If True, the function skips extraction and only performs deep JSON parsing on the response.
                                        Defaults to False.
        keep_structure (bool, optional): If True, retains the full structure of data surrounding the found key. If False,
                                         returns only the values associated with the found key.
                                         Defaults to False.

    """
    def normalize(response=response, target_key=target_key, keep_structure=keep_structure, results=None):
        if results is None:
            results = []
        if isinstance(response, dict):
            if target_key in response:
                if keep_structure:
                    results.append({target_key: response[target_key]})
                else:
                    results.append(response[target_key])
            for value in response.values():
                normalize(value, target_key, keep_structure, results)
        elif isinstance(response, list):
            for item in response:
                normalize(item, target_key, keep_structure, results)
        elif isinstance(response, str):
            try:
                parsed_response = json.loads(response)
                normalize(parsed_response, target_key, keep_structure, results)
            except json.JSONDecodeError:
                pass
        return results

    def deep_parse_json(input_data):
        """ Recursively parses input data, converting all JSON strings within it into Python data structures. """
        if isinstance(input_data, str):
            try:
                parsed_data = json.loads(input_data)
                return deep_parse_json(parsed_data)
            except json.JSONDecodeError:
                return input_data
        elif isinstance(input_data, dict):
            return {k: deep_parse_json(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [deep_parse_json(item) for item in input_data]
        else:
            return input_data

    def process_result(result, multiple=False):
        """ Processes the normalized data, ensuring that all JSON-encoded strings are parsed and returns the final result. """
        if multiple:
            return [deep_parse_json(r) for r in result]
        if isinstance(result, list):
            try:
                return deep_parse_json(result[0])
            except json.JSONDecodeError:
                pass
        return deep_parse_json(result)
    if onlyNormalize:
        return deep_parse_json(response)
    data = normalize(response, target_key, keep_structure)
    multi = (False if len(data) == 1 else True)
    result = (data[0] if len(data) == 1 else data)
    return process_result(result, multiple=multi)


class validateHTMLResponse:
    """
    Validates sections of HTML content based on provided criteria related to financial data.

    This function performs validations to determine if specific sections relevant to financial data queries
    exist within a given HTML content string. It supports different types of financial instruments such as equities
    and currencies, depending on the parameters supplied.   
    """	    
    def __init__(self, html):
        if not self.__is_valid_html_str(html):
            # return False
            raise ValueError("Provided HTML content is not valid.")            
        self.html = HTMLclean.decode(html)
        
    def __is_valid_html_str(self, html):
        if html is None or not isinstance(html, str):
            return False
        if html.strip() == "":
            return False
        errors = []
        if not re.match(r'(?i)<!doctype\s+html>', html):
            errors.append("Missing or incorrect DOCTYPE declaration.")
        if not re.search(r'<html[^>]*>', html, re.IGNORECASE) or not re.search(r'</html>', html, re.IGNORECASE):
            errors.append("Missing <html> or </html> tag.")
        if not re.search(r'<head[^>]*>', html, re.IGNORECASE) or not re.search(r'</head>', html, re.IGNORECASE):
            errors.append("Missing <head> or </head> tag.")
        if re.search(r'<head[^>]*>', html, re.IGNORECASE):
            head_content = re.search(r'<head[^>]*>(.*?)</head>', html, re.IGNORECASE | re.DOTALL)
            if head_content:
                if not re.search(r'<title[^>]*>.*?</title>', head_content.group(1), re.IGNORECASE | re.DOTALL):
                    errors.append("Missing <title> or </title> tag inside <head>.")
            else:
                errors.append("Head tag content not found.")
        if not re.search(r'<body[^>]*>', html, re.IGNORECASE) or not re.search(r'</body>', html, re.IGNORECASE):
            errors.append("Missing <body> or </body> tag.")
        if not errors:
            return True
        else:
            return False
        
    def __ticker_search(self, ticker):
        html_content = self.html        
        symbol = re.sub(r'\s+', '', symbol).upper()
        ticker_match = extract_ticker(html_content).ticker
       
        if ticker_match:
            found_ticker = remove_html_tags(ticker_match)
            if found_ticker == symbol:
                return True            
        return False

    def __currencypair_search(self, currency_pair):
        def remove_non_alphabetic(text):
            return re.sub(r'[^a-zA-Z]', '', text)
           
        html_content = self.html
        currency_pair = remove_non_alphabetic(currency_pair)
        escaped_currency_pair = re.escape(currency_pair)
        pattern = rf"\b{escaped_currency_pair}\b.*Barchart\.com"
        match = re.search(pattern, html_content)
        if match:
            return currency_pair
        return None
         
    def currency(self, currency_pair):
        html_content = self.html
        if self.__currencypair_search(currency_pair=currency_pair):
            if not currency_pair.__contains__("^"):
                currency_pair = "^" + currency_pair
            pattern_pair = rf'<span>\({re.escape(currency_pair)}\)</span>'
            if re.search(pattern_pair, html_content, re.IGNORECASE | re.DOTALL):
                return True
        return False
        
    def equity(self, ticker):
        html_content = self.html
        if self.__ticker_search(ticker=ticker):
            # profile_check = re.search(r'<section data-testid="description".*?<h3.*?>\s*Description\s*</h3>.*?</section>', html_content, re.IGNORECASE | re.DOTALL)
            # stats_check = re.search(r'<div\s+data-testid="quote-statistics"[^>]*>.*?<ul[^>]*>.*?</ul>.*?</div>', html_content, re.IGNORECASE | re.DOTALL)        	
            profile_check = extract_by_keyword(html_content, keyword=["Key Executives", "Corporate Governance", "Description"], tag_name="h3")
            stats_check = extract_by_keyword(html_content, keyword=["Financial Highlights", "Valuation Measures", "Trading Information"], tag_name="h3")
            if profile_check or stats_check:
                return True
        return False
       
       
def clean_initial_content(content):
    """
    Clean the input content by removing entries with URL keys and extracting the contents within their 'response' sub-key.
    
    This function iterates through a list of dictionaries. If a dictionary key is a valid URL, the function checks for the 
    existence of a 'response' sub-key. If found, it extracts the content of the 'response' sub-key directly into the cleaned content. 
    
    If the key is not a valid URL, the original key-value pair is retained in the cleaned content. The validity of a URL is 
    determined using the `is_valid_url` function.
    
    Parameters:
        content (list of dict): A list of dictionaries, where each dictionary may contain one or more key-value pairs. The keys may be URLs.

    Returns:
        list: A list of dictionaries that have been cleaned according to the described logic. If a URL key was present and had a 'response' sub-key, only the content of 'response' is retained. Other content remains unchanged.
    
    Raises:
        KeyError: If the dictionary structure does not conform to expected nesting (although in this script, it simply skips malformed content without explicit error handling).
    """	
    cleaned_content = []
    for entry in content:
        for key, value in entry.items():
            if url_encode_decode.is_valid_url(key):
                if 'response' in value: 
                    cleaned_content.append(value['response'])
            else:
                cleaned_content.append({key: value})
    return cleaned_content

def key_from_mapping(input_str, mappings, invert=False):
    """
    Returns the corresponding key or value from the mappings dictionary for a given input string.
    If the input is a key and exists in the dictionary, it returns the key (default) or value if invert is True.
    If the input is a value (or one of the synonyms in a list) and exists in the dictionary, it returns the corresponding key.
    The function is case-insensitive.

    Args:
    input_str (str): The input string which could be a key or value in the mappings.
    mappings (dict): Dictionary containing the mappings of keys to values (can be strings or lists of strings).
    invert (bool): If True, returns the value for a given key instead of the key.

    Returns:
    str: The corresponding key or value, or None if no match is found.
    """
    input_str = input_str.strip().lower()

    lower_case_mappings = {key.lower(): key for key in mappings}
    
    inverse_mappings = {}
    for key, value in mappings.items():
        if isinstance(value, list):
            for synonym in value:
                inverse_mappings[synonym.lower()] = key
        else:
            inverse_mappings[value.lower()] = key

    if input_str in lower_case_mappings.keys():
        if invert:
            return mappings[lower_case_mappings[input_str]] 
        return lower_case_mappings[input_str]

    if input_str in inverse_mappings:
        return inverse_mappings[input_str]

    return None


##==
def Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False):
    """
    Handles HTTP requests automatically, managing concurrent requests if a list of URLs is provided. The function manages header settings,
    processes responses according to the specified format, and normalizes the response data based on provided parameters.

    Args:
        url (str | list): The URL or a list of URLs for making the requests. If a list is provided and contains more than one URL,
                          the requests are made concurrently.
        headers_to_update (dict, optional): A dictionary of headers that should be updated for this particular request. These headers
                                            are temporarily set for the request and restored to their original values afterward.
        response_format (str, optional): The expected format of the response. This affects the 'Accept' header to expect either 'html' or 'json'.
                                         Defaults to 'html'.
        target_response_key (str, optional): The key in the response payload from which the data should be extracted. Defaults to 'response'.
        return_url (bool, optional): If True, returns the response along with the URL it was fetched from. This is applicable for non-concurrent
                                     requests. Defaults to True.
        onlyParse (bool, optional): If set to True, the function skips the extraction of the target key and performs a deep JSON parsing on the entire response.
                                    Defaults to False.
        no_content (bool, optional): If set to True, retains the entire structure surrounding the target_response_key in the processed response,
                                     otherwise, it returns only the value associated with target_response_key. Defaults to False.

    Returns:
        Any | None: Depending on the existence and content of the target_response_key in the response, this function may return the processed
                    response data or the full response itself if an error occurs during processing.

    Raises:
        HTTPError: If an HTTP error occurs during the request.
        ValueError: If the response content type is unsupported.
        JSONDecodeError: If a JSON parsing error occurs.

    Note:
        This function supports handling multiple URLs concurrently and can handle complex data structures in responses, including nested and JSON strings.
        It also manages headers dynamically and ensures that they are restored after the request, minimizing side effects on the http_client's state.
    """
    concurrent = isinstance(url, list) and len(url) > 1 # Determine if the request should be handled concurrently

    if headers_to_update is None:
        headers_to_update = {}
    if response_format == 'json':
        headers_to_update['Accept'] = 'application/json'
    original_headers = {}
    if headers_to_update:
        for header, value in headers_to_update.items():
            original_headers[header] = http_client.get_headers(header)
            http_client.update_header(header, value)

    params = {'format': response_format}
    if concurrent:
        response = http_client.make_requests_concurrently(url, params, return_url=return_url, delay_enabled=False)
    else:
        if isinstance(url, str):
            http_client.update_base_url(url)
        response = http_client.make_request(params, concurrent=False, return_url=return_url, delay_enabled=True)

    for header, original_value in original_headers.items():
        http_client.update_header(header, original_value)

    try:
        return normalize_response(response, target_key=target_response_key, onlyNormalize=onlyParse, keep_structure=no_content)        
    except:
        return response


def __dir__():
    return ['Request', 'normalize_response']

__all__ = ['Request', 'normalize_response']
