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
from ...._http.response_utils import clean_initial_content, get_top_level_key, safe_content_access



class FinancialStatement(pd.DataFrame):
    @property
    def _constructor(self):
        return FinancialStatement

    @property
    def _constructor_sliced(self):
        return pd.Series

# Subclasses for each type of financial statement
class IncomeStatement(FinancialStatement):
    pass

class BalanceSheet(FinancialStatement):
    pass	

class CashFlowStatement(FinancialStatement):
    pass


class financials:
    def __init__(self, json_content=None):
        self.financialStatements = ['incomeStatementTable', 'balanceSheetTable', 'cashFlowTable']    
        self.income_statement = None           
        self.balance_sheet = None            
        self.cash_flow_statement = None             
        self.ticker = None         

        if isinstance(json_content, list):
            self.json_content = json_content
        else:
            self.json_content = [json_content] if json_content else []

        if self.json_content:
            for statementType in self.financialStatements:
                self.parse(statementType)
                
    def _clean_content(self, content):
        return clean_initial_content(content)
       
    def _getTickerSymbol(self, content):
        if isinstance(content, dict):
            if 'symbol' in content:
                return content['symbol']
            for value in content.values():
                found = self._getTickerSymbol(value)
                if found:
                    return found
        elif isinstance(content, list):
            for item in content:
                found = self._getTickerSymbol(item)
                if found:
                    return found
                   
    def __clean_content(self, df, cols):
        def _clean_currency(df, columns):
            def currency_to_float(value):
                if isinstance(value, str):
                    if value == '--':
                        return value
                    value = value.replace('$', '').replace(',', '')
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return value
            dataframe = deepcopy(df)
            for column in columns:
                dataframe[column] = dataframe[column].apply(currency_to_float)
            return dataframe
        return _clean_currency(df, cols)
       
    def _is_data(self, dataframe):
        if dataframe is None or dataframe.empty:
            return False
        else:
            return True
           
    def _create_dataframe(self, headers, rows, statement):
        column_names = [headers[key] for key in sorted(headers.keys())]
        data_for_df = []
        for row in rows:
            data_for_df.append([row[key] for key in sorted(row.keys())])
        df = FinancialStatement(data=data_for_df, columns=column_names)        

        # Rename Date Columns
        date_columns = df.columns[1:] 
        parsed_dates = [dtparse.parse(date) for date in date_columns]
        column_date_strings = [dtparse.parse(date, to_format='%Y-%m-%d') for date in parsed_dates]
        df.columns = [df.columns[0]] + column_date_strings

        # Reorder Columns
        sorted_dates = sorted(parsed_dates, reverse=True) 
        sorted_date_strings = [dtparse.parse(date, to_format='%Y-%m-%d') for date in sorted_dates]
        new_column_order = [df.columns[0]] + sorted_date_strings
        df = df[new_column_order]
        
        # Clean Data Frame
        df = self.__clean_content(df, df.columns[1:])
        df.iloc[:, 1:] = df.iloc[:, 1:].fillna('')
        
        # Set Index
        df.set_index(df.columns[0], inplace=True) 

        if statement == 'incomeStatementTable':
            df.__class__ = IncomeStatement
            self.income_statement = df
        elif statement == 'balanceSheetTable':
            df.__class__ = BalanceSheet
            self.balance_sheet = df
        elif statement == 'cashFlowTable':
            df.__class__ = CashFlowStatement
            self.cash_flow_statement = df

    def parse(self, statementType):
        if not self.ticker:
            self.ticker = self._getTickerSymbol(self.json_content)
        content = self._clean_content(self.json_content)
        top_key = get_top_level_key(content)
        finstatement = safe_content_access(content, [top_key, statementType])
        if finstatement:
            headers = finstatement['headers']
            rows = finstatement['rows']
        self._create_dataframe(headers, rows, statement=statementType)
        
    @property
    def IncomeStatement(self):
        if not self._is_data(self.income_statement):
            return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.income_statement
       
    @property
    def BalanceSheet(self):
        if not self._is_data(self.balance_sheet):
            return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.balance_sheet
       
    @property       
    def CashFlowStatement(self):
        if not self._is_data(self.cash_flow_statement):
            return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.cash_flow_statement
       
    def __dir__(self):
        return ['IncomeStatement', 'BalanceSheet', 'CashFlowStatement']




def __dir__():
    return ['financials', 'FinancialStatement']

__all__ = ['financials', 'FinancialStatement']




