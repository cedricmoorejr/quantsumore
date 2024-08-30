import re
import pandas as pd
from html import unescape
from copy import deepcopy

# Custom
from ....tools.tool import dtparse



# Daily Treasury Bill Rates
class daily_treasury_bill:
    def __init__(self, html_content, full=False):
        self.html_content = html_content
        self.status = full       
        self.table_html = None
        self.headers = []
        self.rows = []
        self.dataframe = None      
        self.tbill_3month = None         
        self.tbill_6month = None        
        self.tbill_1year = None
        self.complete_table = None         
        self.relevant_columns = [
            "view-field-tdr-date-table-column",  # Date column
            "view-field-br-round-b1-close-4wk-2-table-column",
            "view-field-br-round-b1-yield-4wk-2-table-column",
            "view-field-br-round-b1-close-8wk-2-table-column",
            "view-field-br-round-b1-yield-8wk-2-table-column",
            "view-field-br-round-b1-close-13wk-2-table-column",
            "view-field-br-round-b1-yield-13wk-2-table-column",
            "view-field-br-round-b1-close-17wk-2-table-column",
            "view-field-br-round-b1-yield-17wk-2-table-column",
            "view-field-br-round-b1-close-26wk-2-table-column",
            "view-field-br-round-b1-yield-26wk-2-table-column",
            "view-field-br-round-b1-close-52wk-2-table-column",
            "view-field-br-round-b1-yield-52wk-2-table-column"
        ]
        
        
        if html_content:
            self.process()
            self.restructure()
            if full:
                self.full_table()
            else:
                self.assign_tbill_rates()
        
    def extract_table(self):
        # Locate the specific table
        table_start_marker = '<table class="usa-table views-table views-view-table cols-22">'
        table_end_marker = '</table>'

        # Find the table's start and end
        start_index = self.html_content.find(table_start_marker)
        if (start_index != -1):
            start_index += len(table_start_marker)
            end_index = self.html_content.find(table_end_marker, start_index)
            if (end_index != -1):
                self.table_html = self.html_content[start_index:end_index]

    def extract_headers(self):
        # Extract headers from the <thead> section
        if self.table_html:
            thead_start = self.table_html.find('<thead>')
            thead_end = self.table_html.find('</thead>', thead_start)
            if thead_start != -1 and thead_end != -1:
                thead_content = self.table_html[thead_start:thead_end]
                th_start = 0
                while True:
                    th_start = thead_content.find('<th', th_start)
                    if th_start == -1:
                        break
                    th_end = thead_content.find('</th>', th_start)
                    th_tag = thead_content[th_start:th_end]

                    # Check if the header ID or class matches the relevant columns
                    if any(col in th_tag for col in self.relevant_columns):
                        th_start = th_tag.find('>') + 1
                        header = th_tag[th_start:].strip()
                        self.headers.append(header)
                    th_start = th_end + len('</th>')

    def extract_rows(self):
        # Extract rows from the <tbody> section
        if self.table_html:
            tbody_start = self.table_html.find('<tbody>')
            tbody_end = self.table_html.find('</tbody>', tbody_start)
            if tbody_start != -1 and tbody_end != -1:
                tbody_content = self.table_html[tbody_start:tbody_end]
                tr_start = 0
                while True:
                    tr_start = tbody_content.find('<tr>', tr_start)
                    if tr_start == -1:
                        break
                    tr_start += len('<tr>')
                    tr_end = tbody_content.find('</tr>', tr_start)
                    row_html = tbody_content[tr_start:tr_end]

                    # Extract columns within each row
                    cols = []
                    td_start = 0
                    while True:
                        td_start = row_html.find('<td', td_start)
                        if td_start == -1:
                            break
                        td_end = row_html.find('</td>', td_start)
                        td_tag = row_html[td_start:td_end]

                        # Check if the cell matches the relevant columns
                        if any(col in td_tag for col in self.relevant_columns):
                            td_start = td_tag.find('>') + 1
                            col_data = td_tag[td_start:].strip()
                            cols.append(col_data)
                        elif 'view-field-tdr-date-table-column' in td_tag:  # Always include the date column
                            td_start = td_tag.find('<time datetime="') + len('<time datetime="')
                            date_end = td_tag.find('"', td_start)
                            date_str = td_tag[td_start:date_end]
                            date_parsed = self.format_date(date_str).strftime('%Y-%m-%d')
                            cols.insert(0, date_parsed)  # Date at the beginning of the row
                        td_start = td_end + len('</td>')

                    self.rows.append(cols)
                    tr_start = tr_end + len('</tr>')

    def clean_headers(self):
        # Clean the headers by removing any remaining tags and extracting only the text
        self.headers = [re.sub(r'<[^>]+>', '', header).strip() for header in self.headers]

    def clean_rows(self):
        # Clean up each row by removing HTML tags and extracting text only
        cleaned_rows = []
        for row in self.rows:
            cleaned_row = []
            for cell in row:
                if '<time' in cell:  # Extract date from <time> tag
                    cell = cell.split('>', 1)[-1].split('<')[0].strip()
                cleaned_row.append(unescape(cell.strip()))
            cleaned_rows.append(cleaned_row)
        self.rows = cleaned_rows  # Overwrite self.rows with cleaned rows
        
    def format_date(self, date_str):
        if date_str == 'N/A':
            return pd.NA
        return dtparse.parse(date_str)

    def process(self):
        self.extract_table()
        self.extract_headers()
        self.extract_rows()
        self.clean_headers()
        self.clean_rows()

    def rename_columns(self, dataframe):
        df = deepcopy(dataframe)
        df.columns = df.columns.str.title()
        new_columns = []
        weeks = '' 
        for col in df.columns:
            if 'Bank Discount' in col:
                weeks = ' '.join(col.split()[:2])
                new_columns.append(f'{weeks} Bank Discount')
            elif col == 'Coupon Equivalent':
                new_columns.append(f'{weeks} Coupon Equivalent')
            else:
                new_columns.append(col) 
        df.columns = new_columns
        return df

    def restructure(self):
        """ Converts the parsed headers and rows into a pandas DataFrame."""
        df = pd.DataFrame(self.rows, columns=self.headers)
        df = self.rename_columns(df)
        if 'Date' in df.columns:
            df['Date'] = df['Date'].apply(self.format_date)
            df = df.sort_values('Date')
            self.dataframe = df.reset_index(drop=True)

    def full_table(self):
        if self.dataframe.empty:
            return
        try:
            df = deepcopy(self.dataframe)
            cols = list(df.columns)
            df = df[["Date"] + [f for f in cols if 'Weeks Coupon' in f]]

            rename_mapping = {
                '4 Weeks Coupon Equivalent': '1-Month T-Bill',
                '8 Weeks Coupon Equivalent': '2-Month T-Bill',
                '13 Weeks Coupon Equivalent': '3-Month T-Bill',
                '17 Weeks Coupon Equivalent': '4-Month T-Bill',
                '26 Weeks Coupon Equivalent': '6-Month T-Bill',
                '52 Weeks Coupon Equivalent': '12-Month T-Bill'
            }
            df.columns = [rename_mapping.get(col, col) for col in df.columns]
            self.complete_table = df
        except:
            pass
        return 
            
    def assign_tbill_rates(self):
        if self.dataframe.empty:
            return
        try:
            df = deepcopy(self.dataframe)
            df = pd.melt(df, id_vars=['Date'], var_name='Type', value_name='Value')
            _3month_bill = '13 Weeks Coupon'
            _6month_bill = '26 Weeks Coupon'
            _1year_bill = '52 Weeks Coupon'
            bill_types = {
                'matched_rows_3month': _3month_bill,
                'matched_rows_6month': _6month_bill,
                'matched_rows_1year': _1year_bill
            }
            df_filtered = df[df['Date'] == df['Date'].max()]
            results = {}
            for var_name, name in bill_types.items():
                check_row = df_filtered[df_filtered["Type"].str.contains(name, na=False)]
                if len(check_row) == 1:
                    matched_row = check_row
                    results[var_name] = float(matched_row.iloc[0]["Value"])
            self.tbill_3month = results.get('matched_rows_3month', None)
            self.tbill_6month = results.get('matched_rows_6month', None)
            self.tbill_1year = results.get('matched_rows_1year', None)
        except:
            pass
        return   
       
    def format_rates(self, rates_dict):
        """ Converts T-bill rates from percentage to decimal form. """
        formatted_rates = {}
        for key, rate in rates_dict.items():
            if rate is None:
                formatted_rates[key] = None
                continue
            if isinstance(rate, str):
                if rate.replace('.', '', 1).isdigit():
                    rate = float(rate)
                else:
                    formatted_rates[key] = None
                    continue
            if isinstance(rate, (float, int)):
                if 0 <= rate <= 1:
                    formatted_rates[key] = round(rate, 4)
                else:
                    formatted_rates[key] = round((rate / 100.0), 4)
            else:
                formatted_rates[key] = None
        return formatted_rates       
       
    def DATA(self):
        if self.status:
            return self.complete_table            
        rates = {'3-Month T-Bill':self.tbill_3month, '6-Month T-Bill':self.tbill_6month, '1-Year T-Bill':self.tbill_1year}
        return self.format_rates(rates)
       
    def __dir__(self):
        return ['DATA'] 




