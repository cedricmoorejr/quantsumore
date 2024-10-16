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



from copy import deepcopy
import re


def __is_effectively_empty__(item):
    """
    Recursively checks if a structure is effectively empty.
    An empty structure is:
    - an empty list, tuple, set, or dict
    - a list, tuple, or set where all elements are empty structures
    - a dict where all values are empty structures
    """
    if isinstance(item, (list, tuple, set)):
        return all(__is_effectively_empty__(i) for i in item)
    elif isinstance(item, dict):
        return all(__is_effectively_empty__(v) for v in item.values())
    return False


class IterDict:
    """
    IterDict provides specialized utilities for navigating, filtering, and transforming nested JSON 
    structures commonly returned from financial data APIs integrated into quantsumore. 

    Within quantsumore, API responses often contain complex and deeply nested data formats, with 
    dictionaries, lists, tuples, and sets holding diverse financial information. IterDict is designed 
    to streamline the handling of these structures by allowing you to:
    
    - Prune irrelevant keys or entire sub-dictionaries from the JSON data, specifically targeting 
      metadata or unnecessary fields that can clutter financial metrics.
    - Extract key financial metrics and URLs directly, identifying and isolating relevant data 
      points—like pricing, volume, or performance indicators—within nested structures.
    - Identify and remove empty segments that arise after filtering, ensuring the resulting data is 
      concise and free of superfluous elements.
    - Search for and retrieve specific keys or values, like "ticker," "exchange," or URLs, 
      at any level of nesting, to quickly pinpoint the metrics needed for analysis.

    Each method is optimized for quantsumore’s use cases, allowing efficient data manipulation 
    without affecting the integrity of the JSON structure returned by the APIs. The static methods 
    in IterDict enable quick, recursive operations on the JSON structures, making it easier to 
    focus on meaningful financial data while eliminating distractions.

    Methods:
    - prune_nested_dicts(d, exclude, remove_empty=True): Eliminates dictionaries that contain specified 
      keys, like metadata fields, with an option to remove any that become empty as a result.
    - prune_keys(d, keys_to_remove): Removes specified keys across all dictionaries within the nested 
      JSON structure, ideal for excluding unwanted attributes from financial data.
    - prune_top_key(d, key_to_remove): Quickly removes a specified top-level key, useful for excluding 
      high-level metadata not relevant to analysis.
    - unique_keys(d, pattern=None, ignore_case=True): Gathers unique keys, supporting targeted searches 
      for common patterns, like keys containing “price” or “volume.”
    - unique_url_keys(d, ignore_case=True, flatten=False): Isolates keys that are URLs, making it easy to 
      identify and extract links to related financial documents or resources.
    - top_key(d, top_1=True, exclusion=None, exclusion_sensitive=False): Extracts top-level keys, with 
      options to exclude specific entries, useful for focusing on primary data fields.
    - count_keys(d, pattern=None, ignore_case=True): Counts occurrences of specific keys, aiding in 
      quickly identifying data fields of interest.
    - search_keys(d, target_keys, value_only=True, first_only=True, return_all=False, include_key_in_results=True): 
      Allows detailed searches within nested data for particular keys or values, returning direct hits 
      on essential metrics or identifiers.
    - search_keys_in(d, target_keys, value_only=True, first_only=True, return_all=False): Provides recursive 
      searches for multiple keys, with options to capture entire matched structures, optimizing the process 
      of pinpointing and extracting data points for analysis.

    Usage:
    IterDict is integral to quantsumore’s handling of JSON responses, designed to work seamlessly with 
    the structures returned from financial data APIs. It makes it straightforward to filter, extract, 
    and transform data into actionable formats by focusing on the details that matter while eliminating 
    extraneous information.
    
    Notes:
    - IterDict methods work on copies of the original JSON structure to ensure that operations do not modify 
      the raw API responses directly.
    - The class is designed specifically for the nested JSON formats commonly encountered in our financial 
      data APIs, enabling targeted manipulations to suit quantsumore’s needs.
    """
    @staticmethod            
    def prune_nested_dicts(d, exclude, remove_empty=True):
        """
        Removes entire dictionaries within a nested data structure if they contain any of the specified exclusion keys. Optionally, this function can also clean up
        any dictionaries that become empty as a result of the pruning process, based on a user-defined setting.

        Purpose:
        - To prune a nested data structure by removing dictionaries that contain specified exclusion keys. Optionally cleans up any resulting empty dictionaries based on a configurable parameter.

        Functionality:
        - Searches recursively through a structure composed of dictionaries, lists, tuples, or sets.
        - Removes entire dictionaries if they contain any of the specified exclusion keys.
        - Optionally cleans up any dictionaries that become empty after the removal process, depending on the user's choice.

        Impact:
        - Significantly alters both the content and the structure of the data by removing whole segments if they contain excluded keys.
        - Ensures that the remaining data does not contain the excluded keys at any level. Optionally, ensures that no empty dictionaries are left in the structure if specified.

        Parameters:
        - d: The nested structure to prune (dict, list, tuple, set).
        - exclude (list): A list of keys whose presence in a dictionary causes its removal.
        - remove_empty (bool): Specifies whether to remove empty dictionaries from the structure.

        Returns:
        - The modified and cleaned structure with any dictionaries containing excluded keys removed. If remove_empty is True, also removes any empty dictionaries.
        """
        def clean(data_input):
            if not isinstance(data_input, dict):
                return data_input
            cleaned_dict = {}
            for key, value in data_input.items():
                cleaned_value = clean(value)
                if isinstance(cleaned_value, dict) and not cleaned_value and remove_empty:
                    continue
                elif cleaned_value is not None:
                    cleaned_dict[key] = cleaned_value
            return cleaned_dict

        if isinstance(exclude, list) is False:
            exclude = [exclude]
            
        copied_data = deepcopy(d)    

        if isinstance(copied_data, dict):
            if any(key in copied_data for key in exclude):
                return None 
            else:
                cleaned_data = {k: IterDict.prune_nested_dicts(value, exclude, remove_empty) for k, value in copied_data.items()}
                return clean(cleaned_data)
        elif isinstance(copied_data, list):
            cleaned_data = [IterDict.prune_nested_dicts(x, exclude, remove_empty) for x in copied_data]
            return [clean(item) for item in cleaned_data if item is not None]
        elif isinstance(copied_data, tuple):
            cleaned_data = tuple(IterDict.prune_nested_dicts(x, exclude, remove_empty) for x in copied_data)
            processed = tuple(clean(item) for item in cleaned_data if item is not None)
            return processed if processed else None
        elif isinstance(copied_data, set):
            cleaned_data = {IterDict.prune_nested_dicts(x, exclude, remove_empty) for x in copied_data}
            processed = {clean(item) for item in cleaned_data if item is not None}
            return processed if processed else None
        return clean(copied_data)
    
    @staticmethod           
    def prune_keys(d, keys_to_remove):
        """
        Recursively removes specified keys from all dictionaries within a nested data structure, which can include dictionaries within lists. This function
        modifies the entire structure by removing the given keys from every level of the structure.
        
        Purpose:
        - To systematically remove specified keys from all dictionaries within a nested structure at all levels.
        
        Functionality:
        - Operates on nested data structures including dictionaries and lists of dictionaries.
        - Recursively traverses every level of the data, removing specified keys wherever found.

        Impact:
        - Maintains the overall structure of the data but without the specified keys, significantly affecting the content.
        - Focuses on key removal without eliminating entire dictionaries unless they directly contain the target keys.
            
        Parameters:
        d (dict or list): The input data structure, which can be a dictionary, a list of dictionaries, or a nested combination of both.
        keys_to_remove (str or list): The key or list of keys to be removed from the data structure. If a single key is provided, it is converted to a list internally.

        Returns:
        dict or list: A new data structure with the specified keys removed from all levels.
        """
        copied_data = deepcopy(d)    
        if isinstance(keys_to_remove, list) is False:
            keys_to_remove = [keys_to_remove]    
        def _remove_keys(data_input, keys):
            if isinstance(data_input, list):
                for item in data_input:
                    _remove_keys(item, keys)
            elif isinstance(data_input, dict):
                for key in keys:
                    if key in data_input:
                        del data_input[key]
                for key in data_input:
                    _remove_keys(data_input[key], keys)    
        _remove_keys(copied_data, keys_to_remove)
        return copied_data

    @staticmethod    
    def prune_top_key(d, key_to_remove):
        """
        Remove a key and its value from the dictionary if it exists, returning a new dictionary without the specified key.

        Parameters:
        d (dict): The dictionary from which to remove the key.
        key_to_remove (str): The key to remove from the dictionary.

        Returns:
        dict: The dictionary after removing the specified key.
        """
        if key_to_remove in d:
            new_dict = deepcopy(d)
            del new_dict[key_to_remove]
            return new_dict
        return d

    @staticmethod    
    def unique_keys(d, pattern=None, ignore_case=True):
        """
        Extracts and returns a set of unique keys found in a nested dictionary, list, tuple, set, or other iterable structure.

        Parameters:
        - d (any): The input data structure to search for keys. This can be a dictionary, list, tuple, set, or any other iterable structure.
        - pattern (str, optional): A pattern to match against the keys. If provided, only keys containing the pattern will be included. Defaults to None.
        - ignore_case (bool, optional): If True, the key matching will be case-insensitive. Defaults to True.

        Returns:
        - set: A set of unique keys found in the structure that match the specified pattern (if any).
        """
        keys = set()
        def recurse(data_input):
            if isinstance(data_input, dict):
                for key in data_input.keys():
                    if pattern is not None:
                        key_to_match = key.lower() if ignore_case else key
                        pattern_to_match = pattern.lower() if ignore_case else pattern
                        if pattern_to_match in key_to_match:
                            keys.add(key)
                    else:
                        keys.add(key)
                for value in data_input.values():
                    recurse(value)
            elif isinstance(data_input, (list, tuple, set)):
                for item in data_input:
                    recurse(item)
            elif hasattr(data_input, '__iter__') and not isinstance(data_input, (str, bytes)):
                try:
                    iterator = iter(data_input)
                    for item in iterator:
                        recurse(item)
                except TypeError:
                    pass
        recurse(d)
        return keys
    
    @staticmethod        
    def unique_url_keys(d, ignore_case=True, flatten=False):
        """
        Extracts and returns a set or a single string of unique keys that are URLs from a nested dictionary,
        list, tuple, set, or other iterable structure.

        Parameters:
        - d (any): The input data structure to search for URL keys.
        - ignore_case (bool, optional): If True, the URL matching will be case-insensitive. Defaults to True.
        - flatten (bool, optional): If True and only one URL key is found, return it as a string instead of a set. Defaults to False.

        Returns:
        - set: A set of unique keys that are URLs found in the structure.
        """
        keys = set()
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^ \n]*' # Regular expression pattern for matching URLs
        regex = re.compile(url_pattern, re.IGNORECASE if ignore_case else 0)
        def recurse(data_input):
            if isinstance(data_input, dict):
                for key in data_input.keys():
                    if regex.search(key):  # Check if the key is a URL
                        keys.add(key)
                for value in data_input.values():
                    recurse(value)
            elif isinstance(data_input, (list, tuple, set)):
                for item in data_input:
                    recurse(item)
            elif hasattr(data_input, '__iter__') and not isinstance(data_input, (str, bytes)):
                try:
                    iterator = iter(data_input)
                    for item in iterator:
                        recurse(item)
                except TypeError:
                    pass
        recurse(d)
        if flatten and len(keys) == 1:
            return next(iter(keys))
        if isinstance(keys, set):
            return list(keys)        
        return keys

    @staticmethod    
    def top_key(d, top_1=True, exclusion=None, exclusion_sensitive=False):
        """
        Extracts the top-level keys from a dictionary or a list of dictionaries, optionally excluding a specified key.

        This function processes an input `d` that must either be a dictionary or a list containing dictionaries.
        It extracts the keys from the first dictionary encountered. If the input is a dictionary, it extracts keys from it
        directly. If it is a list of dictionaries, it extracts keys from the first dictionary in the list. The function can
        optionally return only the first key from the extracted keys. Additionally, it can exclude a specified key from the
        results, with an option to make this exclusion case-sensitive.

        Parameters:
        - d (dict or list): The content from which to extract the keys. Must be a dictionary or a list of dictionaries.
        - top_1 (bool): If True (default), only the first key is returned. If False, a list of all qualifying keys is returned.
        - exclusion (str, optional): A key to exclude from the returned keys. If None (default), no key is excluded.
        - exclusion_sensitive (bool): If True, the exclusion of the key is case-sensitive. If False (default), the exclusion
                                      is case-insensitive.

        Returns:
        - str or list: If `top_1` is True and keys are found, the first key is returned. Otherwise, a list of keys is returned.
        - str: If the input is invalid or not supported, returns "Invalid or unsupported structure".

        Raises:
        - TypeError: If the content is neither a dictionary nor a list of dictionaries.
        """
        keys = []
        if isinstance(d, dict):
            keys = list(d.keys())
        elif isinstance(d, list) and d and isinstance(d[0], dict):
            keys = list(d[0]. keys())
        else:
            return "Invalid or unsupported structure"
        if exclusion:
            if exclusion_sensitive:
                keys = [key for key in keys if key != exclusion]
            else:
                keys = [key for key in keys if key.lower() != exclusion.lower()]
        if top_1 and keys:
            return keys[0]
        return keys   

    @staticmethod    
    def count_keys(d, pattern=None, ignore_case=True):
        """
        Counts the number of keys found in a nested dictionary, list, tuple, set, or other iterable structure that match a specified pattern (if any).

        Parameters:
        - d (any): The input data structure to search for keys. This can be a dictionary, list, tuple, set, or any other iterable structure.
        - pattern (str, optional): A pattern to match against the keys. If provided, only keys containing the pattern will be counted. Defaults to None.
        - ignore_case (bool, optional): If True, the key matching will be case-insensitive. Defaults to True.

        Returns:
        - int: The number of keys found in the structure that match the specified pattern.
        """
        key_count = 0
        def recurse(data_input):
            nonlocal key_count
            if isinstance(data_input, dict):
                for key in data_input.keys():
                    if pattern is not None:
                        key_to_match = key.lower() if ignore_case else key
                        pattern_to_match = pattern.lower() if ignore_case else pattern
                        if pattern_to_match in key_to_match:
                            key_count += 1
                    else:
                        key_count += 1
                for value in data_input.values():
                    recurse(value)
            elif isinstance(data_input, (list, tuple, set)):
                for item in data_input:
                    recurse(item)
            elif hasattr(data_input, '__iter__') and not isinstance(data_input, (str, bytes)):
                try:
                    iterator = iter(data_input)
                    for item in iterator:
                        recurse(item)
                except TypeError:
                    pass
        recurse(d)
        return key_count

    @staticmethod    
    def search_keys(d, target_keys, value_only=True, first_only=True, return_all=False, include_key_in_results=True):
        """
        Searches for multiple target keys within a nested structure and returns results for each key.

        Parameters:
        d (Any): The nested structure to search (can be a dict, list, tuple, set, etc.).
        target_keys (Union[str, List[str]]): A single key or list of keys to search for.
        value_only (bool): If True, returns only the value associated with the target key.
        first_only (bool): If True, returns only the first match found. If False, returns all matches.
        return_all (bool): If True, returns the entire sub-structure where the target key is found.
        include_key_in_results (bool): If True, returns results with the target key as keys; otherwise, returns only values.

        Returns:
        dict or list: A dictionary with target keys as keys and their corresponding results as values, or a list of results if include_key_in_results is False.
        """        
        def all_values_none(output):
            if isinstance(output, dict):
                return all(all_values_none(value) for value in output.values())
            elif isinstance(output, list):
                return all(all_values_none(item) for item in output)
            else:
                return output is None
        
        def recurse(d, target_key, value_only=True, first_only=True, return_all=False):
            results = []
            if d is None:
                return None
            if isinstance(d, dict):
                for key, value in d.items():
                    if key == target_key:
                        result = (value if value_only else {key: value}) if not return_all else d
                        if first_only:
                            return result
                        else:
                            results.append(result)
                    sub_result = recurse(value, target_key, value_only, first_only, return_all)
                    if sub_result is not None:
                        if first_only:
                            return sub_result
                        else:
                            results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
            elif isinstance(d, (list, tuple, set)):
                for item in d:
                    sub_result = recurse(item, target_key, value_only, first_only, return_all)
                    if sub_result is not None:
                        if first_only:
                            return sub_result
                        else:
                            results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
            elif isinstance(d, (str, bytes)):
                return None if first_only else results
            else:
                try:
                    iterator = iter(d)
                    for item in iterator:
                        sub_result = recurse(item, target_key, value_only, first_only, return_all)
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
            if __is_effectively_empty__(results):
                return None
            return results if not first_only else None

        if isinstance(target_keys, str):
            target_keys = [target_keys]
            
        if include_key_in_results:
            results = {key: recurse(d, target_key=key, value_only=value_only, first_only=first_only, return_all=return_all) for key in target_keys}
            
            if all_values_none(results):
                results = None
                
        else:
            results = [recurse(d, target_key=key, value_only=value_only, first_only=first_only, return_all=return_all) for key in target_keys]
            
            if all_values_none(results):
                results = None            
            
            if results is not None and len(results) == 1:
                results = results[0]
                
        return results

    @staticmethod    
    def search_keys_in(d, target_keys, value_only=True, first_only=True, return_all=False):
        """
        Recursively searches for keys in a nested structure (dict, list, tuple, set)
        and returns their corresponding values, the key-value pairs, or the entire sub-structure,
        optionally returning all matches instead of just the first.

        Parameters:
        d (Any): The nested structure to search. It can be a dict, list, tuple, set, or any iterable.
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
        if d is None:
            return None
        if isinstance(d, dict):
            for key, value in d.items():
                if key in target_keys:
                    result = (value if value_only else {key: value}) if not return_all else d
                    if first_only:
                        return result
                    else:
                        results.append(result)
                sub_result = IterDict.search_keys_in(value, target_keys, value_only, first_only, return_all)
                if sub_result is not None:
                    if first_only:
                        return sub_result
                    else:
                        results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
        elif isinstance(d, (list, tuple, set)):
            for item in d:
                sub_result = IterDict.search_keys_in(item, target_keys, value_only, first_only, return_all)
                if sub_result is not None:
                    if first_only:
                        return sub_result
                    else:
                        results.extend(sub_result if isinstance(sub_result, list) else [sub_result])
        elif isinstance(d, (str, bytes)):
            return None if first_only else results
        else:
            try:
                iterator = iter(d)
                for item in iterator:
                    sub_result = IterDict.search_keys_in(item, target_keys, value_only, first_only, return_all)
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
        return remove_duplicates(results) if not first_only else None



def __dir__():
    return ['IterDict']

__all__ = ['IterDict']
