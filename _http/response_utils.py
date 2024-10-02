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
from ..web_utils import url_encode_decode

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

    Returns:
        The normalized data which may be a deeply parsed structure or specific values extracted from the structure.

    Raises:
        json.JSONDecodeError: If a JSON-encoded string within the response or its substructures fails to parse.

    Note:
        The function can handle complex nested structures and can optionally parse JSON strings into Python data structures.
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
        """
        Recursively parses input data, converting all JSON strings within it into Python data structures.

        Args:
            input_data (dict | list | str): The input data which may contain JSON strings.

        Returns:
            The input data with all JSON strings parsed into appropriate Python data structures.

        Raises:
            json.JSONDecodeError: If a JSON string cannot be parsed.
        """
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
        """
        Processes the normalized data, ensuring that all JSON-encoded strings are parsed and returns the final result.

        Args:
            result: The data output from the normalize function.
            multiple (bool, optional): Indicates if multiple results are expected and should be parsed accordingly.
                                       Defaults to False.

        Returns:
            The fully processed result after deep parsing.
        """
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


def validateHTMLResponse(html_content, ticker=None, currency_pair=None, query=None):
    """
    Validates sections of HTML content based on provided criteria related to financial data.

    This function performs validations to determine if specific sections relevant to financial data queries
    exist within a given HTML content string. It supports different types of financial instruments such as equities
    and currencies, depending on the parameters supplied.
    
    Parameters:
    - html_content (str): The HTML content to be validated.
    - ticker (str, optional): The ticker symbol associated with equities. If provided, the function will
      validate content specifically related to the ticker within equity-related queries ('profile' and 'stats').
    - currency_pair (str, optional): The currency pair identifier. If provided and the query is 'currency', the function
      will validate content specific to the currency pair.
    - query (str, optional): The type of query to validate against. Expected values are 'profile', 'stats', or 'currency'.
      Default is 'None'.    
    """	
    if query == "currency" and currency_pair:
        if not currency_pair.__contains__("^"):
            currency_pair = "^" + currency_pair
        pattern_pair = rf'<span>\({re.escape(currency_pair)}\)</span>'
        if re.search(pattern_pair, html_content, re.IGNORECASE | re.DOTALL):
            return html_content
        return None

    if ticker and (query == "profile" or query == "stats"):
        if re.search(rf'<section\s+class="container yf-1bx8svv paddingRight">.*?<h1\s+class="yf-1bx8svv">.*?\({ticker}\).*?</h1>.*?</section>', html_content, re.IGNORECASE | re.DOTALL):
            return html_content
        return None

    elif not ticker:
        if query == "profile":
            description_found = re.search(r'<section data-testid="description".*?<h3.*?>\s*Description\s*</h3>.*?</section>', html_content, re.IGNORECASE | re.DOTALL)
            key_exec_found = re.search(r'<section data-testid="key-executives".*?<h3.*?>\s*Key Executives\s*</h3>.*?</section>', html_content, re.IGNORECASE | re.DOTALL)
            if description_found or key_exec_found:
                return html_content

        elif query == "stats":
            stats_found = re.search(r'<div\s+data-testid="quote-statistics"[^>]*>.*?<ul[^>]*>.*?</ul>.*?</div>', html_content, re.IGNORECASE | re.DOTALL)
            if stats_found:
                return html_content
    return None 


def inspect_content(content, root_key='data'):
    """
    Determine if all content in a list contain a specified key.

    This function iterates over a list of dictionaries (content) and checks
    each dictionary to see if it contains a specific key (root_key). It returns
    True if all dictionaries contain the key, and False otherwise.

    Parameters:
    - content (list of dict): A list of dictionaries representing content.
    - root_key (str, optional): The key to check for in each dataset dictionary.
                                Defaults to 'data'.

    Returns:
    - bool: True if all dictionaries in the list contain the root_key, False otherwise.
    """	
    num_content = len(content)

    data_keys_count = 0
    for i, dataset in enumerate(content):
        if root_key in dataset:
            data_keys_count += 1
    if data_keys_count == num_content:
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

