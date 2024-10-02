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



import sqlite3
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import re

class FilePathFinder:
    """Handles finding, reading, writing, and modifying file paths and contents."""	
    
    class fPath:
        """Nested class to manage file path finding within a project structure marked by a unique identifier."""    	
        def __init__(self, unique_identifier="## -- quantsumore -- ##"):
            self.unique_identifier = unique_identifier

        def _root(self):
            """Finds the root directory marked by a unique identifier in its __init__.py."""
            current_directory = os.path.dirname(os.path.abspath(__file__))
            while current_directory != os.path.dirname(current_directory):
                init_file_path = os.path.join(current_directory, '__init__.py')
                if os.path.isfile(init_file_path):
                    with open(init_file_path, 'r') as f:
                        if self.unique_identifier in f.read():
                            return current_directory
                current_directory = os.path.dirname(current_directory)
            return None

        def _find_file(self, directory, file_name):
            """Searches for a file within the given directory."""
            if not os.path.splitext(file_name)[1]:
                file_name += '.py'
            for dirpath, dirnames, filenames in os.walk(directory):
                if file_name in filenames:
                    return os.path.join(dirpath, file_name)
            return None

        def _find_directory(self, root_directory, target_directory):
            """Searches for a directory within the given root directory."""
            for dirpath, dirnames, _ in os.walk(root_directory):
                if target_directory in dirnames:
                    return os.path.join(dirpath, target_directory)
            return None

        def return_path(self, file=None, directory=None):
            """Find either a file or directory based on input."""
            if file and not directory:
                return self._find_file(directory=self._root(), file_name=file)
            elif directory and not file:
                return self._find_directory(root_directory=self._root(), target_directory=directory)
            else:
                return None
    
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.path_handler = self.fPath()
                
    def trace(self, file=None, directory=None):
        """Retrieves the path for a specified file or directory.

        Args:
            file (str, optional): The name of the file to find.
            directory (str, optional): The name of the directory to find.

        Returns:
            str: The path to the file or directory if found, otherwise None.
        """    	
        return self.path_handler.return_path(file=file, directory=directory)       

    def inscribe(self, file, s, overwrite=True):
        """Writes data to a file, with the option to overwrite or append.

        Args:
            file (str): The file path to write to.
            s (str or pandas.DataFrame): The data to write to the file.
            overwrite (bool): True to overwrite the file, False to append.
        """    	
        mode = 'w' if overwrite else 'a'
        if isinstance(s, pd.DataFrame):
            header = True if overwrite else False
            s.to_csv(file, mode=mode, encoding=self.encoding, index=False, header=header)
        else:            
            with open(file, mode, encoding=self.encoding) as compose:
                compose.write(s)
                
    def extend(self, file, s):
        """Appends data to a file, creating the file if it does not exist.

        Args:
            file (str): The file path to append data to.
            s (str): The data to append.
        """    	
        if not os.path.exists(file):
            self.inscribe(file, s)
        with open(file, 'a', encoding=self.encoding) as compose:
            compose.write(s)

    def inject(self, file, s, line):
        """Inserts data into a specific line of a file.

        Args:
            file (str): The file path where data is to be inserted.
            s (str): The data to insert.
            line (int): The line number at which to insert the data.
        """    	
        lines = []
        with open(file) as skim:
            lines = skim.readlines()
        if line == len(lines) or line == -1:
            lines.append(s + '\n')
        else:
            if line < 0:
                line += 1
            lines.insert(line, s + '\n')
        with open(file, 'w', encoding=self.encoding) as compose:
            compose.writelines(lines)

    def extract(self, file, silent=False):
        """Reads the contents of a file.

        Args:
            file (str): The file path to read from.
            silent (bool): If True, returns an empty string instead of raising an error when the file is not found.

        Returns:
            str: The contents of the file or an empty string if silent is True and the file does not exist.
        """    	
        if not os.path.exists(file):
            if silent:
                return ''
            else:
                raise FileNotFoundError(str(file))
        with open(file, encoding=self.encoding) as skim:
            return skim.read()

    def alter(self, file, new, old=None, pattern=None):
        """Replaces occurrences of an old string or pattern in a file with a new string.

        Args:
            file (str): The file path for the replacement operation.
            new (str): The new string to replace with.
            old (str, optional): The old string to replace.
            pattern (str, optional): A regex pattern to match and replace.
        """    	
        if old is None and pattern is None:
            raise ValueError("Either 'old' or 'pattern' must be provided for replacement.")
           
        s = self.extract(file)
        
        if old is not None:
            s = s.replace(old, new)
            
        if pattern is not None:
            s = re.sub(pattern, new, s)
            
        self.inscribe(file, s)



