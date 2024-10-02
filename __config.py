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
import requests
import os
from io import StringIO
from copy import deepcopy
import datetime
import re
import json
import concurrent.futures

# Custom
from .sys_utils import JSON, filePaths, SQLiteDBHandler



# Set Variables
_JSON_CONFIG_FILE = 'config.json'
__CONFIG_DIRECTORY = "configuration"
__STOCK_TICKERS_FILE = "stock_tickers.txt"
_CRYPTO_JSON_CONFIG_FILE = 'crypto.json'
_CRYPTO_DATABASE_FILE = 'crypto.db'

chrome_pattern = r'Chrome/\d[\d\.]*'
edge_pattern = r'Edge/\d[\d\.]*'
macos_pattern = r'Mac OS X \d[\d_]*'


def _file_exists(file_path):
    """Check if the txt file exists at the designated path."""
    return os.path.exists(file_path)

def _modified_today(file):
    """Check if the file was modified today."""
    try:
        if _file_exists(file):
            timestamp = os.path.getmtime(file)
            modified_date = datetime.datetime.fromtimestamp(timestamp).date()
            today_date = datetime.datetime.today().date()
            return modified_date == today_date
        else:
            return False
    except TypeError:
        return False

def setFile(filename =__STOCK_TICKERS_FILE):
    if not filePaths.trace(file=filename):
        directory_ = filePaths.trace(directory=__CONFIG_DIRECTORY)
        file = directory_ + "\\" + filename
        filePaths.inscribe(file=file, s="", overwrite=True)

def saveFile(data, filename =__STOCK_TICKERS_FILE):
    directory_  = filePaths.trace(directory=__CONFIG_DIRECTORY)  
    file = directory_ + "\\" + filename
    filePaths.inscribe(file=file, s=data, overwrite=True)



_json_file_outdated = JSON(filename=_JSON_CONFIG_FILE).is_outdated()
_file_path = filePaths.trace(file=__STOCK_TICKERS_FILE)
_is_modified_today = _modified_today(_file_path)

# Make Sure File Exists
setFile(filename=__STOCK_TICKERS_FILE)



## HTTP Configuration
##=========================================================
def fetch_chrome_version(url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'):
    """ Fetch and process Google Chrome version data from a URL."""
    response = requests.get(url)
    data = response.json()
    chrome_version = data['channels']['Stable']['version']
    return chrome_version

def fetch_edge_version(url='https://learn.microsoft.com/en-us/deployedge/microsoft-edge-release-schedule'):
    """ Fetch and process Microsoft Edge version data from a URL."""
    response = requests.get(url)
    html_content = response.text

    table_pattern = r'<table[^>]*>(.*?)</table>'
    header_pattern = r'<th[^>]*>(.*?)</th>'
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    cell_pattern = r'<td[^>]*>(.*?)</td>'
    table_match = re.search(table_pattern, html_content, re.DOTALL)
    if not table_match:
        return None

    table_html = table_match.group(1)
    headers = re.findall(header_pattern, table_html, re.DOTALL)
    headers = [re.sub(r'<.*?>', '', header).strip() for header in headers]  # Clean header tags
    rows = re.findall(row_pattern, table_html, re.DOTALL)
    table_data = []
    for row in rows:
        cells = re.findall(cell_pattern, row, re.DOTALL)
        cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]  # Clean cell tags
        if cells:  # Skip empty rows
            table_data.append(cells)
    final_headers, final_rows = headers, table_data
    filtered_rows =  [row for row in final_rows if 'ReleaseVersion' in row[1].replace(" ", "")]
    version = filtered_rows[0][2]
    date_match = re.search(r'\d{1,2}-[A-Za-z]{3}-\d{4}', version)
    if date_match:
        version_part = version[date_match.end():].strip()
        version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_part)
        if version_match:
            cleaned_version = version_match.group(0)
    return cleaned_version

