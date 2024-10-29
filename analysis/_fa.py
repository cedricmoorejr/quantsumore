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
from ..api.equity.parse import fin_statement, dividend
from ..api.prep import stocks_asset
from .._http.response_utils import Request, key_from_mapping
from ..strata_utils import IterDict


   

   
class APIClient:
    def __init__(self, asset):
        self.asset = asset

    def _make_request(self, url):
        content = Request(url, response_format='json', target_response_key='response', return_url=True, onlyParse=True, no_content=False)      
        return content
    
    def _urls(self, ticker, period):
        valid_periods = {'Quarterly': ['Q', 'Quarter', 'Qtr'], 'Annually': ['A', 'Annual']} 
        period = key_from_mapping(period, valid_periods, invert=False)
        if not period:
            raise ValueError("Invalid period.")            
        urls = []
        make_method = getattr(self.asset, 'make')
        financials = make_method(query='financials', ticker=ticker, period=period)
        dividends = make_method(query='dividend_history', ticker=ticker) 

        # Handle financial data
        if isinstance(financials, list):
            urls.extend(financials)
        else:
            urls.append(financials)

        # Handle dividend data
        if isinstance(dividends, list):
            urls.extend(dividends)
        else:
            urls.append(dividends)      
        return urls

    def _categorize_content(self, content):        
        categorized_content = {'dividend': [], 'financial_statements': []}
        url_pattern = re.compile(r'https?://(?:[\w-]+\.)+[\w-]+(?:/[\w.-]*)*')
        for entry in content:
            for url, data in entry.items():
                if url_pattern.search(url):
                    if "dividend" in url:
                        categorized_content['dividend'].append({url: data})                    
                    elif "financials" in url:
                        categorized_content['financial_statements'].append({url: data})
        return categorized_content

    def Process(self, ticker, period="Q"):
        urls = self._urls(ticker=ticker, period=period)
        content = self._make_request(urls)
        categorized_content = self._categorize_content(content=content)
        results = {} 
        
        for which, which_content, in categorized_content.items():
            if which == 'financial_statements':             
                if which_content:
                    obj = fin_statement.financials(json_content=which_content)            
                    results['financial_statements'] = [(obj.IncomeStatement, obj.BalanceSheet, obj.CashFlowStatement)]
                        
            elif which == 'dividend':
                if which_content:
                    obj = dividend.dividend_history(json_content=which_content)            
                    results['dividend'] = [(obj.DividendReport, obj.DividendData)]
        return results         

process = APIClient(stocks_asset)