# Daily Treasury Par Yield Curve Rates
class daily_treasury_yield:
    def __init__(self, html_content, full=False):
        self.html_content = html_content
        self.status = full           
        self.table_html = None
        self.headers = []
        self.rows = []
        self.dataframe = None
        self.yield_curve_rates = None
        self.complete_table = None         
        self.relevant_columns = [
            "view-field-tdr-date-table-column",
            "view-field-bc-1month-table-column",
            "view-field-bc-2month-table-column",
            "view-field-bc-3month-table-column",
            "view-field-bc-4month-table-column",
            "view-field-bc-6month-table-column",
            "view-field-bc-1year-table-column",
            "view-field-bc-2year-table-column",
            "view-field-bc-3year-table-column",
            "view-field-bc-5year-table-column",
            "view-field-bc-7year-table-column",
            "view-field-bc-10year-table-column",
            "view-field-bc-20year-table-column",
            "view-field-bc-30year-table-column"
        ]
        if html_content:
            self.process()
            self.restructure()
            if full:
                self.full_table()
            else:
                self.assign_yield_rates()

    def extract_table(self):
        # Locate the specific table
        table_start_marker = '<table class="usa-table views-table views-view-table cols-23">'
        table_end_marker = '</table>'

        # Find the table's start and end
        start_index = self.html_content.find(table_start_marker)
        if (start_index != -1):
            start_index += len(table_start_marker)
            end_index = self.html_content.find(table_end_marker, start_index)
            if (end_index != -1):
                self.table_html = self.html_content[start_index:end_index]

    def extract_headers(self):
        # Extract headers from the <thead> section
        if self.table_html:
            thead_start = self.table_html.find('<thead>')
            thead_end = self.table_html.find('</thead>', thead_start)
            if thead_start != -1 and thead_end != -1:
                thead_content = self.table_html[thead_start:thead_end]
                th_start = 0
                while True:
                    th_start = thead_content.find('<th', th_start)
                    if th_start == -1:
                        break
                    th_end = thead_content.find('</th>', th_start)
                    th_tag = thead_content[th_start:th_end]

                    # Check if the header ID or class matches the relevant columns
                    if any(col in th_tag for col in self.relevant_columns):
                        th_start = th_tag.find('>') + 1
                        header = th_tag[th_start:].strip()
                        self.headers.append(header)
                    th_start = th_end + len('</th>')

    def extract_rows(self):
        # Extract rows from the <tbody> section
        if self.table_html:
            tbody_start = self.table_html.find('<tbody>')
            tbody_end = self.table_html.find('</tbody>', tbody_start)
            if tbody_start != -1 and tbody_end != -1:
                tbody_content = self.table_html[tbody_start:tbody_end]
                tr_start = 0
                while True:
                    tr_start = tbody_content.find('<tr>', tr_start)
                    if tr_start == -1:
                        break
                    tr_start += len('<tr>')
                    tr_end = tbody_content.find('</tr>', tr_start)
                    row_html = tbody_content[tr_start:tr_end]

                    # Extract columns within each row
                    cols = []
                    td_start = 0
                    while True:
                        td_start = row_html.find('<td', td_start)
                        if td_start == -1:
                            break
                        td_end = row_html.find('</td>', td_start)
                        td_tag = row_html[td_start:td_end]

                        # Check if the cell matches the relevant columns
                        if any(col in td_tag for col in self.relevant_columns):
                            td_start = td_tag.find('>') + 1
                            col_data = td_tag[td_start:].strip()
                            cols.append(col_data)
                        elif 'view-field-tdr-date-table-column' in td_tag:  # Always include the date column
                            td_start = td_tag.find('<time datetime="') + len('<time datetime="')
                            date_end = td_tag.find('"', td_start)
                            date_str = td_tag[td_start:date_end]
                            date_parsed = self.format_date(date_str).strftime('%Y-%m-%d')
                            cols.insert(0, date_parsed)  # Date at the beginning of the row
                        td_start = td_end + len('</td>')

                    self.rows.append(cols)
                    tr_start = tr_end + len('</tr>')

    def clean_headers(self):
        # Clean the headers by removing any remaining tags and extracting only the text
        self.headers = [re.sub(r'<[^>]+>', '', header).strip() for header in self.headers]

    def clean_rows(self):
        # Clean up each row by removing HTML tags and extracting text only
        cleaned_rows = []
        for row in self.rows:
            cleaned_row = []
            for cell in row:
                if '<time' in cell:  # Extract date from <time> tag
                    cell = cell.split('>', 1)[-1].split('<')[0].strip()
                cleaned_row.append(unescape(cell.strip()))
            cleaned_rows.append(cleaned_row)
        self.rows = cleaned_rows  # Overwrite self.rows with cleaned rows
        
    def format_date(self, date_str):
        if date_str == 'N/A':
            return pd.NA
        return dtparse.parse(date_str)

    def process(self):
        self.extract_table()
        self.extract_headers()
        self.extract_rows()
        self.clean_headers()
        self.clean_rows()

    def restructure(self):
        """ Converts the parsed headers and rows into a pandas DataFrame."""
        df = pd.DataFrame(self.rows, columns=self.headers)
        if 'Date' in df.columns:
            df['Date'] = df['Date'].apply(self.format_date)
            df = df.sort_values('Date')
            self.dataframe = df.reset_index(drop=True)

    def full_table(self):
        if self.dataframe.empty:
            return
        try:
            df = deepcopy(self.dataframe)
            cols = list(df.columns)
            df = df[["Date"] + [f for f in cols if 'Yr' in f]]

            rename_mapping = {
                '1 Yr': '1-Year Treasury Note',
                '2 Yr': '2-Year Treasury Note',
                '3 Yr': '3-Year Treasury Note',
                '5 Yr': '5-Year Treasury Note',
                '7 Yr': '7-Year Treasury Note',
                '10 Yr': '10-Year Treasury Note',
                '20 Yr': '20-Year Treasury Bond',
                '30 Yr': '30-Year Treasury Bond'
            }
            df.columns = [rename_mapping.get(col, col) for col in df.columns]
            self.complete_table = df
        except:
            pass
        return 

    def assign_yield_rates(self):
        if self.dataframe.empty:
            return
        try:
            df = deepcopy(self.dataframe)
            df = df.set_index('Date')
            df = df.loc[[df.index.max()]]
            yield_curve_dict = df.iloc[0].to_dict()

            # Function to generate the new key names based on the existing key
            def generate_key_name(key):
                if "Mo" in key:
                    months = int(key.split()[0])
                    return f"{months}-Month Treasury Bill (T-Bill)"
                elif "Yr" in key:
                    term_years = int(key.split()[0])
                    if term_years <= 10:
                        return f"{term_years}-Year Treasury Note"
                    else:
                        return f"{term_years}-Year Treasury Bond"
                return None

            # Combine the keys with the new naming convention
            treasury_dict = {generate_key_name(key): value for key, value in yield_curve_dict.items() if generate_key_name(key) is not None}
            
            # Assign the matched values to the corresponding attributes
            self.yield_curve_rates = treasury_dict
        except:
            pass
        return

    def format_rates(self, rates_dict):
        """ Converts T-bill rates from percentage to decimal form. """
        formatted_rates = {}
        for key, rate in rates_dict.items():
            if rate is None:
                formatted_rates[key] = None
                continue
            if isinstance(rate, str):
                if rate.replace('.', '', 1).isdigit():
                    rate = float(rate)
                else:
                    formatted_rates[key] = None
                    continue
            if isinstance(rate, (float, int)):
                if 0 <= rate <= 1:
                    formatted_rates[key] = round(rate, 4)
                else:
                    formatted_rates[key] = round((rate / 100.0), 4)
            else:
                formatted_rates[key] = None
        return formatted_rates

    def DATA(self):
        if self.status:
            return self.complete_table    	
        return self.format_rates(self.yield_curve_rates)

    def __dir__(self):
        return ['DATA']




