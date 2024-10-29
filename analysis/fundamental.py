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
import pandas as pd
import numpy as np
import io
import sys

# Custom
from .._http.response_utils import key_from_mapping
from ._frameworks import WriteExcel
from ..date_parser import dtparse



class FinancialStatement(pd.DataFrame):
    @property
    def _constructor(self):
        return FinancialStatement
    @property
    def _constructor_sliced(self):
        return pd.Series

# Subclasses
class IncomeStatement(FinancialStatement):
    pass
class BalanceSheet(FinancialStatement):
    pass	
class CashFlowStatement(FinancialStatement):
    pass
class DividendSummary(FinancialStatement):
    pass
class DividendHistory(FinancialStatement):
    pass
   






def _ratio_output_(func, *args, **kwargs):
    captured = io.StringIO() 
    old = sys.stdout       
    sys.stdout = captured  

    try:
        result = func(*args, **kwargs) 
        output = captured.getvalue()
    finally:
        sys.stdout = old

    if result is not None and output == '':
        return result 
    return output 
   

class fAnalyze:
    """
    A class to analyze financial data and ratios for a given ticker symbol.

    Attributes:
        income_statement (pd.DataFrame): The income statement for the company.
        balance_sheet (pd.DataFrame): The balance sheet for the company.
        cash_flow_statement (pd.DataFrame): The cash flow statement for the company.
        dividend_data (pd.DataFrame or None): The raw data for dividends.
        dividend_report (pd.DataFrame or None): A summary report of the dividend data.
        common_size (Common_Size): A nested class instance to generate common-size financial statements.
        writeStatement: Write financial statements to an excel file.        
    """
    
    def __init__(self, engine):
        """ Initializes the fAnalyze instance with an engine to process financial data and sets default attributes."""    	
        self.engine = engine
        self.ticker = None       
        self._income_statement = pd.DataFrame()  
        self._balance_sheet = pd.DataFrame()  
        self._cash_flow_statement = pd.DataFrame() 
        self.dividend_data = None
        self.dividend_report = None
        self.ratios = self.Ratios(self)
        self.common_size = self.Common_Size(self)       
        self.vertical_analysis = self.Vertical_Analysis(self)           
        self.cache = {}      
    
    class Statement:
        def __init__(self, data):
            """ Initializes the Statement with a DataFrame."""
            self.data = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
            self._parsed_dates = None

        def __getattr__(self, item):
            """ Delegate attribute access to the underlying DataFrame."""
            return getattr(self.data, item)

        def __getitem__(self, key):
            """ Delegate item getting to the DataFrame. """
            return self.data[key]

        def __setitem__(self, key, value):
            """ Delegate item setting to the DataFrame."""
            self.data[key] = value

        def __repr__(self):
            """ Return the representation of the underlying DataFrame."""
            return repr(self.data)

        def list_accounts(self):
            """ Returns a list of accounts, excluding those where all entries are empty strings."""
            statement = self.data.replace('', pd.NA)
            filtered_statement = statement.dropna(how='all')
            accounts = filtered_statement.index.tolist()
            return accounts

        def _get_parsed_dates(self):
            """ Parses column headers into datetime objects, if not already parsed."""
            if self._parsed_dates is None:
                self._parsed_dates = {col: dtparse.parse(col) for col in self.data.columns}
            return self._parsed_dates

        def LineItem(self, account_name, timeframe=None):
            """
            Searches for the specified account name in a case-insensitive manner and returns its value.

            Args:
                account_name (str): The name of the account to search for.
                timeframe (str or None): Specific timeframe to fetch data for ('current', 'past', or None).
                	Note: None returns all

            Returns:
                The value for the specified account and timeframe.

            Raises:
                KeyError: If the account_name or timeframe is not found.
            """
            account_name_lower = account_name.lower()
            accounts_lower_map = {acct.lower(): acct for acct in self.list_accounts()}
            if account_name_lower not in accounts_lower_map:
                raise KeyError(f"Account '{account_name}' not found in the financial statement.")
            original_account_name = accounts_lower_map[account_name_lower]
            if timeframe:
                dates = self._get_parsed_dates()
                if timeframe == "current":
                    selected_date = dtparse.parse(max(dates.values()), to_format='%Y-%m-%d')
                elif timeframe == "past":
                    selected_date = dtparse.parse(min(dates.values()), to_format='%Y-%m-%d')
                else:
                    if timeframe in dates:
                        selected_date = timeframe
                    else:
                        raise ValueError("Invalid timeframe specified.")
                return self.data.loc[original_account_name, selected_date]
            return self.data.loc[original_account_name]
           
        def __dir__(self):
            return ['LineItem'] 

    @property
    def income_statement(self):
        return self._income_statement
    @income_statement.setter
    def income_statement(self, value):
        self._income_statement = self.Statement(value) if value is not None else pd.DataFrame()

    @property
    def balance_sheet(self):
        return self._balance_sheet
    @balance_sheet.setter
    def balance_sheet(self, value):
        self._balance_sheet = self.Statement(value) if value is not None else pd.DataFrame()

    @property
    def cash_flow_statement(self):
        return self._cash_flow_statement
    @cash_flow_statement.setter
    def cash_flow_statement(self, value):
        self._cash_flow_statement = self.Statement(value) if value is not None else pd.DataFrame()


    @property
    def dividend_data(self):
        return self._dividend_data

    @dividend_data.setter
    def dividend_data(self, value):
        self._dividend_data = value

    @property
    def dividend_report(self):
        return self._dividend_report

    @dividend_report.setter
    def dividend_report(self, value):
        self._dividend_report = value
        
    def __dir__(self):
        available_attributes = []       
        financial_statements_exist = (
            hasattr(self._income_statement, 'data') and not self._income_statement.data.empty and
            hasattr(self._balance_sheet, 'data') and not self._balance_sheet.data.empty and
            hasattr(self._cash_flow_statement, 'data') and not self._cash_flow_statement.data.empty
        )
        if financial_statements_exist:
            available_attributes.extend([
                "CommonSize", "balance_sheet", "capex_ratio",
                "cash_flow_statement", "current_ratio", "debt_to_equity_ratio",
                "ebit_margin", "free_cash_flow_to_operating_cash_flow_ratio",
                "gross_profit_margin_ratio", "income_statement", "interest_coverage_ratio",
                "net_profit_margin", "operating_profit_margin_ratio", "quick_ratio",
                "rd_to_revenue_ratio", "sga_to_revenue_ratio", "cash_ratio", "pretax_profit_margin_ratio",
                "tax_burden", "interest_burden", "debt_to_capital_ratio", "defensive_interval_ratio", 
                "fixed_charge_coverage_ratio", "receivables_turnover_ratio", "inventory_turnover_ratio",
                "writeStatement","Statement", "VerticalAnalysis","days_sales_outstanding", "days_inventory_on_hand",
                "payables_turnover_ratio", "days_of_payables", "cash_conversion_cycle", "return_on_equity", "working_capital_turnover", 
                "fixed_asset_turnover", "total_asset_turnover", "operating_return_on_assets", "return_on_assets", "equity_multiplier", 
                "return_on_invested_capital_pre_tax", "return_on_invested_capital_after_tax",
            ])
            if self.dividend_data is not None and self.dividend_report is not None:
                available_attributes.extend([
                    "dividend_data", "dividend_report", "dividend_yield",
                    "ex_dividend_date", "annual_dividend"
                ])
        return available_attributes       

    def __check_data_availability(self, required_data):
        """Helper method to check if the required data is available."""
        for data in required_data:
            if data is None or (hasattr(data, 'empty') and data.empty):
                raise AttributeError("Required financial data is not available.")

    def __clearNA(self, df):
        return df.fillna("")
           
    def get_financial_data(self, ticker, period):
        if isinstance(ticker, list):
            if not ticker:
                raise ValueError("Cannot find ticker symbol!")
            ticker = ticker[0]

        if not isinstance(ticker, str):
            raise ValueError("Ticker must be a single string value.")
           
        self.ticker = ticker
        
        cache_key = (self.ticker, period)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            self.income_statement = cached_data['income_statement']
            self.balance_sheet = cached_data['balance_sheet']
            self.cash_flow_statement = cached_data['cash_flow_statement']
            self.dividend_data = cached_data.get('dividend_data', None)
            self.dividend_report = cached_data.get('dividend_report', None)
        else:
            try:
                income, balance, cash_flow = (None, None, None)                 
                data = self.engine.Process(self.ticker, period)
                income, balance, cash_flow = data['financial_statements'][0]  
                self.income_statement = self.__clearNA(income)
                self.balance_sheet = self.__clearNA(balance)
                self.cash_flow_statement = self.__clearNA(cash_flow)
                self.cache[cache_key] = {
                    'income_statement': self.__clearNA(income),
                    'balance_sheet': self.__clearNA(balance),
                    'cash_flow_statement': self.__clearNA(cash_flow)
                }
                print(f"Financial Statements successfully loaded for {self.ticker}.")
            except Exception as e:
                self.income_statement = None
                self.balance_sheet = None
                self.cash_flow_statement = None                
                print(f"Financial Statements could not be loaded for {self.ticker}. Error: {e}")
            
            # Attempt to load dividend data separately
            try:
                dividend_report, dividend_data = (None, None)               
                dividend_report, dividend_data = data["dividend"][0]
                self.dividend_data = dividend_data
                self.dividend_report = dividend_report
                self.cache[cache_key].update({
                    'dividend_data': dividend_data,
                    'dividend_report': dividend_report
                })
                print(f"Dividend data successfully loaded for {self.ticker}.")
            except ValueError:
                self.dividend_data = None 
                self.dividend_report = None                
                if "Error: " in data["dividend"]:
                    print(data["dividend"].replace("Error: ", ""))    
            except Exception as e:
                print(f"Dividend data could not be loaded for {self.ticker}. This does not affect financial statements.")
                self.dividend_data = None
                self.dividend_report = None  

    def __call__(self, ticker, period):
        """ Calls the instance as a function to fetch and process financial data for a specified ticker and period."""     	
        self.get_financial_data(ticker, period)
    
    def dividend_yield(self):
        """ Return the dividend yield."""
        self.__check_data_availability([self.dividend_data, self.dividend_report])
        return self.ratios._dividend_yield()

    def ex_dividend_date(self):
        """ Return the EX-Dividend date."""
        self.__check_data_availability([self.dividend_data, self.dividend_report])
        return self.ratios._ex_dividend_date()

    def annual_dividend(self):
        """ Return the total annual dividend paid per share."""
        self.__check_data_availability([self.dividend_data, self.dividend_report])
        return self.ratios._annual_dividend()
       
    def current_ratio(self):
        """ Calculate and return the current ratio from the balance sheet."""
        self.__check_data_availability([self.balance_sheet])        
        return self.ratios._current_ratio()
           
    def quick_ratio(self):
        """Calculate and return the quick ratio from the balance sheet."""
        self.__check_data_availability([self.balance_sheet])
        return self.ratios._quick_ratio()
       
    def cash_ratio(self):
        """Calculate and return the cash ratio from the balance sheet."""
        self.__check_data_availability([self.balance_sheet])
        return self.ratios._cash_ratio()

    def debt_to_equity_ratio(self):
        """Calculate and return the debt to equity ratio from the balance sheet."""
        self.__check_data_availability([self.balance_sheet])
        return self.ratios._debt_to_equity_ratio()

    def debt_to_capital_ratio(self):
        """Calculate and return the debt-to-capital ratio from the balance sheet."""
        self.__check_data_availability([self.balance_sheet])
        return self.ratios._debt_to_capital_ratio()

    def gross_profit_margin_ratio(self):
        """Calculate and return the gross margin ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._gross_profit_margin_ratio()

    def operating_profit_margin_ratio(self):
        """Calculate and return the operating margin ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._operating_profit_margin_ratio()

    def net_profit_margin(self):
        """Calculate and return the net profit margin from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._net_profit_margin()

    def ebit_margin(self):
        """Calculate and return the EBIT margin from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._ebit_margin()

    def rd_to_revenue_ratio(self):
        """Calculate and return the R&D to revenue ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._rd_to_revenue_ratio()

    def sga_to_revenue_ratio(self):
        """Calculate and return the SG&A to revenue ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._sga_to_revenue_ratio()

    def interest_coverage_ratio(self):
        """Calculate and return the interest coverage ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._interest_coverage_ratio()

    def pretax_profit_margin_ratio(self):
        """Calculate and return the pretax margin ratio from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._pretax_profit_margin_ratio()

    def tax_burden(self):
        """Calculate and return the tax burden from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._tax_burden()

    def interest_burden(self):
        """Calculate and return the interest burden from the income statement."""
        self.__check_data_availability([self.income_statement])
        return self.ratios._interest_burden()

    def capex_ratio(self):
        """Calculate and return the CAPEX ratio from the cash flow statement."""
        self.__check_data_availability([self.cash_flow_statement])
        return self.ratios._capex_ratio()

    def free_cash_flow_to_operating_cash_flow_ratio(self):
        """Calculate and return the ratio of free cash flow to operating cash flow from the cash flow statement."""
        self.__check_data_availability([self.cash_flow_statement])
        return self.ratios._free_cash_flow_to_operating_cash_flow_ratio()

    def defensive_interval_ratio(self):
        """Calculate and return the defensive interval ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])   
        return self.ratios._defensive_interval_ratio()

    def fixed_charge_coverage_ratio(self, lease_payments=0):
        """ Calculate and return the fixed charge coverage ratio.
        
		        Args:
		            lease_payments (float): Optional lease payments to include.        
        """ 
        self.__check_data_availability([self.income_statement])
        return self.ratios._fixed_charge_coverage_ratio(lease_payments=lease_payments)

    def receivables_turnover_ratio(self):
        """Calculate and return the receivables turnover ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])   
        return self.ratios._receivables_turnover_ratio()

    def inventory_turnover_ratio(self):
        """Calculate and return the inventory turnover ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])        
        return self.ratios._inventory_turnover_ratio()
      
    def days_sales_outstanding(self):
        """Calculate and return the Days Sales Outstanding (DSO)"""    	
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._days_sales_outstanding()
      
    def days_inventory_on_hand(self):
        """Calculate and return the Days Inventory On Hand (DIOH)."""    	
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._days_inventory_on_hand()      
      
    def payables_turnover_ratio(self):
        """Calculate and return the Payables Turnover Ratio."""    	
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._payables_turnover_ratio()     

    def days_of_payables(self):
        """Calculate and return the Number of Days Payables Ratio."""      	
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._days_of_payables()       
     
    def cash_conversion_cycle(self):
        """ Calculate and return the Cash Conversion Cycle (CCC).""" 
        return self.ratios._cash_conversion_cycle() 

    def return_on_equity(self):
        """ Calculate and return the Return on Equity (ROE)."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_equity()

    def working_capital_turnover(self):
        """ Calculate and return the Working Capital Turnover Ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._working_capital_turnover()

    def fixed_asset_turnover(self):
        """ Calculate and return the Fixed Asset Turnover Ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._fixed_asset_turnover()

    def total_asset_turnover(self):
        """ Calculate and return the Total Asset Turnover Ratio."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._total_asset_turnover()

    def operating_return_on_assets(self):
        """ Calculate and return the Operating Return on Assets (OROA)."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._operating_return_on_assets()

    def return_on_assets(self):
        """ Calculate and return the Return on Assets (ROA)."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_assets()

    def equity_multiplier(self):
        """ Calculate and return the Equity Multiplier."""
        self.__check_data_availability([self.balance_sheet])
        return self.ratios._equity_multiplier()

    def return_on_invested_capital_pre_tax(self):
        """ Calculate and return the Pre-Tax Return on Invested Capital (ROIC)."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_invested_capital_pre_tax()

    def return_on_invested_capital_after_tax(self):
        """ Calculate and return the After-Tax Return on Invested Capital (ROIC)."""
        self.__check_data_availability([self.income_statement, self.balance_sheet])
        return self.ratios._return_on_invested_capital_after_tax()
     
     
    def CommonSize(self, financial_statement):
        """
        Return a common size financial statement based on the specified type.

        Parameters:
        financial_statement (str): Identifier for the type of financial statement. Valid identifiers include:
            - For the Income Statement: "I", "IS", "Income", "Income_Statement", "Income Statement"
            - For the Balance Sheet: "B", "BS", "Balance Sheet", "Balance_Sheet"
            - For the Cash Flow Statement: "C", "CF", "Cash", "Cash Flow", "Cash_Flow", "Cash Flow Statement", "Cash_Flow_Statement"

        Returns:
        DataFrame: A DataFrame representing the common size version of the selected financial statement, with each value transformed into a percentage of a key total figure from that statement.
        """
        self.__check_data_availability([self.income_statement, self.balance_sheet, self.cash_flow_statement])
        return self.common_size._CommonSize(financial_statement=financial_statement) 

    def VerticalAnalysis(self, financial_statement):
        """
        Perform and return a vertical analysis of the specified financial statement.
        
        Parameters:
        financial_statement (str): Identifier for the type of financial statement. Valid identifiers include:
            - "I", "IS", "Income", "Income_Statement", "Income Statement" for the Income Statement
            - "B", "BS", "Balance Sheet", "Balance_Sheet" for the Balance Sheet
            - "C", "CF", "Cash", "Cash Flow", "Cash_Flow", "Cash Flow Statement", "Cash_Flow_Statement" for the Cash Flow Statement

        Returns:
        DataFrame: A DataFrame representing the vertical analysis of the financial statement.
        """    	
        self.__check_data_availability([self.income_statement, self.balance_sheet, self.cash_flow_statement])
        return self.vertical_analysis._VerticalAnalysis(financial_statement=financial_statement) 


    ##----------------------------------------------------------------------------------------------------------------------------##
    #| The writeStatement method writes selected financial statements to an Excel file at the specified path. It allows for the   |#
    #| inclusion of standard or common size formats depending on the include_common_size flag. This method simplifies the process |#
    #| of exporting financial data by providing options to export as standard numbers or as percentages of a key total figure,    |#
    #| making it versatile for comparative and period-over-period financial analysis.                                             |#
    ##----------------------------------------------------------------------------------------------------------------------------##    
    def writeStatement(self, save_path, financial_statements=None, include_common_size=False):
        """
        Writes specified financial statements to an Excel file at the given path in either standard or common size format.

        Args:
            save_path (str): The path where the Excel file will be saved. If the file does not exist, it will be created.
                             If it exists, it will be overwritten.
            financial_statements (list of str or str, optional): A list of financial statement names or aliases to be written.
                If None or 'all', all available financial statements will be written. Default is None.
            include_common_size (bool): If True, financial statements will include common size calculations. Default is False.

        Raises:
            ValueError: If any provided financial statement identifiers are invalid or if no valid financial statements
                        are provided.
            Exception: Propagates exceptions from lower-level operations, notably from file handling and Excel operations.
        """        
        self.__check_data_availability([self.income_statement, self.balance_sheet, self.cash_flow_statement])

        valid_statements = {
            "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
            "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
            "Cash Flow Statement": ["Cash Flow Statement", "Cash_Flow_Statement", "C", "CF", "Cash Flow", "Cash_Flow", "Cash"],
        }
        if include_common_size:
            formats = "common_size"
        else:
            formats = "standard"
            
        statements = {
            "standard": {
                "Income Statement": self.income_statement,
                "Balance Sheet": self.balance_sheet,
                "Cash Flow Statement": self.cash_flow_statement
            },
            "common_size": {
                "Income Statement": self.common_size._CommonSize(financial_statement="Income Statement"),
                "Balance Sheet": self.common_size._CommonSize(financial_statement="Balance Sheet"),
                "Cash Flow Statement": self.common_size._CommonSize(financial_statement="Cash Flow Statement")
            }
        }[formats]               

        if financial_statements:
            if isinstance(financial_statements, str):
                financial_statements = [financial_statements]
            try:
                resolved_statements = [key_from_mapping(f, valid_statements, invert=False) for f in financial_statements]
                statements = {name: stmt for name, stmt in statements.items() if name in resolved_statements}
            except KeyError as e:
                raise ValueError(f"Invalid financial statement identifier: {e}")

        if not statements:
            raise ValueError("No valid financial statements provided to write.")

        try:
            with WriteExcel() as excel_writer:
                for name, statement in statements.items():
                    excel_writer.write_statement(statement)
                excel_writer.save(filename=save_path)
        except Exception as e:
            print(f"An error occurred while writing statements: {e}")     
       
       
       
    ##----------------------------------------------------------------------------------------------------------------------------##
    #| The Ratios class within the financial analysis framework serves to calculate various financial ratios that are essential   |#
    #| for assessing the financial health and performance of a company. This class provides methods for calculating liquidity,    |#
    #| solvency, profitability, efficiency, and coverage ratios using data extracted from a company's financial statements.       |#
    ##----------------------------------------------------------------------------------------------------------------------------##      
    
    class Ratios:
        def __init__(self, analyze_instance):
            self.parent = analyze_instance
           
        def __leap_year(self, year):
            """Determine if the specified year is a leap year."""
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 366
            return 365   
           
        def __clean_statement(self, financial_statement, keep=None):
            """Cleans a financial statement DataFrame, replacing '--' and empty strings with pd.NA, optionally keeping certain original markers."""
            valid = ["markers", "blanks", "all"]
            if keep and keep.lower() not in valid:
                raise ValueError("Invalid value for 'keep'. Choose 'all', 'markers', or 'blanks'.")
            statement = deepcopy(financial_statement)
            statement.replace(['--', ''], pd.NA, inplace=True)
            statement = statement.apply(pd.to_numeric, errors='coerce').astype(float)
            if keep == "all":
                return statement.where(~financial_statement.isin(['--', '']), financial_statement)
            elif keep == "markers":
                return statement.where(~financial_statement.isin(['--']), financial_statement)
            elif keep == "blanks":
                return statement.where(~financial_statement.isin(['']), financial_statement)
            return statement
           
        def __prepare_statement(self, attribute_name):
            statement = getattr(self.parent, attribute_name, None)
            if statement is None:
                # print(f"Warning: {attribute_name} not found in parent.")
                return None
            cleaned_statement = self.__clean_statement(statement, keep="markers")
            if cleaned_statement.empty:
                # print(f"Warning: Cleaned {attribute_name} resulted in an empty DataFrame.")
                return None
            return cleaned_statement   
           
        def __account(self, statement, account_name, missing_accounts=None, period_selection=None):
            """ Retrieves and cleans an account series from a financial statement DataFrame, handling missing or placeholder values. """
            account_series = statement.loc[account_name]
            if any(value == '--' for value in account_series):
                if missing_accounts is not None:
                    missing_accounts.append(account_name)
                    # print(f"Missing or placeholder data found in account: {account_name}")
                return None
            cleaned_series = account_series.apply(lambda x: None if x == '--' else x)
            if isinstance(period_selection, str) and re.match(r"\d{4}-\d{2}-\d{2}", period_selection):
                return cleaned_series.get(period_selection)
            elif period_selection == 1:
                return cleaned_series.iloc[0]
            elif period_selection == 2:
                return cleaned_series.iloc[-1]
            return cleaned_series
           
        def __account_series(self, account_series, inverse=False):
            """ Adjusts financial figures in a given series by normalizing each amount to reflect daily values, accounting for leap years. """           	
            adjusted = {}
            for date, amount in account_series.items():
                year = pd.to_datetime(date).year 
                days_in_year = self.__leap_year(year)
                if inverse:
                    adjusted[date] = days_in_year / amount
                else:
                    adjusted[date] = amount / days_in_year
            return pd.Series(adjusted)
           
        ## Dividend Ratios
        ##--------------------------------------------------------------------------------------------------
        def _dividend_yield(self):
            try:
                summary = self.parent.dividend_report
                if summary is not None and 'Dividend Yield' in summary['Metric'].values:
                    value = summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'].values
                    if value.size > 0:
                        return float(value[0])
            except:
                print("Error: Dividend Yield is not a valid float.")
            return None

        def _ex_dividend_date(self):
            summary = self.parent.dividend_report
            if summary is not None and 'Ex-Dividend Date' in summary['Metric'].values:
                value = summary.loc[summary['Metric'] == 'Ex-Dividend Date', 'Value'].values
                if value.size > 0:
                    return value[0]
            return None

        def _annual_dividend(self):
            try:
                summary = self.parent.dividend_report
                if summary is not None and 'Annual Dividend' in summary['Metric'].values:
                    value = summary.loc[summary['Metric'] == 'Annual Dividend', 'Value'].values
                    if value.size > 0:
                        return float(value[0])
            except:
                print("Error: Annual Dividend is not a valid float.")
            return None

        ## Ratios
        ##--------------------------------------------------------------------------------------------------
        def _current_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')
            if balance_sheet is not None:
                missing_accounts = []
                current_assets = self.__account(balance_sheet, 'Total Current Assets' , missing_accounts)
                current_liabilities = self.__account(balance_sheet, 'Total Current Liabilities', missing_accounts)  
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (current_liabilities != 0).all():
                    return current_assets / current_liabilities
                else:
                    print("Current liabilities is zero or negative, cannot compute current ratio.")
                    return None                        
            return None
           
        def _quick_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')
            if balance_sheet is not None:
                missing_accounts = []
                cash = self.__account(balance_sheet, 'Cash and Cash Equivalents', missing_accounts)
                short_term_investments = self.__account(balance_sheet, 'Short-Term Investments', missing_accounts)
                receivables = self.__account(balance_sheet, 'Net Receivables', missing_accounts)
                current_liabilities = self.__account(balance_sheet, 'Total Current Liabilities', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (current_liabilities != 0).all():
                    return (cash + short_term_investments + receivables) / current_liabilities
                else:
                    print("Current liabilities is zero or negative, cannot compute quick ratio.")
                    return None                        
            return None
           
        def _cash_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')
            if balance_sheet is not None:
                missing_accounts = []
                cash = self.__account(balance_sheet, 'Cash and Cash Equivalents', missing_accounts)
                short_term_investments = self.__account(balance_sheet, 'Short-Term Investments', missing_accounts)
                current_liabilities = self.__account(balance_sheet, 'Total Current Liabilities', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (current_liabilities != 0).all():
                    return (cash + short_term_investments) / current_liabilities
                else:
                    print("Current liabilities is zero or negative, cannot compute cash ratio.")
                    return None
            return None

        def _debt_to_equity_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')    
            if balance_sheet is not None:
                missing_accounts = []
                short_term_debt = self.__account(balance_sheet, 'Short-Term Debt / Current Portion of Long-Term Debt', missing_accounts)
                long_term_debt = self.__account(balance_sheet, 'Long-Term Debt', missing_accounts)
                total_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (total_equity != 0).all():
                    return (short_term_debt + long_term_debt) / total_equity
                else:
                    print("Total equity contains zero or negative values, cannot compute debt-to-equity ratio.")
                    return None
            return None
        
        def _debt_to_capital_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')
            if balance_sheet is not None:
                missing_accounts = []                
                short_term_debt = self.__account(balance_sheet, 'Short-Term Debt / Current Portion of Long-Term Debt', missing_accounts)
                long_term_debt = self.__account(balance_sheet, 'Long-Term Debt', missing_accounts)
                equity = self.__account(balance_sheet, 'Total Equity', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                total_capital = (short_term_debt + long_term_debt) + equity
                if (total_capital != 0).all():
                    return (short_term_debt + long_term_debt) / total_capital
                else:
                    print("Total capital contains zero or negative values, cannot compute debt-to-capital ratio.")
                    return None
            return None

        def _gross_profit_margin_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                gross_profit = self.__account(income_statement, 'Gross Profit', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (total_revenue != 0).all():
                    return gross_profit / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute gross profit margin ratio.")
                    return None
            return None

        def _operating_profit_margin_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                operating_income = self.__account(income_statement, 'Operating Income', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (total_revenue != 0).all():
                    return operating_income / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute operating profit margin ratio.")
                    return None
                        
            return None

        def _net_profit_margin(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                net_income = self.__account(income_statement, 'Net Income', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (total_revenue != 0).all():
                    return net_income / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute net profit margin.")
                    return None
            return None

        def _ebit_margin(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                ebit = self.__account(income_statement, 'Earnings Before Interest and Tax', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (total_revenue != 0).all():
                    return ebit / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute EBIT margin.")
                    return None
            return None


        def _pretax_profit_margin_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                earnings_before_tax = self.__account(income_statement, 'Earnings Before Tax', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (total_revenue != 0).all():
                    return earnings_before_tax / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute pretax profit margin ratio.")
                    return None
            return None

        def _capex_ratio(self):
            cashflow_statement = self.__prepare_statement('cash_flow_statement')
            if cashflow_statement is not None:
                missing_accounts = []
                net_cash_flow_operating = self.__account(cashflow_statement, 'Net Cash Flow-Operating', missing_accounts)
                capital_expenditures = self.__account(cashflow_statement, 'Capital Expenditures', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (capital_expenditures != 0).all():
                    return net_cash_flow_operating / capital_expenditures
                else:
                    print("Capital expenditures contain zero or negative values, cannot compute capex ratio.")
                    return None
            return None

        def _free_cash_flow_to_operating_cash_flow_ratio(self):
            cashflow_statement = self.__prepare_statement('cash_flow_statement')
            if cashflow_statement is not None:
                missing_accounts = []
                free_cash_flow = _ratio_output_(self._capex_ratio)
                if not isinstance(free_cash_flow, pd.Series):
                    print(free_cash_flow.strip())
                    return None
             
                net_cash_flow_operating = self.__account(cashflow_statement, 'Net Cash Flow-Operating', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (net_cash_flow_operating != 0).all():
                    return free_cash_flow / net_cash_flow_operating
                else:
                    print("Net cash flow operating contains zero or negative values, cannot compute free cash flow to operating cash flow ratio.")
                    return None
            return None

        def _rd_to_revenue_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                rd_expense = self.__account(income_statement, 'Research and Development', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (total_revenue != 0).all():
                    return rd_expense / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute R&D to revenue ratio.")
                    return None
            return None

        def _sga_to_revenue_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                sga_expense = self.__account(income_statement, 'Sales, General and Admin.', missing_accounts)
                total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (total_revenue != 0).all():
                    return sga_expense / total_revenue
                else:
                    print("Total revenue contains zero or negative values, cannot compute SG&A to revenue ratio.")
                    return None
            return None

        def _interest_coverage_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                ebit = self.__account(income_statement, 'Earnings Before Interest and Tax', missing_accounts)
                interest_expense = self.__account(income_statement, 'Interest Expense', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (interest_expense != 0).all():
                    return ebit / interest_expense
                else:
                    print("Interest expense contains zero or negative values, cannot compute interest coverage ratio.")
                    return None
            return None

        def _tax_burden(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []
                net_income  = self.__account(income_statement, 'Net Income', missing_accounts)                
                earnings_before_tax = self.__account(income_statement, 'Earnings Before Tax', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                if (earnings_before_tax != 0).all():
                    return net_income / earnings_before_tax
                else:
                    print("Earnings before tax contains zero or negative values, cannot compute tax burden.")
                    return None
                        
            return None

        def _interest_burden(self):
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None:
                missing_accounts = []       
                earnings_before_tax = self.__account(income_statement, 'Earnings Before Tax', missing_accounts)
                ebit  = self.__account(income_statement, 'Earnings Before Interest and Tax', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None

                if (ebit != 0).all():
                    return earnings_before_tax / ebit
                else:
                    print("EBIT contains zero or negative values, cannot compute interest burden.")
                    return None
                        
            return None

        def _defensive_interval_ratio(self):
            balance_sheet = self.__prepare_statement('balance_sheet')
            income_statement = self.__prepare_statement('income_statement')
            if balance_sheet is not None and income_statement is not None:
                missing_accounts = []
                cash = self.__account(balance_sheet, 'Cash and Cash Equivalents', missing_accounts)
                short_term_investments = self.__account(balance_sheet, 'Short-Term Investments', missing_accounts)
                net_receivables = self.__account(balance_sheet, 'Net Receivables', missing_accounts)
                inventory = self.__account(balance_sheet, 'Inventory', missing_accounts)
                cost_of_revenue = self.__account(income_statement, 'Cost of Revenue', missing_accounts)
                r_and_d = self.__account(income_statement, 'Research and Development', missing_accounts)
                sga = self.__account(income_statement, 'Sales, General and Admin.', missing_accounts)
                if missing_accounts:
                    print(f"Defensive Interval Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                total_liquid_assets = cash + short_term_investments + net_receivables
                total_operating_expenses = cost_of_revenue + r_and_d + sga
                daily_operating_expenses = self.__account_series(total_operating_expenses)
                
                if (daily_operating_expenses != 0).all():
                    return total_liquid_assets / daily_operating_expenses
                else:
                    print("Daily operating expenses contain zero or negative values, cannot compute defensive interval ratio.")
                    return None
                        
            return None

        def _fixed_charge_coverage_ratio(self, lease_payments=0):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                ebit = self.__account(statement, 'Earnings Before Interest and Tax', missing_accounts)
                interest_payments = self.__account(statement, 'Interest Expense', missing_accounts)
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                
                total_fixed_charges = interest_payments + lease_payments
                
                if (total_fixed_charges != 0).all():
                    return (ebit + lease_payments) / total_fixed_charges
                else:
                    print("Total fixed charges contain zero or negative values, cannot compute fixed charge coverage ratio.")
                    return None
            return None
        
        
        ##=============================================
        def _receivables_turnover_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                periods = income_statement.columns
                for i in range(1, len(periods)):
                    current_period = periods[i]
                    previous_period = periods[i-1]
                    net_receivables_current = self.__account(balance_sheet, 'Net Receivables', missing_accounts, current_period)
                    net_receivables_previous = self.__account(balance_sheet, 'Net Receivables', missing_accounts, previous_period)
                    total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None    
                       
                    average_receivables = (net_receivables_current + net_receivables_previous) / 2
                    if average_receivables != 0:
                        ratio = total_revenue / average_receivables
                        ratios[current_period] = ratio
                    else:
                        print(f"Average receivables for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _inventory_turnover_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                periods = income_statement.columns
                for i in range(1, len(periods)):
                    current_period = periods[i]
                    previous_period = periods[i-1]            
                    inventory_current = self.__account(balance_sheet, 'Inventory', missing_accounts, current_period)
                    inventory_previous = self.__account(balance_sheet, 'Inventory', missing_accounts, previous_period)
                    cogs = self.__account(income_statement, 'Cost of Revenue', missing_accounts, current_period)            
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None            
                       
                    average_inventory = (inventory_current + inventory_previous) / 2
                    if average_inventory != 0:
                        ratio = cogs / average_inventory
                        ratios[current_period] = ratio
                    else:
                        print(f"Average inventory for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _days_sales_outstanding(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                days_in_periods = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)        
                date_series = pd.to_datetime(periods)
                for i in range(len(date_series) - 1):
                    days_in_periods.append((date_series[i] - date_series[i + 1]).days)
                    
                average_interval = sum(days_in_periods) / len(days_in_periods)
                days_in_periods.append(int(average_interval)) 

                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    days_in_period = days_in_periods[i]
                    current_receivables = self.__account(balance_sheet, 'Net Receivables', missing_accounts, current_period)
                    previous_receivables = self.__account(balance_sheet, 'Net Receivables', missing_accounts, previous_period)
                    total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 
                    
                    average_receivables = (current_receivables + previous_receivables) / 2
                    if average_receivables != 0:
                        ratio = (average_receivables / total_revenue) * days_in_period
                        ratios[current_period] = ratio
                    else:
                        print(f"Average receivables for period {current_period} is zero or negative, cannot compute days sales outstanding ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _days_inventory_on_hand(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')    
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                days_in_periods = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True) 
                date_series = pd.to_datetime(periods)
                for i in range(len(date_series) - 1):
                    days_in_periods.append((date_series[i] - date_series[i + 1]).days)
                    
                average_interval = sum(days_in_periods) / len(days_in_periods)
                days_in_periods.append(int(average_interval)) 

                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    days_in_period = days_in_periods[i]
                    current_inventory = self.__account(balance_sheet, 'Inventory', missing_accounts, current_period)
                    previous_inventory = self.__account(balance_sheet, 'Inventory', missing_accounts, previous_period)
                    cogs = self.__account(income_statement, 'Cost of Revenue', missing_accounts, current_period)            
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 
                       
                    average_inventory = (current_inventory + previous_inventory) / 2
                    if average_inventory != 0:
                        ratio = (average_inventory / cogs) * days_in_period
                        ratios[current_period] = ratio
                    else:
                        print(f"Average inventory for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _payables_turnover_ratio(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')    
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True) 
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    current_payables = self.__account(balance_sheet, 'Accounts Payable', missing_accounts, current_period)
                    previous_payables = self.__account(balance_sheet, 'Accounts Payable', missing_accounts, previous_period)
                    cogs = self.__account(income_statement, 'Cost of Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 
                                           
                    average_payables = (current_payables + previous_payables) / 2                    
                    if average_payables != 0:
                        ratio = cogs / average_payables
                        ratios[current_period] = ratio
                    else:
                        print(f"Average payables for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None
           
        def _days_of_payables(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')    
            if income_statement is not None and balance_sheet is not None:
                ratios = {}
                missing_accounts = []
                days_in_periods = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True) 
                date_series = pd.to_datetime(periods)
                for i in range(len(date_series) - 1):
                    days_in_periods.append((date_series[i] - date_series[i + 1]).days)
                    
                average_interval = sum(days_in_periods) / len(days_in_periods)
                days_in_periods.append(int(average_interval)) 
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    days_in_period = days_in_periods[i]
                    current_payables = self.__account(balance_sheet, 'Accounts Payable', missing_accounts, current_period)
                    previous_payables = self.__account(balance_sheet, 'Accounts Payable', missing_accounts, previous_period)
                    cogs = self.__account(income_statement, 'Cost of Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None
                    
                    average_payables = (current_payables + previous_payables) / 2
                    if average_payables != 0:
                        ratio = (average_payables / cogs) * days_in_period
                        ratios[current_period] = ratio
                    else:
                        print(f"Average payables for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None           
          
        def _cash_conversion_cycle(self):
            dio = self._days_inventory_on_hand()
            dso = self._days_sales_outstanding()
            dpo = self._days_of_payables()
            ccc = pd.Series(index=dio.index)
            for period in ccc.index:
                missing_components = []        
                if period not in dio:
                    missing_components.append("Days Inventory on Hand (DIO)")
                if period not in dso:
                    missing_components.append("Days Sales Outstanding (DSO)")
                if period not in dpo:
                    missing_components.append("Days of Payables (DPO)")
                if missing_components:
                    ccc[period] = None
                    print(f"Missing components for period {period}: {', '.join(missing_components)}. Cannot calculate CCC.")
                    return None
                else:
                    ccc[period] = dio[period] + dso[period] - dpo[period]
            return ccc

        def _return_on_equity(self):
            income_statement = self.__prepare_statement('income_statement')
            balance_sheet = self.__prepare_statement('balance_sheet')
            if income_statement is not None and balance_sheet is not None:    
                missing_accounts = []
                ratios = {}    
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    net_income = self.__account(income_statement, 'Net Income', missing_accounts, current_period)
                    current_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts, current_period)
                    previous_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts, previous_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 
                    
                    average_equity = (current_equity + previous_equity) / 2
                    if average_equity != 0:
                        ratio = (net_income / average_equity) * 100
                        ratios[current_period] = ratio
                    else:
                        print(f"Average equity for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None 

        def _working_capital_turnover(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:    
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                ratios = {}
                missing_accounts = []
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    current_assets = self.__account(balance_sheet, 'Total Current Assets', missing_accounts, current_period)
                    previous_assets = self.__account(balance_sheet, 'Total Current Assets', missing_accounts, previous_period)
                    current_liabilities = self.__account(balance_sheet, 'Total Current Liabilities', missing_accounts, current_period)
                    previous_liabilities = self.__account(balance_sheet, 'Total Current Liabilities', missing_accounts, previous_period)
                    net_sales = self.__account(income_statement, 'Total Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    average_working_capital = (
                        ((current_assets - current_liabilities) +
                         (previous_assets - previous_liabilities)) / 2
                    )            
                    if average_working_capital != 0:
                        ratio = net_sales / average_working_capital
                        ratios[current_period] = ratio
                    else:
                        print(f"Average working capital for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None  

        def _fixed_asset_turnover(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:        
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                missing_accounts = []
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    current_fixed_assets = self.__account(balance_sheet, 'Fixed Assets', missing_accounts, current_period)
                    previous_fixed_assets = self.__account(balance_sheet, 'Fixed Assets', missing_accounts, previous_period)
                    net_sales = self.__account(income_statement, 'Total Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    average_fixed_assets = (current_fixed_assets + previous_fixed_assets) / 2
                    if average_fixed_assets != 0:
                        ratio = net_sales / average_fixed_assets
                        ratios[current_period] = ratio
                    else:
                        print(f"Average fixed assets for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None   

        def _total_asset_turnover(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                missing_accounts = []
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    current_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, current_period)
                    previous_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, previous_period)
                    net_sales = self.__account(income_statement, 'Total Revenue', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    average_total_assets = (current_total_assets + previous_total_assets) / 2
                    if average_total_assets != 0:
                        ratio = net_sales / average_total_assets
                        ratios[current_period] = ratio
                    else:
                        print(f"Average total assets for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None
           
        def _operating_return_on_assets(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                missing_accounts = []
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    operating_income = self.__account(income_statement, 'Operating Income', missing_accounts, current_period)
                    current_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, current_period)
                    previous_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, previous_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None
                    
                    average_total_assets = (current_total_assets + previous_total_assets) / 2            
                    if average_total_assets != 0:
                        ratio = (operating_income / average_total_assets) * 100
                        ratios[current_period] = ratio
                    else:
                        print(f"Average total assets for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _return_on_assets(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                missing_accounts = []
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    net_income = self.__account(income_statement, 'Net Income', missing_accounts, current_period)
                    current_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, current_period)
                    previous_total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, previous_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    average_total_assets = (current_total_assets + previous_total_assets) / 2
                    if average_total_assets != 0:
                        ratio = (net_income / average_total_assets) * 100
                        ratios[current_period] = ratio
                    else:
                        print(f"Average total assets for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _equity_multiplier(self):
            """Calculate and return the Financial Leverage Ratio."""      	
            balance_sheet = self.__prepare_statement('balance_sheet')  
            if balance_sheet is not None:
                missing_accounts = []    
                periods = sorted(balance_sheet.columns, key=pd.to_datetime)
                ratios = {}
                for period in periods:
                    total_assets = self.__account(balance_sheet, 'Total Assets', missing_accounts, period)
                    total_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts, period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    if total_equity != 0:
                        ratio = total_assets / total_equity
                        ratios[period] = ratio
                    else:
                        print(f"Total equity for period {current_period} is zero or negative, cannot compute ratio.")
                        return None                        
                return pd.Series(ratios)
            return None   

        def _return_on_invested_capital_pre_tax(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:
                missing_accounts = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    ebit = self.__account(income_statement, 'Earnings Before Interest and Tax', missing_accounts, current_period)        
                    current_portion_long_term_debt = self.__account(balance_sheet, 'Short-Term Debt / Current Portion of Long-Term Debt', missing_accounts, current_period)  
                    long_term_debt = self.__account(balance_sheet, 'Long-Term Debt', missing_accounts, current_period)                
                    total_debt = current_portion_long_term_debt + long_term_debt      
                    total_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts, current_period)
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    total_invested_capital = total_debt + total_equity
                    if total_invested_capital != 0:
                        ratio = (ebit / total_invested_capital) * 100
                        ratios[current_period] = ratio
                    else:
                        print(f"Total invested capital for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

        def _return_on_invested_capital_after_tax(self):
            balance_sheet = self.__prepare_statement('balance_sheet')  
            income_statement = self.__prepare_statement('income_statement')
            if income_statement is not None and balance_sheet is not None:
                missing_accounts = []
                periods = sorted(balance_sheet.columns, key=pd.to_datetime, reverse=True)
                ratios = {}
                for i in range(len(periods) - 1):
                    current_period = periods[i]
                    previous_period = periods[i + 1]
                    ebit = self.__account(income_statement, 'Earnings Before Interest and Tax', missing_accounts, current_period)
                    income_tax = self.__account(income_statement, 'Income Tax', missing_accounts, current_period)                    
                    current_portion_long_term_debt = self.__account(balance_sheet, 'Short-Term Debt / Current Portion of Long-Term Debt', missing_accounts, current_period)  
                    long_term_debt = self.__account(balance_sheet, 'Long-Term Debt', missing_accounts, current_period)                  
                    total_debt = current_portion_long_term_debt + long_term_debt       
                    total_equity = self.__account(balance_sheet, 'Total Equity', missing_accounts, current_period)
                    effective_tax_rate = income_tax / ebit if ebit != 0 else 0
                    if missing_accounts:
                        print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                        return None 

                    total_invested_capital = total_debt + total_equity
                    if total_invested_capital != 0:
                        ratio = (ebit * (1 - effective_tax_rate) / total_invested_capital) * 100
                        ratios[current_period] = ratio
                    else:
                        print(f"Total invested capital for period {current_period} is zero or negative, cannot compute days inventory on hand ratio.")
                        return None                        
                return pd.Series(ratios)
            return None

    ## Convert Financial Statement to Common Size
    ##-------------------------------------------------------------------------------------------------- 
    class Common_Size:
        def __init__(self, analyze_instance):
            self.parent = analyze_instance

        def __reshape_contents(self, financial_statement):
            df = deepcopy(financial_statement)
            def convert_to_float(value):
                if value == '--':
                    return value
                try:
                    return float(value)
                except ValueError:
                    return value
            df = df.applymap(convert_to_float)            
            return df.reset_index(drop=False)

        def _CommonSize(self, financial_statement):
            valid_statements = {
                "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
                "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
                "Cash Flow Statement": ["Cash Flow Statement", "Cash_Flow_Statement", "C", "CF", "Cash Flow", "Cash_Flow", "Cash"],
            }
            financial_statement = key_from_mapping(financial_statement, valid_statements, invert=False)
            
            if financial_statement == 'Income Statement':
                income_statement = deepcopy(self.parent.income_statement)
                if income_statement is not None and not income_statement.empty:                
                    df = self.__reshape_contents(income_statement)
                    for col in list(df.columns[1:]):
                        total_revenue = df.loc[df[df.columns[0]] == 'Total Revenue', col].values[0]
                        if total_revenue == '--' or not isinstance(total_revenue, (int, float)):
                            continue                        
                        df[col + ' (%)'] = df[col].apply(lambda x: (x / total_revenue) * 100 if isinstance(x, (int, float)) else x)
                    df.set_index(df.columns[0], inplace=True)
                    return df.fillna('') 
                
            if financial_statement == 'Balance Sheet':
                balance_sheet = deepcopy(self.parent.balance_sheet)
                if balance_sheet is not None and not balance_sheet.empty:                
                    df = self.__reshape_contents(balance_sheet)
                    for col in list(df.columns[1:]):
                        total_assets = df.loc[df[df.columns[0]] == 'Total Assets', col].values[0]
                        if total_assets == '--' or not isinstance(total_assets, (int, float)):
                            continue                        
                        df[col + ' (%)'] = df[col].apply(lambda x: (x / total_assets) * 100 if isinstance(x, (int, float)) else x)
                    df.set_index(df.columns[0], inplace=True)
                    return df.fillna('') 
                
            if financial_statement == 'Cash Flow Statement':
                cash_flow_statement = deepcopy(self.parent.cash_flow_statement)
                if cash_flow_statement is not None and not cash_flow_statement.empty:                
                    df = self.__reshape_contents(cash_flow_statement)
                    for col in list(df.columns[1:]):
                        net_income = df.loc[df[df.columns[0]] == 'Net Income', col].values[0]
                        if net_income == '--' or not isinstance(net_income, (int, float)):
                            continue                        
                        df[col + ' (%)'] = df[col].apply(lambda x: (x / net_income) * 100 if isinstance(x, (int, float)) else x)
                    df.set_index(df.columns[0], inplace=True)
                    return df.fillna('') 
                   
    ## Perform Vertical Analysis
    ##--------------------------------------------------------------------------------------------------
    class Vertical_Analysis:
        def __init__(self, analyze_instance):
            self.parent = analyze_instance

        def _VerticalAnalysis(self, financial_statement):
            valid_statements = {
                "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
                "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
                "Cash Flow Statement": ["Cash Flow Statement", "Cash_Flow_Statement", "C", "CF", "Cash Flow", "Cash_Flow", "Cash"],
            }
            financial_statement = key_from_mapping(financial_statement, valid_statements, invert=False)
            
            if financial_statement == 'Income Statement':
                statement = deepcopy(self.parent.income_statement)
                if statement is not None and not statement.empty:                      
                    statement.replace(['--', ''], pd.NA, inplace=True)
                    statement = statement.apply(pd.to_numeric, errors='coerce')
                    vertical_analysis = statement.div(statement.loc['Total Revenue'])
                    vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                    vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.income_statement.isin(['--', '']), self.parent.income_statement)
                    return vertical_analysis_formatted
                
            if financial_statement == 'Balance Sheet':
                statement = deepcopy(self.parent.balance_sheet)
                if statement is not None and not statement.empty:                
                    statement.replace(['--', ''], pd.NA, inplace=True)
                    statement = statement.apply(pd.to_numeric, errors='coerce')
                    vertical_analysis = statement.div(statement.loc['Total Assets'])
                    vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                    vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.balance_sheet.isin(['--', '']), self.parent.balance_sheet)
                    return vertical_analysis_formatted
                
            if financial_statement == 'Cash Flow Statement':
                statement = deepcopy(self.parent.cash_flow_statement)
                if statement is not None and not statement.empty:                    
                    statement.replace(['--', ''], pd.NA, inplace=True)
                    statement = statement.apply(pd.to_numeric, errors='coerce')
                    vertical_analysis = statement.div(statement.loc['Net Cash Flow-Operating'])
                    vertical_analysis_formatted = vertical_analysis.applymap(lambda x: f"{x:.2%}" if pd.notna(x) else '')
                    vertical_analysis_formatted = vertical_analysis_formatted.where(~self.parent.cash_flow_statement.isin(['--', '']), self.parent.cash_flow_statement)
                    return vertical_analysis_formatted


def __dir__():
    return ['fAnalyze']

__all__ = ['fAnalyze']























