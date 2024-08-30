import time
import datetime
import re

# All NYSE markets observe U.S. holidays and early closings as listed below for 2024, 2025, and 2026.
market_early_closings = {
    "Independence Day": {
        1: "Wednesday, July 3 2024 13:00:00 UTC-4",
        2: "Thursday, July 3 2025 13:00:00 UTC-4",
    },
    "Thanksgiving Day": {
        1: "Friday, November 29 2024 13:00:00 UTC-5",
        2: "Friday, November 28 2025 13:00:00 UTC-5",
        3: "Friday, November 27 2026 13:00:00 UTC-5",
    },
    "Christmas": {
        1: "Tuesday, December 24 2024 13:00:00 UTC-5",
        2: "Wednesday, December 24 2025 13:00:00 UTC-5",
        3: "Thursday, December 24 2026 13:00:00 UTC-5",
    }
}

market_observed_holidays = {
    "New Year's Day": {
        1: "Monday, January 1 2024",
        2: "Wednesday, January 1 2025",
        3: "Thursday, January 1 2026"
    },
    "Martin Luther King, Jr. Day": {
        1: "Monday, January 15 2024",
        2: "Monday, January 20 2025",
        3: "Monday, January 19 2026"
    },
    "Washington's Birthday": {
        1: "Monday, February 19 2024",
        2: "Monday, February 17 2025",
        3: "Monday, February 16 2026"
    },
    "Good Friday": {
        1: "Friday, March 29 2024",
        2: "Friday, April 18 2025",
        3: "Friday, April 3 2026"
    },
    "Memorial Day": {
        1: "Monday, May 27 2024",
        2: "Monday, May 26 2025",
        3: "Monday, May 25 2026"
    },
    "Juneteenth National Independence Day": {
        1: "Wednesday, June 19 2024",
        2: "Thursday, June 19 2025",
        3: "Friday, June 19 2026"
    },
    "Independence Day": {
        1: "Thursday, July 4 2024",
        2: "Friday, July 4 2025",
        3: "Friday, July 3 2026"
    },
    "Labor Day": {
        1: "Monday, September 2 2024",
        2: "Monday, September 1 2025",
        3: "Monday, September 7 2026"
    },
    "Thanksgiving Day": {
        1: "Thursday, November 28 2024",
        2: "Thursday, November 27 2025",
        3: "Thursday, November 26 2026"
    },
    "Christmas": {
        1: "Wednesday, December 25 2024",
        2: "Thursday, December 25 2025",
        3: "Friday, December 25 2026"
    }
}

major_currencies = {
		'AUD': 'Australian Dollar',
		'CAD': 'Canadian Dollar',
		'CHF': 'Swiss Franc',
		'CNY': 'Chinese Yuan Renminbi',
		'CZK': 'Czech Koruna',
		'DKK': 'Danish Kroner',
		'EUR': 'Euro',
		'GBP': 'Pound Sterling',
		'HKD': 'Hong Kong Dollar',
		'HRK': 'Croatia Kuna',
		'HUF': 'Hungary Forint',
		'ILS': 'Israel Shekel',
		'INR': 'Indian Rupee',
		'JPY': 'Japanese Yen',
		'MXN': 'Mexican Peso',
		'NZD': 'New Zealand Dollar',
		'PLN': 'Polish Zloty',
		'SEK': 'Swedish Kroner',
		'USD': 'US Dollar',
		'ZAR': 'South African Rand'
}

