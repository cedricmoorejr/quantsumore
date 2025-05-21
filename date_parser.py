# -*- coding: utf-8 -*-
#
## ╭────────────────────────────────────────────────────────────────────────────────────────────╮
## │  Library         : doydl's Finance API Client — quantsumore                                 │
## │                                                                                             │
## │                                                                                             │
## │  Description     : `quantsumore` is a comprehensive Python library designed to streamline   │
## │                    the process of accessing and analyzing real-time financial data across   │
## │                    various markets. It provides specialized API clients to fetch data       │
## │                    from multiple financial instruments, including:                          │
## │                      - Cryptocurrencies                                                     │
## │                      - Equities and Stock Markets                                           │
## │                      - Foreign Exchange (Forex)                                             │
## │                      - Treasury Instruments                                                 │
## │                      - Consumer Price Index (CPI) Metrics                                   │
## │                                                                                             │
## │                    The library offers a unified interface for retrieving diverse financial  │
## │                    data, enabling users to perform in-depth financial and technical         │
## │                    analysis. Whether you're developing trading algorithms, conducting       │
## │                    market research, or building financial dashboards, `quantsumore` serves  │
## │                    as a reliable and efficient tool in your data pipeline.                  │
## │                                                                                             │
## │                                                                                             │
## │  Key Features    : - Real-time data retrieval from multiple financial markets               │
## │                    - Support for various financial instruments and metrics                  │
## │                    - Simplified API clients for ease of integration                         │
## │                    - Designed for both personal and non-commercial use                      │
## │                                                                                             │
## │                                                                                             │
## │  Legal Disclaimer: `quantsumore` is an independent Python library and is not affiliated     │
## │                    with any financial institutions or data providers. Likewise, doydl       │
## │                    technologies is not affiliated with, endorsed by, or sponsored by any    │
## │                    government, corporate, or financial institutions. Users should verify    │
## │                    the accuracy of the data obtained and consult professional advice        │
## │                    before making investment decisions.                                      │
## │                                                                                             │
## │                                                                                             │
## │  Copyright       : © 2023–2025 by doydl technologies. All rights reserved.                  │
## │                                                                                             │
## │                                                                                             │
## │  License         : Licensed under the Apache License, Version 2.0 (the "License");          │
## │                    you may not use this file except in compliance with the License.         │
## │                    You may obtain a copy of the License at:                                 │
## │                                                                                             │
## │                        http://www.apache.org/licenses/LICENSE-2.0                           │
## │                                                                                             │
## │                    Unless required by applicable law or agreed to in writing, software      │
## │                    distributed under the License is distributed on an "AS IS" BASIS,        │
## │                    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or          │
## │                    implied. See the License for the specific language governing             │
## │                    permissions and limitations under the License.                           │
## ╰────────────────────────────────────────────────────────────────────────────────────────────╯
#


from datetime import datetime as dt, timedelta as td, date as d, timezone as tmz
import re
import time