class treasury_yield_all:
    def __init__(self, html_content):
        self.html_content = html_content
        self.table_html = None
        self.headers = []
        self.rows = []
        self.dataframe = None
        self.relevant_columns = [
            "view-field-tdr-date-table-column",
            "view-field-bc-1month-table-column",
            "view-field-bc-2month-table-column",
            "view-field-bc-3month-table-column",
            "view-field-bc-4month-table-column",
            "view-field-bc-6month-table-column",
            "view-field-bc-1year-table-column",
            "view-field-bc-2year-table-column",
            "view-field-bc-3year-table-column",
            "view-field-bc-5year-table-column",
            "view-field-bc-7year-table-column",
            "view-field-bc-10year-table-column",
            "view-field-bc-20year-table-column",
            "view-field-bc-30year-table-column"
        ]
        if html_content:
            self.process()
            self.restructure()

    def extract_table(self):
        # Locate the specific table
        table_start_marker = '<table class="usa-table views-table views-view-table cols-23">'
        table_end_marker = '</table>'

        # Find the table's start and end
        start_index = self.html_content.find(table_start_marker)
        if (start_index != -1):
            start_index += len(table_start_marker)
            end_index = self.html_content.find(table_end_marker, start_index)
            if (end_index != -1):
                self.table_html = self.html_content[start_index:end_index]

    def extract_headers(self):
        # Extract headers from the <thead> section
        if self.table_html:
            thead_start = self.table_html.find('<thead>')
            thead_end = self.table_html.find('</thead>', thead_start)
            if thead_start != -1 and thead_end != -1:
                thead_content = self.table_html[thead_start:thead_end]
                th_start = 0
                while True:
                    th_start = thead_content.find('<th', th_start)
                    if th_start == -1:
                        break
                    th_end = thead_content.find('</th>', th_start)
                    th_tag = thead_content[th_start:th_end]

                    # Check if the header ID or class matches the relevant columns
                    if any(col in th_tag for col in self.relevant_columns):
                        th_start = th_tag.find('>') + 1
                        header = th_tag[th_start:].strip()
                        self.headers.append(header)
                    th_start = th_end + len('</th>')

    def extract_rows(self):
        # Extract rows from the <tbody> section
        if self.table_html:
            tbody_start = self.table_html.find('<tbody>')
            tbody_end = self.table_html.find('</tbody>', tbody_start)
            if tbody_start != -1 and tbody_end != -1:
                tbody_content = self.table_html[tbody_start:tbody_end]
                tr_start = 0
                while True:
                    tr_start = tbody_content.find('<tr>', tr_start)
                    if tr_start == -1:
                        break
                    tr_start += len('<tr>')
                    tr_end = tbody_content.find('</tr>', tr_start)
                    row_html = tbody_content[tr_start:tr_end]

                    # Extract columns within each row
                    cols = []
                    td_start = 0
                    while True:
                        td_start = row_html.find('<td', td_start)
                        if td_start == -1:
                            break
                        td_end = row_html.find('</td>', td_start)
                        td_tag = row_html[td_start:td_end]

                        # Check if the cell matches the relevant columns
                        if any(col in td_tag for col in self.relevant_columns):
                            td_start = td_tag.find('>') + 1
                            col_data = td_tag[td_start:].strip()
                            cols.append(col_data)
                        elif 'view-field-tdr-date-table-column' in td_tag:  # Always include the date column
                            td_start = td_tag.find('<time datetime="') + len('<time datetime="')
                            date_end = td_tag.find('"', td_start)
                            date_str = td_tag[td_start:date_end]
                            date_parsed = self.format_date(date_str).strftime('%Y-%m-%d')
                            cols.insert(0, date_parsed)  # Date at the beginning of the row
                        td_start = td_end + len('</td>')

                    self.rows.append(cols)
                    tr_start = tr_end + len('</tr>')

    def clean_headers(self):
        # Clean the headers by removing any remaining tags and extracting only the text
        self.headers = [re.sub(r'<[^>]+>', '', header).strip() for header in self.headers]

    def clean_rows(self):
        # Clean up each row by removing HTML tags and extracting text only
        cleaned_rows = []
        for row in self.rows:
            cleaned_row = []
            for cell in row:
                if '<time' in cell:  # Extract date from <time> tag
                    cell = cell.split('>', 1)[-1].split('<')[0].strip()
                cleaned_row.append(unescape(cell.strip()))
            cleaned_rows.append(cleaned_row)
        self.rows = cleaned_rows  # Overwrite self.rows with cleaned rows
        
    def format_date(self, date_str):
        if date_str == 'N/A':
            return pd.NA
        return dtparse.parse(date_str)

    def process(self):
        self.extract_table()
        self.extract_headers()
        self.extract_rows()
        self.clean_headers()
        self.clean_rows()

    def restructure(self):
        """ Converts the parsed headers and rows into a pandas DataFrame."""
        df = pd.DataFrame(self.rows, columns=self.headers)
        if 'Date' in df.columns:
            df['Date'] = df['Date'].apply(self.format_date)
            df = df.sort_values('Date')
            df.iloc[:, 1:] = df.iloc[:, 1:].astype(float).round(2)
            df = df.reset_index(drop=True)
            self.dataframe = df

    def DATA(self):
        return self.dataframe

    def __dir__(self):
        return ['DATA']



def __dir__():
    return ['daily_treasury_bill', 'daily_treasury_yield', 'treasury_yield_all']


__all__ = ['daily_treasury_bill', 'daily_treasury_yield', 'treasury_yield_all']