class JSON:
    def __init__(self, filename, directory="configuration", json_data=None):
        self.json_data = json_data       
        self.filename = filename
        self.json_dir = filePaths.trace(directory=directory)
        if self.json_dir is None:
            raise FileNotFoundError(f"Directory '{directory}' not found in the expected paths.")
        try:
            self.json_path = os.path.join(self.json_dir, self.filename)
        except TypeError:
            if json_data:
                self.json_path = None        
                self.flattened_json_data = None
                self.dataframe_json_data = None        
        
    def save(self, data):
        try:
            if isinstance(data, str):
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(data)
                
            elif isinstance(data, dict):
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, indent=4)
            
        except Exception as e:
            print(f"An error occurred while saving data to {self.json_path}: {e}")
    
    def load(self, json_data=None, key=None):
        data = json_data if json_data is not None else self.json_data
        
        if data:
            if isinstance(data, str):
                json_content = json.loads(data)
                json_content = json_content.get(key) if key else json_content
                self.json_data = json_content
                return json_content
            elif isinstance(data, dict):
                json_content = data.get(key) if key else data
                self.json_data = json_content
                return json_content
            else:
                raise  

        if not self.json_path:
            raise ValueError("File path is not specified for loading data.")
        try:
            with open(self.json_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)[key] if key else json.load(json_file)
            return data
        except FileNotFoundError:
            print(f"No such file: '{self.json_path}'")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file: '{self.json_path}'")
        except Exception as e:
            print(f"An error occurred while loading data from {self.json_path}: {e}")
        return None

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
        """ Creates a DataFrame from data which may contain scalar values or lists."""
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
       

class SQLiteDBHandler:
    def __init__(self, filename, directory="configuration"):
        self.filename = filename
        self.db_dir = filePaths.trace(directory=directory)
        self.db_path = os.path.join(self.db_dir, self.filename)
        self.path = self.Path()        
        self.conn = None
        self.cursor = None

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

    def reset_database(self):
        """Deletes the existing database file if it exists."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            os.remove(self.db_path)

    def ensure_database(self):
        """Ensure the database and table exist."""
        self.connect()
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
        self.conn.commit()

    def parse_json(self, json_content):
        """Parse JSON content to prepare for database insertion."""
        data = JSON(json_content).load(key="cryptos")
        return [(item['id'], item['name'], item['symbol'], item['slug'], item['is_active'], item['status'], item['rank']) for item in data.values()]

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

    def save(self, json_content):
        """Process JSON content and save to the database."""
        try:
            self.connect()
            self.ensure_database()
            transformed_data = self.parse_json(json_content)
            self.insert_data(transformed_data)
        except Exception as e:
            print(f"An error occurred during the save process: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def file_exists(self):
        """Check if the database file exists."""
        return os.path.exists(self.db_path)

    def Path(self):
        """Returns the database file path if it exists, otherwise notifies non-existence."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            return self.db_path
        else:
            return None

    def last_modified(self, as_string=False):
        """Return the last modification time of the database file."""
        if self.file_exists():
            timestamp = os.path.getmtime(self.db_path)
            if as_string:
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return datetime.fromtimestamp(timestamp)
        else:
            return None 

    def is_outdated(self):
        """Check if the last modification of the file was more than a month ago."""
        if self.file_exists():
            last_modification_time = os.path.getmtime(self.db_path)
            last_modification_date = datetime.fromtimestamp(last_modification_time)
            if datetime.now() - last_modification_date > timedelta(days=30):
                return True
            else:
                return False
        return True



filePaths = FilePathFinder()


def __dir__():
    return ['JSON', 'SQLiteDBHandler', 'filePaths']

__all__ = ['JSON', 'SQLiteDBHandler', 'filePaths']





