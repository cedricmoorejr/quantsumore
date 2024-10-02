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
# from ...._http.response_utils import locKeyInStructure, ExtractURLKeys




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
        
        if json_content:
            self.json_content = json_content
            
        if self.json_content:
            self.parse()

    def _query_time(self):
        return dtparse.now(utc=True, as_unix=True) 

    def _extract_symbol(self, url):
        match = re.search(r'(?:\/|\?|&|symbols=)([A-Z]{1,4}[-.^]?[A-Z]{0,4})(?=[\/\?&]|$)', url)
        return match.group(1) if match else None
       
    def _convert_to_float(self, value):
        try:
            value = re.sub(r'[\$,]', '', str(value))
            if not ('%' in value or '/' in value):
                return float(value)
            else:
                return value
        except ValueError:
            return value
           
    def _format_yield(self, dyield):
        if dyield is None:
            return None
        if isinstance(dyield, str) and dyield.endswith('%'):
            dyield = dyield.replace('%', '')
            if dyield.replace('.', '', 1).isdigit():
                dyield = float(dyield) / 100
            else:
                return None 
        elif isinstance(dyield, str):
            if dyield.replace('.', '', 1).isdigit():
                dyield = float(dyield)
            else:
                return None
        if isinstance(dyield, (float, int)):
            return round(dyield, 4)
        return None
           
    def _is_data(self, dataframe):
        if dataframe is None or dataframe.empty:
            return False
        else:
            return True
    
    def parse(self):
        dreport = self.parse_report()
        ddata = self.parse_data()

        if self._is_data(dreport) and self._is_data(ddata):
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
            headers = json_content['response']['data']['dividendHeaderValues']
            headers_df = pd.DataFrame(headers)
            headers_df['URL'] = url
            dataframes.append(headers_df)

        for df in dataframes:
            if 'label' in df.columns:
                summary_frames.append(df)

        # summary = FinancialStatement(pd.concat(summary_frames, ignore_index=True))
        summary = pd.concat(summary_frames, ignore_index=True)
        summary['Symbol'] = summary['URL'].apply(self._extract_symbol)
        summary = summary.drop('URL', axis=1)
        summary = deepcopy(summary)
        summary.columns = ['Metric', 'Value', 'Ticker']
        index = summary[summary['Metric'] == 'Annual Dividend'].index.tolist()
        summary.loc[index, 'Value'] = summary.loc[index, 'Value'].apply(self._convert_to_float)
        summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'] = summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'].apply(self._format_yield)
        summary.loc[summary['Metric'] == 'P/E Ratio', 'Value'] = summary.loc[summary['Metric'] == 'P/E Ratio', 'Value'].apply(self._convert_to_float)
        summary['Value'] = pd.to_datetime(summary['Value'], errors='coerce').dt.strftime('%Y-%m-%d').fillna(summary['Value'])
        # df.__class__ = DividendSummary
        # self.Dividend_Summary = DividendSummary(summary)
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

        # history = FinancialStatement(pd.concat(history_frames, ignore_index=True))
        history = pd.concat(history_frames, ignore_index=True)
        history['Symbol'] = history['URL'].apply(self._extract_symbol)
        history = history.drop('URL', axis=1) 
        history['exOrEffDate'] = history['exOrEffDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['declarationDate'] = history['declarationDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['recordDate'] = history['recordDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)
        history['paymentDate'] = history['paymentDate'].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(x, format='%m/%d/%Y', errors='coerce')) else x)        
        history['timeQueried'] = self._query_time()
        history['timeQueried'] = history['timeQueried'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S:%f'))
        history.columns = [f.replace("Symbol", "Ticker") for f in history.columns]
        history['amount'] = history['amount'].apply(self._convert_to_float)        
        # df.__class__ = DividendHistory
        # self.Dividend_Data = DividendHistory(history)
        return history
        
    @property
    def DividendReport(self):
        if not self._is_data(self.Dividend_Summary) or not self._is_data(self.Dividend_Data):
            return "Dividend data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.Dividend_Summary
       
    @property
    def DividendData(self):
        if not self._is_data(self.Dividend_Summary) or not self._is_data(self.Dividend_Data):
            return "Dividend data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.Dividend_Data

    def __dir__(self):
        return ['DividendReport', 'DividendData']


def __dir__():
    return ['dividend_history']

__all__ = ['dividend_history']



