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



import pandas as pd
import json
from copy import deepcopy


def filter_dataframe_columns(df, column_names):
    """
    Filters the DataFrame to include only the specified columns.

    Args:
    df (pd.DataFrame): The DataFrame from which to filter columns.
    column_names (list of str): A list of column names to include in the new DataFrame.

    Returns:
    pd.DataFrame: A new DataFrame containing only the specified columns that exist in the original DataFrame.
    """
    df_copy = deepcopy(df)    
    if isinstance(column_names, str):
        column_names = [column_names]
    filtered_columns = [col for col in column_names if col in df_copy.columns]
    return df_copy[filtered_columns]

def rename_dataframe_columns(df, rename_dict):
    """
    Renames the columns of the DataFrame based on a provided dictionary mapping.

    Args:
    df (pd.DataFrame): The DataFrame whose columns are to be renamed.
    rename_dict (dict): A dictionary mapping current column names to new names.

    Returns:
    pd.DataFrame: A DataFrame with renamed columns, where applicable.
    """
    df_copy = deepcopy(df)    
    valid_renames = {old_name: new_name for old_name, new_name in rename_dict.items() if old_name in df_copy.columns}
    return df_copy.rename(columns=valid_renames)

def apply_conversion_to_columns(df, columns, fun):
    """
    Applies a specified function to the specified columns of a DataFrame.

    Args:
    df (pd.DataFrame): The DataFrame to modify.
    columns (list of str): List of column names to apply the conversion on.
    fun (function): The function to apply to the specified columns.

    Returns:
    pd.DataFrame: The modified DataFrame with specified columns converted.
    """
    df_copy = deepcopy(df)    
    if isinstance(columns, str):
        columns = [columns]    
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = [fun(x) if isinstance(x, (str, int, float)) else x for x in df_copy[col]]            
    return df_copy

def is_valid_dataframe(df):
    """
    Checks if the input is a valid, non-empty DataFrame.

    Args:
    df (pd.DataFrame): The DataFrame to check.
    """
    if not isinstance(df, pd.DataFrame):
        return False
    if df.empty:
        return False
    return True

def normalize_time(df, column_names):
    """Normalize the time part of datetime in the specified column to 00:00:00."""
    df_copy = deepcopy(df)    
    if isinstance(column_names, str):
        column_names = [column_names]
    for column_name in column_names:
        df[column_name] = pd.to_datetime(df[column_name])
        df[column_name] = df[column_name].dt.normalize()
    return df

def get_value_by_index_and_column(df, row_idx, col):
    """
    Retrieves the value from the DataFrame based on row index and either column index or column name.

    Args:
    df (pd.DataFrame): The DataFrame to retrieve the value from.
    row_idx (int): The row index (zero-based).
    col (int or str): The column index (zero-based) or column name.

    Returns:
    The value at the specified row and column position, or an error message if out of range.
    """
    try:
        # Check if 'col' is an integer (column index)
        if isinstance(col, int):
            return df.iloc[row_idx, col]
        # If 'col' is not an integer, treat it as a column name
        elif isinstance(col, str):
            return df.loc[df.index[row_idx], col]
        else:
            return None
    except (IndexError, KeyError):
        return "Index or column name out of range."


def get_row(df, index_value):
    """ Function to return row(s) by index name or number. """    
    if isinstance(index_value, str):
        # If index_value is a string, we assume it's an index label
        if index_value in df.index:
            return df.loc[index_value]
        else:
            return f"Index '{index_value}' not found."
    elif isinstance(index_value, int):
        # If index_value is an integer, we assume it's an index number
        if index_value >= 0 and index_value < len(df):
            return df.iloc[index_value]
        else:
            return f"Index number {index_value} is out of bounds."
    else:
        return "Invalid index type. Please provide a string or integer."


def fix_and_validate_dict_string_or_list(input_data):
    def fix_and_validate_dict_string(dict_string):
        try:
            parsed_dict = json.loads(dict_string)
            return parsed_dict
        except json.JSONDecodeError as e:
            pass
        open_braces = dict_string.count('{')
        close_braces = dict_string.count('}')
        if open_braces > close_braces:
            dict_string += '}' * (open_braces - close_braces)
        if dict_string[-1] != '}':
            dict_string += '}'
        dict_string = dict_string.replace('", "', '", "')
        dict_string = dict_string.replace('": "', '": "')
        dict_string = dict_string.replace(', "', ', "')
        try:
            parsed_dict = json.loads(dict_string)
            return parsed_dict
        except json.JSONDecodeError as e:
            return None
    if isinstance(input_data, list):
        return [fix_and_validate_dict_string(item) for item in input_data]
    elif isinstance(input_data, str):
        return fix_and_validate_dict_string(input_data)
    else:
        raise ValueError("Input data must be either a string or a list of strings.")

def process_dict_or_list(data):
    def convert_to_float(value):
        try:
            return float(value)
        except ValueError:
            return value    
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                new_dict[key] = process_dict_or_list(value)
            elif isinstance(value, str):
                if ' - ' in value: 
                    parts = value.split(' - ')
                    if len(parts) == 2:
                        new_dict[key] = convert_to_float(parts[0])
                    else:
                        new_dict[key] = value
                else:
                    new_dict[key] = convert_to_float(value)
            else:
                new_dict[key] = value
        return new_dict
    elif isinstance(data, list):
        return [process_dict_or_list(item) for item in data]
    else:
        return data

def remove_nested_keys(data):
    data_dict = deepcopy(data)
    def _remove_nested_keys(d):
        if isinstance(d, dict):
            keys_to_remove = []
            for key, value in d.items():
                if isinstance(value, dict):
                    keys_to_remove.append(key)
                else:
                    d[key] = value
            for key in keys_to_remove:
                del d[key]
        elif isinstance(d, list):
            for item in d:
                _remove_nested_keys(item)
    _remove_nested_keys(data_dict)
    return data_dict

def combine_dicts(dict_list):
    result = {}
    def add_key(key, value):
        if key not in result:
            result[key] = value
        else:
            index = 1
            new_key = f"{key}_{index}"
            while new_key in result:
                index += 1
                new_key = f"{key}_{index}"
            result[new_key] = value
    for d in dict_list:
        for key, value in d.items():
            if isinstance(value, dict):
                add_key(key, combine_dicts([value]))
            else:
                add_key(key, value)
    return result

def rename_keys(data, old_keys, new_keys):
    if len(old_keys) != len(new_keys):
        raise ValueError("The list of old keys and new keys must have the same length.")
    new_data = deepcopy(data)
    for old_key, new_key in zip(old_keys, new_keys):
        if old_key in new_data:
            new_data[new_key] = new_data.pop(old_key)
        else:
            raise KeyError(f"The key '{old_key}' does not exist in the dictionary.")
    return new_data

def reorder_dict(original_dict, new_order):
    reordered_dict = {key: original_dict[key] for key in new_order if key in original_dict}
    return reordered_dict

def flatten_nested_lists(list_of_lists):
    flat_list = []
    for item in list_of_lists:
        if isinstance(item, list):
            flat_list.extend(item)
        else:
            flat_list.append(item)
    return flat_list
