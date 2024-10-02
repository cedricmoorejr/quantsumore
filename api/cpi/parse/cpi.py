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



from lxml import html
import re
import datetime
import pandas as pd

# Custom
from ....date_parser import dtparse



current_date = dtparse.nowCT(as_string=True)

class CUUR0000AA0:
    class Date:
        def __init__(self, html_content, force_end_date=None):
            self.html_content = html_content
            self.force_end_date = force_end_date or dtparse.subtract_months(current_date, 2)
            self.data = self.extract()
            self.abbreviated_months = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                "June": 6, "Jul": 7, "July": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12
            }
            self.months_pattern = '|'.join(list(self.abbreviated_months.keys()))
            self.pattern = rf'\b({self.months_pattern})\s(\d{{4}})\b'
            self.end_date = self.peel()

        def extract(self):
            if self.html_content:
                tree = html.fromstring(self.html_content)
                xpath = '//*[@id="mobile-meta-col"]'
                element = tree.xpath(xpath)
                if element:
                    return element[0].text_content()
            return None

        def peel(self):
            if self.data:
                match = re.search(self.pattern, self.data)
                if match:
                    month_abbr = match.group(1)
                    year = int(match.group(2))
                    month = self.abbreviated_months.get(month_abbr)
                    if month:
                        date = datetime.datetime(year, month, 1)
                        return date.strftime('%Y-%m-%d')
            return self.force_end_date 

        def date(self):
            """ Returns date string."""
            if self.end_date is None:
                return "CPI data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
            return self.end_date
           
        def __dir__(self):
            return ['date']


    class Data:
        def __init__(self, start_date='1913-01-01', current_date=current_date, end_date=None):
            self.start = start_date
            self.end = end_date
            self.current = current_date
            self.url = self.construct_url()
            self.period_mapping = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            self.all_items = self.construct_data()
            
        def construct_url(self):
            """
            Constructs a URL for the FRED graph API with customizable date ranges and current date.
            Uses formatted start_date, end_date, and current_date for the URL parameters.
            """
            url_template = (
                "https://fred.stlouisfed.org/graph/fredgraph.csv?"
                "bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&"
                "height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&"
                "width=1140&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&"
                "id=CPIAUCNS&scale=left&cosd={start_date}&coed={end_date}&"
                "line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&"
                "mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&"
                "fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date={current_date}&"
                "revision_date={current_date}&nd={start_date}"
            ).format(start_date=self.start, end_date=self.end, current_date=self.current)

            return url_template

        def construct_data(self):
            if self.url:
                try:
                    df = pd.read_csv(self.url)
                    df['DATE'] = pd.to_datetime(df['DATE'])
                    df['period'] = df['DATE'].dt.month.map(self.period_mapping)
                    df['year'] = df['DATE'].dt.year.astype(int)
                    df = df.drop(columns=['DATE'])
                    df = df.rename(columns={'CPIAUCNS': 'value'})
                    df['series_id'] = 'CUUR0000AA0'
                    df = df[['series_id', 'year', 'period', 'value']]
                    df.loc[:, 'year'] = df['year'].astype(int)
                    df.loc[:, 'value'] = df['value'].astype(float)
                    # Calculating the average value per year and adding it as a new row
                    average_df = df.groupby('year')['value'].mean().round(1).reset_index()
                    average_df['series_id'] = 'CUUR0000AA0'
                    average_df['period'] = 'Average'
                    # Appending the average_df to the original df
                    df = pd.concat([df, average_df], ignore_index=True)
                    df = df.reset_index(drop=True)
                    return df
                except Exception:
                    return None 
            return None

        def all_items_index(self):
            """ Returns pandas DataFrame."""
            if self.all_items is None:
                return "CPI data is currently unavailable. Please try again later. If the issue persists, report it at https://github.com/cedricmoorejr/quantsumore."
            return self.all_items
           
        def __dir__(self):
            return ['all_items_index']



def __dir__():
    return ['CUUR0000AA0']


__all__ = ['CUUR0000AA0']


