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
from ...._http.response_utils import clean_initial_content
from ...shape_tools import is_valid_dataframe
from ....strata_utils import IterDict
from ...parse_tools import extract_symbol_from_url


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
        self.error_messages = []
        self.error = True        

        if json_content:
            self.json_content = IterDict.isNested(json_content)

        if self.json_content:
            self.check_data()  # Processes the data and checks for errors
            self.display_error_messages()  # Display error messages regardless of error status
            if not self.error:
                for statementType in self.financialStatements:
                    self.parse(statementType) # Proceed with parsing if no critical errors

    def display_error_messages(self):
        if self.error_messages:
            for x, t in self.error_messages:
                print(f'{x}: {t}')                

    def check_data(self):
        json_content = self.json_content
        def verify_financial_data(financial_datasets):
            acceptable_data = []
            for entry in financial_datasets:
                url, response_info = list(entry.items())[0]

                if response_info['response']['status']['rCode'] == 200:
                    data = response_info['response']['data']
                    if data and 'tabs' in data:
                        if any(data.get(table) for table in ['incomeStatementTable', 'balanceSheetTable', 'cashFlowTable']):
                            message = response_info['response'].get('message')
                            error_message = response_info['response']['status'].get('bCodeMessage')
                            
                            if message or (error_message and any(em.get('errorMessage') for em in error_message)):
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

        validate_financial_data = verify_financial_data(json_content)

        # Initialize the list to store messages
        error_messages_list = []

        for url, check in validate_financial_data:
            if not check: 
                ticker = extract_symbol_from_url(url)
                data = IterDict.find(json_content, target_key=url)
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
                        error_messages_list.append((ticker, message))
                    else:
                        default_message = "Financial statement data data could not be found."
                        error_messages_list.append((ticker, default_message))		

            # Filter to get only URLs that passed validation (those with True status)
            self.error_messages = error_messages_list
            valid_urls = [url for url, is_valid in validate_financial_data if is_valid]
            self.json_content = [entry for entry in json_content if any(url in entry for url in valid_urls)]

            if valid_urls:            
                self.error = False
                
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
           
    def _clean_headers_rows(self, headers, rows):
        empty_indices = []
        cleaned_headers = {}
        for key, value in headers.items():
            if value: 
                cleaned_headers[key] = value
            else:
                empty_indices.append(key)
        cleaned_rows = []
        for row in rows:
            cleaned_row = {k: v for k, v in row.items() if k not in empty_indices}
            cleaned_rows.append(cleaned_row)
        return cleaned_headers, cleaned_rows
           
    def _create_dataframe(self, headers, rows, statement):
        headers, rows = self._clean_headers_rows(headers, rows)    	
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
        finstatement = content[0]['data'][statementType]       
        if finstatement:
            headers = finstatement['headers']
            rows = finstatement['rows']
        self._create_dataframe(headers, rows, statement=statementType)
        
    @property
    def IncomeStatement(self):
        if not is_valid_dataframe(self.income_statement):
            if not self.error_messages:            
                return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.income_statement
       
    @property
    def BalanceSheet(self):
        if not is_valid_dataframe(self.balance_sheet):
            if not self.error_messages:            
                return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.balance_sheet
       
    @property       
    def CashFlowStatement(self):
        if not is_valid_dataframe(self.cash_flow_statement):
            if not self.error_messages:            
                return "Financial Statement data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
        return self.cash_flow_statement
       
    def __dir__(self):
        return ['IncomeStatement', 'BalanceSheet', 'CashFlowStatement']




def __dir__():
    return ['financials', 'FinancialStatement']

__all__ = ['financials', 'FinancialStatement']




