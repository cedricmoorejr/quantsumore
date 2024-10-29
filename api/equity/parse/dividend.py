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
import pandas as pd
import numpy as np
from copy import deepcopy

# Custom
from ....date_parser import dtparse
from ....strata_utils import IterDict
from ...parse_tools import(
	convert_to_float, 
  extract_symbol_from_url,
  convert_to_yield,
)
from ...shape_tools import is_valid_dataframe


class FinancialStatement(pd.DataFrame):
    @property
    def _constructor(self):
        return FinancialStatement

    @property
    def _constructor_sliced(self):
        return pd.Series

class DividendSummary(FinancialStatement):
    pass
   
class DividendHistory(FinancialStatement):
    pass
   


class dividend_history:
    def __init__(self, json_content=None):
        self.Dividend_Data = None
        self.Dividend_Summary = None
        self.error_messages = []
        self.error = True
        
        if json_content:
            self.json_content = IterDict.isNested(json_content)
            self.check_data()  
            self.display_error_messages() 
            if not self.error:
                self.parse()  

    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')
                
    def check_data(self):
        dividend_content = self.json_content
        
        def verify_dividend_data(dividend_datasets):
            acceptable_data = []
            for entry in dividend_datasets:
                url, response_info = list(entry.items())[0]
                
                if response_info['response']['status']['rCode'] == 200:
                    data = response_info['response']['data']
                    if data and data.get('dividends', None):
                        if data['dividends'].get('rows', []):
                            message = response_info['response'].get('message')
                            error_message = response_info['response']['status'].get('bCodeMessage')
                            if any((message is not None, error_message)):
                                if error_message and any(em.get('errorMessage') for em in error_message):
                                    acceptable_data.append((url, False))
                                else:
                                    acceptable_data.append((url, False))
                            else:
                                acceptable_data.append((url, True))
                        else:
                            acceptable_data.append((url, False))
                    else:
                        acceptable_data.append((url, False))
                else:
                    acceptable_data.append((url, False))
            return acceptable_data

        validate_dividend_data = verify_dividend_data(dividend_content)

        # Initialize the list to store messages
        error_messages_list = []

        for url, check in validate_dividend_data:
            if not check: 
                ticker = extract_symbol_from_url(url)
                data = IterDict.find(dividend_content, target_key=url)
                found_message = IterDict.filter(data, 'message', "^(?!None$)(?i).*", True)
                if found_message:
                    n_message = IterDict.find(found_message, 'message')
                    message = (n_message.rstrip() + ('' if re.search(r'\.$', n_message.rstrip()) else '.') if n_message is not None else None)  
                    error_messages_list.append((ticker, message))
                else:
                    found_error_message = IterDict.filter(data, 'errorMessage', "^(?!None$)(?i).*", True)
                    if found_error_message:
                        n_message = IterDict.find(found_error_message, 'errorMessage')
                        message = (n_message.rstrip() + ('' if re.search(r'\.$', n_message.rstrip()) else '.') if n_message is not None else None)  
                        if message and "not exists" in message:
                            message = "Dividend History information is presently unavailable for this company. It's possible that this company has delisted."
                        error_messages_list.append((ticker, message))
                    else:
                        default_message = "Dividend data could not be found."
                        error_messages_list.append((ticker, default_message))	

            self.error_messages = error_messages_list
            
            # Filter to get only URLs that passed validation (those with True status)
            invalid_div = [url for url, is_valid in validate_dividend_data if not is_valid]
            
            # Filter out invalid dividend data
            dividend_content = [item for item in dividend_content if list(item.keys())[0] not in invalid_div]

            # Update self properties based on validation results
            self.json_content = dividend_content if dividend_content else None

            # Set error flag based on the presence of valid content
            self.error = not self.json_content

    def _check_all_na(self, values):
        return all(pd.isna(value) or value == 'N/A' for value in values)

    def parse(self):
        dreport = self.parse_report()
        ddata = self.parse_data()

        if is_valid_dataframe(dreport) and is_valid_dataframe(ddata):
            if dreport['Ticker'].nunique() == 1:
                ticker = dreport["Ticker"].iloc[0]
                dreport=dreport.drop(columns=['Ticker'])
                new_row = {'Metric': 'Ticker', 'Value': ticker}
                dreport.loc[len(dreport)] = new_row
            report = FinancialStatement(dreport)
                    
            report.__class__ = DividendSummary
            self.Dividend_Summary = DividendSummary(report)

            data = FinancialStatement(ddata)
            data.__class__ = DividendHistory
            self.Dividend_Data = DividendHistory(data)     
            
    def parse_report(self):
        json_content = self.json_content        
        dataframes = []
        summary_frames = []

        for data_item in json_content:
            url, json_content = list(data_item.items())[0]
            headers = IterDict.find(json_content, target_key='dividendHeaderValues', key_path=None, wrap=False)
            headers_df = pd.DataFrame(headers)
            headers_df['URL'] = url
            dataframes.append(headers_df)

        for df in dataframes:
            if 'label' in df.columns:
                summary_frames.append(df)

        summary = pd.concat(summary_frames, ignore_index=True)
        summary['Symbol'] = summary['URL'].apply(extract_symbol_from_url)
        summary = summary.drop('URL', axis=1)
        summary = deepcopy(summary)
        summary.columns = ['Metric', 'Value', 'Ticker']
        index = summary[summary['Metric'] == 'Annual Dividend'].index.tolist()
        summary.loc[index, 'Value'] = summary.loc[index, 'Value'].apply(convert_to_float)
        summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'] = summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'].apply(convert_to_yield)
        summary.loc[summary['Metric'] == 'P/E Ratio', 'Value'] = summary.loc[summary['Metric'] == 'P/E Ratio', 'Value'].apply(convert_to_float)
        summary['Value'] = pd.to_datetime(summary['Value'], errors='coerce').dt.strftime('%Y-%m-%d').fillna(summary['Value'])
        tickers_with_all_na = summary.groupby('Ticker')['Value'].apply(self._check_all_na)
        summary = summary[~summary['Ticker'].isin(tickers_with_all_na[tickers_with_all_na].index)]
        return summary

    def parse_data(self):
        json_content = self.json_content
        
        dataframes = []
        history_frames = []

        for data_item in json_content:
            url, json_content = list(data_item.items())[0]
            dividends = json_content['response']['data']['dividends']['rows']
            dividends_df = pd.DataFrame(dividends)
            dividends_df['URL'] = url
            dataframes.append(dividends_df)
            
        for df in dataframes:
            if 'label' not in df.columns:
                history_frames.append(df)

        history = pd.concat(history_frames, ignore_index=True)
        history['Symbol'] = history['URL'].apply(extract_symbol_from_url)
        history = history.drop('URL', axis=1) 
        history['exOrEffDate'] = history['exOrEffDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['declarationDate'] = history['declarationDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['recordDate'] = history['recordDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['paymentDate'] = history['paymentDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)        
        history['timeQueried'] = dtparse.now(utc=True, as_unix=True) 
        history['timeQueried'] = history['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        history.columns = [f.replace("Symbol", "Ticker") for f in history.columns]
        history['amount'] = history['amount'].apply(convert_to_float)        
        return history
        
    @property
    def DividendReport(self):
        if not is_valid_dataframe(self.Dividend_Summary) or not is_valid_dataframe(self.Dividend_Data):
            if not self.error_messages:
                return "Dividend data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.Dividend_Summary

    @property
    def DividendData(self):
        if not is_valid_dataframe(self.Dividend_Summary) or not is_valid_dataframe(self.Dividend_Data):
            if not self.error_messages:
                return "Dividend data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."            
        return self.Dividend_Data

    def __dir__(self):
        return ['DividendReport', 'DividendData']



def __dir__():
    return ['dividend_history']

__all__ = ['dividend_history']



