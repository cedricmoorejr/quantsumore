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


import sqlite3
import os
from pathlib import Path
import json
from datetime import datetime, timedelta

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from quantsumore import APP_DATA_DIR


__all__ = ['JSON', 'SQLiteDBHandler']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.


_APP_DATA_DIR = str(APP_DATA_DIR)

######################################################################
# JSON
######################################################################

class JSON:
    def __init__(self, filename=None, directory=None, json_data=None):
        self.json_data = json_data
        if directory is None:
            directory = _APP_DATA_DIR  # _APP_DATA_DIR will be whatever is defined at runtime
            
        if json_data is None:
            if filename is None:
                raise ValueError("Either filename or json_data must be provided.")
            self.filename = filename
            self.json_dir = directory
            if self.json_dir is None:
                raise FileNotFoundError(f"Directory '{directory}' not found in the expected paths.")
            self.json_path = os.path.join(self.json_dir, self.filename)
        else:
            self.filename = filename if filename else "data.json"
            self.json_path = None
    
    def save(self, data, force_save_to_file=False):
        if force_save_to_file or self.json_path:
            if self.json_path is None:
                raise ValueError("File path not set. Provide a filename and directory for file operations.")
            try:
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    if isinstance(data, dict):
                        json.dump(data, json_file, indent=4)
                    else:
                        json_file.write(data)
            except Exception as e:
                print(f"An error occurred while saving data to {self.json_path}: {e}")
        else:
            self.json_data = data
    
    def load(self, from_file=False, key=None):
        if from_file and self.json_path:
            try:
                with open(self.json_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    if key:
                        data = data.get(key, None)  # Safely fetch the key if it exists
                    self.json_data = data
                    return data
            except FileNotFoundError:
                print(f"No such file: '{self.json_path}'")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from the file: '{self.json_path}'")
            except Exception as e:
                print(f"An error occurred while loading data from {self.json_path}: {e}")
        elif self.json_data:
            data = self.json_data
            if key:
                data = data.get(key, None)  # Safely fetch the key if it exists
            return data
        else:
            raise ValueError("No data available to load. Provide json_data or enable file loading.")

    def flatten(self, initial_path, keys, data=None):
        """ Flatten the JSON data based on the provided path and keys. """
        data = data if data is not None else self.json_data        
        try:
            for part in initial_path.split('.'):
                if part.isdigit():
                    data = data[int(part)]
                else:
                    data = data[part]
        except KeyError as e:
            raise KeyError(f"Path error: {e}")
        flattened = {}
        try:
            for key in keys:
                parts = key.split('.')
                ref = data
                for part in parts:
                    if part.isdigit():
                        ref = ref[int(part)]
                    else:
                        ref = ref[part]
                flattened[key.replace('.', '_')] = ref
        except KeyError as e:
            print(f"Flattening error on key {key}: {e}")
            flattened[key.replace('.', '_')] = None

        self.flattened_json_data = flattened
        return flattened
    
    def dataframe(self, data=None, rename_columns=None, column_order=None, data_types=None):
        """
        Creates a DataFrame from data which may contain scalar values or lists.
        """
        import pandas as pd # Third-party library imports (from PyPI or other package sources) 
        
        data = data if data is not None else self.flattened_json_data        
        if isinstance(data, dict):
            if all(not isinstance(v, (list, tuple, set, dict)) for v in data.values()):
                data = {k: [v] for k, v in data.items()}
        df = pd.DataFrame(data)

        if rename_columns and isinstance(rename_columns, dict):
            df.rename(columns=rename_columns, inplace=True, errors='ignore')

        if column_order and isinstance(column_order, list):
            filtered_columns = [col for col in column_order if col in df.columns]
            df = df[filtered_columns]

        if data_types and isinstance(data_types, dict):
            valid_data_types = {k: v for k, v in data_types.items() if k in df.columns}
            df = df.astype(valid_data_types, errors='ignore')
        self.dataframe_json_data = df
        return df

    def clear_json(self):
        """ Resets the json_data, flattened_json_data, and dataframe_json_data attributes to None."""
        self.json_data = None
        self.flattened_json_data = None
        self.dataframe_json_data = None
        print("All data has been cleared.")
       
    def file_exists(self):
        """Check if the JSON file exists at the designated path."""
        return os.path.exists(self.json_path)
       
    def last_modified(self, as_string=False):
        """Return the last modification time of the JSON file."""
        if self.file_exists():
            timestamp = os.path.getmtime(self.json_path)
            if as_string:
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return datetime.fromtimestamp(timestamp)
        else:
            return None      
           
    def is_outdated(self):
        """Check if the last modification of the file was more than a month ago."""
        if self.file_exists():
            last_modification_time = os.path.getmtime(self.json_path)
            last_modification_date = datetime.fromtimestamp(last_modification_time)
            if datetime.now() - last_modification_date > timedelta(days=30):
                return True
            else:
                return False
        return True
       
       
######################################################################
# SQLITE HANDLER
######################################################################

class SQLiteDBHandler:
    def __init__(self, filename, directory=None, json_data=None):
        # 1) Directory fallback    	
        if directory is None:
            directory = _APP_DATA_DIR  # Use _APP_DATA_DIR as fallback
            
        # self.filename = filename
        # self.db_dir = directory
        # self.db_path = os.path.join(self.db_dir, self.filename)
        # self.path = self.Path()        
        # self.conn = None
        # self.cursor = None
        # self.json_data = json_data      
        
        filename_path  = Path(filename)
        directory_path = Path(directory)

        # 2) If directory_path looks like a file (has a suffix), treat it as the filename
        if directory_path.suffix:
            filename_path  = directory_path
            directory_path = directory_path.parent

        # 3) If filename_path is absolute or has a parent != current dir,
        #    we assume it's a full path; ignore directory_path.
        if filename_path.is_absolute() or filename_path.parent != Path('.'):
            self.db_path = str(filename_path)
            self.db_dir  = str(filename_path.parent)
            self.filename = filename_path.name
        else:
            # Normal case: filename is just a name, directory_path is the folder
            self.db_dir   = str(directory_path)
            self.filename = filename_path.name
            self.db_path  = os.path.join(self.db_dir, self.filename)

        # Keep a copy for Path() lookup if you still need it
        self.path      = self.Path()        
        self.conn      = None
        self.cursor    = None
        self.json_data = json_data

    def connect(self):
        """Establish a new database connection if one doesn't already exist."""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

    def close(self):
        """Properly close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 
        
    def reset_database(self):
        """Deletes the existing database file if it exists."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            os.remove(self.db_path)

    def ensure_database(self):
        """Ensure the database and table exist, and store creation timestamp."""
        self.connect()
        # Create cryptos table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cryptos (
                id INTEGER PRIMARY KEY,
                name TEXT,
                symbol TEXT,
                slug TEXT,
                is_active INTEGER,
                status INTEGER,
                rank INTEGER
            )
        ''')
        # Create metadata table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # Create exchanges table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchanges (
                exchangeId INTEGER PRIMARY KEY,
                exchangeName TEXT,
                exchangeSlug TEXT
            )
        ''')
        # Create pairs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pairs (
                currencyId INTEGER PRIMARY KEY,
                currencySymbol TEXT,
                currency TEXT
            )
        ''')
        # Insert creation timestamp only if not already present
        self.cursor.execute("SELECT value FROM metadata WHERE key='created_at'")
        result = self.cursor.fetchone()
        if result is None:
            # Use ISO format for timestamp
            now = datetime.now().isoformat()
            self.cursor.execute(
                "INSERT INTO metadata (key, value) VALUES (?, ?)",
                ("created_at", now)
            )
        self.conn.commit()

    def parse_json(self):
        """Parse JSON content to prepare for database insertion."""
        data = self.json_data
        data = data["cryptos"]
        return [(item['id'], item['name'], item['symbol'], item['slug'], item['is_active'], item['status'], item['rank']) for item in data.values()]

    def parse_exchanges(self):
        """Parse exchanges from JSON."""
        data = self.json_data
        exchanges = data.get("crypto_exchanges", {})
        return [
            (int(item["exchangeId"]), item["exchangeName"], item["exchangeSlug"])
            for item in exchanges.values()
        ]

    def parse_pairs(self):
        """Parse pairs from JSON."""
        data = self.json_data
        pairs = data.get("pairs", {})
        return [
            (item["currencyId"], item["currencySymbol"], name)
            for name, item in pairs.items()
        ]
        
    def insert_data(self, transformed_data):
        """Inserts data into the database."""
        for item in transformed_data:
            self.cursor.execute('''
                INSERT INTO cryptos (id, name, symbol, slug, is_active, status, rank)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                symbol=excluded.symbol,
                slug=excluded.slug,
                is_active=excluded.is_active,
                status=excluded.status,
                rank=excluded.rank;
            ''', item)
        self.conn.commit()

    def insert_exchanges(self, exchanges):
        """Insert exchanges into the database."""
        for item in exchanges:
            self.cursor.execute('''
                INSERT INTO exchanges (exchangeId, exchangeName, exchangeSlug)
                VALUES (?, ?, ?)
                ON CONFLICT(exchangeId) DO UPDATE SET
                exchangeName=excluded.exchangeName,
                exchangeSlug=excluded.exchangeSlug;
            ''', item)
        self.conn.commit()

    def insert_pairs(self, pairs):
        """Insert pairs into the database."""
        for item in pairs:
            self.cursor.execute('''
                INSERT INTO pairs (currencyId, currencySymbol, currency)
                VALUES (?, ?, ?)
                ON CONFLICT(currencyId) DO UPDATE SET
                currencySymbol=excluded.currencySymbol,
                currency=excluded.currency;
            ''', item)
        self.conn.commit()

    def file_exists(self):
        """Check if the database file exists."""
        return os.path.exists(self.db_path)

    def get_creation_time(self):
        """Returns the database creation timestamp, or None if not found."""
        self.connect()
        self.cursor.execute("SELECT value FROM metadata WHERE key='created_at'")
        result = self.cursor.fetchone()
        return result[0] if result else None

    def Path(self):
        """Returns the database file path if it exists, otherwise notifies non-existence."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            return self.db_path
        else:
            return None
           
    def save(self):
        """Process JSON content and save to the database."""
        try:
            self.connect()
            self.ensure_database()
            # --- Cryptos ---
            cryptos_data = self.parse_json()
            self.insert_data(cryptos_data)
            # --- Exchanges ---
            exchanges_data = self.parse_exchanges()
            self.insert_exchanges(exchanges_data)
            # --- Pairs ---
            pairs_data = self.parse_pairs()
            self.insert_pairs(pairs_data)
        except Exception as e:
            print(f"An error occurred during the save process: {e}")
            self.conn.rollback()
        finally:
            self.close()

# _local_directory = str(APP_DATA_DIR)

def __dir__():
    return __all__