bchart_currencies = {
    'AFN': 'Afghan Afghanis',
    'DZD': 'Algerian Dinar',
    'ARS': 'Argentine Peso',
    'AMD': 'Armenia Drams',
    'AWG': 'Aruba Guilder',
    'AUD': 'Australian Dollar',
    'BSD': 'Bahamian Dollar',
    'BHD': 'Bahrain Dinar',
    'BDT': 'Bangladesh Taka',
    'BBD': 'Barbados Dollars',
    'LSL': 'Basotho Loti',
    'BYR': 'Belarus Rubles',
    'BZD': 'Belize Dollars',
    'BMD': 'Bermudian Dollar',
    'BTN': 'Bhutanese Ngultrum',
    'BOB': 'Bolivia Bolivianos',
    'BAM': 'Bosnian Marka',
    'BWP': 'Botswana Pula',
    'BRL': 'Brazilian Real',
    'GBP': 'British Pound',
    'BND': 'Brunei Darussalam Dollars',
    'BGN': 'Bulgarian Lev',
    'BIF': 'Burundi Francs',
    'KHR': 'Cambodia Riels',
    'CAD': 'Canadian Dollar',
    'CVE': 'Cape Verde Escudos',
    'KYD': 'Caymanian Dollar',
    'XAF': 'Central African Cfa Franc Beac',
    'XOF': 'Cfa Franc',
    'XPF': 'Cfp Franc',
    'CLP': 'Chilean Peso',
    'CNH': 'Chinese Offshore Spot',
    'CNY': 'Chinese Yuan',
    'COP': 'Colombian Peso',
    'KMF': 'Comorian Franc',
    'CDF': 'Congolese Franc',
    'CRC': 'Costa Rica Colones',
    'HRK': 'Croatian Kuna',
    'CUP': 'Cuba Pesos',
    'CYP': 'Cyprus Pound',
    'CZK': 'Czech Koruna',
    'DKK': 'Danish Krone',
    'DJF': 'Djibouti Francs',
    'DOP': 'Dominican Peso',
    'XCD': 'East Caribbean Dollar',
    'EGP': 'Egyptian Pound',
    'SVC': 'El Salvador Colones',
    'EEK': 'Estonian Kroon',
    'ETB': 'Ethiopia Birr',
    'EUR': 'Euro',
    'FJD': 'Fiji Dollar',
    'GMD': 'Gambia Dalasi',
    'GEL': 'Georgian Lari',
    'GHS': 'Ghanaian Cedi',
    'XAU': 'Gold',
    'GTQ': 'Guatemala Quetzal',
    'GNF': 'Guinean Franc',
    'GYD': 'Guyanese Dollar',
    'HTG': 'Haiti Gourdes',
    'HNL': 'Honduras Lempira',
    'HKD': 'Hong Kong Dollar',
    'HUF': 'Hungarian Forint',
    'ISK': 'Icelandic Krona',
    'XDR': 'Imf Drawing Rights',
    'INR': 'Indian Rupee',
    'IDR': 'Indonesian Rupiah',
    'IRR': 'Iran Rials',
    'IQD': 'Iraq Dinars',
    'ILS': 'Israeli Shekel',
    'JMD': 'Jamaican Dollar',
    'JPY': 'Japanese Yen',
    'JOD': 'Jordanian Dinar',
    'KZT': 'Kazakhstan Tenge',
    'KES': 'Kenyan Shilling',
    'LFX': 'Khazanah Sukuk',
    'KRW': 'Korean Won',
    'KWD': 'Kuwaiti Dinar',
    'KGS': 'Kyrgyzstani Som',
    'LAK': 'Laos Kips',
    'LVL': 'Latvian Lats',
    'LBP': 'Lebanese Pound',
    'LRD': 'Liberia Dollar',
    'LYD': 'Libya Dinars',
    'LTL': 'Lithuanian Litas',
    'MOP': 'Macau Patacas',
    'MKD': 'Macedonian Denar',
    'MGA': 'Madagascar Ariary',
    'MWK': 'Malawian Kwacha',
    'MYR': 'Malaysian Ringgit',
    'MVR': 'Maldives Rufiyaa',
    'MRO': 'Mauritania Ouguiyas',
    'MUR': 'Mauritian Rupee',
    'MXN': 'Mexican Peso',
    'MDL': 'Moldova Lei',
    'MAD': 'Moroccan Dirham',
    'MZN': 'Mozambique Metical',
    'MMK': 'Myanmar Burma Kyats',
    'NAD': 'Namibian Dollar',
    'NPR': 'Nepal Nepal Rupees',
    'NZD': 'New Zealand Dollar',
    'NIO': 'Nicaraguan Cordoba',
    'NGN': 'Nigerian Naira',
    'NOK': 'Norwegian Krone',
    'OMR': 'Omani Rial',
    'PKR': 'Pakistan Rupee',
    'XPD': 'Palladium',
    'PAB': 'Panama Balboa',
    'PGK': 'Papua New Guinea Kina',
    'PYG': 'Paraguayan Guarani',
    'PEN': 'Peruvian Sol',
    'PHP': 'Philippine Peso',
    'XPT': 'Platinum',
    'PLN': 'Polish Zloty',
    'QAR': 'Qatari Riyal',
    'RON': 'Romanian Lei',
    'RUB': 'Russian Ruble',
    'RWF': 'Rwandan Franc',
    'STD': 'Sao Tome Dobra',
    'SAR': 'Saudi Riyal',
    'RSD': 'Serbian Dinar',
    'SCR': 'Seychelles Rupee',
    'SLL': 'Sierra Leonean',
    'XAG': 'Silver',
    'SGD': 'Singapore Dollar',
    'SKK': 'Slovak Koruna',
    'SOS': 'Somali Shillings',
    'ZAR': 'South African Rand',
    'SDR': 'Special Drawing Rights',
    'LKR': 'Sri Lankan Rupee',
    'SHP': 'St Helena Pound',
    'SDG': 'Sudan Pounds',
    'SDD': 'Sudanese Dinars',
    'SZL': 'Swazi Lilangeni',
    'SEK': 'Swedish Krone',
    'CHF': 'Swiss Franc',
    'SYP': 'Syria Pounds',
    'TWD': 'Taiwan Dollar',
    'TJS': 'Tajikistani Somoni',
    'TZS': 'Tanzania Shillings',
    'THB': 'Thai Baht',
    'TTD': 'Trinidadian Dollar',
    'TND': 'Tunisian Dinar',
    'TRY': 'Turkish New Lira',
    'TMT': 'Turkmenistan Manat',
    'AED': 'U.A.E. Dirham',
    'USD': 'U.S. Dollar',
    'UGX': 'Ugandan Shillings',
    'UAH': 'Ukraine Hryvnia',
    'UYU': 'Uruguayan Peso',
    'UZS': 'Uzbekistani Som',
    'VEF': 'Venezuelan Bolivars',
    'VND': 'Vietnam Dong',
    'YER': 'Yemeni Rials',
    'ZMK': 'Zambia Kwacha',
    'ZMW': 'Zambian Kwacha'
}