def fetch_macOS_version(url='https://support.apple.com/en-us/109033', least_version=12):
    """ Fetch and process macOS version data from a URL."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the webpage, status code: {response.status_code}")
    html_content = response.text
    table_pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
    cell_pattern = re.compile(r'<t[dh].*?>(.*?)</t[dh]>', re.DOTALL)
    rows = table_pattern.findall(html_content)
    table_data = []
    for row in rows:
        cells = cell_pattern.findall(row)
        cleaned_cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]
        table_data.append(cleaned_cells)
    filtered_table_data = [row for row in table_data if len(row) > 1 and any(char.isdigit() for char in row[1])] # Step 1: Remove lists where the second item doesn't contain any digits
    updated_table_data = [[row[0], row[1].replace('.', '_')] for row in filtered_table_data] # Step 2: Replace "." with "_" in the second item (version)
    filtered_table_data = [row for row in updated_table_data if int(row[1].split('_')[0]) >= least_version] # Step 3: Remove lists where the first number in the version is less than least_version
    
    # Create a list of acceptable versions in the specified format
    acceptable_versions = ([row[1] for row in filtered_table_data][1]
             if len(filtered_table_data) > 1 and [row[1] for row in filtered_table_data][1]
             else [row[1] for row in filtered_table_data][0]) # Get Second Largest Version
    return acceptable_versions



## Stock Configuration
##=========================================================
def get_stock_ticker_data(url):
    response = requests.get(url)
    data_str = response.content.decode('ISO-8859-1').replace('\r', '')
    data = StringIO(data_str)
    delimiters = ['\t', '|']
    dataframe = None
    for sep in delimiters:
        if re.search(re.escape(sep), data_str):
            df = pd.read_csv(data, sep=sep, keep_default_na=False, na_values=[''])
            dataframe = deepcopy(df)
            dataframe.columns = [item.strip() for item in dataframe.columns]
            break
    if dataframe is None or dataframe.empty:
        raise ValueError("No known delimiter found in the data or data is empty.")
    dataframe['yahoo_mapping'] = dataframe['Symbol'].apply(lambda x: x.replace('.', '-') if isinstance(x, str) and '.' in x else x)
    dataframe['nasdaq_mapping'] = dataframe['Symbol'].apply(lambda x: x.replace('-', '^') if isinstance(x, str) and '-' in x else x)
    modifications = {"F-B": "F-PB", "F-C": "F-PC", "F-D": "F-PD"}
    for original, modified in modifications.items():
        dataframe.loc[dataframe['yahoo_mapping'] == original, 'yahoo_mapping'] = modified
    if "nasdaq" in url:
        dataframe = dataframe[dataframe["Test Issue"] == "N"]
        dataframe = dataframe.dropna(subset=['Security Name'])
        dataframe.loc[:, "Exchange"] = "NASDAQ"
        dataframe = dataframe[['Symbol', 'Security Name', 'Exchange', 'yahoo_mapping', 'nasdaq_mapping']]
        dataframe.columns = ['Symbol', 'Company', 'Exchange', 'yahoo_mapping', 'nasdaq_mapping']
    elif "NYSEAmerican" in url:
        dataframe = dataframe[~dataframe["Symbol"].str.contains('\+', case=False, na=False)]
        dataframe = dataframe[~dataframe["Symbol"].str.contains('\^', case=False, na=False)]
        dataframe = dataframe[~dataframe["Company"].str.contains('TEST STOCK', case=False, na=False)]
        dataframe = dataframe[~dataframe["Symbol"].str.contains('TEST', case=False, na=False)]
        dataframe.loc[:, "Exchange"] = "NYSE"
        dataframe = dataframe[['Symbol', 'Company', 'Exchange', 'yahoo_mapping', 'nasdaq_mapping']]
    return dataframe

def _combine(ticker_data, truncate=False):
    combined = pd.concat(list(ticker_data.values()), axis=0, ignore_index=True)
    combined = combined.sort_values(by='Symbol', ascending=True)
    duplicates = combined.duplicated(subset=['Symbol'], keep=False)
    df_dup = combined[duplicates].groupby('Symbol')['Exchange'].agg(set)
    combined['Both_Exchanges'] = combined['Symbol'].apply(lambda x: 'Both' if set(['NYSE', 'NASDAQ']) == df_dup.get(x, set()) else combined.loc[combined['Symbol'] == x, 'Exchange'].iloc[0])
    dataframe = deepcopy(combined)
    df = dataframe[['Symbol', 'Company', 'Both_Exchanges', 'yahoo_mapping', 'nasdaq_mapping']]
    df.columns = ['Symbol', 'Company', 'Exchange', 'yahoo_mapping', 'nasdaq_mapping']
    df = df.drop_duplicates(subset="Symbol", keep="first")
    if truncate:
        df = df[(~df["Company"].str.contains('%', case=False, na=False) | df["Company"].str.contains('ETF', case=True, na=False))]
        df = df[~df["Company"].str.contains('Warrants|Warrant', case=False, na=False) & ~df["Symbol"].str.endswith('W')]
        df = df[~df["Company"].str.contains('Units|Unit', case=False, na=False) & ~df["Symbol"].str.endswith('U')]
        df = df[~df["Company"].str.contains('Rights|Right', case=False, na=False) & ~df["Symbol"].str.endswith('R')]
        df = df[(~df["Company"].str.contains('Preferred', case=False, na=False) | df["Company"].str.contains('ETF', case=True, na=False))]
        df = df[(~df["Company"].str.contains('Preference', case=False, na=False) | df["Company"].str.contains('ETF', case=True, na=False))]
    return df   




## Crypto Database Configuration
##=========================================================
class CryptoConfig:
    def __init__(self, url="https://resonant-cascaron-556ce0.netlify.app/data.json"):
        self.url = url
        self.data_loaded = False   
        self.saved_json_content = None
        self.loaded_data = None        
        self.exchanges = None
        self.pairs = None    
        self.headers = {'Accept': 'application/json'}           
        
    def to_json(self):
        if JSON(filename=_CRYPTO_JSON_CONFIG_FILE).is_outdated():
            content = requests.get(url=self.url, headers=self.headers)
            if content.status_code == 200:            
                try:
                    self.saved_json_content = content.json()
                    JSON(filename=_CRYPTO_JSON_CONFIG_FILE).save(self.saved_json_content)
                    self.loaded_data = json.loads(self.saved_json_content)                
                    if self.saved_json_content:
                        self.data_loaded = True
                        # print("Data Loaded")
                except Exception as e:
                    print(f"Data Not Loaded: {str(e)}")
                    self.data_loaded = False
        else:                    
            try:
                self.loaded_data = JSON(filename=_CRYPTO_JSON_CONFIG_FILE).load()
                if self.loaded_data:
                    self.data_loaded = True
                    # print("Data Loaded")                
            except Exception as e:
                print(f"Data Not Loaded: {str(e)}")
                self.data_loaded = False            

    def to_sqlite(self):
        sqliteDB = SQLiteDBHandler(_CRYPTO_DATABASE_FILE)
        if sqliteDB.is_outdated():
            sqliteDB.reset_database()
            sqliteDB.save(_CRYPTO_JSON_CONFIG_FILE)

    def transform_exchanges(self):
        if self.data_loaded:
            self.exchanges = list(self.loaded_data['crypto_exchanges'].values())        

    def transform_pairs(self):
        if self.data_loaded:
            data = self.loaded_data['pairs']
            data = {
                currency_name: {
                    **currency_info,
                    'currency': currency_name
                }
                for currency_name, currency_info in data.items()
            }
            self.pairs = list(data.values())

    def parse_json(self):
        self.transform_exchanges()
        self.transform_pairs()
        
    def run(self):
        self.to_json()
        self.to_sqlite()
        self.parse_json()








## Main
##=========================================================
def main_parallel():
    """
    Execute multiple data retrieval and processing tasks in parallel.

    This function manages the concurrent execution of several tasks:
    1. Fetching and processing stock ticker data from NYSE and NASDAQ if the data hasn't been modified today.
    2. Fetching the latest OS versions (Chrome, Edge, macOS) if the local JSON configuration is outdated.
    3. Initializing and performing operations defined in the CryptoConfig class, which involves fetching cryptocurrency data and processing it (includes saving to a file).

    The function uses a ThreadPoolExecutor to run these tasks in parallel to improve efficiency, especially given that these tasks involve I/O operations such as network requests and disk writes, which can benefit from concurrent execution.

    Returns:
        tuple: A tuple containing two dictionaries:
            - The first dictionary (`data_results`) maps URLs to their fetched and processed stock data.
            - The second dictionary (`os_results`) labels and stores version numbers for different operating systems (Chrome, Edge, macOS).

    Each task's success or failure will print respective messages to standard output, and any exceptions will be caught and printed, indicating the failure of a specific task.

    Usage:
        data_results, os_results = main_parallel()
        print("Fetched Stock Data:", data_results)
        print("Fetched OS Versions:", os_results)

    Note:
        This function expects several external dependencies and global flags like _is_modified_today and _json_file_outdated to be defined. Ensure these are properly set up in the global environment before calling this function.
    """	
    with concurrent.futures.ThreadPoolExecutor() as executor:
        data_results = {} 
        os_results = {}  

        # Initialize data_futures as an empty dictionary
        data_futures = {}
        
        # Submit task for CryptoConfig class operations
        crypto_config_future = executor.submit(CryptoConfig().run) 

        # Conditional execution for stock ticker data
        if not _is_modified_today:
            urls = [
                "https://www.nyse.com/publicdocs/nyse/symbols/ELIGIBLESTOCKS_NYSEAmerican.xls",
                "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
            ]
            data_futures = {executor.submit(get_stock_ticker_data, url): url for url in urls}
        else:
            print("Stock data recently modified. No need to update.")

        # Conditional execution for OS versions
        os_tasks = {}
        if _json_file_outdated:
            os_tasks = {
                'Chrome': executor.submit(fetch_chrome_version),
                'Edge': executor.submit(fetch_edge_version),
                'macOS': executor.submit(fetch_macOS_version)
            }
        else:
            print("OS version data is up-to-date. No need to update versions.")

        # Retrieve and store results for data futures
        for future in concurrent.futures.as_completed(data_futures):
            url = data_futures[future]
            try:
                data = future.result()
                data_results[url] = data
                print("Data processed successfully.")
            except Exception as e:
                print("Error processing data: {e}")

        # Retrieve and store results for OS version futures
        for os_name, future in os_tasks.items():
            try:
                os_version = future.result()
                os_results[os_name] = os_version
                print(f"OS version for {os_name} completed with result: {os_version}")
            except Exception as e:
                print(f"OS version task for {os_name} raised an exception: {e}")

        # Handle CryptoConfig class operation completion (even though it returns nothing)
        try:
            crypto_config_future.result()  # We wait for it to complete
            print("Crypto configuration process completed.")
        except Exception as e:
            print(f"Crypto configuration task raised an exception: {e}")

        return data_results, os_results



# Call main_parallel and use its results
data, os_versions = main_parallel()


## OS Configuration
##---------------------------------------------------------
if _json_file_outdated:
    GOOGLECHROMEVERSION = None
    MICROSOFTEDGEVERSION = None
    MACOSVERSION = None
            
    GOOGLECHROMEVERSION = os_versions.get("Chrome", None)
    MICROSOFTEDGEVERSION = os_versions.get("Edge", None)
    MACOSVERSION = os_versions.get("macOS", None)

    user_agents_file = filePaths.trace(file=_JSON_CONFIG_FILE)
    file_contents = filePaths.extract(user_agents_file)

    # New version to replace it with
    if GOOGLECHROMEVERSION:
        GOOGLECHROMEVERSION_w_PREFIX = f'Chrome/{GOOGLECHROMEVERSION}'

    if MICROSOFTEDGEVERSION:
        MICROSOFTEDGEVERSION_w_PREFIX = f'Edge/{MICROSOFTEDGEVERSION}'

    if MACOSVERSION:
        MACOSVERSION_w_PREFIX = f'Mac OS X {MACOSVERSION}'

    # Use the alter method of FileHandler
    filePaths.alter(user_agents_file, new=GOOGLECHROMEVERSION_w_PREFIX, pattern=chrome_pattern)
    filePaths.alter(user_agents_file, new=MICROSOFTEDGEVERSION_w_PREFIX, pattern=edge_pattern)
    filePaths.alter(user_agents_file, new=MACOSVERSION_w_PREFIX, pattern=macos_pattern)


## Stock Ticker Configuration
##---------------------------------------------------------
if not _is_modified_today:
    tickers = _combine(ticker_data=data, truncate=False)
    saveFile(tickers)



