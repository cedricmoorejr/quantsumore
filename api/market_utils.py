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



import json
import os
from pathlib import Path
import re
import csv
from io import StringIO
import sqlite3
import unicodedata
from datetime import datetime, time, timezone

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from quantsumore import APP_DATA_DIR
from ..sys_utils import Download, Package, FileInspector
from ._filebase import JSON, SQLiteDBHandler
from .._version import __version__
from ..date_parser import dtparse

__all__ = [
    'fxutil',
    'forex_hours',
    'equityquery',
    'CurrencyQuery',
    'ExchangeQuery',
    'CoinQuery',
    'major_forex_currencies',    
]


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.

# -- Configure local data directory --
appdata_local_dir = str(APP_DATA_DIR) # Get the local directory for storing data files, using Device.quantsumore_default if set

# -- Define file names, paths, and URLs --
# Stock tickers: file and URL
_STOCK_TICKERS_FILE_PATH = os.path.join(appdata_local_dir, 'stock_tickers.txt')
_STOCK_TICKERS_URL = (
    f"https://raw.githubusercontent.com/"
    f"cedricmoorejr/quantsumore/"
    f"v{__version__}/"
    f"files/stock_tickers.txt"
)
# Crypto config: file, DB, and URL
_CRYPTO_CONFIG_FILE_PATH = os.path.join(appdata_local_dir, 'all_data.json')
_CRYPTO_DATABASE_FILE = 'crypto.db'
_CRYPTO_CONFIG_URL = (
    f"https://raw.githubusercontent.com/"
    f"cedricmoorejr/quantsumore/"
    f"refs/heads/v{__version__}/"
    f"files/crypto/all_data.json"
)

# -- Define the packages to be managed by the downloader --
packages = [
    Package(
        id="stocks",
        filename='stock_tickers.txt',
        url=(_STOCK_TICKERS_URL),
        schedule_hour=0,   # Github cron runs at midnight (12:00 AM), every Monday–Friday
    ),
    Package(
        id="crypto",
        filename='all_data.json',
        url=(_CRYPTO_CONFIG_URL),
        schedule_hour=1,   # Github cron runs at 1:00 AM, every Monday–Friday
    ),
]

# -- Download or refresh packages as needed --
dl = Download(packages) # Create a Download manager instance with the packages
dl.update(quiet=True, replace=True) # Attempt to download or refresh packages if stale/missing