#────────── Third-party library imports (from PyPI or other package sources) ─────────────────────────────────
import pandas as pd
import numpy as np


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.
class dt_parse:
    # Canonical copy of the “factory-fresh” formats.
    DEFAULT_DATE_FORMATS = [
        '%Y.%m.%d', '%m.%d.%Y', '%B %d, %Y', '%b %d, %Y',
        '%d.%m.%Y', '%d %b %Y', '%d %B %Y', '%b %d %Y',
        '%Y%m%d',  '%d%m%Y',  '%A, %B %d %Y', '%Y-%m-%dT%H:%M:%SZ',
        '%a, %d %b %Y %H: %M:%S', '%Y-%m', '%Y-%m-%d %H:%M',
        '%Y-%m-%d %I:%M %p', '%Y-%m-%d %H:%M:%S', '%a, %d %b %Y',
    ]

    def __init__(self):
        # make a *copy* so DEFAULT_DATE_FORMATS itself is never mutated
        self.date_formats = list(self.DEFAULT_DATE_FORMATS)
        self._refresh_format_lists()
        self.iso_format = re.compile(
            r'^\d{4}-\d{2}-\d{2}'             # Date: YYYY-MM-DD
            r'T'                              # Separator: T
            r'\d{2}:\d{2}:\d{2}'              # Time: hh:mm:ss
            r'(?:\.\d+)?'                     # Optional fractional seconds: .digits
            # r'(?:Z|[+-]\d{2}:\d{2})?$'      # Time zone: Z or ±hh:mm
            r'Z$'                             # Time zone: Z only
        )  
        
        self.formats_with_dots = [fmt for fmt in self.date_formats if '.' in fmt]
        self.formats_without_dots = [fmt for fmt in self.date_formats if '.' not in fmt]
        self.last_successful_format = None
    
        # ──────────────────────────────────────── INNER CLASSES ────────────────────────────────────────
        self.ET = self.EasternTime(self)         
        self.sub = self.SubstituteClass(self)           
        
    # _DIR_LETTERS = set(
    #     "aAbBpPzZxXwWdDmMyYHIfSjUWCcGguV"  # all single-letter directives
    # )
    #
    # @staticmethod    
    # def _normalize_format(fmt: str) -> str:
    #     """
    #     Add a leading '%' in front of every lone strftime directive letter
    #     that *isn't* already prefixed.
    # 
    #     Examples
    #     --------
    #     >>> dt_parse._normalize_format('d-b-Y')
    #     '%d-%b-%Y'
    #     >>> dt_parse._normalize_format('%Y/%m/%d')   # already good
    #     '%Y/%m/%d'
    #     """
    #     if '%' in fmt:          # assume caller already wrote a valid pattern
    #         return fmt
    # 
    #     out = []
    #     for ch in fmt:
    #         if ch.isalpha() and ch in dt_parse._DIR_LETTERS:
    #             out.append('%' + ch)
    #         else:
    #             out.append(ch)
    #     return ''.join(out)
    #           
    #
    #
    # _MISSING_PERCENT = re.compile(
    #     rf'(?<!%)'                 # not already prefixed by %
    #     rf'([{_FLAG_CHARS}]?)'     # optional flag   (-  _  0)
    #     rf'([{_DIRECTIVE_CHARS}])' # the directive letter itself
    # )
    #
    # @staticmethod    
    # def _normalize_format(fmt: str) -> str:
    #     """
    #     Insert a leading '%' in front of any directive (optionally carrying a
    #     flag) that is missing it.
    # 
    #     Examples
    #     --------
    #     'd-b-Y'   → '%d-%b-%Y'
    #     '-d-b-Y'  → '%-d-%b-%Y'
    #     '_H:M:S'  → '%_H:%M:%S'
    #     'Y/%m/%d' → '%Y/%m/%d'
    #     A string that is *already* fully prefixed is left untouched.
    #     """
    #     return dt_parse._MISSING_PERCENT.sub(lambda m: '%' + m.group(1) + m.group(2), fmt)
    _DIRECTIVE_CHARS = 'aAbBpPzZxXwWdDmMyYHIfSjUWCcGguV'   # ← single-letter directives
    _FLAG_CHARS      = '-_0'                               # ← padding flags we’ll honour
    _MISSING_PERCENT = re.compile(
        rf'''(?<!%)                 # not already a directive
            (?P<flag>(?<![A-Za-z])  # flag allowed only if the char in front
            [{_FLAG_CHARS}])?       #   isn’t a letter (so dash in “Y-m-d” is safe)
            (?P<dir>[{_DIRECTIVE_CHARS}])
        ''',
        re.VERBOSE
    )    
    
    @staticmethod    
    def _normalize_format(fmt: str) -> str:
        """
        Add a leading '%' in front of every directive letter (with an optional
        padding flag) that doesn’t already have one.
        """
        # If the user has already typed any ‘%’, treat the pattern as complete.
        if '%' in fmt:
            return fmt

        # Otherwise patch it up on the fly.
        return dt_parse._MISSING_PERCENT.sub(
            lambda m: '%' + (m.group('flag') or '') + m.group('dir'),
            fmt
        )

    def _refresh_format_lists(self):
        """Re-derive the convenience sub-lists every time date_formats changes."""
        self.formats_with_dots    = [f for f in self.date_formats if '.' in f]
        self.formats_without_dots = [f for f in self.date_formats if '.' not in f]
        
    def _is_date_str(self, text):
        """
        Determine if the given text contains any date/time formatting directives.

        This method checks whether the input string includes any of the date/time format
        directives (e.g., %a, %b, %d, %H, etc.) typically used with Python's strftime or strptime.
        If the input is not a string, it immediately returns False.

        Parameters:
            text (str): The string to check for date/time format directives.

        Returns:
            bool: True if the string contains at least one date/time directive, otherwise False.
        """   	
        date_format_string_pattern = re.compile(r"%[aAbBcdHImMpSUwWxXyYZ]")
        if not isinstance(text, str):
            return False
        return bool(date_format_string_pattern.search(text))

    def _is_datetimeType(self, obj, format='%Y-%m-%d', strf=False):
        """
        Dynamically check if the object is date-like or datetime-like based on its attributes.

        This method determines whether the given object contains the attributes of a date or datetime.
        If the optional parameter `strf` is True, the object is formatted as a string using the provided
        format.

        Parameters:
            obj: The object to check.
            format (str): The format string to use if `strf` is True.
            strf (bool): If True, return the formatted date string; otherwise, return a boolean indicating
                         if the object is date-like or datetime-like.

        Returns:
            bool or str: If `strf` is True and the object is date-like or datetime-like, returns the formatted string.
                         Otherwise, returns True if the object is date-like or datetime-like; else False.
        """
        date_attrs = {'year', 'month', 'day'}
        datetime_attrs = date_attrs.union({'hour', 'minute', 'second', 'microsecond'})

        # Check if all datetime attributes are present
        if all(hasattr(obj, attr) for attr in datetime_attrs):
            if strf:
                return obj.strftime(format)
            return True
        # Check if only date attributes are present (and not the extra datetime attributes)
        elif all(hasattr(obj, attr) for attr in date_attrs) and not any(hasattr(obj, attr) for attr in datetime_attrs - date_attrs):
            if strf:
                return obj.strftime(format)
            return True
        return False

    def _from_pywintypes_datetime(self, obj):
        """
        Convert a pywintypes.datetime object to a standard Python datetime.datetime object.

        This method checks whether the input object is from the 'pywintypes' module with class name 'datetime'
        or if it has datetime-like attributes. If so, it converts the object into a standard datetime.datetime object.
        If conversion is not applicable, the original object is returned.

        Parameters:
            obj: The object to convert.

        Returns:
            datetime.datetime or original object: A standard datetime.datetime object if conversion succeeds;
            otherwise, the original object.
        """
        # Check if it's from the 'pywintypes' module and class name is 'datetime' or has required attributes
        if ((type(obj).__module__ == "pywintypes" and type(obj).__name__ == "datetime") or
            (hasattr(obj, "year") and hasattr(obj, "microsecond") and (hasattr(obj, "tzinfo") or hasattr(obj, "day")))):
            # Ensure tzinfo is provided if it exists; otherwise, set to None.
            tzinfo = getattr(obj, 'tzinfo', None)
            return dt(
                obj.year,
                obj.month,
                obj.day,
                obj.hour,
                obj.minute,
                obj.second,
                obj.microsecond,
                tzinfo=tzinfo
            )
        return obj

    def _is_iso(self, text):
        """
        Check if the given text is in ISO 8601 format (UTC only).

        Parameters:
            text (str): The string to check.

        Returns:
            bool: True if the text matches the ISO 8601 format with a 'Z' timezone indicator; otherwise, False.
        """
        if not isinstance(text, str):
            return False

        return bool(re.compile(
            r'^'                  # Start of string
            r'\d{4}-\d{2}-\d{2}'  # Date: YYYY-MM-DD
            r'T'                  # Separator: T
            r'\d{2}:\d{2}:\d{2}'  # Time: hh:mm:ss
            r'(?:\.\d+)?'         # Optional fractional seconds: .digits
            r'Z$'                 # Time zone: Z only
        ).search(text))

    def _add_missing_seconds(self, date_str):
        """
        Given a string that may include a date and a time portion, ensure that the time portion
        is in the format HH:MM:SS (adding ":00" if seconds are missing), but only if any text preceding
        the time is actually a date. If the prefix (the text before the time) cannot be parsed as a date,
        the function leaves the string unchanged.

        Steps:
          1. Collapse extra whitespace.
          2. Use a regex to capture two groups:
             - 'prefix': Everything before the time portion.
             - 'time': The time portion in one of the supported formats (HH:MM, HH:MM:SS, or HH:MM:SS.microseconds).
          3. If a prefix is present, try to parse it with dateplumb.pro_parse. If parsing fails,
             assume it isn’t a date and return the original string.
          4. If parsing succeeds (i.e. the prefix is a date), check the time groups.
          5. If seconds are missing, default them to "00".
          6. Reconstruct the string with the (possibly normalized) date prefix and new time.

        Parameters:
            date_str (str): A string that may contain a date and time (e.g., "2024-01-01 12:34" or "2024/01/01 12:34:56.789").

        Returns:
            str: The modified datetime string with seconds ensured, or the original string if the date portion is invalid.
        """
        # 1. Normalize whitespace.
        cleaned = " ".join(date_str.split())
        
        # 2. Regex pattern to capture:
        #    - 'prefix': any text before the time portion (non-greedily),
        #    - 'time': the time portion.
        pattern = r'^(?P<prefix>.*?)\s*(?P<time>(?P<hours>\d{1,2}):(?P<minutes>\d{2})(?::(?P<seconds>\d{2})(?:\.(?P<microseconds>\d+))?)?)\s*$'
        time_regex = re.compile(pattern)
        match = time_regex.search(cleaned)
        
        if not match:
            # No time portion found; return the original string.
            return date_str

        prefix = match.group("prefix")
        
        # Validate the prefix *once* with parse(), but tell parse()
        # to skip its own second-padding step:
        if prefix:
            try:
                parsed_date = self.parse(prefix, _skip_missing=True)
            except Exception:
                # If parsing fails, the prefix isn't a date, so we return the original string.
                return date_str
            # If parsed_date isn't a datetime, treat it as invalid.
            if not isinstance(parsed_date, dt):
                return date_str

        # 4. Extract time components.
        hours = match.group("hours")
        minutes = match.group("minutes")
        seconds = match.group("seconds")
        microseconds = match.group("microseconds")

        # 5. If seconds are missing, default them to "00".
        if seconds is None:
            seconds = "00"

        # 6. Construct the new time string.
        new_time_str = f"{hours}:{minutes}:{seconds}"
        if microseconds:
            new_time_str += f".{microseconds}"

        # 7. Reconstruct the full string.
        if prefix:
            new_str = prefix.strip() + " " + new_time_str
        else:
            new_str = new_time_str

        return new_str
        
    # ──────────────────────────────────────── PUBLIC HELPERS ────────────────────────────────────────
    def add(self, *formats):
        # """
        # Add one or more strftime/strptime format strings at runtime.
        # """
        # new_items = [f for f in formats if f not in self.date_formats]
        # if new_items:
        #     self.date_formats.extend(new_items)
        #     self._refresh_format_lists()   # keep the derivative lists in sync
        """
        Accept one or more new format strings.  If any directive letters are
        missing their leading '%', they will be fixed automatically.

        >>> dtparse.add_date_formats('d-b-Y', 'Y/m/d')  # ⇒ '%d-%b-%Y', '%Y/%m/%d'
        """
        for raw in formats:
            fmt = self._normalize_format(raw)
            if fmt not in self.date_formats:
                self.date_formats.append(fmt)
        self._refresh_format_lists()        

    def flush(self, successful_reset=False):
        """
        Restore the parser to its original list of formats, discarding any extras
        added with `add()`.
        """
        self.date_formats = list(self.DEFAULT_DATE_FORMATS)
        self._refresh_format_lists()
        if successful_reset:
            self.last_successful_format = None     
        
    # ──────────────────────────────────────── MAIN PARSER ────────────────────────────────────────
    def parse(self, date_input, *, from_format=None, to_format=None,
              to_unix_timestamp=False, include_timezone=False,
              timezone_offset='+00:00', keep_time=True,
              _skip_missing=False):          # <- internal flag
        """
        Parse and convert dates from various formats.

        This method handles date parsing for multiple input types (e.g., string, list, numpy.ndarray, pandas.Series)
        and supports conversion to Unix timestamps, formatting, and ISO 8601 parsing.

        Parameters:
            date_input: A date input (string, datetime, list, numpy.ndarray, or pandas.Series).
            from_format (str, optional): Format string for parsing the input date.
            to_format (str, optional): Format string for output formatting.
            to_unix_timestamp (bool, optional): If True, returns an integer Unix timestamp.
            include_timezone (bool, optional): If True, includes a timezone offset for ISO dates.
            timezone_offset (str, optional): Timezone offset to use for ISO dates (default is '+00:00').
            keep_time (bool, optional): If False, returns only the date portion; otherwise, returns the full datetime.

        Returns:
            datetime.datetime, int, str, or collection: The parsed date in the specified format or as a Unix timestamp.

        Raises:
            ValueError: If the date format is not recognized.
        """
        def _parser(date_string):
            date_str = " ".join(date_string.split())

            # 1. Try last successful format first (if it exists)            
            if self.last_successful_format:
                try:
                    parsed_date = dt.strptime(date_str, self.last_successful_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    if not from_format and self._is_date_str(to_format):
                        return parsed_date.strftime(to_format)
                    return parsed_date
                except ValueError:
                    pass

            # 2. Try all known formats                   
            for format_list in [self.formats_with_dots, self.formats_without_dots]:
                for date_format in format_list:
                    try:
                        parsed_date = dt.strptime(date_str, date_format)
                        self.last_successful_format = date_format
                        if to_unix_timestamp:
                            return int(parsed_date.timestamp())
                        if not from_format and self._is_date_str(to_format):
                            return parsed_date.strftime(to_format)
                        return parsed_date
                    except ValueError:
                        continue

            # 3. Try alternate separators ('.' → '/' or '-') if needed                    
            new_separators = ['/', '-']            
            for sep in new_separators:
                for date_format in self.formats_with_dots:
                    new_format = date_format.replace('.', sep)
                    try:
                        parsed_date = dt.strptime(date_str, new_format)
                        self.last_successful_format = new_format
                        if to_unix_timestamp:
                            return int(parsed_date.timestamp())
                        if not from_format and self._is_date_str(to_format):
                            return parsed_date.strftime(to_format)
                        return parsed_date
                    except ValueError:
                        continue

            # 4. Try explicit format if provided                    
            if from_format and to_format:
                try:
                    parsed_date = dt.strptime(date_str, from_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    formatted_date = parsed_date.strftime(to_format)
                    return formatted_date
                except ValueError:
                    raise ValueError("Date format not recognized and fallback failed.")
                
            elif from_format:
                try:
                    parsed_date = dt.strptime(date_str, from_format)
                    if to_unix_timestamp:
                        return int(parsed_date.timestamp())
                    return parsed_date
                except ValueError:
                    raise ValueError("Date format not recognized.")
            raise ValueError("Date format not recognized.")
        
        # 1. Handle Win32 objects (e.g., pywintypes.datetime)
        date_input = self._from_pywintypes_datetime(date_input)     
        
        # 2. Pad missing seconds (only if not skipped and input is str)
        if (not _skip_missing
                and isinstance(date_input, str)
                and not self._is_datetimeType(date_input)):
            date_input = self._add_missing_seconds(date_input)

        # 3. If already a datetime object, return early        
        if self._is_datetimeType(date_input):
            if to_unix_timestamp:
                return int(date_input.timestamp())
            if to_format and self._is_date_str(to_format):
                return date_input.strftime(to_format)
            return date_input        

        # 4. If ISO-8601 (UTC-Z), parse with optional timezone inclusion        
        if self._is_iso(date_input):
            if include_timezone:
                date_input = date_input.replace('Z', timezone_offset)
            else:
                date_input = date_input.replace('Z', '')
            formatted_date = dt.fromisoformat(date_input)
            if to_format:
                return formatted_date.strftime(to_format)
            return formatted_date if keep_time else formatted_date.date()        

        # 5. General parsing for str, list, np.ndarray, or pd.Series                
        try:
            if isinstance(date_input, str):
                return _parser(date_input)
            elif isinstance(date_input, list) or isinstance(date_input, np.ndarray):
                return [_parser(date_str) for date_str in date_input]
            elif isinstance(date_input, pd.Series):
                date_input = date_input.astype(str)
                return date_input.apply(_parser)
        # except ValueError as e:
        #     logging.error(f"Cannot parse due to error: {e}")
        #     return
        except ValueError as e:
            if not _skip_missing:          # Only a real failure
                raise ValueError(f"Cannot parse due to error: {e}")
            return        

    ##────────── Eastern Timezone Inner Class ───────────────────────────────────────────────────────────────────────────────────────────────────────────   
    class EasternTime:
        def __init__(self, parent):
            self.parent = parent
            
        def isDST(self, date_value=None):
            """
            Determine if a given date is in Daylight Saving Time (DST) for Eastern Time.

            Parameters:
                date_value (dt, optional): The date to check. If None, the current UTC time is used.

            Returns:
                bool: True if the date is within the DST period for Eastern Time; otherwise, False.
            """        	
            date_value = date_value if date_value else dt.utcnow()
            dst_start = dt(date_value.year, 3, 8)
            dst_end = dt(date_value.year, 11, 1) 
            while dst_start.weekday() != 6: 
                dst_start += td(days=1)
            while dst_end.weekday() != 6:
                dst_end += td(days=1)
            dst_start = dst_start.replace(hour=2)
            dst_end = dst_end.replace(hour=2)
            return dst_start <= date_value < dst_end 

        def now(self):
            """
            Get the current Eastern Time, accounting for Daylight Saving Time.

            Returns:
                dt: The current time in Eastern Time (EDT or EST, as appropriate).
            """        	
            now_utc = dt.utcnow()
            year = now_utc.year
            dst_start = dt(year, 3, 8, 2) + td(days=(6 - dt(year, 3, 8, 2).weekday()))
            dst_end = dt(year, 11, 1, 2) + td(days=(6 - dt(year, 11, 1, 2).weekday()))
            if dst_start <= now_utc.replace(tzinfo=None) < dst_end:
                offset = td(hours=-4) # Eastern Daylight Time (UTC-4)
            else:
                offset = td(hours=-5) # Eastern Standard Time (UTC-5)
            now_est_edt = now_utc + offset
            return now_est_edt

        def nowOffset(self, datetime_datetime_obj=None):
            """
            Get the UTC offset in hours for Eastern Time.

            Parameters:
                datetime_datetime_obj (dt, optional): A datetime object with timezone info.
                    If provided, its UTC offset is used; otherwise, the current time is evaluated.

            Returns:
                float: The UTC offset in hours (-4 for EDT or -5 for EST).
            """        	
            def has_timezone(dte):
                if isinstance(dte, dt):
                    return isinstance(dt.tzinfo, tmz)
                else:
                    return None
            if datetime_datetime_obj:
                if has_timezone(datetime_datetime_obj):
                    offset = datetime_datetime_obj.utcoffset()
                    offset_seconds = offset.total_seconds()
                    return offset_seconds/3600
            now_utc = dt.utcnow()
            year = now_utc.year
            dst_start = dt(year, 3, 8, 2) + td(days=(6 - dt(year, 3, 8, 2).weekday()))
            dst_end = dt(year, 11, 1, 2) + td(days=(6 - dt(year, 11, 1, 2).weekday()))
            if dst_start <= now_utc.replace(tzinfo=None) < dst_end:
                return -4 # Eastern Daylight Time (UTC-4)
            else:
                return -5 # Eastern Standard Time (UTC-5)
            return 0
    
        def __dir__(self):
            return ['isDST', 'now', 'nowOffset'] 
    
    
    ##────────── Substitute Inner Class ───────────────────────────────────────────────────────────────────────────────────────────────────────────       
    class SubstituteClass:
        def __init__(self, parent):        
            """
            A helper class providing functionalities to substitute date and time components
            in datetime strings.

            Attributes:
                time: An instance of TimeClass for modifying time components.
                date: An instance of DateClass for modifying date components.
            """        	
            self.parent = parent                    
            self.time = self.TimeClass(self.parent).time                                  
        
        class TimeClass:
            def __init__(self, parent):
                self.parent = parent
        	
            def time(self, date_str, hours=None, minutes=None, seconds=None, microseconds=None):
                """
                1) Splits 'date_str' into (potential) 'prefix' (date-like substring) + 'time' (HH:MM, HH:MM:SS, or HH:MM:SS.microseconds).
                2) Uses 'dateplumb.pro_parse' to validate if the prefix or entire string is a parsable date.
                   - If no time portion is found, tries parsing the entire string as a date.
                3) If valid, reconstructs time components (hours, minutes, optional seconds, optional microseconds).
                   - If no original time was present, default missing components to "00", or build from user overrides.
                4) Returns the string with updated (or newly added) time if match+parse is successful; otherwise, returns 'date_str'.

                :param date_str: The original string containing a date-like prefix and optionally a time substring.
                :param hours: (str or int) Override hours, or None to use the matched hours (or "00" if no match).
                :param minutes: (str or int) Override minutes, or None to use the matched minutes (or "00" if no match).
                :param seconds: (str or int) Override seconds, or None to use the matched seconds (or none if no match).
                :param microseconds: (str or int) Override microseconds, or None to use the matched microseconds.
                :return: A modified string with updated or newly added time components if possible,
                         otherwise 'date_str' unchanged.
                """

                # Regex to capture:
                #  - group "prefix" (the part before the time),
                #  - group "time" (the entire time portion),
                #     - sub-group "hours", "minutes", optional "seconds", optional "microseconds".
                pattern = (
                    r'^(?P<prefix>.*?)\s*'                # capture anything (non-greedy) until whitespace
                    r'(?P<time>'                          # capture the time portion
                    r'(?P<hours>\d{1,2}):(?P<minutes>\d{2})'
                    r'(?:'
                    r':(?P<seconds>\d{2})'
                    r'(?:\.(?P<microseconds>\d+))?'
                    r')?'
                    r')\s*$'
                )
                time_regex = re.compile(pattern)

                # 1) Collapse extra whitespace in the input string.
                cleaned_date_str = " ".join(date_str.split())

                # 2) Search for the first occurrence of the time pattern.
                match = time_regex.search(cleaned_date_str)
                
                if match:
                    # ------------------------------------------
                    # CASE A: Found a time substring
                    # ------------------------------------------
                    prefix = match.group("prefix")
                    # Attempt to parse the prefix as a date using dateplumb
                    try:
                        parsed_date = self.parent.parse(prefix)
                    except Exception:
                        # If parsing fails, the prefix isn't a valid date, return original
                        return date_str

                    # If parsed_date isn't recognized as a datetime, return original
                    if not isinstance(parsed_date, dt):
                        return date_str

                    # If we're here, the prefix was parsed successfully as a date
                    parts = match.groupdict()
                    found_hours = parts.get("hours")
                    found_minutes = parts.get("minutes")
                    found_seconds = parts.get("seconds")
                    found_microseconds = parts.get("microseconds")

                    # Construct the final time components (preserve existing if None passed in)
                    final_hours = str(hours) if hours is not None else found_hours
                    final_minutes = str(minutes) if minutes is not None else found_minutes
                    final_seconds = str(seconds) if seconds is not None else found_seconds
                    # Optionally enforce a default value for seconds if missing:
                    # if final_seconds is None:
                    #     final_seconds = "00"

                    final_microseconds = str(microseconds) if microseconds is not None else found_microseconds

                    # Ensure microseconds are always six digits if present
                    if final_microseconds is not None:
                        final_microseconds = final_microseconds.ljust(6, '0')  # pad zeros

                    # Build the new time string
                    new_time_str = f"{final_hours}:{final_minutes}"
                    if final_seconds is not None:
                        new_time_str += f":{final_seconds}"
                        if final_microseconds is not None:
                            new_time_str += f".{final_microseconds}"

                    # Replace the old time portion with the new one
                    time_start, time_end = match.span("time")
                    new_str = cleaned_date_str[:time_start] + new_time_str + cleaned_date_str[time_end:]
                    return new_str

                else:
                    # ------------------------------------------
                    # CASE B: No time substring found
                    # ------------------------------------------
                    # Try parsing the entire cleaned string as a date
                    try:
                        parsed_date = self.parent.parse(cleaned_date_str)                    	
                        # parsed_date = dateplumb.pro_parse(cleaned_date_str)
                    except Exception:
                        # If parsing fails, it's not a valid date => return original
                        return date_str

                    # If parsed_date isn't recognized as a datetime, return original
                    if not isinstance(parsed_date, dt):
                        return date_str

                    # At this point, we have a valid date but no time in the string
                    # so we add time from overrides or default it to "00:00:00" (with optional microseconds)
                    # Use "00" if user didn't specify hours or minutes
                    final_hours = str(hours) if hours is not None else "00"
                    final_minutes = str(minutes) if minutes is not None else "00"
                    final_seconds = str(seconds) if seconds is not None else "00"
                    final_microseconds = None
                    if microseconds is not None:
                        final_microseconds = str(microseconds).ljust(6, '0')

                    new_time_str = f"{final_hours}:{final_minutes}:{final_seconds}"
                    if final_microseconds:
                        new_time_str += f".{final_microseconds}"

                    # Return "original_date + time"
                    # Since the user input had just a date (no trailing time), we can just append
                    # the time with a space or 'T'—depending on your desired format.
                    # Here we'll just use a space:
                    return f"{cleaned_date_str} {new_time_str}"

        def __dir__(self):
            return ['time'] 
           
           
    ##────────── Main Methods ───────────────────────────────────────────────────────────────────────────────────────────────────────────    
    def now(self, utc=False, as_unix=False, format=None):
        """
        Get the current date and time.

        Parameters:
            utc (bool, optional): If True, returns the current UTC time instead of local time. Defaults to False.
            as_unix (bool, optional): If True, returns the Unix timestamp instead of a datetime object. Defaults to False.
            format (str, optional): If provided, returns the formatted date string according to this format.

        Returns:
            dt | int | str: 
                - If `as_unix` is True, returns an integer Unix timestamp.
                - If `format` is provided, returns a formatted string representation of the date.
                - Otherwise, returns a `dt` object.
        """
        current = dt.utcnow() if utc else dt.now()
        if as_unix:
            return self.unix_timestamp(current)
        return current.strftime(format) if format else current

    def nowCT(self, as_unix=False, format=None):
        """
        Retrieve the current date and time in Central Time (CT).

        Parameters:
            as_unix (bool, optional): If True, return the Unix timestamp. Defaults to False.
            format (str, optional): Format string for output. Defaults to None.

        Returns:
            dt, int, or str: The current CT time as a datetime object, Unix timestamp, or formatted string.
        """
        now_utc = dt.utcnow()
        if self.EasternTime.isDST(now_utc):           
            current = now_utc - td(hours=5)  # UTC-5 for DST
        else:
            current = now_utc - td(hours=6)  # UTC-6 for Standard Time
        if as_unix:
            return self.unix_timestamp(current) # Convert to Unix timestamp
        return current.strftime(format) if format else current  # Return formatted time if format is provided, otherwise return datetime object    

    def make_timezone_aware(self, date_value, offset_hours):
        """
        Make a naive datetime object timezone-aware.

        Parameters:
            date_value (dt): A naive datetime object.
            offset_hours (int or float): UTC offset in hours to apply.

        Returns:
            dt: The timezone-aware datetime object.
        """
        if date_value.tzinfo is not None:
            return date_value
        tz = tmz(td(hours=offset_hours))
        return date_value.replace(tzinfo=tz)

    def unix_timestamp(self, date_value, format=None, utc=False, reset_time=False, to_unix=True, assume_utc_if_naive=False):
        """
        Convert between Unix timestamps and datetime objects.

        Parameters:
            date_value (dt or int or str): 
                - If to_unix=True: datetime or parseable string.
                - If to_unix=False: an integer Unix timestamp.
            format (str, optional): If converting from Unix to string, apply this output format.
            utc (bool): If True, interpret or return the time in UTC.
            reset_time (bool): If True, reset time to 00:00:00.
            to_unix (bool): Direction of conversion. True = datetime → Unix. False = Unix → datetime.
            assume_utc_if_naive (bool): 
                - When utc=True and datetime is naive, treat it as UTC (rather than local time).

        Returns:
            int | datetime | str: Converted Unix timestamp, datetime object, or formatted string.

        Raises:
            ValueError: On invalid types or missing information.
        """
        if not isinstance(date_value, (int, dt)):
            try:
                date_value = self.parse(date_value)
            except Exception:
                raise ValueError("Expected datetime object or integer for Unix timestamp conversion.")

        if to_unix:
            if not isinstance(date_value, dt):
                raise ValueError("Expected datetime object for Unix timestamp conversion.")

            datetime_obj = date_value

            if utc:
                if datetime_obj.tzinfo is None:
                    if assume_utc_if_naive:
                        datetime_obj = datetime_obj.replace(tzinfo=tmz.utc)
                    else:
                        # By default, naive is interpreted as local time → convert to UTC manually
                        datetime_obj = datetime_obj.astimezone(tmz.utc)
                else:
                    datetime_obj = datetime_obj.astimezone(tmz.utc)

            if reset_time:
                datetime_obj = datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0)

            return int(datetime_obj.timestamp())

        else:
            if not isinstance(date_value, int):
                raise ValueError("Expected integer Unix timestamp for conversion to datetime.")

            datetime_obj = dt.fromtimestamp(date_value, tmz.utc if utc else None)

            if format:
                return datetime_obj.strftime(format)
            return datetime_obj      

    def subtract_months(self, date_str, months):
        """
        Subtract a specified number of months from a given date.

        Parameters:
            date_str (str): The input date as a string in the format '%Y-%m-%d'.
            months (int): The number of months to subtract.

        Returns:
            str: The resulting date string formatted as '%Y-%m-01'.
        """  	
        date = dt.strptime(date_str, '%Y-%m-%d')
        new_month = date.month - months
        new_year = date.year
        while new_month <= 0:
            new_month += 12
            new_year -= 1        
        new_day = min(date.day, (dt(new_year, new_month + 1, 1) - dt(new_year, new_month, 1)).days)
        new_date = dt(new_year, new_month, new_day)        
        return new_date.strftime('%Y-%m-01')

    def days_in_year(self, year):
        """
        Calculate the number of days in a given year.

        Parameters:
            year (int): The year to evaluate.

        Returns:
            int: 366 if the year is a leap year; otherwise, 365.
        """
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 366  # Leap year has 366 days
        else:
            return 365  # Common year has 365 days

    def weeks_in_year(self, date=None, mode='passed'):
        """
        Calculate the number of weeks passed or remaining in the year from a given date.

        Parameters:
            date (str or datetime.date, optional): The reference date (in '%Y-%m-%d' format or as a date object). Defaults to today.
            mode (str, optional): Calculation mode - 'passed' for weeks passed, 'left' for weeks remaining. Defaults to 'passed'.

        Returns:
            int: The number of weeks based on the specified mode.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        if date is None:
            date = d.today()
        elif isinstance(date, str):
            date = self.parse(date).date()

        start_of_year = d(date.year, 1, 1)
        end_of_year = d(date.year, 12, 31)

        if mode == 'passed':
            days_passed = (date - start_of_year).days
            return days_passed // 7
        elif mode == 'left':
            days_left = (end_of_year - date).days
            return days_left // 7
        else:
            raise ValueError("Invalid mode. Please choose 'passed' or 'left'.")

    def contains_time(self, obj):
        """
        Determines whether the provided object has non-zero time information.

        Accepts datetime, time, or date objects.
        
        - For datetime and time objects, returns True if at least one of the time components
          (hour, minute, second, microsecond) is non-zero.
        - For date objects (which lack time data), returns False.
        
        :param obj: A datetime, date, or time object.
        :return: True if the object has non-zero time information; otherwise, False.
        :raises TypeError: If 'obj' is not a recognized date/time type.
        """
        if self._is_datetimeType(obj):
            if isinstance(obj, dt) or isinstance(obj, t):
                return (obj.hour, obj.minute, obj.second, obj.microsecond) != (0, 0, 0, 0)
            elif isinstance(obj, d):
                return False # date objects have no time information, so return False
        return False
       
    def build(
        self,
        year,
        month,
        day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tz_offset_hours=None,
        as_date=False
    ):
        """
        Build a datetime (or date) object from individual components.

        Parameters:
            year (int): The year.
            month (int): The month (1–12).
            day (int): The day of the month.
            hour (int): Hour (0–23). Default is 0.
            minute (int): Minute (0–59). Default is 0.
            second (int): Second (0–59). Default is 0.
            microsecond (int): Microsecond (0–999999). Default is 0.
            tz_offset_hours (int | float, optional): If given, apply this timezone offset.
            as_date (bool): If True, return a `date` object instead of `datetime`.

        Returns:
            datetime | date: The constructed datetime or date object.
        """
        tzinfo = tmz(td(hours=tz_offset_hours)) if tz_offset_hours is not None else None
        dt_obj = dt(year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo)
        return dt_obj.date() if as_date else dt_obj
       

    def __dir__(self):
        return ['parse', 'now', 'unix_timestamp', 'nowCT', 'subtract_months', 'days_in_year', 'weeks_in_year', 'ET', 'make_timezone_aware', 'sub', 'contains_time', 'add', 'flush', 'build']

dtparse = dt_parse()



def __dir__():
    return ['dtparse']

__all__ = ['dtparse']







# class dt_parse:
#     def __init__(self):
#         self.date_formats = [
#             '%Y.%m.%d', 
#             '%m.%d.%Y', 
#             '%B %d, %Y', 
#             '%b %d, %Y', 
#             '%d.%m.%Y', 
#             '%d %b %Y', 
#             '%d %B %Y',
#             '%b %d %Y',
#             '%Y%m%d',
#             '%d%m%Y',
#             '%A, %B %d %Y',
#             '%Y-%m-%dT%H:%M:%SZ',
#             '%a, %d %b %Y %H: %M:%S',
#             '%Y-%m',
#         ]
#         self.formats_with_dots = [fmt for fmt in self.date_formats if '.' in fmt]
#         self.formats_without_dots = [fmt for fmt in self.date_formats if '.' not in fmt]
#         self.last_successful_format = None
#         self.date_format_string_pattern = re.compile(r"%[aAbBcdHImMpSUwWxXyYZ]")
# 
#     def is_date_format_string(self, text):
#         if not isinstance(text, str):
#             return False
#         return bool(self.date_format_string_pattern.search(text))
# 
#     def is_datetimeType(self, obj, format='%Y-%m-%d', strf=False):
#         """ Check the type of the given object related to date and time, without assuming the import name of the datetime module."""
#         datetime_class_name = 'datetime'
#         date_class_name = 'date'
# 
#         if obj.__class__.__name__ == datetime_class_name and hasattr(obj, 'hour'):
#             if strf:
#                 return obj.strftime(format)
#             else:
#                 return True
#                 
#         elif obj.__class__.__name__ == date_class_name and not hasattr(obj, 'hour'):
#             if strf:
#                 return obj.strftime(format)            
#             else:
#                 return True
#         else:
#             return False
# 
#     def parse(self, date_input, from_format=None, to_format=None, to_unix_timestamp=False):
#         """ Parses and converts dates from various formats.
#             Handles single string inputs, lists, numpy arrays, and pandas Series.
#             The to_unix_timestamp argument converts the parsed date to an integer timestamp.
#         """
#         if self.is_datetimeType(date_input):
#             if to_unix_timestamp:
#                 return int(date_input.timestamp())
#             if to_format and self.is_date_format_string(to_format):
#                 return date_input.strftime(to_format)
#             return date_input        
#         
#         def process(date_string):
#             date_str = re.sub(r'\s+', ' ', date_string).strip()
#             
#             if self.last_successful_format:
#                 try:
#                     parsed_date = datetime.datetime.strptime(date_str, self.last_successful_format)
#                     if to_unix_timestamp:
#                         return int(parsed_date.timestamp())
#                     if not from_format and self.is_date_format_string(to_format):
#                         return parsed_date.strftime(to_format)
#                     return parsed_date
#                 except ValueError:
#                     pass
# 
#             for format_list in [self.formats_with_dots, self.formats_without_dots]:
#                 for date_format in format_list:
#                     try:
#                         parsed_date = datetime.datetime.strptime(date_str, date_format)
#                         self.last_successful_format = date_format
#                         if to_unix_timestamp:
#                             return int(parsed_date.timestamp())
#                         if not from_format and self.is_date_format_string(to_format):
#                             return parsed_date.strftime(to_format)
#                         return parsed_date
#                     except ValueError:
#                         continue
# 
#             new_separators = ['/', '-']
#             for sep in new_separators:
#                 for date_format in self.formats_with_dots:
#                     new_format = date_format.replace('.', sep)
#                     try:
#                         parsed_date = datetime.datetime.strptime(date_str, new_format)
#                         self.last_successful_format = new_format
#                         if to_unix_timestamp:
#                             return int(parsed_date.timestamp())
#                         if not from_format and self.is_date_format_string(to_format):
#                             return parsed_date.strftime(to_format)
#                         return parsed_date
#                     except ValueError:
#                         continue
# 
#             if from_format and to_format:
#                 try:
#                     parsed_date = datetime.datetime.strptime(date_str, from_format)
#                     if to_unix_timestamp:
#                         return int(parsed_date.timestamp())
#                     formatted_date = parsed_date.strftime(to_format)
#                     return formatted_date
#                 except ValueError:
#                     raise ValueError("Date format not recognized and fallback failed. Please check your formats.")
#             elif from_format:
#                 try:
#                     parsed_date = datetime.datetime.strptime(date_str, from_format)
#                     if to_unix_timestamp:
#                         return int(parsed_date.timestamp())
#                     return parsed_date
#                 except ValueError:
#                     raise ValueError("Date format not recognized. Please check your from_format.")
#             raise ValueError("Date format not recognized. Please use a supported date format.")
# 
#         if isinstance(date_input, str):
#             return process(date_input)
#         elif isinstance(date_input, list) or isinstance(date_input, np.ndarray):
#             return [process(date_str) for date_str in date_input]
#         elif isinstance(date_input, pd.Series):
#             date_input = date_input.astype(str)
#             return date_input.apply(process)
#         else:
#             raise ValueError("Unsupported data type. The input must be a str, list, numpy.ndarray, or pandas.Series.")
# 
#     def _is_dst(self, dt=None, timezone="US/Central"):
#         if dt is None:
#             dt = datetime.datetime.utcnow()
#         dst_start = datetime.datetime(dt.year, 3, 8)
#         dst_end = datetime.datetime(dt.year, 11, 1) 
#         while dst_start.weekday() != 6: 
#             dst_start += datetime.timedelta(days=1)
#         while dst_end.weekday() != 6:
#             dst_end += datetime.timedelta(days=1)
#         dst_start = dst_start.replace(hour=2)
#         dst_end = dst_end.replace(hour=2)
#         return dst_start <= dt < dst_end
#     
#     def subtract_months(self, date_str, months):
#         date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#         new_month = date.month - months
#         new_year = date.year
#         while new_month <= 0:
#             new_month += 12
#             new_year -= 1        
#         new_day = min(date.day, (datetime.datetime(new_year, new_month + 1, 1) - datetime.datetime(new_year, new_month, 1)).days)
#         new_date = datetime.datetime(new_year, new_month, new_day)        
#         return new_date.strftime('%Y-%m-01')
#     
#     def now(self, utc=False, as_unix=False, as_string=False, format=None):
#         current_time = datetime.datetime.utcnow() if utc else datetime.datetime.now()
#         if as_unix:
#             return self.unix_timestamp(current_time)        
#         if as_string:
#             if format:
#                 return current_time.strftime(format)
#             return current_time.strftime("%Y-%m-%d")
#         return current_time
#     
#     def nowCT(self, as_unix=False, as_string=False):
#         now_utc = datetime.datetime.utcnow()
#         current_utc_time = now_utc + datetime.timedelta(hours=5)
#         if self._is_dst(current_utc_time):
#             central_time = current_utc_time - datetime.timedelta(hours=1)
#         else:
#             central_time = current_utc_time - datetime.timedelta(hours=2)
#         if as_string:
#             return central_time.date().strftime('%Y-%m-%d')        
#         return central_time
# 
#     def unix_timestamp(self, datetime_obj, utc=True, reset_time=False):
#         if utc:
#             utc_datetime = datetime_obj.replace(tzinfo=datetime.timezone.utc)
#             if reset_time:
#                 utc_datetime = utc_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
#             return int(utc_datetime.timestamp())
#         else:
#             if reset_time:
#                 datetime_obj = datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0)
#             return int(datetime_obj.timestamp())
#            
#     def from_unix_timestamp(self, unix_timestamp, format=None):
#         """ Converts a Unix timestamp to a human-readable date."""
#         if not isinstance(unix_timestamp, int):
#             return None        
#         time_struct = time.localtime(unix_timestamp)
#         if format:
#             return time.strftime(format, time_struct)      
#         return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
# 
#     def __dir__(self):
#         return ['parse', 'now', 'unix_timestamp', 'nowCT', 'subtract_months', 'is_datetimeType']