class currencyquery:
    class which:
        @staticmethod
        def major(currencies=major_currencies):
            return list(currencies.keys())
           
        @staticmethod
        def quote(currencies=bchart_currencies):
            return list(currencies.keys())
           
    @staticmethod    
    def tokenize(currency, as_tuple=False):
        # If the input is a list, handle it accordingly
        if isinstance(currency, list):
            # Normalize each element in the list and then check conditions
            cleaned_list = [re.sub(r'\s+', chr(32), item).strip().upper() for item in currency]
            if len(cleaned_list) == 1 and len(cleaned_list[0]) == 3 and cleaned_list[0].isalpha():
                ccy = cleaned_list[0]
                return (ccy,) if as_tuple else [ccy]
            elif len(cleaned_list) == 2 and all(len(item) == 3 and item.isalpha() for item in cleaned_list):
                if cleaned_list[0] == cleaned_list[1]:
                    return None
                else:
                    return tuple(cleaned_list) if as_tuple else cleaned_list
            else:
                return None
        else:
            # Normalize the string input
            currency = re.sub(r'\s+', chr(32), currency).strip().upper()
            
            # First match: Try to match a pair of currencies
            match = re.match(r'^([A-Z]{3})([-_/]?)([A-Z]{3})$', currency)
            if match:
                currency1, separator, currency2 = match.groups()
                if currency1 == currency2:
                    return None
                else:
                    return (currency1, currency2) if as_tuple else [currency1, currency2]
            # Second match: If the first match fails, try to match a single currency
            match = re.match(r'^([A-Z]{3})$', currency)
            if match:
                ccy = match.group(1)
                return (ccy,) if as_tuple else [ccy]
            return None

    @staticmethod
    def query(query, query_type="major", ret_type=None):
        # currency_dict = xr_currencies if query_type == "historical" else bchart_currencies
        currency_dict = major_currencies if query_type == "major" else bchart_currencies        
        query_lower = query.lower()
        for key, value in currency_dict.items():
            if query_lower == key.lower() or query_lower == value.lower():
                if ret_type is not None:
                    if ret_type.lower() == "code":
                        return key
                    elif ret_type.lower() == "name":
                        return value
                else:
                    return (key, value)
        return None






