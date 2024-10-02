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



import datetime
import re
import pandas as pd
import numpy as np

class dt_parse:
    def __init__(self):
        self.date_formats = [
            '%Y.%m.%d', 
            '%m.%d.%Y', 
            '%B %d, %Y', 
            '%b %d, %Y', 
            '%d.%m.%Y', 
            '%d %b %Y', 
            '%d %B %Y',
            '%b %d %Y',
            '%Y%m%d',
            '%d%m%Y',
            '%A, %B %d %Y',
            '%Y-%m-%dT%H:%M:%SZ',
            '%a, %d %b %Y %H: %M:%S',
        ]
        self.formats_with_dots = [fmt for fmt in self.date_formats if '.' in fmt]
        self.formats_without_dots = [fmt for fmt in self.date_formats if '.' not in fmt]
        self.last_successful_format = None
        self.date_format_string_pattern = re.compile(r"%[aAbBcdHImMpSUwWxXyYZ]")

    def is_date_format_string(self, text):
        if not isinstance(text, str):
            return False
        return bool(self.date_format_string_pattern.search(text))

    def is_datetimeType(self, obj, format='%Y-%m-%d', strf=False):
        """ Check the type of the given object related to date and time, without assuming the import name of the datetime module."""
        datetime_class_name = 'datetime'
        date_class_name = 'date'

        # Check if the object is a datetime object
        if obj.__class__.__name__ == datetime_class_name and hasattr(obj, 'hour'):
            if strf:
                return obj.strftime(format)
            else:
                return True
                
        # Check if the object is a date object
        elif obj.__class__.__name__ == date_class_name and not hasattr(obj, 'hour'):
            if strf:
                return obj.strftime(format)            
            else:
                return True
        else:
            return False

    def parse(self, date_input, from_format=None, to_format=None, to_unix_timestamp=False):
        """ Parses and converts dates from various formats.
            Handles single string inputs, lists, numpy arrays, and pandas Series.
            The to_unix_timestamp argument converts the parsed date to an integer timestamp.
        """
        if self.is_datetimeType(date_input):
            if to_unix_timestamp:
                return int(date_input.timestamp())
            if to_format and self.is_date_format_string(to_format):
                return date_input.strftime(to_format)
            return date_input        
        
        def process(date_string):
            date_str = re.sub(r'\s+', ' ', date_string).strip()
            
            # Try the last successful format first
            if self.last_successful_format:
                try:
                    parsed_date = datetime.datetime.strptime(date_str, self.last_successful_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    if not from_format and self.is_date_format_string(to_format):
                        return parsed_date.strftime(to_format)
                    return parsed_date
                except ValueError:
                    pass  # If it fails, proceed with other formats

            # Try parsing with formats containing and not containing dots
            for format_list in [self.formats_with_dots, self.formats_without_dots]:
                for date_format in format_list:
                    try:
                        parsed_date = datetime.datetime.strptime(date_str, date_format)
                        self.last_successful_format = date_format
                        if to_unix_timestamp:
                            return int(parsed_date.timestamp())
                        if not from_format and self.is_date_format_string(to_format):
                            return parsed_date.strftime(to_format)
                        return parsed_date
                    except ValueError:
                        continue

            # Try parsing with different separators
            new_separators = ['/', '-']
            for sep in new_separators:
                for date_format in self.formats_with_dots:
                    new_format = date_format.replace('.', sep)
                    try:
                        parsed_date = datetime.datetime.strptime(date_str, new_format)
                        self.last_successful_format = new_format
                        if to_unix_timestamp:
                            return int(parsed_date.timestamp())
                        if not from_format and self.is_date_format_string(to_format):
                            return parsed_date.strftime(to_format)
                        return parsed_date
                    except ValueError:
                        continue

            # Fall back to using from_format and to_format if provided
            if from_format and to_format:
                try:
                    parsed_date = datetime.datetime.strptime(date_str, from_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    formatted_date = parsed_date.strftime(to_format)
                    return formatted_date
                except ValueError:
                    raise ValueError("Date format not recognized and fallback failed. Please check your formats.")
            elif from_format:
                try:
                    parsed_date = datetime.datetime.strptime(date_str, from_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    return parsed_date
                except ValueError:
                    raise ValueError("Date format not recognized. Please check your from_format.")
            raise ValueError("Date format not recognized. Please use a supported date format.")

        if isinstance(date_input, str):
            return process(date_input)
        elif isinstance(date_input, list) or isinstance(date_input, np.ndarray):
            return [process(date_str) for date_str in date_input]
        elif isinstance(date_input, pd.Series):
            date_input = date_input.astype(str)
            return date_input.apply(process)
        else:
            raise ValueError("Unsupported data type. The input must be a str, list, numpy.ndarray, or pandas.Series.")

    def _is_dst(self, dt=None, timezone="US/Central"):
        """ Determine whether Daylight Saving Time (DST) is in effect for a given datetime and timezone."""
        if dt is None:
            dt = datetime.datetime.utcnow()
        dst_start = datetime.datetime(dt.year, 3, 8)
        dst_end = datetime.datetime(dt.year, 11, 1) 
        while dst_start.weekday() != 6: 
            dst_start += datetime.timedelta(days=1)
        while dst_end.weekday() != 6:
            dst_end += datetime.timedelta(days=1)
        dst_start = dst_start.replace(hour=2)
        dst_end = dst_end.replace(hour=2)
        return dst_start <= dt < dst_end
    
    def subtract_months(self, date_str, months):
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        new_month = date.month - months
        new_year = date.year
        while new_month <= 0:
            new_month += 12
            new_year -= 1        
        new_day = min(date.day, (datetime.datetime(new_year, new_month + 1, 1) - datetime.datetime(new_year, new_month, 1)).days)
        new_date = datetime.datetime(new_year, new_month, new_day)        
        return new_date.strftime('%Y-%m-01')
    
    def now(self, utc=False, as_unix=False, as_string=False, format=None):
        """ Returns current datetime, optionally in UTC, as a Unix timestamp, or as a string. """
        current_time = datetime.datetime.utcnow() if utc else datetime.datetime.now()
        if as_unix:
            return self.unix_timestamp(current_time)        
        if as_string:
            if format:
                return current_time.strftime(format)
            return current_time.strftime("%Y-%m-%d")
        return current_time
    
    def nowCT(self, as_unix=False, as_string=False):
        now_utc = datetime.datetime.utcnow()
        current_utc_time = now_utc + datetime.timedelta(hours=5)
        if self._is_dst(current_utc_time):
            central_time = current_utc_time - datetime.timedelta(hours=1)
        else:
            central_time = current_utc_time - datetime.timedelta(hours=2)
        if as_string:
            return central_time.date().strftime('%Y-%m-%d')        
        return central_time

    def unix_timestamp(self, datetime_obj, utc=True, reset_time=False):
        """Generate a UTC timestamp for a given datetime, optionally adjusting to UTC and resetting time to 00:00."""
        if utc:
            utc_datetime = datetime_obj.replace(tzinfo=datetime.timezone.utc)
            if reset_time:
                utc_datetime = utc_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            return int(utc_datetime.timestamp())
        else:
            if reset_time:
                datetime_obj = datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            return int(datetime_obj.timestamp())

    def __dir__(self):
        return ['parse', 'now', 'unix_timestamp', 'nowCT', 'subtract_months', 'is_datetimeType']


dtparse = dt_parse()



def __dir__():
    return ['dtparse']

__all__ = ['dtparse']


