######################################################################
# EQUITY
######################################################################
class equityquery:
    _registry = {}

    def __init__(self, symbol, company, exchange, yahoo_mapping, nasdaq_mapping):
        self.symbol = symbol
        self.company = company
        self.exchange = exchange
        self.yahoo_mapping = yahoo_mapping
        self.nasdaq_mapping = nasdaq_mapping
        equityquery._registry[symbol] = self

    def __repr__(self):
        return (f"equityquery(Symbol={self.symbol}, Company={self.company}, "
                f"Exchange={self.exchange}, yahoo_mapping={self.yahoo_mapping}, "
                f"nasdaq_mapping={self.nasdaq_mapping})")

    @staticmethod
    def initial_symbol_check(symbol):
        """Check if the symbol length is within the allowed range, contains no digits, and is not None."""
        if symbol is None:
            return False
        if not isinstance(symbol, str):
            return False
        if len(symbol) > 0 and len(symbol) <= 6:
            return not any(char.isdigit() for char in symbol)
        return False

    @classmethod
    def search_symbol(cls, symbol):
        """Search for a symbol in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symbol.lower()
        return any(stock.symbol.lower() == search_symbol_lower for stock in cls._registry.values())

    @classmethod
    def search_yahoo_symbol(cls, symbol):
        """Search for a symbol specifically in yahoo_mapping in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symbol.lower()
        return any(stock.yahoo_mapping.lower() == search_symbol_lower for stock in cls._registry.values())

    @classmethod
    def search_nasdaq_symbol(cls, symbol):
        """Search for a symbol specifically in nasdaq_mapping in a case-insensitive manner."""
        if not cls.initial_symbol_check(symbol):
            return False
        # Normalize the search symbol to lowercase (or uppercase)
        search_symbol_lower = symbol.lower()
        return any(stock.nasdaq_mapping.lower() == search_symbol_lower for stock in cls._registry.values())
    
    @classmethod
    def load_data(cls, file_path):
        """
        Load equity definitions from a local CSV file.
        First row is assumed to be the header.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"No such file: {file_path!r}")

        with path.open(newline='') as f:
            reader = csv.reader(f)
            next(reader)          # skip header
            for row in reader:
                if row:
                    cls(*row)    

    @classmethod
    def initialize_from_file(cls, data):
        f = StringIO(data)
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row:
                cls(*row)

# Load the data
equityquery.load_data(file_path=_STOCK_TICKERS_FILE_PATH)




######################################################################
# CRYPTOCURRENCY
######################################################################
class CryptoConfig:
    """
    Manages end-to-end synchronization and access of cryptocurrency metadata between
    a local JSON configuration file and a persistent SQLite database, with in-memory caching
    for high-performance reads.

    Purpose:
    -----------
        The `CryptoConfig` class orchestrates the loading, validation, and refreshing
        of crypto asset, exchange, and fiat pair data. It ensures your application always
        works with the freshest available data, while minimizing unnecessary rebuilds.

    Workflows:
    -----------
        - Full refresh:   Load new JSON data, rebuild the SQLite database, and repopulate all in-memory lists.
        - Resume:         Read all data directly from the existing database, skipping JSON parsing if DB is fresh.

    Attributes:
    -----------
        file_path        : Path to the local JSON configuration file (e.g., all_data.json).
        db_filename      : Filename for the SQLite database (e.g., crypto.db).
        db_directory     : Directory for the SQLite database (optional).
        saved_json_content : Cached JSON content after reading from file.
        cryptos          : In-memory list of crypto asset dictionaries.
        exchanges        : In-memory list of exchange dictionaries.
        pairs            : In-memory list of fiat pair dictionaries.

    Methods:
    -----------
        to_json()
            Load JSON data from file into `saved_json_content`.

        to_sqlite()
            Write loaded JSON data into the SQLite database, resetting it if needed.

        parse_db()
            Load all tables (cryptos, exchanges, pairs) from SQLite into memory.

        run()
            Full pipeline: Load JSON → Write SQLite → Read from DB into memory.

        run_from_db()
            Populate all in-memory lists directly from SQLite, skipping JSON.

        auto_run(application_data_directory, threshold_minutes=3, update_hour=1, verbose=False)
            Automatically determines whether to refresh from JSON or simply load from DB,
            based on file timestamps and freshness threshold. Prints detailed step-by-step
            status when `verbose=True`.

    Notes:
    -----------
        - Designed to guarantee atomic DB updates and safe concurrent reads.
        - All in-memory lists are always kept in sync with the DB after any operation.
    """
    def __init__(self, config_file_path = _CRYPTO_CONFIG_FILE_PATH, db_filename = _CRYPTO_DATABASE_FILE, db_directory = None):
        """
        Initialize a new CryptoConfig object for synchronizing cryptocurrency metadata.

        Parameters:
        -----------
        config_file_path : str or Path, optional
            Path to the local JSON configuration file containing cryptocurrency, exchange,
            and fiat pair data. Defaults to `_CRYPTO_CONFIG_FILE_PATH`.

        db_filename : str, optional
            Name of the SQLite database file for storing parsed data.
            Defaults to `_CRYPTO_DATABASE_FILE`.

        db_directory : str or Path, optional
            Directory in which the SQLite database file should be stored.
            If None, uses the handler's default directory.

        Attributes Initialized
        -----------
        file_path : Path
            Absolute path to the JSON configuration file.

        db_filename : str
            Filename for the SQLite database.

        db_directory : Path or None
            Directory for the SQLite database file.

        saved_json_content : dict
            Cached content of the loaded JSON file.

        cryptos : list
            In-memory list for crypto asset dictionaries.

        exchanges : list
            In-memory list for exchange dictionaries.

        pairs : list
            In-memory list for fiat pair dictionaries.

        Notes
        -----------
        - All attributes are instance-level and can be modified after initialization if needed.
        - The class does not load or process data during initialization; use `run`, `run_from_db`, or `auto_run` to load data.
        """    	
        self.file_path = Path(config_file_path)
        self.db_filename = db_filename
        self.db_directory = Path(db_directory) if db_directory is not None else None

        self.saved_json_content: dict = {}
        self.cryptos:   list[dict] = []
        self.exchanges: list[dict] = []
        self.pairs:     list[dict] = []
        
    def to_json(self):
        """
        Load JSON data from the local configuration file into memory.

        Parameters:
        -----------
        None

        Returns
        -----------
        None
            The parsed JSON content is stored in the `saved_json_content` attribute.

        Raises
        -----------
        FileNotFoundError
            If the specified JSON file does not exist at `file_path`.
        json.JSONDecodeError
            If the file content is not valid JSON.
        OSError
            For other I/O errors during file access.

        Notes
        -----------
        This method overwrites any existing value in `saved_json_content` with the newly loaded data.
        """
        with self.file_path.open("r", encoding="utf-8") as f:
            self.saved_json_content = json.load(f)

    def to_sqlite(self):
        """
        Write the currently loaded JSON data into the SQLite database, resetting the database first.

        Parameters:
        -----------
        None

        Returns
        -----------
        None
            Updates the database on disk. Does not return any value.

        Raises
        -----------
        RuntimeError
            If `saved_json_content` is empty or not yet loaded.
        sqlite3.DatabaseError
            For any database errors during the reset or write process.
        OSError
            For file system errors during database file operations.

        Notes
        -----------
        - This method removes any existing SQLite database before creating a fresh one using the current JSON data.
        - Both `db_filename` and `db_directory` are passed to the database handler for precise file location control.
        - Intended to be called after `to_json()` to ensure the latest data is written.
        """
        sqliteDB = SQLiteDBHandler(
            filename=self.db_filename,
            directory=self.db_directory,
            json_data=self.saved_json_content
        )
        sqliteDB.reset_database()
        sqliteDB.save()
        
    def parse_db(self):
        """
        Load all data tables from the SQLite database into in-memory Python lists.

        Parameters:
        -----------
        None

        Returns
        -----------
        None
            Populates the `cryptos`, `exchanges`, and `pairs` attributes with fresh data from the database.

        Raises
        -----------
        RuntimeError
            If the database file does not exist or is inaccessible.
        sqlite3.DatabaseError
            For errors encountered while querying the database.

        Notes
        -----------
        - This method queries the 'cryptos', 'exchanges', and 'pairs' tables in the configured SQLite database.
        - Results are returned as lists of dictionaries, with column names as keys.
        - Intended to be called after the database has been created or refreshed to synchronize all in-memory views.
        - If the database is missing, the method will raise immediately without modifying in-memory data.
        """
        handler = SQLiteDBHandler(
            filename=self.db_filename,
            directory=self.db_directory
        )
        if not handler.file_exists():
            raise RuntimeError(f"{handler.db_path} not found – run the full pipeline first.")

        with handler:
            # Cryptos
            handler.cursor.execute("""
                SELECT id, name, symbol, slug, is_active, status, rank
                FROM cryptos
                ORDER BY rank
            """)
            rows = handler.cursor.fetchall()
            keys = ["id", "name", "symbol", "slug", "is_active", "status", "rank"]
            self.cryptos = [dict(zip(keys, row)) for row in rows]

            # Exchanges
            handler.cursor.execute("""
                SELECT exchangeId, exchangeName, exchangeSlug
                FROM exchanges
                ORDER BY exchangeName
            """)
            rows = handler.cursor.fetchall()
            keys = ["exchangeId", "exchangeName", "exchangeSlug"]
            self.exchanges = [dict(zip(keys, row)) for row in rows]

            # Pairs
            handler.cursor.execute("""
                SELECT currencyId, currencySymbol, currency
                FROM pairs
                ORDER BY currency
            """)
            rows = handler.cursor.fetchall()
            keys = ["currencyId", "currencySymbol", "currency"]
            self.pairs = [dict(zip(keys, row)) for row in rows]
            
    def auto_run(self, application_data_directory, threshold_minutes=3, update_hour=1, verbose=False):
        """
        Automatically refreshes or loads cryptocurrency metadata by comparing the
        database creation time and the JSON configuration file's last update time.

        Parameters:
        -----------
        application_data_directory : str or Path
            Directory where both the SQLite database and JSON config file are located.

        threshold_minutes : int, optional
            Maximum age difference (in minutes) to consider the database "fresh".
            If the database was created within this window of the JSON file's
            last update, no rebuild will occur. Defaults to 3.

        update_hour : int, optional
            The scheduled hour when the JSON file is expected to be refreshed (e.g., 1 for 1AM).
            Used to compute the expected update threshold. Defaults to 1.

        verbose : bool, optional
            If True, prints step-by-step status messages describing the refresh logic.

        Returns
        -----------
        None
            Populates all in-memory lists (`cryptos`, `exchanges`, `pairs`) based on
            either a fresh DB build or a fast reload from SQLite.

        Notes
        -----------
        - If the database does not exist, the method always creates it from the JSON file.
        - If both files exist, but the database is older than the JSON file (by more than `threshold_minutes`), the database is rebuilt.
        - If the database is sufficiently fresh, all data is loaded directly from SQLite.
        - Intended as the one-stop entry point for data pipeline scheduling and ETL refreshes.
        """
        vprint = print if verbose else (lambda *a, **k: None)

        # 1) Prepare handler (point it at the right directory)
        handler_kwargs = {
            "filename": self.db_filename,
            "directory": application_data_directory
        }

        # 2) If no DB yet → full build
        temp = SQLiteDBHandler(**handler_kwargs)
        if not temp.file_exists():
            vprint("No existing database found. Creating new DB from JSON…")
            return self.run()

        # 3) DB exists, so open a context to get its timestamp
        with SQLiteDBHandler(**handler_kwargs) as dbh:
            created_iso = dbh.get_creation_time()
        last_db_dt = dtparse.parse(created_iso)
        vprint(f"Database found. Created at: {created_iso}")

        # 4) Inspect JSON arrival
        inspector    = FileInspector(application_data_directory)
        threshold_dt = inspector.last_scheduled_update(hour=update_hour)
        info_map     = inspector.inspect(self.file_path.name, threshold_dt=threshold_dt)
        file_info    = info_map[self.file_path.name]
        vprint(f"JSON file inspected. Exists: {file_info.exists}. "
               f"Created at: {getattr(file_info, 'creation_time', None)}. "
               f"Scheduled threshold: {threshold_dt}")

        # 5) Compare and choose
        if file_info.exists and dtparse.within_delta(
                file_info.creation_time,
                last_db_dt,
                threshold_minutes,
                "minutes"
        ):
            vprint("Database is fresh. Loading from DB only (no re-creation needed).")
            return self.run_from_db()
        else:
            if file_info.exists:
                vprint("Database is stale or JSON updated. Rebuilding database from JSON.")
            else:
                vprint("JSON file missing or too old. Rebuilding database from JSON.")
            return self.run()
            
    def run(self):
        """
        Executes the complete end-to-end data pipeline: loads JSON configuration,
        writes all data into the SQLite database (overwriting as needed),
        and populates in-memory lists (`cryptos`, `exchanges`, `pairs`) from the database.

        Parameters:
        -----------
        None

        Returns
        -----------
        None
            Updates all in-memory attributes with the latest data.

        Notes
        -----------
        - Always triggers a full refresh, regardless of the current state of the database.
        - Intended for scheduled refreshes or first-time initialization.
        """
        self.to_json()
        self.to_sqlite()
        self.parse_db()

    def run_from_db(self):
        """
        Populates all in-memory lists (`cryptos`, `exchanges`, `pairs`) by reading directly
        from the existing SQLite database, bypassing the JSON file entirely.

        Parameters:
        -----------
        None

        Returns
        -----------
        None
            Updates all in-memory attributes with data from the current database.

        Notes
        -----------
        - Does not modify or refresh the underlying database.
        - Useful for fast reloads when the database is already current.
        """
        self.parse_db()


# Initialize the config object with your paths.
config = CryptoConfig(
    config_file_path=_CRYPTO_CONFIG_FILE_PATH,
    db_filename=_CRYPTO_DATABASE_FILE
)

# Use .auto_run() to automatically handle database and JSON freshness.
# This will:
#   - Check if the database exists.
#   - Compare timestamps of the DB and the JSON config file.
#   - If the DB is up-to-date, load data from the DB (run_from_db).
#   - If the DB is missing or stale, recreate it from the JSON (run).
# You do NOT need to call run() or run_from_db() directly.
config.auto_run(application_data_directory=appdata_local_dir)


class Query:
    """
    Provides a unified, high-level query interface for cryptocurrency metadata, enabling
    rapid lookups across fiat currencies, exchanges, and coins/tokens from either in-memory
    JSON data or a persistent SQLite database.

    Purpose
    -----------
    The `Query` class serves as a namespace for specialized inner classes
    (`Currency`, `Exchange`, `Coin`), each designed to perform efficient searches
    and lookups on their respective data domains. This abstraction allows flexible,
    readable, and consistent access patterns for all supported crypto metadata types.

    Structure
    -----------
    - Query.Currency:    In-memory lookup for fiat currency pairs; supports search by ID and symbol.
    - Query.Exchange:    In-memory lookup for crypto exchanges; supports search by ID, name, slug, or identifier.
    - Query.Coin:        On-disk (SQLite) lookup for coins/tokens; supports search by ID, name, slug, and provides
                         a slug validation utility. Includes query result caching for high performance.
    Attributes
    -----------
    json_data : dict or None
        JSON data for fiat pairs and exchanges (passed to Currency and Exchange).

    Methods (by inner class)
    -----------
    Currency:
        - data               : Property, loads and returns fiat currency list.
        - ID(qID)            : Find currencies matching the given currencyId.
        - Symbol(symbol)     : Find currencies matching the given symbol (case-insensitive).
        - SymbolreturnID(symbol): Return the currencyId for the given symbol.

    Exchange:
        - data               : Property, loads and returns exchange list.
        - ID(exchange_id)    : Find exchanges by ID.
        - Name(exchange_name): Find exchanges by name (case-insensitive).
        - Slug(exchange_slug): Find exchanges by slug (case-insensitive).
        - FindID(identifier) : Find exchangeId by name or slug.

    Coin:
        - ID(crypto_id)      : Query coin by ID (from SQLite).
        - Name(name)         : Query coin by name (case-sensitive, normalized).
        - Slug(slug)         : Query coin by slug (from SQLite).
        - ListSlugs()        : List all slugs, names, and symbols.

    Notes
    -----------
    - Instantiate each inner class with appropriate JSON or DB file input to enable querying.
    - Caching is used for high-frequency queries, particularly with coin lookups.
    - All search methods are designed for interactive as well as programmatic use.
    - Intended to be used alongside the CryptoConfig pipeline for end-to-end data synchronization and access.
    """  	
    def __init__(self, json_data=None):
        self.json_data = json_data

    class Currency:
        def __init__(self, json_data):
            self.handler = JSON(json_data=json_data)                   
            self._data = None

        @property
        def data(self):
            if self._data is None:
                json_data = self.handler.load()
                self._data = json_data
            return self._data

        def ID(self, qID):
            return [ccy for ccy in self.data if str(ccy['currencyId']) == str(qID)]

        def Symbol(self, symbol):
            symbol = symbol.lower()
            return [ccy for ccy in self.data if ccy['currencySymbol'].lower() == symbol]

        def SymbolreturnID(self, symbol):
            symbol = symbol.lower()
            for ccy in self.data:
                if ccy['currencySymbol'].lower() == symbol:
                    return ccy['currencyId']
            return None
           
        def __dir__(self):
            return ['ID', 'Symbol', 'SymbolreturnID', 'data']  

    class Exchange:
        def __init__(self, json_data):
            self.handler = JSON(json_data=json_data)
            self._data = None

        @property
        def data(self):
            if self._data is None:
                json_data = self.handler.load()
                self._data = json_data
            return self._data        

        def ID(self, exchange_id):
            exch = str(exchange_id)
            return [exchange for exchange in self.data if exchange['exchangeId'] == exch]

        def Name(self, exchange_name):
            exchange_name = exchange_name.lower()
            return [exchange for exchange in self.data if exchange['exchangeName'].lower() == exchange_name]

        def Slug(self, exchange_slug):
            exchange_slug = exchange_slug.lower()
            return [exchange for exchange in self.data if exchange['exchangeSlug'].lower() == exchange_slug]

        def FindID(self, identifier):
            identifier = identifier.lower()
            for exchange in self.data:
                if exchange['exchangeName'].lower() == identifier or exchange['exchangeSlug'].lower() == identifier:
                    return int(exchange['exchangeId'])
            return None

        def __dir__(self):
            return ['ID', 'Name', 'Slug', 'FindID', 'data']        

    class Coin:
        def __init__(self, file):
            self.db_path = SQLiteDBHandler(file).path  
            self.cache = {
                'ID': {},
                'Name': {},
                'Slug': {},
                'ListSlugs': None
            }
        def append_active_condition(self, query):
            """Append an is_active = 1 condition to the WHERE clause in a query."""
            if 'WHERE' in query:
                return query + ' AND is_active = 1'
            else:
                return query + ' WHERE is_active = 1'

        def case_sensitive_search(self, word_to_find, word_to_check):
            return word_to_find == word_to_check
           
        def execute_query(self, query, params):
            query = self.append_active_condition(query)
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
            except sqlite3.Error as e:
                return []

        @staticmethod
        def normalize_string(input_string):
            """Normalize a string by removing special characters and accents but keep the case intact."""
            nfkd_form = unicodedata.normalize('NFKD', input_string)
            ascii_string = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
            return re.sub(r'[^\w\s]', '', ascii_string)

        def ID(self, crypto_id):
            # Check cache first
            if crypto_id in self.cache['ID']:
                return self.cache['ID'][crypto_id]
            query = 'SELECT * FROM cryptos WHERE id = ?'
            result = self.execute_query(query, (crypto_id,))
            # Cache the result
            self.cache['ID'][crypto_id] = result
            return result

        def Name(self, name):
            # Check cache first
            if name in self.cache['Name']:
                return self.cache['Name'][name]
            normalized_name = self.normalize_string(name)
            query = 'SELECT * FROM cryptos WHERE name LIKE ?'
            data = self.execute_query(query, (f'%{normalized_name}%',))
            filtered_data = [item for item in data if self.case_sensitive_search(name, item['name'])]
            # Cache the result
            self.cache['Name'][name] = filtered_data
            return filtered_data

        def Slug(self, slug):
            slug = slug.lower()
            # Check cache first
            if slug in self.cache['Slug']:
                return self.cache['Slug'][slug]
            query = 'SELECT * FROM cryptos WHERE slug = ?'
            result = self.execute_query(query, (slug,))
            # Cache the result
            self.cache['Slug'][slug] = result
            return result

        def ListSlugs(self):
            # Cache ListSlugs globally, as it has no parameters
            if self.cache['ListSlugs'] is not None:
                return self.cache['ListSlugs']
            query = 'SELECT name, symbol, slug FROM cryptos'
            result = self.execute_query(query, ())
            # Cache the result
            self.cache['ListSlugs'] = result
            return result

        def __dir__(self):
            return ['ID', 'Name', 'Slug', 'ListSlugs']



# Create an instance of ExchangeQuery, CurrencyQuery, CoinQuery:

# | Class            | Backing Store | Lookup Types         | Main Use                          |
# | ---------------- | ------------- | -------------------- | --------------------------------- |
# | `Query.Currency` | in-memory     | ID, Symbol           | Look up fiat/fiat-pair info       |
# | `Query.Exchange` | in-memory     | ID, Name, Slug       | Look up crypto exchange info      |
# | `Query.Coin`     | SQLite DB     | ID, Name, Slug, List | Look up coin/token info (cached)  |
query = Query()
CurrencyQuery = query.Currency(json_data=config.pairs)
ExchangeQuery = query.Exchange(json_data=config.exchanges)
CoinQuery = query.Coin(file=_CRYPTO_DATABASE_FILE)




######################################################################
# FOREX
######################################################################
major_forex_currencies = {
    'AUD': 'Australian Dollar', 'CAD': 'Canadian Dollar', 'CHF': 'Swiss Franc', 'CNY': 'Chinese Yuan Renminbi', 'CZK': 'Czech Koruna',
    'DKK': 'Danish Kroner', 'EUR': 'Euro', 'GBP': 'Pound Sterling', 'HKD': 'Hong Kong Dollar', 'HRK': 'Croatia Kuna',
    'HUF': 'Hungary Forint', 'ILS': 'Israel Shekel', 'INR': 'Indian Rupee', 'JPY': 'Japanese Yen', 'MXN': 'Mexican Peso',
    'NZD': 'New Zealand Dollar', 'PLN': 'Polish Zloty', 'SEK': 'Swedish Kroner', 'USD': 'US Dollar', 'ZAR': 'South African Rand',
    'AED': 'United Arab Emirates Dirham',
}
all_currency_names = {
    'AFN': 'Afghan Afghanis', 'DZD': 'Algerian Dinar', 'ARS': 'Argentine Peso', 'AMD': 'Armenia Drams', 'AWG': 'Aruba Guilder',
    'AUD': 'Australian Dollar', 'BSD': 'Bahamian Dollar', 'BHD': 'Bahrain Dinar', 'BDT': 'Bangladesh Taka', 'BBD': 'Barbados Dollars',
    'LSL': 'Basotho Loti', 'BYR': 'Belarus Rubles', 'BZD': 'Belize Dollars', 'BMD': 'Bermudian Dollar', 'BTN': 'Bhutanese Ngultrum',
    'BOB': 'Bolivia Bolivianos', 'BAM': 'Bosnian Marka', 'BWP': 'Botswana Pula', 'BRL': 'Brazilian Real', 'GBP': 'British Pound',
    'BND': 'Brunei Darussalam Dollars', 'BGN': 'Bulgarian Lev', 'BIF': 'Burundi Francs', 'KHR': 'Cambodia Riels', 'CAD': 'Canadian Dollar',
    'CVE': 'Cape Verde Escudos', 'KYD': 'Caymanian Dollar', 'XAF': 'Central African Cfa Franc Beac', 'XOF': 'Cfa Franc', 'XPF': 'Cfp Franc',
    'CLP': 'Chilean Peso', 'CNH': 'Chinese Offshore Spot', 'CNY': 'Chinese Yuan', 'COP': 'Colombian Peso', 'KMF': 'Comorian Franc',
    'CDF': 'Congolese Franc', 'CRC': 'Costa Rica Colones', 'HRK': 'Croatian Kuna', 'CUP': 'Cuba Pesos', 'CYP': 'Cyprus Pound',
    'CZK': 'Czech Koruna', 'DKK': 'Danish Krone', 'DJF': 'Djibouti Francs', 'DOP': 'Dominican Peso', 'XCD': 'East Caribbean Dollar',
    'EGP': 'Egyptian Pound', 'SVC': 'El Salvador Colones', 'EEK': 'Estonian Kroon', 'ETB': 'Ethiopia Birr', 'EUR': 'Euro',
    'FJD': 'Fiji Dollar', 'GMD': 'Gambia Dalasi', 'GEL': 'Georgian Lari', 'GHS': 'Ghanaian Cedi', 'XAU': 'Gold',
    'GTQ': 'Guatemala Quetzal', 'GNF': 'Guinean Franc', 'GYD': 'Guyanese Dollar', 'HTG': 'Haiti Gourdes', 'HNL': 'Honduras Lempira',
    'HKD': 'Hong Kong Dollar', 'HUF': 'Hungarian Forint', 'ISK': 'Icelandic Krona', 'XDR': 'Imf Drawing Rights', 'INR': 'Indian Rupee',
    'IDR': 'Indonesian Rupiah', 'IRR': 'Iran Rials', 'IQD': 'Iraq Dinars', 'ILS': 'Israeli Shekel', 'JMD': 'Jamaican Dollar',
    'JPY': 'Japanese Yen', 'JOD': 'Jordanian Dinar', 'KZT': 'Kazakhstan Tenge', 'KES': 'Kenyan Shilling', 'LFX': 'Khazanah Sukuk',
    'KRW': 'Korean Won', 'KWD': 'Kuwaiti Dinar', 'KGS': 'Kyrgyzstani Som', 'LAK': 'Laos Kips', 'LVL': 'Latvian Lats',
    'LBP': 'Lebanese Pound', 'LRD': 'Liberia Dollar', 'LYD': 'Libya Dinars', 'LTL': 'Lithuanian Litas', 'MOP': 'Macau Patacas',
    'MKD': 'Macedonian Denar', 'MGA': 'Madagascar Ariary', 'MWK': 'Malawian Kwacha', 'MYR': 'Malaysian Ringgit', 'MVR': 'Maldives Rufiyaa',
    'MRO': 'Mauritania Ouguiyas', 'MUR': 'Mauritian Rupee', 'MXN': 'Mexican Peso', 'MDL': 'Moldova Lei', 'MAD': 'Moroccan Dirham',
    'MZN': 'Mozambique Metical', 'MMK': 'Myanmar Burma Kyats', 'NAD': 'Namibian Dollar', 'NPR': 'Nepal Nepal Rupees', 'NZD': 'New Zealand Dollar',
    'NIO': 'Nicaraguan Cordoba', 'NGN': 'Nigerian Naira', 'NOK': 'Norwegian Krone', 'OMR': 'Omani Rial', 'PKR': 'Pakistan Rupee',
    'XPD': 'Palladium', 'PAB': 'Panama Balboa', 'PGK': 'Papua New Guinea Kina', 'PYG': 'Paraguayan Guarani', 'PEN': 'Peruvian Sol',
    'PHP': 'Philippine Peso', 'XPT': 'Platinum', 'PLN': 'Polish Zloty', 'QAR': 'Qatari Riyal', 'RON': 'Romanian Lei',
    'RUB': 'Russian Ruble', 'RWF': 'Rwandan Franc', 'STD': 'Sao Tome Dobra', 'SAR': 'Saudi Riyal', 'RSD': 'Serbian Dinar',
    'SCR': 'Seychelles Rupee', 'SLL': 'Sierra Leonean', 'XAG': 'Silver', 'SGD': 'Singapore Dollar', 'SKK': 'Slovak Koruna',
    'SOS': 'Somali Shillings', 'ZAR': 'South African Rand', 'SDR': 'Special Drawing Rights', 'LKR': 'Sri Lankan Rupee', 'SHP': 'St Helena Pound',
    'SDG': 'Sudan Pounds', 'SDD': 'Sudanese Dinars', 'SZL': 'Swazi Lilangeni', 'SEK': 'Swedish Krone', 'CHF': 'Swiss Franc',
    'SYP': 'Syria Pounds', 'TWD': 'Taiwan Dollar', 'TJS': 'Tajikistani Somoni', 'TZS': 'Tanzania Shillings', 'THB': 'Thai Baht',
    'TTD': 'Trinidadian Dollar', 'TND': 'Tunisian Dinar', 'TRY': 'Turkish New Lira', 'TMT': 'Turkmenistan Manat', 'AED': 'U.A.E. Dirham',
    'USD': 'U.S. Dollar', 'UGX': 'Ugandan Shillings', 'UAH': 'Ukraine Hryvnia', 'UYU': 'Uruguayan Peso', 'UZS': 'Uzbekistani Som',
    'VEF': 'Venezuelan Bolivars', 'VND': 'Vietnam Dong', 'YER': 'Yemeni Rials', 'ZMK': 'Zambia Kwacha', 'ZMW': 'Zambian Kwacha'
}
forex_major_pairs = {# NASDAQ
    "EURUSD": "EURO US DOLLAR", "GBPUSD": "BRITISH POUND US DOLLAR", "USDJPY": "US DOLLAR JAPANESE YEN",
    "USDCHF": "US DOLLAR SWISS FRANC", "USDCAD": "US DOLLAR CANADIAN DOLLAR", "AUDUSD": "AUSTRALIAN DOLLAR US DOLLAR",
    "USDMXN": "US DOLLAR MEXICAN PESO", "USDINR": "US DOLLAR INDIAN RUPEE", "USDRUB": "US DOLLAR RUSSIAN RUBLE",
    "USDBRL": "US DOLLAR BRAZILIAN REAL"
}

class fxutil:
    """
    Provides a unified, static interface for querying and validating currency codes and currency pairs
    across major and minor fiat currencies.

    Purpose
    -----------
    The `fxutil` class acts as a namespace for high-level currency lookup, tokenization, and validation,
    using internally defined in-memory dictionaries for major and broad-spectrum currencies. This abstraction
    simplifies the process of working with currency codes in financial, FX, and analytics applications.

    Structure
    -----------
    - fxutil.which:    Static inner class for listing available currency codes in both major and broad sets.
    - fxutil:          Main class contains static methods for string normalization, code lookup, pair validation,
                           and code formatting.

    Methods (by section)
    -----------
    which:
        - major()                  : Returns a list of all major currency codes.
        - quote()                  : Returns a list of all available codes from the broader set.

    General:
        - _join_currency(currency) : Joins a list of one or two 3-letter codes into a single string (e.g., ['USD','JPY'] -> 'USDJPY').
        - tokenize(currency, as_tuple=False): Splits currency pair strings or lists into separate codes, returning a list or tuple.
        - query(query, query_type="major", ret_type=None): Looks up currency codes or names in either major or broad set, returning code, name, or both.

    Notes
    -----------
    - All methods are static and designed for direct class-level use; no instantiation needed.
    - The utility methods ensure consistent normalization and validation of user input for FX operations.
    - Useful for both programmatic and interactive use-cases, including preprocessing for APIs or user input forms.
    - Throws informative errors for invalid or unrecognized currencies, facilitating robust error handling in client code.
    """
    class which:
        """
        Provides static methods to enumerate supported fiat currency codes from predefined
        dictionaries of major and broad-spectrum (including exotic) currencies.

        Purpose
        -----------
        The `which` class is designed for quick discovery of available currency codes.
        It distinguishes between a focused set of major global currencies and a much broader
        collection used for extended financial, FX, or analytics applications.

        Methods
        -----------
        - major(currencies=major_forex_currencies): List all major currency codes.
        - quote(currencies=all_currency_names): List all codes from the broader currency set.
        """    	
        @staticmethod
        def major(currencies=major_forex_currencies):
            """
            Returns a list of all 3-letter ISO currency codes classified as 'major' currencies.

            Parameters:
            -----------
            currencies : dict, optional
                Dictionary of major currencies to use. Defaults to the internal `major_forex_currencies` dictionary.

            Returns
            -----------
            list of str
                List of currency codes (e.g., ['USD', 'EUR', 'JPY']).

            Example
            -----------
            >>> which.major()
            ['AUD', 'CAD', 'CHF', ...]
            """        	
            return list(currencies.keys())
           
        @staticmethod
        def quote(currencies=all_currency_names):
            """
            Returns a list of all available 3-letter ISO currency codes from a broader set,
            including major, minor, and exotic currencies.

            Parameters:
            -----------
            currencies : dict, optional
                Dictionary of currencies to use. Defaults to the internal `all_currency_names` dictionary.

            Returns
            -----------
            list of str
                List of currency codes (e.g., ['USD', 'EUR', 'JPY', ..., 'UZS', 'ZMW']).

            Example
            -----------
            >>> which.quote()
            ['AFN', 'DZD', 'ARS', ...]
            """        	
            return list(currencies.keys())

    @staticmethod  
    def _join_currency(currency):
        """
        Joins a list of one or two 3-letter currency codes into a single string representation.

        Parameters:
        -----------
        currency : list or str
            A list containing one or two currency codes as strings (each 3 characters), or a single string.

        Returns
        -----------
        str
            Concatenated currency code string if input is a valid list, otherwise returns the input unchanged.

        Examples
        -----------
        >>> _join_currency(['USD', 'JPY'])
        'USDJPY'
        >>> _join_currency(['EUR'])
        'EUR'
        >>> _join_currency('USD')
        'USD'
        """
        if isinstance(currency, list) and len(currency) == 2:
            if all(isinstance(item, str) and len(item) == 3 for item in currency):
                return ''.join(currency)
        if isinstance(currency, list) and len(currency) == 1:
            return currency[0]
        return currency
       
    @staticmethod  
    def redact(s: str) -> str:
        # split() with no args breaks on any whitespace, so joining back drops them all.
        return "".join(s.split())
       
    @staticmethod   
    def tokenize(currency):
        """
        Parses and tokenizes a currency code or currency pair into individual 3-letter codes.

        Parameters:
        -----------
        currency : str or list of str
            Currency pair string (e.g., 'USDJPY', 'usd/jpy', 'eur_usd') or a list of such strings.

        Returns
        -----------
        list or tuple or None
            List or tuple of extracted currency codes (e.g., ['USD', 'JPY']), a single code (e.g., ['USD']),
            or None if no valid code is found.

        Examples
        -----------
        >>> tokenize('USDJPY')
        ['USD', 'JPY']
        >>> tokenize(['eur/usd', 'jpy'])
        ['EUR', 'USD', 'JPY']
        >>> tokenize('usd', as_tuple=True)
        ('USD',)
        """
        # Normalize to list of strings
        if isinstance(currency, str):
            parts = [currency]
        elif isinstance(currency, list):
            if not all(isinstance(x, str) for x in currency):
                raise TypeError("All elements in list must be strings")
            parts = currency.copy()
        else:
            raise TypeError("Expression only supports str or list of str")
        
        # 1) Flatten & comma‑split & strip whitespace
        chunks = []
        for part in parts:
            cleaned = fxutil.redact(part)       # drop all whitespace
            for piece in cleaned.split(','):
                if piece:
                    chunks.append(piece)
        
        # 2) Apply regex to each chunk
        codes = []
        for chunk in chunks:
            up = chunk.upper()
            # match a pair like USDJPY, USD-JPY, USD/JPY, USD_JPY
            m = re.fullmatch(r'([A-Z]{3})(?:[-_/]?([A-Z]{3}))?', up)
            if not m:
                continue
            c1, c2 = m.groups()
            codes.append(c1)
            if c2 and c2 != c1:
                codes.append(c2)
        
        if not codes:
            return None

        # 3) Deduplicate while preserving order
        seen = set()
        unique = []
        for c in codes:
            if c not in seen:
                seen.add(c)
                unique.append(c)

        # 4) Return as list
        return unique
       
    @staticmethod
    def query(query, query_type="major", ret_type=None):
        """
        Looks up a currency code or currency name and returns the code, name, both, or existence as a bool.

        Parameters
        -----------
        query : str
            The currency code (e.g., 'USD') or currency name (e.g., 'US Dollar') to look up.
        query_type : str, optional
            Which currency set to search in: 'major' (default), 'major_pairs', or 'quote'.
        ret_type : str or None, optional
            What to return:
              - 'code' → 3‑letter code (e.g. 'USD')
              - 'name' → full currency name (e.g. 'US Dollar')
              - 'bool' → True if found, False otherwise
              - None    → both as a `(code, name)` tuple

        Returns
        -----------
        str or tuple or bool or None
            Depending on `ret_type`: the code, name, tuple, boolean, or None if not found.

        Examples
        -----------
        >>> query('usd', ret_type='name')
        'US Dollar'
        >>> query('Japanese Yen', query_type='quote', ret_type='code')
        'JPY'
        >>> query('CAD')
        ('CAD', 'Canadian Dollar')
        >>> query('EURUSD', query_type='major_pairs', ret_type='name')
        'Euro/US Dollar'
        >>> query('XYZ', ret_type='bool')
        False
        """
        if isinstance(query, str):
            query = fxutil.redact(query)

        if query_type == "major":
            currency_dict = major_forex_currencies
        elif query_type == "major_pairs":
            currency_dict = forex_major_pairs
        else:
            currency_dict = all_currency_names

        ql = query.lower()
        for code, name in currency_dict.items():
            if ql == code.lower() or ql == name.lower():
                if ret_type is not None:
                    rt = ret_type.lower()
                    if rt == "code":
                        return code
                    if rt == "name":
                        return name
                    if rt == "bool":
                        return True
                return (code, name)

        # no match
        if ret_type is not None and ret_type.lower() == "bool":
            return False
        return None



def _timezone_info():
    """
    Dynamically import and return the appropriate time zone class for working with time zones.

    This function is designed for lazy-loading and backward compatibility, allowing code to
    work seamlessly with both new and legacy Python environments without module-level imports.
    """
    try:
        # Python 3.9+
        from zoneinfo import ZoneInfo
        return ZoneInfo
    except ImportError:
        from pytz import timezone as ZoneInfo  # fallback
        return ZoneInfo
       
class ForexMarketHours:
    """
    ForexMarketHours

    A utility class for determining the open/close status of major Forex trading sessions 
    (Sydney, Tokyo, London, New York) based on UTC time, and for reporting the current 
    local time if the market is open. 

    Features:
        - Converts between UTC and a user-defined local timezone (default "US/Central").
        - Handles session windows that cross midnight.
        - Provides convenience methods to check if any Forex session is currently open.
        - Optionally returns the local time (with timezone and DST awareness) when the market is open.
    """
    # Define the four Forex sessions in UTC
    _SESSIONS_UTC = {
        'sydney':   {'start': time(22, 0), 'end': time( 6, 0)},
        'tokyo':    {'start': time( 0, 0), 'end': time( 8, 0)},
        'london':   {'start': time( 8, 0), 'end': time(16, 0)},
        'new_york': {'start': time(13, 0), 'end': time(21, 0)},
    }

    def __init__(self, timezone: str = "US/Central"):
        """
        Initialize the ForexMarketHours instance with a specified local timezone.
        The timezone is used for converting UTC time to local time when reporting
        market open status. Defaults to "US/Central".
        """    	
        # Store a tzinfo object for later conversion
        ZoneInfo = _timezone_info()
        self.local_tz = ZoneInfo(timezone)  

    @staticmethod
    def _in_time_window(t: time, start: time, end: time) -> bool:
        """
        Determine if a given time falls within a specified window.
        Handles time windows that may wrap past midnight (e.g., 22:00 to 06:00).
        Returns True if 't' is in the interval [start, end), otherwise False.
        Static method.
        """    	
        # Handles windows that wrap past midnight
        if start < end:
            return start <= t < end
        return t >= start or t < end

    def is_forex_market_open(self) -> bool:
        """
        Check if any major Forex session (Sydney, Tokyo, London, New York) is currently open.
        Returns True if at least one session is active based on the current UTC time,
        otherwise returns False.
        """
        now_utc = datetime.now(timezone.utc).time()
        for win in self._SESSIONS_UTC.values():
            if self._in_time_window(now_utc, win['start'], win['end']):
                return True
        return False

    @property
    def time(self):
        """
        If the Forex market is open, return the current local time (as a string in
        "YYYY-MM-DD HH:MM:SS" format) for the configured timezone.
        If the market is closed, return None.
        """
        if not self.is_forex_market_open():
            return None
        # Convert UTC→Central (with DST baked in)
        now_utc = datetime.now(timezone.utc)
        now_central = now_utc.astimezone(self.local_tz)
        return now_central.strftime("%Y-%m-%d %H:%M:%S")

forex_hours = ForexMarketHours()

def __dir__():
    return __all__