def get_top_level_key(content, top_1=True):
    """
    This function takes a nested data structure (e.g., a dictionary or list of dictionaries)
    and returns the top-level keys of the structure.
    If top_1 is True, it returns only the first key that is not 'error'.
    
    :param content: The nested data structure (dict or list of dicts)
    :param top_1: Boolean, if True returns only the first valid key
    :return: List of keys, a single key, or an error message
    """
    keys = []
    if isinstance(content, dict):
        keys = list(content.keys())
    elif isinstance(content, list) and content and isinstance(content[0], dict):
        keys = list(content[0].keys())
    else:
        return "Invalid or unsupported structure"
    
    keys = [key for key in keys if key != 'error']
    
    if top_1 and keys:
        return keys[0]
    return keys
   
def safe_content_access(content, path):
    """
    Safely access nested content using a list of keys, automatically handling lists by accessing the first element.
    
    Args:
    content (dict): The dictionary to access.
    path (list): A list of keys representing the path to the desired content.

    Returns:
    The content found at the path, handling lists by returning the first element.
    """
    current_content = content
    for key in path:
        if isinstance(current_content, list):
            if len(current_content) > 0:
                current_content = current_content[0]
            else:
                return None
        if isinstance(current_content, dict):
            current_content = current_content.get(key, None)
            if current_content is None:
                return None
        else:
            return current_content
    return current_content

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



def __is_effectively_empty(item):
    """
    Recursively checks if a structure is effectively empty.
    An empty structure is:
    - an empty list, tuple, set, or dict
    - a list, tuple, or set where all elements are empty structures
    - a dict where all values are empty structures
    """
    if isinstance(item, (list, tuple, set)):
        return all(__is_effectively_empty(i) for i in item)
    elif isinstance(item, dict):
        return all(__is_effectively_empty(v) for v in item.values())
    return False

def locKeyInStructure(structure, target_key, value_only=True, first_only=True, return_all=False):
    """
    Recursively searches for a key in a nested structure (dict, list, tuple, set)
    and returns its corresponding value, the key-value pair, or the entire sub-structure,
    optionally returning all matches instead of just the first.

    Parameters:
    structure (Any): The nested structure to search. It can be a dict, list, tuple, set, or any iterable.
    target_key (str): The key to search for within the structure.
    value_only (bool): If True, returns only the value associated with the target key.
                       If False, returns a dictionary with the key-value pair. Default is True.
    first_only (bool): If True, returns only the first match found. If False, returns all matches.
    return_all (bool): If True, returns the entire sub-structure where the target key is found instead of just the value or key-value pair.

    Returns:
    Union[Any, dict, None, List]: Depending on first_only, value_only, and return_all, returns a single value,
                                  a single key-value pair, the entire structure, a list of values, a list of key-value pairs, or a list of structures.
    """
    results = []

    if structure is None:
        return None
    if isinstance(structure, dict):
        for key, value in structure.items():
            if key == target_key:
                result = (value if value_only else {key: value}) if not return_all else structure
                if first_only:
                    return result
                else:
                    results.append(result)
            sub_result = locKeyInStructure(value, target_key, value_only, first_only, return_all)
            if sub_result is not None:
                if first_only:
                    return sub_result
                else:
                    results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
    elif isinstance(structure, (list, tuple, set)):
        for item in structure:
            sub_result = locKeyInStructure(item, target_key, value_only, first_only, return_all)
            if sub_result is not None:
                if first_only:
                    return sub_result
                else:
                    results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
    elif isinstance(structure, (str, bytes)):
        return None if first_only else results
    else:
        try:
            iterator = iter(structure)
            for item in iterator:
                sub_result = locKeyInStructure(item, target_key, value_only, first_only, return_all)
                if sub_result is not None:
                    if first_only:
                        return sub_result
                    else:
                        results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
        except TypeError:
            return None if first_only else results
           
    if results:
        results = [res for res in results if res is not None]
        if not results: 
            return None
    if __is_effectively_empty(results):
        return None
    return results if not first_only else None