class ForexMarketHours:
    def __init__(self, timezone="US/Central"):
        self.timezone = timezone
        
    def is_dst(self, dt=None):
        """Determine whether Daylight Saving Time (DST) is in effect for a given datetime."""
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

    def get_central_time(self):
        now_utc = datetime.datetime.utcnow()
        current_utc_time = now_utc + datetime.timedelta(hours=5)
        if self.is_dst(current_utc_time):
            central_time = current_utc_time - datetime.timedelta(hours=1)
        else:
            central_time = current_utc_time - datetime.timedelta(hours=2)
        return central_time

    def is_forex_market_open(self):
        central_time = self.get_central_time()
        sessions = {
            'sydney': {'start': 22, 'end': 6},
            'tokyo': {'start': 0, 'end': 8},  
            'london': {'start': 8, 'end': 16}, 
            'new_york': {'start': 13, 'end': 21}
        }
        if self.is_dst(central_time):
            utc_time = central_time + datetime.timedelta(hours=5) 
        else:
            utc_time = central_time + datetime.timedelta(hours=6)
        utc_hour = utc_time.hour
        for session, hours in sessions.items():
            if hours['start'] <= utc_hour < hours['end'] or (hours['end'] < hours['start'] and (utc_hour >= hours['start'] or utc_hour < hours['end'])):
                return True
        return False
    
    @property
    def time(self):
        """Property to get the current Forex time if the market is open, or None if closed."""
        if self.is_forex_market_open():
            return self.get_central_time().strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None


def time_check(datetime_string):
    timezone_part = datetime_string.split(" UTC")[-1]  # Extracts "-4"
    offset_hours = int(timezone_part)  # Convert to integer
    date_part = datetime_string.rsplit(" UTC", 1)[0]  # Removes " UTC-4"
    time_format = "%A, %B %d %Y %H:%M:%S"
    target_time = datetime.datetime.strptime(date_part, time_format)
    timezone_offset = datetime.timedelta(hours=offset_hours)
    target_time = target_time.replace(tzinfo=datetime.timezone(timezone_offset))
    return target_time

def get_current_time_in_est_edt():
    now_utc = datetime.datetime.utcnow()
    year = now_utc.year
    dst_start = datetime.datetime(year, 3, 8, 2) + datetime.timedelta(days=(6 - datetime.datetime(year, 3, 8, 2).weekday()))
    dst_end = datetime.datetime(year, 11, 1, 2) + datetime.timedelta(days=(6 - datetime.datetime(year, 11, 1, 2).weekday()))
    if dst_start <= now_utc.replace(tzinfo=None) < dst_end:
        offset = datetime.timedelta(hours=-4) # Eastern Daylight Time (UTC-4)
    else:
        offset = datetime.timedelta(hours=-5) # Eastern Standard Time (UTC-5)
    now_est_edt = now_utc + offset
    return now_est_edt

def get_current_offset_est_edt(datetime_datetime_obj=None):
    def has_timezone(dt):
        if isinstance(dt, datetime.datetime):
            return isinstance(dt.tzinfo, datetime.timezone)
        else:
            return None
           
    if datetime_datetime_obj:
        if has_timezone(datetime_datetime_obj):
            offset = datetime_datetime_obj.utcoffset()
            offset_seconds = offset.total_seconds()
            return offset_seconds/3600
    
    now_utc = datetime.datetime.utcnow()
    year = now_utc.year
    dst_start = datetime.datetime(year, 3, 8, 2) + datetime.timedelta(days=(6 - datetime.datetime(year, 3, 8, 2).weekday()))
    dst_end = datetime.datetime(year, 11, 1, 2) + datetime.timedelta(days=(6 - datetime.datetime(year, 11, 1, 2).weekday()))
    if dst_start <= now_utc.replace(tzinfo=None) < dst_end:
        return -4 # Eastern Daylight Time (UTC-4)
    else:
        return -5 # Eastern Standard Time (UTC-5)
    return 0

