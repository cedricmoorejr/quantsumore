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

# Custom
from .._http.response_utils import key_from_mapping



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
   


# _SEPARATOR = '========================================'





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
    """
    def __init__(self, engine):
        """
        Initializes the fAnalyze instance with an engine to process financial data and sets default attributes.

        Args:
            engine: The engine responsible for processing financial data.
        """    	
        self.engine = engine
        self.ticker = None       
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow_statement = pd.DataFrame()
        self.dividend_data = None
        self.dividend_report = None
        self.ratios = self.Ratios(self)
        self.common_size = self.Common_Size(self)       
        self.cache = {}   
        
    def __dir__(self):
        return [
            "CommonSize", "balance_sheet", "capex_ratio",
            "cash_flow_statement", "current_ratio", "debt_to_equity_ratio",
            "ebit_margin", "free_cash_flow", "free_cash_flow_to_operating_cash_flow_ratio",
            "gross_profit_margin_ratio", "income_statement", "interest_coverage_ratio",
            "net_profit_margin", "operating_profit_margin_ratio", "quick_ratio",
            "rd_to_revenue_ratio", "sga_to_revenue_ratio","cash_ratio", "pretax_profit_margin_ratio",
            "tax_burden", "interest_burden", "debt_to_capital_ratio", "defensive_interval_ratio", "fixed_charge_coverage_ratio",
            "receivables_turnover_ratio", "inventory_turnover_ratio", "dividend_data", "dividend_report", "dividend_yield",
            "ex_dividend_date", "annual_dividend",
        ] 

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
                print(f"Financial Statements could not be loaded for {self.ticker}. Error: {e}")
            
            # Attempt to load dividend data separately
            try:
                dividend_report, dividend_data = data["dividend"][0]
                self.dividend_data = dividend_data
                self.dividend_report = dividend_report
                self.cache[cache_key].update({
                    'dividend_data': dividend_data,
                    'dividend_report': dividend_report
                })
                print(f"Dividend data successfully loaded for {self.ticker}.")
            except Exception as e:
                print(f"Dividend data could not be loaded for {self.ticker}. This does not affect financial statements. Error: {e}")


    def __call__(self, ticker, period):
        """ Calls the instance as a function to fetch and process financial data for a specified ticker and period."""     	
        self.get_financial_data(ticker, period)

    def dividend_yield(self):
        """ Return the dividend yield."""    	
        return self.ratios._dividend_yield()

    def ex_dividend_date(self):
        """ Return the EX-Dividend date."""    	
        return self.ratios._ex_dividend_date()

    def annual_dividend(self):
        """ Return the annual dividend."""    	
        return self.ratios._annual_dividend()

    def current_ratio(self):
        """ Calculate and return the current ratio from the balance sheet."""
        return self.ratios._current_ratio()
       
    def quick_ratio(self):
        """ Calculate and return the quick ratio from the balance sheet."""
        return self.ratios._quick_ratio()
       
    def cash_ratio(self):
        """ Calculate and return the cash ratio from the balance sheet. """
        return self.ratios._cash_ratio()

    def debt_to_equity_ratio(self):
        """ Calculate and return the debt to equity ratio from the balance sheet. """
        return self.ratios._debt_to_equity_ratio()

    def debt_to_capital_ratio(self):
        """ Calculate and return the debt-to-capital ratio from the balance sheet."""
        return self.ratios._debt_to_capital_ratio()

    def gross_profit_margin_ratio(self):
        """ Calculate and return the gross margin ratio from the income statement. """
        return self.ratios._gross_profit_margin_ratio()

    def operating_profit_margin_ratio(self):
        """ Calculate and return the operating margin ratio from the income statement. """
        return self.ratios._operating_profit_margin_ratio()

    def net_profit_margin(self):
        """ Calculate and return the net profit margin from the income statement. """
        return self.ratios._net_profit_margin()

    def ebit_margin(self):
        """ Calculate and return the EBIT margin from the income statement."""
        return self.ratios._ebit_margin()

    def rd_to_revenue_ratio(self):
        """ Calculate and return the R&D to revenue ratio from the income statement."""
        return self.ratios._rd_to_revenue_ratio()

    def sga_to_revenue_ratio(self):
        """ Calculate and return the SG&A to revenue ratio from the income statement."""
        return self.ratios._sga_to_revenue_ratio()

    def interest_coverage_ratio(self):
        """ Calculate and return the interest coverage ratio from the income statement."""
        return self.ratios._interest_coverage_ratio()

    def pretax_profit_margin_ratio(self):
        """ Calculate and return the pretax margin ratio from the income statement."""
        return self.ratios._pretax_profit_margin_ratio()

    def tax_burden(self):
        """ Calculate and return the tax burden from the income statement."""
        return self.ratios._tax_burden()

    def interest_burden(self):
        """ Calculate and return the interest burden from the income statement."""
        return self.ratios._interest_burden()

    def capex_ratio(self):
        """ Calculate and return the CAPEX ratio from the cash flow statement."""
        return self.ratios._capex_ratio()

    def free_cash_flow(self):
        """ Calculate and return the free cash flow from the cash flow statement."""
        return self.ratios._free_cash_flow()

    def free_cash_flow_to_operating_cash_flow_ratio(self):
        """ Calculate and return the ratio of free cash flow to operating cash flow from the cash flow statement."""
        return self.ratios._free_cash_flow_to_operating_cash_flow_ratio()

    def defensive_interval_ratio(self):
        """ Calculate and return the defensive interval ratio."""
        return self.ratios._defensive_interval_ratio()

    def fixed_charge_coverage_ratio(self, lease_payments=0):
        """ 
        Calculate and return the fixed charge coverage ratio.

        Args:
            lease_payments (float): Optional lease payments to include.        
        """    	
        return self.ratios._fixed_charge_coverage_ratio()

    def receivables_turnover_ratio(self):
        """ Calculate and return the receivables turnover ratio."""    	
        return self.ratios._receivables_turnover_ratio()

    def inventory_turnover_ratio(self):
        """ Calculate and return the inventory turnover ratio."""    	
        return self.ratios._inventory_turnover_ratio()
       
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
        return self.common_size._CommonSize(financial_statement=financial_statement)
 
    class Ratios:
        def __init__(self, analyze_instance):
            self.parent = analyze_instance
           
        def __leap_year(self, year):
            """Determine if the specified year is a leap year."""
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 366
            return 365   
           
        def __clean_content(self, financial_statement):
            try:
                df = deepcopy(financial_statement)
                for column in df.columns:
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype(float)
                return df
            except:
                return None
           
        def __prepare_statement(self, attribute_name):
            statement = self.__clean_content(getattr(self.parent, attribute_name, None))            
            return statement if statement is not None and not statement.empty else None
           
        def __account(self, statement, account_name, missing_accounts=None, period_selection=None):
            """ Retrieves and cleans an account series from a financial statement DataFrame, handling missing or placeholder values. """   
            account_series = statement.loc[account_name]
            if any(value == '--' for value in account_series):
                if missing_accounts:
                    missing_accounts.append(account_name)                     
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
            summary = self.parent.dividend_report
            if summary is not None:
                return float(summary.loc[summary['Metric'] == 'Dividend Yield', 'Value'].values)
            return None

        def _ex_dividend_date(self):
            summary = self.parent.dividend_report
            if summary is not None:
                return summary.loc[summary['Metric'] == 'Ex-Dividend Date', 'Value'].values
            return None

        def _annual_dividend(self):
            summary = self.parent.dividend_report
            if summary is not None:
                return float(summary.loc[summary['Metric'] == 'Annual Dividend', 'Value'].values)
            return None
           
        ## Liquidity Ratios
        ##--------------------------------------------------------------------------------------------------
        def _current_ratio(self):
            statement = self.__prepare_statement('balance_sheet')
            if statement is not None:
                missing_accounts = []
                current_assets = self.__account(statement, 'Total Current Assets')
                current_liabilities = self.__account(statement, 'Total Current Liabilities')   
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                return current_assets / current_liabilities                
            return None
           
        def _quick_ratio(self):
            statement = self.__prepare_statement('balance_sheet')
            if statement is not None:
                missing_accounts = []
                cash = self.__account(statement, 'Cash and Cash Equivalents')
                short_term_investments = self.__account(statement, 'Short-Term Investments')
                receivables = self.__account(statement, 'Net Receivables')
                current_liabilities = self.__account(statement, 'Total Current Liabilities')                
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None
                return (cash + short_term_investments + receivables) / current_liabilities                
            return None

        def _cash_ratio(self):
            statement = self.__prepare_statement('balance_sheet')
            if statement is not None:
                missing_accounts = []
                cash = self.__account(statement, 'Cash and Cash Equivalents')
                short_term_investments = self.__account(statement, 'Short-Term Investments')
                current_liabilities = self.__account(statement, 'Total Current Liabilities')  
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return (cash + short_term_investments) / current_liabilities        
            return None

        ## Solvency Ratios
        ##--------------------------------------------------------------------------------------------------
        def _debt_to_equity_ratio(self):
            statement = self.__prepare_statement('balance_sheet')    
            if statement is not None:
                missing_accounts = []
                short_term_debt = self.__account(statement, 'Short-Term Debt / Current Portion of Long-Term Debt')
                long_term_debt = self.__account(statement, 'Long-Term Debt')
                total_equity = self.__account(statement, 'Total Equity')                
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return (short_term_debt + long_term_debt) / total_equity                
            return None

        def _debt_to_capital_ratio(self):
            statement = self.__prepare_statement('balance_sheet')
            if statement is not None:
                missing_accounts = []                
                short_term_debt = self.__account(statement, 'Short-Term Debt / Current Portion of Long-Term Debt')
                long_term_debt = self.__account(statement, 'Long-Term Debt')
                equity = self.__account(statement, 'Total Equity')                                
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return (short_term_debt + long_term_debt) / ((short_term_debt + long_term_debt) + equity)      
            return None

        ## Profitability Ratios
        ##--------------------------------------------------------------------------------------------------      
        def _gross_profit_margin_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                gross_profit = self.__account(statement, 'Gross Profit')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return gross_profit / total_revenue        
            return None

        def _operating_profit_margin_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                operating_income = self.__account(statement, 'Operating Income')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return operating_income / total_revenue        
            return None

        def _net_profit_margin(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                net_income = self.__account(statement, 'Net Income')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return net_income / total_revenue        
            return None

        def _ebit_margin(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                ebit = self.__account(statement, 'Earnings Before Interest and Tax')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return ebit / total_revenue        
            return None

        def _pretax_profit_margin_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                earnings_before_tax = self.__account(statement, 'Earnings Before Tax')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return earnings_before_tax / total_revenue        
            return None

        ## Efficiency Ratios
        ##--------------------------------------------------------------------------------------------------  
        def _capex_ratio(self):
            statement = self.__prepare_statement('cash_flow_statement')
            if statement is not None:
                missing_accounts = []
                net_cash_flow_operating = self.__account(statement, 'Net Cash Flow-Operating')
                capital_expenditures = self.__account(statement, 'Capital Expenditures')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return net_cash_flow_operating / capital_expenditures
            return None

        def _free_cash_flow_to_operating_cash_flow_ratio(self):
            statement = self.__prepare_statement('cash_flow_statement')
            if statement is not None:
                missing_accounts = []
                free_cash_flow = self._capex_ratio()
                net_cash_flow_operating = self.__account(statement, 'Net Cash Flow-Operating')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return free_cash_flow / net_cash_flow_operating
            return None

        ## Expense Ratios
        ##--------------------------------------------------------------------------------------------------  
        def _rd_to_revenue_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                rd_expense = self.__account(statement, 'Research and Development')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return rd_expense / total_revenue        
            return None

        def _sga_to_revenue_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                sga_expense = self.__account(statement, 'Sales, General and Admin.')
                total_revenue = self.__account(statement, 'Total Revenue')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return sga_expense / total_revenue        
            return None

        ## Coverage Ratios
        ##--------------------------------------------------------------------------------------------------  
        def _interest_coverage_ratio(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                ebit = self.__account(statement, 'Earnings Before Interest and Tax')
                interest_expense = self.__account(statement, 'Interest Expense')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return ebit / interest_expense        
            return None
        
        ## Other Ratios
        ##--------------------------------------------------------------------------------------------------  
        def _tax_burden(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                net_income  = self.__account(statement, 'Net Income')                
                earnings_before_tax = self.__account(statement, 'Earnings Before Tax')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return net_income / earnings_before_tax        
            return None

        def _interest_burden(self):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []       
                earnings_before_tax = self.__account(statement, 'Earnings Before Tax')
                ebit  = self.__account(statement, 'Earnings Before Interest and Tax')                         
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return earnings_before_tax / ebit        
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
                daily_operating_expenses = self.__account_series(total_operating_expenses) # Calculates days in the period
                return total_liquid_assets / daily_operating_expenses
            return None           
           
        def _fixed_charge_coverage_ratio(self, lease_payments=0):
            statement = self.__prepare_statement('income_statement')
            if statement is not None:
                missing_accounts = []
                ebit = self.__account(statement, 'Earnings Before Interest and Tax')
                interest_payments = self.__account(statement, 'Interest Expense')
                if missing_accounts:
                    print(f"Ratio could not be calculated because of missing account data from: {', '.join(missing_accounts)}")
                    return None                    
                return (ebit + lease_payments) / (interest_payments + lease_payments)       
            return None

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
                    
                    if pd.isnull(net_receivables_current) or pd.isnull(net_receivables_previous):
                        print(f"Missing data for net receivables for periods: {previous_period} or {current_period}")
                        continue
                    average_receivables = (net_receivables_current + net_receivables_previous) / 2
                    if average_receivables > 0:
                        total_revenue = self.__account(income_statement, 'Total Revenue', missing_accounts, period_selection=current_period)
                        ratio = total_revenue / average_receivables
                        ratios[current_period] = ratio
                    else:
                        print(f"Average receivables for period {current_period} is zero or negative, cannot compute turnover ratio.")
                if missing_accounts:
                    print(f"Missing financial data for: {', '.join(missing_accounts)}")
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
                    
                    if pd.isnull(inventory_current) or pd.isnull(inventory_previous):
                        print(f"Missing data for inventory for periods: {previous_period} or {current_period}")
                        continue
                    average_inventory = (inventory_current + inventory_previous) / 2
                    if average_inventory > 0:
                        cogs = self.__account(income_statement, 'Cost of Revenue', missing_accounts, current_period)
                        ratio = cogs / average_inventory
                        ratios[current_period] = ratio
                    else:
                        print(f"Average inventory for period {current_period} is zero or negative, cannot compute turnover ratio.")
                if missing_accounts:
                    print(f"Missing financial data for: {', '.join(missing_accounts)}")
                return pd.Series(ratios)
            return None
           
    ## Convert Financial Statement to Common Size
    ##--------------------------------------------------------------------------------------------------  
    class Common_Size:
        def __init__(self, analyze_instance):
            self.parent = analyze_instance

        def __reshape_contents(self, financial_statement):
            df = deepcopy(financial_statement)
            for column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce').astype(float)
            return df.reset_index(drop=False)

        def _CommonSize(self, financial_statement):
            valid_statements = {
                "Income Statement": ["I", "IS", "Income", "Income_Statement", "Income Statement"],
                "Balance Sheet": ["Balance Sheet", "B", "BS", "Balance_Sheet"],
                "Cash Flow Statement": [
                    "Cash Flow Statement",
                    "Cash_Flow_Statement",
                    "C",
                    "CF",
                    "Cash Flow",
                    "Cash_Flow",
                    "Cash",
                ],
            }            
            financial_statement = key_from_mapping(financial_statement, valid_statements, invert=False)
            if financial_statement == 'Income Statement':
                income_statement = deepcopy(self.parent.income_statement)
                if income_statement is not None and not income_statement.empty:                
                    df = self.__reshape_contents(income_statement)
                    for col in list(df.columns[1:]):
                        total_revenue = df.loc[df[df.columns[0]] == 'Total Revenue', col].values[0]
                        df[col + ' (%)'] = (df[col] / total_revenue) * 100            
                    df.set_index(df.columns[0], inplace=True)                    
                    return df.fillna('')
                
            if financial_statement == 'Balance Sheet':
                balance_sheet = deepcopy(self.parent.balance_sheet)
                if balance_sheet is not None and not balance_sheet.empty:                
                    df = self.__reshape_contents(balance_sheet)
                    for col in list(df.columns[1:]):
                        total_assets = df.loc[df[df.columns[0]] == 'Total Assets', col].values[0]
                        df[col + ' (%)'] = (df[col] / total_assets) * 100           
                    df.set_index(df.columns[0], inplace=True)                    
                    return df.fillna('')
                
            if financial_statement == 'Cash Flow Statement':
                cash_flow_statement = deepcopy(self.parent.cash_flow_statement)
                if cash_flow_statement is not None and not cash_flow_statement.empty:                
                    df = self.__reshape_contents(cash_flow_statement)
                    for col in list(df.columns[1:]):
                        net_income = df.loc[df[df.columns[0]] == 'Net Income', col].values[0]
                        df[col + ' (%)'] = (df[col] / net_income) * 100          
                    df.set_index(df.columns[0], inplace=True)                   
                    return df.fillna('')  



def __dir__():
    return ['fAnalyze']

__all__ = ['fAnalyze']
