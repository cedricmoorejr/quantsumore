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



import requests
import pandas as pd
from io import StringIO
from copy import deepcopy
import re
import base64
import random
import json

    
NASDAQ_STOCK_LIST_URL = base64.b64decode('aHR0cDovL3d3dy5uYXNkYXF0cmFkZXIuY29tL2R5bmFtaWMvc3ltZGlyL25hc2RhcWxpc3RlZC50eHQ=').decode('utf-8')
NYSE_STOCK_LIST_URL = base64.b64decode('aHR0cHM6Ly93d3cubnlzZS5jb20vcHVibGljZG9jcy9ueXNlL3N5bWJvbHMvRUxJR0lCTEVTVE9DS1NfTllTRUFtZXJpY2FuLnhscw==').decode('utf-8')

# Load user agents
with open('files/user_agents.json', 'r') as file:
    user_agents = json.load(file)

key = random.choice(list(user_agents['Desktop User-Agents'].keys()))
randkey = str(random.randint(1, 5))
ua = user_agents['Desktop User-Agents'][key][randkey]
headers = {'User-Agent': ua}

def get_stock_ticker_data(url):
    response = requests.get(url, headers=headers, timeout=10)
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

def combine_stock_data(ticker_data, truncate=False):
    combined = pd.concat(list(ticker_data.values()), axis=0, ignore_index=True)
    combined = combined.sort_values(by='Symbol', ascending=True)
    duplicates = combined.duplicated(subset=['Symbol'], keep=False)
    df_dup = combined[duplicates].groupby('Symbol')['Exchange'].agg(set)
    combined['Both_Exchanges'] = combined['Symbol'].apply(lambda x: 'Both' if set(['NYSE', 'NASDAQ']) == df_dup.get(x, set()) else combined.loc[combined['Symbol'] == x, 'Exchange'].iloc[0])
    
    df = combined[['Symbol', 'Company', 'Both_Exchanges', 'yahoo_mapping', 'nasdaq_mapping']]
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

if __name__ == "__main__":
    nasdaq_data = get_stock_ticker_data(NASDAQ_STOCK_LIST_URL)
    nyse_data = get_stock_ticker_data(NYSE_STOCK_LIST_URL)
    ticker_data = {"NASDAQ": nasdaq_data, "NYSE": nyse_data}
    combined_data = combine_stock_data(ticker_data, truncate=False)
    combined_data.to_csv('files/stock_tickers.txt', index=False)




