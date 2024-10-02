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

# Custom
from ..prep import treasuryasset
from .parse import trates
from ..._http.response_utils import Request


class APIClient:
    def __init__(self, asset):
        self.asset = asset  

    def TBill(self, period=None, full_table=False):
        """
        Fetch and cache the most up-to-date daily Treasury bill rates.

        This method retrieves the latest Treasury bill rates from the U.S. Treasury's 
        daily data, caches the data using a generated cache key, and returns the 
        fetched data. The data is sourced from the U.S. Treasury's resource center.
        
        Parameters:
            period (str|int|None): The time period for the data query. Formats are:
                - 'CY' (str): Refers to the current year.
                - YYYY (int): A specific year (e.g., 2021).
                - YYYYMM (int): A specific month and year (e.g., 202308).
                - None: If no period is specified, the current month of the current year is used as the default period.        

        Returns:
            dict: A dictionary containing the latest daily Treasury bill rates.
        """
        make_method = getattr(self.asset, 'make')
        url = make_method(query='tbill', period=period)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        if html_content:
            obj = trates.daily_treasury_bill(html_content, full=full_table)
            rates = obj.DATA()
            return rates

    def Yield(self, period=None, full_table=False):
        """
        Fetch and cache the most up-to-date Daily Treasury Par Yield Curve Rates.

        This method retrieves the latest yield curve rates specifically for U.S. Treasury 
        notes and bonds with maturities of 1 year, 2 years, 3 years, 5 years, 7 years, 
        10 years, 20 years, and 30 years. The data is then cached using a generated 
        cache key and returned. 

        Parameters:
            period (str|int|None): The time period for the data query. Formats are:
                - 'CY' (str): Refers to the current year.
                - YYYY (int): A specific year (e.g., 2021).
                - YYYYMM (int): A specific month and year (e.g., 202308).
                - None: If no period is specified, the current month of the current year is used as the default period.
                
        Returns:
            dict: A dictionary containing the latest Daily Treasury Par Yield Curve Rates 
                  for the specified maturities.
        """ 
        make_method = getattr(self.asset, 'make')
        url = make_method(query='tyield', period=period)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        if html_content:
            obj = trates.daily_treasury_yield(html_content, full=full_table)
            rates = obj.DATA()
            return rates

    def YieldAll(self, period=None):
        """
        Fetch and cache the most up-to-date Treasury Yield Curve Rates for all available maturities.

        This method retrieves the latest yield curve rates from the U.S. Treasury for a comprehensive
        set of maturities, including short-term bills and long-term notes and bonds. The maturities
        covered are: 1 Month, 2 Months, 3 Months, 4 Months, 6 Months, 1 Year, 2 Years, 3 Years, 
        5 Years, 7 Years, 10 Years, 20 Years, and 30 Years. The data is cached using a generated 
        cache key and returned.

        Parameters:
            period (str|int|None): The time period for the data query. Formats are:
                - 'CY' (str): Refers to the current year.
                - YYYY (int): A specific year (e.g., 2021).
                - YYYYMM (int): A specific month and year (e.g., 202308).
                - None: If no period is specified, the current month of the current year is used as the default period.
                
        Returns:
            dict: A dictionary containing the latest Treasury yield curve rates for the specified 
                  maturities.
        """ 
        make_method = getattr(self.asset, 'make')
        url = make_method(query='tyield', period=period)
        html_content = Request(url, headers_to_update=None, response_format='html', target_response_key='response', return_url=True, onlyParse=False, no_content=False)
        if html_content:
            obj = trates.treasury_yield_all(html_content)
            rates = obj.DATA()
            return rates

    def __dir__(self):
        return [
            'TBill',
            'Yield',
            'YieldAll'
        ]       


engine = APIClient(treasuryasset)

def __dir__():
    return ['engine']

__all__ = ['engine']