def make_timezone_aware(dt, offset_hours):
    if dt.tzinfo is not None:
        return dt
    tz = datetime.timezone(datetime.timedelta(hours=offset_hours))
    return dt.replace(tzinfo=tz)

def format_date(datetime_datetime_obj):
    if datetime_datetime_obj.tzinfo is None:
        second_sunday_march = datetime.datetime(datetime_datetime_obj.year, 3, 8, 2) + datetime.timedelta(days=(6-datetime.datetime(datetime_datetime_obj.year, 3, 8).weekday()))
        first_sunday_november = datetime.datetime(datetime_datetime_obj.year, 11, 1, 2) + datetime.timedelta(days=(6-datetime.datetime(datetime_datetime_obj.year, 11, 1).weekday()))
        if second_sunday_march <= datetime_datetime_obj.replace(tzinfo=None) < first_sunday_november:
            tzinfo = datetime.timezone(datetime.timedelta(hours=-4))  # EDT
        else:
            tzinfo = datetime.timezone(datetime.timedelta(hours=-5))  # EST
        datetime_datetime_obj = datetime_datetime_obj.replace(tzinfo=tzinfo)
    offset_hours = datetime_datetime_obj.utcoffset().total_seconds() / 3600
    if offset_hours == -4:
        tz_abbreviation = 'EDT'
    elif offset_hours == -5:
        tz_abbreviation = 'EST'
    else:
        tz_abbreviation = 'UTC'  # Fallback for non-EST/EDT time zones
    formatted_time = datetime_datetime_obj.strftime(f'%Y-%m-%d %I:%M %p {tz_abbreviation}')
    return formatted_time


# Normal Day
def normal_operating_hours():
    now_est_edt = get_current_time_in_est_edt()
    if now_est_edt.weekday() >= 5:
        return False
    # Check if the current time is within market hours (9:30 AM to 4:00 PM)
    market_open_time = now_est_edt.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now_est_edt.replace(hour=16, minute=0, second=0, microsecond=0)
    if market_open_time <= now_est_edt < market_close_time:
        return True
    else:
        return False

# Early Closing
def check_early_closings():
    now_est_edt = get_current_time_in_est_edt()
    for holiday, dates in market_early_closings.items():
        for key, date_str in dates.items():
            early_closing_time = time_check(date_str)
            if now_est_edt.date() == early_closing_time.date():
                if now_est_edt < early_closing_time:
                    return True
                else:
                    return False
    return False
        
# Holidays        
def is_today_holiday():
    now = datetime.datetime.now().date()
    for holiday, dates in market_observed_holidays.items():
        for key, date_str in dates.items():
            holiday_date = datetime.datetime.strptime(date_str, "%A, %B %d %Y").date()
            if now == holiday_date:
                return True
    return False

def is_market_open():
    if is_today_holiday():
        return False

    if check_early_closings():
        return True
    
    if normal_operating_hours():
        return True
    else:
        return False

def precompute_holidays(market_holidays=market_observed_holidays):
    holidays = set()
    for holiday, dates in market_holidays.items():
        for date_str in dates.values():
            holiday_date = datetime.datetime.strptime(date_str, "%A, %B %d %Y").date()
            holidays.add(holiday_date)
    return holidays

def last_open_date(format=None):
    holidays = precompute_holidays(market_observed_holidays)
    now = get_current_time_in_est_edt()
    if now.time() < datetime.time(9, 30):
        now = now.date() - datetime.timedelta(days=1)
    else:
        now = now.date()
    day_delta = datetime.timedelta(days=1)

    while now:
        if now.weekday() > 4:
            now -= datetime.timedelta(days=now.weekday() - 4)
            continue
        if now in holidays:
            now -= day_delta
            continue
        now = datetime.datetime.combine(now, datetime.time(16, 0))
        if format:
            return format_date(now)
        return now
    return None

forex_hours = ForexMarketHours()

def __dir__():
    return ['is_market_open', 'last_open_date', 'currencyquery', 'forex_hours']


__all__ = ['is_market_open', 'last_open_date', 'currencyquery', 'forex_hours']