def locMultipleKeyInStructure(structure, target_keys, value_only=True, first_only=True, return_all=False):
    """
    Recursively searches for keys in a nested structure (dict, list, tuple, set)
    and returns their corresponding values, the key-value pairs, or the entire sub-structure,
    optionally returning all matches instead of just the first.

    Parameters:
    structure (Any): The nested structure to search. It can be a dict, list, tuple, set, or any iterable.
    target_keys (list): The keys to search for within the structure.
    value_only (bool): If True, returns only the values associated with the target keys.
                       If False, returns a dictionary with the key-value pairs. Default is True.
    first_only (bool): If True, returns only the first match found. If False, returns all matches.
    return_all (bool): If True, returns the entire sub-structure where the target keys are found instead of just the values or key-value pairs.

    Returns:
    Union[Any, dict, None, List]: Depending on first_only, value_only, and return_all, returns a single value,
                                  a single key-value pair, the entire structure, a list of values, a list of key-value pairs, or a list of structures.
    """
    def remove_duplicates(dicts):
        seen = []
        unique_dicts = []
        for d in dicts:
            if d not in seen:
                unique_dicts.append(d)
                seen.append(d)
        return unique_dicts  
       
    results = []       

    if structure is None:
        return None
    if isinstance(structure, dict):
        for key, value in structure.items():
            if key in target_keys:
                result = (value if value_only else {key: value}) if not return_all else structure
                if first_only:
                    return result
                else:
                    results.append(result)
            sub_result = locMultipleKeyInStructure(value, target_keys, value_only, first_only, return_all)
            if sub_result is not None:
                if first_only:
                    return sub_result
                else:
                    results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
    elif isinstance(structure, (list, tuple, set)):
        for item in structure:
            sub_result = locMultipleKeyInStructure(item, target_keys, value_only, first_only, return_all)
            if sub_result is not None:
                if first_only:
                    return sub_result
                else:
                    results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
    elif isinstance(structure, (str, bytes)):
        return None if first_only else results
    else:
        try:
            iterator = iter(structure)
            for item in iterator:
                sub_result = locMultipleKeyInStructure(item, target_keys, value_only, first_only, return_all)
                if sub_result is not None:
                    if first_only:
                        return sub_result
                    else:
                        results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
        except TypeError:
            return None if first_only else results

    if results:
        results = [res for res in results if res is not None] 
        if not results:
            return None
    return remove_duplicates(results)  if not first_only else None


def ExtractURLKeys(structure, ignore_case=True, flatten=False):
    """
    Extracts and returns a set or a single string of unique keys that are URLs from a nested dictionary,
    list, tuple, set, or other iterable structure.

    Parameters:
    - structure (any): The input data structure to search for URL keys.
    - ignore_case (bool, optional): If True, the URL matching will be case-insensitive. Defaults to True.
    - flatten (bool, optional): If True and only one URL key is found, return it as a string instead of a set. Defaults to False.

    Returns:
    - set: A set of unique keys that are URLs found in the structure.

    Example usage:
    structure = {
        'https://example.com/api/data': {'data': 123},
        'normal_key': 'value',
        'another_url': 'https://example.com/api/info'
    }
    keys = ExtractURLKeys(structure)
    print(keys)
    # Output: {'https://example.com/api/data', 'https://example.com/api/info'}
    """
    keys = set()
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^ \n]*'
    regex = re.compile(url_pattern, re.IGNORECASE if ignore_case else 0)
    def recurse(current_structure):
        if isinstance(current_structure, dict):
            for key in current_structure.keys():
                if regex.search(key):
                    keys.add(key)
            for value in current_structure.values():
                recurse(value)
        elif isinstance(current_structure, (list, tuple, set)):
            for item in current_structure:
                recurse(item)
        elif hasattr(current_structure, '__iter__') and not isinstance(current_structure, (str, bytes)):
            try:
                iterator = iter(current_structure)
                for item in iterator:
                    recurse(item)
            except TypeError:
                pass
    recurse(structure)
    if flatten and len(keys) == 1:
        return next(iter(keys))
    if isinstance(keys, set):
        return list(keys)        
    return keys


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
    # Determine if the request should be handled concurrently
    concurrent = isinstance(url, list) and len(url) > 1

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
        # Update the base URL if it's a singular request or there's a single URL in concurrent mode
        if isinstance(url, str):
            http_client.update_base_url(url)
        response = http_client.make_request(params, concurrent=False, return_url=return_url, delay_enabled=True)

    # Restore original headers
    for header, original_value in original_headers.items():
        http_client.update_header(header, original_value)

    # Directly use the no_content value for keep_structure in normalize_response.
    try:
        return normalize_response(response, target_key=target_response_key, onlyNormalize=onlyParse, keep_structure=no_content)        
    except:
        return response



def __dir__():
    return ['Request', 'normalize_response', 'locKeyInStructure']

__all__ = ['Request', 'normalize_response', 'locKeyInStructure']
