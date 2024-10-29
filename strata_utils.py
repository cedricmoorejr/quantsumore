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

# Custom
from .date_parser import dtparse


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
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^ \n]*'
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
    def search_keys(d, target_keys, value_only=True, first_only=True, return_all=False, include_key_in_results=False):
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

    @staticmethod 
    # def filter(d, filter_key, filter_value):
    #     """
    #     Filters a complex data structure, recursively checking dictionaries and lists for the presence of a specified key-value pair.
    # 
    #     Parameters:
    #         d (dict or list): The data structure to be filtered, which can be a dictionary, a list, or a nested combination.
    #         filter_key (str): The key to search for within the data structure.
    #         filter_value (Any): The value associated with `filter_key` that the function looks for to include an element in the filtered result.
    # 
    #     Returns:
    #         dict, list, or None: 
    #             - Returns a filtered dictionary or list where only elements containing the specified key-value pair are included.
    #             - If the filter criteria is not met anywhere in the data structure, returns `None`.
    #     """    	
    #     if isinstance(d, dict):
    #         d_dict = {}
    #         for key, value in d.items():
    #             if isinstance(value, (dict, list)):
    #                 filtered_value = IterDict.filter(value, filter_key, filter_value)
    #                 if filtered_value:
    #                     d_dict[key] = filtered_value
    #             elif key == filter_key and value == filter_value:
    #                 return d
    #         return d_dict if d_dict else None
    #     elif isinstance(d, list):
    #         l_list = []
    #         for item in d:
    #             filtered_item = IterDict.filter(item, filter_key, filter_value)
    #             if filtered_item:
    #                 l_list.append(filtered_item)
    #         return l_list if l_list else None
    #     return None
    def filter(d, filter_key, filter_value, regex=False):
        """
        Filters a complex data structure, recursively checking dictionaries and lists for the presence
        of a specified key-value pair or a key with a value matching a regex pattern.

        Parameters:
            d (dict or list): The data structure to be filtered, which can be a dictionary, a list, or a nested combination.
            filter_key (str): The key to search for within the data structure.
            filter_value (Any): The value associated with `filter_key` that the function looks for to include an element in the filtered result.
            regex (bool): If True, treat `filter_value` as a regex pattern to match against the values.

        Returns:
            dict, list, or None: 
                - Returns a filtered dictionary or list where only elements containing the specified key-value pair are included.
                - If the filter criteria is not met anywhere in the data structure, returns `None`.
        """
        if regex:
            pattern = re.compile(filter_value)
        
        def recursive_filter(data):
            if isinstance(data, dict):
                filtered_dict = {}
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        filtered_value = recursive_filter(value)
                        if filtered_value:
                            filtered_dict[key] = filtered_value
                    elif key == filter_key:
                        if (regex and pattern.search(str(value))) or (not regex and value == filter_value):
                            return data
                return filtered_dict if filtered_dict else None
            
            elif isinstance(data, list):
                filtered_list = []
                for item in data:
                    filtered_item = recursive_filter(item)
                    if filtered_item:
                        filtered_list.append(filtered_item)
                return filtered_list if filtered_list else None
            return None

        return recursive_filter(d)
        
    
    @staticmethod 
    def sort(d, sort_key, sort_order='asc'):
        """
        Sorts a complex data structure, recursively sorting dictionaries and lists based on a specified key within each element.

        Parameters:
            d (dict or list): The data structure to be sorted, which can be a dictionary, a list, or a nested combination.
            sort_key (str): The key to sort the data by.
            sort_order (str): The sort order, either 'asc' for ascending or 'desc' for descending. Defaults to 'asc'.

        Returns:
            dict or list:
                - Returns a sorted dictionary or list based on the specified key and order.
                - If the structure contains dictionaries, sorting will only apply where `sort_key` is found.
                - If sorting criteria are not met, the original data structure or a partially sorted version is returned.
        """    	
        def sort_dict(dictionary):
            if sort_key in dictionary:
                return dictionary[sort_key]
            return float('inf')
        if isinstance(d, dict):
            if sort_key in d:
                return d
            d_dict = {}
            for key, value in d.items():
                d_dict[key] = IterDict.sort(value, sort_key, sort_order)
            if all(isinstance(value, dict) for value in d_dict.values()):
                sorted_items = sorted(d_dict.items(), key=lambda x: sort_dict(x[1]), reverse=(sort_order == 'desc'))
                return dict(sorted_items)
            return d_dict
        elif isinstance(d, list):
            l_list = [IterDict.sort(item, sort_key, sort_order) for item in d]
            if all(isinstance(item, dict) for item in l_list):
                return sorted(l_list, key=sort_dict, reverse=(sort_order == 'desc'))
            return l_list
        return d 

    @staticmethod 
    def find(d, first_only=True, target_key=None, key_path=None, wrap=False):
        """
        Locate data within a structure.

        This method searches for a specified target key or follows a specific key path
        to locate data within a nested dictionary or list structure. Optionally, it can
        wrap the found data within a dictionary under the target key.

        Parameters:
        - d (dict or list): The nested data structure to search within.
        - target_key (str, optional): The key to locate within the nested structure. Ignored if key_path is provided.
        - key_path (list of str, optional): A list of keys specifying a direct path to navigate to the target data.
        - wrap (bool, optional): If True, wraps the found data within a dictionary under the target key. Default is False.
        """
        def recursive_search(data_input, target_key, first_only=True, matches=None):
            if matches is None:
                matches = []
            if isinstance(data_input, dict):
                for key, value in data_input.items():
                    if key == target_key:
                        matches.append(value)
                        if first_only:
                            return value
                    else:
                        result = recursive_search(value, target_key, first_only, matches)
                        if result is not None and first_only:
                            return result
            elif isinstance(data_input, list):
                for item in data_input:
                    result = recursive_search(item, target_key, first_only, matches)
                    if result is not None and first_only:
                        return result
            return matches if not first_only else None

        # If a key_path is provided, navigate through it
        if key_path:
            current_data = d
            try:
                for key in key_path:
                    if isinstance(current_data, list):
                        current_data = [item[key] for item in current_data if isinstance(item, dict) and key in item][0]
                    else:
                        current_data = current_data[key]
                result = current_data
            except (IndexError, KeyError):
                result = None
        else:
            result = recursive_search(d, target_key, first_only)
            
        if wrap and result is not None:
            return {target_key: result}
        
        return result

    @staticmethod  
    def to_numeric(d, conversion=float, keys_to_convert=None):
        """
        Recursively converts specified numeric-like string values within a data structure
        to a designated numeric type (float or int), according to the keys specified.

        Parameters:
            d (dict | list | tuple | set): The input data structure containing nested
                elements that may include numeric-like strings.
            conversion (type, optional): The type to convert numeric-like strings to.
                Defaults to float. Can be set to `int` for integer conversion.
            keys_to_convert (list of str, optional): A list of keys specifying which
                numeric-like strings should be converted. If None, all numeric-like strings
                will be converted regardless of key.

        Returns:
            The same type as `d` (dict, list, tuple, or set) with the numeric-like strings
            converted to the specified type within the constraints of the keys provided.

        Note:
            - The conversion is applied recursively, meaning that if a nested dictionary, list,
              tuple, or set contains keys from `keys_to_convert`, those will be converted.
            - If `keys_to_convert` is not provided, all numeric-like strings encountered will
              be converted to the specified numeric type.
            - The function uses a call stack to track and apply conversions selectively based
              on the nesting level and the presence of specified keys.
        """    
        def recursive_convert(input_data):
            if isinstance(input_data, dict):
                return {
                    key: recursive_convert(value) if (keys_to_convert is None or key in keys_to_convert) else value
                    for key, value in input_data.items()
                }
            elif isinstance(input_data, list):
                return [recursive_convert(item) for item in input_data]
            elif isinstance(input_data, tuple):
                return tuple(recursive_convert(item) for item in input_data)
            elif isinstance(input_data, set):
                if keys_to_convert is None or any(parent_key in keys_to_convert for parent_key in call_stack):
                    return {recursive_convert(item) for item in input_data}
                else:
                    return input_data
            elif isinstance(input_data, str):
                if input_data.isdigit():
                    return float(input_data) if conversion == float else int(input_data) 
                else:
                    try:
                        clean_data = input_data.replace('$', '').replace(',', '')
                        return float(clean_data) if conversion == float else int(float(clean_data))
                    except ValueError:
                        return input_data
            elif isinstance(input_data, (int, float)):
                return float(input_data) if conversion == float else int(input_data)
            else:
                return input_data
        call_stack = []
        def handle_conversion(input_data):
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    if keys_to_convert is None or key in keys_to_convert:
                        call_stack.append(key)
                        input_data[key] = recursive_convert(value)
                        call_stack.pop()
                    else:
                        input_data[key] = handle_conversion(value)
            elif isinstance(input_data, list):
                input_data = [handle_conversion(item) for item in input_data]
            elif isinstance(input_data, tuple):
                input_data = tuple(handle_conversion(item) for item in input_data)
            return input_data
        data_copy = deepcopy(d)
        return handle_conversion(data_copy)
      
    @staticmethod  
    def to_rate(r, keys_to_convert=None):
        """
        Converts numeric values within a data structure to rate format, either as a percentage 
        or directly as a rate. Rates are converted based on specific keys provided. 
        Values assumed to be rates (between 0 and 1) are formatted to four decimal places. 
        Values above 1 are treated as percentages and converted to rates by dividing by 100.0.

        Parameters:
            r (dict | list | tuple | set): The input data structure containing nested elements
                that may include numeric values in string or numeric form.
            keys_to_convert (list of str, optional): A list of keys specifying which values 
                should be converted to rate format. If None, all suitable numeric values 
                encountered will be converted to rates.

        Returns:
            The same type as `r` (dict, list, tuple, or set) with the numeric values 
            converted to rates based on the presence and rules associated with the specified keys.

        Note:
            - The function applies conversions recursively, allowing nested dictionaries, lists,
              tuples, and sets to contain converted rates if they contain keys from `keys_to_convert`.
            - Values are rounded to four decimal places.
            - Values are converted based on the assumption: if a value is between 0 and 1, it's 
              already a rate; if it's above 1, it's treated as a percentage.
            - A `call_stack` is used to manage the context of nested structures during recursion 
              to apply conversions selectively.
        """    
        def recursive_convert(rate_input):
            if isinstance(rate_input, dict):
                return {
                    key: recursive_convert(value) if (keys_to_convert is None or key in keys_to_convert) else value
                    for key, value in rate_input.items()
                }
            elif isinstance(rate_input, list):
                return [recursive_convert(item) for item in rate_input]
            elif isinstance(rate_input, tuple):
                return tuple(recursive_convert(item) for item in rate_input)
            elif isinstance(rate_input, set):
                if keys_to_convert is None or any(parent_key in keys_to_convert for parent_key in call_stack):
                    return {recursive_convert(item) for item in rate_input}
                else:
                    return rate_input
            elif isinstance(rate_input, str):
                if rate_input.replace('.', '', 1).isdigit():
                    rate_input = float(rate_input)
                else:
                    try:
                        clean_data = rate_input.replace('$', '').replace(',', '')
                        rate_input = float(clean_data)
                    except ValueError:
                        return rate_input
            if isinstance(rate_input, (float, int)):
                if 0 <= rate_input <= 1:
                    return round(rate_input, 4) 
                else:
                    return round(rate_input / 100.0, 4)
            return rate_input
        call_stack = []
        def handle_conversion(rate_input):
            if isinstance(rate_input, dict):
                for key, value in rate_input.items():
                    if keys_to_convert is None or key in keys_to_convert:
                        call_stack.append(key)
                        rate_input[key] = recursive_convert(value)
                        call_stack.pop()
                    else:
                        rate_input[key] = handle_conversion(value)
            elif isinstance(rate_input, list):
                rate_input = [handle_conversion(item) for item in rate_input]
            elif isinstance(rate_input, tuple):
                rate_input = tuple(handle_conversion(item) for item in rate_input)
            return rate_input
        rate_copy = deepcopy(r)
        return handle_conversion(rate_copy) 
       
    @staticmethod  
    def to_date(d, from_format=None, to_format=None, to_unix_timestamp=False, keys_to_convert=None):
        """
        Recursively convert date strings in various data structures to specified date formats or Unix timestamps using a custom date parsing class.

        Parameters:
            d (dict, list, tuple, set): The input data which may contain date strings. This can be a dictionary, list, tuple, or set.
            from_format (str, optional): The format of the input date strings. If specified, this format will be strictly used for parsing dates.
            to_format (str, optional): The desired format for the output date strings. If not specified, dates will remain in their original format.
            to_unix_timestamp (bool): If True, converts date strings to Unix timestamps. Defaults to False.
            keys_to_convert (list of str, optional): Specific keys in dictionaries whose values should be considered for date conversion. If None, all strings are considered for conversion.

        Returns:
            The same type of input data structure (dict, list, tuple, set) with date strings converted according to the specified options.

        Raises:
            ValueError: If a date string is found and cannot be parsed or formatted as specified, though the function handles it by returning the original string.

        Notes:
            - The function is recursive, able to handle nested data structures.
            - Date conversion is dependent on the dt_parse class's ability to recognize and convert date formats.
            - If `keys_to_convert` is specified, only data associated with these keys will be attempted for conversion. If it's None, all encountered strings will be processed.
        """        
        def recursive_convert(input_data):
            if isinstance(input_data, dict):
                return {
                    key: recursive_convert(value) if (keys_to_convert is None or key in keys_to_convert) else value
                    for key, value in input_data.items()
                }
            elif isinstance(input_data, list):
                return [recursive_convert(item) for item in input_data]
            elif isinstance(input_data, tuple):
                return tuple(recursive_convert(item) for item in input_data)
            elif isinstance(input_data, set):
                if keys_to_convert is None or any(parent_key in keys_to_convert for parent_key in call_stack):
                    return {recursive_convert(item) for item in input_data}
                else:
                    return input_data                   
            elif isinstance(input_data, str):
                try:
                    return dtparse.parse(input_data, from_format, to_format, to_unix_timestamp)
                except ValueError:
                    return input_data
            else:
                return input_data                   
               
        call_stack = []
        def handle_conversion(input_data):
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    if keys_to_convert is None or key in keys_to_convert:
                        call_stack.append(key)
                        input_data[key] = recursive_convert(value)
                        call_stack.pop()
                    else:
                        input_data[key] = handle_conversion(value)
            elif isinstance(input_data, list):
                input_data = [handle_conversion(item) for item in input_data]
            elif isinstance(input_data, tuple):
                input_data = tuple(handle_conversion(item) for item in input_data)
            return input_data
        data_copy = deepcopy(d)
        return handle_conversion(data_copy)   
       
    @staticmethod 
    def rename(d, target_key, key_map):
        """
        Recursively search for a specific key and replace sub-keys within that key based on certain conditions.

        :param d: The data structure to modify (dict or list).
        :param target_key: The key to look for in the dictionary to apply replacements.
        :param key_map: A dictionary mapping old keys to new keys within the found dictionary.
        :return: A modified copy of the data with replaced keys.
        """
        if isinstance(d, dict):
            new_dict = {}
            for key, value in d.items():
                # Check if the current key is the target
                if key == target_key:
                    # If the value is a dictionary, apply the key_map to its keys
                    if isinstance(value, dict):
                        new_value = {key_map.get(sub_key, sub_key): IterDict.rename(sub_value, target_key, key_map)
                                     for sub_key, sub_value in value.items()}
                    else:
                        new_value = IterDict.rename(value, target_key, key_map)
                    new_key = key_map.get(key, key)
                    new_dict[new_key] = new_value
                else:
                    new_dict[key] = IterDict.rename(value, target_key, key_map)
            return new_dict
        elif isinstance(d, list):
            return [IterDict.rename(item, target_key, key_map) for item in d]
        else:
            return d
           
    @staticmethod         
    def isNested(d):
        """
        Ensures that a given dictionary is nested within a list.

        If the input data is not already a list, it encloses the data in a new list.
        If the input is a list and contains any items that are not dictionaries,
        it nests the entire list within another list to ensure uniformity.
        If all items in the list are dictionaries, it returns the list unchanged.

        Parameters:
            d (dict or list): The data to check and potentially modify. 
                                 This should be either a dictionary or a list of dictionaries.

        Returns:
            list: The input data enclosed in a list, modified if necessary.
        """        
        if not isinstance(d, list):
            return [d]
        else:
            if any(not isinstance(item, dict) for item in d):
                return [d]
        return d    
       
    @staticmethod 
    def search_keys_re(d, pattern):
        """
        Recursively search for a dictionary with any key that matches the specified regex pattern
        in a nested structure that may include dictionaries nested within lists.

        :param d: The nested structure (dictionary or list) to search.
        :param pattern: The regex pattern to match keys against.
        :return: The dictionary that contains a key matching the pattern, or None if not found.
        """
        compiled_pattern = re.compile(pattern)
        def remove_none(lst):
            """ Remove all None values from a list. """
            filtered_list = [item for item in lst if item is not None]
            if not filtered_list:
                return None
            return filtered_list

        def recursive_search(data):
            if isinstance(data, dict):
                for key in data.keys():
                    if compiled_pattern.search(key):
                        return data
                for value in data.values():
                    result = recursive_search(value)
                    if result is not None:
                        return result
            elif isinstance(data, list):
                for item in data:
                    result = recursive_search(item)
                    if result is not None:
                        return result
            return None
           
        d = IterDict.isNested(d)
        results = [recursive_search(f) for f in d]        
        return remove_none(results)

    @staticmethod 
    def extract_from(data, target_keys=None):
        """
        Extracts dictionary entries from a nested data structure (dictionaries and lists) 
        based on a specified set of keys or the most extensive set of keys found in the data.

        This function navigates through nested dictionaries and lists to find dictionaries that:
        - Contain all the keys specified in `target_keys` if it is provided.
        - Contain all the keys from the dictionary with the most extensive set of keys, 
          if `target_keys` is not provided.

        Parameters:
        - data (dict | list): The nested data structure from which to extract dictionary entries.
        - target_keys (Iterable, optional): An iterable of keys to look for in dictionaries. 
          If provided, only dictionaries containing all these keys will be extracted. If None,
          the function identifies the dictionary with the maximum keys in the structure and 
          extracts dictionaries that contain all those keys.

        Returns:
        - list: A list of dictionaries that match the criteria of having all the requisite keys.

        Note:
        - The function performs a comprehensive search of all nested levels. It is 
          computationally intensive and may perform poorly on very large or deeply nested data structures.
        """
        entries = []

        def find_max_keys(d, max_keys):
            if isinstance(d, dict):
                if len(d.keys()) > len(max_keys):
                    max_keys.clear()
                    max_keys.update(d.keys())
                for value in d.values():
                    find_max_keys(value, max_keys)
            elif isinstance(d, list):
                for item in d:
                    find_max_keys(item, max_keys)
            return max_keys

        def recurse(d, key_check):
            if isinstance(d, dict):
                if key_check(d):
                    entries.append(d)
                for value in d.values():
                    recurse(value, key_check)
            elif isinstance(d, list):
                for item in d:
                    recurse(item, key_check)

        if target_keys:
            key_check = lambda d: all(key in d for key in target_keys)
        else:
            max_keys = find_max_keys(data, set())
            key_check = lambda d: max_keys.issubset(d.keys())

        recurse(data, key_check)
        return entries       

    @staticmethod 
    def HTMLcontent(d):
        """
        Recursively searches for and extracts the first occurrence of an HTML document from a nested dictionary or list structure.

        The function looks for strings that begin with "<!doctype html", which signifies the start of an HTML document, 
        and returns the first one it finds. The data structure can contain nested dictionaries and/or lists, 
        and the function will explore them recursively until the first HTML content is found.

        Parameters:
        -----------
        data : dict or list
            The input data to search through. This can be a dictionary, list, or a combination of both, containing 
            potentially nested structures of strings, dictionaries, and lists.

        Returns:
        --------
        str or None
            The HTML document as a string if found, otherwise `None` if no HTML content is found in the input.
        """
            
        def recurse(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and value.strip().startswith('<!doctype html'):
                        return value
                    elif isinstance(value, (dict, list)):
                        result = recurse(value)
                        if result is not None:
                            return result
            elif isinstance(data, list):
                for item in data:
                    result = recurse(item)
                    if result is not None:
                        return result
            return None

        if isinstance(d, str) and d.strip().startswith('<!doctype html'):
            return d
        
        elif isinstance(d, list) and len(d) == 1:
            if isinstance(d[0], str) and d[0].strip().startswith('<!doctype html'):
                return d[0]
            
        return recurse(d)       
       
       
       
       
      
class dictEngine(IterDict):
    def __init__(self, data=None):
        self.data = deepcopy(data) if data is not None else None

    def set(self, data):
        """Set the dataset after initialization."""
        self.data = deepcopy(data)

    def __dir__(self):
        base_attributes = dir(super()) + [
            "set",
            "prune_nested_dicts",
            "prune_keys",
            "prune_top_key",
            "unique_keys",
            "unique_url_keys",
            "top_key",
            "count_keys",
            "search_keys",
            "search_keys_in",
            "filter",
            "sort",
            "find",
            "to_numeric",
            "to_rate",
            "to_date",
            "search_keys_re",
            "isNested",
            "rename",
        ]
        
        if self.data is None:
            available_attributes = ["set"]
        else:
            available_attributes = base_attributes
        return sorted(set(available_attributes))

    def prune_nested_dicts(self, exclude, remove_empty=True, inplace=False):
        self._check_data()
        result = super().prune_nested_dicts(self.data, exclude, remove_empty)
        if inplace:
            self.data = result
        else:
            return result

    def prune_keys(self, keys_to_remove, inplace=False):
        self._check_data()
        result = super().prune_keys(self.data, keys_to_remove)
        if inplace:
            self.data = result
        else:
            return result

    def prune_top_key(self, key_to_remove, inplace=False):
        self._check_data()
        result = super().prune_top_key(self.data, key_to_remove)
        if inplace:
            self.data = result
        else:
            return result

    def unique_keys(self, pattern=None, ignore_case=True):
        self._check_data()
        return super().unique_keys(self.data, pattern, ignore_case)

    def unique_url_keys(self, ignore_case=True, flatten=False):
        self._check_data()
        return super().unique_url_keys(self.data, ignore_case, flatten)

    def top_key(self, top_1=True, exclusion=None, exclusion_sensitive=False):
        self._check_data()
        return super().top_key(self.data, top_1, exclusion, exclusion_sensitive)

    def count_keys(self, pattern=None, ignore_case=True):
        self._check_data()
        return super().count_keys(self.data, pattern, ignore_case)

    # def search_keys(self, target_keys, value_only=True, first_only=False, return_all=False, include_key_in_results=False):
    #     self._check_data()
    #     return super().search_keys(self.data, target_keys, value_only, first_only, return_all, include_key_in_results)
    # 
    # def search_keys_in(self, target_keys, value_only=True, first_only=True, return_all=False):
    #     self._check_data()
    #     return super().search_keys_in(self.data, target_keys, value_only, first_only, return_all)
    # 
    # def search_keys_re(self, pattern):
    #     self._check_data()
    #     return super().search_keys_re(self.data, pattern)
    
    def search_keys(self, target_keys, value_only=True, first_only=False, return_all=False, include_key_in_results=False, inplace=False):
        self._check_data()
        result = super().search_keys(self.data, target_keys, value_only, first_only, return_all, include_key_in_results)
        if inplace:
            self.data = result
        else:
            return result

    def search_keys_in(self, target_keys, value_only=True, first_only=True, return_all=False, inplace=False):
        self._check_data()
        result = super().search_keys_in(self.data, target_keys, value_only, first_only, return_all)
        if inplace:
            self.data = result
        else:
            return result

    def search_keys_re(self, pattern, inplace=False):
        self._check_data()
        result = super().search_keys_re(self.data, pattern)
        if inplace:
            self.data = result
        else:
            return result
           
    def filter(self, filter_key, filter_value, regex=False, inplace=False):
        self._check_data()
        result = super().filter(self.data, filter_key, filter_value, regex=False)
        if inplace:
            self.data = result
        else:
            return result

    def sort(self, sort_key, sort_order='asc', inplace=False):
        self._check_data()
        result = super().sort(self.data, sort_key, sort_order)
        if inplace:
            self.data = result
        else:
            return result

    def find(self, first_only=True, target_key=None, key_path=None, wrap=False, inplace=False):
        self._check_data()
        result = super().find(self.data, first_only, target_key, key_path, wrap)
        if inplace:
            self.data = result
        else:
            return result

    def to_numeric(self, conversion=float, keys_to_convert=None, inplace=False):
        self._check_data()
        result = super().to_numeric(self.data, conversion, keys_to_convert)
        if inplace:
            self.data = result
        else:
            return result

    def to_rate(self, keys_to_convert=None, inplace=False):
        self._check_data()
        result = super().to_rate(self.data, keys_to_convert)
        if inplace:
            self.data = result
        else:
            return result           

    def to_date(self, from_format=None, to_format=None, to_unix_timestamp=False, keys_to_convert=None, inplace=False):
        self._check_data()
        result = super().to_date(self.data, from_format, to_format, to_unix_timestamp, keys_to_convert)
        if inplace:
            self.data = result
        else:
            return result 
           
    def rename(self, target_key, key_map, inplace=False):
        self._check_data()
        result = super().rename(self.data, target_key, key_map)
        if inplace:
            self.data = result
        else:
            return result
           
    def extract_from(self, target_keys=None, inplace=False):
        self._check_data()
        result = super().extract_from(self.data, target_keys)
        if inplace:
            self.data = result
        else:
            return result
           
    def isNested(self, inplace=False):
        self._check_data()
        result = super().isNested(self.data)
        if inplace:
            self.data = result
        else:
            return result
           
    def _check_data(self):
        """Internal method to check if data is set before performing operations."""
        if self.data is None:
            raise ValueError("No data has been set. Please set data using the set() method.")
   
      
 

# # Initialize without data
# e = dictEngine()

     
# def __dir__():
#     return ['IterDict', 'e']
# 
# __all__ = ['IterDict', 'e']




def __dir__():
    return ['IterDict', 'dictEngine']

__all__ = ['IterDict', 'dictEngine']


